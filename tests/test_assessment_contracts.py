from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EVIDENCE_VALIDATOR = load_module(
    "validate_evidence_package",
    ROOT / "skills/geto-diligence-company/scripts/validate_evidence_package.py",
)
DELTA_VALIDATOR = load_module(
    "validate_research_delta",
    ROOT / "skills/geto-run-market-research/scripts/validate_research_delta.py",
)


def evidence_package(**overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "assessmentMode": "none",
        "company": {"companyKey": "company:au:example"},
        "capabilityHandoff": {"foundationStatus": "available"},
        "diligenceStatus": "completed",
        "assessmentStatus": "not_requested",
        "assessment": None,
    }
    value.update(overrides)
    return value


def base_delta() -> dict[str, Any]:
    return {
        "researchRun": {
            "researchRunKey": "test:au:assessment",
            "marketCode": "AU",
            "scopeCode": "construction_formwork",
            "asOf": "2026-08-13",
            "resultMode": "sample",
            "sampleBoundary": "unit fixture",
            "provenance": {"skill": "geto-run-market-research"},
        },
        "release": {
            "marketCode": "AU", "scopeCode": "construction_formwork",
            "country": "AU", "asOf": "2026-08-13", "resultMode": "sample",
            "publicationStatus": "private_draft",
        },
        "capabilityFoundation": {
            "foundationKey": "geto:capability-foundation", "asOf": "2026-08-13",
            "contentHash": "sha256:test", "status": "available", "productCodes": [],
            "scenarioCodes": [], "caseKeys": [], "sourceKeys": [], "gapCodes": [],
        },
        "providerStatuses": {}, "externalObservations": [],
        "sourcePackages": [{
            "sourcePackageKey": "package:test", "researchRunKey": "test:au:assessment",
            "sourceType": "unit_fixture",
        }],
        "companies": [{"companyKey": "company:au:example"}], "companyRoles": [],
        "commercialAccounts": [{
            "commercialAccountKey": "account:au:example", "companyKey": "company:au:example",
        }],
        "legalEntities": [], "projects": [], "opportunities": [], "products": [],
        "relationships": [], "assessments": [], "assessmentDimensions": [],
        "claims": [{
            "claimKey": "claim:test", "claimType": "unit", "valueStatus": "observed",
            "targetType": "Company", "targetKey": "company:au:example",
        }],
        "sources": [{
            "sourceKey": "source:test", "url": "https://example.com", "title": "Fixture",
            "sourceType": "official", "publisher": "Example", "retrievedOn": "2026-08-13",
        }],
        "claimSourceLinks": [{
            "linkKey": "link:test", "claimKey": "claim:test", "sourceKey": "source:test",
            "relationType": "supports",
        }],
        "contacts": [], "customsEvidence": [], "financialRecords": [],
        "draftOperations": [], "deliveryStatus": "ready_for_private_draft",
    }


def add_completed_assessment(delta: dict[str, Any], producer: str = "geto-diligence-company") -> None:
    maxima = DELTA_VALIDATOR.LEAD_DIMENSIONS
    dimensions = []
    for index, (code, maximum) in enumerate(maxima.items()):
        score = maximum / 2
        dimensions.append({
            "assessmentKey": "assessment:test", "dimensionCode": code,
            "observedScore": score, "finalDimensionScore": score, "maxScore": maximum,
            "evidenceGrade": "A", "rationale": f"dimension rationale {index}",
            "claimKeys": ["claim:test"], "sourceKeys": ["source:test"],
        })
    delta["assessmentDimensions"] = dimensions
    delta["assessments"] = [{
        "assessmentKey": "assessment:test", "assessmentModelCode": "GETO_LEAD_VALUE",
        "assessmentMode": "lead_value", "producerSkill": producer,
        "diligenceStatus": "completed", "assessmentStatus": "completed",
        "modelVersion": "approved-v1", "asOf": "2026-08-13", "totalScore": 50,
        "rating": "B", "ratingScaleVersion": "approved-v1",
        "scoreCalculatedBy": "deterministic_validator",
    }]


def validate_delta(value: dict[str, Any]) -> tuple[list[str], list[str]]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "delta.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return DELTA_VALIDATOR.validate(path)


class EvidencePackageLifecycleTests(unittest.TestCase):
    def test_none_produces_no_assessment(self) -> None:
        self.assertEqual(EVIDENCE_VALIDATOR.validate(evidence_package()), [])

    def test_identity_conflict_cannot_score(self) -> None:
        value = evidence_package(
            assessmentMode="lead_value", diligenceStatus="identity_conflict",
            assessmentStatus="completed",
            assessment={
                "producerSkill": "geto-diligence-company",
                "assessmentModelCode": "GETO_LEAD_VALUE", "totalScore": 80,
            },
        )
        errors = EVIDENCE_VALIDATOR.validate(value)
        self.assertTrue(any("pending_diligence" in error for error in errors))
        self.assertTrue(any("cannot publish total" in error for error in errors))

    def test_pending_failed_and_identity_conflict_stay_pending_diligence(self) -> None:
        for diligence_status in ("pending", "failed", "identity_conflict"):
            with self.subTest(diligence_status=diligence_status):
                value = evidence_package(
                    assessmentMode="lead_value", diligenceStatus=diligence_status,
                    assessmentStatus="pending_diligence",
                )
                self.assertEqual(EVIDENCE_VALIDATOR.validate(value), [])

    def test_unavailable_foundation_stays_pending_without_assessment(self) -> None:
        value = evidence_package(
            assessmentMode="lead_value", assessmentStatus="pending_capability_foundation",
            capabilityHandoff={"foundationStatus": "unavailable"},
        )
        self.assertEqual(EVIDENCE_VALIDATOR.validate(value), [])

    def test_unavailable_model_stays_pending_without_total(self) -> None:
        value = evidence_package(
            assessmentMode="lead_value", assessmentStatus="pending_model"
        )
        self.assertEqual(EVIDENCE_VALIDATOR.validate(value), [])


class ResearchDeltaAssessmentTests(unittest.TestCase):
    def test_completed_diligence_assessment_is_valid(self) -> None:
        delta = base_delta()
        add_completed_assessment(delta)
        errors, _ = validate_delta(delta)
        self.assertEqual(errors, [])

    def test_find_leads_cannot_be_assessment_producer(self) -> None:
        delta = base_delta()
        add_completed_assessment(delta, producer="geto-find-leads")
        errors, _ = validate_delta(delta)
        self.assertTrue(any("producerSkill" in error for error in errors))

    def test_incomplete_dimension_blocks_total_and_level(self) -> None:
        delta = base_delta()
        add_completed_assessment(delta)
        delta["assessmentDimensions"][0]["finalDimensionScore"] = None
        delta["assessments"][0]["assessmentStatus"] = "incomplete_evidence"
        errors, _ = validate_delta(delta)
        self.assertTrue(any("cannot publish total or level" in error for error in errors))

    def test_completed_with_explicit_gaps_can_stay_incomplete_without_total(self) -> None:
        delta = base_delta()
        add_completed_assessment(delta)
        delta["assessmentDimensions"][0]["finalDimensionScore"] = None
        assessment = delta["assessments"][0]
        assessment["diligenceStatus"] = "completed_with_explicit_gaps"
        assessment["assessmentStatus"] = "incomplete_evidence"
        assessment["totalScore"] = None
        assessment.pop("rating")
        assessment.pop("ratingScaleVersion")
        errors, _ = validate_delta(delta)
        self.assertEqual(errors, [])

    def test_duplicate_account_for_company_is_rejected(self) -> None:
        delta = base_delta()
        delta["commercialAccounts"].append({
            "commercialAccountKey": "account:au:duplicate", "companyKey": "company:au:example",
        })
        errors, _ = validate_delta(delta)
        self.assertTrue(any("one-account-per-company-per-market" in error for error in errors))

    def test_competitor_contract_defaults_self_to_no_assessment(self) -> None:
        text = (
            ROOT / "skills/geto-mine-competitor-customers/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("竞对本身默认调用 diligence 的 `assessmentMode=none`", text)
        self.assertIn("合格竞对客户进入统一线索池后调用 `assessmentMode=lead_value`", text)


if __name__ == "__main__":
    unittest.main()
