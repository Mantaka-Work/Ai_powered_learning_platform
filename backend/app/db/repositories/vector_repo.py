"""Vector embeddings repository for pgvector operations."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.db.supabase_client import get_supabase_client


class VectorRepository:
    """Repository for vector embeddings in pgvector."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.table_name = "document_embeddings"
    
    def _sanitize_text(self, text: str) -> str:
        """Remove null characters and other problematic unicode from text.
        
        PostgreSQL cannot store null characters (\u0000) in text fields.
        """
        if not text:
            return ""
        # Remove null characters
        text = text.replace('\x00', '')
        # Remove other problematic characters
        text = text.replace('\u0000', '')
        # Remove any other control characters except newlines and tabs
        text = ''.join(char for char in text if char == '\n' or char == '\t' or char >= ' ')
        return text
    
    async def store_embedding(
        self,
        material_id: UUID,
        content: str,
        embedding: List[float],
        chunk_index: int,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Store a document chunk embedding."""
        data = {
            "material_id": str(material_id),
            "content": self._sanitize_text(content),
            "embedding": embedding,
            "chunk_index": chunk_index,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = self.supabase.table(self.table_name).insert(data).execute()
        
        return result.data[0] if result.data else None
    
    async def store_embeddings_batch(
        self,
        material_id: UUID,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Store multiple embeddings in batch.
        
        Args:
            material_id: The material ID
            chunks: List of dicts with 'content', 'embedding', 'chunk_index', 'metadata'
        """
        data = [
            {
                "material_id": str(material_id),
                "content": self._sanitize_text(chunk["content"]),
                "embedding": chunk["embedding"],
                "chunk_index": chunk["chunk_index"],
                "metadata": chunk.get("metadata", {}),
                "created_at": datetime.utcnow().isoformat()
            }
            for chunk in chunks
        ]
        
        result = self.supabase.table(self.table_name).insert(data).execute()
        
        return result.data if result.data else []
    
    async def similarity_search(
        self,
        query_embedding: List[float],
        course_id: UUID,
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using pgvector.
        
        Uses the match_documents RPC function for cosine similarity search.
        """
        result = self.supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_count": limit,
                "filter_course_id": str(course_id),
                "similarity_threshold": threshold
            }
        ).execute()
        
        return result.data if result.data else []
    
    async def get_by_material(
        self,
        material_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all embeddings for a material."""
        result = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("material_id", str(material_id))\
            .order("chunk_index")\
            .execute()
        
        return result.data if result.data else []
    
    async def delete_by_material(self, material_id: UUID) -> bool:
        """Delete all embeddings for a material."""
        result = self.supabase.table(self.table_name)\
            .delete()\
            .eq("material_id", str(material_id))\
            .execute()
        
        return bool(result.data)
    
    async def count_by_course(self, course_id: UUID) -> int:
        """Count embeddings for a course (via materials)."""
        # This requires a join, using RPC
        result = self.supabase.rpc(
            "count_embeddings_by_course",
            {"p_course_id": str(course_id)}
        ).execute()
        
        return result.data if result.data else 0


# Singleton instance
_vector_repo = None


def get_vector_repository() -> VectorRepository:
    """Get or create vector repository singleton."""
    global _vector_repo
    if _vector_repo is None:
        _vector_repo = VectorRepository()
    return _vector_repo
