#!/usr/bin/env python3
"""Aggregate verified competitor customers and their current lead-value scores."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


PORTFOLIO_MODEL_CODE = "GETO_COMPETITOR_CUSTOMER_PORTFOLIO"
PORTFOLIO_MODEL_VERSION = "2026-08-19"
CUSTOMER_VALUE_MODEL_CODE = "GETO_LEAD_VALUE"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def confirmed_competitor(company: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict)
        and item.get("classification") == "competitor"
        and item.get("status") == "confirmed"
        for item in company.get("researchClassifications", [])
    )


def customer_index(country_root: Path) -> dict[str, list[tuple[Path, dict[str, Any]]]]:
    result: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for path in sorted((country_root / "companies").glob("*/company.json")):
        value = load_json(path)
        name = str(value.get("company", {}).get("companyName") or path.parent.name).strip()
        result.setdefault(name.casefold(), []).append((path, value))
    return result


def unique_evidence(relationships: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for relationship in relationships:
        for item in relationship.get("evidence", []):
            if not isinstance(item, dict):
                continue
            marker = json.dumps(item, ensure_ascii=False, sort_keys=True)
            if marker not in seen:
                seen.add(marker)
                result.append(item)
    return result


def aggregate(country_root: Path, competitor_dir: Path, as_of: str) -> dict[str, Any]:
    datetime.strptime(as_of, "%Y-%m-%d")
    competitor_path = competitor_dir / "company.json"
    competitor = load_json(competitor_path)
    if not confirmed_competitor(competitor):
        raise ValueError("competitor company requires a confirmed competitor classification")

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    display_names: dict[tuple[str, str], str] = {}
    for relationship in competitor.get("relationships", []):
        if not isinstance(relationship, dict) or relationship.get("reviewDecision") != "verified_customer":
            continue
        if relationship.get("relationshipType") != "customer":
            raise ValueError("verified_customer relationshipType must be customer")
        name = str(relationship.get("counterpartyName") or "").strip()
        if not name:
            raise ValueError("verified_customer relationship requires counterpartyName")
        key = (name.casefold(), str(relationship.get("country") or "").strip().casefold())
        display_names.setdefault(key, name)
        grouped.setdefault(key, []).append(relationship)

    index = customer_index(country_root)
    customers: list[dict[str, Any]] = []
    scores: list[float] = []
    for key in sorted(grouped, key=lambda item: (display_names[item].casefold(), item[1])):
        matches = index.get(key[0], [])
        if len(matches) != 1:
            raise ValueError(
                f"verified customer {display_names[key]!r} must resolve to exactly one company.json; found {len(matches)}"
            )
        _, customer = matches[0]
        profile = customer.get("company", {})
        assessment = customer.get("assessment", {})
        completed = (
            isinstance(assessment, dict)
            and assessment.get("status") == "completed"
            and assessment.get("modelCode") == CUSTOMER_VALUE_MODEL_CODE
            and isinstance(assessment.get("overallScore"), (int, float))
        )
        score = round(float(assessment["overallScore"]), 2) if completed else None
        if score is not None:
            scores.append(score)
        customers.append({
            "companyName": profile.get("companyName") or display_names[key],
            "country": profile.get("country"),
            "relationshipCount": len(grouped[key]),
            "customerAssessmentStatus": assessment.get("status", "not_requested") if isinstance(assessment, dict) else "not_requested",
            "customerValueScore": score,
            "customerValueModelVersion": assessment.get("modelVersion") if completed else None,
            "cohortBaselineVersion": assessment.get("cohortBaselineVersion") if completed else None,
            "assessedOn": assessment.get("assessedOn") if completed else None,
            "evidence": unique_evidence(grouped[key]),
        })

    verified = len(customers)
    scored = len(scores)
    coverage = round(scored / verified, 4) if verified else 0.0
    average = round(sum(scores) / scored, 1) if scored else None
    if verified == 0:
        status = "no_verified_customers"
    elif scored == 0:
        status = "pending_customer_scores"
    elif scored < verified:
        status = "partial_coverage"
    else:
        status = "completed"

    portfolio = {
        "assessmentType": "competitor_customer_portfolio",
        "status": status,
        "modelCode": PORTFOLIO_MODEL_CODE,
        "modelVersion": PORTFOLIO_MODEL_VERSION,
        "customerValueModelCode": CUSTOMER_VALUE_MODEL_CODE,
        "asOf": as_of,
        "verifiedCustomerCount": verified,
        "scoredCustomerCount": scored,
        "customerScoreCoverage": coverage,
        "averageCustomerValueScore": average,
        "customers": customers,
    }
    competitor["competitorCustomerPortfolio"] = portfolio
    atomic_write(competitor_path, competitor)
    return portfolio


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--country-root", required=True)
    parser.add_argument("--competitor-dir", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args()
    portfolio = aggregate(
        Path(args.country_root).expanduser().resolve(),
        Path(args.competitor_dir).expanduser().resolve(),
        args.as_of,
    )
    print(json.dumps(portfolio, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
