# Agent 33: unify Markdown and PDF chunks

This episode adds one capability: both source adapters return the same
`DocumentChunk(source_id, source_type, page, text)` contract. The retriever only
accepts `list[DocumentChunk]`, so it does not branch on file type.

```powershell
python -m pip install -r requirements.txt
python agent_33_document_chunks.py
python -m unittest -v
```

Boundary: Markdown uses `page=None`; PDF keeps one-based page numbers. Upload
validation is deferred to Agent 34, and answer citations are deferred to Agent 35.
