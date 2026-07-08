from pprint import pprint


def fake_llm(data, mode="plan"):
    if mode == "plan":
        return [
            ("parse_source", "parsed"),
            ("summarize", "summary"),
            ("extract_concepts", "concepts"),
            ("build_outline", "outline"),
            ("suggest_next", "next_steps"),
        ]

    if mode == "answer":
        return {
            "summary": data["summary"],
            "concepts": data["concepts"],
            "outline": data["outline"],
            "next_steps": data["next_steps"],
        }

    raise ValueError(f"Unknown mode: {mode}")


def parse_source(state):
    source = state["task"]["source"]
    sentences = [part.strip() for part in source.replace("。", "\n").splitlines()]
    return [sentence for sentence in sentences if sentence]


def summarize(state):
    parsed = state["parsed"]
    if not parsed:
        return "这段资料暂时没有可总结的内容。"

    return "；".join(parsed[:2])


def extract_concepts(state):
    summary = state["summary"]
    concepts = []

    for keyword in ["Agent", "工具", "state", "知识库"]:
        if keyword in summary:
            concepts.append(keyword)

    return concepts or ["资料整理"]


def build_outline(state):
    concepts = state["concepts"]
    return {
        "title": state["task"]["topic"],
        "sections": [
            {"name": concept, "note": f"理解 {concept} 在流程里的作用"}
            for concept in concepts
        ],
    }


def suggest_next(state):
    concepts = state["concepts"]
    return [
        f"用一句话解释：{concept}"
        for concept in concepts
    ]


tools = {
    "parse_source": parse_source,
    "summarize": summarize,
    "extract_concepts": extract_concepts,
    "build_outline": build_outline,
    "suggest_next": suggest_next,
}


def run_tool(action, state):
    return tools[action](state)


def agent(task):
    state = {"task": task}
    plan = fake_llm(task, mode="plan")

    for action, save_as in plan:
        result = run_tool(action, state)
        state[save_as] = result

    answer = fake_llm(state, mode="answer")
    return answer


if __name__ == "__main__":
    task = {
        "topic": "Agent 入门",
        "source": (
            "Agent 会根据任务决定下一步动作。"
            "工具负责执行具体能力。"
            "state 用来保存中间结果。"
            "知识库 Agent 会把资料整理成结构化笔记。"
        ),
    }

    pprint(agent(task), sort_dicts=False)
