"""OpenAI embeddings service."""
from typing import List
import openai
from app.config import settings


class EmbeddingsService:
    """Service for generating text embeddings using OpenAI."""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        # OpenAI supports batch embedding
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query."""
        return await self.embed_text(query)
    
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Generate embeddings for document chunks."""
        # Process in batches of 100 to avoid rate limits
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            embeddings = await self.embed_texts(batch)
            all_embeddings.extend(embeddings)
        
        return all_embeddings


# Singleton instance
_embeddings_service = None


def get_embeddings_service() -> EmbeddingsService:
    """Get or create embeddings service singleton."""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service
