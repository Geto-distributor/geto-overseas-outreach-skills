# 独立子资源

## Contact

contactKey、姓名、职位、层级、工作邮箱、工作电话、公司域名、地点、公司自然键、verificationStatus、sourceKeys、lastCheckedOn。按公司域名、姓名与职位去重，避免把同一联系人重复挂接。

## CustomsEvidence

evidenceKey、主体、交易方、查询时间窗口、HS/商品描述、数量/金额、记录数、查询条件、来源、valueStatus、evidenceBoundary。汇总有数但明细无数时必须明确两者边界。

## Financial

financialKey、公司自然键、财报期、币种、营收、利润、资产负债等结构化指标、风险结论、sourceKeys、valueStatus。不同财报期不得合并成一个长文本。

三类资源均可引用 Claim/Source，但不得把第三方 Observation 直接当已核实事实。
