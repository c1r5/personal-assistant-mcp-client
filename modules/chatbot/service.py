import websockets
from typing import Any, Awaitable, Callable, Union

from .models import UserMessage

logger = __import__("logging").getLogger(__name__)

MessageListener = Callable[[UserMessage], Union[Awaitable[Any], Any]]


class ChatbotService:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url

    async def chatbot_message(self):
        try:
            async with websockets.connect(f"{self.ws_url}/ws") as websocket:
                logger.info(f"Connected to {self.ws_url}")
                self.ws = websocket

                while True:
                    message = await websocket.recv()
                    yield message
                    # TODO Criar um modelo ChatMessage que vai ser responsavel por ter o metodo reply, abstraindo a forma de responder o usuario
        except Exception as e:
            logger.error(f"WebSocket connection closed: {e}")

    async def close(self):
        if self.ws:
            await self.ws.close()
            logger.info("WebSocket connection closed")
        else:
            logger.warning("WebSocket connection was not established")

