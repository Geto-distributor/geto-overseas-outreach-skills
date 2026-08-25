---
name: geto-capability-foundation
description: 为 GETO 海外市场调研提供共享、只读的产品、技术、场景、ICP、采购角色、公开案例与版本化 SearchLexicon，供线索召回、六维价值评分、竞对竞争面和合作切入判断使用。用于选择国家×角色×产品×技术关键词和验证 VMC/制造/品牌/租赁/经销/安装等召回边界；不负责发现公司、背调、分类、评分、调用 Provider 或上传 OmniX。
---

# GETO 能力与关键词底座

本 Skill 只回答 GETO 能提供什么、哪些客户/项目适配、如何形成仅用于召回的关键词切片。不得把 GETO 宣传材料当成目标市场事实。

## 使用方式

1. 读取 [foundation-contract.md](references/foundation-contract.md)，确定 CapabilityContext。
2. 按需读取产品、场景、ICP、案例、关系与竞对种子资产；竞对种子仅用于召回。
3. 需要市场发现或竞对研究时读取 [search-lexicon.json](references/search-lexicon.json)，按 `marketCode + language + laneCode/companyRole + productCode + technology/method + projectScenario` 选择词和查询模板。
4. 运行：

```bash
python scripts/validate_foundation.py
python scripts/validate_search_lexicon.py references/search-lexicon.json
```

5. 可运行 `python scripts/select_context.py --query '<需求>' --country <ISO2>` 选择相关产品、场景、ICP 和案例。

## SearchLexicon 纪律

- 包含产品技术词、VMC、volumetric modular construction、offsite construction、off-site manufacturing、modular housing、prefabricated steel structure、DfMA、concrete/high-rise/residential/formwork、mining camp/site accommodation。
- 包含 manufacturer、factory、system owner、brand owner、contract manufacturing、rental、distributor、reseller、installer、erection、dismantling、labor 等商业与履约角色词。
- `positiveTerms/synonyms/abbreviations` 只扩大召回；`negativeTerms` 帮助发现误召回，不直接排除主体。
- 公司名称包含 framework、formwork、modular 等不得成为 confirmed competitor Evidence。
- 每个回归种子必须声明 expectedRecall 和 expectedClassificationBoundary，覆盖 VMC 漏召回、framework/formwork 名称误召回、installer-only、委外生产自有品牌和渠道经销/租赁。

## 证据纪律

- `company_published` 只证明 GETO 官方资料表达过相应能力或案例。
- `independent_verified` 必须有独立权威来源；缺失时不得升级。
- 匿名案例可证明产品场景，不能证明具名客户关系。
- 目标公司的 lead/competitor 分类必须由目标公司 Evidence 支持，不由本底座直接授予。

## 下游边界

- `$geto-find-leads` 使用关键词做单轨召回，不得据此确认 lead。
- `$geto-mine-competitor-customers` 使用 competitionSurface 和角色词召回，必须另查官网 Products/Services、商业控制与履约模式。
- `$geto-diligence-company` 在产品适配和评分时引用本次 CapabilityContext；底座缺失不阻断客观事实背调。
- `$geto-run-market-research` 在 `progress.md` 记录使用的产品、场景和 SearchLexicon 版本。

## 职责边界

- 本 Skill 只读取本地能力与关键词资产；Web、Provider 和 OmniX 操作由下游研究 Skills 执行。
- Company、Project、Relationship、researchClassifications 和 Assessment 由相应领域 Skill 创建。
- 关键词命中只形成召回候选，制造状态、商业控制、竞对资格和客户价值由目标公司 Evidence 决定。
