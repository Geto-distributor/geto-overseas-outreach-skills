#!/usr/bin/env python3
"""Validate one GETO V2 company.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_bundle import format_result, load_json, validate_company


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("company_json")
    parser.add_argument("--include-infos", action="store_true")
    args = parser.parse_args()
    path = Path(args.company_json).expanduser().resolve()
    try:
        errors, warnings, infos = validate_company(load_json(path))
    except (OSError, json.JSONDecodeError) as error:
        errors, warnings, infos = [f"{path}: {error}"], [], []
    result = {"file": str(path), **format_result(errors, warnings, infos, args.include_infos)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
