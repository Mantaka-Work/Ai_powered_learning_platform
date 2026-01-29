"""Base repository with common CRUD operations."""
from typing import TypeVar, Generic, Optional, List, Dict, Any
from uuid import UUID

from app.db.supabase_client import get_supabase_client

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository with common database operations."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.supabase = get_supabase_client()
    
    async def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        """Get a record by ID."""
        result = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("id", str(id))\
            .single()\
            .execute()
        
        return result.data if result.data else None
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all records with pagination."""
        result = self.supabase.table(self.table_name)\
            .select("*")\
            .order(order_by, desc=not ascending)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        return result.data if result.data else []
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        result = self.supabase.table(self.table_name)\
            .insert(data)\
            .execute()
        
        return result.data[0] if result.data else None
    
    async def update(self, id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record."""
        result = self.supabase.table(self.table_name)\
            .update(data)\
            .eq("id", str(id))\
            .execute()
        
        return result.data[0] if result.data else None
    
    async def delete(self, id: UUID) -> bool:
        """Delete a record."""
        result = self.supabase.table(self.table_name)\
            .delete()\
            .eq("id", str(id))\
            .execute()
        
        return bool(result.data)
    
    async def find_by(
        self,
        filters: Dict[str, Any],
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find records by filter criteria."""
        query = self.supabase.table(self.table_name).select("*")
        
        for key, value in filters.items():
            query = query.eq(key, value)
        
        result = query.limit(limit).execute()
        
        return result.data if result.data else []
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records."""
        query = self.supabase.table(self.table_name).select("*", count="exact")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        result = query.execute()
        
        return result.count if result.count else 0
