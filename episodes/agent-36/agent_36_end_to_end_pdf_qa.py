import json
import sys
from dataclasses import asdict, replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
for episode_name in ("agent-32", "agent-33", "agent-34", "agent-35"):
    sys.path.insert(0, str(ROOT / episode_name))

from agent_32_detect_pdf_type import detect_pdf_type
from agent_33_document_chunks import chunks_from_pdf, retrieve_chunks
from agent_34_save_upload import cleanup_upload, save_upload
from agent_35_citations import add_chunk_ids, format_citations, render_answer


def normalize_question(question: str) -> str:
    """Map the fixed Chinese demo phrase to terms present in the sample PDF."""
    return (
        question
        .replace("页码", " page number ")
        .replace("回答", " answer ")
        .replace("？", " ")
        .replace("，", " ")
    )


def fake_llm(question: str) -> str:
    if "页码" in question or "page number" in question:
        return "Agent 要在回答里保留页码，因为读者需要回到原文核对。"
    return "根据资料，Agent 应该先检索相关证据，再回答。"


def _describe_saved(saved: object) -> dict[str, object]:
    return {
        "source_id": saved.source_id,
        "original_name": saved.original_name,
        "size_bytes": saved.size_bytes,
        "temporary_path": str(saved.path),
    }


def answer_pdf_question(
    original_name: str, content: bytes, question: str
) -> dict[str, object]:
    saved = None
    try:
        saved = save_upload(original_name, content)
    except ValueError as error:
        return {"status": "error", "message": str(error)}

    try:
        detection = detect_pdf_type(saved.path)
        if detection["pdf_type"] != "text":
            return {
                "status": "error",
                "message": detection["message"],
                "detection": {key: detection[key] for key in (
                    "pdf_type", "page_count", "text_pages",
                    "image_only_pages", "empty_pages", "needs_ocr",
                )},
            }

        chunks = chunks_from_pdf(saved.path)
        if not chunks:
            return {"status": "error", "message": "PDF 没有可检索文本。"}

        chunks = [replace(chunk, source_id=saved.source_id) for chunk in chunks]
        citable_chunks = add_chunk_ids(chunks)
        results = retrieve_chunks(normalize_question(question), citable_chunks, top_k=2)
        if not results:
            return {
                "status": "no_match",
                "message": "没有检索到相关片段。",
                "saved": _describe_saved(saved),
            }

        answer_text = fake_llm(question)
        return {
            "status": "success",
            "saved": _describe_saved(saved),
            "detection": {
                "pdf_type": detection["pdf_type"],
                "text_pages": detection["text_pages"],
                "page_count": detection["page_count"],
                "needs_ocr": detection["needs_ocr"],
            },
            "chunk_count": len(citable_chunks),
            "results": [asdict(chunk) for chunk in results],
            "citations": format_citations(results),
            "answer": render_answer(answer_text, results),
            "cleaned": True,
        }
    finally:
        if saved is not None:
            cleanup_upload(saved)


if __name__ == "__main__":
    samples = Path(__file__).with_name("samples")
    qa_path = samples / "sample_qa.pdf"
    if not qa_path.exists():
        from build_qa_samples import build_samples

        build_samples(samples)

    question = "Agent 为什么要在回答里保留页码？"
    result = answer_pdf_question(
        qa_path.name, qa_path.read_bytes(), question
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
