#!/usr/bin/env python3
"""Validate diligence/assessment lifecycle invariants for one EvidencePackage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DILIGENCE_STATUSES = {
    "completed", "completed_with_explicit_gaps", "pending", "failed", "identity_conflict",
}
ASSESSMENT_STATUSES = {
    "not_requested", "pending_diligence", "pending_capability_foundation",
    "pending_model", "incomplete_evidence", "completed",
}


def validate(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    company = value.get("company")
    if not isinstance(company, dict) or not company.get("companyKey"):
        errors.append("company.companyKey is required")

    mode = value.get("assessmentMode")
    diligence_status = value.get("diligenceStatus")
    assessment_status = value.get("assessmentStatus")
    assessment = value.get("assessment")
    if mode not in {"none", "lead_value"}:
        errors.append("assessmentMode must be none or lead_value")
    if diligence_status not in DILIGENCE_STATUSES:
        errors.append("diligenceStatus is invalid")
    if assessment_status not in ASSESSMENT_STATUSES:
        errors.append("assessmentStatus is invalid")

    if mode == "none":
        if assessment_status != "not_requested":
            errors.append("assessmentMode=none requires assessmentStatus=not_requested")
        if assessment is not None:
            errors.append("assessmentMode=none must not produce Assessment")
        return errors

    if assessment_status == "not_requested":
        errors.append("assessmentMode=lead_value cannot use assessmentStatus=not_requested")
    if diligence_status not in {"completed", "completed_with_explicit_gaps"}:
        if assessment_status != "pending_diligence":
            errors.append("non-completed diligence requires assessmentStatus=pending_diligence")

    handoff = value.get("capabilityHandoff")
    foundation_status = handoff.get("foundationStatus") if isinstance(handoff, dict) else None
    if (
        diligence_status in {"completed", "completed_with_explicit_gaps"}
        and foundation_status in {"partial", "unavailable"}
        and assessment_status != "pending_capability_foundation"
    ):
        errors.append("partial/unavailable foundation requires pending_capability_foundation")

    if assessment is not None and not isinstance(assessment, dict):
        errors.append("assessment must be an object or null")
        return errors
    if isinstance(assessment, dict):
        if assessment.get("producerSkill") != "geto-diligence-company":
            errors.append("Assessment producerSkill must be geto-diligence-company")
        if assessment.get("assessmentModelCode") != "GETO_LEAD_VALUE":
            errors.append("Assessment assessmentModelCode must be GETO_LEAD_VALUE")
        has_total_or_level = any(
            assessment.get(field) is not None for field in ("totalScore", "rating", "levelCode")
        )
        if (
            assessment_status != "completed"
            or diligence_status not in {"completed", "completed_with_explicit_gaps"}
        ) and has_total_or_level:
            errors.append("non-completed assessment cannot publish total or level")
    if assessment_status == "completed" and not isinstance(assessment, dict):
        errors.append("assessmentStatus=completed requires Assessment")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    args = parser.parse_args()
    try:
        value = json.loads(Path(args.path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "errors": [str(error)]}, ensure_ascii=False, indent=2))
        return 2
    if not isinstance(value, dict):
        errors = ["root must be an object"]
    else:
        errors = validate(value)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
