
# 

import asyncio
import logging
import signal

from os import getenv
from langchain_google_genai import ChatGoogleGenerativeAI

from modules.api.chatbot_service import ChatbotService


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
chatbot = ChatbotService(ws_url=getenv("CHAT_SERVICE_URL", "ws://localhost:8000/ws/chat"))

async def main ():
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()
    
    def shutdown():
        print("Shutdown signal received.")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    chatbot_task = asyncio.create_task(chatbot.start_chatbot())

    await stop_event.wait()

    print("Cancelando tarefas...")
    chatbot_task.cancel()

    try:
        await asyncio.gather(chatbot_task)
    except asyncio.CancelledError:
        print("Tarefas canceladas com sucesso.")
        await chatbot.close()
        
if __name__ == "__main__":
    asyncio.run(main())