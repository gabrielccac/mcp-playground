"""Sub-recursos de uma licitação — execute: python examples/detalhes_licitacao.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import buscar, obter_documentos, obter_historico, obter_itens, obter_resultado_item

# Pega o primeiro resultado da busca como licitação de teste
pagina = buscar(q="toner", tam_pagina=1)
if not pagina["items"]:
    print("Nenhum resultado encontrado.")
    sys.exit(1)

hit      = pagina["items"][0]
cnpj     = hit["orgao_cnpj"]
ano      = int(hit["ano"])
seq      = int(hit["numero_sequencial"])

print(f"Licitação: {hit.get('title')}")
print(f"  {cnpj} / {ano} / {seq}\n")

# Itens
itens = obter_itens(cnpj, ano, seq)
print(f"Itens ({len(itens)}):")
for item in itens:
    print(f"  [{item.get('numeroItem')}] {item.get('descricao','')[:60]}"
          f" — R$ {item.get('valorUnitarioEstimado')} x {item.get('quantidade')} {item.get('unidadeMedida')}")

# Resultados do primeiro item
print("\nResultado do item 1:")
resultados = obter_resultado_item(cnpj, ano, seq, itens[0]["numeroItem"]) if itens else []
if resultados:
    for r in resultados:
        print(f"  {r.get('nomeRazaoSocialFornecedor')} | "
              f"R$ {r.get('valorUnitarioHomologado')} x {r.get('quantidadeHomologada')} | "
              f"{r.get('situacaoCompraItemResultadoNome')}")
else:
    print("  (sem resultado — licitação pode ainda estar aberta)")

# Documentos
docs = obter_documentos(cnpj, ano, seq)
print(f"\nDocumentos ({len(docs)}):")
for doc in docs:
    print(f"  [{doc.get('sequencialDocumento')}] {doc.get('titulo')} ({doc.get('tipoDocumentoNome')})")

# Histórico
historico = obter_historico(cnpj, ano, seq)
print(f"\nHistórico ({len(historico)}):")
for ev in historico[:5]:
    print(f"  {ev.get('logManutencaoDataInclusao','')[:19]}  "
          f"{ev.get('categoriaLogManutencaoNome')} — {ev.get('tipoLogManutencaoNome')}")
