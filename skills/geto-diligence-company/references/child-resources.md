# Company 子资源字段

- contacts：contactType、name、jobTitle、department、seniority、responsibilities、buyingRole、location、workEmail、workPhone、linkedinUrl、otherProfileUrl、verificationStatus、lastVerifiedOn、evidence。
- financialRecords：recordType、period、value、currency、unit、valueStatus、description、evidence。
- customsTransactions：resultType、direction、importer、exporter、partnerCountry、transactionOn、dateRange、hsCode、productDescription、quantity、quantityUnit、value、currency、ports、recordCount、provider、queryScope、verificationStatus、notes、evidence。
- inquiries：receivedOn、buyerName、buyerContact、buyerRole、requestedProduct、quantity、technicalRequirements、projectName、projectCountry、deliveryDestination/Port、signingEntity、payer、paymentTerms、requestedDocuments、attachments、verificationStatus、openQuestions、evidence。
- projects、relationships、licensesAndCertifications、newsAndSocialMedia、lawsuitsAndCompliance、risks、missingInformation、recommendedActions、additionalInformation 均使用主字段合同并内嵌 Evidence。
- researchQueries 记录查了什么、范围、结果状态和查询 Evidence；`no_result` 与 `not_queried` 可为空 Evidence。
- reportFiles 固定使用 fileName、path、format、reportType、language、generatedOn、description。format 使用 `markdown|docx|pdf|html`；reportType 使用 `diligence|assessment|risk|supplement`。

联系人、财务、海关和询盘不能塞入 company.summary 或报告长文本代替结构化字段。注册资本与实缴资本只进入 capitalRecords。

Provider 只验证邮箱存在或可投递时，contact 使用 `verificationStatus=email_only`；对应 Evidence 使用 `relation=context`、`verificationScope=["workEmail.deliverability"]`，note 明示不支持当前任职、职位、授权或 buyingRole。上述字段保持 null，直到公司官网、人员公开职业页或多源一致证据分别支持。
