import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from agents import Agent, Runner, function_tool
from openai import RateLimitError

from tools import FERRAMENTAS

agent = Agent(
    name="Agente de Licitações PNCP",
    instructions=(
        "Você é um assistente especializado em licitações públicas brasileiras. "
        "Use as ferramentas disponíveis para buscar e analisar licitações no PNCP. "
        "Quando o usuário fornecer uma URL do PNCP, use extrair_dados_url_pncp primeiro "
        "para obter cnpj_orgao, ano e sequencial antes de chamar outras ferramentas. "
        "Complete tarefas de forma autônoma e integralmente — faça todas as consultas "
        "necessárias antes de apresentar a resposta final. "
        "Nunca interrompa a tarefa no meio para pedir confirmação do usuário. "
        "Responda de forma objetiva e em português."
    ),
    tools=[function_tool(fn) for fn in FERRAMENTAS],
)

MAX_TURNS = 20
MAX_RETRIES = 4


def _run_with_retry(messages):
    wait = 5
    for attempt in range(MAX_RETRIES):
        try:
            return Runner.run_sync(agent, input=messages, max_turns=MAX_TURNS)
        except RateLimitError as e:
            if attempt == MAX_RETRIES - 1:
                raise
            print(f"[Rate limit — aguardando {wait}s...]")
            time.sleep(wait)
            wait *= 2


def run(prompt: str) -> str:
    result = Runner.run_sync(agent, prompt, max_turns=MAX_TURNS)
    return result.final_output


def session():
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
        try:
            result = _run_with_retry(messages)
        except RateLimitError:
            print("Erro: limite de requisições atingido. Tente novamente em alguns minutos.\n")
            messages.pop()
            continue
        messages = result.to_input_list()
        print(f"\nAgente: {result.final_output}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(" ".join(sys.argv[1:])))
    else:
        session()
