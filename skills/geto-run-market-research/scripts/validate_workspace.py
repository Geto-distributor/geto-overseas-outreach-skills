#!/usr/bin/env python3
"""Validate a country-level GETO ResearchBundle."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from research_bundle import SECRET_PATTERNS, all_evidence, format_result, load_json, validate_company


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
    print(json.dumps({"mode": mode, "root": str(company_dir or root), **format_result(errors, warnings, infos)}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
