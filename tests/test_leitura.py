from decimal import Decimal

import pandas as pd
import pytest

from comparador.excecoes import TabelaInvalidaError
from comparador.leitura import converter_preco, ler_tabela


def salvar(tmp_path, linhas, colunas=("codigo", "descricao", "unidade", "preco")):
    caminho = tmp_path / "tabela.xlsx"
    pd.DataFrame(linhas, columns=list(colunas)).to_excel(caminho, index=False)
    return caminho


def test_le_tabela_valida(tmp_path):
    caminho = salvar(tmp_path, [["001", "Parafuso", "un", "12,50"]])
    itens = ler_tabela(caminho)
    assert itens[0].codigo == "001"  # o zero à esquerda foi preservado
    assert itens[0].preco == Decimal("12.50")


def test_coluna_faltando(tmp_path):
    caminho = salvar(tmp_path, [["001", "Parafuso", "un"]], colunas=("codigo", "descricao", "unidade"))
    with pytest.raises(TabelaInvalidaError, match="preco"):
        ler_tabela(caminho)


def test_codigo_repetido(tmp_path):
    caminho = salvar(tmp_path, [["001", "A", "un", "1"], ["001", "B", "un", "2"]])
    with pytest.raises(TabelaInvalidaError, match="repetido"):
        ler_tabela(caminho)


def test_arquivo_que_nao_e_planilha(tmp_path):
    caminho = tmp_path / "lixo.xlsx"
    caminho.write_text("isto não é uma planilha")
    with pytest.raises(TabelaInvalidaError):
        ler_tabela(caminho)


@pytest.mark.parametrize(
    "texto, esperado",
    [("12.5", "12.50"), ("12,5", "12.50"), ("R$ 1.234,50", "1234.50")],
)
def test_formatos_de_preco(texto, esperado):
    assert converter_preco(texto, linha=2) == Decimal(esperado)


@pytest.mark.parametrize("texto", ["abc", "0", "-3"])
def test_preco_invalido(texto):
    with pytest.raises(TabelaInvalidaError):
        converter_preco(texto, linha=2)