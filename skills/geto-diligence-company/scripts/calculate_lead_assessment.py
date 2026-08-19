#!/usr/bin/env python3
"""Prepare one company's evidenced lead-value inputs for main-task cohort scoring."""

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


def calculate(
    company: dict[str, Any], model: dict[str, Any], capability: dict[str, Any] | None,
    assessed_on: str, cohort_key: str | None = None,
) -> dict[str, Any]:
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
    weighted_completeness = 0.0
    cohort_key = cohort_key or existing.get("cohortKey")
    cohort_policies = model.get("cohortPolicy", {}).get("dimensionPolicies", {})

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
        if isinstance(observed, (int, float)) and 0 <= observed <= definition["maxScore"] and grade in {"A", "B", "C"} and evidence:
            weighted_completeness += definition["maxScore"] * weight
        else:
            observed = None
            grade = "U"
            weight = 0.0
        policy = cohort_policies.get(definition["dimensionCode"], {})
        dimensions.append({
            "dimensionCode": definition["dimensionCode"],
            "name": definition["name"],
            "observedScore": observed if isinstance(observed, (int, float)) else None,
            "baselineScore": None,
            "baselinePolicy": str(policy.get("mode") or "median_capped"),
            "finalDimensionScore": None,
            "maxScore": definition["maxScore"],
            "evidenceGrade": grade if grade in model["evidenceWeights"] else "U",
            "evidenceWeight": weight,
            "level": level(float(observed), definition["anchors"]) if observed is not None else "unknown",
            "rationale": str(item.get("rationale") or "待补充本维度证据与判断。"),
            "evidence": evidence,
            "gapCodes": sorted(set(item.get("gapCodes", []))),
            "capCodes": local_caps,
        })

    capability_available = bool(capability and capability.get("status") == "available")
    status = "pending_cohort_baseline" if capability_available and cohort_key else (
        "pending_capability_foundation" if not capability_available else "incomplete_evidence"
    )
    completeness = round(weighted_completeness, 2)
    if status == "pending_cohort_baseline":
        gap_codes = sorted(set(gap_codes + ["cohort_baseline_required"]))

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
        "cohortKey": cohort_key,
        "cohortBaselineVersion": None,
        "cohortAsOf": None,
        "grade": None,
        "overallScore": None,
        "informationCompleteness": completeness,
        "overallConclusion": str(existing.get("overallConclusion") or (
            "单公司观察输入已完成，等待主任务生成同类型 cohort baseline 并统一评分。"
            if status == "pending_cohort_baseline" else "评分输入门禁尚未满足，按 gapCodes 补证。"
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
    parser.add_argument("--cohort-key", required=True, help="Canonical countryCode:companyRole cohort key")
    args = parser.parse_args()

    company_path = Path(args.company_json).expanduser().resolve()
    model = load_json(Path(args.model).expanduser().resolve())
    capability = context_ref(load_json(Path(args.capability_context).expanduser().resolve())) if args.capability_context else None
    company = load_json(company_path)
    company["assessment"] = calculate(company, model, capability, args.assessed_on, args.cohort_key)
    atomic_write(company_path, company)
    print(json.dumps({"companyJson": str(company_path), "assessment": company["assessment"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
