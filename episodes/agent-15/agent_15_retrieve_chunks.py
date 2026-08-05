from typing import Any


def split_text(text: str, max_chars: int = 120) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    chunks: list[str] = []
    current = ""

    for line in lines:
        if len(current) + len(line) > max_chars and current:
            chunks.append(current)
            current = line
        else:
            current = (current + "\n" + line).strip()

    if current:
        chunks.append(current)

    return chunks


def score_chunk(query: str, chunk: str) -> int:
    keywords = [word for word in query.replace("，", " ").split() if word]
    return sum(1 for keyword in keywords if keyword in chunk)


def retrieve_chunks(query: str, text: str, top_k: int = 2) -> list[dict[str, Any]]:
    chunks = split_text(text)
    scored = [
        {"chunk": chunk, "score": score_chunk(query, chunk)}
        for chunk in chunks
    ]

    scored.sort(key=lambda item: item["score"], reverse=True)
    return [item for item in scored[:top_k] if item["score"] > 0]


if __name__ == "__main__":
    source = """
    Agent 会围绕任务拆步骤。
    工具负责执行具体动作，比如读取文件、搜索资料。
    state 用来保存中间结果。
    检索会先从资料里找到和问题相关的片段。
    """

    results = retrieve_chunks("Agent 检索", source)
    for item in results:
        print("score:", item["score"])
        print(item["chunk"])
