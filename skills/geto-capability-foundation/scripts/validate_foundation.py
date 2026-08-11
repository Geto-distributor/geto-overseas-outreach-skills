#!/usr/bin/env python3
"""Validate GETO capability foundation references and evidence boundaries."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
REFERENCES = ROOT / "references"


def load(name: str, errors: list[str]) -> dict[str, Any]:
    path = REFERENCES / name
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{name}: {error}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{name}: root must be an object")
        return {}
    return value


def unique(items: list[Any], key: str, label: str, errors: list[str]) -> set[str]:
    values = [item.get(key) for item in items if isinstance(item, dict)]
    if len(values) != len(items) or any(not value for value in values):
        errors.append(f"{label}: every item requires {key}")
    duplicates = [value for value, count in Counter(values).items() if value and count > 1]
    if duplicates:
        errors.append(f"{label}: duplicate {key}: {duplicates}")
    return {str(value) for value in values if value}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    manifest = load("foundation-manifest.json", errors)
    required = manifest.get("requiredResources", [])
    if not isinstance(required, list) or not required:
        errors.append("foundation-manifest.json: requiredResources must be a non-empty array")
        required = []
    documents = {name: load(name, errors) for name in required}

    products = documents.get("product-catalog.json", {}).get("products", [])
    scenarios = documents.get("scenario-map.json", {}).get("scenarios", [])
    roles = documents.get("icp-buyer-roles.json", {}).get("roleCodes", [])
    cases = documents.get("case-register.json", {}).get("cases", [])
    relationships = documents.get("relationship-assets.json", {}).get("relationshipAssets", [])
    sources = documents.get("source-register.json", {}).get("sources", [])
    seeds_doc = documents.get("competitor-seeds.json", {})

    product_keys = unique(products, "productCode", "products", errors)
    scenario_keys = unique(scenarios, "scenarioCode", "scenarios", errors)
    role_keys = unique(roles, "roleCode", "roleCodes", errors)
    case_keys = unique(cases, "caseKey", "cases", errors)
    source_keys = unique(sources, "sourceKey", "sources", errors)
    unique(relationships, "assetKey", "relationshipAssets", errors)

    evidence_codes = set(manifest.get("evidenceStatusCodes", []))
    for label, items in (("sources", sources), ("cases", cases), ("relationshipAssets", relationships)):
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{label}[{index}] must be an object")
                continue
            status = item.get("evidenceStatus")
            if status not in evidence_codes:
                errors.append(f"{label}[{index}] has invalid evidenceStatus={status}")
            item_sources = item.get("sourceKeys", []) or []
            for source_key in item_sources:
                if source_key not in source_keys:
                    errors.append(f"{label}[{index}] references unknown sourceKey={source_key}")
            if label != "sources" and status in {"company_published", "independent_verified"} and not item_sources:
                errors.append(f"{label}[{index}] with {status} requires sourceKeys")

    for index, product in enumerate(products):
        for source_key in product.get("sourceKeys", []) or []:
            if source_key not in source_keys:
                errors.append(f"products[{index}] references unknown sourceKey={source_key}")

    for index, scenario in enumerate(scenarios):
        for product_key in scenario.get("productCodes", []) or []:
            if product_key not in product_keys:
                errors.append(f"scenarios[{index}] references unknown productCode={product_key}")
        for role_key in scenario.get("targetRoleCodes", []) or []:
            if role_key not in role_keys:
                errors.append(f"scenarios[{index}] references unknown roleCode={role_key}")
        for case_key in scenario.get("caseKeys", []) or []:
            if case_key not in case_keys:
                errors.append(f"scenarios[{index}] references unknown caseKey={case_key}")

    for index, case in enumerate(cases):
        for product_key in case.get("productCodes", []) or []:
            if product_key not in product_keys:
                errors.append(f"cases[{index}] references unknown productCode={product_key}")
        for scenario_key in case.get("scenarioCodes", []) or []:
            if scenario_key not in scenario_keys:
                errors.append(f"cases[{index}] references unknown scenarioCode={scenario_key}")
        if case.get("relationshipUseAllowed") and not case.get("namedCounterparties"):
            errors.append(f"cases[{index}] permits relationship use without a named counterparty")

    for index, relationship in enumerate(relationships):
        for case_key in relationship.get("caseKeys", []) or []:
            if case_key not in case_keys:
                errors.append(f"relationshipAssets[{index}] references unknown caseKey={case_key}")

    if seeds_doc.get("seedOnly") is not True:
        errors.append("competitor-seeds.json must declare seedOnly=true")
    for index, source in enumerate(sources):
        if not source.get("url") or not source.get("allowedClaims"):
            errors.append(f"sources[{index}] requires url and allowedClaims")
        if source.get("retrievedOn") is None:
            warnings.append(f"sources[{index}] has no retrievedOn; refresh before time-sensitive external use")

    forbidden = ("databaseId", "sqlPatch", "sheetName", "excelImporter")
    serialized = json.dumps(documents, ensure_ascii=False)
    for token in forbidden:
        if token in serialized:
            errors.append(f"foundation contains forbidden delivery token: {token}")

    digest = hashlib.sha256()
    for name in sorted(required):
        path = REFERENCES / name
        if path.exists():
            digest.update(name.encode("utf-8"))
            digest.update(path.read_bytes())
    result = {
        "valid": not errors,
        "foundationKey": manifest.get("foundationKey"),
        "asOf": manifest.get("asOf"),
        "contentHash": f"sha256:{digest.hexdigest()}",
        "counts": {
            "products": len(products),
            "scenarios": len(scenarios),
            "buyerRoles": len(roles),
            "cases": len(cases),
            "relationshipAssets": len(relationships),
            "sources": len(sources),
        },
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
