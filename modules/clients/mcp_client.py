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
        self.tools: list[BaseTool] = await self.client.get_tools()
        if not self.tools:
            logger.error("Nenhuma ferramenta MCP foi carregada com sucesso.")
        logger.info(f"Total de ferramentas carregadas: {len(self.tools)}")
        
    async def generate_llm_response(self, message: str) -> str | None:
        self.history.append({"role": "user", "content": message})
        self.history = self.history[-100:]
        
        messages = self.history.copy()
        
        agent = create_react_agent(self.model, self.tools, prompt="""
                You are a helpful assistant with access to various tools. 
                Choose the appropriate tool based on the user's question. 
                If no tool is needed, reply directly.
                Reply requirements:
                1. Reply according to user prompt language

                After receiving a tool's response:
                1. Transform the raw data into a natural, conversational response
                2. Keep responses concise but informative
                3. Focus on the most relevant information
                4. Use appropriate context from the user's question
                5. Avoid simply repeating the raw data
        """.strip())
        
        try:
            # Executa e intercepta eventos
            steps = []
            async for event in agent.astream_events({"messages": messages}, config=RunnableConfig(tags=["intercept"])):
                steps.append(event)
            
            tool_used = None
            for s in steps:
                logger.info(f"STEP: {s}")
            #     if s.get("event") == "on_tool_start":
            #         tool_used = s["name"]  
            #         break

            # if tool_used:
            #     namespace = tool_used.split(".")[0]
            #     logger.info(f"Ferramenta escolhida pertence ao servidor: {namespace}")

            #     resources = await self.client.get_resources(namespace)
            #     logger.info(f"Resources: {resources}")
                # matching = [r for r in resources if r.uri.startswith(f"{namespace}://")]
                # loaded_resources = {
                #     r.uri: await self.client.load_resource(r.uri)
                #     for r in matching
                # }

                # logger.info(f"Recursos carregados: {loaded_resources}")

            chunks = [s["data"] for s in steps if s.get("event") == "on_chat_model_stream"]
            if not chunks or chunks == []:
                logger.warning("Nenhuma mensagem final encontrada.")
                return "Não consegui processar sua solicitação."

            final_msg = str()
            
            for chunk in chunks:
                if "chunk" in chunk:
                    final_msg += chunk['chunk'].content
                
            
            if not final_msg == "":
                self.history.append({"role": "assistant", "content": final_msg})
                return final_msg

            return "Erro ao processar resposta"
        
        except Exception as e:
            logger.exception(f"Erro ao invocar agente: {e}")
            return "Ocorreu um erro ao tentar gerar a resposta."