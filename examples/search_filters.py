"""Filter combinations — run from repo root: python examples/search_filters.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import search

cases = [
    dict(label="open tenders",           q="toner", status="recebendo_proposta"),
    dict(label="pregão eletrônico / SP",  q="toner", modalidades=6, ufs="SP"),
    dict(label="dispensa / federal",      q="papel", modalidades=8, esferas="F"),
    dict(label="contratos",               q="toner", tipos_documento="contrato"),
]

for case in cases:
    label = case.pop("label")
    page = search(**case, tam_pagina=3)
    print(f"\n── {label} ({page['total_registros']} results, {page['total_paginas']} pages) ──")
    for r in page["items"]:
        print(f"  [{r.get('uf')}] {r.get('title', '')[:72]}")
