from typing import TypedDict


class SearchItem(TypedDict, total=False):
    id: str
    title: str
    description: str
    document_type: str
    item_url: str
    numero_controle_pncp: str | None
    numero_sequencial: str | None
    ano: str | None
    orgao_cnpj: str | None
    orgao_nome: str | None
    unidade_nome: str | None
    uf: str | None
    municipio_nome: str | None
    esfera_id: str | None
    esfera_nome: str | None
    poder_id: str | None
    poder_nome: str | None
    modalidade_licitacao_id: str | None
    modalidade_licitacao_nome: str | None
    situacao_id: str | None
    situacao_nome: str | None
    tipo_nome: str | None
    data_publicacao_pncp: str | None
    data_inicio_vigencia: str | None
    data_fim_vigencia: str | None
    valor_global: float | None
    cancelado: bool | None
    tem_resultado: bool | None
    exigencia_conteudo_nacional: bool | None


class SearchResponse(TypedDict):
    items: list[SearchItem]
    total: int
    total_paginas: int
    pagina: int


class TenderItem(TypedDict, total=False):
    numeroItem: int
    descricao: str
    materialOuServico: str
    materialOuServicoNome: str
    valorUnitarioEstimado: float | None
    valorTotal: float | None
    quantidade: float
    unidadeMedida: str
    criterioJulgamentoId: int | None
    criterioJulgamentoNome: str | None
    situacaoCompraItem: int | None
    situacaoCompraItemNome: str | None
    temResultado: bool
    dataInclusao: str | None
    dataAtualizacao: str | None
    orcamentoSigiloso: bool


class TenderItemResult(TypedDict, total=False):
    niFornecedor: str
    nomeRazaoSocialFornecedor: str
    tipoPessoa: str
    porteFornecedorId: int | None
    porteFornecedorNome: str | None
    numeroItem: int
    sequencialResultado: int
    valorUnitarioHomologado: float | None
    valorTotalHomologado: float | None
    quantidadeHomologada: float | None
    percentualDesconto: float | None
    ordemClassificacaoSrp: int | None
    dataResultado: str | None
    dataInclusao: str | None
    dataAtualizacao: str | None
    dataCancelamento: str | None
    situacaoCompraItemResultadoId: int | None
    situacaoCompraItemResultadoNome: str | None
    numeroControlePNCPCompra: str | None
    codigoPais: str | None
    naturezaJuridicaId: str | None
    naturezaJuridicaNome: str | None
    indicadorSubcontratacao: bool
    aplicacaoBeneficioMeEpp: bool


class TenderDocument(TypedDict, total=False):
    uri: str
    url: str
    cnpj: str
    tipoDocumentoId: int | None
    tipoDocumentoDescricao: str | None
    tipoDocumentoNome: str | None
    statusAtivo: bool
    anoCompra: int
    sequencialCompra: int
    dataPublicacaoPncp: str | None
    titulo: str | None
    sequencialDocumento: int


class TenderHistoryEvent(TypedDict, total=False):
    justificativa: str | None
    tipoLogManutencao: int
    tipoLogManutencaoNome: str | None
    categoriaLogManutencao: int
    categoriaLogManutencaoNome: str | None
    logManutencaoDataInclusao: str | None
    usuarioNome: str | None
    compraOrgaoCnpj: str | None
    compraAno: int | None
    compraSequencial: int | None
    documentoTipo: str | None
    documentoTitulo: str | None
    documentoSequencial: int | None
