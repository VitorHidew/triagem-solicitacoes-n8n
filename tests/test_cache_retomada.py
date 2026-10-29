from pathlib import Path

from src.avaliar import avaliar_prompt
from src.cache import CacheDisco, chave_cache
from src.modelos import Caso


def test_cache_usa_hash_de_modelo_prompt_e_mensagem():
    base = chave_cache("modelo-a", "prompt", "mensagem")
    assert base != chave_cache("modelo-b", "prompt", "mensagem")
    assert base != chave_cache("modelo-a", "outro", "mensagem")
    assert base != chave_cache("modelo-a", "prompt", "outra")


def test_retomada_pula_respostas_em_cache(tmp_path: Path):
    prompt_path = tmp_path / "v1.md"
    prompt_path.write_text("Responda somente com a categoria.", encoding="utf-8")
    casos = [Caso(1, "Meu pedido não chegou", "atraso")]
    cache = CacheDisco(tmp_path / "cache")

    primeira, chamadas_primeira = avaliar_prompt(
        prompt_path, casos, "SIMULADOR_LOCAL", cache, 10, 0, True, None
    )
    segunda, chamadas_segunda = avaliar_prompt(
        prompt_path, casos, "SIMULADOR_LOCAL", cache, 10, 0, True, None
    )

    assert chamadas_primeira == 1
    assert chamadas_segunda == 0
    assert primeira[0].cache is False
    assert segunda[0].cache is True

