"""Estruturas de dados do projeto."""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True)
class Item:
    """Uma linha da tabela de preços."""

    codigo: str
    descricao: str
    unidade: str
    preco: Decimal


@dataclass(frozen=True)
class Par:
    """Um item da tabela antiga ligado ao seu item na tabela nova."""

    antigo: Item
    novo: Item
    similaridade: float  # 100 quando o código é igual
    motivo: str  # "código", "descrição" ou o motivo da revisão

    @property
    def variacao_percentual(self) -> Decimal:
        diferenca = self.novo.preco - self.antigo.preco
        return (diferenca / self.antigo.preco * 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )


@dataclass(frozen=True)
class ResultadoComparacao:
    """Tudo o que a comparação descobriu."""

    pares_confiaveis: list[Par]
    pares_para_revisao: list[Par]
    novos: list[Item]
    descontinuados: list[Item]