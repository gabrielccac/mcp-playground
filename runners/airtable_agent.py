import asyncio
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI, RateLimitError
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

AIRTABLE_MCP_URL = "https://mcp.airtable.com/mcp"
MODEL = "gpt-4o"
MAX_TURNS = 20

SYSTEM = (
    "You are a helpful assistant with access to Airtable. "
    "Always call the necessary tools immediately and include the results in your response — "
    "never tell the user you are 'checking' or ask them to wait. "
    "Complete tasks fully before responding."
)

client = OpenAI()


def _headers():
    return {"Authorization": f"Bearer {os.environ.get('AIRTABLE_TOKEN', '')}"}


async def _list_tools() -> list[dict]:
    async with streamablehttp_client(url=AIRTABLE_MCP_URL, headers=_headers()) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.list_tools()
    return [
        {"type": "function", "function": {
            "name": t.name,
            "description": t.description or "",
            "parameters": t.inputSchema,
        }}
        for t in result.tools
    ]


async def _call_tool(name: str, args: dict) -> str:
    async with streamablehttp_client(url=AIRTABLE_MCP_URL, headers=_headers()) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.call_tool(name, args)
    parts = [c.text if hasattr(c, "text") else str(c) for c in result.content]
    return "\n".join(parts) or "[]"


def _complete(messages, tools):
    wait = 2
    for attempt in range(5):
        try:
            return client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        except RateLimitError:
            if attempt == 4:
                raise
            print(f"[Rate limit — waiting {wait}s...]")
            import time; time.sleep(wait)
            wait *= 2


async def _run(messages: list, tools: list) -> tuple[str, list]:
    for _ in range(MAX_TURNS):
        response = _complete(messages, tools)
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content or "", messages

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"  → {tc.function.name}({json.dumps(args)})")
            output = await _call_tool(tc.function.name, args)
            print(f"  ← {output[:200]}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": output,
            })

    return "Max turns reached.", messages


async def _session():
    print("Airtable Agent — type 'exit' to quit.\n")
    tools = await _list_tools()
    print(f"Loaded {len(tools)} tools.\n")
    messages = [{"role": "system", "content": SYSTEM}]
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
