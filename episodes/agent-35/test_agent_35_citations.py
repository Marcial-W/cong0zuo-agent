import unittest

from agent_35_citations import (
    CitableChunk,
    add_chunk_ids,
    format_citation,
    render_answer,
)


class FakeChunk:
    def __init__(self, source_id, source_type, page, text):
        self.source_id = source_id
        self.source_type = source_type
        self.page = page
        self.text = text


class CitationTests(unittest.TestCase):
    def test_add_chunk_ids_preserves_source_and_page(self) -> None:
        chunks = [
            FakeChunk("sample.pdf", "pdf", 1, "page one"),
            FakeChunk("notes.md", "markdown", None, "markdown text"),
        ]
        cited = add_chunk_ids(chunks)

        self.assertEqual(cited[0].page, 1)
        self.assertIsNone(cited[1].page)
        self.assertEqual(cited[0].chunk_id, "sample.pdf#1#001")
        self.assertEqual(cited[1].chunk_id, "notes.md#md#002")

    def test_pdf_shows_real_page(self) -> None:
        chunk = CitableChunk("sample.pdf", "pdf", 2, "sample.pdf#2#001", "text")
        self.assertEqual(format_citation(chunk), "[sample.pdf · p.2]")

    def test_missing_page_does_not_fabricate_page_number(self) -> None:
        chunk = CitableChunk("notes.md", "markdown", None, "notes.md#md#001", "text")
        self.assertEqual(format_citation(chunk), "[notes.md]")

    def test_render_answer_appends_only_real_citations(self) -> None:
        chunks = [
            CitableChunk("sample.pdf", "pdf", 2, "sample.pdf#2#001", "text")
        ]
        self.assertIn("[sample.pdf · p.2]", render_answer("回答", chunks))
        self.assertNotIn("p.9", render_answer("回答", chunks))


if __name__ == "__main__":
    unittest.main()
