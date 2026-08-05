import unittest
import sys
from pathlib import Path

EPISODES_ROOT = Path(__file__).resolve().parents[1]
for episode_name in ("agent-32", "agent-33", "agent-34", "agent-35"):
    sys.path.insert(0, str(EPISODES_ROOT / episode_name))

from agent_34_save_upload import MAX_UPLOAD_BYTES
from agent_36_end_to_end_pdf_qa import answer_pdf_question
from build_qa_samples import build_samples


ROOT = Path(__file__).parent


class EndToEndPdfQaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.samples = build_samples(ROOT / "samples")

    def test_text_pdf_returns_cited_answer(self) -> None:
        question = "Agent 为什么要在回答里保留页码？"
        result = answer_pdf_question(
            "sample_qa.pdf", self.samples["qa"].read_bytes(), question
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("[sample_qa.pdf · p.2]", result["answer"])
        self.assertIn("引用：", result["answer"])
        self.assertTrue(result["cleaned"])
        self.assertFalse(Path(str(result["saved"]["temporary_path"])).exists())

    def test_scanned_pdf_has_ocr_message(self) -> None:
        result = answer_pdf_question(
            "sample_scanned.pdf", self.samples["scanned"].read_bytes(), "问题"
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("OCR", result["message"])

    def test_empty_pdf_is_not_silently_dropped(self) -> None:
        result = answer_pdf_question(
            "sample_empty.pdf", self.samples["empty"].read_bytes(), "问题"
        )
        self.assertEqual(result["status"], "error")
        self.assertNotIn("success", result["status"])

    def test_invalid_file_is_rejected(self) -> None:
        result = answer_pdf_question("notes.txt", b"not a pdf", "问题")
        self.assertEqual(result["status"], "error")
        self.assertIn("不支持的文件类型", result["message"])

    def test_oversized_file_is_rejected(self) -> None:
        result = answer_pdf_question(
            "huge.pdf", b"x" * (MAX_UPLOAD_BYTES + 1), "问题"
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("超过大小上限", result["message"])

    def test_no_match_does_not_fabricate_citation(self) -> None:
        result = answer_pdf_question(
            "sample_qa.pdf", self.samples["qa"].read_bytes(), "网页搜索"
        )
        self.assertEqual(result["status"], "no_match")
        self.assertIn("没有检索到相关片段", result["message"])
        self.assertNotIn("p.", str(result))


if __name__ == "__main__":
    unittest.main()
