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
from urllib.parse import urlparse


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


def _domain(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    parsed = urlparse(text if "://" in text else f"https://{text}")
    host = (parsed.hostname or "").casefold()
    return host[4:] if host.startswith("www.") else host


def customer_indexes(country_roots: list[Path]) -> dict[str, dict[str, list[tuple[Path, dict[str, Any]]]]]:
    names: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    domains: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    registrations: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    paths: list[Path] = []
    for country_root in country_roots:
        paths.extend(sorted((country_root / "companies").glob("*/company.json")))
    for path in paths:
        value = load_json(path)
        name = str(value.get("company", {}).get("companyName") or path.parent.name).strip()
        identity = (path, value)
        all_names = [name]
        for alias in value.get("aliases", []):
            if isinstance(alias, dict):
                candidate = alias.get("name") or alias.get("alias") or alias.get("value")
            else:
                candidate = alias
            if candidate:
                all_names.append(str(candidate).strip())
        for candidate in all_names:
            names.setdefault(candidate.casefold(), []).append(identity)
        for website in value.get("websites", []):
            candidate = website.get("url") or website.get("website") or website.get("domain") if isinstance(website, dict) else website
            domain = _domain(candidate)
            if domain:
                domains.setdefault(domain, []).append(identity)
        for registration in value.get("registrations", []):
            if not isinstance(registration, dict):
                continue
            candidate = registration.get("registrationNumber") or registration.get("number") or registration.get("value")
            if candidate:
                registrations.setdefault(str(candidate).strip().casefold(), []).append(identity)
    return {"names": names, "domains": domains, "registrations": registrations}


def unique_matches(matches: list[tuple[Path, dict[str, Any]]]) -> list[tuple[Path, dict[str, Any]]]:
    result: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path, value in matches:
        result[str(path.resolve())] = (path, value)
    return list(result.values())


def resolve_customer(
    relationship: dict[str, Any], display_name: str,
    indexes: dict[str, dict[str, list[tuple[Path, dict[str, Any]]]]],
) -> list[tuple[Path, dict[str, Any]]]:
    identity = relationship.get("relatedPartyIdentity")
    strong_candidates: list[list[tuple[Path, dict[str, Any]]]] = []
    if isinstance(identity, dict):
        registration = identity.get("registrationNumber")
        website = identity.get("website") or identity.get("primaryDomain")
        legal_name = identity.get("legalName")
        if registration:
            strong_candidates.append(indexes["registrations"].get(str(registration).strip().casefold(), []))
        if website and _domain(website):
            strong_candidates.append(indexes["domains"].get(_domain(website), []))
        if legal_name:
            strong_candidates.append(indexes["names"].get(str(legal_name).strip().casefold(), []))
    elif isinstance(identity, str) and _domain(identity):
        strong_candidates.append(indexes["domains"].get(_domain(identity), []))
    for candidates in strong_candidates:
        unique = unique_matches(candidates)
        if len(unique) == 1:
            return unique
        if len(unique) > 1:
            return unique
    return unique_matches(indexes["names"].get(display_name.casefold(), []))


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


def aggregate(country_root: Path, competitor_dir: Path, as_of: str, customer_roots: list[Path] | None = None) -> dict[str, Any]:
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

    roots = [country_root, *(customer_roots or [])]
    indexes = customer_indexes(list(dict.fromkeys(path.resolve() for path in roots)))
    customers: list[dict[str, Any]] = []
    scores: list[float] = []
    for key in sorted(grouped, key=lambda item: (display_names[item].casefold(), item[1])):
        matches = resolve_customer(grouped[key][0], display_names[key], indexes)
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
            "companyName": display_names[key],
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
    parser.add_argument("--customer-root", action="append", default=[], help="Additional country root containing customer Company files")
    args = parser.parse_args()
    portfolio = aggregate(
        Path(args.country_root).expanduser().resolve(),
        Path(args.competitor_dir).expanduser().resolve(),
        args.as_of,
        [Path(value).expanduser().resolve() for value in args.customer_root],
    )
    print(json.dumps(portfolio, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
