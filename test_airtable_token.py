"""Quick script to verify AIRTABLE_TOKEN and probe the MCP endpoint."""
import json
import os
import httpx
from dotenv import load_dotenv
load_dotenv()

token = os.environ.get("AIRTABLE_TOKEN", "")
if not token:
    print("ERROR: AIRTABLE_TOKEN not set in .env")
    raise SystemExit(1)

url = "https://mcp.airtable.com/mcp"
print(f"Token: {token[:8]}...{token[-4:]}")
print(f"URL: {url}\n")

# Proper MCP Streamable HTTP initialization request
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}
body = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "0.1"},
    },
}

try:
    resp = httpx.post(url, headers=headers, json=body, timeout=10)
    print(f"POST {resp.status_code}")
    print(resp.text[:500])
except Exception as e:
    print(f"POST ERROR: {e}")
