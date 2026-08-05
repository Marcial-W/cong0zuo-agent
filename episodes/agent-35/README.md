# Agent 35: keep page citations in answers

`add_chunk_ids()` copies `source_id`, `source_type`, and `page` into every
`CitableChunk` and adds a stable `chunk_id`. `format_citations()` only renders a
page number when the metadata contains one, so missing pages are never invented.

```powershell
python agent_35_citations.py
python -m unittest -v
```

Citation examples:

```text
PDF:      [sample.pdf · p.2]
Markdown: [notes.md]
```
