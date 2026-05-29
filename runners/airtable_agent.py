import asyncio
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

AIRTABLE_MCP_URL = "https://mcp.airtable.com/mcp"
MAX_TURNS = 20

INSTRUCTIONS = (
    "You are a helpful assistant with access to Airtable. "
    "Use the available tools to read, create, update, and delete records as requested. "
    "Always call the necessary tools immediately and include the results in your response — "
    "never tell the user you are 'checking' or ask them to wait. "
    "Complete tasks fully before responding."
)


def _make_airtable_server():
    token = os.environ.get("AIRTABLE_TOKEN", "")
    return MCPServerStreamableHttp(
        params={
            "url": AIRTABLE_MCP_URL,
            "headers": {"Authorization": f"Bearer {token}"},
        },
        cache_tools_list=True,
    )


async def _session():
    print("Airtable Agent — type 'exit' to quit.\n")
    async with _make_airtable_server() as airtable:
        agent = Agent(name="Airtable Agent", instructions=INSTRUCTIONS, mcp_servers=[airtable])
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
