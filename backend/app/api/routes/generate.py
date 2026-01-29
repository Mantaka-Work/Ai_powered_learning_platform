"""Content generation routes - theory and code generation."""
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.api.dependencies import get_optional_user, get_generation_service
from app.services.generation_service import GenerationService
from app.db.models import GeneratedContent, GenerationResponse

router = APIRouter()


class TheoryGenerationRequest(BaseModel):
    topic: str
    course_id: UUID
    type: str = "notes"  # notes, summary, study_guide
    use_web: bool = True  # Include web search for additional context
    max_length: Optional[int] = None


class CodeGenerationRequest(BaseModel):
    topic: str
    course_id: UUID
    language: str  # python, javascript, java, cpp, etc.
    type: str = "example"  # example, solution, explanation
    use_web: bool = True


@router.post("/theory", response_model=GenerationResponse)
async def generate_theory(
    request: TheoryGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_optional_user),
    service: GenerationService = Depends(get_generation_service)
):
    """
    Generate theory learning materials (notes, summaries, study guides).
    
    Content is grounded in course materials with optional web augmentation.
    Returns generation ID for status tracking (async generation).
    """
    try:
        result = await service.generate_theory(
            topic=request.topic,
            course_id=request.course_id,
            gen_type=request.type,
            use_web=request.use_web,
            user_id=UUID(current_user.id) if current_user else None
        )
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.post("/code", response_model=GenerationResponse)
async def generate_code(
    request: CodeGenerationRequest,
    current_user = Depends(get_optional_user),
    service: GenerationService = Depends(get_generation_service)
):
    """
    Generate code examples with syntax validation.
    
    Code is relevant to course materials with optional web augmentation
    for latest syntax/best practices.
    """
    try:
        result = await service.generate_code(
            topic=request.topic,
            course_id=request.course_id,
            language=request.language,
            code_type=request.type,
            use_web=request.use_web,
            user_id=UUID(current_user.id) if current_user else None
        )
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.get("/{generation_id}/status")
async def get_generation_status(
    generation_id: UUID,
    service: GenerationService = Depends(get_generation_service)
):
    """
    Get status of a generation request.
    
    Returns:
    - status: processing, completed, failed
    - content: generated content (if completed)
    - validation_status: validated, warning, failed
    - sources: course and web sources used
    """
    try:
        result = await service.get_generation_status(generation_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generation not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{generation_id}/regenerate", response_model=GenerationResponse)
async def regenerate_content(
    generation_id: UUID,
    current_user = Depends(get_optional_user),
    service: GenerationService = Depends(get_generation_service)
):
    """Regenerate content with same parameters."""
    try:
        result = await service.regenerate(generation_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/history/{course_id}")
async def get_generation_history(
    course_id: UUID,
    limit: int = 20,
    current_user = Depends(get_optional_user),
    service: GenerationService = Depends(get_generation_service)
):
    """Get generation history for a course."""
    try:
        history = await service.get_history(
            course_id=course_id,
            user_id=UUID(current_user.id) if current_user else None,
            limit=limit
        )
        return {"generations": history}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
