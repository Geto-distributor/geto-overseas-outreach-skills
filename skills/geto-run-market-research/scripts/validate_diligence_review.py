#!/usr/bin/env python3
"""Validate a country-main-task diligence review decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REVIEW_STATUSES = {"accepted", "accepted_with_gaps", "returned_for_followup", "rejected"}
COVERAGE_STATUSES = {"exhaustive", "bounded", "partial", "not_queried", "not_applicable"}
CRITICAL_DOMAINS = {
    "identity",
    "officialWebsite",
    "socialMedia",
    "projects",
    "externalCorroboration",
    "providerReconciliation",
    "procurementChain",
    "classification",
}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_nonempty_string(item) for item in value)


def validate_review(review: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in (
        "companyName",
        "reviewedOn",
        "reviewerTaskTitle",
        "sourceTaskTitle",
        "reviewStatus",
        "artifactChecks",
        "coverage",
        "challengeFindings",
        "followUp",
        "reviewConclusion",
        "progressSectionName",
    ):
        if field not in review:
            errors.append(f"missing field: {field}")

    for field in ("companyName", "reviewedOn", "reviewerTaskTitle", "sourceTaskTitle", "reviewConclusion", "progressSectionName"):
        if field in review and not _nonempty_string(review[field]):
            errors.append(f"{field} must be a non-empty string")

    status = review.get("reviewStatus")
    if status not in REVIEW_STATUSES:
        errors.append(f"reviewStatus must be one of {sorted(REVIEW_STATUSES)}")

    artifacts = review.get("artifactChecks")
    if not isinstance(artifacts, dict):
        errors.append("artifactChecks must be an object")
        artifacts = {}
    for field in ("companyJson", "report", "sources", "validatorReproduced"):
        if not isinstance(artifacts.get(field), bool):
            errors.append(f"artifactChecks.{field} must be boolean")
    validator_errors = artifacts.get("validatorErrors")
    if not isinstance(validator_errors, int) or isinstance(validator_errors, bool) or validator_errors < 0:
        errors.append("artifactChecks.validatorErrors must be a non-negative integer")

    coverage = review.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("coverage must be an object")
        coverage = {}
    missing_domains = sorted(CRITICAL_DOMAINS - set(coverage))
    if missing_domains:
        errors.append(f"coverage missing domains: {', '.join(missing_domains)}")

    for domain in sorted(CRITICAL_DOMAINS & set(coverage)):
        item = coverage[domain]
        if not isinstance(item, dict):
            errors.append(f"coverage.{domain} must be an object")
            continue
        if item.get("status") not in COVERAGE_STATUSES:
            errors.append(f"coverage.{domain}.status must be one of {sorted(COVERAGE_STATUSES)}")
        if not _nonempty_string(item.get("queryBoundary")):
            errors.append(f"coverage.{domain}.queryBoundary must be a non-empty string")
        for field in ("evidenceRefs", "gaps", "nextActions"):
            if not _string_list(item.get(field)):
                errors.append(f"coverage.{domain}.{field} must be a string array")

    website = coverage.get("officialWebsite", {})
    if isinstance(website, dict):
        for field in ("sectionsDiscovered", "sectionsReviewed", "inaccessibleSections"):
            if not _string_list(website.get(field)):
                errors.append(f"coverage.officialWebsite.{field} must be a string array")
        pages_reviewed = website.get("pagesReviewed")
        if not isinstance(pages_reviewed, int) or isinstance(pages_reviewed, bool) or pages_reviewed < 0:
            errors.append("coverage.officialWebsite.pagesReviewed must be a non-negative integer")
        discovered = set(website.get("sectionsDiscovered", [])) if isinstance(website.get("sectionsDiscovered"), list) else set()
        accounted = set(website.get("sectionsReviewed", [])) | set(website.get("inaccessibleSections", []))
        unaccounted = sorted(discovered - accounted)
        if unaccounted:
            errors.append(f"official website sections are unaccounted for: {', '.join(unaccounted)}")

    social = coverage.get("socialMedia", {})
    if isinstance(social, dict):
        channels = social.get("channels")
        if not isinstance(channels, list):
            errors.append("coverage.socialMedia.channels must be an array")
        else:
            for index, channel in enumerate(channels):
                if not isinstance(channel, dict):
                    errors.append(f"coverage.socialMedia.channels[{index}] must be an object")
                    continue
                for field in ("platform", "url", "queryBoundary"):
                    if not _nonempty_string(channel.get(field)):
                        errors.append(f"coverage.socialMedia.channels[{index}].{field} must be a non-empty string")
                for field in ("accessiblePosts", "reviewedPosts"):
                    value = channel.get(field)
                    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                        errors.append(f"coverage.socialMedia.channels[{index}].{field} must be a non-negative integer")
                if isinstance(channel.get("accessiblePosts"), int) and isinstance(channel.get("reviewedPosts"), int):
                    if channel["reviewedPosts"] > channel["accessiblePosts"]:
                        errors.append(f"coverage.socialMedia.channels[{index}] reviewedPosts cannot exceed accessiblePosts")

    projects = coverage.get("projects", {})
    if isinstance(projects, dict):
        for field in ("projectsDiscovered", "projectsReviewed", "priorityProjectsDiscovered", "priorityProjectsReviewed"):
            value = projects.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"coverage.projects.{field} must be a non-negative integer")
        if not _string_list(projects.get("projectFieldsReviewed")):
            errors.append("coverage.projects.projectFieldsReviewed must be a string array")
        if isinstance(projects.get("projectsDiscovered"), int) and isinstance(projects.get("projectsReviewed"), int):
            if projects["projectsReviewed"] > projects["projectsDiscovered"]:
                errors.append("coverage.projects.projectsReviewed cannot exceed projectsDiscovered")
        if isinstance(projects.get("priorityProjectsDiscovered"), int) and isinstance(projects.get("priorityProjectsReviewed"), int):
            if projects["priorityProjectsReviewed"] > projects["priorityProjectsDiscovered"]:
                errors.append("coverage.projects.priorityProjectsReviewed cannot exceed priorityProjectsDiscovered")

    findings = review.get("challengeFindings")
    if not isinstance(findings, list):
        errors.append("challengeFindings must be an array")
        findings = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"challengeFindings[{index}] must be an object")
            continue
        if finding.get("severity") not in {"blocking", "material", "minor"}:
            errors.append(f"challengeFindings[{index}].severity is invalid")
        if finding.get("status") not in {"open", "resolved", "accepted_gap"}:
            errors.append(f"challengeFindings[{index}].status is invalid")
        for field in ("question", "finding", "requiredAction"):
            if not _nonempty_string(finding.get(field)):
                errors.append(f"challengeFindings[{index}].{field} must be a non-empty string")

    follow_up = review.get("followUp")
    if not isinstance(follow_up, dict):
        errors.append("followUp must be an object")
        follow_up = {}
    if not isinstance(follow_up.get("required"), bool):
        errors.append("followUp.required must be boolean")
    if not isinstance(follow_up.get("cycle"), int) or isinstance(follow_up.get("cycle"), bool) or follow_up.get("cycle", -1) < 0:
        errors.append("followUp.cycle must be a non-negative integer")
    if not _string_list(follow_up.get("questions")):
        errors.append("followUp.questions must be a string array")

    open_blocking = any(
        isinstance(item, dict) and item.get("severity") == "blocking" and item.get("status") == "open"
        for item in findings
    )
    open_material = any(
        isinstance(item, dict) and item.get("severity") == "material" and item.get("status") == "open"
        for item in findings
    )
    accepted = status in {"accepted", "accepted_with_gaps"}
    if accepted:
        if any(artifacts.get(field) is not True for field in ("companyJson", "report", "sources", "validatorReproduced")):
            errors.append("accepted review requires all artifacts and reproduced validator")
        if validator_errors != 0:
            errors.append("accepted review requires validatorErrors=0")
        if open_blocking:
            errors.append("accepted review cannot have an open blocking challenge")
        if open_material:
            errors.append("accepted review cannot have an open material challenge; use accepted_gap or follow-up")
        for domain in ("identity", "officialWebsite", "socialMedia", "projects", "externalCorroboration", "classification"):
            domain_status = coverage.get(domain, {}).get("status") if isinstance(coverage.get(domain), dict) else None
            if domain_status not in {"exhaustive", "bounded", "not_applicable"}:
                errors.append(f"accepted review requires bounded or exhaustive coverage for {domain}")
        if isinstance(website, dict) and website.get("status") != "not_applicable" and website.get("pagesReviewed", 0) <= 1:
            errors.append("accepted review cannot rely on only a homepage or single website page")
        if isinstance(projects, dict):
            if projects.get("priorityProjectsReviewed", 0) < projects.get("priorityProjectsDiscovered", 0):
                errors.append("accepted review must inspect every discovered priority project")
            if projects.get("priorityProjectsDiscovered", 0) > 0:
                procurement_status = coverage.get("procurementChain", {}).get("status") if isinstance(coverage.get("procurementChain"), dict) else None
                if procurement_status not in {"exhaustive", "bounded"}:
                    errors.append("accepted review with priority projects requires bounded or exhaustive procurement-chain coverage")
        if follow_up.get("required") is True:
            errors.append("accepted review cannot require follow-up")

    if status == "returned_for_followup":
        if follow_up.get("required") is not True or not follow_up.get("questions"):
            errors.append("returned_for_followup requires actionable follow-up questions")
    if status == "rejected" and not findings:
        errors.append("rejected review requires at least one challenge finding")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_file", type=Path)
    args = parser.parse_args()
    value = json.loads(args.review_file.read_text(encoding="utf-8"))
    errors = validate_review(value)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
