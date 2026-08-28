#!/usr/bin/env python3
"""Require explicit Markdown approval before inquiry DOCX/PDF publication."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {"approved", "review_skipped_by_user"}
REQUIRED_FIELDS = {
    "status", "reportPath", "reportSha256", "reviewedOn", "reviewedBy", "instructionRef",
}


def _publication_files(company: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item for item in company.get("reportFiles", [])
        if isinstance(item, dict) and item.get("format") in {"docx", "pdf"}
    ]


def validate_publication(company_dir: Path, company: dict[str, Any]) -> list[str]:
    publications = _publication_files(company)
    if not publications:
        return []

    errors: list[str] = []
    review_path = company_dir / "Additional" / "report-review.json"
    if not review_path.is_file():
        return [
            "publication gate: Additional/report-review.json is required before DOCX/PDF publication"
        ]
    try:
        review = json.loads(review_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [f"publication gate: cannot read report-review.json: {error}"]
    if not isinstance(review, dict):
        return ["publication gate: report-review.json must be an object"]

    missing = sorted(REQUIRED_FIELDS - set(review))
    extra = sorted(set(review) - REQUIRED_FIELDS)
    if missing:
        errors.append(f"publication gate: report-review.json missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"publication gate: report-review.json unsupported fields: {', '.join(extra)}")
    if review.get("status") not in ALLOWED_STATUSES:
        errors.append("publication gate: status must be approved or review_skipped_by_user")
    if review.get("reviewedBy") != "user":
        errors.append("publication gate: reviewedBy must be user")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(review.get("reviewedOn") or "")):
        errors.append("publication gate: reviewedOn must use YYYY-MM-DD")
    if not str(review.get("instructionRef") or "").strip():
        errors.append("publication gate: instructionRef must record explicit user approval or skip")

    report_value = str(review.get("reportPath") or "")
    report_path = Path(report_value)
    if not report_path.is_absolute():
        report_path = company_dir / report_path
    try:
        report_path = report_path.resolve()
        report_path.relative_to(company_dir.resolve())
    except (OSError, ValueError):
        errors.append("publication gate: reportPath must resolve inside the company directory")
        return errors
    if report_path.name != "report.md" or not report_path.is_file():
        errors.append("publication gate: reportPath must identify the existing company report.md")
        return errors

    digest = hashlib.sha256(report_path.read_bytes()).hexdigest()
    if review.get("reportSha256") != digest:
        errors.append("publication gate: report.md changed after user review; obtain approval again")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("company_dir")
    args = parser.parse_args()
    company_dir = Path(args.company_dir).expanduser().resolve()
    try:
        company = json.loads((company_dir / "company.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 1
    errors = validate_publication(company_dir, company)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if _publication_files(company):
        print("Inquiry publication gate passed")
    else:
        print("No DOCX/PDF publication requested; Markdown remains the default deliverable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
