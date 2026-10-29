#!/usr/bin/env python3
"""Envia exemplos fictícios ao webhook ou simula o lote localmente."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARQUIVO_PADRAO = ROOT / "data" / "mensagens_exemplo.json"


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="URL do webhook; omitida com --simular")
    parser.add_argument("--inicio", type=int, default=0, help="Índice inicial (base zero)")
    parser.add_argument("--quantidade", type=int, default=10, help="Itens a processar")
    parser.add_argument("--pausa", type=float, default=1.0, help="Pausa entre itens em segundos")
    parser.add_argument("--arquivo", type=Path, default=ARQUIVO_PADRAO)
    parser.add_argument("--simular", action="store_true", help="Não usa rede; apenas imprime o lote")
    args = parser.parse_args()
    if args.inicio < 0 or args.quantidade < 1 or args.pausa < 0:
        parser.error("inicio >= 0, quantidade >= 1 e pausa >= 0")
    if not args.simular and not args.url:
        parser.error("informe --url ou use --simular")
    return args


def carregar(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, list):
        raise ValueError("o arquivo deve conter uma lista JSON")
    return dados


def enviar(url: str, payload: dict) -> tuple[int, str]:
    requisicao = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=30) as resposta:
            return resposta.status, resposta.read().decode("utf-8")
    except urllib.error.HTTPError as erro:
        return erro.code, erro.read().decode("utf-8")


def main() -> int:
    args = argumentos()
    exemplos = carregar(args.arquivo)
    lote = exemplos[args.inicio : args.inicio + args.quantidade]
    if not lote:
        print("Nenhum item no intervalo solicitado.", file=sys.stderr)
        return 2

    for posicao, exemplo in enumerate(lote, start=args.inicio):
        payload = {chave: exemplo[chave] for chave in ("nome", "canal", "mensagem")}
        if args.simular:
            print(json.dumps({"indice": posicao, "payload": payload}, ensure_ascii=False))
        else:
            status, corpo = enviar(args.url, payload)
            print(json.dumps({"indice": posicao, "http": status, "resposta": corpo}, ensure_ascii=False))
        if posicao != args.inicio + len(lote) - 1:
            time.sleep(args.pausa)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

