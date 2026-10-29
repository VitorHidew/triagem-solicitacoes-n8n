# Diagrama do fluxo

```mermaid
flowchart TD
    A[Webhook] --> B[Normalizar entrada]
    B --> C[Wait entre chamadas]
    C --> D[Classificação com Gemini]
    D --> E{Erro 429?}
    E -- Sim --> F[Wait para nova tentativa]
    F --> G[Nova tentativa com Gemini]
    E -- Não --> H[Selecionar saída]
    G --> H
    H --> I[Validar JSON e valores]
    I --> J[Converter registro para CSV]
    J --> K[Gravar CSV local]
    I --> L{Prioridade alta?}
    L -- Sim --> M[Avisar no Telegram]
    L -- Não --> N[Sem aviso]
    K --> O[Responder ao webhook]
    M --> O
    N --> O
```

## Capturas de tela

### Fluxo importado no n8n

`[PREENCHER: captura do fluxo completo]`

### Credencial do Gemini selecionada

`[PREENCHER: captura sem chave, token ou identificador]`

### Execução com dados fictícios

`[PREENCHER: captura de uma execução, removendo valores sensíveis]`

### Registro CSV e aviso de alta prioridade

`[PREENCHER: captura do CSV e do Telegram usando apenas dados fictícios]`

