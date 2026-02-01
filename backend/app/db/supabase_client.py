"""Supabase client initialization."""
from supabase import create_client, Client
from functools import lru_cache

from app.config import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get Supabase client singleton.
    
    Uses service key if available for backend operations,
    otherwise uses anon key.
    """
    settings = get_settings()
    key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
    return create_client(settings.SUPABASE_URL, key)


def get_supabase_admin_client() -> Client:
    """Get Supabase client with service role key for admin operations."""
    settings = get_settings()
    if not settings.SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_SERVICE_KEY not configured")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
