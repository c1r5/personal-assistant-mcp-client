import asyncio
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_mcp_adapters.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig
from mcp.shared.exceptions import McpError # Import the specific exception

from modules.services.mcp_server_service import MCPServerService

logger = __import__('logging').getLogger(__name__)

class MCPClient:
    def __init__(self, model: BaseChatModel, mcp_server_service: MCPServerService):
        self.client = MultiServerMCPClient(mcp_server_service.mcp_servers)
        self.model = model
        self.history = []
        self.tools: list[BaseTool] = []
        self.server_name_by_tool_name = {}
        self.resources_by_server = {}

    async def load_tools_and_resources(self):
        logger.info("Carregando ferramentas e recursos dos servidores MCP...")
        
        server_names = list(self.client.connections.keys())
        if not server_names:
            logger.warning("Nenhum servidor MCP conectado.")
            return
        
        tool_tasks = [self.client.get_tools(server_name=name) for name in server_names]
        resource_tasks = [self.client.get_resources(server_name=name) for name in server_names]

        all_results = await asyncio.gather(
            *tool_tasks,
            *resource_tasks,
            return_exceptions=True 
        )

        num_servers = len(server_names)
        tool_results = all_results[:num_servers]
        resource_results = all_results[num_servers:]

        for i, server_name in enumerate(server_names):
            tools = tool_results[i]
            if isinstance(tools, Exception):
                logger.error(f"Erro ao carregar ferramentas do servidor '{server_name}': {tools}")
            else:
                self.tools.extend(tools) # type: ignore
                for tool in tools: # type: ignore
                    self.server_name_by_tool_name[tool.name] = server_name
            
            resources = resource_results[i]
            if isinstance(resources, Exception):
                if isinstance(resources, McpError) and "Method not found" in str(resources):
                    logger.warning(f"Servidor '{server_name}' não suporta listagem de recursos (Method not found). Ignorando recursos para este servidor.")
                else:
                    logger.error(f"Erro ao carregar recursos do servidor '{server_name}': {resources}")
            elif resources:
                self.resources_by_server[server_name] = resources
                logger.info(f"{len(resources)} recursos carregados do servidor '{server_name}'.") # type: ignore

        if not self.tools:
            logger.error("Nenhuma ferramenta MCP foi carregada.")
        
        logger.info(f"Total de ferramentas carregadas: {len(self.tools)}")
        logger.info(f"Total de servidores com recursos: {len(self.resources_by_server)}")

    def _build_system_prompt(self) -> str:
        """Builds the system prompt including instructions and available resources."""
        
        resource_contexts = []
        for server_name, resources in self.resources_by_server.items():
            # Using .data as per the original user code's hint `r.data`
            resource_strings = "\n".join(f"- {res.data}" for res in resources)
            if resource_strings:
                resource_contexts.append(f"Recursos do servidor '{server_name}':\n{resource_strings}")

        resource_section = "\n\n".join(resource_contexts)
        if not resource_section:
            resource_section = "Nenhum recurso disponível."

        return f'''
You are a helpful assistant with access to tools. Your role is to decide the best tool to use based on the user's question.

Important guidelines:

1. **Always select the most appropriate tool** based on the user's intent.
2. **Use the provided resources** to fill in any missing arguments for the tools. The resources are listed below.
3. Do **not ask the user for missing arguments** if the information can be found in the loaded resources.
4. Only if a required parameter is missing after checking the resources, then you may ask the user for clarification.
5. After receiving the tool’s response, generate a friendly and concise reply summarizing the result.
6. Respond in the same language as the user's message.

Here are the resources available to you:
---
{resource_section}
---
'''.strip()

    async def generate_llm_response(self, message: str) -> str | None:
        if not self.tools:
            logger.error("Ferramentas não carregadas. Chame 'load_tools_and_resources' primeiro.")
            return "Erro: As ferramentas não foram carregadas corretamente."

        self.history.append({"role": "user", "content": message})
        self.history = self.history[-100:]
        
        messages = self.history.copy()
        messages.append({
            "role": "system",
            "content": self._build_system_prompt()
        })
        
        agent = create_react_agent(self.model, self.tools)
        
        try:
            # Run the agent once with all context provided upfront
            result = await agent.ainvoke({"messages": messages}, config=RunnableConfig(tags=["invoke"]))
            
            # The final answer is in the 'messages' list with role 'assistant'
            final_msg = result.get('messages', [])[-1].content

            if final_msg:
                self.history.append({"role": "assistant", "content": final_msg})
                return final_msg

            logger.warning("Nenhuma resposta final foi encontrada na saída do agente.")
            return "Não consegui gerar uma resposta adequada."

        except Exception as e:
            logger.exception(f"Erro ao invocar agente: {e}")
            return "Ocorreu um erro ao tentar gerar a resposta."
