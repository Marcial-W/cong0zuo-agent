# Agent 37: 什么时候查网页

`choose_source()` 用固定规则决定当前问题应该继续使用本地资料，还是转向网页搜索。

```powershell
python agent_37_choose_source.py
python -m unittest -v
```

返回的 `SourceRoute(source, reason, query, local_match_count, requires_freshness)`
是可测试的结构化状态，不是模糊自然语言。

- 本地有匹配且不要求最新信息：`source=local`
- 明确要求最新信息：`source=web`
- 本地无匹配：`source=web`
- 空问题或非法路由配置：`source=error`
