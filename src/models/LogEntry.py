from pydantic import BaseModel
from typing import Optional


class LogEntry(BaseModel):
    timestamp: str
    endpoint: str
    status: int
    process_time: float
    user: Optional[str] = None
    user_id: Optional[str] = None

