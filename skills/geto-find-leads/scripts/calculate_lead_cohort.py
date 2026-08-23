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


def cohort_baseline_evidence(
    country_root: Path, version: str, as_of: str, cohort_key: str,
    dimension_code: str, baseline: float,
) -> dict[str, Any]:
    artifact_path = (country_root / "Scoring" / "lead-value-cohort.json").resolve()
    return {
        "sourceTitle": "GETO Lead Value Cohort Baseline",
        "sourceUrl": artifact_path.as_uri(),
        "publisher": "GETO market research main task",
        "sourceType": "other",
        "publishedOn": as_of,
        "retrievedOn": as_of,
        "locator": f"cohort={cohort_key}; dimension={dimension_code}; baselineVersion={version}",
        "excerpt": f"The approved cohort baseline for {dimension_code} is {baseline}.",
        "note": "GETO cohort baseline evidence; this supports only the statistical baseline supplement, not a company-specific observed fact.",
    }


def cohort_zero_fallback_evidence(
    country_root: Path, as_of: str, cohort_key: str,
    dimension_code: str, eligible_count: int,
) -> dict[str, Any]:
    artifact_path = (country_root / "Scoring" / "lead-value-cohort.json").resolve()
    return {
        "sourceTitle": "GETO Lead Value Cohort Zero Fallback",
        "sourceUrl": artifact_path.as_uri(),
        "publisher": "GETO market research main task",
        "sourceType": "other",
        "publishedOn": as_of,
        "retrievedOn": as_of,
        "locator": f"cohort={cohort_key}; dimension={dimension_code}; eligibleCompanyCount={eligible_count}",
        "excerpt": "No usable same-cohort median was available for this dimension; the configured zero-baseline policy set the baseline to 0.",
        "note": "This is a scoring-policy fallback, not a company-specific factual observation. It applies only after the company research pass has recorded no usable evidence for the dimension; it must not be used to convert an unqueried/provider-failed company into a factual zero.",
    }


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
    fallback_policy = policy.get("insufficientBaselineFallback", {})
    use_zero_fallback = fallback_policy.get("mode") == "zero"
    preserve_unknown_for = set(fallback_policy.get("preserveUnknownFor", []))
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
            baseline = round(min(float(raw_median), maximum), 4) if raw_median is not None else (
                0.0 if use_zero_fallback else None
            )
            if baseline is not None:
                cohort_baselines[code] = baseline
            dimension_artifacts.append({
                "dimensionCode": code,
                "eligibleCompanyCount": len(values),
                "rawMedian": raw_median,
                "maximumBaseline": maximum,
                "baselineScore": baseline,
                "status": (
                    "available" if raw_median is not None else
                    "zero_fallback_no_median" if baseline == 0.0 else
                    "insufficient_sample"
                ),
                "fallbackReason": (
                    "no_usable_same_cohort_median" if raw_median is None and baseline == 0.0 else None
                ),
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

        dimension_codes = {
            item.get("dimensionCode") for item in assessment.get("dimensions", [])
            if isinstance(item, dict)
        }
        if dimension_codes != set(definitions):
            assessment["status"] = "pending_cohort_baseline"
            assessment["overallScore"] = None
            assessment["grade"] = None
            assessment["cohortBaselineVersion"] = None
            assessment["cohortAsOf"] = None
            assessment["gapCodes"] = sorted(set(assessment.get("gapCodes", [])) | {"assessment_dimensions_incomplete"})
            for dimension in assessment.get("dimensions", []):
                if isinstance(dimension, dict):
                    dimension["baselineScore"] = None
                    dimension["finalDimensionScore"] = None
            assessment["overallConclusion"] = "assessment 未提供完整六维输入，保持 pending，不能用零分兜底替代缺失维度结构。"
            pending.append(str(path))
            atomic_write(path, company)
            continue

        fallback_codes = {
            item["dimensionCode"] for item in cohort_artifacts
            if item.get("cohortKey") == cohort_key
            for item in item.get("dimensions", [])
            if item.get("status") == "zero_fallback_no_median"
        }
        dimensions_by_code = {
            item.get("dimensionCode"): item for item in assessment.get("dimensions", [])
            if isinstance(item, dict)
        }
        blocked_fallback_codes = set()
        for code in fallback_codes:
            dimension = dimensions_by_code.get(code, {})
            if isinstance(dimension.get("observedScore"), (int, float)):
                continue
            gap_codes = {str(item) for item in dimension.get("gapCodes", [])}
            if company.get("researchStatus") == "identity_conflict" or any(
                marker == gap or marker in gap
                for marker in preserve_unknown_for for gap in gap_codes
            ):
                blocked_fallback_codes.add(code)
        if blocked_fallback_codes:
            assessment["status"] = "pending_cohort_baseline"
            assessment["overallScore"] = None
            assessment["grade"] = None
            assessment["cohortBaselineVersion"] = None
            assessment["cohortAsOf"] = None
            assessment["gapCodes"] = sorted(set(assessment.get("gapCodes", [])) | {
                f"cohort_zero_baseline_blocked:{code}" for code in blocked_fallback_codes
            })
            for dimension in assessment.get("dimensions", []):
                if isinstance(dimension, dict):
                    dimension["baselineScore"] = None
                    dimension["finalDimensionScore"] = None
            assessment["overallConclusion"] = (
                "零分基线不适用于未查询、Provider 失败或主体冲突造成的未知维度，"
                "assessment 保持 pending。"
            )
            pending.append(str(path))
            atomic_write(path, company)
            continue
        final_total = 0.0
        baseline_evidence_items: list[dict[str, Any]] = []
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
            dimension["evidence"] = [
                item for item in dimension.get("evidence", [])
                if not (isinstance(item, dict) and (
                    item.get("note") == "GETO cohort baseline evidence; this supports only the statistical baseline supplement, not a company-specific observed fact."
                    or item.get("note", "").startswith("This is a scoring-policy fallback")
                ))
            ]
            if code in fallback_codes:
                baseline_evidence = cohort_zero_fallback_evidence(
                    country_root, as_of, cohort_key, code,
                    next(item["eligibleCompanyCount"] for item in next(
                        a for a in cohort_artifacts if a.get("cohortKey") == cohort_key
                    )["dimensions"] if item.get("dimensionCode") == code),
                )
                dimension.setdefault("gapCodes", [])
                dimension["gapCodes"] = sorted(set(dimension["gapCodes"]) | {f"cohort_baseline_zero_fallback:{code}"})
                dimension["evidence"].append(baseline_evidence)
                baseline_evidence_items.append(baseline_evidence)
            elif dimension.get("evidenceGrade") == "U" or not isinstance(observed, (int, float)):
                baseline_evidence = cohort_baseline_evidence(
                    country_root, version, as_of, cohort_key, code, baseline,
                )
                dimension["evidence"].append(baseline_evidence)
                baseline_evidence_items.append(baseline_evidence)
            final_total += fair
        total = round(final_total, 2)
        for cap_code in assessment.get("capCodes", []):
            if cap_code in model.get("caps", {}):
                total = min(total, float(model["caps"][cap_code]))
        assessment["status"] = "completed"
        assessment["overallScore"] = total
        completeness_value = assessment.get("informationCompleteness")
        try:
            completeness = float(completeness_value or 0)
        except (TypeError, ValueError):
            completeness = 0.0
        assessment["grade"] = rating(
            model, total, completeness,
            assessment["dimensions"], assessment.get("capCodes", []),
        )
        assessment["cohortBaselineVersion"] = version
        assessment["cohortAsOf"] = as_of
        assessment["evidence"] = [
            item for item in assessment.get("evidence", [])
            if not (isinstance(item, dict) and item.get("note") == "GETO cohort baseline evidence; this supports only the statistical baseline supplement, not a company-specific observed fact.")
        ]
        for item in baseline_evidence_items:
            key = (item.get("sourceUrl"), item.get("locator"))
            if not any((existing.get("sourceUrl"), existing.get("locator")) == key for existing in assessment["evidence"] if isinstance(existing, dict)):
                assessment["evidence"].append(item)
        assessment["gapCodes"] = sorted({
            code for code in assessment.get("gapCodes", [])
            if code != "cohort_baseline_required" and not str(code).startswith("cohort_baseline_insufficient:")
        })
        assessment["gapCodes"] = sorted(set(assessment.get("gapCodes", [])) | {
            f"cohort_baseline_zero_fallback:{code}" for code in fallback_codes
        })
        assessment["overallConclusion"] = (
            f"主任务已使用 {cohort_key} 同版本中位数基线完成公平价值评分；"
            "无可用中位数的维度使用0分基线。"
            if fallback_codes else
            f"主任务已使用 {cohort_key} 同版本中位数基线完成公平价值评分。"
        )
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
