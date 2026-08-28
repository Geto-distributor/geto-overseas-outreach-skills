#!/usr/bin/env python3
"""Validate a country-level GETO ResearchBundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from research_bundle import (
    CAPABILITY_CONTEXT_FIELDS, SECRET_PATTERNS, all_evidence, format_result,
    load_json, validate_company, validate_inquiry_report,
)

INQUIRY_SCRIPTS = Path(__file__).resolve().parents[2] / "geto-diligence-inquiry" / "scripts"
sys.path.insert(0, str(INQUIRY_SCRIPTS))
from validate_publication_gate import validate_publication  # noqa: E402


def validate(root: Path, company_dir: Path | None = None) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []
    progress = root / "progress.md"
    companies_root = root / "companies"
    if company_dir is None and not re.fullmatch(r"[A-Z]{2}-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", root.name):
        errors.append("country directory must use <ISO2>-<English-Display-Name>")
    if company_dir is None and not progress.is_file():
        errors.append("progress.md is required at the country root")
    if company_dir is None and not companies_root.is_dir():
        errors.append("companies/ is required at the country root")
        return errors, warnings, infos

    company_dirs = [company_dir] if company_dir is not None else sorted(path for path in companies_root.iterdir() if path.is_dir())
    if not company_dirs:
        warnings.append("companies/: no company workspaces found")
    for company_dir in company_dirs:
        company_json = company_dir / "company.json"
        report = company_dir / "report.md"
        if not company_json.is_file():
            errors.append(f"{company_dir.name}/company.json is missing")
            continue
        if not report.is_file():
            errors.append(f"{company_dir.name}/report.md is missing")
        try:
            value = load_json(company_json)
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{company_json}: {error}")
            continue
        local_errors, local_warnings, local_infos = validate_company(value)
        errors.extend(f"{company_dir.name}: {item}" for item in local_errors)
        warnings.extend(f"{company_dir.name}: {item}" for item in local_warnings)
        infos.extend(f"{company_dir.name}: {item}" for item in local_infos)
        if report.is_file():
            try:
                report_text = report.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as error:
                errors.append(f"{company_dir.name}: report.md cannot be read: {error}")
            else:
                errors.extend(
                    f"{company_dir.name}: {item}" for item in validate_inquiry_report(report_text, value)
                )
        if isinstance(value.get("inquiryAssessment"), dict) and value["inquiryAssessment"].get("status") != "not_requested":
            errors.extend(
                f"{company_dir.name}: {item}" for item in validate_publication(company_dir, value)
            )
        assessment = value.get("assessment", {})
        if isinstance(assessment, dict) and assessment.get("status") != "not_requested":
            context_file = company_dir / "RisksAndAssessment" / "capability-context.json"
            if not context_file.is_file():
                errors.append(f"{company_dir.name}: RisksAndAssessment/capability-context.json is required for assessment")
            else:
                try:
                    context_value = load_json(context_file)
                except (OSError, json.JSONDecodeError) as error:
                    errors.append(f"{company_dir.name}: {context_file}: {error}")
                else:
                    if not isinstance(context_value, dict) or set(context_value) != CAPABILITY_CONTEXT_FIELDS:
                        errors.append(
                            f"{company_dir.name}: capability-context.json must contain the direct contextRef fields"
                        )
                    if context_value != assessment.get("capabilityContext"):
                        errors.append(
                            f"{company_dir.name}: capability-context.json differs from assessment.capabilityContext"
                        )
            if assessment.get("status") == "completed":
                baseline_file = root / "Scoring" / "lead-value-cohort.json"
                if not baseline_file.is_file():
                    errors.append(f"{company_dir.name}: Scoring/lead-value-cohort.json is required for completed lead assessment")
                else:
                    try:
                        baseline_value = load_json(baseline_file)
                    except (OSError, json.JSONDecodeError) as error:
                        errors.append(f"{company_dir.name}: {baseline_file}: {error}")
                    else:
                        if baseline_value.get("baselineVersion") != assessment.get("cohortBaselineVersion"):
                            errors.append(f"{company_dir.name}: cohort baseline version differs from country artifact")
                        cohort_keys = {
                            item.get("cohortKey") for item in baseline_value.get("cohorts", [])
                            if isinstance(item, dict)
                        }
                        if assessment.get("cohortKey") not in cohort_keys:
                            errors.append(f"{company_dir.name}: cohortKey is missing from country baseline artifact")
        if all_evidence(value) and not (company_dir / "Sources" / "sources.md").is_file():
            errors.append(f"{company_dir.name}/Sources/sources.md is missing")
        for index, report_file in enumerate(value.get("reportFiles", [])):
            if not isinstance(report_file, dict) or not report_file.get("path"):
                errors.append(f"{company_dir.name}: reportFiles[{index}].path is required")
                continue
            target = Path(str(report_file["path"]))
            if not target.is_absolute():
                target = company_dir / target
            if not target.exists():
                errors.append(f"{company_dir.name}: reportFiles[{index}] does not exist: {target}")

    scan_root = company_dir if company_dir is not None else root
    for path in scan_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".txt", ".csv"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            errors.append(f"possible secret leak: {path.relative_to(scan_root)}")
    return sorted(set(errors)), sorted(set(warnings)), sorted(set(infos))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("country_root", nargs="?")
    parser.add_argument("--company-dir")
    parser.add_argument("--include-infos", action="store_true")
    args = parser.parse_args()
    if not args.country_root and not args.company_dir:
        parser.error("provide country_root or --company-dir")
    company_dir = Path(args.company_dir).expanduser().resolve() if args.company_dir else None
    if company_dir:
        root = company_dir.parent.parent if company_dir.parent.name == "companies" else company_dir.parent
    else:
        root = Path(args.country_root).expanduser().resolve()
    errors, warnings, infos = validate(root, company_dir)
    mode = "company" if company_dir else "country"
    print(json.dumps({
        "mode": mode, "root": str(company_dir or root),
        **format_result(errors, warnings, infos, args.include_infos),
    }, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
