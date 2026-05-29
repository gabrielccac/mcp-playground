"""Basic search — run from repo root: python examples/search_basic.py"""

from api import search

page = search(q="toner", tam_pagina=10)

print(f"total: {page['total_registros']}  pages: {page['total_paginas']}")
print()
for r in page["items"]:
    print(f"[{r.get('uf')}] {r.get('title', '')[:80]}")
    print(f"       {r.get('orgao_nome')} | {r.get('situacao_nome')}")
