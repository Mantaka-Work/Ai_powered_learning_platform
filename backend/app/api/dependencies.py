"""FastAPI dependencies for dependency injection."""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db.supabase_client import get_supabase_client
from app.services.material_service import MaterialService
from app.services.search_service import SearchService
from app.services.generation_service import GenerationService
from app.services.chat_service import ChatService


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
):
    """Get current authenticated user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(credentials.credentials)
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {str(e)}"
        )


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
):
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(credentials.credentials)
        return user.user
    except Exception:
        return None


def get_material_service() -> MaterialService:
    """Get material service instance."""
    return MaterialService()


def get_search_service() -> SearchService:
    """Get search service instance."""
    return SearchService()


def get_generation_service() -> GenerationService:
    """Get generation service instance."""
    return GenerationService()


def get_chat_service() -> ChatService:
    """Get chat service instance."""
    return ChatService()
