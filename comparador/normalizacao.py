"""Funções que deixam textos e unidades num formato padrão para comparar."""
import re
import unicodedata

UNIDADES_PADRAO = {
    "un": "un", "und": "un", "unid": "un", "unidade": "un", "pc": "un", "pç": "un",
    "kg": "kg", "quilo": "kg",
    "m": "m", "mt": "m", "metro": "m",
    "l": "l", "lt": "l", "litro": "l",
    "cx": "cx", "caixa": "cx",
    "sc": "sc", "saco": "sc",
    "rl": "rl", "rolo": "rl",
}


def remover_acentos(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def normalizar_unidade(unidade: str) -> str:
    limpa = remover_acentos(unidade).lower().strip().strip(".")
    return UNIDADES_PADRAO.get(limpa, limpa)


def normalizar_descricao(descricao: str) -> str:
    """'CIM. CPII 50KG' -> 'cim cpii 50 kg'"""
    texto = remover_acentos(descricao).lower()
    texto = re.sub(r"[^a-z0-9]+", " ", texto)  # pontuação vira espaço
    texto = re.sub(r"(\d)([a-z])", r"\1 \2", texto)  # 50kg -> 50 kg
    texto = re.sub(r"([a-z])(\d)", r"\1 \2", texto)  # mm2 -> mm 2
    return re.sub(r"\s+", " ", texto).strip()


def extrair_numeros(descricao_normalizada: str) -> tuple[str, ...]:
    """Os números de uma descrição: '50 mm' e '40 mm' são produtos diferentes."""
    return tuple(sorted(re.findall(r"\d+", descricao_normalizada)))