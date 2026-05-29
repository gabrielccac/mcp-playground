import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from agents import Agent, Runner, function_tool

from tools import FERRAMENTAS

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
    tools=[function_tool(fn) for fn in FERRAMENTAS],
)


def run(prompt: str) -> str:
    result = Runner.run_sync(agent, prompt)
    return result.final_output


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Busca licitações abertas de toner em SP"
    print(run(prompt))
