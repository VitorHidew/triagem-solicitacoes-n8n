from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from .cache import CacheDisco, chave_cache
from .metricas import calcular
from .modelos import CATEGORIAS, Caso, Resultado
from .parser import interpretar_resposta
from .provedor import LimitePersistenteError, ProvedorGemini, gerar_simulado
from .relatorio import salvar_comparacao, salvar_relatorios


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Avalia versões de prompt em casos rotulados.")
    parser.add_argument("--prompt", action="append", required=True, type=Path, help="Pode ser repetido para comparar versões")
    parser.add_argument("--casos", type=Path, default=Path("data/casos.jsonl"))
    parser.add_argument("--pausa", type=float, default=6.0)
    parser.add_argument("--limite-diario", type=int, default=15)
    parser.add_argument("--simulado", action="store_true")
    parser.add_argument("--cache", type=Path, default=Path("cache/respostas"))
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    if args.pausa < 0 or args.limite_diario < 1:
        parser.error("--pausa deve ser >= 0 e --limite-diario deve ser >= 1")
    return args


def carregar_casos(caminho: Path) -> list[Caso]:
    casos: list[Caso] = []
    for numero, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), start=1):
        if not linha.strip():
            continue
        dados = json.loads(linha)
        if dados.get("rotulo") not in CATEGORIAS:
            raise ValueError(f"Rótulo inválido na linha {numero}: {dados.get('rotulo')}")
        casos.append(Caso(id=int(dados["id"]), mensagem=str(dados["mensagem"]), rotulo=dados["rotulo"]))
    return casos


def avaliar_prompt(
    prompt_path: Path,
    casos: list[Caso],
    modelo: str,
    cache: CacheDisco,
    limite: int,
    pausa: float,
    simulado: bool,
    provedor: ProvedorGemini | None,
) -> tuple[list[Resultado], int]:
    prompt = prompt_path.read_text(encoding="utf-8")
    resultados: list[Resultado] = []
    chamadas = 0
    for caso in casos:
        chave = chave_cache(modelo, prompt, caso.mensagem)
        resposta = cache.obter(chave)
        veio_cache = resposta is not None
        if resposta is None:
            if chamadas >= limite:
                break
            if simulado:
                resposta = gerar_simulado(prompt, caso.mensagem)
            else:
                assert provedor is not None
                resposta = provedor.gerar(prompt, caso.mensagem)
            cache.salvar(chave, resposta)
            chamadas += 1
            if pausa and chamadas < limite:
                time.sleep(pausa)
        obtido, erro_formato = interpretar_resposta(resposta)
        resultados.append(
            Resultado(caso.id, caso.mensagem, caso.rotulo, obtido, erro_formato, veio_cache)
        )
    return resultados, chamadas


def main() -> int:
    args = argumentos()
    load_dotenv()
    modelo = os.getenv("GEMINI_MODEL", "SIMULADOR_LOCAL" if args.simulado else "")
    chave = os.getenv("GEMINI_API_KEY", "")
    if not args.simulado and (not chave or not modelo):
        print("Defina GEMINI_API_KEY e GEMINI_MODEL no .env local.", file=sys.stderr)
        return 2

    saida = args.saida or (Path("cache/resultados-simulados") if args.simulado else Path("results"))
    cache = CacheDisco(args.cache / ("simulado" if args.simulado else "gemini"))
    casos = carregar_casos(args.casos)
    provedor = None if args.simulado else ProvedorGemini(chave, modelo, espera_inicial=max(args.pausa, 1.0))
    restantes = args.limite_diario
    resumos: list[dict] = []

    try:
        for prompt_path in args.prompt:
            resultados, chamadas = avaliar_prompt(
                prompt_path, casos, modelo, cache, restantes, args.pausa, args.simulado, provedor
            )
            restantes -= chamadas
            metricas = calcular(resultados)
            salvar_relatorios(saida, prompt_path.stem, resultados, metricas, args.simulado)
            resumos.append(
                {
                    "prompt": prompt_path.stem,
                    "casos_concluidos": metricas["total"],
                    "acertos": metricas["acertos"],
                    "acuracia": f"{metricas['acuracia']:.4f}",
                    "erros_formato": metricas["erros_formato"],
                }
            )
            print(f"{prompt_path.name}: {metricas['total']} casos concluídos ({chamadas} chamadas novas).")
            if restantes <= 0:
                print("Limite diário configurado atingido. Execute novamente para retomar pelo cache.")
                break
    except LimitePersistenteError as erro:
        print(str(erro), file=sys.stderr)
        return 3

    salvar_comparacao(saida, resumos, args.simulado)
    if args.simulado:
        print("Execução simulada: estes números não medem desempenho do Gemini.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

