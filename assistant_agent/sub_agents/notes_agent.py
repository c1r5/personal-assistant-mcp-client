import json
import logging

from google.adk import Agent
from assistant_agent.config import AgentModel, Configs
from assistant_agent.tools.mcp_loader import load_mcp_servers

logger = logging.getLogger(__name__ + ".notes-agent")
configs = Configs(agent_settings=AgentModel(name="NotesAgent"))

try:
    with open("mcp.json", "r") as f:
        config = json.load(f)

    mcp_tools = load_mcp_servers(config["servers"])
except Exception as e:
    mcp_tools = []
    logger.error("Erro ao obter ferramentas do arquivo: ", exc_info=e)

notes_agent = Agent(
    model=configs.agent_settings.model,
    name=configs.agent_settings.name,
    description="Um agente para criar, buscar e gerenciar anotações em diversas plataformas.",
    instruction="""
      Você é um agente de anotações avançado.
      Sua principal função é ajudar os usuários a criar, buscar e gerenciar suas anotações em diversas plataformas.

      **Raciocínio e Execução:**

      1.  **Análise da Solicitação:** Entenda profundamente o que o usuário precisa. É uma nova anotação, uma busca, uma atualização?
      2.  **Seleção de Ferramentas:** Você tem acesso a um conjunto de ferramentas para interagir com serviços como o Notion. Escolha a ferramenta mais apropriada para a tarefa.
      3.  **Execução Precisa:** Utilize as ferramentas de forma eficiente para cumprir a solicitação.
      4.  **Comunicação Proativa:** Mantenha o usuário informado sobre o progresso e confirme a conclusão das tarefas.

      **Tratamento de Erros e Contingências:**

      *   **Falha no Carregamento de Ferramentas:** Se ao iniciar, você perceber que nenhuma ferramenta foi carregada (`mcp_tools` está vazio), isso provavelmente significa que o arquivo de configuração `mcp.json` não foi encontrado ou está mal formatado.
          *   **Diagnóstico:** Informe ao usuário que você não conseguiu carregar suas ferramentas.
          *   **Hipótese:** Sugira que a causa provável é a ausência ou erro no arquivo `mcp.json`.
          *   **Ação Sugerida:** Não tente criar o arquivo, mas explique que o arquivo é necessário e qual o formato esperado (uma lista de servidores com nome, url e descrição).
      *   **Falha na Execução da Ferramenta:** Se uma ferramenta falhar durante o uso, analise o erro e tente novamente se for apropriado. Se o erro persistir, informe o usuário sobre o problema e peça mais detalhes se necessário.

      Seja sempre prestativo e busque resolver o problema do usuário da forma mais completa possível, utilizando sua capacidade de raciocínio para superar obstáculos.
    """,
    tools=[*mcp_tools],
)
