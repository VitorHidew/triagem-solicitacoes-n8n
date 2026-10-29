from __future__ import annotations

import json
import re

from .modelos import CATEGORIAS


def interpretar_resposta(texto: str) -> tuple[str | None, bool]:
    """Retorna (categoria, erro_formato), sem lançar erro para saída inválida."""
    limpo = texto.strip()
    if not limpo:
        return None, True

    try:
        objeto = json.loads(limpo)
    except json.JSONDecodeError:
        objeto = None

    if isinstance(objeto, dict):
        categoria = objeto.get("categoria")
        if isinstance(categoria, str) and categoria in CATEGORIAS:
            return categoria, False
        return None, True

    normalizado = re.sub(r"[.`'\"\s]", "", limpo.lower())
    if normalizado in CATEGORIAS:
        return normalizado, False
    return None, True

