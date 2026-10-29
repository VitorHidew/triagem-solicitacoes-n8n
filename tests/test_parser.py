from src.parser import interpretar_resposta


def test_parser_aceita_categoria_simples():
    assert interpretar_resposta("atraso") == ("atraso", False)


def test_parser_aceita_json():
    assert interpretar_resposta('{"categoria":"cobrança"}') == ("cobrança", False)


def test_parser_marca_formato_invalido():
    assert interpretar_resposta("A categoria parece ser atraso.") == (None, True)


def test_parser_rejeita_categoria_desconhecida():
    assert interpretar_resposta('{"categoria":"cancelamento"}') == (None, True)

