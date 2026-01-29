"""Generated content repository."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.db.repositories.base_repo import BaseRepository


class GenerationRepository(BaseRepository):
    """Repository for generated content."""
    
    def __init__(self):
        super().__init__("generated_content")
    
    async def create_generation(
        self,
        course_id: UUID,
        user_id: Optional[UUID],
        gen_type: str,
        topic: str,
        content: str,
        programming_language: Optional[str] = None,
        validation_status: Optional[str] = None,
        validation_score: Optional[float] = None,
        validation_details: Optional[Dict] = None,
        sources: Optional[Dict] = None,
        used_web_search: bool = False,
        web_sources: Optional[List[Dict]] = None,
        source_mix_ratio: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create a new generated content record."""
        data = {
            "course_id": str(course_id),
            "user_id": str(user_id) if user_id else None,
            "type": gen_type,
            "topic": topic,
            "content": content,
            "programming_language": programming_language,
            "validation_status": validation_status,
            "validation_score": validation_score,
            "validation_details": validation_details or {},
            "sources": sources or {},
            "used_web_search": used_web_search,
            "web_sources": web_sources or [],
            "source_mix_ratio": source_mix_ratio,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return await self.create(data)
    
    async def get_by_course(
        self,
        course_id: UUID,
        user_id: Optional[UUID] = None,
        gen_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get generated content for a course."""
        query = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("course_id", str(course_id))
        
        if user_id:
            query = query.eq("user_id", str(user_id))
        
        if gen_type:
            query = query.eq("type", gen_type)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        
        return result.data if result.data else []
    
    async def update_validation(
        self,
        generation_id: UUID,
        validation_status: str,
        validation_score: float,
        validation_details: Dict
    ) -> Dict[str, Any]:
        """Update validation results for generated content."""
        return await self.update(generation_id, {
            "validation_status": validation_status,
            "validation_score": validation_score,
            "validation_details": validation_details
        })
    
    async def get_recent_topics(
        self,
        course_id: UUID,
        limit: int = 10
    ) -> List[str]:
        """Get recently generated topics for a course."""
        result = self.supabase.table(self.table_name)\
            .select("topic")\
            .eq("course_id", str(course_id))\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        if result.data:
            return list(dict.fromkeys(r["topic"] for r in result.data))  # Unique, ordered
        return []


# Singleton instance
_generation_repo = None


def get_generation_repository() -> GenerationRepository:
    """Get or create generation repository singleton."""
    global _generation_repo
    if _generation_repo is None:
        _generation_repo = GenerationRepository()
    return _generation_repo
