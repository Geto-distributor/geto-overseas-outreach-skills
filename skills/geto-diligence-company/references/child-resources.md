# Company 子资源字段

- contacts：contactType、name、jobTitle、department、seniority、responsibilities、buyingRole、location、workEmail、workPhone、linkedinUrl、otherProfileUrl、verificationStatus、lastVerifiedOn、evidence。
- financialRecords：recordType、period、value、currency、unit、valueStatus、description、evidence。
- customsTransactions：resultType、direction、importer、exporter、partnerCountry、transactionOn、dateRange、hsCode、productDescription、quantity、quantityUnit、value、currency、ports、recordCount、provider、queryScope、verificationStatus、notes、evidence。
- inquiries：receivedOn、buyerName、buyerContact、buyerRole、requestedProduct、quantity、technicalRequirements、projectName、projectCountry、deliveryDestination/Port、signingEntity、payer、paymentTerms、requestedDocuments、attachments、verificationStatus、openQuestions、evidence。
- projects、relationships、licensesAndCertifications、newsAndSocialMedia、lawsuitsAndCompliance、risks、missingInformation、recommendedActions、additionalInformation 均使用主字段合同并内嵌 Evidence。
- researchQueries 记录查了什么、范围、结果状态和查询 Evidence；`no_result` 与 `not_queried` 可为空 Evidence。
- reportFiles 固定使用 fileName、path、format、reportType、language、generatedOn、description。

联系人、财务、海关和询盘不能塞入 company.summary 或报告长文本代替结构化字段。注册资本与实缴资本只进入 capitalRecords。
