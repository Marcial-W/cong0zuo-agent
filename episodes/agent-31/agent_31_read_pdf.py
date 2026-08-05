import json
from pathlib import Path

from pypdf import PdfReader


def read_pdf(file_path: str | Path) -> list[dict[str, int | str]]:
    """Read a text PDF page by page while preserving one-based page numbers."""
    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        raise ValueError("只支持 PDF 文件。")
    if not path.is_file():
        raise FileNotFoundError(f"PDF 不存在：{path}")

    reader = PdfReader(path)
    pages: list[dict[str, int | str]] = []
    for page_number, page in enumerate(reader.pages, start=1):
        pages.append(
            {
                "source_id": path.name,
                "page": page_number,
                "text": (page.extract_text() or "").strip(),
            }
        )
    return pages


if __name__ == "__main__":
    sample_path = Path(__file__).with_name("sample_agent_notes.pdf")
    print(json.dumps(read_pdf(sample_path), ensure_ascii=False, indent=2))
