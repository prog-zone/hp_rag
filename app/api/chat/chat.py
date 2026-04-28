from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select
from app.core.logging import logger
from app.core.postgres import get_session
from app.models.chat import Session as UserSession, Chat, Message
from app.schemas.chat import ChatRead, MessageRead, ChatCreate, QueryRequest, QueryResponse,  ChatRequest, ChatResponse
from app.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

@router.post("/query", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Query the Harry Potter RAG engine. 
    Returns an answer with citations from the books and retrieval metadata.
    """
    try:
        result = await rag_service.answer_question(request.question)
        
        latency = result.get("time_taken_seconds", 0.0)
        chunks = result.get("chunks_used", 0)
        
        logger.info(f"Query successful | latency: {latency}s | chunks_used: {chunks} | query: '{request.question}'")

        return ChatResponse(
            success=True,
            sources=result.get("sources", []),
            time_taken_seconds=result.get("time_taken_seconds", 0.0),
            chunks_used=result.get("chunks_used", 0),
            answer=result["answer"],
        )
    except Exception as e:
        logger.error(f"Query failed | query: '{request.question}' | error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question. Please try again later."
        )

@router.get("/threads", response_model=List[ChatRead])
def get_chats(x_session_id: str = Header(...), db: Session = Depends(get_session)):
    """Retrieve all chat threads for the current session."""
    statement = select(Chat).where(Chat.session_id == x_session_id).order_by(Chat.created_at.desc())
    return db.exec(statement).all()

@router.post("/threads", response_model=ChatRead)
def create_chat(chat_data: ChatCreate, x_session_id: str = Header(...), db: Session = Depends(get_session)):
    """Initialize a new chat thread."""
    session_record = db.get(UserSession, x_session_id)
    if not session_record:
        session_record = UserSession(id=x_session_id)
        db.add(session_record)
    
    new_chat = Chat(title=chat_data.title, session_id=x_session_id)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

@router.get("/threads/{chat_id}/messages", response_model=List[MessageRead])
def get_messages(chat_id: int, db: Session = Depends(get_session)):
    """Fetch the full message history for a specific thread."""
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat.messages

@router.post("/threads/{chat_id}/query", response_model=QueryResponse)
async def chat_thread(
    chat_id: int, 
    request: QueryRequest, 
    db: Session = Depends(get_session)
):
    """Process a question, utilize RAG, and persist the conversation."""
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 1. Save user message
    user_msg = Message(role="user", content=request.question, chat_id=chat_id)
    db.add(user_msg)
    
    # 2. Get Answer from RAG Service
    # In a real app, you would pass the chat history here for context-aware RAG. For simplicity, we're just sending the question.
    answer_text = await rag_service.answer_question(request.question)
    assistant_msg = Message(role="assistant", content=answer_text, chat_id=chat_id)
    db.add(assistant_msg)
    
    db.commit()
    return QueryResponse(answer=answer_text, chat_id=chat_id)