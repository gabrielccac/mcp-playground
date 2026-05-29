"""PNCP API — search endpoint."""

from typing import Literal

import httpx

from .models import SearchPage

SEARCH_URL = "https://pncp.gov.br/api/search/"

_http = httpx.Client(
    headers={"User-Agent": "Mozilla/5.0 (compatible; pncp-client/1.0)"},
    timeout=30,
    http2=False,
)

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
# Endpoints
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
) -> SearchPage:
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

    data = _http.get(SEARCH_URL, params=params).raise_for_status().json()

    return SearchPage(
        items=data.get("items", []),
        total_registros=data.get("totalRegistros", 0),
        total_paginas=data.get("totalPaginas", 0),
        pagina=data.get("numeroPagina", pagina),
    )
