from __future__ import annotations

from typing import Any, Callable


SOURCE = """
Agent 可以围绕一个目标拆步骤，调用工具，保存中间结果，
最后把结果整理成可读答案。
如果先固定输入和输出，就更容易调试每一个工具函数。
"""


def parse_source(state: dict[str, Any]) -> str:
    text = state["task"]["source"]
    parts = text.replace("。", "\n").splitlines()
    lines = [line.strip() for line in parts]
    return "。".join(line for line in lines if line)


def summarize(state: dict[str, Any]) -> str:
    parsed = state["parsed"]
    first_sentence = parsed.split("。")[0].rstrip("，,。")
    return first_sentence + "。"


def extract_concepts(state: dict[str, Any]) -> list[str]:
    parsed = state["parsed"]
    concepts: list[str] = []
    keyword_map = {
        "目标": "目标",
        "工具": "工具",
        "中间结果": "state",
        "答案": "answer",
    }
    for keyword, concept in keyword_map.items():
        if keyword in parsed and concept not in concepts:
            concepts.append(concept)
    return concepts


def build_outline(state: dict[str, Any]) -> dict[str, Any]:
    concepts = state["concepts"]
    return {
        "主题": state["task"]["topic"],
        "一级结构": [
            f"理解 {concept} 在流程里的作用"
            for concept in concepts
        ],
        "关键概念": concepts,
    }


def format_answer(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": state["summary"],
        "concepts": state["concepts"],
        "outline": state["outline"],
    }


TOOLS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "parse_source": parse_source,
    "summarize": summarize,
    "extract_concepts": extract_concepts,
    "build_outline": build_outline,
}


def fake_llm(_: dict[str, Any], mode: str = "plan") -> list[tuple[str, str]]:
    if mode != "plan":
        raise ValueError(f"Unsupported mode: {mode}")
    return [
        ("parse_source", "parsed"),
        ("summarize", "summary"),
        ("extract_concepts", "concepts"),
        ("build_outline", "outline"),
    ]


def run_tool(action: str, state: dict[str, Any]) -> Any:
    return TOOLS[action](state)


def agent(task: dict[str, str]) -> dict[str, Any]:
    state: dict[str, Any] = {"task": task}
    plan = fake_llm(state, mode="plan")

    for action, save_as in plan:
        result = run_tool(action, state)
        state[save_as] = result

    return format_answer(state)


if __name__ == "__main__":
    task = {
        "topic": "Agent 入门",
        "source": SOURCE,
    }
    answer = agent(task)
    print("summary:", answer["summary"])
    print("concepts:", " / ".join(answer["concepts"]))
    print("outline:")
    for item in answer["outline"]["一级结构"]:
        print("-", item)
