"""Basic search — run: python examples/basic_search.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import search

page = search(q="toner", tam_pagina=10)

print(f"total: {page['total']}  pages: {page['total_paginas']}")
print()
for item in page["items"]:
    print(f"[{item.get('uf')}] {item.get('title', '')[:80]}")
    print(f"       {item.get('orgao_nome')} | {item.get('situacao_nome')}")
