import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from modules.clients.mcp_client import MCPClient
from modules.services.mcp_server_service import MCPServerService
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_mcp_adapters.resources import load_mcp_resources

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-002",
    temperature=0.75
)

        
mcp_server_service = MCPServerService()
mcp_client = MCPClient(model, mcp_server_service)


async def test_load_tools():
    await mcp_client.load_tools_and_resources()
    ...
        
    
    
if __name__ == '__main__':
    asyncio.run(test_load_tools())