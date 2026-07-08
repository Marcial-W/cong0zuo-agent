task = "整理一份 Agent 入门笔记"

plan = llm.plan(task)
tool_result = run_tool(plan.tool, plan.input)
answer = llm.summarize(task, tool_result)

print(answer)
