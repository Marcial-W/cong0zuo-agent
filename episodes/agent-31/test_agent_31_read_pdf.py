import tempfile
import unittest
from pathlib import Path

from agent_31_read_pdf import read_pdf
from make_sample_pdf import SAMPLE_PAGES, build_sample_pdf


class ReadPdfTests(unittest.TestCase):
    def test_returns_text_with_one_based_page_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = build_sample_pdf(Path(temp_dir) / "sample.pdf")

            result = read_pdf(pdf_path)

        self.assertEqual([page["page"] for page in result], [1, 2])
        self.assertEqual([page["text"] for page in result], SAMPLE_PAGES)
        self.assertTrue(all(page["source_id"] == "sample.pdf" for page in result))

    def test_rejects_non_pdf_files(self) -> None:
        with self.assertRaisesRegex(ValueError, "只支持 PDF"):
            read_pdf("notes.md")


if __name__ == "__main__":
    unittest.main()
