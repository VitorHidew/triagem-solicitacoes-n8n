import json

from src.parser import interpretar_resposta
from src.provedor import gerar_simulado


def test_simulado_e_deterministico():
    prompt = "Responda somente com categoria"
    mensagem = "Cobraram duas vezes o pedido fictício"
    assert gerar_simulado(prompt, mensagem) == gerar_simulado(prompt, mensagem)
    assert interpretar_resposta(gerar_simulado(prompt, mensagem)) == ("cobrança", False)


def test_simulado_respeita_formato_json_do_prompt():
    resposta = gerar_simulado('Responda com JSON válido: {"categoria":"atraso"}', "Ainda não chegou")
    assert json.loads(resposta) == {"categoria": "atraso"}

