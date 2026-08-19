#!/usr/bin/env python3
"""Select a small GETO capability context by codes, query text, and country."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "references"


def load(name: str) -> dict[str, Any]:
    return json.loads((REF / name).read_text(encoding="utf-8"))


def terms(value: str) -> set[str]:
    latin = re.findall(r"[a-z0-9_]+", value.lower())
    chinese_phrases = re.findall(r"[\u4e00-\u9fff]{2,}", value)
    chinese = list(chinese_phrases)
    for phrase in chinese_phrases:
        chinese.extend(phrase[index:index + 2] for index in range(len(phrase) - 1))
    return set(latin + chinese)


def text_score(item: dict[str, Any], query_terms: set[str]) -> int:
    if not query_terms:
        return 0
    text = json.dumps(item, ensure_ascii=False).lower()
    return sum(1 for term in query_terms if term.lower() in text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="")
    parser.add_argument("--country", default=None, help="ISO2 country code")
    parser.add_argument("--product-code", action="append", default=[])
    parser.add_argument("--scenario-code", action="append", default=[])
    parser.add_argument("--role-code", action="append", default=[])
    args = parser.parse_args()

    manifest = load("foundation-manifest.json")
    products = load("product-catalog.json")["products"]
    scenarios = load("scenario-map.json")["scenarios"]
    roles = load("icp-buyer-roles.json")["roleCodes"]
    cases = load("case-register.json")["cases"]
    relationships = load("relationship-assets.json")["relationshipAssets"]
    sources = load("source-register.json")["sources"]
    query_terms = terms(args.query)

    requested_products = set(args.product_code)
    requested_scenarios = set(args.scenario_code)
    requested_roles = set(args.role_code)
    unknown = {
        "productCodes": sorted(requested_products - {item["productCode"] for item in products}),
        "scenarioCodes": sorted(requested_scenarios - {item["scenarioCode"] for item in scenarios}),
        "roleCodes": sorted(requested_roles - {item["roleCode"] for item in roles}),
    }

    scenario_scores = {item["scenarioCode"]: text_score(item, query_terms) for item in scenarios}
    max_scenario_score = max(scenario_scores.values(), default=0)
    scenario_threshold = 1 if max_scenario_score <= 1 else max(2, max_scenario_score // 2)
    selected_scenarios = [
        item for item in scenarios
        if item["scenarioCode"] in requested_scenarios
        or requested_products.intersection(item.get("productCodes", []))
        or requested_roles.intersection(item.get("targetRoleCodes", []))
        or scenario_scores[item["scenarioCode"]] >= scenario_threshold
    ]
    scenario_codes = {item["scenarioCode"] for item in selected_scenarios}
    product_codes = requested_products | {
        code for item in selected_scenarios for code in item.get("productCodes", [])
    }
    role_codes = requested_roles | {
        code for item in selected_scenarios for code in item.get("targetRoleCodes", [])
    }
    if not selected_scenarios and not requested_products and query_terms:
        product_codes |= {item["productCode"] for item in products if text_score(item, query_terms) > 0}
        role_codes |= {item["roleCode"] for item in roles if text_score(item, query_terms) > 0}

    selected_products = [item for item in products if item["productCode"] in product_codes]
    selected_roles = [item for item in roles if item["roleCode"] in role_codes]
    case_codes = {code for item in selected_scenarios for code in item.get("caseKeys", [])}
    selected_cases = [
        item for item in cases
        if item["caseKey"] in case_codes
        and (not args.country or item.get("country") in {None, args.country.upper()})
    ]
    if args.country:
        selected_cases += [
            item for item in cases
            if item.get("country") == args.country.upper()
            and item["caseKey"] not in {case["caseKey"] for case in selected_cases}
            and (not product_codes or product_codes.intersection(item.get("productCodes", [])))
        ]
    selected_relationships = [
        item for item in relationships
        if set(item.get("caseKeys", [])).intersection({case["caseKey"] for case in selected_cases})
    ]
    source_keys = {
        key
        for item in selected_products + selected_cases + selected_relationships
        for key in item.get("sourceKeys", [])
    }

    digest = hashlib.sha256()
    for name in sorted(manifest["requiredResources"]):
        digest.update(name.encode("utf-8"))
        digest.update((REF / name).read_bytes())
    gaps = [f"unknown_{kind}:{value}" for kind, values in unknown.items() for value in values]
    if any(item.get("evidenceStatus") in {"pending_source_mapping", "pending_refresh"} for item in selected_relationships):
        gaps.append("relationship_assets_require_refresh")

    result = {
        "foundationKey": manifest["foundationKey"],
        "foundationVersion": manifest["foundationVersion"],
        "asOf": manifest["asOf"],
        "contentHash": f"sha256:{digest.hexdigest()}",
        "status": "partial" if gaps else "available",
        "selection": {
            "query": args.query or None,
            "country": args.country.upper() if args.country else None,
            "productCodes": sorted(product_codes),
            "scenarioCodes": sorted(scenario_codes),
            "roleCodes": sorted(role_codes),
        },
        "products": selected_products,
        "scenarios": selected_scenarios,
        "buyerRoles": selected_roles,
        "caseAnchors": selected_cases,
        "relationshipAssets": selected_relationships,
        "sources": [item for item in sources if item["sourceKey"] in source_keys],
        "sourceKeys": sorted(source_keys),
        "gaps": gaps,
    }
    result["contextRef"] = {
        "foundationKey": result["foundationKey"],
        "foundationVersion": result["foundationVersion"],
        "asOf": result["asOf"],
        "status": result["status"],
        "contentHash": result["contentHash"],
        "productCodes": result["selection"]["productCodes"],
        "scenarioCodes": result["selection"]["scenarioCodes"],
        "roleCodes": result["selection"]["roleCodes"],
        "caseKeys": sorted(item["caseKey"] for item in selected_cases),
        "gapCodes": result["gaps"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
