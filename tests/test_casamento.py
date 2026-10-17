from decimal import Decimal

from comparador.casamento import comparar_tabelas
from comparador.modelos import Item


def item(codigo: str, descricao: str, unidade: str = "un", preco: str = "10.00") -> Item:
    return Item(codigo, descricao, unidade, Decimal(preco))


def test_mesmo_codigo_casa_direto():
    resultado = comparar_tabelas([item("A1", "Parafuso")], [item("A1", "Parafuso", preco="11.00")])
    assert len(resultado.pares_confiaveis) == 1
    assert resultado.pares_confiaveis[0].motivo == "código"


def test_variacao_percentual_usa_decimal():
    resultado = comparar_tabelas([item("A1", "Parafuso")], [item("A1", "Parafuso", preco="11.00")])
    assert resultado.pares_confiaveis[0].variacao_percentual == Decimal("10.00")


def test_descricao_reescrita_casa_por_similaridade():
    antiga = [item("A1", "Cimento CP-II 50 kg", "sc")]
    nova = [item("B9", "CIMENTO CPII 50KG", "SC")]
    resultado = comparar_tabelas(antiga, nova)
    assert len(resultado.pares_confiaveis) == 1
    assert resultado.pares_confiaveis[0].motivo == "descrição"


def test_item_novo_e_descontinuado():
    antiga = [item("A1", "Parafuso sextavado")]
    nova = [item("Z9", "Martelo de borracha")]
    resultado = comparar_tabelas(antiga, nova)
    assert [i.codigo for i in resultado.descontinuados] == ["A1"]
    assert [i.codigo for i in resultado.novos] == ["Z9"]
    assert resultado.pares_confiaveis == []


def test_unidade_diferente_vai_para_revisao():
    resultado = comparar_tabelas([item("A1", "Prego", "kg")], [item("A1", "Prego", "cx")])
    assert resultado.pares_confiaveis == []
    assert resultado.pares_para_revisao[0].motivo == "unidade diferente"


def test_medida_diferente_nao_casa():
    antiga = [item("A1", "Tubo PVC esgoto 40 mm")]
    nova = [item("B1", "Tubo PVC esgoto 50 mm")]
    resultado = comparar_tabelas(antiga, nova)
    assert resultado.pares_confiaveis == []
    assert resultado.pares_para_revisao == []
    assert len(resultado.descontinuados) == 1
    assert len(resultado.novos) == 1


def test_descricao_parecida_demais_para_aceitar_sozinha_vai_para_revisao():
    antiga = [item("A1", "Registro de gaveta 1 pol")]
    nova = [item("B1", "Reg. de gaveta 1 pol")]
    resultado = comparar_tabelas(antiga, nova)
    assert resultado.pares_confiaveis == []
    assert resultado.pares_para_revisao[0].motivo == "descrição parecida"