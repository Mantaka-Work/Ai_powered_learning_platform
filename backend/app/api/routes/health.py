"""Health check endpoint."""
from fastapi import APIRouter
from datetime import datetime

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "services": {
            "openai": bool(settings.OPENAI_API_KEY),
            "supabase": bool(settings.SUPABASE_URL),
            "perplexity": bool(settings.PERPLEXITY_API_KEY)
        }
    }
