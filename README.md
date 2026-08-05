# 从 0 做 Agent 系列代码

这个仓库是抖音账号「Marcial 的 Agent 实验室」中《从 0 做 Agent》系列视频的配套代码仓库。

系列目标不是一上来做一个复杂框架，而是把 Agent 的核心结构拆成一小段一小段可以理解、可以运行、可以改造的代码：任务、模型、工具、状态、输出展示，以及后续接入真实 API 的准备工作。

仓库地址：

```text
https://github.com/Marcial-W/cong0zuo-agent
```

## 适合谁

- 刚开始学习 Agent，不想先被框架和工程配置淹没的人。
- 想看懂 Agent 的基本执行链路：`task -> plan -> tool -> state -> answer`。
- 想从一个最小知识库 Agent 项目开始，慢慢加上真实 LLM、网页读取、本地文件读取和前端展示的人。

## 当前进度

这个仓库会随着视频更新逐步补齐。每一期尽量只保留一个最小示例，方便对照视频理解。

| 集数 | 主题 | 文件 | 说明 |
|------|------|------|------|
| Agent 01 | 什么是 Agent | `episodes/agent-01/agent_01_minimal_pseudocode.py` | 概念伪代码，用来理解基本流程。 |
| Agent 02 | Agent 和 ChatGPT 的区别 | 暂无独立代码 | 这一期偏概念讲解，后续如有示例会补入。 |
| Agent 03 | 一个最小 Agent 需要哪些部分 | `episodes/agent-03/agent_03_minimal_agent_shape.py` | 概念片段，展示最小 Agent 形状。 |
| Agent 04 | 写 Agent 前先做一个模拟 LLM | `episodes/agent-04/agent_04_fake_llm.py` | 可运行的 Python 示例。 |
| Agent 05 | 最小知识库 Agent 伪代码 | `episodes/agent-05/agent_05_pseudocode.py` | 可运行的 Python 示例，开始引入 state。 |
| Agent 06 | 让 Agent 整理一段本地资料 | `episodes/agent-06/agent_06_local_notes.py` | 可运行的 Python 示例，把本地资料整理成结构化结果。 |
| Agent 07 | Agent 结果别只打印在终端 | `episodes/agent-07/agent_07_notion_page.html` | 可直接打开的 HTML 页面示例。 |
| Agent 08 | 思维框架图 | `episodes/agent-08/agent_08_mind_map.html` | 可直接打开的 HTML 页面示例。 |
| Agent 11 | 第一版真实 API 适配器 | `episodes/agent-11/agent_11_llm_adapter.py` | 用适配器保留 fake fallback。 |
| Agent 12 | 固定字段约束 | `episodes/agent-12/agent_12_validate_result.py` | 校验 `summary / concepts / outline`。 |
| Agent 13 | API 失败不中断 | `episodes/agent-13/agent_13_safe_call_llm.py` | 加超时、fallback 和错误信息。 |
| Agent 14 | 读取本地 Markdown | `episodes/agent-14/agent_14_read_markdown.py` | 最小文件读取工具。 |
| Agent 15 | 最小本地检索 | `episodes/agent-15/agent_15_retrieve_chunks.py` | 用关键词和分段检索讲清 RAG 前置逻辑。 |
| Agent 16 | 第一次真实资料问答 | `episodes/agent-16/agent_16_real_qa_demo.py` | 串起读取、检索、prompt 和模型入口。 |
| Agent 17 | 什么才算 Agent 的工具 | `episodes/agent-17/agent_17_tool_schema.py` | 展示普通函数、工具描述和执行边界。 |
| Agent 18 | 给知识库 Agent 加一个搜索工具 | `episodes/agent-18/agent_18_search_tool_call.py` | 模拟模型提出 tool call，代码检查并执行搜索工具。 |
| Agent 19 | 工具调用结果写回 state | `episodes/agent-19/agent_19_tool_result_state.py` | 把工具调用与结果保存到统一运行状态。 |
| Agent 21 | 本地文件 MCP 怎么接 | `episodes/agent-21/agent_21_file_server.py`、`agent_21_client.py` | 用 stdio 完成最小 MCP 连接，并把只读文件结果写回 state。 |
| Agent 31 | 让知识库 Agent 读取 PDF | `episodes/agent-31/agent_31_read_pdf.py` | 用 pypdf 逐页提取文本，并保留 `source_id / page / text`。 |
| Agent 32 | 为什么有些 PDF 读出来是空的 | `episodes/agent-32/agent_32_detect_pdf_type.py` | 区分文本页、图片页和混合 PDF，明确 OCR fallback 边界。 |
| Agent 33 | Markdown 和 PDF 怎么进入同一条链路 | `episodes/agent-33/agent_33_document_chunks.py` | 统一 `DocumentChunk(source_id, source_type, page, text)` 并共用检索入口。 |
| Agent 34 | 网页上传的文件应该先放哪里 | `episodes/agent-34/agent_34_save_upload.py` | 白名单、大小限制、临时目录、安全文件名和清理流程。 |
| Agent 35 | Agent 回答怎么带上 PDF 页码 | `episodes/agent-35/agent_35_citations.py` | 用 `chunk_id` 保留来源，回答只展示真实页码引用。 |
| Agent 36 | 第一次真实 PDF 问答 | `episodes/agent-36/agent_36_end_to_end_pdf_qa.py` | 串起上传、校验、解析、检索、回答、引用和清理。 |
| Agent 37 | 什么时候应该查网页 | `episodes/agent-37/agent_37_choose_source.py` | 用可测试规则把问题路由到本地资料或网页搜索。 |
| Agent 38 | 怎样接入真实网页搜索 | `episodes/agent-38/agent_38_web_search.py` | 调用真实搜索接口，把结果标准化为 `SearchResult` 并明确失败状态。 |

## 目录结构

```text
cong0zuo-agent/
  README.md
  episodes/
    agent-01/
      agent_01_minimal_pseudocode.py
    agent-03/
      agent_03_minimal_agent_shape.py
    agent-04/
      agent_04_fake_llm.py
    agent-05/
      agent_05_pseudocode.py
    agent-06/
      agent_06_local_notes.py
    agent-07/
      agent_07_notion_page.html
    agent-17/
      agent_17_tool_schema.py
    agent-18/
      agent_18_search_tool_call.py
```

后续如果某一期需要更完整的运行环境，会再增加：

```text
examples/   # 更完整、可复用的示例
docs/       # 补充说明、概念图和运行记录
```

## 快速运行

Python 示例不依赖第三方库，直接用 Python 3.10+ 运行即可。

```bash
python episodes/agent-04/agent_04_fake_llm.py
python episodes/agent-05/agent_05_pseudocode.py
python episodes/agent-06/agent_06_local_notes.py
python episodes/agent-17/agent_17_tool_schema.py
python episodes/agent-18/agent_18_search_tool_call.py
python episodes/agent-31/make_sample_pdf.py
python episodes/agent-31/agent_31_read_pdf.py
python episodes/agent-32/make_sample_pdfs.py
python episodes/agent-32/agent_32_detect_pdf_type.py
python episodes/agent-33/agent_33_document_chunks.py
python episodes/agent-34/agent_34_save_upload.py
python episodes/agent-35/agent_35_citations.py
python episodes/agent-36/build_qa_samples.py
python episodes/agent-36/agent_36_end_to_end_pdf_qa.py
python episodes/agent-37/agent_37_choose_source.py
python episodes/agent-38/agent_38_web_search.py
python episodes/agent-38/agent_38_route_search_demo.py
```

`agent-38` 的自动测试使用注入 transport，不依赖每次联网；需要查看真实搜索证据时单独运行：

```bash
python episodes/agent-38/smoke_test_web_search.py
```

HTML 示例可以直接用浏览器打开：

```text
episodes/agent-07/agent_07_notion_page.html
```

也可以在仓库根目录启动一个本地静态服务：

```bash
python -m http.server 8000
```

然后访问：

```text
http://localhost:8000/episodes/agent-07/agent_07_notion_page.html
```

## 学习路线

建议按下面顺序看代码：

1. 先看 Agent 01 / 03：只理解 Agent 最小结构，不纠结能不能运行。
2. 再跑 Agent 04：用 `fake_llm` 代替真实大模型，先把流程跑通。
3. 再跑 Agent 05 / 06：理解 `state` 如何保存中间结果，以及工具函数如何串起来。
4. 最后看 Agent 07：理解后端结构化结果如何变成可读页面。

这条路线的重点是先把项目骨架跑顺，再考虑真实 API、向量库、网页读取、PDF 读取等更重的能力。

## 设计原则

- 每期代码尽量小，不追求一次写成完整框架。
- 优先使用标准库，减少环境配置成本。
- 函数名和变量名尽量贴近视频里的讲解词：`task`、`plan`、`tools`、`state`、`answer`。
- 先用模拟 LLM 跑通流程，再替换成真实 API。
- 输出结果先结构化，再考虑做成页面、图谱或对话界面。

## 后续计划

- 补齐每一期的代码说明。
- 增加 `examples/`，放更接近完整项目的示例。
- 增加 `docs/`，整理 Agent 项目结构、README 写法和接入真实 API 的注意事项。
- 从 `fake_llm` 升级到真实 LLM API。
- 增加网页、本地 Markdown、PDF 等资料来源。

## 说明

这个仓库是一个学习型项目，不是开箱即用的生产级 Agent 框架。代码会优先服务于视频讲解的清晰度，所以有些文件会故意保持得很短。

如果你正在跟着视频做，建议每次只改一个文件、只验证一个动作。Agent 项目最容易变乱的地方，不是代码少，而是一次想加太多能力。
