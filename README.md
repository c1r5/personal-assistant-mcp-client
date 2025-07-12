# Personal Assistant Client integrated with [Chatbot Service](https://github.com/c1r5/chatbot-service)

## Funcionalidades

Este projeto implementa um cliente de assistente pessoal utilizando o protocolo Model Context Protocol (MCP) e integra-se a um serviço de chatbot com suporte a ferramentas externas. As principais funcionalidades são:

### 1. Integração com LLM e Chatbot
- Utiliza modelos de linguagem (LLM) para gerar respostas inteligentes.
- Conecta-se a um serviço de chatbot via WebSocket para comunicação em tempo real.
- Suporte a histórico de conversas e múltiplos ouvintes de mensagens.

### 2. Suporte a Ferramentas MCP
- Carrega e integra ferramentas MCP a partir de um arquivo de configuração (`.vscode/mcp.json`).
- Permite que o assistente utilize ferramentas externas para responder perguntas específicas.

### 3. Arquitetura Modular
- Código organizado em módulos para API, clientes, helpers e servidores de ferramentas.
- Fácil extensão para adicionar novas ferramentas MCP.

### 4. Testes
- Estrutura básica para testes automatizados dos módulos e ferramentas.

## Estrutura dos Principais Arquivos
- `main.py`: Inicialização do cliente, integração com LLM e ChatbotService.
- `modules/api/`: Modelos e serviço de chatbot (WebSocket).
- `modules/clients/`: Cliente do chatbot e integração com LLM e MCP.
- `modules/helpers/`: Utilitários para carregar ferramentas MCP.
- `servers/`: Implementações das ferramentas MCP (get_time, pastebin, weather).
- `tests/`: Testes automatizados.

## Como funciona
1. O usuário envia uma mensagem.
2. O assistente processa a mensagem, decide se precisa usar uma ferramenta MCP.
3. Se necessário, aciona a ferramenta e retorna a resposta formatada.
4. Toda a comunicação é feita de forma assíncrona e extensível.

## Requisitos
- Python 3.10+
- Dependências listadas em `pyproject.toml` e `uv.lock`

## Observações
- Para funcionamento das ferramentas, configure corretamente as variáveis de ambiente e o arquivo `.vscode/mcp.json`.
- Consulte o código de cada servidor em `servers/` para detalhes de uso e parâmetros.

## Utilização com Docker

Este projeto pode ser executado facilmente utilizando Docker. Siga os passos abaixo para buildar e rodar o ambiente:

### DEV

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build --watch
```

### PROD

```bash
docker compose -f docker-compose.yml --build
```
