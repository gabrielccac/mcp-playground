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
        "Use as ferramentas disponíveis para buscar e analisar licitações no PNCP. "
        "Quando o usuário fornecer uma URL do PNCP, use extrair_dados_url_pncp primeiro "
        "para obter cnpj_orgao, ano e sequencial antes de chamar outras ferramentas. "
        "Responda de forma objetiva e em português."
    ),
    tools=[function_tool(fn) for fn in FERRAMENTAS],
)


def run(prompt: str) -> str:
    result = Runner.run_sync(agent, prompt)
    return result.final_output


def session():
    """Interactive conversational loop with message history."""
    print("Agente de Licitações PNCP — digite 'sair' para encerrar.\n")
    messages = []
    while True:
        try:
            user_input = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ("sair", "exit", "quit"):
            break
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})
        result = Runner.run_sync(agent, input=messages)
        messages = result.to_input_list()
        print(f"\nAgente: {result.final_output}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(" ".join(sys.argv[1:])))
    else:
        session()
