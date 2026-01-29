"""Search service for semantic and hybrid search."""
import time
from typing import Optional, List, Dict, Any
from uuid import UUID

from app.core.rag.embeddings import get_embeddings_service
from app.core.rag.retriever import get_retriever
from app.core.mcp.web_search_service import get_web_search_service
from app.db.repositories.material_repo import get_material_repository
from app.config import settings


class SearchService:
    """Service for hybrid search (course materials + web)."""
    
    def __init__(self):
        self.embedding_service = get_embeddings_service()
        self.retriever = get_retriever()
        self.web_search = get_web_search_service()
        self.material_repo = get_material_repository()
    
    async def semantic_search(
        self,
        query: str,
        course_id: UUID,
        limit: int = 10,
        category: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search course materials using semantic similarity.
        
        Returns results from course materials only.
        """
        start_time = time.time()
        
        # Get search results from retriever
        results = await self.retriever.retrieve(
            query=query,
            course_id=course_id,
            limit=limit,
            category=category,
            file_type=file_type
        )
        
        # Enrich results with material metadata
        enriched = await self._enrich_results(results)
        
        # Calculate average relevance
        avg_relevance = sum(r["relevance_score"] for r in enriched) / len(enriched) if enriched else 0
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        return {
            "query": query,
            "course_results": enriched,
            "web_results": [],
            "took_ms": elapsed_ms,
            "used_web_search": False,
            "average_relevance": avg_relevance
        }
    
    async def hybrid_search(
        self,
        query: str,
        course_id: UUID,
        limit: int = 10,
        include_web: Optional[bool] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Hybrid search that automatically uses web search when course relevance is low.
        
        Args:
            query: Search query
            course_id: Course to search in
            limit: Max results per source
            include_web: Force web search (None = auto-decide based on relevance)
            category: Filter by category (theory/lab)
        """
        start_time = time.time()
        
        # First, search course materials
        course_results = await self.retriever.retrieve(
            query=query,
            course_id=course_id,
            limit=limit,
            category=category
        )
        
        enriched_course = await self._enrich_results(course_results)
        
        # Calculate average relevance
        avg_relevance = sum(r["relevance_score"] for r in enriched_course) / len(enriched_course) if enriched_course else 0
        
        # Decide whether to use web search
        web_results = []
        used_web = False
        
        if include_web is None:
            # Auto-decide based on relevance threshold
            should_use_web = avg_relevance < settings.WEB_SEARCH_RELEVANCE_THRESHOLD
        else:
            should_use_web = include_web
        
        if should_use_web:
            try:
                print(f"[SearchService] Triggering web search for query: {query}")
                web_response = await self.web_search.search(query)
                print(f"[SearchService] Web search response: {web_response}")
                web_results = web_response.get("results", [])[:limit]
                print(f"[SearchService] Got {len(web_results)} web results")
                used_web = True
            except Exception as e:
                # Log but don't fail the entire search
                print(f"[SearchService] Web search failed: {e}")
                import traceback
                traceback.print_exc()
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        return {
            "query": query,
            "course_results": enriched_course,
            "web_results": web_results,
            "took_ms": elapsed_ms,
            "used_web_search": used_web,
            "average_relevance": avg_relevance,
            "web_search_triggered_by": "low_relevance" if used_web and include_web is None else ("user_request" if used_web else None)
        }
    
    async def web_search(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Perform web search only using Perplexity.
        
        Use this when user explicitly wants web results.
        """
        start_time = time.time()
        
        try:
            response = await self.web_search.search(query)
            web_results = response.get("results", [])[:limit]
        except Exception as e:
            print(f"Web search failed: {e}")
            web_results = []
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        return {
            "query": query,
            "course_results": [],
            "web_results": web_results,
            "took_ms": elapsed_ms,
            "used_web_search": True,
            "average_relevance": 0.0
        }
    
    async def _filter_results(
        self,
        results: List[Dict],
        category: Optional[str],
        file_type: Optional[str]
    ) -> List[Dict]:
        """Filter results by category and file type."""
        filtered = []
        
        for result in results:
            material_id = result.get("material_id")
            if not material_id:
                continue
            
            material = await self.material_repo.get_by_id(UUID(material_id))
            if not material:
                continue
            
            if category and material.get("category") != category:
                continue
            
            if file_type and material.get("file_type") != file_type:
                continue
            
            filtered.append(result)
        
        return filtered
    
    async def _enrich_results(
        self,
        results: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Enrich search results with material metadata."""
        enriched = []
        
        for result in results:
            material_id = result.get("material_id")
            if not material_id:
                enriched.append(result)
                continue
            
            material = await self.material_repo.get_by_id(UUID(material_id))
            
            enriched.append({
                "id": result.get("id"),
                "content": result.get("content", ""),
                "material_id": material_id,
                "material_title": material.get("title", "Unknown") if material else "Unknown",
                "file_type": material.get("file_type", "") if material else "",
                "category": material.get("category", "") if material else "",
                "relevance_score": result.get("similarity", result.get("relevance_score", 0)),
                "chunk_index": result.get("chunk_index", 0),
                "metadata": result.get("metadata", {})
            })
        
        return enriched


# Singleton instance
_search_service = None


def get_search_service() -> SearchService:
    """Get or create search service singleton."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
