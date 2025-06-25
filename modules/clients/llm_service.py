from mcp import ClientSession, stdio_client
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_mcp_adapters.tools import load_mcp_tools, BaseTool
from langgraph.prebuilt import create_react_agent

from mcp.client.sse import sse_client

from modules.helpers.mcp_tools import load_mcp_tool_from_file
from modules.models import SSEServerParameters


logger = __import__('logging').getLogger(__name__)

class LLMService:
    def __init__(self, model: BaseChatModel):
        self.model = model
        self.history = []
    
    async def generate_llm_response(self, message: str) -> str | None:
        try:
            self.tools = load_mcp_tool_from_file()
        except Exception as e:
            logger.error(f"Error loading MCP tools: {e}")
            self.tools = []
        
        tools: list[BaseTool] = []
        
        for tool in self.tools:
            async with (
                sse_client(tool.url, headers=tool.headers) 
                if isinstance(tool, SSEServerParameters) 
                else stdio_client(tool)
            ) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await load_mcp_tools(session)

        if len(tools) != 0:
            logger.info(f"Loaded {len(tools)} tools from MCP.")
        
        # Adiciona a mensagem do usuário ao histórico
        self.history.append({"role": "user", "content": message})
        # Limita o histórico para as 100 últimas mensagens
        self.history = self.history[-100:]
        
        # Prepara o histórico para o modelo
        messages = self.history.copy()
        
        agent = create_react_agent(self.model, tools, prompt="""
                You are a helpful assistant with access to various tools. 
                Choose the appropriate tool based on the user's question. If no tool is needed, reply directly.
                After receiving a tool's response:
                1. Transform the raw data into a natural, conversational response
                2. Keep responses concise but informative
                3. Focus on the most relevant information
                4. Use appropriate context from the user's question
                5. Avoid simply repeating the raw data
        """.strip())
        
        agent_response = await agent.ainvoke({"messages": messages})
        
        # Adiciona a resposta do agente ao histórico
        if agent_response and "messages" in agent_response and agent_response["messages"]:
            self.history.append({"role": "assistant", "content": agent_response["messages"][-1].content})
            logger.info(f"Agent response: {agent_response}")
            return agent_response["messages"][-1].content
        else:
            logger.info(f"Agent response: {agent_response}")
            return None