# Agent 34: save uploads safely

`save_upload()` validates the extension and byte size, then writes the upload to
a generated filename inside a temporary directory. The parser never receives an
arbitrary local path from the user.

```powershell
python agent_34_save_upload.py
python -m unittest -v
```

Boundary: only `.pdf` is allowed and the maximum size is 10 MiB. Invalid files
are rejected before a temporary directory is created; `cleanup_upload()` removes
the file and directory after parsing.
