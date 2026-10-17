"""Erros próprios do projeto."""


class TabelaInvalidaError(Exception):
    """A planilha enviada não pode ser usada (coluna faltando, preço inválido etc.)."""