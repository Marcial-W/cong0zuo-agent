from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Literal

from pypdf import PdfReader


@dataclass(frozen=True)
class DocumentChunk:
    source_id: str
    source_type: Literal["markdown", "pdf"]
    page: int | None
    text: str


def split_text(text: str, max_chars: int = 120) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    chunks: list[str] = []
    current = ""

    for line in lines:
        if current and len(current) + 1 + len(line) > max_chars:
            chunks.append(current)
            current = line
        else:
            current = "\n".join(part for part in (current, line) if part)

    if current:
        chunks.append(current)
    return chunks


def chunks_from_markdown(file_path: str | Path) -> list[DocumentChunk]:
    path = Path(file_path)
    if path.suffix.lower() != ".md":
        raise ValueError("只支持 Markdown 文件。")
    if not path.is_file():
        raise FileNotFoundError(f"Markdown 不存在：{path}")

    return [
        DocumentChunk(path.name, "markdown", None, text)
        for text in split_text(path.read_text(encoding="utf-8"))
    ]


def chunks_from_pdf(file_path: str | Path) -> list[DocumentChunk]:
    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        raise ValueError("只支持 PDF 文件。")
    if not path.is_file():
        raise FileNotFoundError(f"PDF 不存在：{path}")

    chunks: list[DocumentChunk] = []
    for page_number, page in enumerate(PdfReader(path).pages, start=1):
        for text in split_text(page.extract_text() or ""):
            chunks.append(DocumentChunk(path.name, "pdf", page_number, text))
    return chunks


def retrieve_chunks(
    query: str, chunks: list[DocumentChunk], top_k: int = 2
) -> list[DocumentChunk]:
    keywords = [word.lower() for word in query.replace("，", " ").split() if word]
    scored = [
        (sum(keyword in chunk.text.lower() for keyword in keywords), index, chunk)
        for index, chunk in enumerate(chunks)
    ]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [chunk for score, _, chunk in scored[:top_k] if score > 0]


if __name__ == "__main__":
    root = Path(__file__).parent
    all_chunks = chunks_from_markdown(root / "sample_notes.md")
    all_chunks += chunks_from_pdf(root / "sample_agent_notes.pdf")

    results = retrieve_chunks("Agent evidence", all_chunks)
    print(json.dumps([asdict(chunk) for chunk in results], ensure_ascii=False, indent=2))
