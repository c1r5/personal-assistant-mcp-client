from ast import List
from typing import Any, Awaitable, Callable, Union
from pydantic import ValidationError
import websockets

from .models import UserMessage  # Assuming UserMessage is defined in models.py

logger = __import__('logging').getLogger(__name__)

MessageListener = Callable[[UserMessage], Union[Awaitable[Any], Any]]

class ChatbotService:
    __on_message_listeners: list[MessageListener] = []

    def __init__(self, ws_url: str):
        self.ws_url = ws_url

    async def start_chatbot(self):
        try:
            async with websockets.connect(f"{self.ws_url}/ws") as websocket:
                logger.info(f"Connected to {self.ws_url}")
                self.ws = websocket
                
                while True:
                        message = await websocket.recv()
                        await self.handle_message(str(message))
                    
        except Exception as e:
            logger.error(f"WebSocket connection closed: {e}")

    async def add_on_message_listener(self, listener: MessageListener):
        """Add a listener for incoming messages."""
        self.__on_message_listeners.append(listener)
        
    async def handle_message(self, message: str):
        try:
            user_message = UserMessage.model_validate(message)
            for listener in self.__on_message_listeners:
                await listener(user_message)
        except ValidationError as e:
            logger.error(f"Error parsing message: {e}")
            return

    async def close(self):
        if self.ws:
            await self.ws.close()
            logger.info("WebSocket connection closed")
        else:
            logger.warning("WebSocket connection was not established")