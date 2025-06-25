from langchain_core.language_models.chat_models import BaseChatModel
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from modules.helpers.mcp_tools import load_mcp_tool_from_file

logger = __import__('logging').getLogger(__name__)

class LLMService:
    def __init__(self, model: BaseChatModel):
        tools = load_mcp_tool_from_file()
        
        self.model = model
        self.client = MultiServerMCPClient(tools)
        self.history = []
    
    async def generate_llm_response(self, message: str) -> str | None:
        
        tools = await self.client.get_tools()
        
        self.history.append({"role": "user", "content": message})
        self.history = self.history[-100:]
        
        messages = self.history.copy()
        
        agent = create_react_agent(self.model, tools, prompt="""
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
        
        agent_response = await agent.ainvoke({"messages": messages})
        
        # # Adiciona a resposta do agente ao histórico
        if agent_response and "messages" in agent_response and agent_response["messages"]:
            self.history.append({"role": "assistant", "content": agent_response["messages"][-1].content})
            logger.info(f"Agent response: {agent_response}")
            return agent_response["messages"][-1].content

        logger.info(f"Agent response: {agent_response}")
        return None