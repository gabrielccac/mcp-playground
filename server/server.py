"""
MCP server exposing PNCP tools via FastMCP.

Run directly:
    python server/server.py

Or launched automatically via stdio by runners/mcp_agent.py.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from tools import FERRAMENTAS

mcp = FastMCP("PNCP Licitações")

for fn in FERRAMENTAS:
    mcp.tool()(fn)

if __name__ == "__main__":
    mcp.run(transport="stdio")
