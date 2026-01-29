"""Content validation routes."""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

router = APIRouter()


class CodeValidationRequest(BaseModel):
    code: str
    language: str  # python, javascript, java, cpp, etc.
    run_tests: bool = False  # Attempt sandboxed execution


class ContentValidationRequest(BaseModel):
    content: str
    topic: str
    course_id: UUID
    check_grounding: bool = True  # Check if grounded in course materials
    check_web_sources: bool = True  # Validate web source credibility


class ValidationIssue(BaseModel):
    type: str  # error, warning, info
    message: str
    line: Optional[int] = None
    suggestion: Optional[str] = None


class CodeValidationResponse(BaseModel):
    status: str  # validated, warning, failed
    score: float  # 0-100
    syntax_valid: bool
    lint_issues: List[ValidationIssue]
    execution_result: Optional[dict] = None
    suggestions: List[str]


class ContentValidationResponse(BaseModel):
    status: str  # validated, warning, failed
    score: float  # 0-100
    grounding_score: float  # How well grounded in course materials
    structure_score: float  # Formatting quality
    relevance_score: float  # Topic relevance
    issues: List[ValidationIssue]
    web_sources_valid: bool
    suggestions: List[str]


@router.post("/code", response_model=CodeValidationResponse)
async def validate_code(request: CodeValidationRequest):
    """
    Validate generated code.
    
    Checks:
    - Syntax correctness (compilation/parsing)
    - Linting (code standards)
    - Static analysis (potential bugs)
    - Optional: Sandboxed execution
    """
    from app.core.validation.code_validator import CodeValidator
    
    try:
        validator = CodeValidator()
        result = await validator.validate(
            code=request.code,
            language=request.language,
            run_tests=request.run_tests
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/content", response_model=ContentValidationResponse)
async def validate_content(request: ContentValidationRequest):
    """
    Validate generated theory content.
    
    Checks:
    - Grounding in course materials
    - Structure and formatting
    - Topic relevance
    - Web source credibility (if applicable)
    """
    from app.core.validation.content_validator import ContentValidator
    
    try:
        validator = ContentValidator()
        result = await validator.validate(
            content=request.content,
            topic=request.topic,
            course_id=request.course_id,
            check_grounding=request.check_grounding,
            check_web_sources=request.check_web_sources
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/web-sources")
async def validate_web_sources(sources: List[dict]):
    """
    Validate credibility of web sources.
    
    Checks:
    - Domain authority
    - Recency
    - Content relevance
    """
    from app.core.validation.content_validator import ContentValidator
    
    try:
        validator = ContentValidator()
        results = []
        for source in sources:
            result = await validator.validate_web_source(source)
            results.append(result)
        return {"sources": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
