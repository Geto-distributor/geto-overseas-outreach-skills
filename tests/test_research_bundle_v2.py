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
COMPETITOR_CUSTOMER_AGGREGATOR = load_module(
    "aggregate_competitor_customers",
    COMPETITOR_CUSTOMER_SCRIPTS / "aggregate_competitor_customers.py",
)


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

    def test_relationship_entry_score_requires_matching_fact_anchor(self) -> None:
        value = base_company()
        relation = {
            "relationshipType": "customer", "counterpartyName": "Customer A",
            "counterpartyRole": "developer", "companyRole": "supplier",
            "projectName": "Project A", "country": "Australia", "status": "confirmed",
            "description": "Single-project product supply", "reviewDecision": "verified_customer",
            "cooperationDepthCode": "single_project", "relationshipStatusCode": "current",
            "entrySignalCode": None, "isExclusive": None,
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
            "asOf": "2026-08-11", "status": "available", "contentHash": "sha256:test",
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
            "asOf": "2026-08-11", "status": "available", "contentHash": "sha256:test",
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

    def test_main_task_requires_five_peers_then_batch_scores_one_version(self) -> None:
        model = json.loads((ROOT / "skills/geto-diligence-company/references/lead-value-model.json").read_text())
        capability = {
            "foundationKey": "geto:capability-foundation", "foundationVersion": "2026-08-11",
            "asOf": "2026-08-11", "status": "available", "contentHash": "sha256:test",
            "productCodes": ["aluminum_formwork"], "scenarioCodes": [], "roleCodes": [],
            "caseKeys": [], "gapCodes": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "AU-Australia"
            for index in range(6):
                company = RESEARCH_BUNDLE.empty_company(f"Company {index}", "Australia", "AU")
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

            result = COHORT_CALCULATOR.score_country(root, model, "2026-08-19")
            scored = [
                json.loads(path.read_text(encoding="utf-8"))
                for path in sorted((root / "companies").glob("*/company.json"))
            ]
            versions = {item["assessment"]["cohortBaselineVersion"] for item in scored}
            sixth = next(item for item in scored if item["company"]["companyName"] == "Company 5")
        self.assertEqual(len(pending_result["pendingCompanyFiles"]), 4)
        self.assertEqual(len(result["updatedCompanyFiles"]), 6)
        self.assertEqual(len(versions), 1)
        self.assertTrue(all(item["assessment"]["status"] == "completed" for item in scored))
        for item in scored:
            errors, _, _ = RESEARCH_BUNDLE.validate_company(item)
            self.assertEqual(errors, [])
        account = next(
            item for item in sixth["assessment"]["dimensions"]
            if item["dimensionCode"] == "account_scale"
        )
        self.assertEqual(account["baselineScore"], 10)
        self.assertEqual(account["finalDimensionScore"], 10)

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

    def test_inquiry_report_requires_depth_and_project_coverage(self) -> None:
        company = base_company()
        company["inquiryAssessment"] = {"status": "completed"}
        shallow = "# Report\n\n## 结论\n\n资料较少。\n"
        errors = RESEARCH_BUNDLE.validate_inquiry_report(shallow, company)
        self.assertTrue(any("12 substantive" in item for item in errors))
        self.assertTrue(any("project search coverage" in item for item in errors))

        headings = [
            "执行摘要", "询盘原始信息", "主体身份", "业务与产品能力", "项目组合",
            "项目检索覆盖", "管理层与联系人", "财务与信用", "诉讼监管与合规",
            "Provider 海关与供应链", "GETO 适配", "询盘准备度", "核心冲突与缺口",
            "风险矩阵与硬阻断", "下一步动作清单", "建议交易条件", "最终判断",
        ]
        detailed = "# Report\n\n" + "\n\n".join(f"## {heading}\n\n待证据化展开。" for heading in headings)
        self.assertEqual(RESEARCH_BUNDLE.validate_inquiry_report(detailed, company), [])

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
