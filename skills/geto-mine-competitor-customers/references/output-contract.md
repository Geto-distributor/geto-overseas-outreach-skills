# 竞对客户任务输出

输出包含：竞对自然名称与强身份锚点、目标国家与产品范围、查询边界、关系候选、仲裁结果、已核实客户、非客户关系、客户公司目录、客户六维评分状态、组合平均分与覆盖率、逐关系合作切入分、Evidence、冲突、缺口和下一步。

竞对 `company.json` 保存已核实 relationships[] 和派生的 competitorCustomerPortfolio；每个客户事实与六维 assessment 保存在该客户自己的 company.json。report.md 展示竞对客户组合和关系切入结论，Sources/sources.md 从内嵌 Evidence 生成。

主任务回传至少列出：

- verifiedCustomerCount；
- scoredCustomerCount；
- customerScoreCoverage；
- averageCustomerValueScore；
- score=null 的客户及缺口；
- 每条 score=null 的关系切入评估及缺口；
- 竞对、客户、项目、产品与关系成果路径。
