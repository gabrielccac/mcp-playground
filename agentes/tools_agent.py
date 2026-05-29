import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import Agent, Runner

from tools import (
    buscar_licitacoes,
    obter_documentos_licitacao,
    obter_historico_licitacao,
    obter_itens_licitacao,
    obter_resultado_item_licitacao,
)

agent = Agent(
    name="Agente de Licitações PNCP",
    instructions=(
        "Você é um assistente especializado em licitações públicas brasileiras. "
        "Use as ferramentas disponíveis para buscar e analisar licitações no Portal "
        "Nacional de Contratações Públicas (PNCP). "
        "Sempre que buscar uma licitação e o usuário quiser mais detalhes, use os campos "
        "'orgao_cnpj', 'ano' e 'numero_sequencial' do resultado para consultar itens, "
        "documentos ou histórico. "
        "Responda de forma objetiva e em português."
    ),
    tools=[
        buscar_licitacoes,
        obter_itens_licitacao,
        obter_resultado_item_licitacao,
        obter_documentos_licitacao,
        obter_historico_licitacao,
    ],
)


def run(prompt: str) -> str:
    result = Runner.run_sync(agent, prompt)
    return result.final_output


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Busca licitações abertas de toner em SP"
    print(run(prompt))
