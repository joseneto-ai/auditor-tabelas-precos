"""Descobre qual item da tabela antiga é qual item da tabela nova."""
from rapidfuzz import fuzz, process

from comparador.modelos import Item, Par, ResultadoComparacao
from comparador.normalizacao import (
    extrair_numeros,
    normalizar_descricao,
    normalizar_unidade,
)

LIMITE_AUTOMATICO = 90  # a partir daqui, aceitamos sozinhos
LIMITE_REVISAO = 70  # entre 70 e 89, uma pessoa precisa conferir


def _mesma_unidade(a: Item, b: Item) -> bool:
    return normalizar_unidade(a.unidade) == normalizar_unidade(b.unidade)


def comparar_tabelas(antiga: list[Item], nova: list[Item]) -> ResultadoComparacao:
    confiaveis: list[Par] = []
    revisao: list[Par] = []
    descontinuados: list[Item] = []
    disponiveis = {item.codigo: item for item in nova}  # novos ainda sem par

    # Passo 1: mesmo código = mesmo produto.
    sem_codigo_igual: list[Item] = []
    for antigo in antiga:
        novo = disponiveis.pop(antigo.codigo, None)
        if novo is None:
            sem_codigo_igual.append(antigo)
        elif _mesma_unidade(antigo, novo):
            confiaveis.append(Par(antigo, novo, 100.0, "código"))
        else:
            revisao.append(Par(antigo, novo, 100.0, "unidade diferente"))

    # Passo 2: sem código igual, compara as descrições parecidas.
    for antigo in sem_codigo_igual:
        descricao = normalizar_descricao(antigo.descricao)
        numeros = extrair_numeros(descricao)
        candidatos = {}
        for codigo, item in disponiveis.items():
            candidato = normalizar_descricao(item.descricao)
            if extrair_numeros(candidato) == numeros:  # medidas diferentes: outro produto
                candidatos[codigo] = candidato
        melhor = process.extractOne(descricao, candidatos, scorer=fuzz.token_sort_ratio)
        if melhor is None or melhor[1] < LIMITE_REVISAO:
            descontinuados.append(antigo)
            continue
        _, nota, codigo = melhor
        novo = disponiveis.pop(codigo)
        if nota >= LIMITE_AUTOMATICO and _mesma_unidade(antigo, novo):
            confiaveis.append(Par(antigo, novo, round(nota, 1), "descrição"))
        elif not _mesma_unidade(antigo, novo):
            revisao.append(Par(antigo, novo, round(nota, 1), "unidade diferente"))
        else:
            revisao.append(Par(antigo, novo, round(nota, 1), "descrição parecida"))

    return ResultadoComparacao(
        pares_confiaveis=confiaveis,
        pares_para_revisao=revisao,
        novos=list(disponiveis.values()),
        descontinuados=descontinuados,
    )