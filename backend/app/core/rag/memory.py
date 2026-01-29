"""Conversation memory management."""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.db.supabase_client import get_supabase_client


class ConversationMemory:
    """Manage conversation history for chat sessions."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def get_history(
        self,
        session_id: UUID,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a session.
        
        Returns list of {"role": "user"|"assistant", "content": "..."}
        """
        result = self.supabase.table("chat_messages")\
            .select("role, content")\
            .eq("session_id", str(session_id))\
            .order("created_at", desc=False)\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
    
    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        sources: Optional[List[Dict]] = None,
        used_web_search: bool = False
    ) -> UUID:
        """Add a message to conversation history."""
        result = self.supabase.table("chat_messages").insert({
            "session_id": str(session_id),
            "role": role,
            "content": content,
            "sources": sources or [],
            "used_web_search": used_web_search,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return UUID(result.data[0]["id"])
    
    async def clear_history(self, session_id: UUID) -> None:
        """Clear conversation history for a session."""
        self.supabase.table("chat_messages")\
            .delete()\
            .eq("session_id", str(session_id))\
            .execute()
    
    async def summarize_if_needed(
        self,
        session_id: UUID,
        max_messages: int = 20
    ) -> Optional[str]:
        """
        Check if conversation needs summarization.
        If too long, summarize older messages.
        """
        history = await self.get_history(session_id, limit=100)
        
        if len(history) <= max_messages:
            return None
        
        # Get older messages to summarize
        to_summarize = history[:-max_messages]
        
        # Create summary (simplified - could use LLM for better summary)
        summary_parts = []
        for msg in to_summarize:
            role = "User" if msg["role"] == "user" else "Assistant"
            summary_parts.append(f"{role}: {msg['content'][:100]}...")
        
        return "Previous conversation summary:\n" + "\n".join(summary_parts[-5:])


# Singleton instance
_memory = None


def get_memory() -> ConversationMemory:
    """Get or create memory singleton."""
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
    return _memory
