import tempfile
import unittest
from pathlib import Path

from agent_32_detect_pdf_type import detect_pdf_type, ocr_pdf
from make_sample_pdfs import build_samples


class DetectPdfTypeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.samples = build_samples(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_detects_text_pdf(self) -> None:
        result = detect_pdf_type(self.samples["text"])

        self.assertEqual(result["pdf_type"], "text")
        self.assertEqual(result["text_pages"], 1)
        self.assertFalse(result["needs_ocr"])

    def test_detects_scanned_pdf_without_calling_it_empty(self) -> None:
        result = detect_pdf_type(self.samples["scanned"])

        self.assertEqual(result["pdf_type"], "scanned")
        self.assertEqual(result["image_only_pages"], 1)
        self.assertTrue(result["needs_ocr"])
        self.assertIn("需要 OCR", result["message"])

    def test_detects_mixed_pdf_page_by_page(self) -> None:
        result = detect_pdf_type(self.samples["mixed"])

        self.assertEqual(result["pdf_type"], "mixed")
        self.assertEqual(result["text_pages"], 1)
        self.assertEqual(result["image_only_pages"], 1)
        self.assertTrue(result["needs_ocr"])

    def test_ocr_is_an_explicit_placeholder(self) -> None:
        with self.assertRaisesRegex(NotImplementedError, "OCR 尚未接入"):
            ocr_pdf(Path("scanned.pdf"))


if __name__ == "__main__":
    unittest.main()
