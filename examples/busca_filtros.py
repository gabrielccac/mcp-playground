"""Combinações de filtros — execute: python examples/busca_filtros.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import buscar

casos = [
    dict(label="licitações abertas",         q="toner", status="recebendo_proposta"),
    dict(label="pregão eletrônico / SP",      q="toner", modalidades=6, ufs="SP"),
    dict(label="dispensa / federal",          q="papel", modalidades=8, esferas="F"),
    dict(label="contratos",                   q="toner", tipos_documento="contrato"),
]

for caso in casos:
    label = caso.pop("label")
    pagina = buscar(**caso, tam_pagina=3)
    print(f"\n── {label} ({pagina['total']} resultados) ──")
    for item in pagina["items"]:
        print(f"  [{item.get('uf')}] {item.get('title', '')[:72]}")
