#!/usr/bin/env python3
"""Validate the GETO SearchLexicon and its recall/classification regressions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROLES = {
    "developer", "main_contractor", "subcontractor", "agent_consultant_pm",
    "distributor_trading", "design_consulting_supervision_other",
}
REQUIRED_TERMS = {
    "volumetric modular construction", "vmc", "offsite construction",
    "off-site manufacturing", "modular housing", "prefabricated steel structure",
    "dfma", "concrete", "high-rise", "residential", "formwork", "mining camp",
    "site accommodation", "manufacturer", "factory", "system owner", "brand owner",
    "rental", "distributor", "installer", "dismantling", "labor",
}
REQUIRED_SEEDS = {
    "freecity vmc recall", "framework name false positive", "formwork installer only",
    "outsourced own brand", "channel rental competitor",
}
LIST_FIELDS = {
    "projectScenario", "technology", "method", "positiveTerms", "synonyms",
    "abbreviations", "negativeTerms", "queryTemplates", "sourceChannels",
}


def validate(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["$: lexicon must be an object"]
    for field in ("schemaVersion", "lexiconVersion"):
        if not value.get(field):
            errors.append(f"$.{field} is required")
    entries = value.get("entries")
    if not isinstance(entries, list) or not entries:
        return errors + ["$.entries must be a non-empty array"]
    covered_roles: set[str] = set()
    all_terms: set[str] = set()
    for index, entry in enumerate(entries):
        path = f"$.entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{path} must be an object")
            continue
        for field in ("marketCode", "language", "laneCode", "companyRole", "productCode"):
            if not entry.get(field):
                errors.append(f"{path}.{field} is required")
        for field in LIST_FIELDS:
            if not isinstance(entry.get(field), list):
                errors.append(f"{path}.{field} must be an array")
            else:
                all_terms.update(str(item).casefold() for item in entry[field])
        if entry.get("companyRole") in ROLES:
            covered_roles.add(str(entry["companyRole"]))
        for template in entry.get("queryTemplates", []):
            if "{" not in str(template) and len(str(template).split()) < 3:
                errors.append(f"{path}.queryTemplates contains an underspecified template")
    missing_roles = sorted(ROLES - covered_roles)
    if missing_roles:
        errors.append(f"$.entries missing company roles: {missing_roles}")
    flattened = " ".join(sorted(all_terms))
    missing_terms = sorted(term for term in REQUIRED_TERMS if term not in flattened)
    if missing_terms:
        errors.append(f"$.entries missing required recall terms: {missing_terms}")

    seeds = value.get("regressionSeeds")
    if not isinstance(seeds, list):
        errors.append("$.regressionSeeds must be an array")
        seeds = []
    names: set[str] = set()
    for index, seed in enumerate(seeds):
        if not isinstance(seed, dict):
            errors.append(f"$.regressionSeeds[{index}] must be an object")
            continue
        names.add(str(seed.get("name") or "").casefold())
        for field in ("queryText", "expectedClassificationBoundary"):
            if not seed.get(field):
                errors.append(f"$.regressionSeeds[{index}].{field} is required")
        if seed.get("expectedRecall") is not True:
            errors.append(f"$.regressionSeeds[{index}].expectedRecall must be true")
    missing_seeds = sorted(REQUIRED_SEEDS - names)
    if missing_seeds:
        errors.append(f"$.regressionSeeds missing required cases: {missing_seeds}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lexicon", nargs="?", default=str(Path(__file__).resolve().parents[1] / "references/search-lexicon.json"))
    args = parser.parse_args()
    path = Path(args.lexicon).expanduser().resolve()
    try:
        errors = validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as error:
        errors = [str(error)]
    print(json.dumps({"file": str(path), "valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
