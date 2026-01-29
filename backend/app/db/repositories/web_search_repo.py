"""Web search cache repository."""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.db.repositories.base_repo import BaseRepository
from app.config import settings


class WebSearchRepository(BaseRepository):
    """Repository for cached web search results."""
    
    def __init__(self):
        super().__init__("web_search_cache")
    
    async def get_cached_results(
        self,
        query_hash: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached search results if not expired."""
        result = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("query_hash", query_hash)\
            .single()\
            .execute()
        
        if not result.data:
            return None
        
        # Check expiration
        cached = result.data
        created = datetime.fromisoformat(cached["created_at"].replace("Z", "+00:00"))
        expires = created + timedelta(days=settings.SEARCH_CACHE_DAYS)
        
        if datetime.now(created.tzinfo) > expires:
            # Cache expired
            await self.delete_by_hash(query_hash)
            return None
        
        return cached
    
    async def cache_results(
        self,
        query_hash: str,
        query: str,
        results: List[Dict[str, Any]],
        provider: str = "perplexity"
    ) -> Dict[str, Any]:
        """Cache search results."""
        data = {
            "query_hash": query_hash,
            "query": query,
            "results": results,
            "provider": provider,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Upsert to handle duplicates
        result = self.supabase.table(self.table_name)\
            .upsert(data, on_conflict="query_hash")\
            .execute()
        
        return result.data[0] if result.data else None
    
    async def delete_by_hash(self, query_hash: str) -> bool:
        """Delete cached results by hash."""
        result = self.supabase.table(self.table_name)\
            .delete()\
            .eq("query_hash", query_hash)\
            .execute()
        
        return bool(result.data)
    
    async def cleanup_expired(self) -> int:
        """Remove expired cache entries. Returns count of deleted entries."""
        expiry_date = datetime.utcnow() - timedelta(days=settings.SEARCH_CACHE_DAYS)
        
        result = self.supabase.table(self.table_name)\
            .delete()\
            .lt("created_at", expiry_date.isoformat())\
            .execute()
        
        return len(result.data) if result.data else 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = await self.count()
        
        # Count by provider
        providers = self.supabase.table(self.table_name)\
            .select("provider")\
            .execute()
        
        provider_counts = {}
        if providers.data:
            for p in providers.data:
                prov = p["provider"]
                provider_counts[prov] = provider_counts.get(prov, 0) + 1
        
        return {
            "total_cached": total,
            "by_provider": provider_counts,
            "cache_duration_days": settings.SEARCH_CACHE_DAYS
        }


# Singleton instance
_web_search_repo = None


def get_web_search_repository() -> WebSearchRepository:
    """Get or create web search repository singleton."""
    global _web_search_repo
    if _web_search_repo is None:
        _web_search_repo = WebSearchRepository()
    return _web_search_repo
