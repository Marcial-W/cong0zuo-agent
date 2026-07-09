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
