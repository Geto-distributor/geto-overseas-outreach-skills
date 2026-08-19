from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPTS = ROOT / "skills/geto-run-market-research/scripts"
CAPABILITY_SCRIPTS = ROOT / "skills/geto-capability-foundation/scripts"
DILIGENCE_SCRIPTS = ROOT / "skills/geto-diligence-company/scripts"


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


def evidence(url: str = "https://example.com/product") -> dict[str, object]:
    return {
        "sourceTitle": "Official product page", "sourceUrl": url,
        "publisher": "Example", "sourceType": "official_website",
        "publishedOn": None, "retrievedOn": "2026-08-19", "relation": "supports",
        "locator": "Products", "excerpt": "Product system", "note": "Fixture",
    }


def base_company() -> dict[str, object]:
    return RESEARCH_BUNDLE.empty_company("Example", "Australia", "AU")


class ResearchBundleValidationTests(unittest.TestCase):
    def test_freecity_and_electron_fixtures_validate(self) -> None:
        for name in ("freecity-company.json", "electron-company.json"):
            with self.subTest(name=name):
                value = json.loads((ROOT / "tests/fixtures" / name).read_text(encoding="utf-8"))
                errors, _, _ = RESEARCH_BUNDLE.validate_company(value)
                self.assertEqual(errors, [])

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

    def test_approved_model_calculates_six_dimensions(self) -> None:
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
            "asOf": "2026-08-11", "status": "available", "contentHash": "sha256:test",
            "productCodes": ["FORMWORK"], "scenarioCodes": [], "roleCodes": [],
            "caseKeys": [], "gapCodes": [],
        }
        assessment = ASSESSMENT_CALCULATOR.calculate(company, model, capability, "2026-08-19")
        company["assessment"] = assessment
        errors, _, _ = RESEARCH_BUNDLE.validate_company(company)
        self.assertEqual(errors, [])
        self.assertEqual(assessment["overallScore"], 100)
        self.assertEqual(assessment["grade"], "verified_high_value")

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
            "asOf": "2026-08-11", "status": "available", "contentHash": "sha256:test",
            "productCodes": ["aluminum_formwork"], "scenarioCodes": [], "roleCodes": [],
            "caseKeys": [], "gapCodes": [],
        }
        company["assessment"] = ASSESSMENT_CALCULATOR.calculate(company, model, capability, "2026-08-19")
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

    def test_info_summary_hides_details_by_default(self) -> None:
        result = RESEARCH_BUNDLE.format_result([], [], [
            "$.researchQueries[0]: not_queried",
            "$.researchQueries[1]: checked with no result",
        ])
        self.assertEqual(result["infos"], [])
        self.assertEqual(result["infoSummary"], {"notQueried": 1, "noResult": 1, "other": 0})
        self.assertEqual(result["infoDetailsOmitted"], 2)


class SearchLexiconTests(unittest.TestCase):
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
            "runId", "taskId", "claimKey", "sourceKey", "OmniX Draft",
            "Draft/Approval", "blocked_market_unavailable", "旧接口", "fallback",
            "不再", "取代", "迁移",
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


if __name__ == "__main__":
    unittest.main()
