task = "整理一段资料"

plan = model.plan(task)
tool_result = run_tool(plan.tool, plan.input)
answer = model.summarize(task, tool_result)
