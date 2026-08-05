# Agent 38: 怎样接入真实网页搜索

`web_search()` 调用真实 Wikipedia Search API，并把结果标准化为
`SearchResult(title, url, snippet, source_type="web", rank)`。

```powershell
python agent_38_web_search.py
python smoke_test_web_search.py
python -m unittest -v
```

- 默认自动测试使用注入 transport，不依赖每次联网。
- `smoke_test_web_search.py` 是单独的真实联网证据。
- HTTP 错误、超时、空结果和非法返回分别返回
  `http_error`、`timeout`、`empty`、`invalid`。
- 接口的 `timestamp` 是页面最后编辑时间，不作为 `published_at` 使用。

合并演示：

```powershell
python agent_38_route_search_demo.py
```
