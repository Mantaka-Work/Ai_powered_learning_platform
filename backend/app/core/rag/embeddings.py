"""OpenAI embeddings service."""
from typing import List
import openai
from app.config import get_settings


class EmbeddingsService:
    """Service for generating text embeddings using OpenAI."""
    
    def __init__(self):
        settings = get_settings()
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
        """Generate embeddings for multiple texts, processing one at a time to avoid token limits."""
        if not texts:
            return []
        
        # Max safe characters per text (~2000 chars ≈ 500 tokens, well under 8192 limit)
        MAX_CHARS_PER_TEXT = 2000
        
        all_embeddings = []
        for text in texts:
            # Truncate if too long
            if len(text) > MAX_CHARS_PER_TEXT:
                text = text[:MAX_CHARS_PER_TEXT]
            
            # Skip empty texts
            if not text.strip():
                # Return a zero embedding for empty texts
                all_embeddings.append([0.0] * self.dimension)
                continue
            
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                all_embeddings.append(response.data[0].embedding)
            except Exception as e:
                print(f"Warning: Failed to embed text, using zero vector: {e}")
                all_embeddings.append([0.0] * self.dimension)
        
        return all_embeddings
    
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
