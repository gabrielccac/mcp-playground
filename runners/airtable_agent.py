import asyncio
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from agents import Agent, Runner, function_tool
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

AIRTABLE_MCP_URL = "https://mcp.airtable.com/mcp"
MAX_TURNS = 20

INSTRUCTIONS = (
    "You are a helpful assistant with access to Airtable. "
    "Use the available tools to read, create, update, and delete records as requested. "
    "Always call the necessary tools immediately and include the results in your response — "
    "never tell the user you are 'checking' or ask them to wait. "
    "Complete tasks fully before responding."
)


def _mcp_headers():
    return {"Authorization": f"Bearer {os.environ.get('AIRTABLE_TOKEN', '')}"}


def _make_tool(name: str, description: str):
    """Wrap a single MCP tool as a function_tool the agents SDK can call."""
    async def _call(**kwargs) -> str:
        async with streamablehttp_client(url=AIRTABLE_MCP_URL, headers=_mcp_headers()) as (r, w, _):
            async with ClientSession(r, w) as session:
                await session.initialize()
                result = await session.call_tool(name, kwargs)
                parts = [c.text if hasattr(c, "text") else str(c) for c in result.content]
                return "\n".join(parts) or "[]"

    _call.__name__ = name
    _call.__doc__ = description
    return function_tool(_call)


async def _build_tools() -> list:
    """Connect once to fetch the tool list, then build function_tool wrappers."""
    async with streamablehttp_client(url=AIRTABLE_MCP_URL, headers=_mcp_headers()) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            tools = await session.list_tools()
    return [_make_tool(t.name, t.description or "") for t in tools.tools]


async def _session():
    print("Airtable Agent — type 'exit' to quit.\n")
    tools = await _build_tools()
    print(f"Loaded {len(tools)} tools from Airtable MCP.\n")
    agent = Agent(name="Airtable Agent", instructions=INSTRUCTIONS, tools=tools)
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
        result = await Runner.run(agent, input=messages, max_turns=MAX_TURNS)
        messages = result.to_input_list()
        print(f"\nAgent: {result.final_output}\n")


if __name__ == "__main__":
    asyncio.run(_session())
