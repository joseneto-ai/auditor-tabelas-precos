"""Transforma o resultado da comparação em tabelas, números e Excel."""
from decimal import Decimal
from io import BytesIO

import pandas as pd

from comparador.modelos import Item, Par, ResultadoComparacao

COLUNAS_PARES = [
    "código antigo", "código novo", "descrição antiga", "descrição nova",
    "preço antigo", "preço novo", "variação %", "similaridade", "motivo",
]


def pares_em_tabela(pares: list[Par]) -> pd.DataFrame:
    linhas = [
        [
            p.antigo.codigo, p.novo.codigo, p.antigo.descricao, p.novo.descricao,
            float(p.antigo.preco), float(p.novo.preco),
            float(p.variacao_percentual), p.similaridade, p.motivo,
        ]
        for p in pares
    ]
    tabela = pd.DataFrame(linhas, columns=COLUNAS_PARES)
    return tabela.sort_values("variação %", ascending=False, ignore_index=True)


def itens_em_tabela(itens: list[Item]) -> pd.DataFrame:
    linhas = [[i.codigo, i.descricao, i.unidade, float(i.preco)] for i in itens]
    return pd.DataFrame(linhas, columns=["código", "descrição", "unidade", "preço"])


def calcular_resumo(resultado: ResultadoComparacao, limite_alerta: Decimal) -> dict[str, float | int]:
    variacoes = [p.variacao_percentual for p in resultado.pares_confiaveis]
    media = sum(variacoes) / len(variacoes) if variacoes else Decimal(0)
    return {
        "itens comparados": len(resultado.pares_confiaveis),
        "reajuste médio %": round(float(media), 2),
        "acima do limite": sum(1 for v in variacoes if v >= limite_alerta),
        "para revisão": len(resultado.pares_para_revisao),
        "novos": len(resultado.novos),
        "descontinuados": len(resultado.descontinuados),
    }


def gerar_excel(resultado: ResultadoComparacao, limite_alerta: Decimal) -> bytes:
    resumo = calcular_resumo(resultado, limite_alerta)
    memoria = BytesIO()
    with pd.ExcelWriter(memoria, engine="openpyxl") as escritor:
        pd.DataFrame({"indicador": list(resumo), "valor": list(resumo.values())}).to_excel(
            escritor, sheet_name="Resumo", index=False
        )
        pares_em_tabela(resultado.pares_confiaveis).to_excel(escritor, sheet_name="Comparados", index=False)
        pares_em_tabela(resultado.pares_para_revisao).to_excel(escritor, sheet_name="Revisar", index=False)
        itens_em_tabela(resultado.novos).to_excel(escritor, sheet_name="Novos", index=False)
        itens_em_tabela(resultado.descontinuados).to_excel(escritor, sheet_name="Descontinuados", index=False)
    return memoria.getvalue()