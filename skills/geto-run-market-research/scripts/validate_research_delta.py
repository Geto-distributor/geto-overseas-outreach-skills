#!/usr/bin/env python3
"""Validate GETO ResearchDelta invariants before OmniX draft delivery."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROVIDER_STATUSES = {
    "available", "skill_unavailable", "not_configured", "unauthenticated",
    "forbidden", "rate_limited", "provider_session_expired",
    "upstream_unavailable", "partial", "failed",
}
CAPABILITY_FOUNDATION_STATUSES = {"available", "partial", "unavailable"}
DILIGENCE_STATUSES = {
    "completed", "completed_with_explicit_gaps", "pending", "failed", "identity_conflict",
}
ASSESSMENT_STATUSES = {
    "not_requested", "pending_diligence", "pending_capability_foundation",
    "pending_model", "incomplete_evidence", "completed",
}
ASSESSMENT_CALCULATORS = {"deterministic_validator", "server_rule"}
LEAD_LEVELS = {"A", "B", "C", "U"}
ROLE_RELATIONSHIP_TYPES = {"customer", "competitor", "partner", "ecosystem", "project"}
LEAD_DIMENSIONS = {
    "project_city_value": 15,
    "account_scale": 20,
    "future_project_demand": 20,
    "reachability": 10,
    "payment_capacity": 15,
    "multi_product_fit": 20,
}
KEY_FIELDS = {
    "companies": "companyKey",
    "commercialAccounts": "commercialAccountKey",
    "legalEntities": "legalEntityKey",
    "projects": "projectKey",
    "opportunities": "opportunityKey",
    "relationships": "relationshipKey",
    "assessments": "assessmentKey",
    "claims": "claimKey",
    "sources": "sourceKey",
    "claimSourceLinks": "linkKey",
    "contacts": "contactKey",
    "customsEvidence": "evidenceKey",
    "financialRecords": "financialKey",
}


def list_value(root: dict[str, Any], name: str, errors: list[str]) -> list[Any]:
    value = root.get(name, [])
    if not isinstance(value, list):
        errors.append(f"{name} must be an array")
        return []
    return value


def validate(path: Path) -> tuple[list[str], list[str]]:
    root = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(root, dict):
        return ["root must be an object"], []
    errors: list[str] = []
    warnings: list[str] = []

    run = root.get("researchRun")
    release = root.get("release")
    if not isinstance(run, dict):
        errors.append("researchRun is required")
        run = {}
    if not isinstance(release, dict):
        errors.append("release is required")
        release = {}
    for field in ("researchRunKey", "marketCode", "scopeCode", "asOf", "resultMode"):
        if not run.get(field):
            errors.append(f"researchRun.{field} is required")
    if run.get("resultMode") not in {"full", "sample"}:
        errors.append("researchRun.resultMode must be full or sample")
    if run.get("resultMode") == "sample" and not run.get("sampleBoundary"):
        errors.append("sample ResearchRun requires sampleBoundary")
    provenance = run.get("provenance")
    if not isinstance(provenance, dict) or not provenance.get("skill"):
        errors.append("researchRun.provenance.skill is required")
    for field in ("marketCode", "scopeCode", "country", "asOf", "resultMode", "publicationStatus"):
        if not release.get(field):
            errors.append(f"release.{field} is required")

    foundation = root.get("capabilityFoundation")
    if not isinstance(foundation, dict):
        errors.append("capabilityFoundation is required")
        foundation = {}
    for field in ("foundationKey", "asOf", "status"):
        if not foundation.get(field):
            errors.append(f"capabilityFoundation.{field} is required")
    foundation_status = foundation.get("status")
    if foundation_status not in CAPABILITY_FOUNDATION_STATUSES:
        errors.append("capabilityFoundation.status must be available, partial or unavailable")
    if foundation_status in {"available", "partial"} and not foundation.get("contentHash"):
        errors.append("available/partial capabilityFoundation requires contentHash")
    if foundation_status in {"partial", "unavailable"} and not foundation.get("gapCodes"):
        errors.append("partial/unavailable capabilityFoundation requires gapCodes")
    for field in ("productCodes", "scenarioCodes", "caseKeys", "sourceKeys", "gapCodes"):
        value = foundation.get(field, [])
        if not isinstance(value, list):
            errors.append(f"capabilityFoundation.{field} must be an array")

    providers = root.get("providerStatuses", {})
    if not isinstance(providers, dict):
        errors.append("providerStatuses must be an object")
    else:
        for provider, status in providers.items():
            if status not in PROVIDER_STATUSES:
                errors.append(f"invalid Provider status {provider}={status}")

    collections: dict[str, list[Any]] = {}
    keys: dict[str, set[str]] = {}
    for name, field in KEY_FIELDS.items():
        values = list_value(root, name, errors)
        collections[name] = values
        present = [item.get(field) for item in values if isinstance(item, dict)]
        missing = sum(1 for item in values if not isinstance(item, dict) or not item.get(field))
        if missing:
            errors.append(f"{name} has {missing} item(s) without {field}")
        duplicates = [value for value, count in Counter(present).items() if value and count > 1]
        if duplicates:
            errors.append(f"{name} has duplicate natural keys: {duplicates}")
        keys[name] = {str(value) for value in present if value}

    source_packages = list_value(root, "sourcePackages", errors)
    if any(collections.values()) and not source_packages:
        errors.append("non-empty ResearchDelta requires at least one sourcePackage")
    for index, package in enumerate(source_packages):
        if not isinstance(package, dict):
            errors.append(f"sourcePackages[{index}] must be an object")
            continue
        for field in ("sourcePackageKey", "researchRunKey", "sourceType"):
            if not package.get(field):
                errors.append(f"sourcePackages[{index}].{field} is required")
        if package.get("researchRunKey") and package.get("researchRunKey") != run.get("researchRunKey"):
            errors.append(f"sourcePackages[{index}] references another ResearchRun")

    for index, observation in enumerate(list_value(root, "externalObservations", errors)):
        if not isinstance(observation, dict):
            errors.append(f"externalObservations[{index}] must be an object")
            continue
        for field in ("provider", "operation", "queryBoundary", "retrievedOn", "valueStatus"):
            if field not in observation or observation.get(field) is None:
                errors.append(f"externalObservations[{index}].{field} is required")

    companies = keys["companies"]
    account_company_keys: list[str] = []
    for index, account in enumerate(collections["commercialAccounts"]):
        if isinstance(account, dict) and account.get("companyKey") not in companies:
            errors.append(f"commercialAccounts[{index}] references unknown companyKey")
        if isinstance(account, dict) and account.get("companyKey"):
            account_company_keys.append(str(account["companyKey"]))
    duplicate_account_companies = [
        value for value, count in Counter(account_company_keys).items() if count > 1
    ]
    if duplicate_account_companies:
        errors.append(
            "commercialAccounts violates one-account-per-company-per-market: "
            f"{duplicate_account_companies}"
        )
    for index, project in enumerate(collections["projects"]):
        if not isinstance(project, dict):
            continue
        for field in ("projectName", "country"):
            if not project.get(field):
                errors.append(f"projects[{index}].{field} is required")
        if project.get("matchedProductCodes") and foundation_status == "unavailable":
            errors.append(f"projects[{index}] cannot publish matchedProductCodes without capability foundation")
    opportunity_project_keys: list[str] = []
    for index, opportunity in enumerate(collections["opportunities"]):
        if not isinstance(opportunity, dict):
            continue
        if opportunity.get("commercialAccountKey") not in keys["commercialAccounts"]:
            errors.append(f"opportunities[{index}] references unknown commercialAccountKey")
        if opportunity.get("projectKey") not in keys["projects"]:
            errors.append(f"opportunities[{index}] references unknown projectKey")
        elif opportunity.get("projectKey"):
            opportunity_project_keys.append(str(opportunity["projectKey"]))
    duplicate_opportunity_projects = [
        value for value, count in Counter(opportunity_project_keys).items() if count > 1
    ]
    if duplicate_opportunity_projects:
        errors.append(
            "opportunities violates one-opportunity-per-project: "
            f"{duplicate_opportunity_projects}"
        )
    role_pairs: set[tuple[str, str]] = set()
    for index, role in enumerate(list_value(root, "companyRoles", errors)):
        if not isinstance(role, dict):
            errors.append(f"companyRoles[{index}] must be an object")
            continue
        company_key, role_code = role.get("companyKey"), role.get("roleCode")
        if company_key not in companies:
            errors.append(f"companyRoles[{index}] references unknown companyKey")
        if not role_code:
            errors.append(f"companyRoles[{index}].roleCode is required")
        pair = (str(company_key), str(role_code))
        if pair in role_pairs:
            errors.append(f"duplicate company role: {pair}")
        role_pairs.add(pair)

    for index, relationship in enumerate(collections["relationships"]):
        if not isinstance(relationship, dict):
            continue
        source = relationship.get("sourceCompanyKey")
        target = relationship.get("targetCompanyKey")
        relation_type = str(relationship.get("relationshipType") or "").lower()
        if source not in companies or target not in companies:
            errors.append(f"relationships[{index}] references unknown company")
        if source == target and source:
            errors.append(f"relationships[{index}] is a self-edge")
        if not relation_type:
            errors.append(f"relationships[{index}].relationshipType is required")
        if relation_type in ROLE_RELATIONSHIP_TYPES:
            errors.append(f"relationships[{index}] uses node role as relationshipType: {relation_type}")
        if relationship.get("projectKey") and relationship["projectKey"] not in keys["projects"]:
            errors.append(f"relationships[{index}] references unknown projectKey")

    sources = keys["sources"]
    claims = keys["claims"]
    supports: dict[str, set[str]] = {}
    for index, link in enumerate(collections["claimSourceLinks"]):
        if not isinstance(link, dict):
            continue
        claim_key, source_key = link.get("claimKey"), link.get("sourceKey")
        if claim_key not in claims:
            errors.append(f"claimSourceLinks[{index}] references unknown claimKey")
        if source_key not in sources:
            errors.append(f"claimSourceLinks[{index}] references unknown sourceKey")
        relation_type = str(link.get("relationType") or "").lower()
        if relation_type not in {"supports", "refutes", "context"}:
            errors.append(f"claimSourceLinks[{index}].relationType is invalid")
        if relation_type == "supports":
            supports.setdefault(str(claim_key), set()).add(str(source_key))
    for index, source in enumerate(collections["sources"]):
        if not isinstance(source, dict):
            continue
        for field in ("url", "title", "sourceType", "retrievedOn"):
            if not source.get(field):
                errors.append(f"sources[{index}].{field} is required")
        if not source.get("publisher"):
            warnings.append(f"sources[{index}].publisher is missing")
    for index, claim in enumerate(collections["claims"]):
        if not isinstance(claim, dict):
            continue
        for field in ("claimType", "valueStatus", "targetType", "targetKey"):
            if not claim.get(field):
                errors.append(f"claims[{index}].{field} is required")
        value_status = str(claim.get("valueStatus") or "").replace("_", "").lower()
        if value_status == "observed" and not supports.get(str(claim.get("claimKey"))):
            errors.append(f"observed claims[{index}] has no Supports source")

    all_dimensions = list_value(root, "assessmentDimensions", errors)
    dimensions_by_assessment: dict[str, list[dict[str, Any]]] = {}
    for index, dimension in enumerate(all_dimensions):
        if not isinstance(dimension, dict):
            errors.append(f"assessmentDimensions[{index}] must be an object")
            continue
        assessment_key = dimension.get("assessmentKey")
        if assessment_key not in keys["assessments"]:
            errors.append(f"assessmentDimensions[{index}] references unknown assessmentKey")
        dimensions_by_assessment.setdefault(str(assessment_key), []).append(dimension)
        for source_key in dimension.get("sourceKeys", []) or []:
            if source_key not in sources:
                errors.append(f"assessmentDimensions[{index}] references unknown sourceKey")
        for claim_key in dimension.get("claimKeys", []) or []:
            if claim_key not in claims:
                errors.append(f"assessmentDimensions[{index}] references unknown claimKey")
        if dimension.get("finalDimensionScore") is not None:
            if not dimension.get("rationale"):
                errors.append(f"assessmentDimensions[{index}].rationale is required when scored")
            if not dimension.get("claimKeys") or not dimension.get("sourceKeys"):
                errors.append(f"assessmentDimensions[{index}] requires dimension-specific evidence when scored")
        code = dimension.get("dimensionCode")
        maximum = LEAD_DIMENSIONS.get(str(code))
        observed = dimension.get("observedScore")
        final = dimension.get("finalDimensionScore")
        if maximum is not None:
            for field, value in (("observedScore", observed), ("finalDimensionScore", final)):
                if value is not None and (
                    not isinstance(value, (int, float)) or not 0 <= float(value) <= maximum
                ):
                    errors.append(
                        f"assessmentDimensions[{index}].{field} must be between 0 and {maximum}"
                    )
        if dimension.get("evidenceGrade") == "U" and final is not None:
            errors.append(
                f"assessmentDimensions[{index}] cannot score an evidenceGrade=U dimension"
            )

    for index, assessment in enumerate(collections["assessments"]):
        if not isinstance(assessment, dict):
            continue
        assessment_key = str(assessment.get("assessmentKey"))
        dimensions = dimensions_by_assessment.get(assessment_key, [])
        if assessment.get("assessmentModelCode") == "GETO_LEAD_VALUE":
            producer = assessment.get("producerSkill")
            diligence_status = assessment.get("diligenceStatus")
            assessment_status = assessment.get("assessmentStatus")
            if producer != "geto-diligence-company":
                errors.append(
                    f"assessments[{index}] GETO_LEAD_VALUE producerSkill must be geto-diligence-company"
                )
            if diligence_status not in DILIGENCE_STATUSES:
                errors.append(f"assessments[{index}].diligenceStatus is invalid")
            if assessment_status not in ASSESSMENT_STATUSES - {"not_requested"}:
                errors.append(f"assessments[{index}].assessmentStatus is invalid")
            if assessment.get("assessmentMode") not in {None, "lead_value"}:
                errors.append(f"assessments[{index}].assessmentMode must be lead_value")
            if diligence_status not in {"completed", "completed_with_explicit_gaps"}:
                if assessment_status != "pending_diligence":
                    errors.append(
                        f"assessments[{index}] non-completed diligence requires pending_diligence"
                    )
            elif foundation_status != "available":
                if assessment_status != "pending_capability_foundation":
                    errors.append(
                        f"assessments[{index}] unavailable capability foundation requires "
                        "pending_capability_foundation"
                    )
            elif not assessment.get("modelVersion"):
                if assessment_status != "pending_model":
                    errors.append(
                        f"assessments[{index}] missing modelVersion requires pending_model"
                    )
            dimension_map = {item.get("dimensionCode"): item for item in dimensions}
            if dimensions and set(dimension_map) != set(LEAD_DIMENSIONS):
                errors.append(f"assessments[{index}] GETO_LEAD_VALUE requires exactly six dimensions")
            for code, maximum in LEAD_DIMENSIONS.items():
                item = dimension_map.get(code)
                if item is not None and item.get("maxScore") != maximum:
                    errors.append(f"assessments[{index}] {code}.maxScore must be {maximum}")
            unscored = [
                item for item in dimensions
                if not isinstance(item.get("finalDimensionScore"), (int, float))
                or item.get("evidenceGrade") == "U"
            ]
            if (
                diligence_status in {"completed", "completed_with_explicit_gaps"}
                and foundation_status == "available"
                and assessment.get("modelVersion")
                and dimensions
                and unscored
                and assessment_status != "incomplete_evidence"
            ):
                errors.append(
                    f"assessments[{index}] unscored dimension requires incomplete_evidence"
                )
            if assessment_status == "completed":
                if set(dimension_map) != set(LEAD_DIMENSIONS) or unscored:
                    errors.append(
                        f"assessments[{index}] completed requires six scored dimensions"
                    )
                if assessment.get("scoreCalculatedBy") not in ASSESSMENT_CALCULATORS:
                    errors.append(
                        f"assessments[{index}] completed requires deterministic/server calculator"
                    )
        total = assessment.get("totalScore")
        level = assessment.get("rating", assessment.get("levelCode"))
        assessment_status = assessment.get("assessmentStatus")
        if assessment_status != "completed" and (total is not None or level is not None):
            errors.append(
                f"assessments[{index}] non-completed assessment cannot publish total or level"
            )
        if total is not None:
            for field in ("assessmentModelCode", "modelVersion", "asOf"):
                if not assessment.get(field):
                    errors.append(f"assessments[{index}].{field} is required when totalScore is set")
            scores = [item.get("finalDimensionScore") for item in dimensions]
            if not dimensions or any(not isinstance(score, (int, float)) for score in scores):
                errors.append(f"assessments[{index}] totalScore requires numeric dimensions")
            elif not math.isclose(float(total), sum(float(score) for score in scores), abs_tol=0.01):
                errors.append(f"assessments[{index}] totalScore does not equal dimension sum")
            if assessment.get("scoreCalculatedBy") not in ASSESSMENT_CALCULATORS:
                errors.append(
                    f"assessments[{index}] totalScore requires deterministic/server calculator"
                )
        if level is not None:
            if level not in LEAD_LEVELS:
                errors.append(f"assessments[{index}] lead level must be A, B, C or U")
            if not assessment.get("ratingScaleVersion"):
                errors.append(f"assessments[{index}] level requires ratingScaleVersion")
        rationales = [str(item.get("rationale") or "").strip() for item in dimensions]
        if len(rationales) > 1 and rationales[0] and len(set(rationales)) == 1:
            errors.append(f"assessments[{index}] copies one rationale to every dimension")
        source_sets = [tuple(sorted(item.get("sourceKeys", []) or [])) for item in dimensions]
        if len(source_sets) > 1 and source_sets[0] and len(set(source_sets)) == 1:
            warnings.append(f"assessments[{index}] maps the same sources to every dimension; verify links")

    for name in ("contacts", "customsEvidence", "financialRecords"):
        for index, item in enumerate(collections[name]):
            if not isinstance(item, dict):
                continue
            company_key = item.get("companyKey") or item.get("subjectCompanyKey")
            if company_key not in companies:
                errors.append(f"{name}[{index}] references unknown companyKey")

    for index, operation in enumerate(list_value(root, "draftOperations", errors)):
        text = json.dumps(operation, ensure_ascii=False).lower()
        if "/approvals" in text or ":approve" in text or ":reject" in text:
            errors.append(f"draftOperations[{index}] contains a forbidden approval operation")

    if root.get("deliveryStatus") not in {
        "ready_for_private_draft", "private_drafts_written", "submitted",
        "blocked_market_unavailable", "blocked_validation",
    }:
        errors.append("deliveryStatus is invalid")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    args = parser.parse_args()
    try:
        errors, warnings = validate(Path(args.path))
    except (OSError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "errors": [str(error)], "warnings": []}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps({"valid": not errors, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
