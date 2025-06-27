from langchain_core.language_models.chat_models import BaseChatModel
from langchain_mcp_adapters.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from modules.services.mcp_server_service import MCPServerService

logger = __import__('logging').getLogger(__name__)

class MCPClient:
    def __init__(self, model: BaseChatModel, mcp_server_service: MCPServerService):
        self.client = MultiServerMCPClient(mcp_server_service.mcp_servers)
        self.model = model
        self.history = []
    
    async def load_tools(self):
        logger.info("Carregando ferramentas...")
        self.tools: list[BaseTool] = []
        self.server_name_by_tool_name = {}
        
        for server_name in self.client.connections.keys():
            tools = await self.client.get_tools(server_name=server_name)
            self.tools.extend(tools)
            
            for tool in tools:
                self.server_name_by_tool_name[tool.name] = server_name
                
        if not self.tools:
            logger.error("Nenhuma ferramenta MCP foi carregada.")
        logger.info(f"Total de ferramentas carregadas: {len(self.tools)}")

    async def generate_llm_response(self, message: str) -> str | None:
        self.history.append({"role": "user", "content": message})
        self.history = self.history[-100:]
        
        messages = self.history.copy()

        messages.append({
            "role": "system",
            "content": """
                You are a helpful assistant with access to tools.

                Your role is to decide the best tool to use based on the user's question, even if the user doesn't provide all the necessary arguments directly.

                Important guidelines:

                1. **Always select the most appropriate tool** based on the user's intent, even if not all parameters are available yet.
                2. Do **not ask the user for missing arguments immediately** — first attempt to call the tool.
                3. Parameters may be inferred from:
                - Previously known context
                - System messages
                - Loaded resources
                4. Only if a required parameter is missing after trying to call the tool, then you may ask the user.
                5. After receiving the tool’s response, generate a friendly and concise reply summarizing the result.
                6. Respond in the same language as the user's message.

                Let the tool execution determine if arguments are missing — do not block tool calls preemptively.
            """.strip()
        })
        
        agent = create_react_agent(self.model, self.tools)
        
        try:
            steps = []
            tool_used = None

            # Etapa 2 — Rodar o agente até a escolha da ferramenta
            async for event in agent.astream_events({"messages": messages}, config=RunnableConfig(tags=["intercept"])):
                steps.append(event)
                if event.get("event") == "on_tool_start":
                    tool_used = event["name"]
                    break 

            if tool_used:
                # Etapa 3 — Carregar os recursos do servidor MCP correspondente
                namespace = self.server_name_by_tool_name[tool_used]
                logger.info(f"Ferramenta escolhida: {tool_used} (servidor: {namespace})")

                resources = await self.client.get_resources(namespace)
                logger.info(f"Recursos carregados do servidor '{namespace}': {resources}")

                resource_context = "\n".join(
                    f"resource: {r.data}" for r in resources
                )

                # Etapa 4 — Injetar os recursos no histórico como system message
                messages.append({
                    "role": "system",
                    "content": f"Use these resources when calling the tool '{tool_used}':\n{resource_context}"
                })

            agent = create_react_agent(self.model, self.tools)
            steps_final = []

            async for event in agent.astream_events({"messages": messages}, config=RunnableConfig(tags=["intercept"])):
                steps_final.append(event)

            # Etapa 6 — Extrair a resposta final do modelo
            chunks = [s["data"] for s in steps_final if s.get("event") == "on_chat_model_stream"]

            final_msg = "".join(chunk["chunk"].content for chunk in chunks if "chunk" in chunk)

            if final_msg:
                self.history.append({"role": "assistant", "content": final_msg})
                return final_msg

            logger.warning("Nenhuma resposta final encontrada.")
            return "Não consegui gerar uma resposta adequada."

        except Exception as e:
            logger.exception(f"Erro ao invocar agente: {e}")
            return "Ocorreu um erro ao tentar gerar a resposta."
