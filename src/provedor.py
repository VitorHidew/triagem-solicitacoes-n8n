from __future__ import annotations

import json
import time
from dataclasses import dataclass


class LimitePersistenteError(RuntimeError):
    pass


@dataclass
class ProvedorGemini:
    api_key: str
    modelo: str
    tentativas_429: int = 3
    espera_inicial: float = 6.0

    def gerar(self, prompt: str, mensagem: str) -> str:
        try:
            from google import genai
        except ImportError as erro:
            raise RuntimeError("Instale as dependências de requirements.txt para usar a API.") from erro

        cliente = genai.Client(api_key=self.api_key)
        entrada = f"{prompt.rstrip()}\n\nMensagem:\n{mensagem}"
        try:
            for tentativa in range(self.tentativas_429):
                try:
                    resposta = cliente.models.generate_content(model=self.modelo, contents=entrada)
                    return resposta.text or ""
                except Exception as erro:  # o SDK expõe tipos distintos conforme transporte
                    if "429" not in str(erro):
                        raise
                    if tentativa == self.tentativas_429 - 1:
                        raise LimitePersistenteError(
                            "Limite 429 persistiu. Progresso salvo no cache; retome mais tarde."
                        ) from erro
                    time.sleep(self.espera_inicial * (2**tentativa))
        finally:
            cliente.close()
        raise RuntimeError("Falha inesperada ao obter resposta do Gemini.")


def gerar_simulado(prompt: str, mensagem: str) -> str:
    """Classificador determinístico para exercitar o pipeline, não o modelo."""
    texto = mensagem.lower()
    regras = (
        ("item_faltando", ("faltou", "faltando", "não veio", "sem a ", "sem o ", "metade")),
        ("cobrança", ("cobr", "valor", "estorno", "taxa", "cupom", "recibo")),
        ("atraso", ("atras", "não chegou", "nada ate", "esperando", "parado no mapa", "previsão mudou")),
        ("elogio", ("adorei", "excelente", "parabéns", "parabens", "muito bom", "ótimo", "gostei")),
    )
    categoria = next((rotulo for rotulo, termos in regras if any(termo in texto for termo in termos)), "outro")
    if "{\"categoria\"" in prompt or "JSON válido" in prompt:
        return json.dumps({"categoria": categoria}, ensure_ascii=False)
    return categoria

