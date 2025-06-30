from typing import Optional
from pydantic import BaseModel

class UserMessage(BaseModel):
    message_id: int
    message: str
    
    
class BotMessage(BaseModel):
    message: str
    reply_to_message_id: Optional[int] = None