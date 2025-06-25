
# 

import asyncio
import logging
import signal

from os import getenv
from langchain_google_genai import ChatGoogleGenerativeAI

from modules.api.chatbot_service import ChatbotService
from modules.clients.chatbot_client import ChatBotClient
from modules.clients.llm_service import LLMService


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-002",
    temperature=0.75
)

chatbot_service = ChatbotService(getenv("CHAT_SERVICE_URL", "ws://localhost:8000/ws/chat"))

llm_client = LLMService(model)
chatbot_client = ChatBotClient(llm_client)


async def main ():
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()
    
    def shutdown():
        print("Shutdown signal received.")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    chatbot_task = asyncio.create_task(chatbot_service.start_chatbot())

    await stop_event.wait()

    print("Cancelando tarefas...")
    chatbot_task.cancel()

    try:
        await asyncio.gather(chatbot_task)
    except asyncio.CancelledError:
        print("Tarefas canceladas com sucesso.")
        await chatbot_service.close()
        
if __name__ == "__main__":
    chatbot_service.add_on_message_listener(chatbot_client.on_message)
    chatbot_client.add_on_response_listener(chatbot_service.send_message)
    
    asyncio.run(main())