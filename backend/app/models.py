from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    skill: Optional[str] = None  # None | "ship30" | "artifact"


class Source(BaseModel):
    title: str
    source: str
    snippet: str
    guest: Optional[str] = None
    url: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    artifact: Optional[str] = None
    provider: str
    grounded: bool = True  # False when no supporting transcript chunks were found


class NewSessionResponse(BaseModel):
    session_id: str


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageOut]
