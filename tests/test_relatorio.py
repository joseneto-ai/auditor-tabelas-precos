from decimal import Decimal
from io import BytesIO

import pandas as pd

from comparador.casamento import comparar_tabelas
from comparador.modelos import Item
from comparador.relatorio import calcular_resumo, gerar_excel


def item(codigo, descricao, preco):
    return Item(codigo, descricao, "un", Decimal(preco))


def resultado_exemplo():
    antiga = [item("A", "Alfa", "100.00"), item("B", "Beta", "50.00"), item("C", "Gama velho", "5.00")]
    nova = [item("A", "Alfa", "120.00"), item("B", "Beta", "50.00"), item("D", "Delta novo", "9.00")]
    return comparar_tabelas(antiga, nova)


def test_resumo():
    resumo = calcular_resumo(resultado_exemplo(), limite_alerta=Decimal("10"))
    assert resumo["itens comparados"] == 2
    assert resumo["reajuste médio %"] == 10.0
    assert resumo["acima do limite"] == 1
    assert resumo["novos"] == 1
    assert resumo["descontinuados"] == 1


def test_excel_tem_todas_as_abas():
    conteudo = gerar_excel(resultado_exemplo(), Decimal("10"))
    abas = pd.ExcelFile(BytesIO(conteudo)).sheet_names
    assert abas == ["Resumo", "Comparados", "Revisar", "Novos", "Descontinuados"]