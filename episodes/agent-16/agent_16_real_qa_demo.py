import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable


def fake_llm(prompt: str) -> str:
    return (
        "模拟回答：可以先读取本地 Markdown，再检索相关片段，"
        "最后把问题和片段一起交给 llm_adapter。"
    )


def api_llm(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 OPENAI_API_KEY。")

    return "真实 API 占位：脚本定稿前需要确认 SDK 版本、模型名和请求写法。"


def llm_adapter(prompt: str) -> str:
    if os.getenv("AGENT_USE_REAL_API") != "1":
        return fake_llm(prompt)
    return api_llm(prompt)


def safe_call_llm(
    prompt: str,
    llm_func: Callable[[str], str],
    fallback_func: Callable[[str], str] = fake_llm,
    timeout_seconds: float = 3,
) -> str:
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(llm_func, prompt)
            return future.result(timeout=timeout_seconds)
    except Exception as error:
        return fallback_func(prompt) + f"\n备用原因：{error}"


def read_markdown(file_path: str | Path) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def split_text(text: str, max_chars: int = 140) -> list[str]:
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


def retrieve_chunks(query: str, text: str, top_k: int = 2) -> list[str]:
    keywords = [word for word in query.replace("，", " ").split() if word]
    chunks = split_text(text)
    scored = []

    for chunk in chunks:
        score = sum(1 for keyword in keywords if keyword in chunk)
        scored.append((score, chunk))

    scored.sort(reverse=True)
    return [chunk for score, chunk in scored[:top_k] if score > 0]


def build_prompt(question: str, chunks: list[str]) -> str:
    context = "\n\n".join(chunks) if chunks else "没有检索到相关片段。"
    return f"请根据资料回答问题。\n\n问题：{question}\n\n资料片段：\n{context}"


def answer_question(question: str, file_path: str | Path) -> str:
    markdown = read_markdown(file_path)
    chunks = retrieve_chunks(question, markdown)
    prompt = build_prompt(question, chunks)
    return safe_call_llm(prompt, llm_adapter)


if __name__ == "__main__":
    notes_path = Path(__file__).with_name("sample_notes.md")
    question = "Agent 为什么要先检索相关片段？"
    print(answer_question(question, notes_path))
