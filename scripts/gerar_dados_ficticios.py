"""Gera duas tabelas de preços FICTÍCIAS para testar o projeto.

Rode a partir da pasta do projeto:  python scripts/gerar_dados_ficticios.py
"""
import random
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pandas as pd

PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"

# (nome, unidade, preço base, medidas)
FAMILIAS = [
    ("Tubo PVC esgoto", "un", 22.0, ["40 mm", "50 mm", "75 mm", "100 mm", "150 mm"]),
    ("Joelho PVC 90 graus", "un", 4.5, ["25 mm", "32 mm", "40 mm", "50 mm", "75 mm", "100 mm"]),
    ("Luva PVC soldável", "un", 3.2, ["20 mm", "25 mm", "32 mm", "40 mm", "50 mm"]),
    ("Registro de gaveta", "un", 32.0, ["1/2 pol", "3/4 pol", "1 pol", "1 1/4 pol"]),
    ("Fio flexível", "rl", 140.0, ["1,5 mm2", "2,5 mm2", "4 mm2", "6 mm2", "10 mm2"]),
    ("Cabo de cobre", "m", 8.0, ["16 mm2", "25 mm2", "35 mm2", "50 mm2"]),
    ("Disjuntor monopolar", "un", 14.0, ["10 A", "16 A", "20 A", "25 A", "32 A", "40 A"]),
    ("Tomada embutir", "un", 11.0, ["10 A", "20 A"]),
    ("Cimento", "sc", 38.0, ["CP-II 50 kg", "CP-III 50 kg", "CP-V 50 kg"]),
    ("Argamassa colante", "sc", 19.0, ["AC-I 20 kg", "AC-II 20 kg", "AC-III 20 kg"]),
    ("Tinta acrílica fosca", "l", 28.0, ["branco 3,6 l", "branco 18 l", "gelo 3,6 l", "gelo 18 l"]),
    ("Massa corrida", "l", 17.0, ["3,6 l", "18 l", "25 kg"]),
    ("Parafuso sextavado", "cx", 45.0, ["1/4 x 2", "5/16 x 3", "3/8 x 4", "1/2 x 5"]),
    ("Prego com cabeça", "kg", 12.0, ["15 x 15", "17 x 21", "18 x 27", "19 x 36"]),
    ("Disco de corte", "un", 7.5, ["4 1/2 pol", "7 pol", "9 pol"]),
    ("Broca para concreto", "un", 9.0, ["6 mm", "8 mm", "10 mm", "12 mm"]),
    ("Fita isolante", "rl", 6.0, ["10 m", "20 m", "50 m"]),
    ("Lâmpada LED", "un", 8.0, ["9 W", "12 W", "15 W", "20 W"]),
    ("Luminária de emergência", "un", 59.0, ["30 led", "60 led"]),
    ("Telha cerâmica", "un", 2.8, ["tipo romana", "tipo colonial", "tipo francesa"]),
]
UNIDADES_ESCRITAS = {"un": ["un", "UN", "und", "Und."], "sc": ["sc", "SC", "saco"],
                     "rl": ["rl", "rolo"], "kg": ["kg", "KG"], "m": ["m", "mt"],
                     "l": ["l", "L", "lt"], "cx": ["cx", "CX", "caixa"]}


def dinheiro(valor: float) -> Decimal:
    return Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def reescrever(descricao: str, sorteio: random.Random) -> str:
    """Muda o jeito de escrever, sem mudar o produto."""
    receitas = [
        lambda d: d.upper(),
        lambda d: d.replace(" mm", "mm").replace(" kg", "kg").replace(" pol", "pol"),
        lambda d: d.replace("Registro", "Reg.").replace("Tubo", "Tb").replace("Lâmpada", "Lamp."),
        lambda d: d.replace("PVC", "P.V.C.").replace("-", ""),
        lambda d: d.replace("flexível", "flexivel").replace("cerâmica", "ceramica"),
    ]
    for receita in sorteio.sample(receitas, k=sorteio.choice([1, 2])):
        descricao = receita(descricao)
    return descricao


def gerar() -> None:
    sorteio = random.Random(42)  # semente fixa: sempre gera os mesmos dados
    antiga = []
    for numero_familia, (nome, unidade, base, medidas) in enumerate(FAMILIAS, start=1):
        for posicao, medida in enumerate(medidas, start=1):
            preco = dinheiro(base * (1 + 0.4 * (posicao - 1)))
            antiga.append({"codigo": f"F{numero_familia:02d}-{posicao:02d}",
                           "descricao": f"{nome} {medida}", "unidade": unidade, "preco": preco})

    descontinuados = {item["codigo"] for item in sorteio.sample(antiga, k=6)}
    unidade_trocada = {item["codigo"] for item in sorteio.sample(antiga, k=3)}
    nova = []
    for item in antiga:
        if item["codigo"] in descontinuados:
            continue
        sorte = sorteio.random()
        if sorte < 0.62:
            reajuste = sorteio.uniform(-0.02, 0.04)
        elif sorte < 0.88:
            reajuste = sorteio.uniform(0.05, 0.09)
        else:
            reajuste = sorteio.uniform(0.12, 0.25)  # reajuste exagerado
        codigo = item["codigo"]
        descricao = item["descricao"]
        if sorteio.random() < 0.40:  # o fornecedor mudou o código
            codigo = "N" + codigo
        if sorteio.random() < 0.35:
            descricao = reescrever(descricao, sorteio)
        unidade = "cx" if codigo in unidade_trocada or item["codigo"] in unidade_trocada else item["unidade"]
        if unidade == item["unidade"]:
            unidade = sorteio.choice(UNIDADES_ESCRITAS.get(unidade, [unidade]))
        nova.append({"codigo": codigo, "descricao": descricao, "unidade": unidade,
                     "preco": dinheiro(float(item["preco"]) * (1 + reajuste))})

    produtos_novos = ["Fita veda rosca 18 mm", "Silicone acético 280 g", "Trena emborrachada 5 m",
                      "Luva de raspa cano curto", "Óculos de proteção incolor",
                      "Nível de bolha 40 cm", "Espátula de aço 8 cm", "Rolo de lã 23 cm"]
    for posicao, descricao in enumerate(produtos_novos, start=1):
        nova.append({"codigo": f"X{posicao:02d}", "descricao": descricao, "unidade": "un",
                     "preco": dinheiro(sorteio.uniform(5, 40))})

    PASTA_DADOS.mkdir(exist_ok=True)
    for nome_arquivo, linhas in [("tabela_anterior.xlsx", antiga), ("tabela_nova.xlsx", nova)]:
        pd.DataFrame(linhas).to_excel(PASTA_DADOS / nome_arquivo, index=False)
    print(f"Tabela anterior: {len(antiga)} itens | Tabela nova: {len(nova)} itens")
    print(f"Arquivos criados em: {PASTA_DADOS}")


if __name__ == "__main__":
    gerar()