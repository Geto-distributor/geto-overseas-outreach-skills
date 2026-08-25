# Company 字段必填性合同

## 读取方式

本合同定义本地 `company.json` 的字段出现要求、值要求和条件门禁。字段含义与枚举读取 [company-json-contract.md](company-json-contract.md)，完整形态读取 [company-json-example.json](company-json-example.json)。

| 标记 | 含义 | 合法表达 |
| --- | --- | --- |
| R | 字段必须出现且必须有有效值 | 非空字符串、有效数字、布尔值、非空对象或满足合同的非空数组 |
| S | 字段必须出现，当前可以没有事实值 | `null`、`[]`、`unknown` 或相应状态对象 |
| C | 触发条件成立时必须出现并有值 | 条件未触发时使用合同指定的空值或状态 |
| O | 有事实时填写 | 可省略；若出现仍需满足类型、枚举与 Evidence 合同 |

`R/S/C/O` 描述数据合同，不描述公开资料是否一定存在。研究范围内未取得的事实通过 `researchQueries[]` 和 `missingInformation[]` 表达。

## 顶层字段

所有顶层字段都属于 S：键必须存在，列表没有记录时写 `[]`，三个评估对象未执行时分别写 `{"status":"not_requested"}`。

| 字段 | 值要求 |
| --- | --- |
| company | R，对象 |
| aliases、registrations、capitalRecords、websites、addresses | S，数组 |
| marketPresence、socialChannels、researchClassifications、companyRoles | S，数组 |
| productsAndServices、projects、relationships、contacts | S，数组 |
| licensesAndCertifications、financialRecords、newsAndSocialMedia | S，数组 |
| customsTransactions、lawsuitsAndCompliance、inquiries、risks | S，数组 |
| researchQueries、missingInformation、recommendedActions、additionalInformation | S，数组 |
| reportFiles | S，数组 |
| assessment | S；执行长期价值观察或评分时进入 C |
| inquiryAssessment | S；存在本次原始询盘时进入 C |
| competitorCustomerPortfolio | S；执行竞对客户组合研究时进入 C，不作为 competitor 分类或上传前置条件 |
| researchStatus | R：completed、completed_with_gaps、identity_conflict |
| lastResearchedOn | R：YYYY-MM-DD |

## Company 核心

`company` 的全部键都需要出现，便于新任务和后续投影保持稳定形态。

| 字段 | 要求 |
| --- | --- |
| companyName、entityType、country、countryCode | R |
| status、summary、researchConclusion、listingStatus | R；listingStatus 可使用 unknown |
| evidence | S；完成主体判断或引用公司核心事实时至少一条 |
| foundedOn、companyScale、headcount | S；未知时为 null |
| listingDetails | C：listingStatus=self_listed 或 parent_listed 时填写 |
| marketPosition、priority、procurementBoundary | S；未形成判断时为 null |

`entityType` 使用 legal_entity、operating_company、corporate_group。countryCode 使用大写 ISO2。主体身份冲突未解决时，researchStatus 使用 identity_conflict。

## Evidence

每条 Evidence 的九个基础键都必须出现。

| 字段 | 要求 |
| --- | --- |
| sourceTitle、sourceType、retrievedOn | R |
| sourceUrl | R；sourceType=customer_document 且没有公开 URL 时可为空字符串 |
| publisher、publishedOn、locator、excerpt、note | S；来源未提供对应信息时可为 null 或空字符串 |
| verificationScope | O；Provider 只验证特定字段时填写非空数组 |

主要业务列表 item 出现时必须带 `evidence[]`。confirmed、verified、active、own_factory_confirmed 等肯定性事实至少需要一条 Evidence。`researchQueries.status=not_queried|no_result|failed` 可没有 Evidence；found、partial 必须有 Evidence。

## 主体与经营资源

| 资源 | R 字段 | C 字段 | S/O 字段 |
| --- | --- | --- | --- |
| aliases[] | name、aliasType、status、evidence | — | language、description、note |
| registrations[] | registrationType、registrationNumber、legalName、entityKind、jurisdiction、status、verificationStatus、evidence | issuingAuthority：声称 verified 时；registeredOn：已取得登记日期时 | issueDateRaw、expiresOn、registeredBusinessScope、description |
| capitalRecords[] | capitalType、amount、currency、asOf、status、description、evidence | — | — |
| websites[] | url、websiteType、status、verificationStatus、lastCheckedOn、evidence | — | — |
| addresses[] | addressType、country、status、evidence；fullAddress 或 addressLine 至少一个 | street、city、state/province/region、postalCode：地址来源提供时 | note |
| marketPresence[] | presenceType、country、status、description、evidence | region、city：市场存在可定位时 | — |
| socialChannels[] | platform、url、status、lastCheckedOn、evidence | handle：平台存在公开 handle 时 | lastActivityOn |

## 分类、角色与产品

| 资源 | R 字段 | C 字段 | S/O 字段 |
| --- | --- | --- | --- |
| researchClassifications[] | classification、status、country、productScope[]、reason、evidence | confirmed competitor：productScope 非空并满足产品门禁；active lead：满足独立采购、使用、选型影响或正式渠道路径 | rejected 仍保留反证 Evidence；active 列表集合排除 rejected |
| companyRoles[] | role、scope、country、status、rationale、evidence | projectName：角色由具体项目证明时 | — |
| productsAndServices[] | name、type、category、markets[]、commercialRoles[]、manufacturingStatus、status、getoRelevance、evidence | confirmed competitor 对应产品：markets、商业控制角色与 Evidence 非空；manufacturingStatus 为 own_factory_confirmed、manufacturing_claimed、outsourced 时填写 manufacturingDescription | systemName、description、technologyTerms[]、applications[]、targetCustomers[]、factoryLocations[]、media[]、representativeProject |
| productsAndServices[].media[] | url、mediaType、caption、lastVerifiedOn、evidence | — | — |

confirmed competitor 的匹配产品至少包含 manufacturer、system_owner、brand_owner、distributor、reseller、rental_provider 之一。installer 或 service_contractor 可表达履约角色，不单独形成 confirmed competitor。

## 项目

| 对象 | R 字段 | C 字段 | S/O 字段 |
| --- | --- | --- | --- |
| projects[] | projectName、country、status、currentOrHistorical、participants[]、roleVerificationStatus、verificationStatus、lastVerifiedOn、description、evidence | targetCompanyRole：目标公司被列为参与方时；startedOn：已核实开工时；expectedCompletionOn：当前/未来项目取得计划日期时；endedOn：历史项目取得结束日期时 | aliases[]、projectType、region、city/location、address、contractScope、contractNumber、contractValue、currency、scale、buildingArea、areaUnit、storeys、units、procurementStage、inquiryMatchStatus、productsOrTechnologies[]、potentialProducts[]、demandJudgement、entryWindow、opportunity、procurementBoundary、knownRelationship、getoRelevance |
| participants[] | name、role、status、lastVerifiedOn、evidence | identity：取得强身份锚点时填写；confirmed participant 需要 Evidence | — |
| potentialProducts[] | productName、usageSummary、evidence | — | — |

项目金额出现时 currency 必填；buildingArea 出现时 areaUnit 必填。项目需求、采购边界、进入窗口与 GETO 机会只在存在事实或明确分析依据时填写。

## 关系与竞对客户

每条 relationships[] 的通用 R 字段是：relationshipType、counterpartyName、country、status、description、limitations[]、exclusivity、evidence。exclusivity 的 status、scope、description、lastVerifiedOn、evidence 五个键都必须出现；status=exclusive 或 non_exclusive 时需要范围或描述及 Evidence。

| 条件 | 条件必填字段 |
| --- | --- |
| 关系涉及具体项目 | projectName |
| 关系涉及具体产品或服务 | productOrService |
| counterparty 已核实强身份 | relatedPartyIdentity |
| reviewDecision=verified_customer | relationshipType=customer、counterpartyName、projectName 或 productOrService、合作 description、Evidence |
| 保存客户长期价值摘要 | customerValueAssessment.overallScore、grade、assessedOn、evidence |
| 计算合作切入分 | relationshipRole、cooperationModeCode、cooperationDepthCode、relationshipStatusCode、buyer、actualUser、firstEvidenceOn、lastVerifiedOn、reviewDecision、entryPoint、entrySignalCode、entryAssessment |
| entryAssessment.status=completed | modelCode、modelVersion、0–5 score、rationale、assessedOn、evidenceStatus、gapCodes[]、Evidence；分数具有对应关系事实锚点 |
| entryAssessment.status=pending_evidence | score=null、非空 gapCodes[] |

## 联系人与资质

| 资源 | R 字段 | C 字段 | S/O 字段 |
| --- | --- | --- | --- |
| contacts[] | contactType、name、verificationStatus、lastVerifiedOn、evidence；workEmail、workPhone、linkedinUrl、otherProfileUrl 至少一个 | jobTitle、department、seniority、responsibilities、buyingRole：存在对应任职或授权 Evidence 时 | location |
| licensesAndCertifications[] | name、licenseType、licenseNumber、holderName、authority、jurisdiction、scope、status、evidence | issuedOn、expiresOn：来源提供时 | description |

verificationStatus=email_only 只确认 workEmail 对应验证范围；任职、职位、授权和 buyingRole 分别依赖相应 Evidence。

## 财务、新闻、海关与合规

| 资源 | R 字段 | C 字段 | S/O 字段 |
| --- | --- | --- | --- |
| financialRecords[] | recordType、subjectEntity、scope（或兼容 financialScope）、accountingScope、relationshipToTarget、period、valueStatus、description、evidence | value 有值时填写 unit；货币金额填写 currency | financialScope：兼容旧输入字段 |
| newsAndSocialMedia[] | itemType、title、summary、publishedOn、status、evidence | publisherOrPlatform、url：来源可定位时；relatedProject：新闻指向具体项目时 | businessMeaning |
| customsTransactions[] | resultType、direction、partnerCountry、productDescription、provider、queryScope、verificationStatus、evidence；importer 或 exporter 至少一个；transactionOn 或 dateRange 至少一个 | quantity 出现时 quantityUnit；value 出现时 currency | hsCode、ports[]、recordCount、notes |
| lawsuitsAndCompliance[] | recordType、caseNumber、authority、jurisdiction、recordOn、status、adverse、description、evidence | amount 出现时 currency；存在具名当事人、结果或项目时填写 parties[]、outcome、relatedProject | — |

## 询盘

存在原始询盘任务时，inquiries[] 至少一条。每条询盘的 R 字段是 inquiryRef、receivedOn、requestedProduct、verificationStatus、openQuestions[]、evidence；已取得的信息分别进入 buyerName、buyerContact、buyerRole、quantity、quantityUnit、technicalRequirements、projectName、projectCountry、deliveryDestination、deliveryPort、incoterm、signingEntity、payer、paymentTerms、requestedDocuments[]、attachments[]。

| 条件 | 条件必填字段 |
| --- | --- |
| quantity 有值 | quantityUnit |
| deliveryPort 有值 | incoterm |
| inquiryAssessment 非 not_requested | inquiryRef 必须匹配 inquiries[]；完整填写固定 assessment 字段和六个维度 |
| inquiryAssessment.status=completed | overallScore、grade、overallConclusion、assessedOn；六个维度 score、maxScore、rationale、Evidence、gapCodes[] |
| 存在硬阻断或关键缺口 | hardBlockCodes[]、gapCodes[] 使用对应非空代码 |

询盘原文只证明买方当时陈述的需求；主体、授权和付款能力使用各自来源闭合。

## 风险、缺口、行动与查询

| 资源 | R 字段 | C 字段 | S/O 字段 |
| --- | --- | --- | --- |
| risks[] | riskType、severity、status、description、impact、blocking、mitigation、evidence | blocking=true 时明确阻断解除条件 | — |
| missingInformation[] | topic、status、description、impact、checkedScope、recommendedAction、evidence | status=not_queried 时 evidence 可为空；conflicting、outdated、provider_failed 保留对应查询或冲突 Evidence | — |

`lead_assessment_contract_incomplete` 只表示长期价值评分合同尚未完成。assessment 完成、六维均有最终分且 overallScore 非空时必须移除该主题；它不能承载注册主体或 entity kind 仲裁，身份缺口使用独立且具体的 topic。
| recommendedActions[] | action、priority、owner、timing、reason 或 rationale、evidence | — | — |
| additionalInformation[] | topic、title、details、status、evidence | — | 仅承载没有专属结构的事实 |
| researchQueries[] | topic、channel、query、scope、status、checkedOn、resultCount、evidence | found、partial 时 Evidence 非空 | not_queried、no_result、failed 可为空 Evidence |
| reportFiles[] | fileName、path、format、reportType、language、generatedOn、description | item 出现时 path 对应文件必须存在 | — |

## 长期价值 assessment

| 状态 | 必填规则 |
| --- | --- |
| not_requested | 只包含 status |
| pending_model、pending_capability_foundation、incomplete_evidence、pending_cohort_baseline | assessment 的全部结构键出现；overallScore、grade、cohortBaselineVersion、cohortAsOf 保持 null；capabilityContext、dimensions、Evidence 与 gapCodes 反映当前阶段 |
| completed | assessmentType=lead_value、固定 modelCode/modelVersion/ratingScaleVersion、完整 capabilityContext、六个固定维度、overallScore、grade、informationCompleteness、overallConclusion、assessedOn、cohortKey、cohortBaselineVersion、cohortAsOf、顶层 Evidence |

每个已评分维度需要 observedScore、baselineScore、baselinePolicy、finalDimensionScore、maxScore、evidenceGrade、evidenceWeight、level、rationale、Evidence、gapCodes[]、capCodes[]。完成态六个维度都必须有最终分和 Evidence。

## competitorCustomerPortfolio

| 状态 | 必填规则 |
| --- | --- |
| not_requested | 只包含 status |
| no_verified_customers | 完整组合结构；customers=[]，计数和覆盖率为 0，averageCustomerValueScore=null |
| pending_customer_scores | customers[] 与 verified_customer 去重集合一致；客户分为 null |
| partial_coverage | 已核实客户全部列出；只有完成长期价值评分的客户带分；覆盖率和均分按已评分客户计算 |
| completed | 所有 verified_customer 都完成评分；计数、覆盖率、平均分与 customers[] 精确一致 |

customers[] 每项始终需要 companyName、country、relationshipCount、customerAssessmentStatus、customerValueScore、customerValueModelVersion、cohortBaselineVersion、assessedOn、evidence。未评分客户的 score 与三个评分版本/日期字段为 null；已评分客户完整填写这些字段。

## 工作空间条件

| 条件 | 必需工件 |
| --- | --- |
| 单公司交付 | company.json、report.md；存在 Evidence 时生成 Sources/sources.md |
| assessment.status != not_requested | RisksAndAssessment/capability-context.json，并与 assessment.capabilityContext 完全一致 |
| assessment.status=completed | 国家 Scoring/lead-value-cohort.json，baselineVersion 与 cohortKey 对应 assessment |
| reportFiles[] 有记录 | 每个 path 指向真实文件 |
| inquiryAssessment 已执行 | report.md 满足询盘报告主题、项目讨论与项目检索覆盖合同 |

交付前依次运行 `build_deduplicated_sources.py`、`validate_company_json.py` 和 `validate_workspace.py --company-dir`。国家主任务再运行国家模式 validator。
