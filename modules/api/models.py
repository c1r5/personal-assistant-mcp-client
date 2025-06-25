from typing import Optional
from pydantic import BaseModel

class UserMessage(BaseModel):
    message_id: int
    message: Optional[str] = None 