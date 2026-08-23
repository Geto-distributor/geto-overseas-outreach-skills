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

`intake → discovery → arbitration → diligence → decision → validation → optional_upload → complete`

主任务在 `progress.md` 为每个检查点记录状态、任务标题、成果路径、接受/拒绝理由、缺口和下一步；任务使用唯一 sectionName 调用 `merge_progress.py` 更新自己的区块。完整任务 trace 留在 Codex 任务自身。

主任务按批次持续执行 wait/read：

- 主动读取每个一级任务 final，不依赖 callback 自动进入上下文；
- final、progress 区块和成果文件分别验收；
- 验证成果路径存在、JSON 可解析、自然公司目录正确且 validator 结果可复现；
- 单次等待目标有工具数量限制时分组执行；
- 运行中或 idle 但尚未读取 final 的任务仍属于未回收；
- 当前批次全部完成或明确需要用户输入后，才进入仲裁、下一批背调或交付。

## 统一回传

每个任务结束时返回：

1. 做了什么；
2. 找到了什么；
3. 成果所在路径；
4. 接受或拒绝理由；
5. 未完成项和缺口；
6. 建议主任务采取的下一步。

Provider 任务另加 provider、queryBoundary、retrievedOn、status 和 ExternalObservation 文件路径。单公司任务另加身份锚点、lead/competitor 分类建议、冲突与 report.md 路径。

## 恢复

恢复时先读 `progress.md`、覆盖矩阵、候选总账和成果文件，再使用任务等待/读取能力获取尚未完成任务的最新状态。仅向需要补证的任务发 follow-up；不重建已完成任务，不无条件重查已完成来源。Provider 已有异步 taskId 时优先恢复状态与结果，不重复提交相同 queryBoundary。

## progress.md 最小结构

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

## 任务
| 任务 | 状态 | 做了什么 | 成果路径 | 接受/拒绝理由 | 缺口 | 下一步 |

## 公司仲裁
| 公司 | lead | competitor | 目录 | 理由/冲突 |

## 上传
- uploadStatus: not_requested
- detailRoute:
```
