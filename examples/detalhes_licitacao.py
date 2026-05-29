"""Sub-recursos de uma licitação — execute: python examples/detalhes_licitacao.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import get_tender_documents, get_tender_history, get_tender_item_results, get_tender_items, search

page = search(q="toner", tam_pagina=1)
if not page["items"]:
    print("Nenhum resultado encontrado.")
    sys.exit(1)

hit  = page["items"][0]
cnpj = hit["orgao_cnpj"]
ano  = int(hit["ano"])
seq  = int(hit["numero_sequencial"])

print(f"Licitação: {hit.get('title')}")
print(f"  {cnpj} / {ano} / {seq}\n")

items = get_tender_items(cnpj, ano, seq)
print(f"Itens ({len(items)}):")
for item in items:
    print(f"  [{item.get('numeroItem')}] {item.get('descricao','')[:60]}"
          f" — R$ {item.get('valorUnitarioEstimado')} x {item.get('quantidade')} {item.get('unidadeMedida')}")

print("\nResultado do item 1:")
results = get_tender_item_results(cnpj, ano, seq, items[0]["numeroItem"]) if items else []
if results:
    for r in results:
        print(f"  {r.get('nomeRazaoSocialFornecedor')} | R$ {r.get('valorUnitarioHomologado')} | {r.get('situacaoCompraItemResultadoNome')}")
else:
    print("  (sem resultado — licitação pode ainda estar aberta)")

docs = get_tender_documents(cnpj, ano, seq)
print(f"\nDocumentos ({len(docs)}):")
for doc in docs:
    print(f"  [{doc.get('sequencialDocumento')}] {doc.get('titulo')} ({doc.get('tipoDocumentoNome')})")

history = get_tender_history(cnpj, ano, seq)
print(f"\nHistórico ({len(history)}):")
for ev in history[:5]:
    print(f"  {ev.get('logManutencaoDataInclusao','')[:19]}  {ev.get('categoriaLogManutencaoNome')} — {ev.get('tipoLogManutencaoNome')}")
