"""Materials management routes."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from typing import Annotated, Optional
from uuid import UUID

from app.api.dependencies import get_current_user, get_material_service
from app.services.material_service import MaterialService
from app.db.models import Material, MaterialCreate, MaterialResponse, MaterialListResponse

router = APIRouter()


@router.post("/upload", response_model=MaterialResponse)
async def upload_material(
    file: UploadFile = File(...),
    course_id: UUID = Form(...),
    title: str = Form(...),
    category: str = Form(...),  # theory or lab
    week_number: Optional[int] = Form(None),
    tags: Optional[str] = Form(None),  # comma-separated
    programming_language: Optional[str] = Form(None),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: MaterialService = Depends(get_material_service)
):
    """Upload a new course material."""
    try:
        # Parse tags
        tag_list = [t.strip() for t in tags.split(",")] if tags else []
        
        material_data = MaterialCreate(
            course_id=course_id,
            title=title,
            category=category,
            week_number=week_number,
            tags=tag_list,
            programming_language=programming_language,
            uploaded_by=UUID(current_user.id) if current_user else None
        )
        
        result = await service.upload_material(file, material_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/course/{course_id}", response_model=MaterialListResponse)
async def get_course_materials(
    course_id: UUID,
    category: Optional[str] = None,
    week: Optional[int] = None,
    file_type: Optional[str] = None,
    service: MaterialService = Depends(get_material_service)
):
    """Get all materials for a course with optional filters."""
    try:
        materials = await service.get_materials(
            course_id=course_id,
            category=category,
            week=week,
            file_type=file_type
        )
        return MaterialListResponse(materials=materials, total=len(materials))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: UUID,
    service: MaterialService = Depends(get_material_service)
):
    """Get a specific material by ID."""
    try:
        material = await service.get_material_by_id(material_id)
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material not found"
            )
        return material
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{material_id}")
async def delete_material(
    material_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: MaterialService = Depends(get_material_service)
):
    """Delete a material (admin only)."""
    try:
        # Check if user is admin
        user_metadata = current_user.user_metadata or {}
        if user_metadata.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        await service.delete_material(material_id)
        return {"message": "Material deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: UUID,
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    week_number: Optional[int] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: MaterialService = Depends(get_material_service)
):
    """Update material metadata."""
    try:
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        
        result = await service.update_material(
            material_id=material_id,
            title=title,
            category=category,
            week_number=week_number,
            tags=tag_list
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
