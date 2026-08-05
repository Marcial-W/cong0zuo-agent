from dataclasses import dataclass
from typing import Iterable, Literal


@dataclass(frozen=True)
class CitableChunk:
    source_id: str
    source_type: Literal["markdown", "pdf"]
    page: int | None
    chunk_id: str
    text: str


def add_chunk_ids(chunks: Iterable[object]) -> list[CitableChunk]:
    """Copy source metadata to every chunk and add a stable chunk_id."""
    result: list[CitableChunk] = []
    for index, chunk in enumerate(chunks, start=1):
        page_part = str(chunk.page) if chunk.page is not None else "md"
        chunk_id = f"{chunk.source_id}#{page_part}#{index:03d}"
        result.append(
            CitableChunk(
                source_id=chunk.source_id,
                source_type=chunk.source_type,
                page=chunk.page,
                chunk_id=chunk_id,
                text=chunk.text,
            )
        )
    return result


def format_citation(chunk: object) -> str:
    """Show a real page only when metadata has one; otherwise show source only."""
    if chunk.page is None:
        return f"[{chunk.source_id}]"
    return f"[{chunk.source_id} · p.{chunk.page}]"


def format_citations(chunks: Iterable[object]) -> list[str]:
    return [format_citation(chunk) for chunk in chunks]


def render_answer(answer: str, chunks: Iterable[object]) -> str:
    citations = format_citations(chunks)
    if not citations:
        return answer
    return f"{answer}\n\n引用：{'，'.join(citations)}"


if __name__ == "__main__":
    fake_chunks = [
        CitableChunk("notes.md", "markdown", None, "notes.md#md#001", "Markdown notes"),
        CitableChunk("report.pdf", "pdf", 2, "report.pdf#2#001", "PDF page two"),
    ]
    print(render_answer("示例回答。", fake_chunks))
