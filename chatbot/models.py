from typing import Optional
from pydantic import BaseModel
from websockets.asyncio.client import ClientConnection

class Message:
    def __init__(self, websocket, **kwargs):
            self.websocket: ClientConnection = websocket
            self.message_id = kwargs.get('message_id')
            self.message = kwargs.get('message')

    async def reply(self, message: str, is_reply: bool = False):
        bot_message = BotMessage(message=message, reply_to_message_id=self.message_id if is_reply else None)
        await self.websocket.send(bot_message.model_dump_json())

class UserMessage(Message):
    message_id: int
    message: str

    def __init__(self, websocket, message_id, message):
        super().__init__(websocket, message_id=message_id, message=message)

class BotMessage(BaseModel):
    message: str
    reply_to_message_id: Optional[int] = None
