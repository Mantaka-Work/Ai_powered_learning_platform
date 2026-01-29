"""Material repository for CRUD operations."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.db.repositories.base_repo import BaseRepository


class MaterialRepository(BaseRepository):
    """Repository for course materials."""
    
    def __init__(self):
        super().__init__("materials")
    
    async def get_by_course(
        self,
        course_id: UUID,
        category: Optional[str] = None,
        week: Optional[int] = None,
        file_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get materials for a course with optional filters."""
        query = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("course_id", str(course_id))
        
        if category:
            query = query.eq("category", category)
        
        if week:
            query = query.eq("week_number", week)
        
        if file_type:
            query = query.eq("file_type", file_type)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        
        return result.data if result.data else []
    
    async def create_material(
        self,
        course_id: UUID,
        title: str,
        file_path: str,
        file_type: str,
        file_size: int,
        category: str,
        week_number: Optional[int] = None,
        tags: Optional[List[str]] = None,
        programming_language: Optional[str] = None,
        uploaded_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new material record."""
        data = {
            "course_id": str(course_id),
            "title": title,
            "file_path": file_path,
            "file_type": file_type,
            "file_size": file_size,
            "category": category,
            "week_number": week_number,
            "tags": tags or [],
            "programming_language": programming_language,
            "uploaded_by": str(uploaded_by) if uploaded_by else None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return await self.create(data)
    
    async def update_metadata(
        self,
        material_id: UUID,
        title: Optional[str] = None,
        category: Optional[str] = None,
        week_number: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update material metadata."""
        data = {"updated_at": datetime.utcnow().isoformat()}
        
        if title is not None:
            data["title"] = title
        if category is not None:
            data["category"] = category
        if week_number is not None:
            data["week_number"] = week_number
        if tags is not None:
            data["tags"] = tags
        
        return await self.update(material_id, data)
    
    async def get_file_types(self, course_id: UUID) -> List[str]:
        """Get unique file types for a course."""
        result = self.supabase.table(self.table_name)\
            .select("file_type")\
            .eq("course_id", str(course_id))\
            .execute()
        
        if result.data:
            return list(set(r["file_type"] for r in result.data))
        return []
    
    async def get_weeks(self, course_id: UUID) -> List[int]:
        """Get unique week numbers for a course."""
        result = self.supabase.table(self.table_name)\
            .select("week_number")\
            .eq("course_id", str(course_id))\
            .not_.is_("week_number", "null")\
            .execute()
        
        if result.data:
            return sorted(set(r["week_number"] for r in result.data if r["week_number"]))
        return []
    
    async def search_by_title(
        self,
        course_id: UUID,
        search_term: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search materials by title."""
        result = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("course_id", str(course_id))\
            .ilike("title", f"%{search_term}%")\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []


# Singleton instance
_material_repo = None


def get_material_repository() -> MaterialRepository:
    """Get or create material repository singleton."""
    global _material_repo
    if _material_repo is None:
        _material_repo = MaterialRepository()
    return _material_repo
