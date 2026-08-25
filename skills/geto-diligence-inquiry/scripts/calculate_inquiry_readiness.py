#!/usr/bin/env python3
"""Calculate one inquiry's evidence-only readiness score without peer imputation."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = ROOT / "references" / "inquiry-readiness-model.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, value: Any) -> None:
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


def calculate(company: dict[str, Any], model: dict[str, Any], inquiry_ref: str, assessed_on: str) -> dict[str, Any]:
    if model.get("approvalStatus") != "approved":
        raise ValueError("inquiry-readiness model is not approved")
    existing = company.get("inquiryAssessment") if isinstance(company.get("inquiryAssessment"), dict) else {}
    supplied = {
        item.get("dimensionCode"): item
        for item in existing.get("dimensions", [])
        if isinstance(item, dict) and item.get("dimensionCode")
    }
    dimensions: list[dict[str, Any]] = []
    complete = True
    total = 0.0
    for definition in model["dimensions"]:
        item = supplied.get(definition["dimensionCode"], {})
        score = item.get("score")
        evidence = item.get("evidence") if isinstance(item.get("evidence"), list) else []
        if not isinstance(score, (int, float)) or not 0 <= score <= definition["maxScore"]:
            score = None
            complete = False
        elif score > 0 and not evidence:
            complete = False
        if score is not None:
            total += float(score)
        dimensions.append({
            "dimensionCode": definition["dimensionCode"],
            "name": definition["name"],
            "score": score,
            "maxScore": definition["maxScore"],
            "rationale": str(item.get("rationale") or "待按 component 逐项核对。"),
            "evidence": evidence,
            "gapCodes": sorted(set(item.get("gapCodes", []))),
        })

    hard_blocks = sorted(set(existing.get("hardBlockCodes", [])))
    gap_codes = sorted(set(existing.get("gapCodes", [])))
    status = "completed" if complete and inquiry_ref else "incomplete_inquiry"
    overall = round(total, 2) if status == "completed" else None
    grade = None
    if overall is not None:
        for code in hard_blocks:
            if code in model.get("caps", {}):
                overall = min(overall, float(model["caps"][code]))
        by_code = {item["dimensionCode"]: item["score"] or 0 for item in dimensions}
        for rule in model["grades"]:
            if overall < rule["minimumScore"]:
                continue
            if any(by_code.get(code, 0) < floor for code, floor in rule.get("dimensionFloors", {}).items()):
                continue
            grade = rule["grade"]
            break
        grade = grade or "high_risk_or_unqualified"

    return {
        "assessmentType": "inquiry_readiness",
        "status": status,
        "modelCode": model["modelCode"],
        "modelVersion": model["modelVersion"],
        "inquiryRef": inquiry_ref,
        "grade": grade,
        "overallScore": overall,
        "overallConclusion": str(existing.get("overallConclusion") or (
            "询盘准备度已按当前证据计算。" if status == "completed" else "询盘输入尚未满足完整评分合同。"
        )),
        "assessedOn": assessed_on,
        "dimensions": dimensions,
        "hardBlockCodes": hard_blocks,
        "gapCodes": gap_codes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("company_json")
    parser.add_argument("--inquiry-ref", required=True)
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    parser.add_argument("--assessed-on", default=date.today().isoformat())
    args = parser.parse_args()
    path = Path(args.company_json).expanduser().resolve()
    company = load_json(path)
    company["inquiryAssessment"] = calculate(
        company, load_json(Path(args.model).expanduser().resolve()),
        args.inquiry_ref, args.assessed_on,
    )
    atomic_write(path, company)
    print(json.dumps({"companyJson": str(path), "inquiryAssessment": company["inquiryAssessment"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
