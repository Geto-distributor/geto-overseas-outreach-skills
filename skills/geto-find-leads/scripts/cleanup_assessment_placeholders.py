#!/usr/bin/env python3
"""Remove or correct the legacy lead-assessment placeholder without rescoring companies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from calculate_lead_cohort import atomic_write, load_json, synchronize_assessment_gap


def cleanup(country_root: Path, apply: bool) -> dict[str, object]:
    results = {"removed": [], "corrected": [], "unchanged": []}
    for path in sorted((country_root / "companies").glob("*/company.json")):
        company = load_json(path)
        action = synchronize_assessment_gap(company)
        results[action].append(str(path))
        if apply and action != "unchanged":
            atomic_write(path, company)
    return {
        "countryRoot": str(country_root),
        "apply": apply,
        "removedCount": len(results["removed"]),
        "correctedCount": len(results["corrected"]),
        "unchangedCount": len(results["unchanged"]),
        **results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("country_root")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    result = cleanup(Path(args.country_root).expanduser().resolve(), args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
