import unittest
from pathlib import Path

from agent_34_save_upload import (
    MAX_UPLOAD_BYTES,
    cleanup_upload,
    save_upload,
)


class SaveUploadTests(unittest.TestCase):
    def test_valid_pdf_is_saved_inside_temp_dir(self) -> None:
        saved = save_upload("../notes/sample.pdf", b"%PDF-1.4\nfake content")

        self.assertEqual(saved.source_id, "sample.pdf")
        self.assertEqual(saved.path.read_bytes(), b"%PDF-1.4\nfake content")
        self.assertTrue(saved.path.is_relative_to(saved.temp_dir))
        self.assertNotEqual(saved.path.name, "sample.pdf")

        cleanup_upload(saved)
        self.assertFalse(saved.path.exists())
        self.assertFalse(saved.temp_dir.exists())

    def test_non_pdf_is_rejected_before_save(self) -> None:
        with self.assertRaisesRegex(ValueError, "不支持的文件类型"):
            save_upload("notes.txt", b"not a pdf")

    def test_oversized_file_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "超过大小上限"):
            save_upload("huge.pdf", b"x" * (MAX_UPLOAD_BYTES + 1))

    def test_upload_name_never_becomes_arbitrary_read_path(self) -> None:
        saved = save_upload("../../etc/passwd.pdf", b"%PDF-1.4\nsafe")
        self.assertEqual(saved.path.parent, saved.temp_dir)
        self.assertEqual(saved.source_id, "passwd.pdf")
        cleanup_upload(saved)


if __name__ == "__main__":
    unittest.main()
