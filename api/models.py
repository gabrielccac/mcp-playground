"""Pydantic response models for the PNCP search API."""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SearchResult(BaseModel):
    id: str = ""
    title: str = ""
    description: str = ""
    document_type: str = ""
    item_url: str = ""

    # Identifiers
    ano: str = ""
    numero_sequencial: str = Field(default="", alias="numero_sequencial")
    numero_controle_pncp: str | None = Field(default=None, alias="numeroControlePNCP")

    # Org
    orgao_cnpj: str | None = Field(default=None, alias="orgaoCnpj")
    orgao_nome: str | None = Field(default=None, alias="orgaoNome")
    unidade_nome: str | None = Field(default=None, alias="unidadeNome")

    # Sphere / Branch
    esfera_nome: str | None = Field(default=None, alias="esferaNome")
    poder_nome: str | None = Field(default=None, alias="poderNome")

    # Location
    uf: str | None = None
    municipio_nome: str | None = Field(default=None, alias="municipioNome")

    # Modality
    modalidade_licitacao_nome: str | None = Field(
        default=None, alias="modalidadeLicitacaoNome"
    )

    # Status
    situacao_nome: str | None = Field(default=None, alias="situacaoNome")

    # Dates
    data_publicacao_pncp: datetime | None = Field(
        default=None, alias="dataPublicacaoPncp"
    )
    data_assinatura: datetime | None = Field(default=None, alias="dataAssinatura")
    data_inicio_vigencia: datetime | None = Field(
        default=None, alias="dataInicioVigencia"
    )
    data_fim_vigencia: datetime | None = Field(default=None, alias="dataFimVigencia")

    # Value
    valor_global: float | None = Field(default=None, alias="valorGlobal")

    # Flags
    cancelado: bool | None = None
    tem_resultado: bool | None = Field(default=None, alias="temResultado")
    exigencia_conteudo_nacional: bool | None = Field(
        default=None, alias="exigenciaConteudoNacional"
    )

    # Type labels
    tipo_nome: str | None = Field(default=None, alias="tipoNome")

    model_config = {"populate_by_name": True, "extra": "ignore"}

    def __repr__(self) -> str:
        return f"SearchResult(title={self.title!r}, orgao={self.orgao_nome})"


class SearchPage(BaseModel, Generic[T]):
    """Paginated wrapper returned by /api/search/."""

    items: list[T] = []
    total_registros: int = Field(default=0, alias="totalRegistros")
    total_paginas: int = Field(default=0, alias="totalPaginas")
    pagina: int = Field(default=1, alias="numeroPagina")

    model_config = {"populate_by_name": True, "extra": "ignore"}

    @property
    def has_more(self) -> bool:
        return self.pagina < self.total_paginas
