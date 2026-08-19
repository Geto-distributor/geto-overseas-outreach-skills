# 用户可见任务编排

## 拓扑

- 当前完整国家调研任务是主任务。
- Web 发现按六个 companyRole 分为六个用户可见任务。
- 竞对发现按产品/技术面和商业角色拆任务。
- TradeWind、网易外贸通各自一个独立任务。
- 一家公司一个背调任务；一个竞对也使用一家公司一个任务。
- subagent 只在单个任务内部并行网页、法规、项目或反证轨。

## 状态机

`intake → discovery → arbitration → diligence → decision → validation → optional_upload → complete`

主任务在 `progress.md` 为每个检查点记录状态、任务标题、成果路径、接受/拒绝理由、缺口和下一步；任务使用唯一 sectionName 调用 `merge_progress.py` 更新自己的区块。完整任务 trace 留在 Codex 任务自身。

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

恢复时先读 `progress.md` 和成果文件，再使用任务等待/读取能力获取尚未完成任务的最新状态。仅向需要补证的任务发 follow-up；不重建已完成任务，不无条件重查已完成来源。

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
