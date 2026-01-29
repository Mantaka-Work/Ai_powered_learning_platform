"""Chat service for conversational interactions."""
from typing import Optional, List, Dict, Any, AsyncGenerator
from uuid import UUID

from app.core.rag.chains import get_chains
from app.core.rag.memory import get_memory
from app.services.search_service import get_search_service
from app.db.repositories.chat_repo import get_chat_repository
from app.core.mcp.perplexity_client import PerplexityClient
from app.config import settings


class ChatService:
    """Service for chat interactions with RAG."""
    
    def __init__(self):
        self.rag_chain = get_chains()
        self.memory = get_memory()
        self.search_service = get_search_service()
        self.chat_repo = get_chat_repository()
        self.perplexity = PerplexityClient()
    
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
        
        # Add message_count for response model compatibility
        session["message_count"] = 0
        
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
        When include_web_search is True, also queries Perplexity for latest web info.
        """
        # Store user message
        await self.chat_repo.add_message(
            session_id=session_id,
            role="user",
            content=content
        )
        
        # Get conversation history
        history = await self.memory.get_history(session_id, limit=10)
        
        # Search for relevant course context
        search_results = await self.search_service.hybrid_search(
            query=content,
            course_id=course_id,
            limit=5,
            include_web=False  # Don't use old web search, we use Perplexity directly
        )
        
        # Prepare context and determine if it's relevant
        context, context_relevance = self._prepare_context_with_relevance(search_results)
        
        # Determine if we should use course context or general knowledge
        use_course_context = context_relevance >= 0.2 and len(search_results.get("course_results", [])) > 0
        
        print(f"[ChatService] Context relevance: {context_relevance:.3f}, Use course context: {use_course_context}")
        
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
        
        # If web search is enabled, query Perplexity
        web_context = ""
        used_web = False
        if include_web_search:
            print(f"[ChatService] Web search enabled, querying Perplexity...")
            perplexity_results = await self.perplexity.search(query=content, limit=5, recency="week")
            
            if perplexity_results.get("results") and not perplexity_results.get("error"):
                used_web = True
                web_results = perplexity_results["results"]
                
                # Build web context string
                web_parts = []
                for i, r in enumerate(web_results[:3], 1):
                    title = r.get("title", f"Source {i}")
                    url = r.get("url", "")
                    snippet = r.get("snippet", "")
                    web_parts.append(f"🌐 [Web Source {i}: {title}]\nURL: {url}\n{snippet}")
                
                web_context = "\n\n".join(web_parts)
                
                sources["web"] = [
                    {"title": r.get("title", "Web Source"), "url": r.get("url", "")}
                    for r in web_results[:3]
                ]
                
                print(f"[ChatService] Got {len(web_results)} web results from Perplexity")
        
        # Generate response with appropriate mode
        response = await self.rag_chain.generate_response(
            query=content,
            context=context if use_course_context else "",
            chat_history=history,
            web_context=web_context if used_web else None,
            use_general_knowledge=not use_course_context
        )
        
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
        When include_web_search is True, also queries Perplexity for latest web info.
        """
        # Store user message
        await self.chat_repo.add_message(
            session_id=session_id,
            role="user",
            content=content
        )
        
        # Get conversation history
        history = await self.memory.get_history(session_id, limit=10)
        
        # Search for relevant course context (always do this)
        search_results = await self.search_service.hybrid_search(
            query=content,
            course_id=course_id,
            limit=5,
            include_web=False  # Don't use the old web search, we'll use Perplexity directly
        )
        
        # Prepare course context and determine relevance
        context, context_relevance = self._prepare_context_with_relevance(search_results)
        
        # Determine if we should use course context or general knowledge
        use_course_context = context_relevance >= 0.2 and len(search_results.get("course_results", [])) > 0
        
        print(f"[ChatService-Stream] Context relevance: {context_relevance:.3f}, Use course context: {use_course_context}")
        
        # Prepare sources
        sources = {
            "course": [
                {"title": r["material_title"], "type": r["file_type"], "relevance": r["relevance_score"]}
                for r in search_results.get("course_results", [])[:3]
            ]
        }
        
        # If web search is enabled, query Perplexity for latest info
        web_context = ""
        used_web = False
        if include_web_search:
            print(f"[ChatService-Stream] Web search enabled, querying Perplexity...")
            perplexity_results = await self.perplexity.search(query=content, limit=5, recency="week")
            
            if perplexity_results.get("results") and not perplexity_results.get("error"):
                used_web = True
                web_results = perplexity_results["results"]
                
                # Build web context string
                web_parts = []
                for i, r in enumerate(web_results[:3], 1):
                    title = r.get("title", f"Source {i}")
                    url = r.get("url", "")
                    snippet = r.get("snippet", "")
                    web_parts.append(f"🌐 [Web Source {i}: {title}]\nURL: {url}\n{snippet}")
                
                web_context = "\n\n".join(web_parts)
                
                # Add to sources
                sources["web"] = [
                    {"title": r.get("title", "Web Source"), "url": r.get("url", "")}
                    for r in web_results[:3]
                ]
                
                print(f"[ChatService-Stream] Got {len(web_results)} web results from Perplexity")
            elif perplexity_results.get("error"):
                print(f"[ChatService-Stream] Perplexity error: {perplexity_results['error']}")
        
        # Yield sources first
        yield {
            "type": "sources",
            "sources": sources,
            "used_web_search": used_web,
            "used_general_knowledge": not use_course_context
        }
        
        # Stream response with both course context and web context if available
        full_response = ""
        async for chunk in self.rag_chain.generate_response_stream(
            query=content,
            context=context if use_course_context else "",
            chat_history=history,
            web_context=web_context if used_web else None,
            use_general_knowledge=not use_course_context
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
        return self._prepare_context_with_relevance(search_results)[0]
    
    def _prepare_context_with_relevance(self, search_results: Dict) -> tuple[str, float]:
        """Prepare context string and return average relevance score."""
        parts = []
        relevance_scores = []
        
        print(f"[ChatService] Preparing context from search results...")
        print(f"[ChatService] Course results: {len(search_results.get('course_results', []))}")
        print(f"[ChatService] Web results: {len(search_results.get('web_results', []))}")
        
        # Course context - include more results (up to 5) for better coverage
        for i, result in enumerate(search_results.get("course_results", [])[:5], 1):
            content = result.get("content", "")
            title = result.get("material_title", "Course Material")
            score = result.get("relevance_score", 0)
            relevance_scores.append(score)
            parts.append(f"📚 [Course Source {i}: {title}]\n{content}")
            print(f"[ChatService] Added course source: {title} (score: {score:.3f})")
        
        # Web context
        for i, result in enumerate(search_results.get("web_results", [])[:2], 1):
            snippet = result.get("snippet", "")
            title = result.get("title", "Web Source")
            url = result.get("url", "")
            parts.append(f"🌐 [Web Source {i}: {title}]\nURL: {url}\n{snippet}")
        
        context = "\n\n---\n\n".join(parts) if parts else ""
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        
        print(f"[ChatService] Final context length: {len(context)} chars")
        print(f"[ChatService] Average relevance: {avg_relevance:.3f}")
        
        return context, avg_relevance


# Singleton instance
_chat_service = None


def get_chat_service() -> ChatService:
    """Get or create chat service singleton."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
