# 询盘报告可选发布合同

## 1. 默认停止点

询盘背调的默认第一交付是经验证的 `report.md`。向用户提供 Markdown 路径并请求审阅内容、章节、评分、结论和语气；此时不自动生成 DOCX/PDF。

## 2. 进入发布的条件

仅在以下任一条件满足时进入：

1. 用户明确确认 Markdown 内容无问题并要求生成发布文件；
2. 用户明确要求跳过 Review，直接生成指定格式。

不得把用户仅要求“开展背调”“出报告”解释为默认需要 PDF。PDF 是可选发布物，不是研究完成条件。

## 3. 内容冻结记录

进入发布前，在 `<公司目录>/Additional/report-review.json` 保存：

```json
{
  "status": "approved",
  "reportPath": "report.md",
  "reportSha256": "<approved report.md SHA-256>",
  "reviewedOn": "YYYY-MM-DD",
  "reviewedBy": "user",
  "instructionRef": "User explicitly approved the Markdown report for publication."
}
```

允许状态：

- `approved`：用户审阅并确认；
- `review_skipped_by_user`：用户明确要求跳过 Review。

`instructionRef` 只写简短授权事实，不保存敏感聊天内容。报告修改后 SHA-256 变化，原确认失效，必须重新 Review 或由用户再次明确跳过。

## 4. 格式选择

只生成用户要求的格式：DOCX、PDF、DOCX + PDF 或其他格式。没有要求 PDF 时不生成 PDF。

如果用户提供参考文档，只把它视为版式、章节组织和表达风格参考；不得把参考文档中的公司事实、结论或说明复制到目标报告。

## 5. 单一内容来源

DOCX/PDF 必须从已确认的 `report.md` 派生，不维护第二套独立事实文本。发布阶段发现内容错误时，先返回修改 `company.json`、Evidence、Sources 和 Markdown，再重新确认和生成。

## 6. 生成与验收

生成 DOCX 时遵循 `$documents`；生成或检查 PDF 时遵循 `$pdf`。使用能够稳定显示中文的渲染路径；LibreOffice 出现丢字、方框或错误替代时，改用 Pages 等可靠原生引擎，不交付已知损坏文件。

交付前必须：

- 比较 Markdown 与 DOCX/PDF 的标题、结论、评分、表格和下一步；
- 渲染全部页面并检查封面、目录、章节、分页、页眉页脚和来源；
- 检查中文字体、方框、裁切、重叠、空白异常和表格跨页；
- 对 PDF 进行文本抽取，确认可搜索且关键文字没有丢失；
- 扫描内部状态码和未汉化术语；
- 只把验证通过的文件写入 `reportFiles[]`。

运行发布门禁：

```bash
python '<geto-diligence-inquiry-dir>/scripts/validate_publication_gate.py' \
  '<公司目录>'
```

## 7. 版本管理

- 不覆盖原始询盘、Evidence 和旧版研究工件；
- 内容修改后更新版本名或生成日期；
- 同一版本的 DOCX/PDF 内容必须一致；
- 告知用户生成了哪些格式、哪些未生成，以及 Review 状态。
