from __future__ import annotations

import hashlib
import json
from pathlib import Path


def chave_cache(modelo: str, prompt: str, mensagem: str) -> str:
    conteudo = json.dumps([modelo, prompt, mensagem], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()


class CacheDisco:
    def __init__(self, diretorio: Path) -> None:
        self.diretorio = diretorio

    def obter(self, chave: str) -> str | None:
        caminho = self.diretorio / f"{chave}.json"
        if not caminho.exists():
            return None
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        return dados.get("resposta") if isinstance(dados, dict) else None

    def salvar(self, chave: str, resposta: str) -> None:
        self.diretorio.mkdir(parents=True, exist_ok=True)
        caminho = self.diretorio / f"{chave}.json"
        temporario = caminho.with_suffix(".tmp")
        temporario.write_text(json.dumps({"resposta": resposta}, ensure_ascii=False), encoding="utf-8")
        temporario.replace(caminho)

