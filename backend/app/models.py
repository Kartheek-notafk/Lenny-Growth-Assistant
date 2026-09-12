from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    skill: Optional[str] = None

class Source(BaseModel):
    title: str
    source: str
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    artifact: Optional[str] = None
    provider: str
