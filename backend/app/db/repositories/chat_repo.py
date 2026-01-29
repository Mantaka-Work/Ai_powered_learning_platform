"""Chat repository for session and message operations."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.db.repositories.base_repo import BaseRepository


class ChatRepository(BaseRepository):
    """Repository for chat sessions and messages."""
    
    def __init__(self):
        super().__init__("chat_sessions")
        self.messages_table = "chat_messages"
    
    async def create_session(
        self,
        user_id: UUID,
        course_id: UUID,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new chat session."""
        data = {
            "user_id": str(user_id),
            "course_id": str(course_id),
            "title": title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return await self.create(data)
    
    async def get_user_sessions(
        self,
        user_id: UUID,
        course_id: Optional[UUID] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get chat sessions for a user."""
        query = self.supabase.table(self.table_name)\
            .select("*, chat_messages(count)")\
            .eq("user_id", str(user_id))
        
        if course_id:
            query = query.eq("course_id", str(course_id))
        
        result = query.order("updated_at", desc=True).limit(limit).execute()
        
        sessions = result.data if result.data else []
        
        # Add message count
        for session in sessions:
            messages = session.get("chat_messages", [])
            session["message_count"] = messages[0]["count"] if messages else 0
            del session["chat_messages"]
        
        return sessions
    
    async def get_session_with_messages(
        self,
        session_id: UUID,
        message_limit: int = 50
    ) -> Optional[Dict[str, Any]]:
        """Get a session with its messages."""
        # Get session
        session = await self.get_by_id(session_id)
        if not session:
            return None
        
        # Get messages
        result = self.supabase.table(self.messages_table)\
            .select("*")\
            .eq("session_id", str(session_id))\
            .order("created_at", desc=False)\
            .limit(message_limit)\
            .execute()
        
        session["messages"] = result.data if result.data else []
        session["message_count"] = len(session["messages"])
        
        return session
    
    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        sources: Optional[List[Dict]] = None,
        used_web_search: bool = False
    ) -> Dict[str, Any]:
        """Add a message to a session."""
        data = {
            "session_id": str(session_id),
            "role": role,
            "content": content,
            "sources": sources or [],
            "used_web_search": used_web_search,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = self.supabase.table(self.messages_table).insert(data).execute()
        
        # Update session timestamp
        await self.update(session_id, {"updated_at": datetime.utcnow().isoformat()})
        
        return result.data[0] if result.data else None
    
    async def get_messages(
        self,
        session_id: UUID,
        limit: int = 50,
        before_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get messages for a session."""
        query = self.supabase.table(self.messages_table)\
            .select("*")\
            .eq("session_id", str(session_id))
        
        if before_id:
            # Get messages before a specific ID (for pagination)
            msg = await self._get_message_by_id(before_id)
            if msg:
                query = query.lt("created_at", msg["created_at"])
        
        result = query.order("created_at", desc=False).limit(limit).execute()
        
        return result.data if result.data else []
    
    async def _get_message_by_id(self, message_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a single message by ID."""
        result = self.supabase.table(self.messages_table)\
            .select("*")\
            .eq("id", str(message_id))\
            .single()\
            .execute()
        
        return result.data if result.data else None
    
    async def delete_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Delete a session and its messages (must be owner)."""
        # Verify ownership
        session = await self.get_by_id(session_id)
        if not session or session["user_id"] != str(user_id):
            return False
        
        # Delete messages first (cascade should handle this, but being explicit)
        self.supabase.table(self.messages_table)\
            .delete()\
            .eq("session_id", str(session_id))\
            .execute()
        
        # Delete session
        return await self.delete(session_id)
    
    async def update_session_title(
        self,
        session_id: UUID,
        title: str
    ) -> Dict[str, Any]:
        """Update session title."""
        return await self.update(session_id, {
            "title": title,
            "updated_at": datetime.utcnow().isoformat()
        })


# Singleton instance
_chat_repo = None


def get_chat_repository() -> ChatRepository:
    """Get or create chat repository singleton."""
    global _chat_repo
    if _chat_repo is None:
        _chat_repo = ChatRepository()
    return _chat_repo
