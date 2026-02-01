"""Perplexity API client for web search."""
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime, timedelta

from app.config import get_settings


class PerplexityClient:
    """Client for Perplexity API web search."""
    
    BASE_URL = "https://api.perplexity.ai"
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.PERPLEXITY_API_KEY
        self.rate_limit = settings.PERPLEXITY_RATE_LIMIT
        self._last_request_time = None
        self._request_count = 0
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        recency: str = "week"
    ) -> Dict[str, Any]:
        """
        Search the web using Perplexity API.
        
        Args:
            query: Search query
            limit: Maximum number of results
            recency: Result recency filter (day, week, month, year)
        
        Returns:
            Search results with sources
        """
        if not self.api_key:
            print("[PerplexityClient] No API key configured!")
            return {
                "results": [],
                "error": "Perplexity API key not configured",
                "took_ms": 0
            }
        
        # Check rate limit
        await self._check_rate_limit()
        
        start_time = datetime.now()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar",  # Latest Perplexity online model
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful search assistant. Provide concise, factual information with sources. Include relevant URLs."
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ],
                        "max_tokens": 1024,
                        "return_citations": True,
                        "search_recency_filter": recency
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                took_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                
                # Parse response
                results = self._parse_response(data, limit)
                
                return {
                    "results": results,
                    "took_ms": took_ms,
                    "source": "perplexity"
                }
                
        except httpx.HTTPStatusError as e:
            return {
                "results": [],
                "error": f"API error: {e.response.status_code}",
                "took_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
        except Exception as e:
            return {
                "results": [],
                "error": str(e),
                "took_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
    
    async def research(
        self,
        topic: str,
        context: Optional[str] = None,
        max_sources: int = 10
    ) -> Dict[str, Any]:
        """
        Deep research on a topic with synthesis.
        
        Good for content generation use cases.
        """
        query = topic
        if context:
            query = f"{topic}. Context: {context}"
        
        return await self.search(query, limit=max_sources, recency="month")
    
    def _parse_response(self, data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Parse Perplexity API response into structured results."""
        results = []
        
        # Get the main content
        choices = data.get("choices", [])
        if not choices:
            return results
        
        message = choices[0].get("message", {})
        content = message.get("content", "")
        
        # Get citations if available
        citations = data.get("citations", [])
        
        # Create results from citations
        for i, citation in enumerate(citations[:limit]):
            if isinstance(citation, str):
                # Simple URL citation
                results.append({
                    "title": f"Source {i+1}",
                    "url": citation,
                    "snippet": "",
                    "relevance_score": 0.8,
                    "source_domain": self._extract_domain(citation),
                    "published_date": None
                })
            elif isinstance(citation, dict):
                # Detailed citation
                results.append({
                    "title": citation.get("title", f"Source {i+1}"),
                    "url": citation.get("url", ""),
                    "snippet": citation.get("snippet", ""),
                    "relevance_score": citation.get("score", 0.8),
                    "source_domain": self._extract_domain(citation.get("url", "")),
                    "published_date": citation.get("date")
                })
        
        # If no citations, create a result from the content
        if not results and content:
            results.append({
                "title": "Search Result",
                "url": "",
                "snippet": content[:500],
                "relevance_score": 0.7,
                "source_domain": "perplexity.ai",
                "published_date": datetime.now().isoformat()
            })
        
        return results
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        now = datetime.now()
        
        # Reset counter every minute
        if self._last_request_time and (now - self._last_request_time) > timedelta(minutes=1):
            self._request_count = 0
        
        # Check limit
        if self._request_count >= self.rate_limit:
            wait_time = 60 - (now - self._last_request_time).seconds
            if wait_time > 0:
                import asyncio
                await asyncio.sleep(wait_time)
                self._request_count = 0
        
        self._last_request_time = now
        self._request_count += 1


# Singleton instance
_perplexity_client = None


def get_perplexity_client() -> PerplexityClient:
    """Get or create Perplexity client singleton."""
    global _perplexity_client
    if _perplexity_client is None:
        _perplexity_client = PerplexityClient()
    return _perplexity_client
