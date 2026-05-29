from typing import Literal

from curl_cffi import requests

from .models import (
    SearchResponse,
    TenderDocument,
    TenderHistoryEvent,
    TenderItem,
    TenderItemResult,
)

SEARCH_URL = "https://pncp.gov.br/api/search/"
PNCP_BASE  = "https://pncp.gov.br/api/pncp/v1"

_session = requests.Session(impersonate="chrome")

TipoDocumento = Literal["edital", "ata", "contrato"]
Ordenacao     = Literal["-data", "data", "relevancia"]
Status        = Literal[
    "recebendo_proposta", "propostas_encerradas", "em_julgamento",
    "homologada", "revogada", "anulada", "cancelada",
]
Esfera        = Literal["F", "E", "D", "M"]
Poder         = Literal["E", "L", "J", "M", "D"]
UF            = Literal[
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]
Modalidade    = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]


def _get(url: str, params: dict | None = None) -> requests.Response:
    resp = _session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp


def _tender_base(orgao_cnpj: str, ano: int, sequencial: int) -> str:
    return f"{PNCP_BASE}/orgaos/{orgao_cnpj}/compras/{ano}/{sequencial}"


def search(
    q: str,
    tipos_documento: TipoDocumento = "edital",
    ordenacao: Ordenacao = "-data",
    pagina: int = 1,
    tam_pagina: int = 10,
    status: Status | None = None,
    ufs: UF | None = None,
    modalidades: Modalidade | None = None,
    esferas: Esfera | None = None,
    poderes: Poder | None = None,
    orgaos: str | None = None,
    unidades: str | None = None,
    municipios: str | None = None,
    fontes_orcamentarias: str | None = None,
    tipos_margens_preferencia: str | None = None,
    exigencia_conteudo_nacional: bool | None = None,
    possui_emenda_parlamentar: bool | None = None,
) -> SearchResponse:
    params = {k: v for k, v in {
        "q": q,
        "tipos_documento": tipos_documento,
        "ordenacao": ordenacao,
        "pagina": pagina,
        "tam_pagina": tam_pagina,
        "status": status,
        "ufs": ufs,
        "modalidades": modalidades,
        "esferas": esferas,
        "poderes": poderes,
        "orgaos": orgaos,
        "unidades": unidades,
        "municipios": municipios,
        "fontes_orcamentarias": fontes_orcamentarias,
        "tipos_margens_preferencia": tipos_margens_preferencia,
        "exigencia_conteudo_nacional": (
            str(exigencia_conteudo_nacional).lower()
            if exigencia_conteudo_nacional is not None else None
        ),
        "possui_emenda_parlamentar": (
            str(possui_emenda_parlamentar).lower()
            if possui_emenda_parlamentar is not None else None
        ),
    }.items() if v is not None}

    data = _get(SEARCH_URL, params).json()
    total = data.get("total", 0)

    return SearchResponse(
        items=data.get("items", []),
        total=total,
        total_paginas=-(-total // tam_pagina),
        pagina=pagina,
    )


def get_tender(orgao_cnpj: str, ano: int, sequencial: int, captcha: str = "") -> dict:
    if not captcha:
        return {"mocked": True, "orgao_cnpj": orgao_cnpj, "ano": ano, "sequencial": sequencial}
    return _get(f"{_tender_base(orgao_cnpj, ano, sequencial)}/portal", {"captcha": captcha}).json()


def get_tender_items(
    orgao_cnpj: str, ano: int, sequencial: int,
    pagina: int = 1, tamanho_pagina: int = 50,
) -> list[TenderItem]:
    return _get(f"{_tender_base(orgao_cnpj, ano, sequencial)}/itens",
                {"pagina": pagina, "tamanhoPagina": tamanho_pagina}).json()


def get_tender_item_results(
    orgao_cnpj: str, ano: int, sequencial: int, numero_item: int,
) -> list[TenderItemResult]:
    return _get(f"{_tender_base(orgao_cnpj, ano, sequencial)}/itens/{numero_item}/resultados").json()


def get_tender_documents(
    orgao_cnpj: str, ano: int, sequencial: int,
    pagina: int = 1, tamanho_pagina: int = 50,
) -> list[TenderDocument]:
    return _get(f"{_tender_base(orgao_cnpj, ano, sequencial)}/arquivos",
                {"pagina": pagina, "tamanhoPagina": tamanho_pagina}).json()


def get_tender_history(
    orgao_cnpj: str, ano: int, sequencial: int,
    pagina: int = 1, tamanho_pagina: int = 50,
) -> list[TenderHistoryEvent]:
    return _get(f"{_tender_base(orgao_cnpj, ano, sequencial)}/historico",
                {"pagina": pagina, "tamanhoPagina": tamanho_pagina}).json()
