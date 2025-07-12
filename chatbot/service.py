import websockets

from chatbot.models import UserMessage
from typing import AsyncGenerator
import json

logger = __import__("logging").getLogger(__name__)


class ChatbotService:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url

    async def on_user_message(self) -> AsyncGenerator[UserMessage, None]:
        try:
            async with websockets.connect(self.ws_url) as websocket:
                logger.info(f"Connected to {self.ws_url}")
                self.ws = websocket

                while True:
                    message = await websocket.recv()
                    try:
                        parse_message = json.loads(message)

                        user_message = UserMessage(
                            websocket=websocket,
                            message_id=parse_message.get("message_id", None),
                            message=parse_message.get("message", None)
                        )

                        yield user_message
                    except Exception as e:
                        logger.error(f"Invalid message received: {e}")
                        continue
                    # TODO Criar um modelo ChatMessage que vai ser responsavel por ter o metodo reply, abstraindo a forma de responder o usuario
        except Exception as e:
            logger.error(f"WebSocket connection closed: {e}")

    async def close(self):
        if self.ws:
            await self.ws.close()
            logger.info("WebSocket connection closed")
        else:
            logger.warning("WebSocket connection was not established")
