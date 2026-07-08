# Agent 01：什么是 Agent

本期用一个最小伪代码说明 Agent 的基本结构：

1. 用户给出任务。
2. 模型根据任务生成计划。
3. Agent 调用工具执行计划。
4. 模型把任务和工具结果总结成答案。

对应代码：

- `agent_01_minimal_pseudocode.py`
