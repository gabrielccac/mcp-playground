"""Tender sub-resource endpoints — run: python examples/tender_details.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import (
    get_tender_documents,
    get_tender_history,
    get_tender_item_results,
    get_tender_items,
    search,
)

# Grab the first result from a search to use as our test tender
page = search(q="toner", tam_pagina=1)
if not page["items"]:
    print("No results found")
    sys.exit(1)

hit = page["items"][0]
cnpj = hit["orgao_cnpj"]
ano  = int(hit["ano"])
seq  = int(hit["numero_sequencial"])

print(f"Tender: {hit.get('title')}")
print(f"  {cnpj} / {ano} / {seq}\n")

# Items
items = get_tender_items(cnpj, ano, seq)
print(f"Items ({len(items)}):")
for item in items:
    print(f"  [{item.get('numeroItem')}] {item.get('descricao','')[:60]}"
          f" — R$ {item.get('valorUnitarioEstimado')} x {item.get('quantidade')} {item.get('unidadeMedida')}")

# Item results (only meaningful for closed tenders)
print("\nItem results (first item):")
if items:
    results = get_tender_item_results(cnpj, ano, seq, items[0]["numeroItem"])
    if results:
        for r in results:
            print(f"  {r.get('nomeRazaoSocialFornecedor')} | R$ {r.get('valorUnitarioHomologado')} "
                  f"x {r.get('quantidadeHomologada')} | {r.get('situacaoCompraItemResultadoNome')}")
    else:
        print("  (no results yet — tender may still be open)")

# Documents
docs = get_tender_documents(cnpj, ano, seq)
print(f"\nDocuments ({len(docs)}):")
for doc in docs:
    print(f"  [{doc.get('sequencialDocumento')}] {doc.get('titulo')} ({doc.get('tipoDocumentoNome')})")

# History
history = get_tender_history(cnpj, ano, seq)
print(f"\nHistory ({len(history)}):")
for ev in history[:5]:
    print(f"  {ev.get('logManutencaoDataInclusao','')[:19]}  "
          f"{ev.get('categoriaLogManutencaoNome')} — {ev.get('tipoLogManutencaoNome')}")
