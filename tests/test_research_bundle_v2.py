from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPTS = ROOT / "skills/geto-run-market-research/scripts"
CAPABILITY_SCRIPTS = ROOT / "skills/geto-capability-foundation/scripts"


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


def evidence(url: str = "https://example.com/product") -> dict[str, object]:
    return {
        "sourceTitle": "Official product page", "sourceUrl": url,
        "publisher": "Example", "sourceType": "official_website",
        "publishedOn": None, "retrievedOn": "2026-08-19", "relation": "supports",
        "locator": "Products", "excerpt": "Product system", "note": "Fixture",
    }


def base_company() -> dict[str, object]:
    return RESEARCH_BUNDLE.empty_company("Example", "Australia")


class ResearchBundleValidationTests(unittest.TestCase):
    def test_freecity_and_electron_fixtures_validate(self) -> None:
        for name in ("freecity-company.json", "electron-company.json"):
            with self.subTest(name=name):
                value = json.loads((ROOT / "tests/fixtures" / name).read_text(encoding="utf-8"))
                errors, _ = RESEARCH_BUNDLE.validate_company(value)
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
        errors, _ = RESEARCH_BUNDLE.validate_company(value)
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
        errors, _ = RESEARCH_BUNDLE.validate_company(value)
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
        errors, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertEqual(errors, [])

    def test_assessment_total_requires_complete_evidenced_dimensions(self) -> None:
        value = base_company()
        value["assessment"] = {
            "assessmentType": "lead_value", "overallScore": 80, "grade": "A",
            "overallConclusion": "Strong candidate", "assessedOn": "2026-08-19",
            "dimensions": [{"name": "project opportunity", "score": None, "rationale": "Pending", "evidence": []}],
        }
        errors, _ = RESEARCH_BUNDLE.validate_company(value)
        self.assertTrue(any("dimensions[0].evidence" in item for item in errors))
        self.assertTrue(any("overallScore/grade" in item for item in errors))

    def test_forbidden_local_keys_and_secrets_are_errors(self) -> None:
        value = base_company()
        value["companyKey"] = "legacy"
        value["additionalInformation"] = [{
            "topic": "secret", "title": "credential", "details": "api_key=omx_test_abcdefghijk",
            "evidence": [evidence()],
        }]
        errors, _ = RESEARCH_BUNDLE.validate_company(value)
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

    def test_workspace_requires_report_and_sources(self) -> None:
        value = base_company()
        value["websites"] = [{"url": "https://example.com", "evidence": [evidence()]}]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "progress.md").write_text("# progress", encoding="utf-8")
            company_dir = root / "companies" / "Example"
            company_dir.mkdir(parents=True)
            (company_dir / "company.json").write_text(json.dumps(value), encoding="utf-8")
            errors, _ = WORKSPACE_VALIDATOR.validate(root)
        self.assertTrue(any("report.md" in item for item in errors))
        self.assertTrue(any("Sources/sources.md" in item for item in errors))


class SearchLexiconTests(unittest.TestCase):
    def test_lexicon_and_required_regressions_validate(self) -> None:
        path = ROOT / "skills/geto-capability-foundation/references/search-lexicon.json"
        errors = LEXICON_VALIDATOR.validate(json.loads(path.read_text(encoding="utf-8")))
        self.assertEqual(errors, [])

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
