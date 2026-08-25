# Company 分类与业务参与合同

## 三类对象

`companyRoles[]` 表达公司在市场中的客观角色；`researchClassifications[]` 只表达 GETO 对该公司的业务分类；合作设想写入 `relationships[]`、`recommendedActions[]` 或项目机会字段。三者不得互相替代。

## Lead Gate

Lead 表示 GETO 可开发的目标账户。每条 active lead 必须有独立 Evidence 支持至少一种路径：

- 采购、租赁或付款路径；
- 模板、脚手架、支撑、预制或模块化产品的实际使用；
- 设计、规范、预审、批准或供应商选型影响；
- 对 GETO 产品或明确非重叠互补产品的经销、转售或正式渠道路径；
- 已识别当前或未来项目，且目标公司在项目中具有可核验的采购、使用或技术影响角色。

状态语义：

- `confirmed`：主体稳定，目标账户路径和对应产品范围由直接或高质量交叉 Evidence 闭合。
- `possible`：主体稳定且存在合理目标账户路径，但需求时态、项目责任、采购权限或渠道边界仍有关键缺口。
- `rejected`：没有可证实的采购、使用、选型影响或正式渠道路径；仅有行业相邻、共同项目、一般合作设想或直接竞争关系。

公司规模、官网产品、行业目录、联系人存在或“可能联合供货”不能单独形成 lead。顾问、开发商、总包、分包和经销商分别按其实际影响路径判断，不因 companyRole 自动成为 lead。

## Competitor Gate

Competitor 表示在目标国家或地区经营重叠产品，并控制品牌、系统、制造、销售、经销、转售或租赁商业化的公司。状态规则由 `$geto-diligence-competitor` 的 competitor-contract 定义。

安装、施工或咨询服务本身不能形成 confirmed competitor。产品名称、关键词和共同参建只用于召回。

## 双分类

同一 Company 可以同时存在 active lead 和 confirmed competitor，但两个 Gate 必须分别成立：

- competitor Evidence 证明产品、市场和商业控制；
- lead Evidence 证明独立的采购、使用、选型影响或正式渠道路径；
- 两条分类分别写清 productScope、理由、限制和 Evidence；
- lead 理由不能只复述竞对的销售、租赁、制造能力或泛化合作可能；
- 对直接竞对开展合作时，在 `risks[]` 和 `recommendedActions[]` 记录信息隔离、非重叠产品或项目限定边界。

泛化的产能互补、联合投标、战略合作或第二来源设想属于合作机会，不激活 lead 分类。

## active 分类集合

列表、投影、统计和导入计划只把 `status=confirmed|possible` 视为 active：

- lead 列表排除 `lead=rejected`；
- competitor 列表排除 `competitor=rejected`；
- `possible` 必须保留状态标签，不能展示为 confirmed；
- 本地 ResearchBundle 保留 rejected 分类及反证 Evidence，但 rejected 不进入对应业务列表索引。

## 竞对合作披露

竞对或对方官方来源明确点名可识别公司，并闭合具体项目或具体产品/服务及实际合作内容时，可以确认关系事实。buyer、payer、actualUser、sale/rental、排他、框架关系和当前持续性分别取证；未知字段保持 null，不阻止保存已闭合的合作关系。

Logo 墙、匿名案例、搜索摘要、共同参建或无法拆分的组合主体保持 pending。客户价值评分和关系切入分是可选的后续分析，不是 confirmed competitor 或合作关系进入 Company Aggregate 的前置条件。
