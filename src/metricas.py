from __future__ import annotations

from collections import Counter

from .modelos import CATEGORIAS, Resultado


def calcular(resultados: list[Resultado]) -> dict:
    total = len(resultados)
    acertos = sum(r.obtido == r.esperado for r in resultados)
    por_categoria: dict[str, dict[str, int | float]] = {}
    for categoria in CATEGORIAS:
        itens = [r for r in resultados if r.esperado == categoria]
        corretos = sum(r.obtido == categoria for r in itens)
        por_categoria[categoria] = {
            "total": len(itens),
            "acertos": corretos,
            "acuracia": corretos / len(itens) if itens else 0.0,
        }

    matriz = {
        esperado: {obtido: 0 for obtido in (*CATEGORIAS, "erro_formato")}
        for esperado in CATEGORIAS
    }
    for resultado in resultados:
        coluna = resultado.obtido if resultado.obtido in CATEGORIAS else "erro_formato"
        matriz[resultado.esperado][coluna] += 1

    return {
        "total": total,
        "acertos": acertos,
        "acuracia": acertos / total if total else 0.0,
        "erros_formato": sum(r.erro_formato for r in resultados),
        "por_categoria": por_categoria,
        "matriz": matriz,
        "erros": [r for r in resultados if r.obtido != r.esperado],
        "cache_hits": Counter(r.cache for r in resultados)[True],
    }

