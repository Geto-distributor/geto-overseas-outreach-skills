#!/usr/bin/env python3
"""Validate a formal inquiry Markdown report for completeness and business readability."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


RUN_MARKET_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "geto-run-market-research" / "scripts"
)
sys.path.insert(0, str(RUN_MARKET_SCRIPTS))

from research_bundle import load_json, validate_inquiry_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_md")
    parser.add_argument("--company-json", required=True)
    args = parser.parse_args()

    report_path = Path(args.report_md).expanduser().resolve()
    company_path = Path(args.company_json).expanduser().resolve()
    try:
        report = report_path.read_text(encoding="utf-8")
        company = load_json(company_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 1

    errors = validate_inquiry_report(report, company)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Inquiry Markdown report passed business-language validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
