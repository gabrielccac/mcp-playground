"""Response types for the PNCP search API."""

from typing import TypedDict


class SearchResult(TypedDict, total=False):
    id: str
    title: str
    description: str
    document_type: str
    item_url: str
    numero_controle_pncp: str | None

    # Org
    orgao_cnpj: str | None
    orgao_nome: str | None
    unidade_nome: str | None

    # Location
    uf: str | None
    municipio_nome: str | None

    # Classification
    esfera_id: str | None
    esfera_nome: str | None
    poder_id: str | None
    poder_nome: str | None
    modalidade_licitacao_id: str | None
    modalidade_licitacao_nome: str | None
    situacao_id: str | None
    situacao_nome: str | None
    tipo_nome: str | None

    # Dates (strings as returned by the API)
    data_publicacao_pncp: str | None
    data_inicio_vigencia: str | None
    data_fim_vigencia: str | None

    # Value / flags
    valor_global: float | None
    cancelado: bool | None
    tem_resultado: bool | None
    exigencia_conteudo_nacional: bool | None


class SearchPage(TypedDict):
    items: list[SearchResult]
    total_registros: int
    total_paginas: int
    pagina: int
