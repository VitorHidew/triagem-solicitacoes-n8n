# Avaliador de prompts

Ferramenta em Python para comparar versões de prompts de classificação contra um conjunto rotulado. O cenário é inteiramente fictício: mensagens de suporte de um aplicativo de delivery, classificadas em `atraso`, `cobrança`, `item_faltando`, `elogio` ou `outro`.

## Problema

Alterar um prompt sem avaliação sistemática torna difícil saber se a nova versão melhorou, piorou ou apenas mudou os tipos de erro. Este projeto executa o mesmo conjunto de casos contra uma ou mais versões, valida o formato da resposta, calcula métricas e salva relatórios reproduzíveis.

## SDK do Gemini

O projeto usa o SDK oficial atual **Google Gen AI SDK for Python**, pacote `google-genai`, importado com `from google import genai`. A [documentação oficial de bibliotecas do Gemini](https://ai.google.dev/gemini-api/docs/libraries) recomenda esse pacote e classifica `google-generativeai` como legado e sem manutenção ativa.

O nome do modelo não é fixado. Defina `GEMINI_MODEL` com um modelo pequeno da linha Flash que esteja disponível na sua conta no momento da execução.

## Estrutura

```text
prompts/        v1 simples, v2 com exemplos e v3 com JSON e critérios
data/           30 casos fictícios rotulados em JSON Lines
src/            CLI, provedor, parser, cache, métricas e relatórios
tests/          testes automatizados
results/        destino reservado para relatórios de API real
cache/          respostas e resultados simulados locais (ignorado)
```

Uma rodada completa com três prompts e 30 casos pode fazer no máximo 90 chamadas novas. O cache reduz esse total em reexecuções.

## Instalação

```bash
python -m venv .venv
```

Ative o ambiente virtual conforme seu sistema e instale:

```bash
python -m pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha somente no ambiente local:

```dotenv
GEMINI_API_KEY=SEU_VALOR_LOCAL
GEMINI_MODEL=MODELO_FLASH_DISPONIVEL_NA_SUA_CONTA
```

O `.env`, o cache e os relatórios gerados são ignorados pelo Git. Nunca publique esses valores.

## Obter acesso gratuito ao Gemini

1. Acesse [aistudio.google.com](https://aistudio.google.com/).
2. Consulte os termos, os modelos disponíveis e os limites da sua própria conta.
3. Crie a chave no ambiente local e guarde-a apenas no `.env`.
4. Escolha um modelo pequeno da linha Flash disponível e coloque seu nome em `GEMINI_MODEL`.

Os limites gratuitos variam por modelo e conta e podem ser baixos. Este projeto não presume valores de cota.

## Executar em modo simulado

O modo simulado não usa rede, chave ou Gemini. Ele existe para testar o pipeline de forma determinística:

```bash
python -m src.avaliar \
  --prompt prompts/v1.md \
  --casos data/casos.jsonl \
  --pausa 0 \
  --limite-diario 15 \
  --simulado
```

Resultados simulados são gravados por padrão em `cache/resultados-simulados/`, ficam ignorados e **não representam desempenho do modelo**.

## Executar com a API em partes

O exemplo conservador solicitado processa até 15 novas chamadas na execução:

```bash
python -m src.avaliar \
  --prompt prompts/v1.md \
  --casos data/casos.jsonl \
  --pausa 6 \
  --limite-diario 15
```

Execute novamente quando sua cota permitir. A chave do cache é o hash de modelo + conteúdo do prompt + mensagem; itens já concluídos são reutilizados sem nova chamada. O limite diário informado é local à execução e deve ser ajustado por você conforme a cota atual mostrada pelo provedor.

Para comparar as três versões em sequência:

```bash
python -m src.avaliar \
  --prompt prompts/v1.md \
  --prompt prompts/v2.md \
  --prompt prompts/v3.md \
  --casos data/casos.jsonl \
  --pausa 6 \
  --limite-diario 15
```

Se ocorrer 429, a ferramenta faz novas tentativas com espera crescente. Se o erro persistir, encerra com mensagem clara; cada resposta concluída já estará salva no cache para retomada posterior.

## Métricas e relatórios

Para cada prompt, a ferramenta salva:

- acurácia geral e por categoria;
- matriz de confusão;
- erros com mensagem, rótulo esperado e saída obtida;
- quantidade de casos concluídos e respostas recuperadas do cache;
- CSV detalhado e resumo Markdown.

Uma saída fora das categorias ou do JSON esperado é contabilizada como `erro_formato` e não interrompe a rodada.

## Adicionar prompts e casos

Adicione uma versão como arquivo Markdown em `prompts/` e passe seu caminho em outro `--prompt`. Cada linha de `data/casos.jsonl` deve ter:

```json
{"id":31,"mensagem":"Mensagem inteiramente fictícia.","rotulo":"outro"}
```

Rótulos aceitos: `atraso`, `cobrança`, `item_faltando`, `elogio` e `outro`.

## Testes

```bash
pytest
```

Validações executadas neste ambiente:

- `pytest`: 9 testes aprovados;
- importação do pacote `google-genai` versão 2.34.0;
- rodada simulada dos três prompts com os 30 casos;
- nova execução simulada de v1 reutilizando o cache, sem chamadas novas.

Essas validações testam o pipeline local e não medem desempenho do Gemini.

Não foram verificadas chamadas reais ao Gemini, validade de chave, disponibilidade de modelo, cotas da conta nem comportamento real de 429.

## Comparação de versões

Preencha somente após executar com a API real e revisar os relatórios. Números do simulador não devem entrar nesta tabela.

| Versão | Casos concluídos | Acurácia geral | Erros de formato | Observações |
|---|---:|---:|---:|---|
| v1 | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| v2 | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| v3 | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |

## Limitações e privacidade

- O conjunto tem somente 30 casos fictícios e não representa toda a variedade de linguagem possível.
- Resultados variam por modelo, versão, parâmetros e momento da execução.
- O plano gratuito pode usar dados enviados para melhorar produtos do provedor. Por isso, use somente dados fictícios e confira os termos atuais antes de executar.
- O modo simulado valida o software, não a qualidade de uma LLM.
- O cache deve ser invalidado naturalmente ao trocar modelo, prompt ou mensagem; outras alterações de configuração podem exigir limpeza manual.

