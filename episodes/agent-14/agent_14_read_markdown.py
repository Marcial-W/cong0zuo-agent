from pathlib import Path


def read_markdown(file_path: str | Path) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{path}")
    if path.suffix.lower() != ".md":
        raise ValueError("这一期只读取 Markdown 文件。")

    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    sample_notes = Path(__file__).with_name("sample_notes.md")
    content = read_markdown(sample_notes)
    print(content[:200])
