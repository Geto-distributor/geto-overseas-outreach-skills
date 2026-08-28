from __future__ import annotations

import importlib.util
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPTS = ROOT / "skills/geto-run-market-research/scripts"
CAPABILITY_SCRIPTS = ROOT / "skills/geto-capability-foundation/scripts"
DILIGENCE_SCRIPTS = ROOT / "skills/geto-diligence-company/scripts"
FIND_LEADS_SCRIPTS = ROOT / "skills/geto-find-leads/scripts"
INQUIRY_SCRIPTS = ROOT / "skills/geto-diligence-inquiry/scripts"
COMPETITOR_CUSTOMER_SCRIPTS = ROOT / "skills/geto-mine-competitor-customers/scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


import sys
sys.path.insert(0, str(RUN_SCRIPTS))
RESEARCH_BUNDLE = load_module("research_bundle", RUN_SCRIPTS / "research_bundle.py")
SOURCE_BUILDER = load_module("build_deduplicated_sources", RUN_SCRIPTS / "build_deduplicated_sources.py")
WORKSPACE_VALIDATOR = load_module("validate_workspace", RUN_SCRIPTS / "validate_workspace.py")
LEXICON_VALIDATOR = load_module("validate_search_lexicon", CAPABILITY_SCRIPTS / "validate_search_lexicon.py")
ASSESSMENT_CALCULATOR = load_module("calculate_lead_assessment", DILIGENCE_SCRIPTS / "calculate_lead_assessment.py")
COHORT_CALCULATOR = load_module("calculate_lead_cohort", FIND_LEADS_SCRIPTS / "calculate_lead_cohort.py")
INQUIRY_CALCULATOR = load_module("calculate_inquiry_readiness", INQUIRY_SCRIPTS / "calculate_inquiry_readiness.py")
INQUIRY_INTAKE_GATE = load_module("validate_inquiry_intake", INQUIRY_SCRIPTS / "validate_inquiry_intake.py")
PUBLICATION_GATE = load_module("validate_publication_gate", INQUIRY_SCRIPTS / "validate_publication_gate.py")
COMPETITOR_CUSTOMER_AGGREGATOR = load_module(
    "aggregate_competitor_customers",
    COMPETITOR_CUSTOMER_SCRIPTS / "aggregate_competitor_customers.py",
)
COMPANY_EXAMPLE_GENERATOR = load_module(
    "generate_company_json_example",
    RUN_SCRIPTS / "generate_company_json_example.py",
)
DILIGENCE_REVIEW_VALIDATOR = load_module(
    "validate_diligence_review",
    RUN_SCRIPTS / "validate_diligence_review.py",
)
WORKSPACE_INITIALIZER = load_module(
    "init_company_workspace",
    RUN_SCRIPTS / "init_company_workspace.py",
)


def evidence(url: str = "https://example.com/product") -> dict[str, object]:
    return {
        "sourceTitle": "Official product page", "sourceUrl": url,
        "publisher": "Example", "sourceType": "official_website",
        "publishedOn": None, "retrievedOn": "2026-08-19",
        "locator": "Products", "excerpt": "Product system", "note": "Fixture",
    }


def base_company() -> dict[str, object]:
    return RESEARCH_BUNDLE.empty_company("Example", "Australia", "AU")


class ResearchBundleValidationTests(unittest.TestCase):
    def test_diligence_review_example_passes_research_sufficiency_gate(self) -> None:
        review = json.loads((
            ROOT / "skills/geto-run-market-research/references/diligence-review-example.json"
        ).read_text(encoding="utf-8"))
        self.assertEqual(DILIGENCE_REVIEW_VALIDATOR.validate_review(review), [])

    def test_diligence_review_rejects_shallow_site_and_project_coverage(self) -> None:
        review = json.loads((
            ROOT / "skills/geto-run-market-research/references/diligence-review-example.json"
        ).read_text(encoding="utf-8"))
        review["reviewStatus"] = "accepted"
        review["coverage"]["officialWebsite"]["pagesReviewed"] = 1
        review["coverage"]["officialWebsite"]["sectionsReviewed"].remove("Projects")
        review["coverage"]["projects"]["priorityProjectsReviewed"] = 2
        review["coverage"]["procurementChain"]["status"] = "not_queried"
        review["challengeFindings"] = []
        errors = DILIGENCE_REVIEW_VALIDATOR.validate_review(review)
        self.assertTrue(any("sections are unaccounted" in item for item in errors))
        self.assertTrue(any("homepage or single website page" in item for item in errors))
        self.assertTrue(any("every discovered priority project" in item for item in errors))
        self.assertTrue(any("procurement-chain coverage" in item for item in errors))

    def test_returned_diligence_review_requires_actionable_followup(self) -> None:
        review = json.loads((
            ROOT / "skills/geto-run-market-research/references/diligence-review-example.json"
        ).read_text(encoding="utf-8"))
        review["reviewStatus"] = "returned_for_followup"
        review["followUp"] = {"required": True, "cycle": 1, "questions": []}
        errors = DILIGENCE_REVIEW_VALIDATOR.validate_review(review)
        self.assertTrue(any("actionable follow-up questions" in item for item in errors))

    def test_inquiry_intake_gate_routes_identity_and_provider_gaps_without_stopping_research(self) -> None:
        manifest = json.loads(
            (ROOT / "skills/geto-diligence-inquiry/references/inquiry-intake-example.json").read_text(
                encoding="utf-8"
            )
        )
        result = INQUIRY_INTAKE_GATE.validate_intake(manifest)
        self.assertEqual(result["gateStatus"], "ready_for_diligence")
        manifest["tradewind"]["status"] = "no_result"
        result = INQUIRY_INTAKE_GATE.validate_intake(manifest)
        self.assertEqual(result["gateStatus"], "diligence_with_identity_gaps")
        self.assertTrue(result["researchAllowed"])
        manifest["tradewind"]["status"] = "not_configured"
        result = INQUIRY_INTAKE_GATE.validate_intake(manifest)
        self.assertEqual(result["gateStatus"], "diligence_with_provider_gaps")
        self.assertTrue(result["researchAllowed"])

    def test_inquiry_intake_gate_uses_partial_anchors_and_only_blocks_without_any_anchor(self) -> None:
        manifest = {
            "companyName": "",
            "requirement": {"requestedProduct": ""},
            "email": "buyer@invalid",
            "webSearch": {"status": "found", "strongIdentityMatch": False, "matchedEntity": "Candidate", "evidence": [{}]},
            "tradewind": {"status": "found", "strongIdentityMatch": False, "matchedEntity": "Candidate", "evidence": [{}]},
        }
        result = INQUIRY_INTAKE_GATE.validate_intake(manifest)
        self.assertEqual(result["gateStatus"], "diligence_with_partial_intake")
        self.assertTrue(result["researchAllowed"])
        self.assertEqual(set(result["missingFields"]), {"companyName", "requirement", "email"})
        manifest["webSearch"] = {"status": "no_result", "strongIdentityMatch": False, "evidence": []}
        manifest["tradewind"] = {"status": "no_result", "strongIdentityMatch": False, "evidence": []}
        result = INQUIRY_INTAKE_GATE.validate_intake(manifest)
        self.assertEqual(result["gateStatus"], "blocked_no_research_anchor")
        self.assertFalse(result["researchAllowed"])

    def test_complete_company_example_is_deterministic_valid_and_nonempty(self) -> None:
        path = ROOT / "skills/geto-run-market-research/references/company-json-example.json"
        committed = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(committed, COMPANY_EXAMPLE_GENERATOR.build_example())
        errors, warnings, infos = RESEARCH_BUNDLE.validate_company(committed)
        self.assertEqual((errors, warnings, infos), ([], [], []))

        def empty_paths(value: object, path: str = "$") -> list[str]:
            if value is None or value == "" or value == [] or value == {}:
                return [path]
            if isinstance(value, dict):
                return [
                    item
                    for key, child in value.items()
                    for item in empty_paths(child, f"{path}.{key}")
                ]
            if isinstance(value, list):
                return [
                    item
                    for index, child in enumerate(value)
                    for item in empty_paths(child, f"{path}[{index}]")
                ]
            return []

        self.assertEqual(empty_paths(committed), [])

    def test_freecity_and_electron_fixtures_validate(self) -> None:
        for name in ("freecity-company.json", "electron-company.json"):
            with self.subTest(name=name):
                value = json.loads((ROOT / "tests/fixtures" / name).read_text(encoding="utf-8"))
                errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
                self.assertEqual(errors, [])

    def test_evidence_uses_source_metadata_only(self) -> None:
        value = base_company()
        source = evidence()
        source["relation"] = "supports"
        value["websites"] = [{"url": "https://example.com", "evidence": [source]}]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("unsupported fields: relation" in item for item in errors))

    def test_required_structure_and_evidence_keys_are_enforced(self) -> None:
        value = base_company()
        value.pop("researchQueries")
        value["company"].pop("foundedOn")
        source = evidence()
        source.pop("note")
        source["verificationScope"] = []
        value["websites"] = [{"url": "https://example.com", "evidence": [source]}]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("missing top-level fields: researchQueries" in item for item in errors))
        self.assertTrue(any("$.company is missing fields: foundedOn" in item for item in errors))
        self.assertTrue(any("missing fields: note" in item for item in errors))
        self.assertTrue(any("verificationScope must be a non-empty string array" in item for item in errors))

    def test_financial_records_require_real_subject_and_scope_metadata(self) -> None:
        value = base_company()
        value["financialRecords"] = [{
            "recordType": "revenue", "period": "FY2025", "value": 100,
            "currency": "EUR", "unit": "currency_units", "valueStatus": "audited",
            "description": "Audited revenue.", "evidence": [evidence()],
        }]

        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)

        self.assertTrue(any("subjectEntity is required" in item for item in errors))
        self.assertTrue(any("scope or financialScope is required" in item for item in errors))
        self.assertTrue(any("accountingScope is required" in item for item in errors))
        self.assertTrue(any("relationshipToTarget is required" in item for item in errors))

    def test_capital_records_cannot_be_stored_as_financial_records(self) -> None:
        value = base_company()
        value["financialRecords"] = [{
            "recordType": "registered_capital", "subjectEntity": "Example",
            "scope": "standalone", "accountingScope": "individual",
            "relationshipToTarget": "target_entity", "period": "2025-12-31",
            "value": 100, "currency": "EUR", "unit": "currency_units",
            "valueStatus": "reported", "description": "Registered capital.",
            "evidence": [evidence()],
        }]

        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)

        self.assertTrue(any("belongs in capitalRecords" in item for item in errors))

    def test_project_participants_are_typed_and_evidence_backed(self) -> None:
        value = base_company()
        value["projects"] = [{
            "projectName": "Example Tower", "status": "active",
            "participants": [{
                "name": "Example Developer", "role": "developer", "identity": None,
                "status": "confirmed", "lastVerifiedOn": "2026-08-19",
                "evidence": [evidence()],
            }],
            "evidence": [evidence()],
        }]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertEqual(errors, [])
        value["projects"][0]["developer"] = "Example Developer"
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("unsupported participant fields: developer" in item for item in errors))

    def test_exclusivity_is_a_status_object(self) -> None:
        value = base_company()
        value["relationships"] = [{
            "relationshipType": "customer", "counterpartyName": "Customer A",
            "status": "possible", "limitations": ["Current continuity is unverified"],
            "exclusivity": {
                "status": "unknown", "scope": None, "description": None,
                "lastVerifiedOn": None, "evidence": [],
            },
            "evidence": [evidence()],
        }]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertEqual(errors, [])
        value["relationships"][0]["isExclusive"] = False
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("unsupported relationship fields: isExclusive" in item for item in errors))

    def test_every_relationship_requires_exclusivity(self) -> None:
        value = base_company()
        value["relationships"] = [{
            "relationshipType": "supplier", "counterpartyName": "Supplier A",
            "status": "possible", "limitations": [], "evidence": [evidence()],
        }]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("exclusivity is required" in item for item in errors))

    def test_listing_status_matches_market_contract(self) -> None:
        value = base_company()
        value["company"]["listingStatus"] = "self_listed"
        value["company"]["listingDetails"] = "Example Securities Exchange: EXM"
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertEqual(errors, [])
        value["company"]["listingStatus"] = "direct_listed"
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("listingStatus" in item for item in errors))

    def test_installer_only_cannot_be_confirmed_competitor(self) -> None:
        value = base_company()
        value["researchClassifications"] = [{
            "classification": "competitor", "status": "confirmed", "country": "Australia",
            "productScope": ["formwork"], "reason": "Name match", "evidence": [evidence()],
        }]
        value["productsAndServices"] = [{
            "name": "Installation", "markets": ["Australia"], "commercialRoles": ["installer"],
            "manufacturingStatus": "not_found", "getoRelevance": "high", "evidence": [evidence()],
        }]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("confirmed competitor requires" in item for item in errors))
        self.assertTrue(any("installer/service_contractor-only" in item for item in errors))

    def test_outsourced_brand_owner_can_be_confirmed_competitor(self) -> None:
        value = base_company()
        value["researchClassifications"] = [{
            "classification": "competitor", "status": "confirmed", "country": "Australia",
            "productScope": ["formwork"], "reason": "Own brand", "evidence": [evidence()],
        }]
        value["productsAndServices"] = [{
            "name": "Own system", "markets": ["Australia"], "commercialRoles": ["brand_owner"],
            "manufacturingStatus": "outsourced", "getoRelevance": "high", "evidence": [evidence()],
        }]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertEqual(errors, [])

    def test_channel_rental_can_be_confirmed_competitor(self) -> None:
        value = base_company()
        value["researchClassifications"] = [{
            "classification": "competitor", "status": "confirmed", "country": "Australia",
            "productScope": ["formwork"], "reason": "Competing rental fleet", "evidence": [evidence()],
        }]
        value["productsAndServices"] = [{
            "name": "Rental fleet", "markets": ["Australia"], "commercialRoles": ["rental_provider"],
            "manufacturingStatus": "not_found", "getoRelevance": "high", "evidence": [evidence()],
        }]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertEqual(errors, [])

    def test_relationship_entry_score_requires_matching_fact_anchor(self) -> None:
        value = base_company()
        relation = {
            "relationshipType": "customer", "counterpartyName": "Customer A",
            "counterpartyRole": "developer", "companyRole": "supplier",
            "projectName": "Project A", "country": "Australia", "status": "confirmed",
            "description": "Single-project product supply", "reviewDecision": "verified_customer",
            "cooperationDepthCode": "single_project", "relationshipStatusCode": "current",
            "entrySignalCode": None,
            "limitations": [],
            "exclusivity": {
                "status": "unknown", "scope": None, "description": None,
                "lastVerifiedOn": None, "evidence": [],
            },
            "entryAssessment": {
                "assessmentType": "relationship_entry", "status": "completed",
                "modelCode": "GETO_RELATIONSHIP_ENTRY", "modelVersion": "1.0",
                "score": 3, "rationale": "One current project with no framework evidence",
                "assessedOn": "2026-08-19", "evidenceStatus": "verified",
                "gapCodes": [], "evidence": [evidence()],
            },
            "evidence": [evidence()],
        }
        value["relationships"] = [relation]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertEqual(errors, [])
        relation["entryAssessment"]["score"] = 5
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("fact anchor" in item for item in errors))

    def test_competitor_customer_portfolio_uses_scored_customers_and_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "AU-Australia"
            competitor_dir = root / "companies" / "Competitor A"
            competitor_dir.mkdir(parents=True)
            competitor = RESEARCH_BUNDLE.empty_company("Competitor A", "Australia", "AU")
            competitor["researchClassifications"] = [{
                "classification": "competitor", "status": "confirmed", "country": "Australia",
                "productScope": ["formwork"], "reason": "Own competing system", "evidence": [evidence()],
            }]
            competitor["productsAndServices"] = [{
                "name": "Competing system", "markets": ["Australia"],
                "commercialRoles": ["system_owner"], "manufacturingStatus": "outsourced",
                "getoRelevance": "high", "evidence": [evidence()],
            }]
            competitor["relationships"] = [
                {
                    "relationshipType": "customer", "counterpartyName": name,
                    "counterpartyRole": "developer", "companyRole": "supplier",
                    "projectName": f"{name} Project", "country": "Australia", "status": "confirmed",
                    "description": "Official named project supply", "reviewDecision": "verified_customer",
                    "limitations": [],
                    "exclusivity": {
                        "status": "unknown", "scope": None, "description": None,
                        "lastVerifiedOn": None, "evidence": [],
                    },
                    "evidence": [evidence(f"https://example.com/{name[-1].lower()}")],
                }
                for name in ("Customer A", "Customer B")
            ]
            (competitor_dir / "company.json").write_text(json.dumps(competitor), encoding="utf-8")
            for name, score in (("Customer A", 80), ("Customer B", None)):
                customer = RESEARCH_BUNDLE.empty_company(name, "Australia", "AU")
                if score is not None:
                    customer["assessment"] = {
                        "status": "completed", "modelCode": "GETO_LEAD_VALUE",
                        "modelVersion": "2026-07-29", "overallScore": score,
                        "cohortBaselineVersion": "AU:developer:fixture", "assessedOn": "2026-08-19",
                    }
                customer_dir = root / "companies" / name
                customer_dir.mkdir(parents=True)
                (customer_dir / "company.json").write_text(json.dumps(customer), encoding="utf-8")

            portfolio = COMPETITOR_CUSTOMER_AGGREGATOR.aggregate(root, competitor_dir, "2026-08-19")
            updated = json.loads((competitor_dir / "company.json").read_text(encoding="utf-8"))
            errors, _, _ = RESEARCH_BUNDLE.validate_company(updated)
        self.assertEqual(errors, [])
        self.assertEqual(portfolio["status"], "partial_coverage")
        self.assertEqual(portfolio["verifiedCustomerCount"], 2)
        self.assertEqual(portfolio["scoredCustomerCount"], 1)
        self.assertEqual(portfolio["customerScoreCoverage"], 0.5)
        self.assertEqual(portfolio["averageCustomerValueScore"], 80.0)
        updated["competitorCustomerPortfolio"]["customers"] = updated["competitorCustomerPortfolio"]["customers"][:1]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(updated)
        self.assertTrue(any("must match deduplicated verified_customer" in item for item in errors))

    def test_competitor_customer_portfolio_blocks_missing_customer_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "AU-Australia"
            competitor_dir = root / "companies" / "Competitor A"
            competitor_dir.mkdir(parents=True)
            competitor = RESEARCH_BUNDLE.empty_company("Competitor A", "Australia", "AU")
            competitor["researchClassifications"] = [{
                "classification": "competitor", "status": "confirmed", "country": "Australia",
                "productScope": ["formwork"], "reason": "Own competing system", "evidence": [evidence()],
            }]
            competitor["relationships"] = [{
                "relationshipType": "customer", "counterpartyName": "Missing Customer",
                "country": "Australia", "reviewDecision": "verified_customer", "evidence": [evidence()],
            }]
            (competitor_dir / "company.json").write_text(json.dumps(competitor), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "exactly one company.json; found 0"):
                COMPETITOR_CUSTOMER_AGGREGATOR.aggregate(root, competitor_dir, "2026-08-25")

    def test_assessment_total_requires_complete_evidenced_dimensions(self) -> None:
        value = base_company()
        value["assessment"] = {
            "assessmentType": "lead_value", "status": "completed", "modelCode": "GETO_LEAD_VALUE",
            "modelVersion": "2026-07-29", "ratingScaleVersion": "value-status-2026-07-29",
            "capabilityContext": {}, "overallScore": 80, "grade": "verified_high_value",
            "informationCompleteness": 100, "overallConclusion": "Strong candidate",
            "assessedOn": "2026-08-19", "dimensions": [], "capCodes": [], "gapCodes": [],
        }
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("capabilityContext" in item for item in errors))
        self.assertTrue(any("exactly six dimensions" in item for item in errors))

    def test_assessment_and_report_files_reject_variant_fields(self) -> None:
        value = base_company()
        value["assessment"] = {"status": "not_requested", "assessmentStatus": "insufficient_evidence"}
        value["reportFiles"] = [{"type": "markdown_report", "path": "report.md"}]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("not_requested permits only" in item for item in errors))
        self.assertTrue(any("unsupported fields: type" in item for item in errors))

    def test_not_queried_is_info_not_warning(self) -> None:
        value = base_company()
        value["researchQueries"] = [{
            "topic": "provider", "channel": "TradeWind", "query": "Example",
            "scope": "company lookup", "status": "not_queried", "checkedOn": "2026-08-19",
            "resultCount": 0, "evidence": [],
        }]
        errors, warnings, infos = RESEARCH_BUNDLE.validate_company(value)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertTrue(any("not_queried" in item for item in infos))

    def test_forbidden_local_keys_and_secrets_are_errors(self) -> None:
        value = base_company()
        value["companyKey"] = "legacy"
        value["additionalInformation"] = [{
            "topic": "secret", "title": "credential", "details": "api_key=omx_test_abcdefghijk",
            "evidence": [evidence()],
        }]
        errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("forbidden" in item for item in errors))
        self.assertTrue(any("credential leak" in item for item in errors))

    def test_source_builder_deduplicates_tracking_and_fragment(self) -> None:
        value = base_company()
        value["websites"] = [
            {"url": "https://example.com", "evidence": [evidence("https://example.com/page?utm_source=a#one")]},
            {"url": "https://example.com", "evidence": [evidence("https://example.com/page#two")]},
        ]
        with tempfile.TemporaryDirectory() as directory:
            company_dir = Path(directory) / "companies" / "Example"
            company_dir.mkdir(parents=True)
            company_json = company_dir / "company.json"
            company_json.write_text(json.dumps(value), encoding="utf-8")
            output = SOURCE_BUILDER.build(company_json)
            text = output.read_text(encoding="utf-8")
        self.assertEqual(text.count("## 1."), 1)
        self.assertIn("Evidence occurrences: 2", text)
        self.assertNotIn("utm_source", text)

    def test_source_builder_groups_multiple_locators_for_one_url(self) -> None:
        value = base_company()
        first = evidence("https://example.com/report.pdf")
        first["locator"] = "p. 3"
        second = evidence("https://example.com/report.pdf")
        second["locator"] = "p. 19"
        value["websites"] = [{"url": "https://example.com", "evidence": [first, second]}]
        with tempfile.TemporaryDirectory() as directory:
            company_dir = Path(directory) / "companies" / "Example"
            company_dir.mkdir(parents=True)
            company_json = company_dir / "company.json"
            company_json.write_text(json.dumps(value), encoding="utf-8")
            text = SOURCE_BUILDER.build(company_json).read_text(encoding="utf-8")
        self.assertEqual(text.count("## 1."), 1)
        self.assertIn("Locators: p. 19; p. 3", text)

    def test_workspace_requires_report_and_sources(self) -> None:
        value = base_company()
        value["websites"] = [{"url": "https://example.com", "evidence": [evidence()]}]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "progress.md").write_text("# progress", encoding="utf-8")
            company_dir = root / "companies" / "Example"
            company_dir.mkdir(parents=True)
            (company_dir / "company.json").write_text(json.dumps(value), encoding="utf-8")
            errors, _, _ = WORKSPACE_VALIDATOR.validate(root)
        self.assertTrue(any("report.md" in item for item in errors))
        self.assertTrue(any("Sources/sources.md" in item for item in errors))

    def test_company_workspace_mode_ignores_siblings_and_country_progress(self) -> None:
        value = base_company()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "AU-Australia"
            company_dir = root / "companies" / "Example"
            company_dir.mkdir(parents=True)
            (company_dir / "company.json").write_text(json.dumps(value), encoding="utf-8")
            (company_dir / "report.md").write_text("# report", encoding="utf-8")
            sibling = root / "companies" / "Broken"
            sibling.mkdir()
            errors, _, _ = WORKSPACE_VALIDATOR.validate(root, company_dir)
        self.assertFalse(any("progress.md" in item or "Broken" in item for item in errors))

    def test_progress_merge_preserves_parallel_task_blocks(self) -> None:
        script = RUN_SCRIPTS / "merge_progress.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            progress = root / "progress.md"
            payloads = []
            for section in ("company_a", "company_b"):
                path = root / f"{section}.json"
                path.write_text(json.dumps({
                    "sectionName": section, "title": section, "status": "completed",
                    "did": ["diligence"], "artifacts": [f"{section}/company.json"],
                    "decision": ["lead confirmed"], "gaps": [], "next": ["review"],
                }), encoding="utf-8")
                payloads.append(path)
            processes = [subprocess.Popen(["python3", str(script), str(progress), str(path)]) for path in payloads]
            self.assertEqual([process.wait() for process in processes], [0, 0])
            text = progress.read_text(encoding="utf-8")
        self.assertIn("task:company_a:start", text)
        self.assertIn("task:company_b:start", text)

    def test_single_company_prepares_inputs_without_final_score(self) -> None:
        company = base_company()
        model = json.loads((ROOT / "skills/geto-diligence-company/references/lead-value-model.json").read_text())
        company["assessment"] = {"dimensions": [
            {"dimensionCode": item["dimensionCode"], "observedScore": item["maxScore"],
             "evidenceGrade": "A", "rationale": "Verified", "evidence": [evidence()],
             "gapCodes": [], "capCodes": []}
            for item in model["dimensions"]
        ], "capCodes": [], "gapCodes": [], "overallConclusion": "Verified lead"}
        capability = {
            "foundationKey": "geto:capability-foundation", "foundationVersion": "2026-08-11",
            "asOf": "2026-08-11", "status": "available", "contentHash": "sha256:" + "a" * 64,
            "productCodes": ["FORMWORK"], "scenarioCodes": [], "roleCodes": [],
            "caseKeys": [], "gapCodes": [],
        }
        assessment = ASSESSMENT_CALCULATOR.calculate(
            company, model, capability, "2026-08-19", "AU:main_contractor"
        )
        company["assessment"] = assessment
        errors, _, _ = RESEARCH_BUNDLE.validate_company(company)
        self.assertEqual(errors, [])
        self.assertEqual(assessment["status"], "pending_cohort_baseline")
        self.assertIsNone(assessment["overallScore"])
        self.assertIsNone(assessment["grade"])
        self.assertTrue(assessment["evidence"])
        self.assertTrue(all(item["baselineScore"] is None for item in assessment["dimensions"]))

    def test_workspace_requires_direct_matching_capability_artifact(self) -> None:
        company = base_company()
        model = json.loads((ROOT / "skills/geto-diligence-company/references/lead-value-model.json").read_text())
        company["assessment"] = {"dimensions": [
            {"dimensionCode": item["dimensionCode"], "observedScore": item["maxScore"],
             "evidenceGrade": "A", "rationale": "Verified", "evidence": [evidence()],
             "gapCodes": [], "capCodes": []}
            for item in model["dimensions"]
        ], "capCodes": [], "gapCodes": [], "overallConclusion": "Verified lead"}
        capability = {
            "foundationKey": "geto:capability-foundation", "foundationVersion": "2026-08-11",
            "asOf": "2026-08-11", "status": "available", "contentHash": "sha256:" + "a" * 64,
            "productCodes": ["aluminum_formwork"], "scenarioCodes": [], "roleCodes": [],
            "caseKeys": [], "gapCodes": [],
        }
        company["assessment"] = ASSESSMENT_CALCULATOR.calculate(
            company, model, capability, "2026-08-19", "AU:main_contractor"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "AU-Australia"
            company_dir = root / "companies" / "Example"
            context_dir = company_dir / "RisksAndAssessment"
            context_dir.mkdir(parents=True)
            (company_dir / "company.json").write_text(json.dumps(company), encoding="utf-8")
            (company_dir / "report.md").write_text("# report", encoding="utf-8")
            SOURCE_BUILDER.build(company_dir / "company.json")
            context_file = context_dir / "capability-context.json"
            context_file.write_text(json.dumps({"contextRef": capability}), encoding="utf-8")
            errors, _, _ = WORKSPACE_VALIDATOR.validate(root, company_dir)
            self.assertTrue(any("direct contextRef fields" in item for item in errors))
            context_file.write_text(json.dumps(capability), encoding="utf-8")
            errors, _, _ = WORKSPACE_VALIDATOR.validate(root, company_dir)
        self.assertEqual(errors, [])

    def test_main_task_uses_zero_baseline_until_five_peer_observations_exist(self) -> None:
        model = json.loads((ROOT / "skills/geto-diligence-company/references/lead-value-model.json").read_text())
        capability = {
            "foundationKey": "geto:capability-foundation", "foundationVersion": "2026-08-11",
            "asOf": "2026-08-11", "status": "available", "contentHash": "sha256:" + "a" * 64,
            "productCodes": ["aluminum_formwork"], "scenarioCodes": [], "roleCodes": [],
            "caseKeys": [], "gapCodes": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "AU-Australia"
            early_companies = []
            early_artifact = {}
            for index in range(6):
                company = RESEARCH_BUNDLE.empty_company(f"Company {index}", "Australia", "AU")
                if index == 0:
                    company["missingInformation"] = [{
                        "topic": "lead_assessment_contract_incomplete",
                        "status": "not_queried",
                        "description": "lead assessment contract incomplete",
                        "impact": "Strong identity gate future upload",
                        "checkedScope": "Legacy company and legal-entity records",
                        "recommendedAction": "Complete identity arbitration before upload",
                        "evidence": [],
                    }, {
                        "topic": "payment_capacity_evidence",
                        "status": "not_queried",
                        "description": "Payment evidence remains open.",
                        "impact": "Commercial terms need confirmation.",
                        "checkedScope": "Published financial and payment sources.",
                        "recommendedAction": "Request payment references.",
                        "evidence": [],
                    }]
                company["assessment"] = {"dimensions": [
                    {
                        "dimensionCode": item["dimensionCode"],
                        "observedScore": (
                            None if index == 5 and item["dimensionCode"] in {"account_scale", "payment_capacity"}
                            else item["maxScore"]
                        ),
                        "evidenceGrade": (
                            "U" if index == 5 and item["dimensionCode"] in {"account_scale", "payment_capacity"}
                            else "A"
                        ),
                        "rationale": "Verified", "evidence": [evidence()],
                        "gapCodes": [], "capCodes": [],
                    }
                    for item in model["dimensions"]
                ], "capCodes": [], "gapCodes": [], "overallConclusion": "Prepared"}
                company["assessment"] = ASSESSMENT_CALCULATOR.calculate(
                    company, model, capability, "2026-08-19", "AU:main_contractor"
                )
                company_dir = root / "companies" / f"Company {index}"
                company_dir.mkdir(parents=True)
                (company_dir / "company.json").write_text(json.dumps(company), encoding="utf-8")
                if index == 3:
                    pending_result = COHORT_CALCULATOR.score_country(root, model, "2026-08-19")
                    early_companies = [
                        json.loads(path.read_text(encoding="utf-8"))
                        for path in sorted((root / "companies").glob("*/company.json"))
                    ]
                    early_artifact = json.loads(
                        Path(pending_result["baselineArtifact"]).read_text(encoding="utf-8")
                    )
            result = COHORT_CALCULATOR.score_country(root, model, "2026-08-19")
            scored = [
                json.loads(path.read_text(encoding="utf-8"))
                for path in sorted((root / "companies").glob("*/company.json"))
            ]
            versions = {item["assessment"]["cohortBaselineVersion"] for item in scored}
            sixth = next(item for item in scored if item["company"]["companyName"] == "Company 5")
            first = next(item for item in scored if item["company"]["companyName"] == "Company 0")
        self.assertEqual(len(pending_result["pendingCompanyFiles"]), 0)
        self.assertEqual(len(pending_result["updatedCompanyFiles"]), 4)
        self.assertTrue(all(item["assessment"]["status"] == "completed" for item in early_companies))
        self.assertTrue(all(
            item["status"] == "zero_fallback_no_median"
            for cohort in early_artifact["cohorts"]
            for item in cohort["dimensions"]
        ))
        self.assertEqual(len(result["updatedCompanyFiles"]), 6)
        self.assertEqual(len(versions), 1)
        self.assertTrue(all(item["assessment"]["status"] == "completed" for item in scored))
        self.assertEqual(
            [item["topic"] for item in first["missingInformation"]],
            ["payment_capacity_evidence"],
        )
        self.assertTrue(any("Company 0" in item for item in pending_result["removedAssessmentPlaceholders"]))
        for item in scored:
            errors, _, _ = RESEARCH_BUNDLE.validate_company(item)
            self.assertEqual(errors, [])
        account = next(
            item for item in sixth["assessment"]["dimensions"]
            if item["dimensionCode"] == "account_scale"
        )
        self.assertEqual(account["baselineScore"], 10)
        self.assertEqual(account["finalDimensionScore"], 10)

    def test_zero_baseline_preserves_provider_failed_unknown_as_pending(self) -> None:
        model = json.loads((ROOT / "skills/geto-diligence-company/references/lead-value-model.json").read_text())
        capability = {
            "foundationKey": "geto:capability-foundation", "foundationVersion": "2026-08-11",
            "asOf": "2026-08-11", "status": "available", "contentHash": "sha256:" + "a" * 64,
            "productCodes": ["aluminum_formwork"], "scenarioCodes": [], "roleCodes": [],
            "caseKeys": [], "gapCodes": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "AU-Australia"
            company = RESEARCH_BUNDLE.empty_company("Provider Pending", "Australia", "AU")
            company["missingInformation"] = [{
                "topic": "lead_assessment_contract_incomplete",
                "status": "not_queried",
                "description": "lead assessment contract incomplete",
                "impact": "Strong identity gate future upload",
                "checkedScope": "Legacy company and legal-entity records",
                "recommendedAction": "Complete identity arbitration before upload",
                "evidence": [],
            }]
            company["assessment"] = {"dimensions": [
                {
                    "dimensionCode": item["dimensionCode"], "observedScore": None,
                    "evidenceGrade": "U", "rationale": "Provider query unavailable",
                    "evidence": [], "gapCodes": ["provider_failed"], "capCodes": [],
                }
                for item in model["dimensions"]
            ], "capCodes": [], "gapCodes": [], "overallConclusion": "Prepared"}
            company["assessment"] = ASSESSMENT_CALCULATOR.calculate(
                company, model, capability, "2026-08-24", "AU:main_contractor"
            )
            company_dir = root / "companies" / "Provider Pending"
            company_dir.mkdir(parents=True)
            company_file = company_dir / "company.json"
            company_file.write_text(json.dumps(company), encoding="utf-8")
            result = COHORT_CALCULATOR.score_country(root, model, "2026-08-24")
            updated = json.loads(company_file.read_text(encoding="utf-8"))
        self.assertEqual(result["updatedCompanyFiles"], [])
        self.assertEqual(result["pendingCompanyFiles"], [str(company_file)])
        self.assertEqual(updated["assessment"]["status"], "pending_cohort_baseline")
        self.assertIsNone(updated["assessment"]["overallScore"])
        self.assertTrue(any(
            code.startswith("cohort_zero_baseline_blocked:")
            for code in updated["assessment"]["gapCodes"]
        ))
        gap = updated["missingInformation"][0]
        self.assertEqual(gap["status"], "pending_cohort_baseline")
        self.assertIn("GETO_LEAD_VALUE assessment", gap["description"])
        self.assertNotIn("identity", json.dumps(gap).lower())

    def test_inquiry_readiness_scores_without_cohort(self) -> None:
        company = base_company()
        model = json.loads((ROOT / "skills/geto-diligence-inquiry/references/inquiry-readiness-model.json").read_text())
        company["inquiryAssessment"] = {"dimensions": [
            {
                "dimensionCode": item["dimensionCode"], "score": item["maxScore"],
                "rationale": "Verified inquiry input", "evidence": [evidence()], "gapCodes": [],
            }
            for item in model["dimensions"]
        ], "hardBlockCodes": [], "gapCodes": [], "overallConclusion": "Ready"}
        company["inquiryAssessment"] = INQUIRY_CALCULATOR.calculate(
            company, model, "inquiry:fixture-1", "2026-08-19"
        )
        errors, _, _ = RESEARCH_BUNDLE.validate_company(company)
        self.assertEqual(errors, [])
        self.assertEqual(company["assessment"], {"status": "not_requested"})
        self.assertEqual(company["inquiryAssessment"]["overallScore"], 100)
        self.assertEqual(company["inquiryAssessment"]["grade"], "ready_for_quotation")

    def test_inquiry_report_requires_business_answers_not_fixed_section_count(self) -> None:
        company = base_company()
        company["assessment"] = {
            "status": "pending_cohort_baseline",
            "dimensions": [{"dimensionCode": f"value_{index}"} for index in range(6)],
        }
        company["inquiryAssessment"] = {"status": "completed"}
        shallow = "# Report\n\n## 结论\n\n资料较少。\n"
        errors = RESEARCH_BUNDLE.validate_inquiry_report(shallow, company)
        self.assertTrue(any("too short" in item for item in errors))
        self.assertTrue(any("core question" in item for item in errors))

        detailed = """# Example 公司询盘背调报告

## 结论与建议

总体判断：公司经营身份可以核实，本次询盘值得继续，但当前只适合发送产品资料和预算计算方法。正式报价、签约和授信前，必须确认项目、图纸、采购方、合同签约主体和付款方。当前建议是继续培育并补充核实，不承诺最终价格和交期。

## 询盘、公司与联系人

客户提出铝模板需求，但没有提供数量、结构图纸和目标交付时间。公司公开登记和官网支持其真实经营，历史至当前的业务资料表明其从事建筑施工。联系人已有公司邮箱和电话，可以继续联系；公开资料尚不能确认其采购、签约和付款权限，因此需要补充职位和公司授权。

## 项目、产品与交易判断

在已检查的官网、政府许可和交易对手资料中，未发现可直接绑定本次询盘的公开项目。客户需求与铝模板应用场景可能匹配，但缺少墙柱板尺寸、层高、接触面积、重复率和施工节拍，当前无法完成正式选型。采购窗口、实际使用方和付款条件也尚未确认。

## 客户价值、风险与下一步

客户价值方面，公司存在真实经营和潜在项目需求，值得保持联系；同类样本不足，暂不出具最终等级。主要风险是项目和决策链没有闭合。下一步应向客户索取项目名称、建筑和结构图、工程量、交付城市、采购时间、合同公司、付款公司及联系人职位；可以发送标准目录和案例，暂时不提供账期、锁价或交期承诺。
"""
        self.assertEqual(RESEARCH_BUNDLE.validate_inquiry_report(detailed, company), [])

        company["projects"] = [{"projectName": "Aluminum Pergola Structural Design"}]
        translated_project_report = detailed.replace("结论与建议", "结论先行").replace(
            "在已检查的官网、政府许可和交易对手资料中，未发现可直接绑定本次询盘的公开项目。",
            "公开项目线索包括铝制凉棚结构设计，但与本次询盘没有直接采购关系。",
        )
        self.assertEqual(
            RESEARCH_BUNDLE.validate_inquiry_report(translated_project_report, company), []
        )

        company["inquiryAssessment"]["overallScore"] = 39
        score_errors = RESEARCH_BUNDLE.validate_inquiry_report(translated_project_report, company)
        self.assertTrue(any("score differs" in item for item in score_errors))
        score_aligned_report = translated_project_report.replace(
            "总体判断：", "询盘准备度为39/100。总体判断：", 1
        )
        self.assertEqual(
            RESEARCH_BUNDLE.validate_inquiry_report(score_aligned_report, company), []
        )

    def test_inquiry_report_rejects_internal_machine_terms(self) -> None:
        company = base_company()
        company["assessment"] = {
            "status": "pending_cohort_baseline",
            "dimensions": [{"dimensionCode": f"value_{index}"} for index in range(6)],
        }
        company["inquiryAssessment"] = {"status": "completed"}
        report = ("公司、联系人、询盘、项目、产品、报价、付款、客户价值和下一步均已说明。" * 30)
        report += " pending_cohort_baseline Provider queryBoundary hard block"
        errors = RESEARCH_BUNDLE.validate_inquiry_report(report, company)
        for label in ("pending_cohort_baseline", "Provider", "queryBoundary", "hard block"):
            with self.subTest(label=label):
                self.assertTrue(any(label in item for item in errors))

        url_only = ("公司、联系人、询盘、项目、产品、报价、付款、客户价值和下一步均已说明。" * 30)
        url_only += " 来源：https://example.com/provider/no_result"
        url_errors = RESEARCH_BUNDLE.validate_inquiry_report(url_only, company)
        self.assertFalse(any("raw query state" in item for item in url_errors))

    def test_inquiry_report_requires_chinese_to_be_the_dominant_readable_language(self) -> None:
        company = base_company()
        company["assessment"] = {
            "status": "pending_cohort_baseline",
            "dimensions": [{"dimensionCode": f"value_{index}"} for index in range(6)],
        }
        company["inquiryAssessment"] = {"status": "completed"}
        report = (
            "总体判断 公司 联系人 询盘 项目 产品 报价 付款 客户价值 下一步。\n"
            + "This company inquiry report repeats untranslated business analysis, project details, "
              "product fit, transaction conditions, contact findings, and recommended actions. " * 20
        )
        errors = RESEARCH_BUNDLE.validate_inquiry_report(report, company)
        self.assertTrue(any("Chinese business prose" in item for item in errors))

    def test_publication_gate_requires_review_hash_for_docx_or_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            company_dir = Path(directory)
            report = company_dir / "report.md"
            report.write_text("# 已确认内容\n", encoding="utf-8")
            company = base_company()
            company["inquiryAssessment"] = {"status": "completed"}
            self.assertEqual(PUBLICATION_GATE.validate_publication(company_dir, company), [])

            (company_dir / "report.pdf").write_bytes(b"pdf")
            company["reportFiles"] = [{
                "fileName": "report.pdf", "path": "report.pdf", "format": "pdf",
                "reportType": "diligence", "language": "zh-CN",
                "generatedOn": "2026-08-28", "description": "正式报告",
            }]
            errors = PUBLICATION_GATE.validate_publication(company_dir, company)
            self.assertTrue(any("report-review.json is required" in item for item in errors))

            additional = company_dir / "Additional"
            additional.mkdir()
            review = {
                "status": "approved", "reportPath": "report.md",
                "reportSha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                "reviewedOn": "2026-08-28", "reviewedBy": "user",
                "instructionRef": "User approved the Markdown report for publication.",
            }
            (additional / "report-review.json").write_text(
                json.dumps(review, ensure_ascii=False), encoding="utf-8"
            )
            self.assertEqual(PUBLICATION_GATE.validate_publication(company_dir, company), [])
            report.write_text("# 已修改内容\n", encoding="utf-8")
            errors = PUBLICATION_GATE.validate_publication(company_dir, company)
            self.assertTrue(any("changed after user review" in item for item in errors))

    def test_info_summary_hides_details_by_default(self) -> None:
        result = RESEARCH_BUNDLE.format_result([], [], [
            "$.researchQueries[0]: not_queried",
            "$.researchQueries[1]: checked with no result",
        ])
        self.assertEqual(result["infos"], [])
        self.assertEqual(result["infoSummary"], {"notQueried": 1, "noResult": 1, "other": 0})
        self.assertEqual(result["infoDetailsOmitted"], 2)


class SearchLexiconTests(unittest.TestCase):
    def test_inquiry_skill_bundles_the_complete_company_resource_contract(self) -> None:
        company_contract = (
            ROOT / "skills/geto-diligence-company/references/child-resources.md"
        ).read_text(encoding="utf-8")
        inquiry_contract = (
            ROOT / "skills/geto-diligence-inquiry/references/child-resources.md"
        ).read_text(encoding="utf-8")
        competitor_contract = (
            ROOT / "skills/geto-diligence-competitor/references/child-resources.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(inquiry_contract, company_contract)
        self.assertEqual(competitor_contract, company_contract)
        for resource in (
            "contacts[]", "inquiries[]", "projects[]", "relationships[]",
            "financialRecords[]", "customsTransactions[]", "lawsuitsAndCompliance[]",
            "researchQueries[]", "reportFiles[]",
        ):
            self.assertIn(resource, inquiry_contract)
        self.assertIn("competitorCustomerPortfolio", company_contract)

    def test_company_json_reference_example_validates(self) -> None:
        example = json.loads((
            ROOT / "skills/geto-run-market-research/references/company-json-example.json"
        ).read_text(encoding="utf-8"))
        errors, warnings, _ = RESEARCH_BUNDLE.validate_company(example)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_inquiry_reference_example_merges_into_company_contract(self) -> None:
        example = json.loads((
            ROOT / "skills/geto-run-market-research/references/company-json-example.json"
        ).read_text(encoding="utf-8"))
        text = (ROOT / "skills/geto-diligence-inquiry/references/inquiry-example.md").read_text(encoding="utf-8")
        fragment = json.loads(text.split("```json\n", 1)[1].split("\n```", 1)[0])
        example.update(fragment)
        errors, warnings, _ = RESEARCH_BUNDLE.validate_company(example)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_competitor_skills_separate_company_facts_from_customer_portfolio(self) -> None:
        diligence = (ROOT / "skills/geto-diligence-competitor/SKILL.md").read_text(encoding="utf-8")
        mining = (ROOT / "skills/geto-mine-competitor-customers/SKILL.md").read_text(encoding="utf-8")
        model = json.loads((
            ROOT / "skills/geto-mine-competitor-customers/references/relationship-entry-model.json"
        ).read_text(encoding="utf-8"))
        competitor_contract = (
            ROOT / "skills/geto-diligence-competitor/references/competitor-contract.md"
        ).read_text(encoding="utf-8")
        self.assertIn("公司级结果由竞对分类", competitor_contract)
        self.assertNotIn("威胁分", competitor_contract)
        self.assertIn("competitorCustomerPortfolio", mining)
        self.assertIn("$geto-diligence-competitor", mining)
        self.assertNotIn("competitor_intensity", diligence)
        self.assertEqual([item["score"] for item in model["levels"]], [5, 4, 3, 2, 1, 0])

    def test_lexicon_and_required_regressions_validate(self) -> None:
        path = ROOT / "skills/geto-capability-foundation/references/search-lexicon.json"
        errors = LEXICON_VALIDATOR.validate(json.loads(path.read_text(encoding="utf-8")))
        self.assertEqual(errors, [])

    def test_explicit_capability_codes_do_not_expand_to_related_products(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "RisksAndAssessment" / "capability-context.json"
            completed = subprocess.run(
                ["python3", str(CAPABILITY_SCRIPTS / "select_context.py"),
                 "--country", "MX", "--product-code", "aluminum_formwork",
                 "--output", str(output)],
                check=True, capture_output=True, text=True,
            )
            result = json.loads(completed.stdout)
            artifact = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(result["contextRef"]["productCodes"], ["aluminum_formwork"])
        self.assertEqual(result["contextRef"]["scenarioCodes"], [])
        self.assertEqual(result["contextRef"]["status"], "available")
        self.assertEqual(artifact, result["contextRef"])
        self.assertNotIn("contextRef", artifact)

        with_query = subprocess.run(
            ["python3", str(CAPABILITY_SCRIPTS / "select_context.py"),
             "--country", "SA", "--product-code", "aluminum_formwork",
             "--query", "column formwork contractor Jeddah"],
            check=True, capture_output=True, text=True,
        )
        self.assertEqual(json.loads(with_query.stdout)["contextRef"]["scenarioCodes"], [])

    def test_runtime_docs_read_as_a_current_contract(self) -> None:
        forbidden = (
            "ResearchDelta", "ResearchRun", "ClaimSourceLink", "EvidencePackage",
            "runId", "claimKey", "sourceKey", "OmniX Draft",
            "Draft/Approval", "blocked_market_unavailable", "旧接口",
            "此前版本", "本轮修复", "因为土耳其", "旧规则", "迁移说明",
        )
        documents = [ROOT / "README.md"]
        documents.extend((ROOT / "skills").glob("geto-*/SKILL.md"))
        documents.extend((ROOT / "skills").glob("geto-*/references/*.md"))
        for document in documents:
            if document.name.endswith(" 2.md"):
                continue
            text = document.read_text(encoding="utf-8")
            for phrase in forbidden:
                with self.subTest(document=document.name, phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_shared_classification_contract_separates_leads_from_cooperation_ideas(self) -> None:
        contract = (
            ROOT / "skills/geto-run-market-research/references/classification-and-engagement-contract.md"
        ).read_text(encoding="utf-8")
        self.assertIn("采购、租赁或付款路径", contract)
        self.assertIn("泛化的产能互补、联合投标、战略合作或第二来源设想属于合作机会", contract)
        self.assertIn("lead 列表排除 `lead=rejected`", contract)
        self.assertIn("客户价值评分和关系切入分是可选的后续分析", contract)

    def test_competitor_portfolio_is_optional_for_company_classification(self) -> None:
        company = base_company()
        company["researchClassifications"] = [
            {
                "classification": "competitor", "status": "confirmed", "country": "Australia",
                "productScope": ["steel_formwork"], "reason": "Own system and sales control",
                "evidence": [evidence()],
            },
            {
                "classification": "lead", "status": "rejected", "country": "Australia",
                "productScope": ["steel_formwork"], "reason": "No buying or channel path",
                "evidence": [evidence("https://example.com/terms")],
            },
        ]
        company["productsAndServices"] = [{
            "name": "Steel Formwork", "systemName": "Frame", "type": "product",
            "category": "steel_formwork", "description": "Owned system", "technologyTerms": [],
            "applications": [], "targetCustomers": [], "markets": ["Australia"],
            "commercialRoles": ["system_owner"], "manufacturingStatus": "manufacturing_claimed",
            "manufacturingDescription": "Company-controlled production", "factoryLocations": [],
            "media": [], "representativeProject": None, "status": "active", "getoRelevance": "high",
            "evidence": [evidence()],
        }]
        self.assertEqual(company["competitorCustomerPortfolio"], {"status": "not_requested"})
        errors, _, _ = RESEARCH_BUNDLE.validate_company(company)
        self.assertEqual(errors, [])


class ResearchFirstSkillContractTests(unittest.TestCase):
    CORE_SKILLS = (
        "geto-run-market-research",
        "geto-diligence-company",
        "geto-diligence-competitor",
        "geto-diligence-inquiry",
        "geto-find-leads",
        "geto-mine-competitor-customers",
        "geto-map-relationships",
    )

    def test_shared_contract_makes_local_research_and_ai_conclusions_first_class(self) -> None:
        contract = (
            ROOT / "skills/geto-run-market-research/references/research-intelligence-contract.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "本地 ResearchBundle 是研究的第一交付和事实主合同",
            "广度覆盖",
            "重点路径深挖",
            "关联扩展",
            "开放信号",
            "AI 推理",
            "AI 结论",
            "不得用“留待人工判断”代替",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, contract)
        self.assertIn("OmniX 只是用户明确要求后的可选投影", contract)

    def test_core_research_skills_use_the_shared_contract_without_goal_dependency(self) -> None:
        for skill_name in self.CORE_SKILLS:
            skill = (ROOT / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill_name):
                self.assertIn("research-intelligence-contract.md", skill)
                self.assertNotIn("/goal", skill)

    def test_inquiry_skill_uses_dual_axis_markdown_first_and_optional_publication(self) -> None:
        skill_dir = ROOT / "skills/geto-diligence-inquiry"
        skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        report_contract = (skill_dir / "references/report-contract.md").read_text(encoding="utf-8")
        project_contract = (skill_dir / "references/project-research-contract.md").read_text(encoding="utf-8")
        publication = (skill_dir / "references/publication-contract.md").read_text(encoding="utf-8")
        inquiry_research = (
            skill_dir / "references/inquiry-research-intelligence-contract.md"
        ).read_text(encoding="utf-8")

        for phrase in (
            "完整公司轴", "Markdown 第一交付", "默认停止，不自动生成 DOCX/PDF",
            "公司从历史至今", "不固定章节数量",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)
        self.assertIn("公司轴", inquiry_research)
        self.assertIn("询盘轴", inquiry_research)
        self.assertIn("历史至当前", inquiry_research)
        self.assertIn("固定核心问题，不固定模板", report_contract)
        self.assertNotIn("## 必需章节", report_contract)
        self.assertNotIn("至少 3 个", project_contract)
        self.assertIn("用户明确确认 Markdown", publication)
        self.assertIn("PDF 是可选发布物", publication)

    def test_formal_inquiry_report_contract_requires_plain_business_chinese(self) -> None:
        contract = (
            ROOT / "skills/geto-diligence-inquiry/references/report-contract.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "极致汉化", "务实易读", "对本次业务意味着什么",
            "不固定章节数量", "机器状态", "下一步必须具体",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, contract)

    def test_workspace_progress_tracks_frontier_synthesis_and_local_completion(self) -> None:
        progress = WORKSPACE_INITIALIZER.progress_template("Spain", "ES")
        for checkpoint in (
            "research_frontier", "review", "synthesis", "validation", "local_complete",
        ):
            with self.subTest(checkpoint=checkpoint):
                self.assertIn(f"| {checkpoint} |", progress)
        self.assertIn("## 研究前沿", progress)
        self.assertIn("## AI 市场综合", progress)
        self.assertIn("仅在用户明确要求时启用", progress)
        self.assertNotIn("| optional_upload | pending", progress)

    def test_historical_rework_rules_are_targeted_not_mechanical(self) -> None:
        review_contract = (
            ROOT / "skills/geto-run-market-research/references/diligence-review-contract.md"
        ).read_text(encoding="utf-8")
        company_skill = (
            ROOT / "skills/geto-diligence-company/SKILL.md"
        ).read_text(encoding="utf-8")
        field_contract = (
            ROOT / "skills/geto-run-market-research/references/company-field-requirements.md"
        ).read_text(encoding="utf-8")
        self.assertIn("先建立最近活动、公开数量和分页边界", review_contract)
        self.assertIn("数量过大或平台受限时是否说明选择方法", review_contract)
        self.assertIn("Provider 没有具名人员不等于公司没有可用联系方式", company_skill)
        self.assertIn("公司通用邮箱、电话、表单、办公室、项目咨询、供应商/投标和投资者关系入口与具名人员分别建模", field_contract)
        self.assertNotIn("默认最近 24 个月公开可见范围内，帖子是否逐页检查", review_contract)


if __name__ == "__main__":
    unittest.main()
