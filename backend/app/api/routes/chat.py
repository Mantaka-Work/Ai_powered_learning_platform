"""Chat interface routes with streaming support."""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from app.api.dependencies import get_current_user, get_chat_service
from app.services.chat_service import ChatService

router = APIRouter()


class CreateSessionRequest(BaseModel):
    course_id: UUID
    title: Optional[str] = None


class ChatMessageRequest(BaseModel):
    session_id: UUID
    message: str
    include_web_search: bool = False  # Explicitly request web search


class ChatMessage(BaseModel):
    id: UUID
    role: str  # user or assistant
    content: str
    sources: Optional[List[dict]] = None
    used_web_search: bool = False
    created_at: str


class ChatSession(BaseModel):
    id: UUID
    course_id: UUID
    title: str
    created_at: str
    updated_at: str
    message_count: int


@router.post("/sessions", response_model=ChatSession)
async def create_session(
    request: CreateSessionRequest,
    current_user = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    """Create a new chat session."""
    try:
        session = await service.create_session(
            course_id=request.course_id,
            user_id=UUID(current_user.id),
            title=request.title
        )
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/sessions", response_model=List[ChatSession])
async def list_sessions(
    course_id: Optional[UUID] = None,
    current_user = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    """List all chat sessions for current user."""
    try:
        sessions = await service.list_sessions(
            user_id=UUID(current_user.id),
            course_id=course_id
        )
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: UUID,
    current_user = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    """Get a chat session with all messages."""
    try:
        session = await service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/message")
async def send_message(
    request: ChatMessageRequest,
    current_user = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    """
    Send a message and get streaming response.
    
    The response integrates:
    - Course material search (always)
    - Content generation (if requested)
    - Web search (if enabled and relevance is low)
    
    Returns Server-Sent Events (SSE) stream.
    """
    try:
        async def generate():
            async for chunk in service.chat_stream(
                session_id=request.session_id,
                message=request.message,
                include_web_search=request.include_web_search,
                user_id=UUID(current_user.id)
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/message/sync")
async def send_message_sync(
    request: ChatMessageRequest,
    current_user = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    """
    Send a message and get non-streaming response.
    Use this for simpler integrations that don't support SSE.
    """
    try:
        response = await service.chat(
            session_id=request.session_id,
            message=request.message,
            include_web_search=request.include_web_search,
            user_id=UUID(current_user.id)
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: UUID,
    current_user = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    """Delete a chat session."""
    try:
        await service.delete_session(session_id, UUID(current_user.id))
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
