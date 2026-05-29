import asyncio
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import anthropic
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

AIRTABLE_MCP_URL = "https://mcp.airtable.com/mcp"
MODEL = "claude-opus-4-8"
MAX_TOKENS = 4096

SYSTEM = (
    "You are a helpful assistant with access to Airtable. "
    "Always call the necessary tools immediately and include the results in your response — "
    "never tell the user you are 'checking' or ask them to wait. "
    "Complete tasks fully before responding."
)

client = anthropic.Anthropic()


def _headers():
    return {"Authorization": f"Bearer {os.environ.get('AIRTABLE_TOKEN', '')}"}


async def _list_tools() -> list[dict]:
    async with streamablehttp_client(url=AIRTABLE_MCP_URL, headers=_headers()) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.list_tools()
    return [
        {
            "name": t.name,
            "description": t.description or "",
            "input_schema": t.inputSchema,
        }
        for t in result.tools
    ]


async def _call_tool(name: str, args: dict) -> str:
    async with streamablehttp_client(url=AIRTABLE_MCP_URL, headers=_headers()) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.call_tool(name, args)
    parts = [c.text if hasattr(c, "text") else str(c) for c in result.content]
    return "\n".join(parts) or "[]"


async def _run(messages: list, tools: list) -> tuple[str, list]:
    """One agentic loop — keeps calling tools until the model stops."""
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM,
            tools=tools,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            text = next((b.text for b in response.content if hasattr(b, "text")), "")
            return text, messages

        # Execute all tool calls in this turn
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  → {block.name}({json.dumps(block.input)})")
                output = await _call_tool(block.name, block.input)
                print(f"  ← {output[:200]}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        messages.append({"role": "user", "content": tool_results})


async def _session():
    print("Airtable Agent — type 'exit' to quit.\n")
    tools = await _list_tools()
    print(f"Loaded {len(tools)} tools.\n")
    messages = []
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})
        answer, messages = await _run(messages, tools)
        print(f"\nAgent: {answer}\n")


if __name__ == "__main__":
    asyncio.run(_session())
