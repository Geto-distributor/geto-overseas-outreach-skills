# GETO Overseas Outreach Skills

GETO 海外市场调研 Skill 家族。当前国家调研任务负责协调，六类角色、TradeWind、网易外贸通和单公司背调分别使用独立任务；subagent 只在单个任务内部并行。研究成果保存在本地 ResearchBundle。

本地交付结构：

```text
<国家>/
├── progress.md
└── companies/<公司自然名称>/
    ├── company.json
    ├── report.md
    └── Sources/sources.md
```

company.json 使用内嵌 Evidence，lead/competitor 由 researchClassifications 独立表达。关键词只用于召回；竞对判定必须核查产品商业控制、目标市场和制造/委外/经销/租赁/安装履约模式。

Skills：

- `geto-run-market-research`：用户可见任务编排与国家 progress.md。
- `geto-find-leads`：单公司角色轨道发现。
- `geto-diligence-company`：一家公司一个任务的 ResearchBundle。
- `geto-diligence-inquiry`：一条询盘一个任务的主体核验与交易准备度，不使用 cohort 插补。
- `geto-mine-competitor-customers`：竞对判定与官方案例客户反查。
- `geto-map-relationships`：有证据的 typed relationships[]。
- `geto-assess-precontract-risk`：成熟交易的签约前风险。
- `geto-capability-foundation`：产品、场景、ICP 与 SearchLexicon。

长期客户价值采用两阶段评分：单公司任务提交六维观察输入，国家主任务在同类型样本满足门槛后生成版本化中位数基线并批量评分。询盘准备度使用独立固定口径，可在单条询盘背调完成后立即生成。

验证：

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
```

OmniX 不是研究完成条件。本地验证通过后才询问用户是否通过独立 `omnix-market` Skill 上传完整 Company Aggregate。
