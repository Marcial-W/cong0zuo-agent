# Agent 36: end-to-end PDF QA with page citations

`answer_pdf_question()` runs the complete loop: safe upload, PDF type check,
`DocumentChunk` parsing, retrieval, answer, citation rendering, and cleanup.

```powershell
python build_qa_samples.py
python agent_36_end_to_end_pdf_qa.py
python -m unittest -v
```

Fixed sample: `sample_qa.pdf` plus the question `Agent 为什么要在回答里保留页码？`
should produce `[sample_qa.pdf · p.2]`. Scanned, empty, invalid, oversized, and
no-match inputs return explicit messages instead of silent success.
