"""Busca básica — execute: python examples/busca_basica.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import buscar

pagina = buscar(q="toner", tam_pagina=10)

print(f"total: {pagina['total']}  páginas: {pagina['total_paginas']}")
print()
for item in pagina["items"]:
    print(f"[{item.get('uf')}] {item.get('title', '')[:80]}")
    print(f"       {item.get('orgao_nome')} | {item.get('situacao_nome')}")
