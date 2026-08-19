#!/usr/bin/env python3
"""Create the canonical GETO lead-value assessment from evidenced dimension inputs."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = ROOT / "references" / "lead-value-model.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def context_ref(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    candidate = value.get("contextRef", value)
    return candidate if isinstance(candidate, dict) else None


def level(score: float, anchors: dict[str, list[float]]) -> str:
    for name in ("high", "medium", "low"):
        lower, upper = anchors[name]
        if lower <= score <= upper:
            return name
    return "low"


def calculate(company: dict[str, Any], model: dict[str, Any], capability: dict[str, Any] | None, assessed_on: str) -> dict[str, Any]:
    if model.get("approvalStatus") != "approved":
        raise ValueError("lead-value model is not approved")
    existing = company.get("assessment") if isinstance(company.get("assessment"), dict) else {}
    supplied = {
        item.get("dimensionCode"): item
        for item in existing.get("dimensions", [])
        if isinstance(item, dict) and item.get("dimensionCode")
    }
    cap_codes = sorted(set(existing.get("capCodes", [])))
    gap_codes = sorted(set(existing.get("gapCodes", [])))
    dimensions: list[dict[str, Any]] = []
    complete = True
    weighted_completeness = 0.0
    final_total = 0.0

    for definition in model["dimensions"]:
        item = supplied.get(definition["dimensionCode"], {})
        grade = item.get("evidenceGrade", "U")
        weight = model["evidenceWeights"].get(grade, 0.0)
        observed = item.get("observedScore")
        evidence = item.get("evidence") if isinstance(item.get("evidence"), list) else []
        local_caps = sorted(set(item.get("capCodes", [])))
        dimension_cap = definition["maxScore"]
        for code in cap_codes + local_caps:
            dimension_cap = min(
                dimension_cap,
                model.get("dimensionCaps", {}).get(code, {}).get(definition["dimensionCode"], dimension_cap),
            )
        final = None
        if isinstance(observed, (int, float)) and 0 <= observed <= definition["maxScore"] and grade in {"A", "B", "C"} and evidence:
            final = round(min(float(observed), float(dimension_cap)) * weight, 2)
            weighted_completeness += definition["maxScore"] * weight
            final_total += final
        else:
            complete = False
        dimensions.append({
            "dimensionCode": definition["dimensionCode"],
            "name": definition["name"],
            "observedScore": observed if isinstance(observed, (int, float)) else None,
            "finalDimensionScore": final,
            "maxScore": definition["maxScore"],
            "evidenceGrade": grade if grade in model["evidenceWeights"] else "U",
            "evidenceWeight": weight,
            "level": level(final, definition["anchors"]) if final is not None else "unknown",
            "rationale": str(item.get("rationale") or "待补充本维度证据与判断。"),
            "evidence": evidence,
            "gapCodes": sorted(set(item.get("gapCodes", []))),
            "capCodes": local_caps,
        })

    capability_available = bool(capability and capability.get("status") == "available")
    status = "completed" if capability_available and complete else (
        "pending_capability_foundation" if not capability_available else "incomplete_evidence"
    )
    completeness = round(weighted_completeness, 2)
    overall = None
    grade = None
    if status == "completed":
        overall = round(final_total, 2)
        for code in cap_codes:
            if code in model.get("caps", {}):
                overall = min(overall, float(model["caps"][code]))
        by_code = {item["dimensionCode"]: item["finalDimensionScore"] for item in dimensions}
        for rule in model["ratingRules"]:
            if overall < rule["minimumScore"]:
                continue
            if completeness < rule.get("minimumCompleteness", 0):
                continue
            if completeness >= rule.get("maximumCompletenessExclusive", 101):
                continue
            if any(by_code.get(code, 0) < floor for code, floor in rule.get("dimensionFloors", {}).items()):
                continue
            if set(cap_codes).intersection(rule.get("forbiddenCapCodes", [])):
                continue
            grade = rule["grade"]
            break
        grade = grade or "watch"

    return {
        "assessmentType": "lead_value",
        "status": status,
        "modelCode": model["modelCode"],
        "modelVersion": model["modelVersion"],
        "ratingScaleVersion": model["ratingScaleVersion"],
        "capabilityContext": capability or {
            "foundationKey": "geto:capability-foundation", "foundationVersion": "unknown",
            "asOf": assessed_on, "status": "unavailable", "contentHash": "unavailable",
            "productCodes": [], "scenarioCodes": [], "roleCodes": [], "caseKeys": [],
            "gapCodes": ["capability_context_unavailable"],
        },
        "grade": grade,
        "overallScore": overall,
        "informationCompleteness": completeness,
        "overallConclusion": str(existing.get("overallConclusion") or (
            "六维证据与能力底座满足评分门禁。" if status == "completed" else "评分门禁尚未满足，按 gapCodes 补证。"
        )),
        "assessedOn": assessed_on,
        "dimensions": dimensions,
        "capCodes": cap_codes,
        "gapCodes": gap_codes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("company_json")
    parser.add_argument("--capability-context")
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    parser.add_argument("--assessed-on", default=date.today().isoformat())
    args = parser.parse_args()

    company_path = Path(args.company_json).expanduser().resolve()
    model = load_json(Path(args.model).expanduser().resolve())
    capability = context_ref(load_json(Path(args.capability_context).expanduser().resolve())) if args.capability_context else None
    company = load_json(company_path)
    company["assessment"] = calculate(company, model, capability, args.assessed_on)
    atomic_write(company_path, company)
    print(json.dumps({"companyJson": str(company_path), "assessment": company["assessment"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
