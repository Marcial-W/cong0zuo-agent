import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path


ALLOWED_UPLOAD_EXTENSIONS = {".pdf"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class SavedUpload:
    source_id: str
    original_name: str
    path: Path
    temp_dir: Path
    size_bytes: int


def save_upload(original_name: str, content: bytes) -> SavedUpload:
    """Validate an upload and write it to a controlled temporary directory."""
    if not original_name or not original_name.strip():
        raise ValueError("上传文件名不能为空。")

    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError(f"不支持的文件类型：{suffix or '无扩展名'}，只允许 .pdf。")
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError(f"文件超过大小上限：{MAX_UPLOAD_BYTES} 字节。")

    source_id = Path(original_name).name
    temp_dir = Path(tempfile.mkdtemp(prefix="agent-upload-"))
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    path = temp_dir / safe_name
    path.write_bytes(content)

    return SavedUpload(
        source_id=source_id,
        original_name=original_name,
        path=path,
        temp_dir=temp_dir,
        size_bytes=len(content),
    )


def cleanup_upload(saved: SavedUpload | None) -> bool:
    """Remove the saved file and its temporary directory."""
    if saved is None:
        return False
    if saved.path.exists():
        saved.path.unlink()
    if saved.temp_dir.exists():
        try:
            saved.temp_dir.rmdir()
        except OSError:
            return False
    return True


if __name__ == "__main__":
    sample = save_upload("sample_qa.pdf", b"%PDF-1.4\nminimal sample")
    print(
        {
            "source_id": sample.source_id,
            "temp_dir": str(sample.temp_dir),
            "path": str(sample.path),
            "size_bytes": sample.size_bytes,
        }
    )
    cleanup_upload(sample)
