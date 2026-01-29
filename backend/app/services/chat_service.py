"""Chat service for conversational interactions."""
from typing import Optional, List, Dict, Any, AsyncGenerator
from uuid import UUID

from app.core.rag.chains import get_chains
from app.core.rag.memory import get_memory
from app.services.search_service import get_search_service
from app.db.repositories.chat_repo import get_chat_repository
from app.config import settings


class ChatService:
    """Service for chat interactions with RAG."""
    
    def __init__(self):
        self.rag_chain = get_chains()
        self.memory = get_memory()
        self.search_service = get_search_service()
        self.chat_repo = get_chat_repository()
    
    async def create_session(
        self,
        user_id: UUID,
        course_id: UUID,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new chat session."""
        session = await self.chat_repo.create_session(
            user_id=user_id,
            course_id=course_id,
            title=title
        )
        
        return session
    
    async def get_sessions(
        self,
        user_id: UUID,
        course_id: Optional[UUID] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get chat sessions for a user."""
        return await self.chat_repo.get_user_sessions(
            user_id=user_id,
            course_id=course_id,
            limit=limit
        )
    
    async def get_session_history(
        self,
        session_id: UUID,
        limit: int = 50
    ) -> Optional[Dict[str, Any]]:
        """Get a session with its message history."""
        return await self.chat_repo.get_session_with_messages(
            session_id=session_id,
            message_limit=limit
        )
    
    async def send_message(
        self,
        session_id: UUID,
        user_id: UUID,
        course_id: UUID,
        content: str,
        include_web_search: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Send a message and get a response.
        
        Returns the complete response (non-streaming).
        """
        # Store user message
        await self.chat_repo.add_message(
            session_id=session_id,
            role="user",
            content=content
        )
        
        # Get conversation history
        history = await self.memory.get_history(session_id, limit=10)
        
        # Search for relevant context
        search_results = await self.search_service.hybrid_search(
            query=content,
            course_id=course_id,
            limit=5,
            include_web=include_web_search
        )
        
        # Prepare context
        context = self._prepare_context(search_results)
        
        # Generate response
        response = await self.rag_chain.generate_response(
            query=content,
            context=context,
            chat_history=history
        )
        
        # Prepare sources
        sources = {
            "course": [
                {
                    "title": r["material_title"],
                    "type": r["file_type"],
                    "relevance": r["relevance_score"]
                }
                for r in search_results.get("course_results", [])[:3]
            ]
        }
        
        used_web = False
        if search_results.get("web_results"):
            used_web = True
            sources["web"] = [
                {"title": r["title"], "url": r["url"]}
                for r in search_results.get("web_results", [])[:3]
            ]
        
        # Store assistant message
        message = await self.chat_repo.add_message(
            session_id=session_id,
            role="assistant",
            content=response,
            sources=list(sources.get("course", [])) + list(sources.get("web", [])),
            used_web_search=used_web
        )
        
        # Update memory
        await self.memory.add_message(
            session_id=session_id,
            role="assistant",
            content=response,
            used_web_search=used_web
        )
        
        return {
            "message": message,
            "session_id": str(session_id),
            "sources": sources
        }
    
    async def stream_message(
        self,
        session_id: UUID,
        user_id: UUID,
        course_id: UUID,
        content: str,
        include_web_search: Optional[bool] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a message and stream the response.
        
        Yields chunks of the response as they are generated.
        """
        # Store user message
        await self.chat_repo.add_message(
            session_id=session_id,
            role="user",
            content=content
        )
        
        # Get conversation history
        history = await self.memory.get_history(session_id, limit=10)
        
        # Search for relevant context
        search_results = await self.search_service.hybrid_search(
            query=content,
            course_id=course_id,
            limit=5,
            include_web=include_web_search
        )
        
        # Prepare context
        context = self._prepare_context(search_results)
        
        # Prepare sources early
        sources = {
            "course": [
                {"title": r["material_title"], "type": r["file_type"], "relevance": r["relevance_score"]}
                for r in search_results.get("course_results", [])[:3]
            ]
        }
        
        used_web = False
        if search_results.get("web_results"):
            used_web = True
            sources["web"] = [
                {"title": r["title"], "url": r["url"]}
                for r in search_results.get("web_results", [])[:3]
            ]
        
        # Yield sources first
        yield {
            "type": "sources",
            "sources": sources,
            "used_web_search": used_web
        }
        
        # Stream response
        full_response = ""
        async for chunk in self.rag_chain.generate_response_stream(
            query=content,
            context=context,
            chat_history=history
        ):
            full_response += chunk
            yield {
                "type": "content",
                "content": chunk
            }
        
        # Store complete assistant message
        message = await self.chat_repo.add_message(
            session_id=session_id,
            role="assistant",
            content=full_response,
            sources=list(sources.get("course", [])) + list(sources.get("web", [])),
            used_web_search=used_web
        )
        
        # Update memory
        await self.memory.add_message(
            session_id=session_id,
            role="assistant",
            content=full_response,
            used_web_search=used_web
        )
        
        # Yield completion signal
        yield {
            "type": "done",
            "message_id": message["id"]
        }
    
    async def delete_session(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a chat session."""
        # Also clear memory
        await self.memory.clear_history(session_id)
        
        return await self.chat_repo.delete_session(session_id, user_id)
    
    async def update_session_title(
        self,
        session_id: UUID,
        title: str
    ) -> Dict[str, Any]:
        """Update session title."""
        return await self.chat_repo.update_session_title(session_id, title)
    
    def _prepare_context(self, search_results: Dict) -> str:
        """Prepare context string from search results."""
        parts = []
        
        # Course context
        for i, result in enumerate(search_results.get("course_results", [])[:3], 1):
            content = result.get("content", "")
            title = result.get("material_title", "Course Material")
            parts.append(f"📚 [Course Source {i}: {title}]\n{content}")
        
        # Web context
        for i, result in enumerate(search_results.get("web_results", [])[:2], 1):
            snippet = result.get("snippet", "")
            title = result.get("title", "Web Source")
            url = result.get("url", "")
            parts.append(f"🌐 [Web Source {i}: {title}]\nURL: {url}\n{snippet}")
        
        return "\n\n---\n\n".join(parts) if parts else "No relevant context found."


# Singleton instance
_chat_service = None


def get_chat_service() -> ChatService:
    """Get or create chat service singleton."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
