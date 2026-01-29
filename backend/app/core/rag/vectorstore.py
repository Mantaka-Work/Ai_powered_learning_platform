"""Supabase pgvector operations for vector storage and retrieval."""
from typing import List, Optional, Dict, Any
from uuid import UUID
import json

from app.db.supabase_client import get_supabase_client
from app.core.rag.embeddings import get_embeddings_service
from app.config import settings


class VectorStore:
    """Vector store using Supabase pgvector for similarity search."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.embeddings = get_embeddings_service()
        self.table_name = "document_embeddings"
    
    async def add_documents(
        self,
        texts: List[str],
        material_id: UUID,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[UUID]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text chunks to embed and store
            material_id: ID of the parent material
            metadatas: Optional metadata for each chunk
        
        Returns:
            List of chunk IDs
        """
        # Generate embeddings
        embeddings = await self.embeddings.embed_documents(texts)
        
        # Prepare records
        records = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            records.append({
                "material_id": str(material_id),
                "content": text,
                "chunk_index": i,
                "metadata": json.dumps(metadata),
                "embedding": embedding
            })
        
        # Insert into Supabase
        result = self.supabase.table(self.table_name).insert(records).execute()
        
        return [UUID(r["id"]) for r in result.data]
    
    async def similarity_search(
        self,
        query: str,
        course_id: UUID,
        limit: int = 5,
        category: Optional[str] = None,
        file_type: Optional[str] = None,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query
            course_id: Course to search within
            limit: Maximum results to return
            category: Filter by category (theory/lab)
            file_type: Filter by file type
            threshold: Minimum similarity threshold
        
        Returns:
            List of matching documents with scores
        """
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.embed_query(query)
            
            # Build RPC call for vector similarity search
            # This uses a Supabase function we'll create
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
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
    
    async def delete_by_material(self, material_id: UUID) -> int:
        """Delete all chunks for a material."""
        result = self.supabase.table(self.table_name)\
            .delete()\
            .eq("material_id", str(material_id))\
            .execute()
        
        return len(result.data) if result.data else 0
    
    async def get_chunks_by_material(self, material_id: UUID) -> List[Dict[str, Any]]:
        """Get all chunks for a material."""
        result = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("material_id", str(material_id))\
            .order("chunk_index")\
            .execute()
        
        return result.data if result.data else []


# Singleton instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
