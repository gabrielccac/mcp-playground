"""PNCP API — search and tender endpoints."""

from typing import Literal

from curl_cffi import requests

from .models import (
    SearchItem,
    SearchResponse,
    TenderDocument,
    TenderHistoryEvent,
    TenderItem,
)

SEARCH_URL = "https://pncp.gov.br/api/search/"
PNCP_BASE  = "https://pncp.gov.br/api/pncp/v1"

_session = requests.Session(impersonate="chrome")

# ---------------------------------------------------------------------------
# Param types
# ---------------------------------------------------------------------------

TipoDocumento = Literal["edital", "ata", "contrato"]

Ordenacao = Literal["-data", "data", "relevancia"]

Status = Literal[
    "recebendo_proposta",
    "propostas_encerradas",
    "em_julgamento",
    "homologada",
    "revogada",
    "anulada",
    "cancelada",
]

Esfera = Literal["F", "E", "D", "M"]

Poder = Literal["E", "L", "J", "M", "D"]

UF = Literal[
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]

Modalidade = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
# 1=Leilão Eletrônico, 2=Diálogo Competitivo, 3=Concurso,
# 4=Concorrência Eletrônica, 5=Concorrência Presencial,
# 6=Pregão Eletrônico, 7=Pregão Presencial, 8=Dispensa de Licitação,
# 9=Inexigibilidade, 10=Manifestação de Interesse,
# 11=Pré-Qualificação, 12=Credenciamento, 13=Leilão Presencial

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(url: str, params: dict | None = None) -> requests.Response:
    resp = _session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp

def _tender_base(orgao_cnpj: str, ano: int, sequencial: int) -> str:
    return f"{PNCP_BASE}/orgaos/{orgao_cnpj}/compras/{ano}/{sequencial}"

# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

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
    """Full-text search across PNCP editais, contratos and atas."""
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

# ---------------------------------------------------------------------------
# Tender details (requires captcha — mocked)
# ---------------------------------------------------------------------------

def get_tender(orgao_cnpj: str, ano: int, sequencial: int, captcha: str = "") -> dict:
    """Get full tender details. Requires a captcha token — returns mock until integrated."""
    if not captcha:
        return {
            "mocked": True,
            "orgao_cnpj": orgao_cnpj,
            "ano": ano,
            "sequencial": sequencial,
            "note": "captcha token required to call portal endpoint",
        }
    url = f"{_tender_base(orgao_cnpj, ano, sequencial)}/portal"
    return _get(url, {"captcha": captcha}).json()

# ---------------------------------------------------------------------------
# Tender items
# ---------------------------------------------------------------------------

def get_tender_items_count(orgao_cnpj: str, ano: int, sequencial: int) -> int:
    """Total number of items in a tender."""
    url = f"{_tender_base(orgao_cnpj, ano, sequencial)}/itens/quantidade"
    return _get(url).json()

def get_tender_items(
    orgao_cnpj: str,
    ano: int,
    sequencial: int,
    pagina: int = 1,
    tamanho_pagina: int = 20,
) -> list[TenderItem]:
    """Items (products/services) being procured in a tender."""
    url = f"{_tender_base(orgao_cnpj, ano, sequencial)}/itens"
    return _get(url, {"pagina": pagina, "tamanhoPagina": tamanho_pagina}).json()

# ---------------------------------------------------------------------------
# Tender documents
# ---------------------------------------------------------------------------

def get_tender_documents_count(orgao_cnpj: str, ano: int, sequencial: int) -> int:
    """Total number of attached documents in a tender."""
    url = f"{_tender_base(orgao_cnpj, ano, sequencial)}/arquivos/quantidade"
    return _get(url).json()

def get_tender_documents(
    orgao_cnpj: str,
    ano: int,
    sequencial: int,
    pagina: int = 1,
    tamanho_pagina: int = 20,
) -> list[TenderDocument]:
    """Attached documents (edital, annexes, etc.) for a tender."""
    url = f"{_tender_base(orgao_cnpj, ano, sequencial)}/arquivos"
    return _get(url, {"pagina": pagina, "tamanhoPagina": tamanho_pagina}).json()

# ---------------------------------------------------------------------------
# Tender history
# ---------------------------------------------------------------------------

def get_tender_history_count(orgao_cnpj: str, ano: int, sequencial: int) -> int:
    """Total number of history events for a tender."""
    url = f"{_tender_base(orgao_cnpj, ano, sequencial)}/historico/quantidade"
    return _get(url).json()

def get_tender_history(
    orgao_cnpj: str,
    ano: int,
    sequencial: int,
    pagina: int = 1,
    tamanho_pagina: int = 20,
) -> list[TenderHistoryEvent]:
    """Audit log / history of changes for a tender."""
    url = f"{_tender_base(orgao_cnpj, ano, sequencial)}/historico"
    return _get(url, {"pagina": pagina, "tamanhoPagina": tamanho_pagina}).json()
