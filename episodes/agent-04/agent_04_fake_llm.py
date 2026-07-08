def fake_llm(data, mode="plan"):
    if mode == "answer":
        return "最终回答：" + data["summary"]

    return {
        "action": "extract",
        "input": data,
        "reason": "先提取资料重点",
    }


def extract_notes(text):
    return {
        "summary": "这段资料说明了 Agent 会围绕任务调用工具并循环执行。",
        "keywords": ["Agent", "工具", "循环"],
    }


tools = {"extract": extract_notes}


def run_tool(plan):
    return tools[plan["action"]](plan["input"])


if __name__ == "__main__":
    task = "整理这段资料：Agent 会根据任务决定下一步，并调用工具完成任务。"

    plan = fake_llm(task)
    result = run_tool(plan)
    answer = fake_llm(result, mode="answer")

    print(answer)
