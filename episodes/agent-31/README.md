# Agent 31：读取文本型 PDF

本期只增加一个能力：用 `read_pdf()` 逐页提取文本，并保留从 1 开始的页码。

```powershell
python -m pip install -r requirements.txt
python make_sample_pdf.py
python agent_31_read_pdf.py
python -m unittest -v
```

返回结构：

```json
{
  "source_id": "sample_agent_notes.pdf",
  "page": 1,
  "text": "..."
}
```

边界：`pypdf` 只能提取 PDF 中已有的文本层。本期不做扫描件 OCR；空文本识别与 OCR fallback 留到 Agent 32。
