from __future__ import annotations

import csv
from pathlib import Path

from .modelos import CATEGORIAS, Resultado


def salvar_relatorios(
    saida: Path,
    nome_prompt: str,
    resultados: list[Resultado],
    metricas: dict,
    simulado: bool,
) -> tuple[Path, Path]:
    saida.mkdir(parents=True, exist_ok=True)
    csv_path = saida / f"{nome_prompt}.csv"
    md_path = saida / f"{nome_prompt}.md"

    with csv_path.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=("caso_id", "mensagem", "esperado", "obtido", "erro_formato", "cache"),
        )
        escritor.writeheader()
        for item in resultados:
            escritor.writerow(item.__dict__)

    aviso = "**EXECUÇÃO SIMULADA — não representa desempenho do Gemini.**" if simulado else "Execução com API Gemini."
    linhas = [
        f"# Resultado: {nome_prompt}",
        "",
        aviso,
        "",
        f"Casos concluídos: {metricas['total']}",
        f"Acurácia: {metricas['acuracia']:.4f}",
        f"Erros de formato: {metricas['erros_formato']}",
        f"Respostas reutilizadas do cache: {metricas['cache_hits']}",
        "",
        "## Acurácia por categoria",
        "",
        "| Categoria | Concluídos | Acertos | Acurácia |",
        "|---|---:|---:|---:|",
    ]
    for categoria in CATEGORIAS:
        valor = metricas["por_categoria"][categoria]
        linhas.append(f"| {categoria} | {valor['total']} | {valor['acertos']} | {valor['acuracia']:.4f} |")

    colunas = [*CATEGORIAS, "erro_formato"]
    linhas.extend(["", "## Matriz de confusão", "", "| Esperado \\ Obtido | " + " | ".join(colunas) + " |", "|---|" + "---:|" * len(colunas)])
    for esperado in CATEGORIAS:
        linhas.append("| " + esperado + " | " + " | ".join(str(metricas["matriz"][esperado][c]) for c in colunas) + " |")

    linhas.extend(["", "## Erros", "", "| Caso | Mensagem | Esperado | Obtido |", "|---:|---|---|---|"])
    for erro in metricas["erros"]:
        mensagem = erro.mensagem.replace("|", "\\|")
        linhas.append(f"| {erro.caso_id} | {mensagem} | {erro.esperado} | {erro.obtido or 'erro_formato'} |")
    md_path.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return csv_path, md_path


def salvar_comparacao(saida: Path, resumos: list[dict], simulado: bool) -> Path:
    caminho = saida / "comparacao.csv"
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=("prompt", "casos_concluidos", "acertos", "acuracia", "erros_formato", "simulado")
        )
        escritor.writeheader()
        for resumo in resumos:
            escritor.writerow({**resumo, "simulado": simulado})
    return caminho

