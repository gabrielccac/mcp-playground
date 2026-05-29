import asyncio
import os
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from openai import RateLimitError

SERVER_SCRIPT = str(Path(__file__).parent.parent / "tender-mcp" / "server.py")

MAX_TURNS = 20
MAX_RETRIES = 4

INSTRUCTIONS = (
    "You are a specialist in Brazilian public procurement (licitações). "
    "You have two sets of tools: PNCP tools for searching and retrieving tender data, "
    "and Airtable tools for saving and managing records in the database. "
    "\n\n"
    "PNCP tools:\n"
    "- When the user provides a PNCP URL, always call extrair_dados_url_pncp first "
    "to extract cnpj_orgao, ano, and sequencial before calling any other tool.\n"
    "- Status values for editais: 'recebendo_proposta' (open), 'propostas_encerradas' "
    "(under judgment), 'encerradas' (concluded, results available).\n"
    "\n"
    "Airtable tools:\n"
    "- When the user asks to save, track, or add a tender to the database, use the "
    "Airtable tools to create or update the corresponding record.\n"
    "- When the user asks to list or check saved tenders, query Airtable.\n"
    "\n"
    "General rules:\n"
    "- Complete tasks fully and autonomously — make all necessary tool calls before "
    "presenting the final answer.\n"
    "- Never stop mid-task to ask for confirmation.\n"
    "- Reply objectively in the same language the user writes in."
)


def _make_pncp_server():
    return MCPServerStdio(
        params={"command": "python", "args": [SERVER_SCRIPT]},
        cache_tools_list=True,
    )


def _make_airtable_server():
    return MCPServerStdio(
        params={
            "command": "npx",
            "args": ["-y", "@airtable/mcp-server"],
            "env": {**os.environ, "AIRTABLE_API_KEY": os.environ.get("AIRTABLE_API_KEY", "")},
        },
        cache_tools_list=True,
    )


async def _run_with_retry(agent, messages):
    wait = 5
    for attempt in range(MAX_RETRIES):
        try:
            return await Runner.run(agent, input=messages, max_turns=MAX_TURNS)
        except RateLimitError:
            if attempt == MAX_RETRIES - 1:
                raise
            print(f"[Rate limit — waiting {wait}s...]")
            await asyncio.sleep(wait)
            wait *= 2


async def _run(prompt: str) -> str:
    async with _make_pncp_server() as pncp, _make_airtable_server() as airtable:
        agent = Agent(name="PNCP Agent", instructions=INSTRUCTIONS, mcp_servers=[pncp, airtable])
        result = await Runner.run(agent, prompt, max_turns=MAX_TURNS)
    return result.final_output


async def _session():
    print("PNCP Agent — type 'exit' to quit.\n")
    async with _make_pncp_server() as pncp, _make_airtable_server() as airtable:
        agent = Agent(name="PNCP Agent", instructions=INSTRUCTIONS, mcp_servers=[pncp, airtable])
        messages = []
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if user_input.lower() in ("sair", "exit", "quit"):
                break
            if not user_input:
                continue
            messages.append({"role": "user", "content": user_input})
            try:
                result = await _run_with_retry(agent, messages)
            except RateLimitError:
                print("Error: rate limit reached. Try again in a few minutes.\n")
                messages.pop()
                continue
            messages = result.to_input_list()
            print(f"\nAgent: {result.final_output}\n")


def run(prompt: str) -> str:
    return asyncio.run(_run(prompt))


def session():
    asyncio.run(_session())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(" ".join(sys.argv[1:])))
    else:
        session()
