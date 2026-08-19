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
    "researchQueries", "missingInformation", "recommendedActions", "additionalInformation", "reportFiles",
)
EVIDENCE_FIELDS = tuple(field for field in ARRAY_FIELDS if field not in {"reportFiles", "researchQueries"})
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
ASSESSMENT_STATUSES = {
    "not_requested", "pending_model", "pending_capability_foundation",
    "incomplete_evidence", "completed",
}
ASSESSMENT_FIELDS = {
    "assessmentType", "status", "modelCode", "modelVersion", "ratingScaleVersion",
    "capabilityContext", "grade", "overallScore", "informationCompleteness",
    "overallConclusion", "assessedOn", "dimensions", "capCodes", "gapCodes",
}
DIMENSION_FIELDS = {
    "dimensionCode", "name", "observedScore", "finalDimensionScore", "maxScore",
    "evidenceGrade", "evidenceWeight", "level", "rationale", "evidence",
    "gapCodes", "capCodes",
}
CAPABILITY_CONTEXT_FIELDS = {
    "foundationKey", "foundationVersion", "asOf", "status", "contentHash",
    "productCodes", "scenarioCodes", "roleCodes", "caseKeys", "gapCodes",
}
REPORT_FILE_FIELDS = {
    "fileName", "path", "format", "reportType", "language", "generatedOn", "description",
}
RESEARCH_QUERY_FIELDS = {
    "topic", "channel", "query", "scope", "status", "checkedOn", "resultCount", "evidence",
}
LEAD_DIMENSIONS = {
    "project_city_value": 15,
    "account_scale": 20,
    "future_project_demand": 20,
    "reachability": 10,
    "payment_capacity": 15,
    "multi_product_fit": 20,
}
EVIDENCE_WEIGHTS = {"A": 1.0, "B": 0.75, "C": 0.5, "U": 0.0}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def empty_company(company_name: str = "", country: str = "", country_code: str = "") -> dict[str, Any]:
    value: dict[str, Any] = {
        "company": {
            "companyName": company_name,
            "entityType": "operating_company",
            "country": country,
            "countryCode": country_code.upper(),
            "status": "unknown",
            "summary": "",
            "researchConclusion": "",
            "evidence": [],
        }
    }
    value.update({field: [] for field in ARRAY_FIELDS})
    value["assessment"] = {"status": "not_requested"}
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


def _validate_evidence_item(source: Any, path: str, errors: list[str]) -> None:
    if not isinstance(source, dict):
        errors.append(f"{path} must be an object")
        return
    if source.get("relation") not in ALLOWED_RELATIONS:
        errors.append(f"{path}.relation must be supports, refutes, or context")
    if source.get("sourceType") not in ALLOWED_SOURCE_TYPES:
        errors.append(f"{path}.sourceType has an invalid value")
    if not source.get("sourceTitle") or not source.get("retrievedOn"):
        errors.append(f"{path} requires sourceTitle and retrievedOn")
    if source.get("retrievedOn") and not _validate_date(source.get("retrievedOn")):
        errors.append(f"{path}.retrievedOn must use YYYY-MM-DD")
    if not source.get("sourceUrl") and source.get("sourceType") != "customer_document":
        errors.append(f"{path}.sourceUrl is required except for customer documents")


def _validate_date(raw: Any) -> bool:
    try:
        datetime.strptime(str(raw), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _validate_assessment(assessment: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(assessment, dict):
        return ["$.assessment must be an object"]
    status = assessment.get("status")
    if status not in ASSESSMENT_STATUSES:
        errors.append("$.assessment.status has an invalid value")
        return errors
    if status == "not_requested":
        if set(assessment) != {"status"}:
            errors.append("$.assessment: not_requested permits only the status field")
        return errors
    unknown = sorted(set(assessment) - ASSESSMENT_FIELDS)
    if unknown:
        errors.append(f"$.assessment has unsupported fields: {', '.join(unknown)}")
    missing = sorted(ASSESSMENT_FIELDS - set(assessment))
    if missing:
        errors.append(f"$.assessment is missing required fields: {', '.join(missing)}")
    if assessment.get("assessmentType") != "lead_value":
        errors.append("$.assessment.assessmentType must be lead_value")
    if assessment.get("modelCode") != "GETO_LEAD_VALUE":
        errors.append("$.assessment.modelCode must be GETO_LEAD_VALUE")
    if assessment.get("modelVersion") != "2026-07-29":
        errors.append("$.assessment.modelVersion must be 2026-07-29")
    if assessment.get("ratingScaleVersion") != "value-status-2026-07-29":
        errors.append("$.assessment.ratingScaleVersion must be value-status-2026-07-29")
    for field in ("modelVersion", "ratingScaleVersion", "overallConclusion", "assessedOn"):
        if not assessment.get(field):
            errors.append(f"$.assessment.{field} is required")
    if assessment.get("assessedOn") and not _validate_date(assessment.get("assessedOn")):
        errors.append("$.assessment.assessedOn must use YYYY-MM-DD")
    for field in ("capCodes", "gapCodes"):
        if not isinstance(assessment.get(field), list):
            errors.append(f"$.assessment.{field} must be an array")

    context = assessment.get("capabilityContext")
    if not isinstance(context, dict):
        errors.append("$.assessment.capabilityContext must be an object")
    else:
        unknown_context = sorted(set(context) - CAPABILITY_CONTEXT_FIELDS)
        missing_context = sorted(CAPABILITY_CONTEXT_FIELDS - set(context))
        if unknown_context:
            errors.append(f"$.assessment.capabilityContext has unsupported fields: {', '.join(unknown_context)}")
        if missing_context:
            errors.append(f"$.assessment.capabilityContext is missing fields: {', '.join(missing_context)}")
        if context.get("status") not in {"available", "partial", "unavailable"}:
            errors.append("$.assessment.capabilityContext.status has an invalid value")
        for field in ("productCodes", "scenarioCodes", "roleCodes", "caseKeys", "gapCodes"):
            if not isinstance(context.get(field), list):
                errors.append(f"$.assessment.capabilityContext.{field} must be an array")

    dimensions = assessment.get("dimensions")
    if not isinstance(dimensions, list):
        errors.append("$.assessment.dimensions must be an array")
        dimensions = []
    seen_codes: set[str] = set()
    for index, dimension in enumerate(dimensions):
        path = f"$.assessment.dimensions[{index}]"
        if not isinstance(dimension, dict):
            errors.append(f"{path} must be an object")
            continue
        unknown_dimension = sorted(set(dimension) - DIMENSION_FIELDS)
        missing_dimension = sorted(DIMENSION_FIELDS - set(dimension))
        if unknown_dimension:
            errors.append(f"{path} has unsupported fields: {', '.join(unknown_dimension)}")
        if missing_dimension:
            errors.append(f"{path} is missing fields: {', '.join(missing_dimension)}")
        code = dimension.get("dimensionCode")
        if not code:
            errors.append(f"{path}.dimensionCode is required")
        elif code in seen_codes:
            errors.append(f"{path}.dimensionCode is duplicated")
        seen_codes.add(str(code))
        if code not in LEAD_DIMENSIONS:
            errors.append(f"{path}.dimensionCode has an invalid value")
        elif dimension.get("maxScore") != LEAD_DIMENSIONS[code]:
            errors.append(f"{path}.maxScore does not match the approved model")
        if not dimension.get("name") or not dimension.get("rationale"):
            errors.append(f"{path} requires name and rationale")
        if dimension.get("evidenceGrade") not in {"A", "B", "C", "U"}:
            errors.append(f"{path}.evidenceGrade must be A, B, C, or U")
        elif dimension.get("evidenceWeight") != EVIDENCE_WEIGHTS[dimension["evidenceGrade"]]:
            errors.append(f"{path}.evidenceWeight does not match evidenceGrade")
        evidence = dimension.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{path}.evidence must be an array")
            evidence = []
        if dimension.get("finalDimensionScore") is not None and not evidence:
            errors.append(f"{path}: a scored dimension requires Evidence")
        for evidence_index, source in enumerate(evidence):
            _validate_evidence_item(source, f"{path}.evidence[{evidence_index}]", errors)
        for field in ("gapCodes", "capCodes"):
            if not isinstance(dimension.get(field), list):
                errors.append(f"{path}.{field} must be an array")

    if status == "completed":
        if len(dimensions) != 6:
            errors.append("$.assessment: completed assessment requires exactly six dimensions")
        if assessment.get("overallScore") is None or not assessment.get("grade"):
            errors.append("$.assessment: completed assessment requires overallScore and grade")
        if assessment.get("informationCompleteness") is None:
            errors.append("$.assessment: completed assessment requires informationCompleteness")
        if assessment.get("grade") not in {
            "verified_high_value", "high_potential_needs_evidence", "routine_follow_up", "watch"
        }:
            errors.append("$.assessment.grade has an invalid value")
        if seen_codes != set(LEAD_DIMENSIONS):
            errors.append("$.assessment: completed assessment requires the approved six dimension codes")
        if any(not isinstance(item, dict) or item.get("finalDimensionScore") is None or not _has_evidence(item) for item in dimensions):
            errors.append("$.assessment: completed assessment requires six scored, evidenced dimensions")
    else:
        if assessment.get("overallScore") is not None or assessment.get("grade") is not None:
            errors.append("$.assessment: non-completed assessment cannot contain overallScore or grade")
    return errors


def validate_company(value: Any) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []
    if not isinstance(value, dict):
        return ["$: company.json must be a JSON object"], warnings, infos

    company = value.get("company")
    if not isinstance(company, dict):
        errors.append("$.company is required and must be an object")
    else:
        for field in ("companyName", "entityType", "country", "countryCode"):
            if not company.get(field):
                errors.append(f"$.company.{field} is required")
        if company.get("countryCode") and not re.fullmatch(r"[A-Z]{2}", str(company.get("countryCode"))):
            errors.append("$.company.countryCode must be ISO 3166-1 alpha-2")
        if company.get("entityType") not in {"legal_entity", "operating_company", "corporate_group"}:
            errors.append("$.company.entityType has an invalid value")
        if not isinstance(company.get("evidence"), list):
            errors.append("$.company.evidence must be an array")
        else:
            for evidence_index, source in enumerate(company["evidence"]):
                _validate_evidence_item(source, f"$.company.evidence[{evidence_index}]", errors)

    if value.get("researchStatus") not in {"completed", "completed_with_gaps", "identity_conflict"}:
        errors.append("$.researchStatus is required and must use the V2 enum")
    researched_on = value.get("lastResearchedOn")
    if not _validate_date(researched_on):
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
                _validate_evidence_item(source, source_path, errors)

    for index, item in enumerate(value.get("researchQueries", [])):
        path = f"$.researchQueries[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        unknown = sorted(set(item) - RESEARCH_QUERY_FIELDS)
        missing = sorted(RESEARCH_QUERY_FIELDS - set(item))
        if unknown:
            errors.append(f"{path} has unsupported fields: {', '.join(unknown)}")
        if missing:
            errors.append(f"{path} is missing fields: {', '.join(missing)}")
        status = item.get("status")
        if status not in {"found", "no_result", "partial", "failed", "not_queried"}:
            errors.append(f"{path}.status has an invalid value")
        if not _validate_date(item.get("checkedOn")):
            errors.append(f"{path}.checkedOn must use YYYY-MM-DD")
        if not isinstance(item.get("evidence"), list):
            errors.append(f"{path}.evidence must be an array")
        elif status in {"found", "partial"} and not item.get("evidence"):
            errors.append(f"{path}: found/partial query requires Evidence")
        for evidence_index, source in enumerate(item.get("evidence") or []):
            _validate_evidence_item(source, f"{path}.evidence[{evidence_index}]", errors)
        if status == "not_queried":
            infos.append(f"{path}: not_queried")
        elif status == "no_result":
            infos.append(f"{path}: checked with no result")
        elif status == "failed":
            warnings.append(f"{path}: query failed")

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
        if not isinstance(item, dict):
            continue
        if item.get("status") == "not_queried":
            infos.append(f"$.missingInformation[{index}]: not_queried")
        elif item.get("status") in {"provider_failed", "outdated", "conflicting"}:
            warnings.append(f"$.missingInformation[{index}]: unresolved {item.get('status')}")

    errors.extend(_validate_assessment(value.get("assessment")))

    for index, report_file in enumerate(value.get("reportFiles", [])):
        path = f"$.reportFiles[{index}]"
        if not isinstance(report_file, dict):
            errors.append(f"{path} must be an object")
            continue
        unknown = sorted(set(report_file) - REPORT_FILE_FIELDS)
        missing = sorted(REPORT_FILE_FIELDS - set(report_file))
        if unknown:
            errors.append(f"{path} has unsupported fields: {', '.join(unknown)}")
        if missing:
            errors.append(f"{path} is missing fields: {', '.join(missing)}")
        if report_file.get("format") not in {"markdown", "docx", "pdf", "html"}:
            errors.append(f"{path}.format has an invalid value")
        if report_file.get("reportType") not in {"diligence", "assessment", "risk", "supplement"}:
            errors.append(f"{path}.reportType has an invalid value")
        if not _validate_date(report_file.get("generatedOn")):
            errors.append(f"{path}.generatedOn must use YYYY-MM-DD")

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

    return sorted(set(errors)), sorted(set(warnings)), sorted(set(infos))


def format_result(errors: list[str], warnings: list[str], infos: list[str] | None = None) -> dict[str, Any]:
    infos = infos or []
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "infos": infos,
        "errorCount": len(errors),
        "warningCount": len(warnings),
        "infoCount": len(infos),
    }
