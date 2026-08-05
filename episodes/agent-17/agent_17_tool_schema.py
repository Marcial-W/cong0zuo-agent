from pprint import pprint


def search_notes(query: str, top_k: int = 3) -> list[str]:
    """普通 Python 函数：只有代码知道怎么调用它。"""
    notes = [
        "Agent 工具要有名字、说明、参数和返回值。",
        "普通函数只有函数签名，模型看不到适用场景。",
        "工具描述负责告诉模型什么时候可以用这个函数。",
    ]
    return [note for note in notes if query in note][:top_k]


search_notes_tool = {
    "name": "search_notes",
    "description": "从本地笔记里搜索和问题相关的片段。",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "用户问题里最关键的搜索词。",
            },
            "top_k": {
                "type": "integer",
                "description": "最多返回几条片段。",
            },
        },
        "required": ["query"],
    },
}


tool_registry = {
    "search_notes": search_notes,
}


if __name__ == "__main__":
    print("普通函数只告诉代码怎么调用：")
    print(search_notes("工具"))
    print()

    print("工具描述告诉模型什么时候可以调用：")
    pprint(search_notes_tool, sort_dicts=False)
    print()

    print("真正执行时，仍然由代码检查并调用函数：")
    result = tool_registry["search_notes"](query="工具", top_k=2)
    pprint(result)
