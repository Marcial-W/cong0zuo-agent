import unittest
from pathlib import Path

from agent_33_document_chunks import (
    chunks_from_markdown,
    chunks_from_pdf,
    retrieve_chunks,
)


ROOT = Path(__file__).parent


class DocumentChunkTests(unittest.TestCase):
    def test_markdown_and_pdf_share_one_contract(self) -> None:
        markdown_chunks = chunks_from_markdown(ROOT / "sample_notes.md")
        pdf_chunks = chunks_from_pdf(ROOT / "sample_agent_notes.pdf")

        self.assertEqual(markdown_chunks[0].source_type, "markdown")
        self.assertIsNone(markdown_chunks[0].page)
        self.assertEqual(pdf_chunks[0].source_type, "pdf")
        self.assertEqual([chunk.page for chunk in pdf_chunks], [1, 2])
        self.assertEqual(
            set(markdown_chunks[0].__dataclass_fields__),
            {"source_id", "source_type", "page", "text"},
        )

    def test_one_retriever_accepts_both_sources(self) -> None:
        chunks = chunks_from_markdown(ROOT / "sample_notes.md")
        chunks += chunks_from_pdf(ROOT / "sample_agent_notes.pdf")

        markdown_result = retrieve_chunks("Markdown state", chunks, top_k=1)
        pdf_result = retrieve_chunks("Agent evidence", chunks, top_k=1)

        self.assertEqual(markdown_result[0].source_type, "markdown")
        self.assertEqual(pdf_result[0].source_type, "pdf")
        self.assertEqual(pdf_result[0].page, 1)

    def test_empty_pdf_pages_do_not_create_empty_chunks(self) -> None:
        chunks = chunks_from_pdf(ROOT / "sample_agent_notes.pdf")
        self.assertTrue(all(chunk.text.strip() for chunk in chunks))

    def test_rejects_wrong_adapter_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "Markdown"):
            chunks_from_markdown(ROOT / "sample_agent_notes.pdf")
        with self.assertRaisesRegex(ValueError, "PDF"):
            chunks_from_pdf(ROOT / "sample_notes.md")


if __name__ == "__main__":
    unittest.main()
