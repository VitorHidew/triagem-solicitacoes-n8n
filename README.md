# Triagem automática de solicitações com n8n + Gemini

Projeto de portfólio que demonstra uma automação de triagem usando n8n self-hosted, Gemini e Telegram. Todos os exemplos deste repositório são fictícios.

## Problema

Ler, resumir e priorizar solicitações manualmente consome atenção e pode produzir classificações inconsistentes. Este fluxo recebe uma mensagem, pede uma classificação estruturada a uma LLM, valida a resposta, registra o resultado em CSV e avisa um canal apenas quando a prioridade é alta.

## Como funciona

1. Um Webhook recebe `nome`, `canal` e `mensagem`.
2. O fluxo espera antes da chamada ao modelo.
3. O nó **Google Gemini Chat Model** classifica a solicitação em `dúvida`, `reclamação`, `pedido`, `elogio` ou `outro`, cria um resumo de uma frase e define prioridade `alta`, `média` ou `baixa`.
4. Se a chamada retornar erro 429, o fluxo aguarda e faz uma nova tentativa espaçada.
5. Um nó Code valida o JSON e os valores permitidos. Saídas inválidas viram `status: revisar manualmente`, sem interromper o fluxo.
6. Cada solicitação é gravada em um CSV local com `data`, `categoria`, `prioridade`, `resumo` e `status` (além dos campos fictícios de origem).
7. Somente itens de prioridade alta geram aviso no Telegram.

O diagrama está em [docs/fluxo.md](docs/fluxo.md).

## Estrutura

```text
workflow/   fluxo n8n importável
prompts/    contrato de classificação e exemplos
data/       30 mensagens fictícias e rótulos esperados
scripts/    cliente de teste em lotes
docs/       diagrama e espaços para capturas
```

## Pré-requisitos

- Node.js e `npx`, ou Docker;
- uma instalação local do n8n;
- conta no Google AI Studio com acesso ao Gemini;
- bot e conversa de teste no Telegram;
- Python 3 para o script de exemplos.

Não coloque chaves no repositório. O arquivo `.env.example` contém somente placeholders; crie seu `.env` local, que está ignorado pelo Git. O fluxo espera que as credenciais sejam cadastradas pela interface do n8n.

## Rodar o n8n localmente

### Opção 1: npx

```bash
npx n8n
```

Defina `GEMINI_MODEL`, `TELEGRAM_CHAT_ID` e `N8N_CSV_DIR` no ambiente que inicia o n8n. Use em `GEMINI_MODEL` um modelo pequeno da linha Flash que esteja disponível na sua conta; o nome não fica fixo no fluxo porque a oferta muda.

### Opção 2: Docker

Exemplo conceitual — substitua apenas valores locais e nunca versione o `.env`:

```bash
docker run --rm -it \
  -p 5678:5678 \
  --env-file .env \
  -v n8n_data:/home/node/.n8n \
  -v "$(pwd)/data/saida:/files/data/saida" \
  docker.n8n.io/n8nio/n8n
```

No Docker, `N8N_CSV_DIR` deve apontar para `/files/data/saida`. O volume é necessário para que os CSVs sobrevivam fora do contêiner. Em Windows/PowerShell, adapte a sintaxe de caminho conforme o terminal.

## Importar e configurar o fluxo

1. Abra o n8n em `http://localhost:5678`.
2. Importe `workflow/triagem-solicitacoes-n8n-gemini.json`.
3. No Google AI Studio, acesse [aistudio.google.com](https://aistudio.google.com/), crie uma chave para seu ambiente de teste e confira os modelos e limites atualmente disponíveis.
4. No n8n, crie uma credencial Google Gemini com a chave e selecione-a nos dois nós **Google Gemini Chat Model**. O nome sugerido de placeholder é `GEMINI_AI_STUDIO_CREDENTIAL`.
5. Configure `GEMINI_MODEL` com um modelo pequeno da linha Flash disponível na sua conta.
6. Configure o Telegram conforme a próxima seção e selecione a credencial nos nós correspondentes.
7. Configure `N8N_CSV_DIR`, garanta permissão de escrita e ative o fluxo quando terminar os testes.

As versões e os campos dos nós do n8n mudam. Após importar, talvez seja necessário ajustar os nós Gemini, Wait, Convert to File, Read/Write Files from Disk, Telegram e Respond to Webhook para a versão instalada.

## Configurar o Telegram sem expor valores

1. No Telegram, abra a conversa oficial com `@BotFather` e confirme cuidadosamente o identificador da conta.
2. Use `/newbot`, escolha nome e usuário e copie o token somente para o gerenciador de credenciais do n8n.
3. Inicie uma conversa com o bot de teste e envie uma mensagem fictícia.
4. Obtenha o chat ID usando a API `getUpdates` localmente ou um nó Telegram de teste no n8n. Não cole o retorno em issues, commits, capturas ou logs compartilhados.
5. Guarde o identificador apenas na variável local `TELEGRAM_CHAT_ID` e selecione a credencial do bot no nó **Avisar no Telegram**.
6. Antes de capturar telas, oculte token, chat ID e qualquer outro identificador.

## Testar em lotes

Primeiro, valide o script sem rede:

```bash
python scripts/enviar_exemplos.py --simular --inicio 0 --quantidade 5 --pausa 0
```

Depois de colocar o Webhook em modo de teste ou ativar o fluxo:

```bash
python scripts/enviar_exemplos.py \
  --url http://localhost:5678/webhook/triagem-solicitacao \
  --inicio 0 \
  --quantidade 5 \
  --pausa 3
```

Os índices começam em zero. A pausa ajuda a controlar a cadência, mas não garante que o lote fique abaixo dos limites da sua conta.

## Checklist após importar

- [ ] Os dois nós Gemini reconhecem a credencial criada na interface.
- [ ] `GEMINI_MODEL` corresponde a um modelo Flash disponível na conta.
- [ ] O prompt chega ao modelo e a saída aparece no campo esperado pelo nó de validação.
- [ ] Os nós Wait usam unidades e durações aceitas pela versão instalada.
- [ ] Um erro 429 percorre a espera e uma única nova tentativa; outros erros viram revisão manual.
- [ ] O diretório configurado em `N8N_CSV_DIR` existe e aceita escrita.
- [ ] Cada CSV contém cabeçalho e os campos previstos.
- [ ] O bot consegue enviar para a conversa de teste sem revelar token ou chat ID.
- [ ] Apenas prioridade alta percorre o ramo Telegram.
- [ ] O Webhook responde uma vez com o resultado validado.
- [ ] As capturas usam somente exemplos fictícios e não mostram credenciais.

## Limitações conhecidas

- O fluxo **não foi executado no n8n** neste ambiente. A importação e a compatibilidade dos nós precisam ser verificadas localmente.
- Gemini e Telegram **não foram acessados**; credenciais, resposta real do modelo, 429 real e entrega de mensagens não foram verificados.
- Os limites gratuitos do Gemini variam por modelo e conta e podem ser baixos. Consulte o Google AI Studio no momento do teste; este projeto não assume números.
- Resultados de classificação variam conforme modelo, versão, prompt e conteúdo.
- O plano gratuito pode usar os dados enviados para melhorar produtos do provedor. Use somente dados fictícios e consulte os termos atuais antes de testar.
- A retentativa de 429 é limitada a uma tentativa adicional. Para produção, use backoff exponencial e fila.
- Um arquivo CSV é criado por solicitação para evitar disputa de escrita. Uma consolidação posterior pode ser adicionada se necessário.
- Os rótulos esperados são referências humanas fictícias, não resultados medidos.

## O que foi validado neste repositório

- Sintaxe do JSON do workflow e dos dados de exemplo.
- Quantidade e estrutura dos exemplos fictícios.
- Sintaxe do script Python e execução em modo `--simular`.
- Ausência de valores reais de credenciais nos arquivos versionados.

Não foram validados: importação/execução no n8n, chamadas ao Gemini, limites da conta, retentativa real de 429, escrita pelo n8n em cada sistema operacional e envio pelo Telegram.

## Resultados

Preencha somente depois de executar um protocolo de avaliação documentado.

| Indicador | Manual | Automático | Observações |
|---|---:|---:|---|
| Tempo por solicitação | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| Acertos de categoria | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| Acertos de prioridade | [PREENCHER] | [PREENCHER] | [PREENCHER] |

## Segurança e privacidade

Este repositório contém somente pessoas, mensagens e cenários fictícios. Não use dados pessoais, corporativos ou confidenciais. Credenciais pertencem exclusivamente ao armazenamento local/gerenciador de credenciais do n8n.

