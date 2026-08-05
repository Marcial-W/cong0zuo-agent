# Agent 32：识别 PDF 空文本与扫描件

本期只增加一个能力：用 `detect_pdf_type()` 检查可提取文本和页面图片信号，避免把扫描型 PDF 静默当成空资料。

```powershell
python -m pip install -r requirements.txt
python make_sample_pdfs.py
python agent_32_detect_pdf_type.py
python -m unittest -v
```

返回类型：

- `text`：存在可提取文本，可直接进入现有问答链路。
- `scanned`：没有文本但存在页面图片，需要 OCR。
- `mixed`：文本页和图片页同时存在，返回 `needs_ocr=true`，提醒仍有图片页待处理。
- `empty_or_unsupported`：既没有文本也没有页面图片，不能武断归类为扫描件。

边界：`ocr_pdf()` 本期只保留显式接口占位，调用会抛出 `NotImplementedError`。本期不安装 OCR 引擎，也不承诺识别准确率。

同页混合限制：如果同一页同时存在可提取文本与图片，当前规则优先将其计为文本页，不识别页面内部的局部扫描区域。
