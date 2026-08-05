# Agent 39: 搜索结果如何清洗

`extract_page()` 接收 P038 的 `SearchResult`，从真实 URL 请求网页，
并用 BeautifulSoup 清除导航、页脚、广告、重复菜单等明显噪声，输出稳定的
`PageExtraction(status, url, title, summary, body_text, source_type, http_status, content_type, message)`。

```powershell
python -m unittest -v
python smoke_test_extract_page.py
```

- `snippet` 只是搜索摘要，不会被写入正文字段。
- 失败状态：`invalid_url`、`timeout`、`http_error`、`empty`、`not_html`、`parse_error`。
- 自动测试使用固定 HTML fixture 和注入 transport，不依赖每次联网。
- `smoke_test_extract_page.py` 是单独的真实联网证据，普通测试不调用它。
- 本项目不做浏览器自动化，也不承诺支持登录页、付费墙、复杂 JavaScript 渲染页面。

成功提取后可调用 `to_page_evidence()` 转成 P040 评分使用的
`PageEvidence(evidence_id, title, url, summary, body_text, source_type, source_quality, published_at, claim, extracted_at)`。
