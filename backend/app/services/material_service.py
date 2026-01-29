"""Material service for file upload and management."""
import hashlib
from typing import Optional, List, Dict, Any, BinaryIO
from uuid import UUID, uuid4
from pathlib import Path

from app.db.supabase_client import get_supabase_client
from app.db.repositories.material_repo import get_material_repository
from app.db.repositories.vector_repo import get_vector_repository
from app.core.document_processing.parsers import DocumentParser, get_document_parser
from app.core.document_processing.chunking import ChunkingStrategy, get_chunking_strategy
from app.core.document_processing.metadata_extractor import MetadataExtractor, get_metadata_extractor
from app.core.rag.embeddings import EmbeddingService, get_embedding_service
from app.config import settings


class MaterialService:
    """Service for handling material uploads and management."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.material_repo = get_material_repository()
        self.vector_repo = get_vector_repository()
        self.parser = get_document_parser()
        self.chunker = get_chunking_strategy()
        self.metadata_extractor = get_metadata_extractor()
        self.embedding_service = get_embedding_service()
        self.storage_bucket = "course-materials"
    
    async def upload_material(
        self,
        course_id: UUID,
        file: BinaryIO,
        filename: str,
        file_size: int,
        category: str,
        title: Optional[str] = None,
        week_number: Optional[int] = None,
        tags: Optional[List[str]] = None,
        uploaded_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Upload a material file, parse it, chunk it, and embed it.
        
        Returns:
            Material record with processing status
        """
        # Validate file size
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE} bytes")
        
        # Detect file type and extract metadata
        file_type = Path(filename).suffix.lower().lstrip(".")
        
        if file_type not in settings.SUPPORTED_FILE_TYPES:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Read file content
        content = file.read()
        file.seek(0)  # Reset for potential re-read
        
        # Generate unique file path
        file_hash = hashlib.md5(content).hexdigest()[:8]
        storage_path = f"{course_id}/{category}/{file_hash}_{filename}"
        
        # Upload to Supabase Storage
        storage_result = self.supabase.storage\
            .from_(self.storage_bucket)\
            .upload(storage_path, content)
        
        if hasattr(storage_result, 'error') and storage_result.error:
            raise Exception(f"Storage upload failed: {storage_result.error}")
        
        # Auto-extract title if not provided
        if not title:
            title = self.metadata_extractor.extract_title(filename, content.decode('utf-8', errors='ignore')[:1000])
        
        # Auto-detect week number if not provided
        if week_number is None:
            week_number = self.metadata_extractor.extract_week_number(filename, title)
        
        # Detect programming language for code files
        programming_language = None
        if file_type in ['py', 'js', 'java', 'cpp', 'c', 'ts']:
            programming_language = self.metadata_extractor.detect_programming_language(filename, file_type)
        
        # Create material record
        material = await self.material_repo.create_material(
            course_id=course_id,
            title=title,
            file_path=storage_path,
            file_type=file_type,
            file_size=file_size,
            category=category,
            week_number=week_number,
            tags=tags,
            programming_language=programming_language,
            uploaded_by=uploaded_by
        )
        
        # Parse document content
        try:
            parsed_content = await self.parser.parse(content, file_type, filename)
        except Exception as e:
            # Log but don't fail - material is still uploaded
            print(f"Warning: Failed to parse {filename}: {e}")
            parsed_content = content.decode('utf-8', errors='ignore')
        
        # Chunk the content
        chunks = await self.chunker.chunk(
            content=parsed_content,
            file_type=file_type,
            metadata={"material_id": str(material["id"]), "title": title}
        )
        
        # Generate embeddings and store
        if chunks:
            embeddings = await self.embedding_service.embed_batch([c["content"] for c in chunks])
            
            embedding_chunks = [
                {
                    "content": chunk["content"],
                    "embedding": embedding,
                    "chunk_index": i,
                    "metadata": chunk.get("metadata", {})
                }
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
            ]
            
            await self.vector_repo.store_embeddings_batch(
                material_id=UUID(material["id"]),
                chunks=embedding_chunks
            )
        
        return {
            **material,
            "chunks_created": len(chunks),
            "embeddings_stored": len(chunks)
        }
    
    async def get_material(
        self,
        material_id: UUID,
        include_download_url: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get a material by ID with optional signed download URL."""
        material = await self.material_repo.get_by_id(material_id)
        
        if not material:
            return None
        
        if include_download_url:
            # Generate signed URL (valid for 1 hour)
            url_result = self.supabase.storage\
                .from_(self.storage_bucket)\
                .create_signed_url(material["file_path"], 3600)
            
            material["download_url"] = url_result.get("signedURL")
        
        return material
    
    async def get_course_materials(
        self,
        course_id: UUID,
        category: Optional[str] = None,
        week: Optional[int] = None,
        file_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get materials for a course with optional filters."""
        materials = await self.material_repo.get_by_course(
            course_id=course_id,
            category=category,
            week=week,
            file_type=file_type,
            limit=limit
        )
        
        return {
            "materials": materials,
            "total": len(materials),
            "filters": {
                "category": category,
                "week": week,
                "file_type": file_type
            }
        }
    
    async def delete_material(
        self,
        material_id: UUID,
        course_id: UUID
    ) -> bool:
        """Delete a material and its embeddings."""
        material = await self.material_repo.get_by_id(material_id)
        
        if not material or material["course_id"] != str(course_id):
            return False
        
        # Delete from storage
        self.supabase.storage\
            .from_(self.storage_bucket)\
            .remove([material["file_path"]])
        
        # Delete embeddings
        await self.vector_repo.delete_by_material(material_id)
        
        # Delete material record
        return await self.material_repo.delete(material_id)
    
    async def update_material_metadata(
        self,
        material_id: UUID,
        title: Optional[str] = None,
        category: Optional[str] = None,
        week_number: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update material metadata."""
        return await self.material_repo.update_metadata(
            material_id=material_id,
            title=title,
            category=category,
            week_number=week_number,
            tags=tags
        )
    
    async def get_available_filters(self, course_id: UUID) -> Dict[str, List]:
        """Get available filter options for a course."""
        file_types = await self.material_repo.get_file_types(course_id)
        weeks = await self.material_repo.get_weeks(course_id)
        
        return {
            "categories": ["theory", "lab"],
            "file_types": file_types,
            "weeks": weeks
        }


# Singleton instance
_material_service = None


def get_material_service() -> MaterialService:
    """Get or create material service singleton."""
    global _material_service
    if _material_service is None:
        _material_service = MaterialService()
    return _material_service
