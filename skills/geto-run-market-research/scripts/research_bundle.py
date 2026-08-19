#!/usr/bin/env python3
"""Shared helpers for GETO local ResearchBundle validation."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ARRAY_FIELDS = (
    "aliases", "registrations", "capitalRecords", "websites", "addresses",
    "marketPresence", "socialChannels", "researchClassifications", "companyRoles",
    "productsAndServices", "projects", "relationships", "contacts",
    "licensesAndCertifications", "financialRecords", "newsAndSocialMedia",
    "customsTransactions", "lawsuitsAndCompliance", "inquiries", "risks",
    "missingInformation", "recommendedActions", "additionalInformation", "reportFiles",
)
EVIDENCE_FIELDS = tuple(field for field in ARRAY_FIELDS if field != "reportFiles")
FORBIDDEN_LOCAL_KEYS = {
    "runId", "taskId", "companyKey", "claimKey", "sourceKey", "claimSourceLinks",
    "ownerUserId", "identityKey", "visibility", "deletedAt", "businessActivities",
}
ALLOWED_RELATIONS = {"supports", "refutes", "context"}
ALLOWED_SOURCE_TYPES = {
    "official_website", "registry", "government", "court", "financial_report",
    "media", "social_media", "provider", "customer_document", "other",
}
CONTROL_ROLES = {
    "manufacturer", "system_owner", "brand_owner", "distributor", "reseller",
    "rental_provider",
}
INSTALL_ONLY_ROLES = {"installer", "service_contractor"}
TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}
SECRET_PATTERNS = (
    re.compile(r"\bomx_(?:test|live)_[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\btw_(?:test|live)_[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"(?i)(api[-_ ]?key|authorization|bearer|cookie)\s*[:=]\s*[^\s,;]{8,}"),
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def empty_company(company_name: str = "", country: str = "") -> dict[str, Any]:
    value: dict[str, Any] = {
        "company": {
            "companyName": company_name,
            "entityType": "operating_company",
            "country": country,
            "status": "unknown",
            "summary": "",
            "researchConclusion": "",
            "evidence": [],
        }
    }
    value.update({field: [] for field in ARRAY_FIELDS})
    value["assessment"] = {}
    value["researchStatus"] = "completed_with_gaps"
    value["lastResearchedOn"] = date.today().isoformat()
    return value


def walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


def canonical_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    parts = urlsplit(raw)
    filtered = [
        (key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_KEYS
        and not any(key.lower().startswith(prefix) for prefix in TRACKING_QUERY_PREFIXES)
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(filtered), ""))


def all_evidence(value: Any) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for _, node in walk(value):
        if isinstance(node, dict) and isinstance(node.get("evidence"), list):
            evidence.extend(item for item in node["evidence"] if isinstance(item, dict))
    return evidence


def _has_evidence(item: dict[str, Any]) -> bool:
    return isinstance(item.get("evidence"), list) and bool(item["evidence"])


def _confirmed(item: dict[str, Any]) -> bool:
    return any(
        item.get(field) in {"confirmed", "verified", "active", "own_factory_confirmed"}
        for field in ("status", "verificationStatus", "officialStatus", "manufacturingStatus")
    )


def _contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def validate_company(value: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(value, dict):
        return ["$: company.json must be a JSON object"], warnings

    company = value.get("company")
    if not isinstance(company, dict):
        errors.append("$.company is required and must be an object")
    else:
        for field in ("companyName", "entityType", "country"):
            if not company.get(field):
                errors.append(f"$.company.{field} is required")
        if company.get("entityType") not in {"legal_entity", "operating_company", "corporate_group"}:
            errors.append("$.company.entityType has an invalid value")

    if value.get("researchStatus") not in {"completed", "completed_with_gaps", "identity_conflict"}:
        errors.append("$.researchStatus is required and must use the V2 enum")
    researched_on = value.get("lastResearchedOn")
    try:
        datetime.strptime(str(researched_on), "%Y-%m-%d")
    except ValueError:
        errors.append("$.lastResearchedOn is required in YYYY-MM-DD format")

    for path, node in walk(value):
        if isinstance(node, dict):
            for forbidden in node.keys() & FORBIDDEN_LOCAL_KEYS:
                errors.append(f"{path}.{forbidden}: forbidden local/platform key")

    if _contains_secret(json.dumps(value, ensure_ascii=False)):
        errors.append("$: possible API key, token, cookie, or credential leak")

    for field in ARRAY_FIELDS:
        if field in value and not isinstance(value[field], list):
            errors.append(f"$.{field} must be an array")

    for field in EVIDENCE_FIELDS:
        for index, item in enumerate(value.get(field, [])):
            path = f"$.{field}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{path} must be an object")
                continue
            evidence = item.get("evidence")
            may_be_empty = field == "missingInformation" and item.get("status") == "not_queried"
            if not isinstance(evidence, list) or (not evidence and not may_be_empty):
                errors.append(f"{path}.evidence must contain at least one Evidence item")
            if _confirmed(item) and not _has_evidence(item):
                errors.append(f"{path}: confirmed/verified fact requires Evidence")
            for evidence_index, source in enumerate(evidence or []):
                source_path = f"{path}.evidence[{evidence_index}]"
                if not isinstance(source, dict):
                    errors.append(f"{source_path} must be an object")
                    continue
                if source.get("relation") not in ALLOWED_RELATIONS:
                    errors.append(f"{source_path}.relation must be supports, refutes, or context")
                if source.get("sourceType") not in ALLOWED_SOURCE_TYPES:
                    errors.append(f"{source_path}.sourceType has an invalid value")
                if not source.get("sourceTitle") or not source.get("retrievedOn"):
                    errors.append(f"{source_path} requires sourceTitle and retrievedOn")
                if not source.get("sourceUrl") and source.get("sourceType") != "customer_document":
                    errors.append(f"{source_path}.sourceUrl is required except for customer documents")

    classifications = value.get("researchClassifications", [])
    seen_classifications: set[str] = set()
    for index, item in enumerate(classifications):
        if not isinstance(item, dict):
            continue
        classification = item.get("classification")
        if classification not in {"lead", "competitor"}:
            errors.append(f"$.researchClassifications[{index}].classification must be lead or competitor")
        if classification in seen_classifications:
            warnings.append(f"$.researchClassifications[{index}]: duplicate {classification} classification")
        seen_classifications.add(str(classification))
        if not item.get("reason"):
            warnings.append(f"$.researchClassifications[{index}].reason is missing")
        if item.get("status") == "confirmed" and not _has_evidence(item):
            errors.append(f"$.researchClassifications[{index}]: confirmed classification requires Evidence")

    confirmed_competitors = [
        item for item in classifications
        if isinstance(item, dict) and item.get("classification") == "competitor"
        and item.get("status") == "confirmed"
    ]
    products = [item for item in value.get("productsAndServices", []) if isinstance(item, dict)]
    for index, classification in enumerate(confirmed_competitors):
        country = str(classification.get("country") or "").casefold()
        matching = []
        for product in products:
            markets = {str(item).casefold() for item in product.get("markets", [])}
            roles = set(product.get("commercialRoles", []))
            relevant = product.get("getoRelevance") in {"high", "medium"}
            if relevant and (not country or country in markets) and roles & CONTROL_ROLES and _has_evidence(product):
                matching.append(product)
        if not matching:
            errors.append(
                f"$.researchClassifications competitor[{index}]: confirmed competitor requires "
                "overlapping product, target market, commercial-control role, and Evidence"
            )
        relevant_products = [p for p in products if p.get("getoRelevance") in {"high", "medium"}]
        if relevant_products and all(
            set(product.get("commercialRoles", [])) <= INSTALL_ONLY_ROLES
            for product in relevant_products
        ):
            errors.append("$: installer/service_contractor-only company cannot be confirmed competitor")

    active_regs: dict[tuple[str, str], set[str]] = {}
    for item in value.get("registrations", []):
        if not isinstance(item, dict) or item.get("status") not in {"active", "unknown"}:
            continue
        key = (str(item.get("registrationType")), str(item.get("jurisdiction")))
        number = str(item.get("registrationNumber") or "")
        if number:
            active_regs.setdefault(key, set()).add(number)
    if any(len(numbers) > 1 for numbers in active_regs.values()) and value.get("researchStatus") != "identity_conflict":
        errors.append("$: conflicting strong registration identities require researchStatus=identity_conflict")

    for index, item in enumerate(value.get("missingInformation", [])):
        if isinstance(item, dict) and item.get("status") in {"not_queried", "provider_failed", "outdated", "conflicting"}:
            warnings.append(f"$.missingInformation[{index}]: unresolved {item.get('status')}")

    assessment = value.get("assessment")
    if not isinstance(assessment, dict):
        errors.append("$.assessment must be an object")
    elif assessment:
        if assessment.get("assessmentType") not in {"lead_value", "competitor", "company_risk", "precontract"}:
            errors.append("$.assessment.assessmentType has an invalid value")
        dimensions = assessment.get("dimensions")
        if not isinstance(dimensions, list):
            errors.append("$.assessment.dimensions must be an array")
            dimensions = []
        for index, dimension in enumerate(dimensions):
            path = f"$.assessment.dimensions[{index}]"
            if not isinstance(dimension, dict):
                errors.append(f"{path} must be an object")
                continue
            if not dimension.get("name") or not dimension.get("rationale"):
                errors.append(f"{path} requires name and rationale")
            if not _has_evidence(dimension):
                errors.append(f"{path}.evidence must contain at least one Evidence item")
        if assessment.get("overallScore") is not None or assessment.get("grade"):
            if not dimensions or any(
                not isinstance(item, dict) or item.get("score") is None or not _has_evidence(item)
                for item in dimensions
            ):
                errors.append("$.assessment: overallScore/grade requires complete evidenced dimensions")

    if researched_on:
        for index, contact in enumerate(value.get("contacts", [])):
            if not isinstance(contact, dict) or contact.get("verificationStatus") not in {"verified", "likely"}:
                continue
            try:
                verified = datetime.strptime(str(contact.get("lastVerifiedOn")), "%Y-%m-%d").date()
                researched = datetime.strptime(str(researched_on), "%Y-%m-%d").date()
            except ValueError:
                warnings.append(f"$.contacts[{index}].lastVerifiedOn is missing or invalid")
                continue
            if (researched - verified).days > 365:
                warnings.append(f"$.contacts[{index}] verification is outdated")

    capital_text = " ".join(
        json.dumps(item, ensure_ascii=False) for item in value.get("capitalRecords", []) if isinstance(item, dict)
    )
    if re.search(r"(?i)(cash|revenue|credit|solvency|现金|收入|营收|授信|偿债)", capital_text):
        warnings.append("$.capitalRecords: review possible misuse of capital as cash/revenue/credit evidence")

    for index, item in enumerate(value.get("additionalInformation", [])):
        text = json.dumps(item, ensure_ascii=False).casefold()
        if any(term in text for term in ("financial", "project", "lawsuit", "customs", "contact", "财务", "项目", "诉讼", "海关", "联系人")):
            warnings.append(f"$.additionalInformation[{index}]: may duplicate an existing structured field")

    return sorted(set(errors)), sorted(set(warnings))


def format_result(errors: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "errorCount": len(errors),
        "warningCount": len(warnings),
    }
