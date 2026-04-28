from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime


class ChatRequest(BaseModel):
    question: str

class SourceData(BaseModel):
    book_title: str
    page: Union[int, str]
    dense_score: float
    
class ChatResponse(BaseModel):
    answer: str
    success: bool = True
    sources: List[SourceData] = []
    time_taken_seconds: float = 0.0
    chunks_used: int = 0

class MessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

class ChatRead(BaseModel):
    id: int
    title: str
    created_at: datetime

class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)

class QueryResponse(BaseModel):
    answer: str
    chat_id: int