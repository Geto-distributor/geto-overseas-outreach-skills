# GETO Overseas Outreach Skills

GETO 海外市场调研 Skill 家族。当前国家调研任务负责协调，六类角色、竞对、TradeWind、网易外贸通和单公司背调分别使用独立任务；subagent 只在单个任务内部并行。国家任务维护产品×角色×来源覆盖矩阵和候选总账，研究成果保存在唯一的本地 ResearchBundle。

本地交付结构：

```text
<国家>/
├── progress.md
└── companies/<公司自然名称>/
    ├── company.json
    ├── report.md
    └── Sources/sources.md
```

company.json 使用内嵌 Evidence，lead/competitor 由 researchClassifications 独立表达。Lead 要求采购、使用、选型影响或正式渠道路径；泛化合作机会不形成 Lead。关键词只用于召回；竞对判定必须核查产品商业控制、目标市场和制造/委外/经销/租赁/安装履约模式。

Skills：

- `geto-run-market-research`：用户可见任务编排与国家 progress.md。
- `geto-find-leads`：单公司角色轨道发现。
- `geto-diligence-company`：一条线索或普通目标公司一个任务的 ResearchBundle。
- `geto-diligence-inquiry`：一条询盘一个任务的主体核验与交易准备度，不使用 cohort 插补。
- `geto-diligence-competitor`：一家竞对一个任务的产品、商业控制、制造、项目与客户事实背调。
- `geto-mine-competitor-customers`：已确认竞对的官方合作披露与客户关系核验，并可按需执行客户价值组合与关系切入评估。
- `geto-map-relationships`：有证据的 typed relationships[]。
- `geto-assess-precontract-risk`：成熟交易的签约前风险。
- `geto-capability-foundation`：产品、场景、ICP 与 SearchLexicon。

长期客户价值采用两阶段评分：单公司任务提交六维观察输入，国家主任务优先使用同类型版本化中位数；没有可用中位数且公开研究已完成时使用 0 分基线，未查询、Provider 失败和身份冲突保持 pending。询盘准备度使用独立固定口径，可在单条询盘背调完成后立即生成。执行竞对组合分析时，客户价值平均分由已核实客户的当前六维总分聚合，并同时显示客户数和评分覆盖率；每条竞对客户关系可另行使用 0–5 合作切入分。

验证：

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
```

OmniX 不是研究完成条件。本地验证通过后才询问用户是否通过独立 `omnix-market` Skill 上传完整 Company Aggregate。
