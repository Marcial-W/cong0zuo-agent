import asyncio
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


SERVER_PATH = Path(__file__).with_name("agent_21_file_server.py").resolve()


def create_state(question: str) -> dict[str, Any]:
    """Continue using the inspectable run state introduced in P019."""
    return {
        "question": question,
        "tool_calls": [],
        "tool_results": [],
        "answer": None,
    }


def get_text(result: types.CallToolResult) -> str:
    """Extract text blocks from an MCP tool result."""
    return "\n".join(
        block.text for block in result.content if isinstance(block, types.TextContent)
    )


async def run() -> dict[str, Any]:
    state = create_state("MCP 怎样把本地笔记接进 Agent？")
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("发现工具：", [tool.name for tool in tools.tools])

            tool_call = {
                "name": "read_note",
                "arguments": {"filename": "mcp-notes.md"},
            }
            result = await session.call_tool(
                tool_call["name"],
                arguments=tool_call["arguments"],
            )

    state["tool_calls"].append(tool_call)
    state["tool_results"].append(
        {
            "name": tool_call["name"],
            "arguments": tool_call["arguments"],
            "status": "error" if result.isError else "success",
            "content": get_text(result),
        }
    )
    return state


if __name__ == "__main__":
    final_state = asyncio.run(run())
    print("MCP 结果已写回 state：")
    print(final_state)
