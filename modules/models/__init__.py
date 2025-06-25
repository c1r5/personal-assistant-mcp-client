from typing import Any, Optional
import httpx
from pydantic import BaseModel


class SSEServerParameters(BaseModel):
    url: str
    headers: Optional[dict[str, Any]] = None