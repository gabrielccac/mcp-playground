"""Tender sub-resource endpoints — run: python examples/tender_details.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import (
    get_tender_documents,
    get_tender_documents_count,
    get_tender_history,
    get_tender_history_count,
    get_tender_items,
    get_tender_items_count,
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

print(f"Testing tender: {hit.get('title')}")
print(f"  {cnpj} / {ano} / {seq}\n")

# Items
n_items = get_tender_items_count(cnpj, ano, seq)
print(f"Items ({n_items}):")
for item in get_tender_items(cnpj, ano, seq, tamanho_pagina=n_items or 5):
    print(f"  [{item.get('numeroItem')}] {item.get('descricao','')[:60]}"
          f" — R$ {item.get('valorUnitarioEstimado')} x {item.get('quantidade')} {item.get('unidadeMedida')}")

# Documents
n_docs = get_tender_documents_count(cnpj, ano, seq)
print(f"\nDocuments ({n_docs}):")
for doc in get_tender_documents(cnpj, ano, seq, tamanho_pagina=n_docs or 5):
    print(f"  [{doc.get('sequencialDocumento')}] {doc.get('titulo')} ({doc.get('tipoDocumentoNome')})")

# History
n_hist = get_tender_history_count(cnpj, ano, seq)
print(f"\nHistory ({n_hist}):")
for ev in get_tender_history(cnpj, ano, seq, tamanho_pagina=min(n_hist or 5, 5)):
    print(f"  {ev.get('logManutencaoDataInclusao','')[:19]}  {ev.get('categoriaLogManutencaoNome')} — {ev.get('tipoLogManutencaoNome')}")
