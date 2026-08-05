from typing import Any

NOTES = [
    "Agent 工具调用分成两步：模型提出工具调用，代码负责检查和执行。",
    "tool_result 要写回 state，后面的回答才能读取同一份运行记录。",
    "state 可以记录问题、工具调用、工具结果和最终回答。",
]


def fake_tool_choice_llm(question: str) -> dict[str, Any]:
    """沿用 P018 的最小工具选择结果。"""
    return {
        "type": "tool_call",
        "name": "search_notes",
        "arguments": {"query": question, "top_k": 2},
    }


def run_tool_call(tool_call: dict[str, Any]) -> dict[str, Any]:
    """沿用 P018 的执行边界，这里只保留最小搜索示例。"""
    query = str(tool_call.get("arguments", {}).get("query", "")).strip()
    if not query:
        return {"status": "error", "content": ["缺少 query，无法搜索。"]}

    keywords = [word for word in query.replace("，", " ").split() if word]
    matches = [note for note in NOTES if any(word in note for word in keywords)]
    return {"status": "success", "content": (matches or NOTES)[:2]}


def fake_answer_llm(prompt: str) -> str:
    return "模拟回答：我会基于 state 里的工具结果回答。\n\n" + prompt


def create_state(question: str) -> dict[str, Any]:
    """为一次 Agent 运行创建统一状态。"""
    return {
        "question": question,
        "tool_calls": [],
        "tool_results": [],
        "answer": None,
    }


def append_tool_result(
    state: dict[str, Any],
    tool_call: dict[str, Any],
    tool_output: dict[str, Any],
) -> None:
    """把工具调用和结果作为一条可检查记录写回 state。"""
    state["tool_calls"].append(tool_call)
    state["tool_results"].append(
        {
            "name": tool_call["name"],
            "arguments": tool_call.get("arguments", {}),
            "status": tool_output["status"],
            "content": tool_output["content"],
        }
    )


def build_prompt_from_state(state: dict[str, Any]) -> str:
    """回答阶段只从 state 读取问题和工具结果。"""
    context_lines = [
        item
        for record in state["tool_results"]
        for item in record["content"]
    ]
    context = "\n".join(f"- {item}" for item in context_lines)
    return f"问题：{state['question']}\n\n工具刚查到的资料：\n{context}"


def answer_from_state(state: dict[str, Any]) -> str:
    prompt = build_prompt_from_state(state)
    state["answer"] = fake_answer_llm(prompt)
    return state["answer"]


def run_agent(question: str) -> dict[str, Any]:
    state = create_state(question)
    decision = fake_tool_choice_llm(question)

    if decision["type"] == "final_answer":
        state["answer"] = decision["content"]
        return state

    tool_output = run_tool_call(decision)
    append_tool_result(state, decision, tool_output)
    answer_from_state(state)
    return state


if __name__ == "__main__":
    final_state = run_agent("Agent 为什么要把工具结果写回 state？")
    print(final_state)
