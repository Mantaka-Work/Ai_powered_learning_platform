"""RAG retrieval logic."""
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.core.rag.vectorstore import get_vector_store
from app.core.rag.embeddings import get_embeddings_service
from app.config import get_settings


class Retriever:
    """RAG retriever for course materials."""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.embeddings = get_embeddings_service()
    
    async def retrieve(
        self,
        query: str,
        course_id: UUID,
        limit: int = 5,
        category: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            course_id: Course to search within
            limit: Maximum results
            category: Filter by theory/lab
            file_type: Filter by file type
        
        Returns:
            List of relevant document chunks with metadata
        """
        results = await self.vector_store.similarity_search(
            query=query,
            course_id=course_id,
            limit=limit,
            category=category,
            file_type=file_type,
            threshold=settings.WEB_SEARCH_RELEVANCE_THRESHOLD
        )
        
        return self._format_results(results)
    
    async def retrieve_with_scores(
        self,
        query: str,
        course_id: UUID,
        limit: int = 5,
        category: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], float]:
        """
        Retrieve documents and return average relevance score.
        
        Returns:
            Tuple of (results, average_relevance_score)
        """
        results = await self.vector_store.similarity_search(
            query=query,
            course_id=course_id,
            limit=limit,
            category=category,
            threshold=0.0  # Get all results to calculate average
        )
        
        if not results:
            return [], 0.0
        
        # Calculate average relevance
        avg_relevance = sum(r.get("similarity", 0) for r in results) / len(results)
        
        # Filter by threshold
        filtered = [r for r in results if r.get("similarity", 0) >= settings.WEB_SEARCH_RELEVANCE_THRESHOLD]
        
        return self._format_results(filtered[:limit]), avg_relevance
    
    def _format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format results for API response."""
        formatted = []
        for r in results:
            formatted.append({
                "id": r.get("id"),
                "content": r.get("content"),
                "material_id": r.get("material_id"),
                "material_title": r.get("material_title"),
                "file_type": r.get("file_type"),
                "category": r.get("category"),
                "relevance_score": r.get("similarity", 0),
                "chunk_index": r.get("chunk_index"),
                "metadata": r.get("metadata", {})
            })
        return formatted
    
    async def get_context_for_generation(
        self,
        topic: str,
        course_id: UUID,
        max_chunks: int = 10
    ) -> str:
        """
        Get combined context from relevant documents for generation.
        
        Returns a formatted string of relevant content.
        """
        results = await self.retrieve(
            query=topic,
            course_id=course_id,
            limit=max_chunks
        )
        
        if not results:
            return ""
        
        # Combine content with source attribution
        context_parts = []
        for i, r in enumerate(results, 1):
            source = r.get("material_title", "Unknown source")
            content = r.get("content", "")
            context_parts.append(f"[Source {i}: {source}]\n{content}")
        
        return "\n\n---\n\n".join(context_parts)


# Singleton instance
_retriever = None


def get_retriever() -> Retriever:
    """Get or create retriever singleton."""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
