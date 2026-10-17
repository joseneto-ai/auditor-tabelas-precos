from comparador.normalizacao import (
    extrair_numeros,
    normalizar_descricao,
    normalizar_unidade,
    remover_acentos,
)


def test_remover_acentos():
    assert remover_acentos("Lâmpada cerâmica") == "Lampada ceramica"


def test_descricao_com_pontuacao_e_unidade_colada():
    assert normalizar_descricao("CIM. CPII 50KG") == "cim cpii 50 kg"


def test_descricao_com_hifen():
    assert normalizar_descricao("Cimento CP-II 50 kg") == "cimento cp ii 50 kg"


def test_unidades_diferentes_viram_a_mesma():
    assert normalizar_unidade("Und.") == "un"
    assert normalizar_unidade("UN") == "un"
    assert normalizar_unidade("saco") == "sc"


def test_unidade_desconhecida_so_e_limpa():
    assert normalizar_unidade(" Pallet ") == "pallet"


def test_numeros_diferentes_sao_detectados():
    assert extrair_numeros("tubo 40 mm") != extrair_numeros("tubo 50 mm")