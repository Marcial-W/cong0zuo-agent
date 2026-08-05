from pathlib import Path

from mcp.server.fastmcp import FastMCP


NOTES_DIR = (Path(__file__).parent / "notes").resolve()
mcp = FastMCP("local-notes")


@mcp.tool()
def read_note(filename: str) -> str:
    """Read one Markdown note from the demo notes directory."""
    note_path = (NOTES_DIR / filename).resolve()

    if not note_path.is_relative_to(NOTES_DIR):
        raise ValueError("只能读取 notes 目录内的文件。")
    if note_path.suffix.lower() != ".md":
        raise ValueError("本示例只允许读取 Markdown 文件。")
    if not note_path.is_file():
        raise FileNotFoundError(f"找不到笔记：{filename}")

    return note_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run(transport="stdio")
