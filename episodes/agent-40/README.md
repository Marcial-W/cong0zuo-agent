# Agent 40: 证据评分与冲突保留

`score_evidence()` 对 P039 的 `PageEvidence` 做确定性评分，并返回
`EvidenceScoringResponse(status, evidence, conflict_status, message)`。

```powershell
python -m unittest -v
python agent_40_evidence_demo.py
```

评分权重固定为：

```text
score = 0.4 * source_quality + 0.3 * freshness + 0.3 * task_relevance
```

- 来源质量：`official=1.0`、`reference=0.7`、`general=0.4`、`unknown=0.0`。
- 新鲜度：缺少或非法 `published_at` 为 `0.0`；365 天内 `1.0`；1095 天内 `0.5`；更早 `0.2`。
- 任务相关性：全部关键词匹配 `1.0`、部分匹配 `0.6`、无匹配 `0.2`。
- 冲突状态：`no_conflict`、`conflict`、`undetermined`、`insufficient_evidence`。
- 冲突时保留全部证据，不静默丢弃低分来源，也不自动判断谁正确。
- 评分是启发规则，不是真实性认证；`reason` 字段解释每个分数来源。

固定演示：

```text
fixture-a: official + 2026-01-01 + claim=local -> score=1.0
fixture-b: general + no date + claim=utc -> score=0.46
conflict_status=conflict
```
