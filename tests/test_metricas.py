from src.metricas import calcular
from src.modelos import Resultado


def test_metricas_contabilizam_acertos_e_formato():
    resultados = [
        Resultado(1, "a", "atraso", "atraso", False, False),
        Resultado(2, "b", "cobrança", "outro", False, False),
        Resultado(3, "c", "elogio", None, True, True),
    ]
    metricas = calcular(resultados)
    assert metricas["total"] == 3
    assert metricas["acertos"] == 1
    assert metricas["erros_formato"] == 1
    assert metricas["matriz"]["elogio"]["erro_formato"] == 1
    assert metricas["cache_hits"] == 1

