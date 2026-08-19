#!/usr/bin/env python3
"""Build cohort medians and batch-score all GETO lead assessments in one country workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import tempfile
from datetime import date
from pathlib import Path
from typing import Any


SKILLS_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = SKILLS_ROOT / "geto-diligence-company" / "references" / "lead-value-model.json"


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


def score_level(score: float, anchors: dict[str, list[float]]) -> str:
    for name in ("high", "medium", "low"):
        lower, upper = anchors[name]
        if lower <= score <= upper:
            return name
    return "low"


def rating(model: dict[str, Any], total: float, completeness: float, dimensions: list[dict[str, Any]], cap_codes: list[str]) -> str:
    by_code = {item["dimensionCode"]: item["finalDimensionScore"] for item in dimensions}
    for rule in model["ratingRules"]:
        if total < rule["minimumScore"]:
            continue
        if completeness < rule.get("minimumCompleteness", 0):
            continue
        if completeness >= rule.get("maximumCompletenessExclusive", 101):
            continue
        if any(by_code.get(code, 0) < floor for code, floor in rule.get("dimensionFloors", {}).items()):
            continue
        if set(cap_codes).intersection(rule.get("forbiddenCapCodes", [])):
            continue
        return str(rule["grade"])
    return "watch"


def baseline_version(model: dict[str, Any], as_of: str, companies: list[tuple[Path, dict[str, Any]]]) -> str:
    digest = hashlib.sha256()
    digest.update(model["modelVersion"].encode("utf-8"))
    digest.update(as_of.encode("utf-8"))
    for path, company in sorted(companies, key=lambda item: str(item[0])):
        assessment = company.get("assessment", {})
        signature = {
            "path": str(path),
            "cohortKey": assessment.get("cohortKey"),
            "dimensions": [
                {
                    "dimensionCode": item.get("dimensionCode"),
                    "observedScore": item.get("observedScore"),
                    "evidenceGrade": item.get("evidenceGrade"),
                }
                for item in assessment.get("dimensions", []) if isinstance(item, dict)
            ],
        }
        digest.update(json.dumps(signature, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return f"{model['modelVersion']}:{as_of}:sha256:{digest.hexdigest()[:16]}"


def score_country(country_root: Path, model: dict[str, Any], as_of: str) -> dict[str, Any]:
    company_files = sorted((country_root / "companies").glob("*/company.json"))
    companies = [(path, load_json(path)) for path in company_files]
    lead_companies = [
        (path, value) for path, value in companies
        if isinstance(value.get("assessment"), dict)
        and value["assessment"].get("assessmentType") == "lead_value"
        and value["assessment"].get("modelVersion") == model["modelVersion"]
    ]
    version = baseline_version(model, as_of, lead_companies)
    policy = model["cohortPolicy"]
    minimum = int(policy["minimumComparableCompanies"])
    eligible_grades = set(policy["eligibleBaselineEvidenceGrades"])
    definitions = {item["dimensionCode"]: item for item in model["dimensions"]}
    groups: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for path, company in lead_companies:
        key = company["assessment"].get("cohortKey")
        if key:
            groups.setdefault(str(key), []).append((path, company))

    cohort_artifacts: list[dict[str, Any]] = []
    baselines: dict[str, dict[str, float]] = {}
    for cohort_key, members in sorted(groups.items()):
        dimension_artifacts: list[dict[str, Any]] = []
        cohort_baselines: dict[str, float] = {}
        for code, definition in definitions.items():
            values: list[float] = []
            for _, company in members:
                dimension = next(
                    (item for item in company["assessment"].get("dimensions", []) if item.get("dimensionCode") == code),
                    None,
                )
                if not isinstance(dimension, dict):
                    continue
                observed = dimension.get("observedScore")
                if isinstance(observed, (int, float)) and dimension.get("evidenceGrade") in eligible_grades:
                    values.append(float(observed))
            raw_median = statistics.median(values) if len(values) >= minimum else None
            dimension_policy = policy["dimensionPolicies"][code]
            maximum = round(definition["maxScore"] * dimension_policy["maximumBaselineFraction"], 4)
            baseline = round(min(float(raw_median), maximum), 4) if raw_median is not None else None
            if baseline is not None:
                cohort_baselines[code] = baseline
            dimension_artifacts.append({
                "dimensionCode": code,
                "eligibleCompanyCount": len(values),
                "rawMedian": raw_median,
                "maximumBaseline": maximum,
                "baselineScore": baseline,
                "status": "available" if baseline is not None else "insufficient_sample",
            })
        baselines[cohort_key] = cohort_baselines
        cohort_artifacts.append({
            "cohortKey": cohort_key,
            "companyCount": len(members),
            "dimensions": dimension_artifacts,
        })

    updated: list[str] = []
    pending: list[str] = []
    for path, company in lead_companies:
        assessment = company["assessment"]
        cohort_key = str(assessment.get("cohortKey") or "")
        cohort_baselines = baselines.get(cohort_key, {})
        missing = sorted(set(definitions) - set(cohort_baselines))
        if missing:
            assessment["status"] = "pending_cohort_baseline"
            assessment["overallScore"] = None
            assessment["grade"] = None
            assessment["cohortBaselineVersion"] = None
            assessment["cohortAsOf"] = None
            assessment["gapCodes"] = sorted({
                *[code for code in assessment.get("gapCodes", []) if not str(code).startswith("cohort_baseline_insufficient:")],
                "cohort_baseline_required",
                *[f"cohort_baseline_insufficient:{code}" for code in missing],
            })
            for dimension in assessment.get("dimensions", []):
                dimension["baselineScore"] = None
                dimension["finalDimensionScore"] = None
            assessment["overallConclusion"] = (
                f"主任务中的同类型 cohort 样本不足 {minimum} 家，等待形成统一中位数基线。"
            )
            pending.append(str(path))
            atomic_write(path, company)
            continue

        final_total = 0.0
        for dimension in assessment["dimensions"]:
            code = dimension["dimensionCode"]
            baseline = cohort_baselines[code]
            observed = dimension.get("observedScore")
            weight = float(dimension.get("evidenceWeight") or 0)
            observed_value = float(observed) if isinstance(observed, (int, float)) else 0.0
            fair = weight * observed_value + (1 - weight) * baseline
            dimension_cap = definitions[code]["maxScore"]
            for cap_code in assessment.get("capCodes", []) + dimension.get("capCodes", []):
                dimension_cap = min(
                    dimension_cap,
                    model.get("dimensionCaps", {}).get(cap_code, {}).get(code, dimension_cap),
                )
            fair = round(min(fair, dimension_cap), 2)
            dimension["baselineScore"] = baseline
            dimension["finalDimensionScore"] = fair
            dimension["level"] = score_level(fair, definitions[code]["anchors"])
            final_total += fair
        total = round(final_total, 2)
        for cap_code in assessment.get("capCodes", []):
            if cap_code in model.get("caps", {}):
                total = min(total, float(model["caps"][cap_code]))
        assessment["status"] = "completed"
        assessment["overallScore"] = total
        assessment["grade"] = rating(
            model, total, float(assessment.get("informationCompleteness") or 0),
            assessment["dimensions"], assessment.get("capCodes", []),
        )
        assessment["cohortBaselineVersion"] = version
        assessment["cohortAsOf"] = as_of
        assessment["gapCodes"] = sorted({
            code for code in assessment.get("gapCodes", [])
            if code != "cohort_baseline_required" and not str(code).startswith("cohort_baseline_insufficient:")
        })
        assessment["overallConclusion"] = f"主任务已使用 {cohort_key} 同版本中位数基线完成公平价值评分。"
        updated.append(str(path))
        atomic_write(path, company)

    artifact = {
        "modelCode": model["modelCode"],
        "modelVersion": model["modelVersion"],
        "baselineVersion": version,
        "asOf": as_of,
        "minimumComparableCompanies": minimum,
        "cohorts": cohort_artifacts,
    }
    artifact_path = country_root / "Scoring" / "lead-value-cohort.json"
    atomic_write(artifact_path, artifact)
    return {
        "countryRoot": str(country_root),
        "baselineArtifact": str(artifact_path),
        "baselineVersion": version,
        "updatedCompanyFiles": updated,
        "pendingCompanyFiles": pending,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("country_root")
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()
    result = score_country(
        Path(args.country_root).expanduser().resolve(),
        load_json(Path(args.model).expanduser().resolve()),
        args.as_of,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
