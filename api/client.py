"""PNCP API client — thin HTTP wrapper around the search endpoint."""

from typing import Literal

import httpx

from .models import SearchPage, SearchResult

# ---------------------------------------------------------------------------
# Type aliases for documented enum params
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

Esfera = Literal["F", "E", "D", "M"]  # Federal, Estadual, Distrital, Municipal

Poder = Literal["E", "L", "J", "M", "D"]  # Executivo, Legislativo, Judiciário, MP, Defensoria

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

MODALIDADE_NAMES: dict[int, str] = {
    1: "Leilão Eletrônico",
    2: "Diálogo Competitivo",
    3: "Concurso",
    4: "Concorrência Eletrônica",
    5: "Concorrência Presencial",
    6: "Pregão Eletrônico",
    7: "Pregão Presencial",
    8: "Dispensa de Licitação",
    9: "Inexigibilidade",
    10: "Manifestação de Interesse",
    11: "Pré-Qualificação",
    12: "Credenciamento",
    13: "Leilão Presencial",
}


class PNCPClient:
    """Synchronous HTTP client for the PNCP public API."""

    SEARCH_BASE = "https://pncp.gov.br/api/search/"

    def __init__(self, timeout: int = 30) -> None:
        self._http = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; pncp-client/1.0)"},
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "PNCPClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # -----------------------------------------------------------------------
    # Search endpoint
    # -----------------------------------------------------------------------

    def search(
        self,
        *,
        q: str,
        tipos_documento: TipoDocumento = "edital",
        ordenacao: Ordenacao = "-data",
        pagina: int = 1,
        tam_pagina: int = 10,
        status: Status | None = None,
        # Filters — IDs, not enumerating all options
        orgaos: str | None = None,       # CNPJ of the org
        unidades: str | None = None,     # unit code
        municipios: str | None = None,   # IBGE municipality code
        # Enumerated filters
        esferas: Esfera | None = None,
        poderes: Poder | None = None,
        ufs: UF | None = None,
        modalidades: Modalidade | None = None,
        # Rarely used filters — mapped but no enum enforcement
        fontes_orcamentarias: str | None = None,
        tipos_margens_preferencia: str | None = None,
        exigencia_conteudo_nacional: bool | None = None,
        possui_emenda_parlamentar: bool | None = None,
    ) -> SearchPage[SearchResult]:
        """Full-text search across PNCP editais, contratos, and atas."""
        params: dict[str, object] = {
            "q": q,
            "tipos_documento": tipos_documento,
            "ordenacao": ordenacao,
            "pagina": pagina,
            "tam_pagina": tam_pagina,
        }

        if status is not None:
            params["status"] = status
        if orgaos is not None:
            params["orgaos"] = orgaos
        if unidades is not None:
            params["unidades"] = unidades
        if municipios is not None:
            params["municipios"] = municipios
        if esferas is not None:
            params["esferas"] = esferas
        if poderes is not None:
            params["poderes"] = poderes
        if ufs is not None:
            params["ufs"] = ufs
        if modalidades is not None:
            params["modalidades"] = modalidades
        if fontes_orcamentarias is not None:
            params["fontes_orcamentarias"] = fontes_orcamentarias
        if tipos_margens_preferencia is not None:
            params["tipos_margens_preferencia"] = tipos_margens_preferencia
        if exigencia_conteudo_nacional is not None:
            params["exigencia_conteudo_nacional"] = str(exigencia_conteudo_nacional).lower()
        if possui_emenda_parlamentar is not None:
            params["possui_emenda_parlamentar"] = str(possui_emenda_parlamentar).lower()

        response = self._http.get(self.SEARCH_BASE, params=params)
        response.raise_for_status()
        data = response.json()

        items = [SearchResult.model_validate(item) for item in data.get("items", [])]
        return SearchPage[SearchResult](
            items=items,
            totalRegistros=data.get("totalRegistros", 0),
            totalPaginas=data.get("totalPaginas", 0),
            numeroPagina=data.get("numeroPagina", pagina),
        )
