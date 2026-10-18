"""Interface do Auditor de Tabelas de Preços (Streamlit)."""
from decimal import Decimal
from pathlib import Path

import streamlit as st

from comparador.casamento import comparar_tabelas
from comparador.excecoes import TabelaInvalidaError
from comparador.leitura import ler_tabela
from comparador.relatorio import (
    calcular_resumo,
    gerar_excel,
    itens_em_tabela,
    pares_em_tabela,
)

st.set_page_config(page_title="Auditor de Tabelas de Preços", layout="wide")
st.title("Auditor de Tabelas de Preços")
st.caption("Versão 1 (protótipo) · use apenas dados fictícios ou autorizados.")

PASTA_DADOS = Path(__file__).parent / "dados"
TIPO_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

with st.expander("Não tem planilhas? Baixe exemplos fictícios para testar"):
    for nome_arquivo in ["tabela_anterior.xlsx", "tabela_nova.xlsx"]:
        caminho = PASTA_DADOS / nome_arquivo
        if caminho.exists():
            st.download_button(
                f"Baixar {nome_arquivo}",
                data=caminho.read_bytes(),
                file_name=nome_arquivo,
                mime=TIPO_XLSX,
                key=f"exemplo_{nome_arquivo}",
            )

coluna_a, coluna_b = st.columns(2)
arquivo_antigo = coluna_a.file_uploader("Tabela anterior (.xlsx)", type=["xlsx"])
arquivo_novo = coluna_b.file_uploader("Tabela nova (.xlsx)", type=["xlsx"])
limite = st.number_input("Alertar reajustes a partir de (%)", min_value=0.0, value=10.0, step=0.5)

if arquivo_antigo and arquivo_novo:
    try:
        antiga = ler_tabela(arquivo_antigo)
        nova = ler_tabela(arquivo_novo)
    except TabelaInvalidaError as erro:
        st.error(f"Problema na planilha: {erro}")
        st.stop()

    limite_alerta = Decimal(str(limite))
    resultado = comparar_tabelas(antiga, nova)
    resumo = calcular_resumo(resultado, limite_alerta)

    colunas = st.columns(len(resumo))
    for coluna, (nome, valor) in zip(colunas, resumo.items()):
        coluna.metric(nome, valor)

    abas = st.tabs(["Comparados", "Para revisar", "Novos", "Descontinuados"])
    with abas[0]:
        st.dataframe(pares_em_tabela(resultado.pares_confiaveis), width="stretch")
    with abas[1]:
        st.info("Casamentos de que o programa não tem certeza. Uma pessoa deve conferir.")
        st.dataframe(pares_em_tabela(resultado.pares_para_revisao), width="stretch")
    with abas[2]:
        st.dataframe(itens_em_tabela(resultado.novos), width="stretch")
    with abas[3]:
        st.dataframe(itens_em_tabela(resultado.descontinuados), width="stretch")

    st.download_button(
        "Baixar relatório em Excel",
        data=gerar_excel(resultado, limite_alerta),
        file_name="relatorio_comparacao.xlsx",
        mime=TIPO_XLSX,
    )
else:
    st.info("Envie as duas planilhas para começar. Colunas: codigo, descricao, unidade, preco.")