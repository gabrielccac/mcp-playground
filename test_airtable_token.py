"""Quick script to verify AIRTABLE_TOKEN and probe the MCP endpoint."""
import os
import httpx
from dotenv import load_dotenv
load_dotenv()

token = os.environ.get("AIRTABLE_TOKEN", "")
if not token:
    print("ERROR: AIRTABLE_TOKEN not set in .env")
    raise SystemExit(1)

url = "https://mcp.airtable.com/mcp"
headers = {"Authorization": f"Bearer {token}"}

print(f"Token: {token[:8]}...{token[-4:]}")
print(f"URL: {url}\n")

for method in ("GET", "POST"):
    try:
        resp = httpx.request(method, url, headers=headers, timeout=10)
        print(f"{method} {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"{method} ERROR: {e}")
