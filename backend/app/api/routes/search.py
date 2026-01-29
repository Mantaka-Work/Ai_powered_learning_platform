"""Search routes - semantic, hybrid, and web search."""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.api.dependencies import get_search_service
from app.services.search_service import SearchService
from app.db.models import SearchResult, SearchResponse

router = APIRouter()


class SemanticSearchRequest(BaseModel):
    query: str
    course_id: UUID
    category: Optional[str] = None  # theory or lab
    file_type: Optional[str] = None
    limit: int = 5


class HybridSearchRequest(BaseModel):
    query: str
    course_id: UUID
    category: Optional[str] = None
    include_web: Optional[bool] = None  # None = auto-detect based on relevance
    limit: int = 5


class WebSearchRequest(BaseModel):
    query: str
    limit: int = 5
    cache: bool = True


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    service: SearchService = Depends(get_search_service)
):
    """
    Semantic search within course materials only.
    Uses RAG-based retrieval with vector embeddings.
    """
    try:
        results = await service.semantic_search(
            query=request.query,
            course_id=request.course_id,
            category=request.category,
            file_type=request.file_type,
            limit=request.limit
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/hybrid", response_model=SearchResponse)
async def hybrid_search(
    request: HybridSearchRequest,
    service: SearchService = Depends(get_search_service)
):
    """
    Hybrid search combining course materials and web search.
    
    - If include_web is None: auto-triggers web search when relevance < 40%
    - If include_web is True: always includes web search
    - If include_web is False: course materials only
    """
    try:
        results = await service.hybrid_search(
            query=request.query,
            course_id=request.course_id,
            category=request.category,
            include_web=request.include_web,
            limit=request.limit
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/web")
async def web_search(
    request: WebSearchRequest,
    service: SearchService = Depends(get_search_service)
):
    """
    Force web search via Perplexity API.
    Returns web results only (no course materials).
    """
    try:
        results = await service.web_search(
            query=request.query,
            limit=request.limit,
            use_cache=request.cache
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web search failed: {str(e)}"
        )


@router.get("/filters/{course_id}")
async def get_search_filters(
    course_id: UUID,
    service: SearchService = Depends(get_search_service)
):
    """Get available search filters for a course."""
    try:
        filters = await service.get_available_filters(course_id)
        return filters
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/suggestions")
async def get_search_suggestions(
    query: str,
    course_id: UUID,
    service: SearchService = Depends(get_search_service)
):
    """Get search query suggestions/autocomplete."""
    try:
        suggestions = await service.get_suggestions(query, course_id)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
