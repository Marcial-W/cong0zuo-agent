from typing import Any


NOTES = [
    "Agent 工具调用分成两步：模型提出工具调用，代码负责检查和执行。",
    "search_notes 可以从本地笔记里找出和用户问题相关的片段。",
    "搜索工具要先找到相关资料片段，再把片段交回回答模型。",
    "tool_result 要回到回答流程里，不能只停留在临时打印结果。",
    "P019 会继续把工具结果写回 state，让 Agent 记住刚刚发生过什么。",
]


def search_notes(query: str, top_k: int = 2) -> list[str]:
    """搜索本地笔记片段，返回最相关的几条结果。"""
    keywords = [word for word in query.replace("，", " ").split() if word]
    scored: list[tuple[int, int, str]] = []

    for index, note in enumerate(NOTES):
        score = sum(1 for keyword in keywords if keyword in note)
        scored.append((score, index, note))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [note for score, _, note in scored[:top_k] if score > 0]


search_notes_tool = {
    "name": "search_notes",
    "description": "从本地笔记里搜索和用户问题相关的片段。",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "用户问题里的搜索关键词。",
            },
            "top_k": {
                "type": "integer",
                "description": "最多返回几条资料片段。",
            },
        },
        "required": ["query"],
    },
}


tool_registry = {
    "search_notes": search_notes,
}


def fake_tool_choice_llm(question: str) -> dict[str, Any]:
    """模拟模型先判断是否需要调用工具。"""
    need_search_words = ["资料", "笔记", "搜索", "检索", "Agent", "工具"]

    if any(word in question for word in need_search_words):
        return {
            "type": "tool_call",
            "name": "search_notes",
            "arguments": {
                "query": "Agent 工具 搜索 资料",
                "top_k": 2,
            },
        }

    return {
        "type": "final_answer",
        "content": "这个问题不需要查资料，可以直接回答。",
    }


def run_tool_call(tool_call: dict[str, Any]) -> list[str]:
    """代码检查工具名和参数，再执行真实函数。"""
    name = tool_call.get("name")
    arguments = tool_call.get("arguments", {})

    if name not in tool_registry:
        return [f"没有找到工具：{name}"]

    query = str(arguments.get("query", "")).strip()
    try:
        top_k = int(arguments.get("top_k", 2))
    except (TypeError, ValueError):
        top_k = 2
    top_k = max(1, min(top_k, 3))

    if not query:
        return ["缺少 query，无法搜索。"]

    tool_func = tool_registry[name]
    return tool_func(query=query, top_k=top_k)


def build_answer_prompt(question: str, tool_result: list[str]) -> str:
    context = "\n".join(f"- {item}" for item in tool_result)
    return f"问题：{question}\n\n刚搜索到的资料：\n{context}"


def fake_answer_llm(prompt: str) -> str:
    """模拟回答模型基于 tool_result 组织最终回答。"""
    return "模拟回答：我会基于刚搜索到的资料回答，而不是直接凭空生成。\n\n" + prompt


def answer_with_search_tool(question: str) -> str:
    decision = fake_tool_choice_llm(question)

    if decision["type"] == "final_answer":
        return decision["content"]

    tool_result = run_tool_call(decision)
    prompt = build_answer_prompt(question, tool_result)
    return fake_answer_llm(prompt)


if __name__ == "__main__":
    user_question = "Agent 工具调用为什么要先搜索资料？"
    print("模型先提出工具调用：")
    print(fake_tool_choice_llm(user_question))
    print()

    print("代码执行后得到回答：")
    print(answer_with_search_tool(user_question))
