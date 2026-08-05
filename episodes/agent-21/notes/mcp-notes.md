# MCP 本地笔记

MCP client 先初始化连接，再发现 server 暴露的能力。

本期只调用只读工具 `read_note`，并把返回内容写回 Agent 的 `state`。

目录范围、文件类型和路径校验都由 server 负责。
