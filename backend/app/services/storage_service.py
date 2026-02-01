"""Storage service for Supabase file operations."""
from typing import Optional, List, BinaryIO
from uuid import UUID
import mimetypes

from app.db.supabase_client import get_supabase_client
from app.config import get_settings


class StorageService:
    """Service for file storage operations using Supabase Storage."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.materials_bucket = "course-materials"
        self.exports_bucket = "exports"
    
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_content: bytes,
        content_type: Optional[str] = None
    ) -> dict:
        """
        Upload a file to storage.
        
        Args:
            bucket: Storage bucket name
            path: File path within bucket
            file_content: File content as bytes
            content_type: MIME type (auto-detected if not provided)
        
        Returns:
            Upload result with path
        """
        if content_type is None:
            content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
        
        result = self.supabase.storage\
            .from_(bucket)\
            .upload(
                path,
                file_content,
                {"content-type": content_type}
            )
        
        return {"path": path, "bucket": bucket}
    
    async def download_file(
        self,
        bucket: str,
        path: str
    ) -> bytes:
        """
        Download a file from storage.
        
        Args:
            bucket: Storage bucket name
            path: File path within bucket
        
        Returns:
            File content as bytes
        """
        result = self.supabase.storage\
            .from_(bucket)\
            .download(path)
        
        return result
    
    async def get_signed_url(
        self,
        bucket: str,
        path: str,
        expires_in: int = 3600
    ) -> str:
        """
        Get a signed URL for file access.
        
        Args:
            bucket: Storage bucket name
            path: File path within bucket
            expires_in: URL expiration time in seconds (default 1 hour)
        
        Returns:
            Signed URL string
        """
        result = self.supabase.storage\
            .from_(bucket)\
            .create_signed_url(path, expires_in)
        
        return result.get("signedURL", "")
    
    async def delete_file(
        self,
        bucket: str,
        path: str
    ) -> bool:
        """
        Delete a file from storage.
        
        Args:
            bucket: Storage bucket name
            path: File path within bucket
        
        Returns:
            True if deleted successfully
        """
        result = self.supabase.storage\
            .from_(bucket)\
            .remove([path])
        
        return bool(result)
    
    async def delete_files(
        self,
        bucket: str,
        paths: List[str]
    ) -> bool:
        """Delete multiple files."""
        result = self.supabase.storage\
            .from_(bucket)\
            .remove(paths)
        
        return bool(result)
    
    async def list_files(
        self,
        bucket: str,
        folder: str = "",
        limit: int = 100
    ) -> List[dict]:
        """
        List files in a folder.
        
        Args:
            bucket: Storage bucket name
            folder: Folder path (empty for root)
            limit: Max files to return
        
        Returns:
            List of file objects with name, id, metadata
        """
        result = self.supabase.storage\
            .from_(bucket)\
            .list(folder, {"limit": limit})
        
        return result or []
    
    async def move_file(
        self,
        bucket: str,
        from_path: str,
        to_path: str
    ) -> dict:
        """
        Move/rename a file within a bucket.
        
        Args:
            bucket: Storage bucket name
            from_path: Current file path
            to_path: New file path
        
        Returns:
            Move result
        """
        result = self.supabase.storage\
            .from_(bucket)\
            .move(from_path, to_path)
        
        return result
    
    async def get_public_url(
        self,
        bucket: str,
        path: str
    ) -> str:
        """
        Get public URL for a file (bucket must be public).
        
        Args:
            bucket: Storage bucket name
            path: File path within bucket
        
        Returns:
            Public URL string
        """
        result = self.supabase.storage\
            .from_(bucket)\
            .get_public_url(path)
        
        return result
    
    # Convenience methods for specific buckets
    
    async def upload_material(
        self,
        course_id: UUID,
        category: str,
        filename: str,
        content: bytes
    ) -> dict:
        """Upload a course material file."""
        path = f"{course_id}/{category}/{filename}"
        return await self.upload_file(self.materials_bucket, path, content)
    
    async def get_material_url(
        self,
        course_id: UUID,
        category: str,
        filename: str,
        expires_in: int = 3600
    ) -> str:
        """Get signed URL for a material file."""
        path = f"{course_id}/{category}/{filename}"
        return await self.get_signed_url(self.materials_bucket, path, expires_in)
    
    async def upload_export(
        self,
        user_id: UUID,
        filename: str,
        content: bytes
    ) -> dict:
        """Upload an export file (generated content, etc.)."""
        path = f"{user_id}/{filename}"
        return await self.upload_file(self.exports_bucket, path, content)


# Singleton instance
_storage_service = None


def get_storage_service() -> StorageService:
    """Get or create storage service singleton."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
