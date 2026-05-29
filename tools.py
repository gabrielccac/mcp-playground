"""
Ferramentas de busca e análise de licitações do PNCP.

Este módulo é a única fonte de definição das ferramentas — usado tanto pelo
servidor MCP quanto pelo agente com tools da API da Anthropic.
"""

import json
from typing import Literal

from api.client import (
    buscar,
    obter_documentos,
    obter_historico,
    obter_itens,
    obter_licitacao,
    obter_resultado_item,
)


def buscar_licitacoes(
    consulta: str,
    tipo_documento: Literal["edital", "ata", "contrato"] = "edital",
    ordenacao: Literal["-data", "data", "relevancia"] = "-data",
    status: Literal[
        "recebendo_proposta", "propostas_encerradas", "em_julgamento",
        "homologada", "revogada", "anulada", "cancelada"
    ] | None = None,
    uf: Literal[
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ] | None = None,
    modalidade: int | None = None,
    esfera: Literal["F", "E", "D", "M"] | None = None,
    pagina: int = 1,
    quantidade: int = 10,
) -> str:
    """
    Busca licitações no Portal Nacional de Contratações Públicas (PNCP).

    Args:
        consulta: Termo de busca (ex: 'toner', 'consultoria de TI', 'obras')
        tipo_documento: Tipo do documento — 'edital' (padrão), 'ata' ou 'contrato'
        ordenacao: Ordenação — '-data' (mais recentes, padrão), 'data' (mais antigos), 'relevancia'
        status: Situação — 'recebendo_proposta' (abertas), 'propostas_encerradas' (encerradas).
                Deixar vazio retorna todos os status.
        uf: Sigla do estado para filtrar (ex: 'SP', 'RJ', 'MG'). Deixar vazio busca em todo o Brasil.
        modalidade: Código da modalidade de contratação.
                    6=Pregão Eletrônico, 7=Pregão Presencial, 8=Dispensa de Licitação,
                    9=Inexigibilidade, 4=Concorrência Eletrônica, 5=Concorrência Presencial.
        esfera: Esfera de governo — 'F' (Federal), 'E' (Estadual), 'D' (Distrital), 'M' (Municipal)
        pagina: Número da página (padrão: 1)
        quantidade: Resultados por página (padrão: 10, máximo recomendado: 50)
    """
    resultado = buscar(
        q=consulta,
        tipos_documento=tipo_documento,
        ordenacao=ordenacao,
        status=status,
        ufs=uf,
        modalidades=modalidade,
        esferas=esfera,
        pagina=pagina,
        tam_pagina=quantidade,
    )
    return json.dumps(resultado, ensure_ascii=False)


def obter_itens_licitacao(
    cnpj_orgao: str,
    ano: int,
    sequencial: int,
) -> str:
    """
    Retorna os itens (produtos ou serviços) de uma licitação específica.

    Use os campos 'orgao_cnpj', 'ano' e 'numero_sequencial' retornados por
    buscar_licitacoes para montar os parâmetros.

    Args:
        cnpj_orgao: CNPJ do órgão responsável pela licitação (ex: '22980999000115')
        ano: Ano da licitação (ex: 2026)
        sequencial: Número sequencial da licitação (ex: 76)
    """
    itens = obter_itens(cnpj_orgao, ano, sequencial)
    return json.dumps(itens, ensure_ascii=False)


def obter_resultado_item_licitacao(
    cnpj_orgao: str,
    ano: int,
    sequencial: int,
    numero_item: int,
) -> str:
    """
    Retorna o resultado/vencedor de um item específico de uma licitação encerrada.

    Disponível apenas para licitações com status 'propostas_encerradas' e
    que já tenham resultado homologado (campo 'tem_resultado' = true nos itens).

    Args:
        cnpj_orgao: CNPJ do órgão responsável pela licitação
        ano: Ano da licitação
        sequencial: Número sequencial da licitação
        numero_item: Número do item (campo 'numeroItem' retornado por obter_itens_licitacao)
    """
    resultados = obter_resultado_item(cnpj_orgao, ano, sequencial, numero_item)
    return json.dumps(resultados, ensure_ascii=False)


def obter_documentos_licitacao(
    cnpj_orgao: str,
    ano: int,
    sequencial: int,
) -> str:
    """
    Retorna os documentos anexados a uma licitação (edital, anexos, atas, etc.).

    Cada documento inclui URL de download, título e tipo.

    Args:
        cnpj_orgao: CNPJ do órgão responsável pela licitação
        ano: Ano da licitação
        sequencial: Número sequencial da licitação
    """
    documentos = obter_documentos(cnpj_orgao, ano, sequencial)
    return json.dumps(documentos, ensure_ascii=False)


def obter_historico_licitacao(
    cnpj_orgao: str,
    ano: int,
    sequencial: int,
) -> str:
    """
    Retorna o histórico de eventos de uma licitação (inclusões, alterações, documentos).

    Útil para acompanhar o andamento e verificar atualizações recentes.

    Args:
        cnpj_orgao: CNPJ do órgão responsável pela licitação
        ano: Ano da licitação
        sequencial: Número sequencial da licitação
    """
    historico = obter_historico(cnpj_orgao, ano, sequencial)
    return json.dumps(historico, ensure_ascii=False)


# Todas as ferramentas disponíveis — importado pelo servidor MCP e pelo agente
FERRAMENTAS = [
    buscar_licitacoes,
    obter_itens_licitacao,
    obter_resultado_item_licitacao,
    obter_documentos_licitacao,
    obter_historico_licitacao,
]
