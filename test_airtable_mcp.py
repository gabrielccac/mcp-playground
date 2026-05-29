"""
Direct MCP connection test — no agents SDK involved.
Uses the mcp library's streamablehttp_client to connect, list tools,
and call list_bases.
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

URL = "https://mcp.airtable.com/mcp"
token = os.environ.get("AIRTABLE_TOKEN", "")

async def main():
    print(f"Token: {token[:8]}...{token[-4:]}\n")
    async with streamablehttp_client(
        url=URL,
        headers={"Authorization": f"Bearer {token}"},
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected.\n")

            tools = await session.list_tools()
            print(f"=== TOOLS ({len(tools.tools)}) ===")
            for t in tools.tools:
                print(f"  {t.name}")

            print("\n=== list_bases ===")
            result = await session.call_tool("list_bases", {})
            for item in result.content:
                print(item)

asyncio.run(main())
