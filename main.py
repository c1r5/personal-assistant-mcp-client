
# 

import asyncio
import logging
import signal

from os import getenv
from anyio import Path
from langchain_google_genai import ChatGoogleGenerativeAI

from modules.api.chatbot_service import ChatbotService
from modules.clients.chatbot_client import ChatBotClient
from modules.clients.mcp_client import MCPClient
from modules.services.mcp_server_service import MCPServerService

logger = logging.getLogger(__name__)

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-002",
    temperature=0.75
)

chatbot_service = ChatbotService(getenv("CHAT_SERVICE_URL", "ws://localhost:8000/ws/chat"))
mcp_server_service = MCPServerService()
mcp_client = MCPClient(model, mcp_server_service)
chatbot_client = ChatBotClient(mcp_client)


async def main ():
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()
    
    def shutdown():
        print("Shutdown signal received.")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    start_chatbot = asyncio.create_task(chatbot_service.start_chatbot())
    load_mcp_tools = asyncio.create_task(mcp_client.load_tools())
        
    await stop_event.wait()

    print("Cancelando tarefas...")
    start_chatbot.cancel()

    try:
        await asyncio.gather(load_mcp_tools, start_chatbot)
    except asyncio.CancelledError:
        print("Tarefas canceladas com sucesso.")
        await chatbot_service.close()
        
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    chatbot_service.add_on_message_listener(chatbot_client.on_message)
    chatbot_client.add_on_response_listener(chatbot_service.send_message)
    
    asyncio.run(main())