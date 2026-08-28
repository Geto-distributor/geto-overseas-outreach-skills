# 用户可见任务编排

## 拓扑

- 当前完整国家调研任务是主任务。
- Web 发现按六个 companyRole 分为六个用户可见任务。
- 竞对发现按产品/技术面和商业角色拆任务。
- TradeWind、网易外贸通各自一个独立任务。
- 一条线索使用一个 `$geto-diligence-company` 任务；一家竞对使用一个 `$geto-diligence-competitor` 任务。
- 需要研究 confirmed 竞对的客户关系、切入分或组合价值时，每家竞对使用一个 `$geto-mine-competitor-customers` 任务；需要长期价值评分的 verified_customer 仍由自己的单公司任务维护事实和六维评分。
- 一条明确原始询盘使用一个 `$geto-diligence-inquiry` 任务；同一公司的长期价值观察输入仍归入其 Company，不重复建主体。
- subagent 只在单个任务内部并行网页、法规、项目或反证轨。

每个一级任务提示包含 parentTaskId、准确标题、queryBoundary、成果目录、唯一 sectionName 和禁止重复查询清单。任务完成时先调用 `merge_progress.py`，再向 parentTaskId 发送精简 callback；无法 callback 时在 final 明确标记 callback_failed。

## 状态机

`intake → discovery → research_frontier → arbitration → diligence → review → decision → synthesis → validation → local_complete`

只有用户明确要求 OmniX 时，才从 `local_complete` 进入 `optional_upload`。评分、Provider 和平台状态各自记录，不替代本地研究状态。

主任务在 `progress.md` 为每个检查点记录状态、任务标题、成果路径、接受/拒绝理由、缺口和下一步；任务使用唯一 sectionName 调用 `merge_progress.py` 更新自己的区块。完整任务 trace 留在 Codex 任务自身。

主任务按批次持续执行 wait/read：

- 主动读取每个一级任务 final，不依赖 callback 自动进入上下文；
- final、progress 区块和成果文件分别验收；
- 验证成果路径存在、JSON 可解析、自然公司目录正确且 validator 结果可复现；
- 按 `research-intelligence-contract.md` 与 `diligence-review-contract.md` 对信息广度、重点路径深度、关联扩展、来源使用、AI 推理、官网、社媒、项目、Provider、采购链和分类进行独立审校；只对影响主要结论的事实做定向反向核查；
- TradeWind Agentic 第一次 submit 前先读取并挑战 Provider plan；范围不全、意图混合、缺 pilot 或任务边界重复时退回 Provider 任务，不批准付费提交；
- 单公司 final 只把任务状态改为已回收，不自动把 diligenceReviewStatus 改为 accepted；
- 有可补救缺口时向原任务发送具体 follow-up，等待其更新原工件和唯一 progress section，再重新审查；
- 单次等待目标有工具数量限制时分组执行；
- 运行中或 idle 但尚未读取 final 的任务仍属于未回收；
- 当前批次全部完成或明确需要用户输入后，才进入仲裁、下一批背调或交付。

每回收一批任务都更新研究前沿，跨公司归并反复出现的公司、项目、产品、供应商、客户、渠道和人员。主任务根据它们对市场理解的增量选择下一批，不把“任务全部回收”自动等同研究完成。

## 统一回传

每个任务结束时返回：

1. 做了什么；
2. 找到了什么；
3. 成果所在路径；
4. 接受或拒绝理由；
5. AI 当前结论及推理摘要；
6. 新发现的关联对象和信息边界；
7. 建议主任务采取的下一跳。

Provider 任务另加 provider、queryBoundary、retrievedOn、status、信号用途限制和 ExternalObservation 文件路径。单公司任务另加身份锚点、lead/competitor 分类建议、冲突、report.md 路径、事实/信号/推理/结论摘要、值得扩展的下一跳，以及官网、社媒、项目、外部交叉和 Provider 的 `exhaustive|bounded|partial|not_queried|not_applicable` 覆盖摘要。

## 恢复

恢复时先读 `progress.md`、覆盖矩阵、候选总账、diligence-review.json 和成果文件，再使用任务等待/读取能力获取尚未完成任务的最新状态。任务 final 已回收但 review 未通过时仍属于未完成；向原任务发送审查中的具体 follow-up，不重建已完成任务，不无条件重查已完成来源。Provider 已有异步 taskId 时优先恢复状态与结果，不重复提交相同 queryBoundary。

## progress.md 最小结构

### 财务结构化补证增量 section

财务补证属于已有国家 ResearchBundle 的增量验收，不重新创建国家主任务或重复派发已完成公司任务。统一沿用 `financial_structure_supplement_<iso2>_<yyyymmdd>`，在同一 section 记录补证范围、公司目录、subjectEntity、scope/accountingScope/relationshipToTarget、period、valueStatus、Evidence、实体 mismatch、未披露字段和下一步。国家主任务独立复核 company.json、report.md、Sources 和 validator；回传 final 不能直接替代验收。

目标法人单体、母公司/集团、品牌、JV、SPV 或分部记录必须保留真实主体和口径；实体不匹配不删除也不改名。商业数据库仅作为 secondary 记录。capitalRecords 与 financialRecords 永久隔离，注册资本/实缴资本不得作为收入、资产、现金、授信或付款能力。

```markdown
# <国家> GETO 市场调研进度

## 范围
- 国家：
- 产品：
- 语言：
- 截止日：
- 结果范围：

## 检查点
| 阶段 | 状态 | 成果路径 | 缺口 | 下一步 |

## 研究前沿
| 节点/问题 | 来源公司或任务 | 为什么重要 | 当前证据强度 | 下一跳 | 状态 |

## 任务
| 任务 | 状态 | 做了什么 | 成果路径 | 接受/拒绝理由 | 缺口 | 下一步 |

## 公司仲裁
| 公司 | lead | competitor | 背调任务 | 背调验收 | reviewCycle | 目录 | 理由/冲突 |

## AI 市场综合
- 事实底座：
- 关键信号：
- AI 推理：
- AI 结论：
- 不确定性：
- 继续研究方向：

## 可选上传
- uploadStatus: not_requested
- detailRoute:
```
