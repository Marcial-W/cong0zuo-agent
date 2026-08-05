import json
from pathlib import Path

from pypdf import PdfReader


def _open_pdf(file_path: str | Path) -> tuple[Path, PdfReader]:
    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        raise ValueError("只支持 PDF 文件。")
    if not path.is_file():
        raise FileNotFoundError(f"PDF 不存在：{path}")
    return path, PdfReader(path)


def detect_pdf_type(file_path: str | Path) -> dict[str, int | str | bool]:
    """Classify a PDF by extractable text and image-only page signals."""
    path, reader = _open_pdf(file_path)
    text_pages = 0
    image_only_pages = 0
    empty_pages = 0
    text_char_count = 0

    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        compact_text = "".join(text.split())
        if compact_text:
            text_pages += 1
            text_char_count += len(compact_text)
        elif len(page.images) > 0:
            image_only_pages += 1
        else:
            empty_pages += 1

    if text_pages and image_only_pages:
        pdf_type = "mixed"
        message = "部分页面只有图片，需要对这些页面执行 OCR。"
    elif text_pages:
        pdf_type = "text"
        message = "检测到可提取文本，可以直接进入现有问答链路。"
    elif image_only_pages:
        pdf_type = "scanned"
        message = "页面只有图片，不能当作空资料；需要 OCR。"
    else:
        pdf_type = "empty_or_unsupported"
        message = "未检测到文本或页面图片，请检查文件是否空白或使用了暂不支持的内容结构。"

    return {
        "source_id": path.name,
        "pdf_type": pdf_type,
        "page_count": len(reader.pages),
        "text_pages": text_pages,
        "image_only_pages": image_only_pages,
        "empty_pages": empty_pages,
        "text_char_count": text_char_count,
        "needs_ocr": image_only_pages > 0,
        "message": message,
    }


def ocr_pdf(file_path: str | Path) -> list[dict[str, int | str]]:
    """Reserve the OCR integration boundary without pretending it is ready."""
    raise NotImplementedError(f"OCR 尚未接入：{Path(file_path).name}")


if __name__ == "__main__":
    samples_dir = Path(__file__).with_name("samples")
    for sample_path in sorted(samples_dir.glob("*.pdf")):
        print(json.dumps(detect_pdf_type(sample_path), ensure_ascii=False, indent=2))
