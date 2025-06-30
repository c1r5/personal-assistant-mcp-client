#

import asyncio
import logging

from os import getenv
from modules.chatbot.service import ChatbotService

logger = logging.getLogger(__name__)


async def main():
    chatbot_service = ChatbotService(
        getenv("CHAT_SERVICE_URL", "ws://localhost:8000/ws/chat")
    )
    async for message in chatbot_service.chatbot_message():
        ...


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    asyncio.run(main())

