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
TOP_LEVEL_FIELDS = set(ARRAY_FIELDS) | {
    "company", "assessment", "inquiryAssessment", "competitorCustomerPortfolio",
    "researchStatus", "lastResearchedOn",
}
COMPANY_FIELDS = {
    "companyName", "entityType", "country", "countryCode", "status", "summary",
    "researchConclusion", "foundedOn", "companyScale", "headcount", "listingStatus",
    "listingDetails", "marketPosition", "priority", "procurementBoundary", "evidence",
}
EVIDENCE_FIELDS = tuple(field for field in ARRAY_FIELDS if field not in {"reportFiles", "researchQueries"})
FORBIDDEN_LOCAL_KEYS = {
    "runId", "taskId", "companyKey", "claimKey", "sourceKey", "claimSourceLinks",
    "ownerUserId", "identityKey", "visibility", "deletedAt", "businessActivities",
}
ALLOWED_SOURCE_TYPES = {
    "official_website", "registry", "government", "court", "financial_report",
    "media", "social_media", "provider", "customer_document", "other",
}
EVIDENCE_ITEM_FIELDS = {
    "sourceTitle", "sourceUrl", "publisher", "sourceType", "publishedOn",
    "retrievedOn", "locator", "excerpt", "note", "verificationScope",
}
EVIDENCE_BASE_FIELDS = EVIDENCE_ITEM_FIELDS - {"verificationScope"}
PROJECT_PARTICIPANT_ROLES = {
    "owner", "developer", "main_contractor", "subcontractor", "consultant",
    "designer", "supervisor", "partner", "other",
}
PROJECT_PARTICIPANT_STATUSES = {"confirmed", "possible", "conflicting", "historical"}
EXCLUSIVITY_STATUSES = {"exclusive", "non_exclusive", "unknown", "conflicting"}
LISTING_STATUSES = {"self_listed", "parent_listed", "not_listed", "unknown"}
CAPITAL_TYPES = {"registered_capital", "paid_in_capital"}
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
    "incomplete_evidence", "pending_cohort_baseline", "completed",
}
ASSESSMENT_FIELDS = {
    "assessmentType", "status", "modelCode", "modelVersion", "ratingScaleVersion",
    "capabilityContext", "grade", "overallScore", "informationCompleteness",
    "overallConclusion", "assessedOn", "dimensions", "capCodes", "gapCodes",
    "cohortKey", "cohortBaselineVersion", "cohortAsOf", "evidence",
}
DIMENSION_FIELDS = {
    "dimensionCode", "name", "observedScore", "finalDimensionScore", "maxScore",
    "evidenceGrade", "evidenceWeight", "level", "rationale", "evidence",
    "gapCodes", "capCodes", "baselineScore", "baselinePolicy",
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
INQUIRY_ASSESSMENT_STATUSES = {"not_requested", "incomplete_inquiry", "completed"}
INQUIRY_ASSESSMENT_FIELDS = {
    "assessmentType", "status", "modelCode", "modelVersion", "inquiryRef",
    "grade", "overallScore", "overallConclusion", "assessedOn", "dimensions",
    "hardBlockCodes", "gapCodes",
}
INQUIRY_DIMENSION_FIELDS = {
    "dimensionCode", "name", "score", "maxScore", "rationale", "evidence", "gapCodes",
}
INQUIRY_DIMENSIONS = {
    "identity_confidence": 15,
    "requirement_specificity": 20,
    "project_readiness": 20,
    "reachability_authority": 15,
    "commercial_payment_readiness": 15,
    "technical_product_fit": 15,
}
COMPETITOR_PORTFOLIO_STATUSES = {
    "not_requested", "no_verified_customers", "pending_customer_scores",
    "partial_coverage", "completed",
}
COMPETITOR_PORTFOLIO_FIELDS = {
    "assessmentType", "status", "modelCode", "modelVersion", "customerValueModelCode",
    "asOf", "verifiedCustomerCount", "scoredCustomerCount", "customerScoreCoverage",
    "averageCustomerValueScore", "customers",
}
COMPETITOR_CUSTOMER_FIELDS = {
    "companyName", "country", "relationshipCount", "customerAssessmentStatus",
    "customerValueScore", "customerValueModelVersion", "cohortBaselineVersion",
    "assessedOn", "evidence",
}
RELATIONSHIP_ENTRY_FIELDS = {
    "assessmentType", "status", "modelCode", "modelVersion", "score", "rationale",
    "assessedOn", "evidenceStatus", "gapCodes", "evidence",
}
RELATIONSHIP_REVIEW_DECISIONS = {
    "verified_customer", "verified_non_customer", "pending", "conflicting", "invalid",
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
            "foundedOn": None,
            "companyScale": None,
            "headcount": None,
            "listingStatus": "unknown",
            "listingDetails": None,
            "marketPosition": None,
            "priority": None,
            "procurementBoundary": None,
            "evidence": [],
        }
    }
    value.update({field: [] for field in ARRAY_FIELDS})
    value["assessment"] = {"status": "not_requested"}
    value["inquiryAssessment"] = {"status": "not_requested"}
    value["competitorCustomerPortfolio"] = {"status": "not_requested"}
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


INQUIRY_REPORT_CORE_QUESTIONS = {
    "conclusion": r"总体判断|先说结论|结论先行|结论与建议|最终判断|当前建议",
    "inquiry": r"询盘|需求|客户提出",
    "company": r"公司|法定主体|经营主体|企业",
    "contact": r"联系人|联系方式|邮箱|电话",
    "project": r"项目|采购场景|采购窗口|工程",
    "product": r"产品|模板|技术|方案|适配",
    "transaction": r"报价|签约|付款|授信|交易条件",
    "customer_value": r"客户价值|长期价值|长期潜力|投入建议",
    "actions": r"下一步|建议动作|需要向客户|索取资料|暂时不",
}

INQUIRY_REPORT_FORBIDDEN_TERMS = {
    "pending_cohort_baseline": r"\bpending_cohort_baseline\b",
    "nurture_or_verify": r"\bnurture_or_verify\b",
    "not_requested": r"\bnot_requested\b",
    "diligence machine status": r"\bdiligence_with_[a-z_]+\b|\bblocked_no_research_anchor\b",
    "Provider": r"\bProvider\b",
    "queryBoundary": r"\bqueryBoundary\b",
    "hard block": r"\bhard[ _-]?blocks?\b",
    "unverified_signing_and_payer": r"\bunverified_signing_and_payer\b",
    "readiness machine grade": r"\bready_for_quotation\b|\bqualified_needs_clarification\b|\bhigh_risk_or_unqualified\b",
    "raw query state": r"\bno_result\b|\bnot_queried\b|\bupstream_unavailable\b",
    "claimed profile": r"\bclaimed profile\b",
}

GENERIC_PROJECT_NAME_PATTERN = re.compile(
    r"(?:historical|current|public)?\s*project\s*(?:pool|portfolio)|历史项目池|项目组合|若干.{0,8}项目",
    re.IGNORECASE,
)


def _project_report_names(project: dict[str, Any]) -> list[str]:
    names = [str(project.get("projectName") or "").strip()]
    for alias in project.get("aliases", []):
        if isinstance(alias, str):
            names.append(alias.strip())
        elif isinstance(alias, dict):
            names.append(str(alias.get("name") or alias.get("alias") or "").strip())
    return [name for name in names if name]


def validate_inquiry_report(text: str, company: dict[str, Any]) -> list[str]:
    assessment = company.get("inquiryAssessment")
    if not isinstance(assessment, dict) or assessment.get("status") == "not_requested":
        return []
    errors: list[str] = []
    company_value = company.get("assessment")
    company_value_dimensions = (
        company_value.get("dimensions", []) if isinstance(company_value, dict) else []
    )
    if not isinstance(company_value_dimensions, list) or len(company_value_dimensions) != 6:
        errors.append(
            "report.md: inquiry diligence requires six-dimensional long-term company-value observations"
        )
    if len(text.strip()) < 500:
        errors.append("report.md: inquiry diligence is too short to explain the company and current inquiry")
    for question, pattern in INQUIRY_REPORT_CORE_QUESTIONS.items():
        if not re.search(pattern, text, re.IGNORECASE):
            errors.append(f"report.md: missing plain-language answer for core question {question}")
    term_text = re.sub(r"https?://[^\s)>]+", "", text)
    for label, pattern in INQUIRY_REPORT_FORBIDDEN_TERMS.items():
        if re.search(pattern, term_text, re.IGNORECASE):
            errors.append(f"report.md: internal or untranslated term must not appear in the formal report: {label}")
    visible = re.sub(r"https?://\S+", "", text)
    visible = re.sub(r"```.*?```", "", visible, flags=re.DOTALL)
    cjk_count = len(re.findall(r"[\u3400-\u9fff]", visible))
    latin_count = len(re.findall(r"[A-Za-z]", visible))
    if cjk_count + latin_count >= 300 and cjk_count / (cjk_count + latin_count) < 0.40:
        errors.append("report.md: Chinese business prose is not the dominant readable language")
    projects = [item for item in company.get("projects", []) if isinstance(item, dict) and item.get("projectName")]
    if projects:
        generic_names = [
            str(project["projectName"]) for project in projects
            if GENERIC_PROJECT_NAME_PATTERN.search(str(project["projectName"]))
        ]
        if generic_names:
            errors.append(
                "report.md: projects[] must use one item per named project, not aggregate placeholders: "
                + ", ".join(generic_names)
            )
        if not re.search(r"公司.{0,4}项目池|公开项目池|项目总表|项目一览|项目组合总表", text):
            errors.append("report.md: a company project-pool table is required")
        missing_projects = [
            str(project["projectName"]) for project in projects
            if not any(name.casefold() in text.casefold() for name in _project_report_names(project))
        ]
        if missing_projects:
            errors.append(
                "report.md: company project-pool table omits structured projects: "
                + ", ".join(missing_projects)
            )
    if not projects and not re.search(r"未发现.{0,12}项目|项目.{0,12}未取得|项目检索|公开项目", text):
        errors.append("report.md: no project evidence exists and the public-search boundary is not explained")
    overall_score = assessment.get("overallScore")
    if isinstance(overall_score, (int, float)) and not isinstance(overall_score, bool):
        score_text = f"{overall_score:g}"
        if not re.search(rf"(?<!\d){re.escape(score_text)}(?:\.0)?\s*(?:/\s*100|分)(?!\d)", text):
            errors.append("report.md: inquiry readiness score differs from company.json")
    return errors


def _validate_evidence_item(source: Any, path: str, errors: list[str]) -> None:
    if not isinstance(source, dict):
        errors.append(f"{path} must be an object")
        return
    unknown = sorted(set(source) - EVIDENCE_ITEM_FIELDS)
    missing = sorted(EVIDENCE_BASE_FIELDS - set(source))
    if unknown:
        errors.append(f"{path} has unsupported fields: {', '.join(unknown)}")
    if missing:
        errors.append(f"{path} is missing fields: {', '.join(missing)}")
    if source.get("sourceType") not in ALLOWED_SOURCE_TYPES:
        errors.append(f"{path}.sourceType has an invalid value")
    if not source.get("sourceTitle") or not source.get("retrievedOn"):
        errors.append(f"{path} requires sourceTitle and retrievedOn")
    if source.get("retrievedOn") and not _validate_date(source.get("retrievedOn")):
        errors.append(f"{path}.retrievedOn must use YYYY-MM-DD")
    if source.get("publishedOn") and not _validate_date(source.get("publishedOn")):
        errors.append(f"{path}.publishedOn must use YYYY-MM-DD")
    if not source.get("sourceUrl") and source.get("sourceType") != "customer_document":
        errors.append(f"{path}.sourceUrl is required except for customer documents")
    if "verificationScope" in source and (
        not isinstance(source.get("verificationScope"), list)
        or not source.get("verificationScope")
        or any(not isinstance(item, str) or not item.strip() for item in source["verificationScope"])
    ):
        errors.append(f"{path}.verificationScope must be a non-empty string array when present")
    verification_scope = source.get("verificationScope")
    if verification_scope is not None and (
        not isinstance(verification_scope, list)
        or not all(isinstance(item, str) and item.strip() for item in verification_scope)
    ):
        errors.append(f"{path}.verificationScope must be an array of non-empty strings")


def _validate_project(project: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    old_fields = sorted(set(project) & {"owner", "developer", "consultant", "mainContractor"})
    if old_fields:
        errors.append(f"{path} has unsupported participant fields: {', '.join(old_fields)}")
    participants = project.get("participants")
    if participants is None:
        return errors
    if not isinstance(participants, list):
        return errors + [f"{path}.participants must be an array"]
    for index, participant in enumerate(participants):
        participant_path = f"{path}.participants[{index}]"
        if not isinstance(participant, dict):
            errors.append(f"{participant_path} must be an object")
            continue
        if not str(participant.get("name") or "").strip():
            errors.append(f"{participant_path}.name is required")
        if participant.get("role") not in PROJECT_PARTICIPANT_ROLES:
            errors.append(f"{participant_path}.role has an invalid value")
        if participant.get("status") not in PROJECT_PARTICIPANT_STATUSES:
            errors.append(f"{participant_path}.status has an invalid value")
        if participant.get("identity") is not None and not isinstance(participant.get("identity"), dict):
            errors.append(f"{participant_path}.identity must be an object or null")
        if participant.get("lastVerifiedOn") is not None and not _validate_date(participant.get("lastVerifiedOn")):
            errors.append(f"{participant_path}.lastVerifiedOn must use YYYY-MM-DD")
        evidence = participant.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{participant_path}.evidence must contain at least one Evidence item")
            continue
        for evidence_index, source in enumerate(evidence):
            _validate_evidence_item(source, f"{participant_path}.evidence[{evidence_index}]", errors)
    potential_products = project.get("potentialProducts")
    if potential_products is not None:
        if not isinstance(potential_products, list):
            errors.append(f"{path}.potentialProducts must be an array")
        else:
            for index, product in enumerate(potential_products):
                product_path = f"{path}.potentialProducts[{index}]"
                if not isinstance(product, dict) or not str(product.get("productName") or "").strip():
                    errors.append(f"{product_path}.productName is required")
                    continue
                evidence = product.get("evidence")
                if not isinstance(evidence, list) or not evidence:
                    errors.append(f"{product_path}.evidence must contain at least one Evidence item")
                    continue
                for evidence_index, source in enumerate(evidence):
                    _validate_evidence_item(source, f"{product_path}.evidence[{evidence_index}]", errors)
    return errors


def _validate_product(product: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    media = product.get("media")
    if media is None:
        return errors
    if not isinstance(media, list):
        return [f"{path}.media must be an array"]
    for index, item in enumerate(media):
        media_path = f"{path}.media[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{media_path} must be an object")
            continue
        if not item.get("url"):
            errors.append(f"{media_path}.url is required")
        if item.get("mediaType") not in {"image", "video", "document"}:
            errors.append(f"{media_path}.mediaType has an invalid value")
        if item.get("lastVerifiedOn") is not None and not _validate_date(item.get("lastVerifiedOn")):
            errors.append(f"{media_path}.lastVerifiedOn must use YYYY-MM-DD")
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{media_path}.evidence must contain at least one Evidence item")
            continue
        for evidence_index, source in enumerate(evidence):
            _validate_evidence_item(source, f"{media_path}.evidence[{evidence_index}]", errors)
    return errors


def _validate_exclusivity(relationship: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    old_fields = sorted(set(relationship) & {"isExclusive", "limitation"})
    if old_fields:
        errors.append(f"{path} has unsupported relationship fields: {', '.join(old_fields)}")
    limitations = relationship.get("limitations")
    if limitations is not None and (
        not isinstance(limitations, list) or not all(isinstance(item, str) for item in limitations)
    ):
        errors.append(f"{path}.limitations must be an array of strings")
    exclusivity = relationship.get("exclusivity")
    if exclusivity is None:
        return errors + [f"{path}.exclusivity is required"]
    if not isinstance(exclusivity, dict):
        return errors + [f"{path}.exclusivity must be an object"]
    allowed = {"status", "scope", "description", "lastVerifiedOn", "evidence"}
    unknown = sorted(set(exclusivity) - allowed)
    missing = sorted({"status", "scope", "description", "lastVerifiedOn", "evidence"} - set(exclusivity))
    if unknown:
        errors.append(f"{path}.exclusivity has unsupported fields: {', '.join(unknown)}")
    if missing:
        errors.append(f"{path}.exclusivity is missing fields: {', '.join(missing)}")
    if exclusivity.get("status") not in EXCLUSIVITY_STATUSES:
        errors.append(f"{path}.exclusivity.status has an invalid value")
    if exclusivity.get("lastVerifiedOn") is not None and not _validate_date(exclusivity.get("lastVerifiedOn")):
        errors.append(f"{path}.exclusivity.lastVerifiedOn must use YYYY-MM-DD")
    evidence = exclusivity.get("evidence")
    if not isinstance(evidence, list):
        errors.append(f"{path}.exclusivity.evidence must be an array")
    else:
        for evidence_index, source in enumerate(evidence):
            _validate_evidence_item(source, f"{path}.exclusivity.evidence[{evidence_index}]", errors)
    return errors


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
    if not assessment.get("cohortKey"):
        errors.append("$.assessment.cohortKey is required")
    for field in ("modelVersion", "ratingScaleVersion", "overallConclusion", "assessedOn"):
        if not assessment.get(field):
            errors.append(f"$.assessment.{field} is required")
    if assessment.get("assessedOn") and not _validate_date(assessment.get("assessedOn")):
        errors.append("$.assessment.assessedOn must use YYYY-MM-DD")
    for field in ("capCodes", "gapCodes"):
        if not isinstance(assessment.get(field), list):
            errors.append(f"$.assessment.{field} must be an array")
    evidence = assessment.get("evidence")
    if not isinstance(evidence, list):
        errors.append("$.assessment.evidence must be an array")
    else:
        for evidence_index, source in enumerate(evidence):
            _validate_evidence_item(source, f"$.assessment.evidence[{evidence_index}]", errors)
        if status == "completed" and not evidence:
            errors.append("$.assessment: completed score requires top-level Evidence")

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
        if context.get("foundationKey") != "geto:capability-foundation":
            errors.append("$.assessment.capabilityContext.foundationKey must be geto:capability-foundation")
        if context.get("status") in {"available", "partial"}:
            if not context.get("foundationVersion"):
                errors.append("$.assessment.capabilityContext.foundationVersion is required")
            if not _validate_date(context.get("asOf")):
                errors.append("$.assessment.capabilityContext.asOf must use YYYY-MM-DD")
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(context.get("contentHash") or "")):
                errors.append("$.assessment.capabilityContext.contentHash must be a sha256 hash")
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
        if not dimension.get("baselinePolicy"):
            errors.append(f"{path}.baselinePolicy is required")
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
        if not assessment.get("cohortBaselineVersion") or not assessment.get("cohortAsOf"):
            errors.append("$.assessment: completed assessment requires cohortBaselineVersion and cohortAsOf")
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
        if assessment.get("cohortBaselineVersion") is not None or assessment.get("cohortAsOf") is not None:
            errors.append("$.assessment: non-completed assessment cannot contain cohort baseline metadata")
    return errors


def _validate_inquiry_assessment(assessment: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(assessment, dict):
        return ["$.inquiryAssessment must be an object"]
    status = assessment.get("status")
    if status not in INQUIRY_ASSESSMENT_STATUSES:
        return ["$.inquiryAssessment.status has an invalid value"]
    if status == "not_requested":
        if set(assessment) != {"status"}:
            errors.append("$.inquiryAssessment: not_requested permits only the status field")
        return errors
    unknown = sorted(set(assessment) - INQUIRY_ASSESSMENT_FIELDS)
    missing = sorted(INQUIRY_ASSESSMENT_FIELDS - set(assessment))
    if unknown:
        errors.append(f"$.inquiryAssessment has unsupported fields: {', '.join(unknown)}")
    if missing:
        errors.append(f"$.inquiryAssessment is missing required fields: {', '.join(missing)}")
    if assessment.get("assessmentType") != "inquiry_readiness":
        errors.append("$.inquiryAssessment.assessmentType must be inquiry_readiness")
    if assessment.get("modelCode") != "GETO_INQUIRY_READINESS":
        errors.append("$.inquiryAssessment.modelCode must be GETO_INQUIRY_READINESS")
    if assessment.get("modelVersion") != "2026-08-19":
        errors.append("$.inquiryAssessment.modelVersion must be 2026-08-19")
    if not assessment.get("inquiryRef"):
        errors.append("$.inquiryAssessment.inquiryRef is required")
    if not _validate_date(assessment.get("assessedOn")):
        errors.append("$.inquiryAssessment.assessedOn must use YYYY-MM-DD")
    for field in ("hardBlockCodes", "gapCodes"):
        if not isinstance(assessment.get(field), list):
            errors.append(f"$.inquiryAssessment.{field} must be an array")
    dimensions = assessment.get("dimensions")
    if not isinstance(dimensions, list):
        errors.append("$.inquiryAssessment.dimensions must be an array")
        dimensions = []
    seen: set[str] = set()
    total = 0.0
    for index, dimension in enumerate(dimensions):
        path = f"$.inquiryAssessment.dimensions[{index}]"
        if not isinstance(dimension, dict):
            errors.append(f"{path} must be an object")
            continue
        unknown_dimension = sorted(set(dimension) - INQUIRY_DIMENSION_FIELDS)
        missing_dimension = sorted(INQUIRY_DIMENSION_FIELDS - set(dimension))
        if unknown_dimension:
            errors.append(f"{path} has unsupported fields: {', '.join(unknown_dimension)}")
        if missing_dimension:
            errors.append(f"{path} is missing fields: {', '.join(missing_dimension)}")
        code = dimension.get("dimensionCode")
        if code not in INQUIRY_DIMENSIONS:
            errors.append(f"{path}.dimensionCode has an invalid value")
        elif dimension.get("maxScore") != INQUIRY_DIMENSIONS[code]:
            errors.append(f"{path}.maxScore does not match the inquiry model")
        if code in seen:
            errors.append(f"{path}.dimensionCode is duplicated")
        seen.add(str(code))
        score = dimension.get("score")
        if score is not None and (
            not isinstance(score, (int, float)) or isinstance(score, bool)
            or not 0 <= score <= INQUIRY_DIMENSIONS.get(code, 0)
        ):
            errors.append(f"{path}.score is outside the inquiry model range")
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            total += float(score)
        evidence = dimension.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{path}.evidence must be an array")
            evidence = []
        if isinstance(score, (int, float)) and score > 0 and not evidence:
            errors.append(f"{path}: positive readiness score requires Evidence")
        for evidence_index, source in enumerate(evidence):
            _validate_evidence_item(source, f"{path}.evidence[{evidence_index}]", errors)
        if not isinstance(dimension.get("gapCodes"), list):
            errors.append(f"{path}.gapCodes must be an array")
    if status == "completed":
        if seen != set(INQUIRY_DIMENSIONS):
            errors.append("$.inquiryAssessment: completed assessment requires the approved six dimensions")
        if assessment.get("overallScore") is None or assessment.get("grade") not in {
            "ready_for_quotation", "qualified_needs_clarification",
            "nurture_or_verify", "high_risk_or_unqualified",
        }:
            errors.append("$.inquiryAssessment: completed assessment requires a valid score and grade")
        if isinstance(assessment.get("overallScore"), (int, float)) and assessment["overallScore"] > total:
            errors.append("$.inquiryAssessment.overallScore cannot exceed the dimension total")
    elif assessment.get("overallScore") is not None or assessment.get("grade") is not None:
        errors.append("$.inquiryAssessment: incomplete assessment cannot contain overallScore or grade")
    return errors


def _validate_relationship_entry(relationship: dict[str, Any], path: str) -> list[str]:
    errors = _validate_exclusivity(relationship, path)
    decision = relationship.get("reviewDecision")
    if decision is not None and decision not in RELATIONSHIP_REVIEW_DECISIONS:
        errors.append(f"{path}.reviewDecision has an invalid value")
    if decision == "verified_customer":
        if relationship.get("relationshipType") != "customer":
            errors.append(f"{path}: verified_customer requires relationshipType=customer")
        if not relationship.get("counterpartyName"):
            errors.append(f"{path}: verified_customer requires counterpartyName")
        if not relationship.get("projectName") and not relationship.get("productOrService"):
            errors.append(f"{path}: verified_customer requires projectName or productOrService")
        if not relationship.get("description") or not _has_evidence(relationship):
            errors.append(f"{path}: verified_customer requires cooperation description and Evidence")

    assessment = relationship.get("entryAssessment")
    if assessment is None:
        return errors
    if decision != "verified_customer":
        errors.append(f"{path}.entryAssessment is limited to verified_customer relationships")
    if not isinstance(assessment, dict):
        errors.append(f"{path}.entryAssessment must be an object")
        return errors
    unknown = sorted(set(assessment) - RELATIONSHIP_ENTRY_FIELDS)
    missing = sorted(RELATIONSHIP_ENTRY_FIELDS - set(assessment))
    if unknown:
        errors.append(f"{path}.entryAssessment has unsupported fields: {', '.join(unknown)}")
    if missing:
        errors.append(f"{path}.entryAssessment is missing fields: {', '.join(missing)}")
    if assessment.get("assessmentType") != "relationship_entry":
        errors.append(f"{path}.entryAssessment.assessmentType must be relationship_entry")
    if assessment.get("modelCode") != "GETO_RELATIONSHIP_ENTRY" or assessment.get("modelVersion") != "1.0":
        errors.append(f"{path}.entryAssessment requires GETO_RELATIONSHIP_ENTRY 1.0")
    if assessment.get("status") not in {"completed", "pending_evidence"}:
        errors.append(f"{path}.entryAssessment.status has an invalid value")
    if assessment.get("evidenceStatus") not in {"verified", "partial", "pending", "conflicting"}:
        errors.append(f"{path}.entryAssessment.evidenceStatus has an invalid value")
    if not _validate_date(assessment.get("assessedOn")):
        errors.append(f"{path}.entryAssessment.assessedOn must use YYYY-MM-DD")
    if not isinstance(assessment.get("gapCodes"), list):
        errors.append(f"{path}.entryAssessment.gapCodes must be an array")
    evidence = assessment.get("evidence")
    if not isinstance(evidence, list):
        errors.append(f"{path}.entryAssessment.evidence must be an array")
        evidence = []
    for index, source in enumerate(evidence):
        _validate_evidence_item(source, f"{path}.entryAssessment.evidence[{index}]", errors)

    score = assessment.get("score")
    if assessment.get("status") == "pending_evidence":
        if score is not None:
            errors.append(f"{path}.entryAssessment: pending_evidence requires score=null")
        if not assessment.get("gapCodes"):
            errors.append(f"{path}.entryAssessment: pending_evidence requires gapCodes")
        return errors
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 5:
        errors.append(f"{path}.entryAssessment.score must be an integer from 0 to 5")
        return errors
    if not assessment.get("rationale") or not evidence:
        errors.append(f"{path}.entryAssessment: completed score requires rationale and Evidence")
    depth = relationship.get("cooperationDepthCode")
    relation_status = relationship.get("relationshipStatusCode")
    entry_signal = relationship.get("entrySignalCode")
    anchors = {
        0: (
            isinstance(relationship.get("exclusivity"), dict)
            and relationship["exclusivity"].get("status") == "exclusive"
        ) or depth == "exclusive_closed",
        1: depth == "framework_designated",
        2: depth == "repeat_business",
        3: depth == "single_project",
        4: depth == "trial" or relation_status in {"historical", "ended"},
        5: entry_signal in {
            "open_supplier_window", "supplier_termination", "product_gap", "new_procurement_window",
        },
    }
    if not anchors[score]:
        errors.append(f"{path}.entryAssessment.score lacks the required relationship fact anchor")
    return errors


def _validate_competitor_portfolio(portfolio: Any, relationships: Any = None) -> list[str]:
    errors: list[str] = []
    if portfolio is None:
        return errors
    if not isinstance(portfolio, dict):
        return ["$.competitorCustomerPortfolio must be an object"]
    status = portfolio.get("status")
    if status not in COMPETITOR_PORTFOLIO_STATUSES:
        return ["$.competitorCustomerPortfolio.status has an invalid value"]
    if status == "not_requested":
        if set(portfolio) != {"status"}:
            errors.append("$.competitorCustomerPortfolio: not_requested permits only the status field")
        return errors
    unknown = sorted(set(portfolio) - COMPETITOR_PORTFOLIO_FIELDS)
    missing = sorted(COMPETITOR_PORTFOLIO_FIELDS - set(portfolio))
    if unknown:
        errors.append(f"$.competitorCustomerPortfolio has unsupported fields: {', '.join(unknown)}")
    if missing:
        errors.append(f"$.competitorCustomerPortfolio is missing fields: {', '.join(missing)}")
    if portfolio.get("assessmentType") != "competitor_customer_portfolio":
        errors.append("$.competitorCustomerPortfolio.assessmentType must be competitor_customer_portfolio")
    if portfolio.get("modelCode") != "GETO_COMPETITOR_CUSTOMER_PORTFOLIO":
        errors.append("$.competitorCustomerPortfolio.modelCode has an invalid value")
    if portfolio.get("modelVersion") != "2026-08-19":
        errors.append("$.competitorCustomerPortfolio.modelVersion has an invalid value")
    if portfolio.get("customerValueModelCode") != "GETO_LEAD_VALUE":
        errors.append("$.competitorCustomerPortfolio.customerValueModelCode must be GETO_LEAD_VALUE")
    if not _validate_date(portfolio.get("asOf")):
        errors.append("$.competitorCustomerPortfolio.asOf must use YYYY-MM-DD")
    customers = portfolio.get("customers")
    if not isinstance(customers, list):
        errors.append("$.competitorCustomerPortfolio.customers must be an array")
        customers = []
    scores: list[float] = []
    seen: set[tuple[str, str]] = set()
    for index, customer in enumerate(customers):
        path = f"$.competitorCustomerPortfolio.customers[{index}]"
        if not isinstance(customer, dict):
            errors.append(f"{path} must be an object")
            continue
        unknown_customer = sorted(set(customer) - COMPETITOR_CUSTOMER_FIELDS)
        missing_customer = sorted(COMPETITOR_CUSTOMER_FIELDS - set(customer))
        if unknown_customer:
            errors.append(f"{path} has unsupported fields: {', '.join(unknown_customer)}")
        if missing_customer:
            errors.append(f"{path} is missing fields: {', '.join(missing_customer)}")
        name = str(customer.get("companyName") or "").strip()
        if not name:
            errors.append(f"{path}.companyName is required")
        else:
            customer_key = (name.casefold(), str(customer.get("country") or "").strip().casefold())
            if customer_key in seen:
                errors.append(f"{path}.companyName and country are duplicated")
            seen.add(customer_key)
        if not isinstance(customer.get("relationshipCount"), int) or customer.get("relationshipCount", 0) < 1:
            errors.append(f"{path}.relationshipCount must be a positive integer")
        evidence = customer.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{path}.evidence must contain relationship Evidence")
            evidence = []
        for evidence_index, source in enumerate(evidence):
            _validate_evidence_item(source, f"{path}.evidence[{evidence_index}]", errors)
        score = customer.get("customerValueScore")
        if score is None:
            if any(customer.get(field) is not None for field in (
                "customerValueModelVersion", "cohortBaselineVersion", "assessedOn"
            )):
                errors.append(f"{path}: unscored customer cannot contain score version metadata")
        elif isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 100:
            errors.append(f"{path}.customerValueScore must be between 0 and 100")
        else:
            scores.append(float(score))
            if customer.get("customerAssessmentStatus") != "completed":
                errors.append(f"{path}: scored customer requires completed assessment status")
            if not customer.get("customerValueModelVersion") or not customer.get("cohortBaselineVersion"):
                errors.append(f"{path}: scored customer requires model and cohort baseline versions")
            if not _validate_date(customer.get("assessedOn")):
                errors.append(f"{path}.assessedOn must use YYYY-MM-DD when scored")

    verified = len(customers)
    scored = len(scores)
    coverage = round(scored / verified, 4) if verified else 0.0
    average = round(sum(scores) / scored, 1) if scored else None
    if portfolio.get("verifiedCustomerCount") != verified:
        errors.append("$.competitorCustomerPortfolio.verifiedCustomerCount does not match customers")
    if portfolio.get("scoredCustomerCount") != scored:
        errors.append("$.competitorCustomerPortfolio.scoredCustomerCount does not match customers")
    if portfolio.get("customerScoreCoverage") != coverage:
        errors.append("$.competitorCustomerPortfolio.customerScoreCoverage is inconsistent")
    if portfolio.get("averageCustomerValueScore") != average:
        errors.append("$.competitorCustomerPortfolio.averageCustomerValueScore is inconsistent")
    expected_status = (
        "no_verified_customers" if verified == 0 else
        "pending_customer_scores" if scored == 0 else
        "partial_coverage" if scored < verified else
        "completed"
    )
    if status != expected_status:
        errors.append("$.competitorCustomerPortfolio.status is inconsistent with coverage")
    if isinstance(relationships, list):
        verified_keys = {
            (
                str(item.get("counterpartyName") or "").strip().casefold(),
                str(item.get("country") or "").strip().casefold(),
            )
            for item in relationships
            if isinstance(item, dict) and item.get("reviewDecision") == "verified_customer"
        }
        verified_keys.discard(("", ""))
        if seen != verified_keys:
            errors.append(
                "$.competitorCustomerPortfolio.customers must match deduplicated verified_customer relationships"
            )
    return errors


def validate_company(value: Any) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []
    if not isinstance(value, dict):
        return ["$: company.json must be a JSON object"], warnings, infos

    unknown_top_level = sorted(set(value) - TOP_LEVEL_FIELDS)
    missing_top_level = sorted(TOP_LEVEL_FIELDS - set(value))
    if unknown_top_level:
        errors.append(f"$: unsupported top-level fields: {', '.join(unknown_top_level)}")
    if missing_top_level:
        errors.append(f"$: missing top-level fields: {', '.join(missing_top_level)}")

    company = value.get("company")
    if not isinstance(company, dict):
        errors.append("$.company is required and must be an object")
    else:
        unknown_company = sorted(set(company) - COMPANY_FIELDS)
        missing_company = sorted(COMPANY_FIELDS - set(company))
        if unknown_company:
            errors.append(f"$.company has unsupported fields: {', '.join(unknown_company)}")
        if missing_company:
            errors.append(f"$.company is missing fields: {', '.join(missing_company)}")
        for field in ("companyName", "entityType", "country", "countryCode"):
            if not company.get(field):
                errors.append(f"$.company.{field} is required")
        if company.get("countryCode") and not re.fullmatch(r"[A-Z]{2}", str(company.get("countryCode"))):
            errors.append("$.company.countryCode must be ISO 3166-1 alpha-2")
        if company.get("entityType") not in {"legal_entity", "operating_company", "corporate_group"}:
            errors.append("$.company.entityType has an invalid value")
        if company.get("foundedOn") is not None and not _validate_date(company.get("foundedOn")):
            errors.append("$.company.foundedOn must use YYYY-MM-DD")
        if company.get("headcount") is not None and (
            isinstance(company.get("headcount"), bool)
            or not isinstance(company.get("headcount"), int)
            or company.get("headcount") < 0
        ):
            errors.append("$.company.headcount must be a non-negative integer or null")
        if company.get("listingStatus") is not None and company.get("listingStatus") not in LISTING_STATUSES:
            errors.append("$.company.listingStatus has an invalid value")
        if company.get("listingStatus") in {"self_listed", "parent_listed"} and not company.get("listingDetails"):
            errors.append("$.company.listingDetails is required for a listed company")
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

    for index, item in enumerate(value.get("capitalRecords", [])):
        if isinstance(item, dict) and item.get("capitalType") not in CAPITAL_TYPES:
            errors.append(f"$.capitalRecords[{index}].capitalType has an invalid value")

    for index, item in enumerate(value.get("financialRecords", [])):
        if not isinstance(item, dict):
            continue
        path = f"$.financialRecords[{index}]"
        for field in ("recordType", "subjectEntity", "accountingScope", "relationshipToTarget", "period", "valueStatus", "description"):
            if not str(item.get(field) or "").strip():
                errors.append(f"{path}.{field} is required")
        if not str(item.get("scope") or item.get("financialScope") or "").strip():
            errors.append(f"{path}.scope or financialScope is required")
        if item.get("value") is not None and not str(item.get("unit") or "").strip():
            errors.append(f"{path}.unit is required when value is present")
        record_type = str(item.get("recordType") or "").casefold()
        if "registered_capital" in record_type or "paid_in_capital" in record_type:
            errors.append(f"{path}: registered/paid-in capital belongs in capitalRecords")

    for index, product in enumerate(value.get("productsAndServices", [])):
        if isinstance(product, dict):
            errors.extend(_validate_product(product, f"$.productsAndServices[{index}]"))

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

    for index, relationship in enumerate(value.get("relationships", [])):
        if isinstance(relationship, dict):
            errors.extend(_validate_relationship_entry(relationship, f"$.relationships[{index}]"))

    for index, project in enumerate(value.get("projects", [])):
        if isinstance(project, dict):
            errors.extend(_validate_project(project, f"$.projects[{index}]"))

    errors.extend(_validate_assessment(value.get("assessment")))
    assessment = value.get("assessment")
    if isinstance(assessment, dict) and assessment.get("status") == "completed":
        if any(
            isinstance(item, dict) and item.get("topic") == "lead_assessment_contract_incomplete"
            for item in value.get("missingInformation", [])
        ):
            errors.append(
                "$.missingInformation: completed lead assessment cannot retain "
                "lead_assessment_contract_incomplete"
            )
    errors.extend(_validate_inquiry_assessment(value.get("inquiryAssessment")))
    errors.extend(_validate_competitor_portfolio(
        value.get("competitorCustomerPortfolio"), value.get("relationships")
    ))

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


def _info_summary(infos: list[str]) -> dict[str, int]:
    return {
        "notQueried": sum("not_queried" in item for item in infos),
        "noResult": sum("no result" in item for item in infos),
        "other": sum("not_queried" not in item and "no result" not in item for item in infos),
    }


def format_result(
    errors: list[str], warnings: list[str], infos: list[str] | None = None,
    include_infos: bool = False,
) -> dict[str, Any]:
    infos = infos or []
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "infos": infos if include_infos else [],
        "infoSummary": _info_summary(infos),
        "infoDetailsOmitted": 0 if include_infos else len(infos),
        "errorCount": len(errors),
        "warningCount": len(warnings),
        "infoCount": len(infos),
    }
