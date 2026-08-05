# Agent 21：本地文件 MCP 怎么接

## 环境

- Python 3.10 及以上
- MCP Python SDK 稳定版 v1：`mcp>=1.28,<2`

## 运行

在本目录执行：

```powershell
uv run --python (Get-Command python).Source --with "mcp>=1.28,<2" python agent_21_client.py
```

如果 `python` 指向 3.9 或更早版本，请把 `--python` 后面的值换成 Python 3.10+ 的实际路径。

运行后应看到：

```text
发现工具： ['read_note']
MCP 结果已写回 state：
```

## 文件

- `agent_21_file_server.py`：只读本地 Markdown 的 MCP server。
- `agent_21_client.py`：通过 stdio 初始化、发现并调用工具。
- `notes/mcp-notes.md`：演示笔记。

本示例只允许读取 `notes/` 目录内的 `.md` 文件，不提供写入、编辑、移动或删除能力。

为了单独验证 MCP 连接，本期由 Host 侧代码手动指定 `read_note`，不加入模型决策。结果写入 `state["tool_results"]`，`answer` 保持 `None`，回答阶段留在既有 Agent 主线中。
