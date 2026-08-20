# Company 子资源字段合同

## 通用规则

- 一个 company.json 只表达一个 legal_entity、operating_company 或 corporate_group。
- 事实进入对应结构化字段，不用 summary、report.md 或 additionalInformation 代替。
- 字段未知时使用 null、空数组或省略可选字段，不编造占位值。
- 所有主要列表 item 包含 evidence[]。Evidence 固定使用 sourceTitle、sourceUrl、publisher、sourceType、publishedOn、retrievedOn、locator、excerpt、note；字段级 Provider 证据可增加 verificationScope[]。
- sourceType 只用 official_website|registry|government|court|financial_report|media|social_media|provider|customer_document|other。事实成立、待核、冲突或拒绝由所属 item 的 status、verificationStatus、reason 和 researchConclusion 表达。

## 主体与身份

- company：companyName、entityType、country、countryCode、status、summary、researchConclusion、foundedOn、companyScale、headcount、listingStatus、listingDetails、marketPosition、priority、procurementBoundary、evidence。listingStatus 使用 self_listed|parent_listed|not_listed|unknown。
- aliases[]：name、aliasType、status、description、note、evidence。
- registrations[]：registrationType、registrationNumber、legalName、entityKind、jurisdiction、issuingAuthority、registeredOn、issueDateRaw、status、verificationStatus、description、evidence。
- capitalRecords[]：capitalType、amount、currency、asOf、status、description、evidence。capitalType 使用 registered_capital|paid_in_capital；注册资本与实缴资本不能解释为现金、收入、净资产、授信或付款能力。
- websites[]：url、websiteType、status、verificationStatus、lastCheckedOn、evidence。
- addresses[]：addressType、fullAddress/addressLine、street、city、state/province/region、postalCode、country、status、note、evidence。
- marketPresence[]：presenceType、country、region、city、status、description、evidence。
- socialChannels[]：platform、handle、url、status、lastCheckedOn、evidence。

## 分类、角色与产品

- researchClassifications[]：classification、status、country、productScope[]、reason、evidence。classification 只用 lead|competitor。
- companyRoles[]：role、scope、country、projectName、status、rationale、evidence。
- productsAndServices[]：name、type、category、description、technologyTerms[]、applications[]、targetCustomers[]、markets[]、commercialRoles[]、manufacturingStatus、manufacturingDescription、factoryLocations[]、media[]、representativeProject、status、getoRelevance、evidence。media[] 使用 url、mediaType=image|video|document、caption、lastVerifiedOn、evidence；representativeProject 使用 projects[] 中的自然项目名。

## 项目与关系

- projects[]：projectName、aliases[]、projectType、country、region、city/location、address、participants[]、targetCompanyRole、contractScope、contractNumber、contractValue、currency、scale、buildingArea、storeys、units、status、procurementStage、startedOn、endedOn、currentOrHistorical、inquiryMatchStatus、roleVerificationStatus、productsOrTechnologies[]、potentialProducts[]、demandJudgement、entryWindow、opportunity、procurementBoundary、knownRelationship、getoRelevance、verificationStatus、lastVerifiedOn、description、evidence。
- participants[] 每项使用 name、role、identity、status、lastVerifiedOn、evidence。role 使用 owner|developer|main_contractor|subcontractor|consultant|designer|supervisor|partner|other；status 使用 confirmed|possible|conflicting|historical。
- relationships[] 通用字段：relationshipType、counterpartyName、counterpartyRole、companyRole、projectName、country、status、startedOn、endedOn、description、evidence。
- 竞对客户关系扩展字段：relationshipRole、productOrService、cooperationModeCode、cooperationDepthCode、relationshipStatusCode、buyer、payer、actualUser、exclusivity、firstEvidenceOn、lastVerifiedOn、reviewDecision、entryPoint、limitations[]、entrySignalCode、entryAssessment。exclusivity 使用 status、scope、description、lastVerifiedOn、evidence；status 使用 exclusive|non_exclusive|unknown|conflicting。详细枚举与 0–5 切入评估结构由 geto-mine-competitor-customers 的 competitor-customer-contract 定义。
- licensesAndCertifications[]：licenseType、licenseNumber、authority、jurisdiction、issuedOn、expiresOn、status、description、evidence。

## 联系人

- contacts[]：contactType、name、jobTitle、department、seniority、responsibilities、buyingRole、location、workEmail、workPhone、linkedinUrl、otherProfileUrl、verificationStatus、lastVerifiedOn、evidence。
- Provider 只验证邮箱存在或可投递时，verificationStatus=email_only；Evidence 使用 verificationScope=["workEmail.deliverability"]，note 只陈述邮箱验证范围。任职、职位、授权和 buyingRole 分别依据公司官网、人员公开职业页或多源一致证据填写。

## 财务、海关与合规

- financialRecords[]：recordType、period、value、currency、unit、valueStatus、description、evidence。
- customsTransactions[]：resultType、direction、importer、exporter、partnerCountry、transactionOn、dateRange、hsCode、productDescription、quantity、quantityUnit、value、currency、ports[]、recordCount、provider、queryScope、verificationStatus、notes、evidence。
- lawsuitsAndCompliance[]：recordType、caseNumber、authority、jurisdiction、recordOn、status、adverse、description、evidence。
- newsAndSocialMedia[]：itemType、title、summary、publishedOn、status、evidence。

## 询盘

- inquiries[]：inquiryRef/inquiryNumber、receivedOn、buyerName、buyerContact、buyerRole、requestedProduct、quantity、quantityUnit、technicalRequirements、projectName、projectCountry、deliveryDestination、deliveryPort、incoterm、signingEntity、payer、paymentTerms、requestedDocuments[]、attachments[]、verificationStatus、openQuestions[]、evidence。
- inquiryRef 是本地业务引用，不使用 Provider 内部 job/result ID。
- 询盘原文和附件使用 sourceType=customer_document；它们可证明买方当时陈述的需求，不能单独证明法定主体、任职授权或付款能力。

## 风险、缺口与行动

- risks[]：riskType、severity、status、description、mitigation、evidence。
- missingInformation[]：topic、status、description、impact、evidence。
- recommendedActions[]：action、priority、owner、timing、reason/rationale、evidence。
- additionalInformation[]：topic、title、details、status、evidence。已有专属结构的联系人、财务、项目、诉讼、海关或询盘不能放在这里。
- researchQueries[]：topic、channel、query、scope、status、checkedOn、resultCount、evidence。status 使用 found|no_result|partial|failed|not_queried。

## 评估与报告

- assessment：长期客户价值观察输入与主任务 cohort 结果；字段由 lead-assessment-contract 定义。
- inquiryAssessment：单条询盘准备度；字段由 geto-diligence-inquiry 的 inquiry-contract 定义。
- competitorCustomerPortfolio：竞对已核实客户的去重组合统计；保存客户数、已评分数、覆盖率、客户价值平均分和 customers[]。字段由 geto-mine-competitor-customers 的 competitor-customer-contract 定义。
- reportFiles[]：fileName、path、format、reportType、language、generatedOn、description。format 使用 markdown|docx|pdf|html；reportType 使用 diligence|assessment|risk|supplement。
