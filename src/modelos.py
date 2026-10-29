from __future__ import annotations

from dataclasses import dataclass


CATEGORIAS = ("atraso", "cobrança", "item_faltando", "elogio", "outro")


@dataclass(frozen=True)
class Caso:
    id: int
    mensagem: str
    rotulo: str


@dataclass(frozen=True)
class Resultado:
    caso_id: int
    mensagem: str
    esperado: str
    obtido: str | None
    erro_formato: bool
    cache: bool

