"""Leitura e validação das planilhas de preços."""
from decimal import Decimal, InvalidOperation
from typing import BinaryIO

import pandas as pd

from comparador.excecoes import TabelaInvalidaError
from comparador.modelos import Item

COLUNAS_OBRIGATORIAS = ["codigo", "descricao", "unidade", "preco"]


def converter_preco(texto: str, linha: int) -> Decimal:
    """Aceita '12.50', '12,50' e 'R$ 1.234,50'. Nunca usa float."""
    limpo = texto.replace("R$", "").replace(" ", "").strip()
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    try:
        preco = Decimal(limpo)
    except InvalidOperation:
        raise TabelaInvalidaError(f"Linha {linha}: preço inválido ({texto!r}).") from None
    if preco <= 0:
        raise TabelaInvalidaError(f"Linha {linha}: o preço precisa ser maior que zero.")
    return preco.quantize(Decimal("0.01"))


def ler_tabela(arquivo: str | BinaryIO) -> list[Item]:
    try:
        tabela = pd.read_excel(arquivo, dtype=str)
    except Exception as erro:
        raise TabelaInvalidaError(f"Não consegui abrir a planilha: {erro}") from erro

    tabela.columns = [str(c).strip().lower() for c in tabela.columns]
    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in tabela.columns]
    if faltando:
        raise TabelaInvalidaError(f"Faltam as colunas: {', '.join(faltando)}.")

    tabela = tabela.dropna(how="all")
    itens: list[Item] = []
    codigos_vistos: set[str] = set()
    for posicao, linha in tabela.iterrows():
        numero_linha = int(posicao) + 2  # +2: cabeçalho e contagem a partir do 1
        if linha[COLUNAS_OBRIGATORIAS].isna().any():
            raise TabelaInvalidaError(f"Linha {numero_linha}: há campos vazios.")
        codigo = str(linha["codigo"]).strip()
        if codigo in codigos_vistos:
            raise TabelaInvalidaError(f"Linha {numero_linha}: código repetido ({codigo}).")
        codigos_vistos.add(codigo)
        itens.append(
            Item(
                codigo=codigo,
                descricao=str(linha["descricao"]).strip(),
                unidade=str(linha["unidade"]).strip(),
                preco=converter_preco(str(linha["preco"]), numero_linha),
            )
        )
    if not itens:
        raise TabelaInvalidaError("A planilha não tem nenhum item.")
    return itens