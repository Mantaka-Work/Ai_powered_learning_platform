"""Web search orchestration service."""
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from app.core.mcp.perplexity_client import get_perplexity_client
from app.db.supabase_client import get_supabase_client
from app.config import settings


class WebSearchService:
    """Orchestrate web search with caching."""
    
    def __init__(self):
        self.perplexity = get_perplexity_client()
        self.supabase = get_supabase_client()
        self.cache_ttl = settings.PERPLEXITY_CACHE_TTL
    
    async def search(
        self,
        query: str,
        course_id: Optional[UUID] = None,
        limit: int = 5,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Search the web with caching.
        
        Args:
            query: Search query
            course_id: Optional course ID for cache scoping
            limit: Maximum results
            use_cache: Whether to use/update cache
        
        Returns:
            Search results
        """
        # Try cache first
        if use_cache:
            cached = await self._get_cached(query, course_id)
            if cached:
                return {
                    **cached,
                    "cached": True
                }
        
        # Search via Perplexity
        results = await self.perplexity.search(query, limit=limit)
        
        # Cache results
        if use_cache and results.get("results"):
            await self._cache_results(query, course_id, results)
        
        return {
            **results,
            "cached": False
        }
    
    async def research_for_generation(
        self,
        topic: str,
        course_id: UUID,
        context: Optional[str] = None
    ) -> str:
        """
        Research a topic for content generation.
        
        Returns formatted context string for LLM.
        """
        results = await self.search(
            query=f"{topic} educational explanation examples",
            course_id=course_id,
            limit=5
        )
        
        if not results.get("results"):
            return ""
        
        # Format results as context
        context_parts = []
        for i, r in enumerate(results["results"], 1):
            source = r.get("source_domain", "web")
            snippet = r.get("snippet", "")
            url = r.get("url", "")
            
            if snippet:
                context_parts.append(f"[Web Source {i}: {source}]\n{snippet}\nURL: {url}")
        
        return "\n\n---\n\n".join(context_parts)
    
    async def should_search_web(
        self,
        course_relevance: float,
        query: str
    ) -> bool:
        """
        Determine if web search should be triggered.
        
        Args:
            course_relevance: Relevance score from course materials (0-1)
            query: User query
        
        Returns:
            Whether to trigger web search
        """
        # Explicit web search request
        web_keywords = ["latest", "current", "recent", "news", "update", "trend"]
        if any(kw in query.lower() for kw in web_keywords):
            return True
        
        # Low relevance threshold
        if course_relevance < settings.WEB_SEARCH_RELEVANCE_THRESHOLD:
            return True
        
        return False
    
    async def _get_cached(
        self,
        query: str,
        course_id: Optional[UUID]
    ) -> Optional[Dict[str, Any]]:
        """Get cached search results."""
        try:
            query_builder = self.supabase.table("web_search_cache")\
                .select("*")\
                .eq("query", query)
            
            if course_id:
                query_builder = query_builder.eq("course_id", str(course_id))
            
            result = query_builder.single().execute()
            
            if result.data:
                # Check expiry
                expires_at = result.data.get("expires_at")
                if expires_at:
                    expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                    if datetime.now(expiry.tzinfo) > expiry:
                        return None
                
                # Update usage stats
                await self._update_cache_usage(result.data["id"])
                
                return result.data.get("results")
            
            return None
        except Exception:
            return None
    
    async def _cache_results(
        self,
        query: str,
        course_id: Optional[UUID],
        results: Dict[str, Any]
    ):
        """Cache search results."""
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=self.cache_ttl)
            
            self.supabase.table("web_search_cache").upsert({
                "query": query,
                "course_id": str(course_id) if course_id else None,
                "results": results,
                "searched_at": datetime.utcnow().isoformat(),
                "expires_at": expires_at.isoformat(),
                "used_count": 1,
                "last_used_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception:
            pass  # Cache failure shouldn't break search
    
    async def _update_cache_usage(self, cache_id: str):
        """Update cache usage statistics."""
        try:
            self.supabase.table("web_search_cache")\
                .update({
                    "used_count": self.supabase.sql("used_count + 1"),
                    "last_used_at": datetime.utcnow().isoformat()
                })\
                .eq("id", cache_id)\
                .execute()
        except Exception:
            pass
    
    async def clear_expired_cache(self):
        """Clear expired cache entries."""
        try:
            self.supabase.table("web_search_cache")\
                .delete()\
                .lt("expires_at", datetime.utcnow().isoformat())\
                .execute()
        except Exception:
            pass


# Singleton instance
_web_search_service = None


def get_web_search_service() -> WebSearchService:
    """Get or create web search service singleton."""
    global _web_search_service
    if _web_search_service is None:
        _web_search_service = WebSearchService()
    return _web_search_service
