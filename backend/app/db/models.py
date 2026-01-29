"""Pydantic models for database and API."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


# Enums
class Category(str, Enum):
    THEORY = "theory"
    LAB = "lab"


class ValidationStatus(str, Enum):
    VALIDATED = "validated"
    WARNING = "warning"
    FAILED = "failed"


class Role(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"


# Course Models
class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Material Models
class MaterialBase(BaseModel):
    title: str
    category: Category
    week_number: Optional[int] = None
    tags: List[str] = []
    programming_language: Optional[str] = None


class MaterialCreate(MaterialBase):
    course_id: UUID
    uploaded_by: Optional[UUID] = None


class Material(MaterialBase):
    id: UUID
    course_id: UUID
    file_path: str
    file_type: str
    file_size: int
    uploaded_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaterialResponse(BaseModel):
    id: UUID
    title: str
    category: str
    file_type: str
    file_size: int
    week_number: Optional[int]
    tags: List[str]
    programming_language: Optional[str]
    created_at: datetime
    download_url: Optional[str] = None


class MaterialListResponse(BaseModel):
    materials: List[MaterialResponse]
    total: int


# Search Models
class SearchResult(BaseModel):
    id: UUID
    content: str
    material_id: UUID
    material_title: str
    file_type: str
    category: str
    relevance_score: float
    chunk_index: int
    metadata: Dict[str, Any] = {}


class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    relevance_score: float
    source_domain: str
    published_date: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    course_results: List[SearchResult] = []
    web_results: List[WebSearchResult] = []
    took_ms: int
    used_web_search: bool = False
    average_relevance: float = 0.0


# Generation Models
class GeneratedContent(BaseModel):
    id: UUID
    course_id: UUID
    user_id: Optional[UUID]
    type: str  # theory or code
    topic: str
    content: str
    programming_language: Optional[str]
    validation_status: Optional[ValidationStatus]
    validation_score: Optional[float]
    validation_details: Dict[str, Any] = {}
    sources: Dict[str, Any] = {}
    used_web_search: bool = False
    web_sources: List[Dict[str, Any]] = []
    source_mix_ratio: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class GenerationResponse(BaseModel):
    id: UUID
    status: str  # processing, completed, failed
    type: str
    topic: str
    content: Optional[str] = None
    programming_language: Optional[str] = None
    validation_status: Optional[str] = None
    validation_score: Optional[float] = None
    sources: Dict[str, Any] = {}
    used_web_search: bool = False


# Chat Models
class ChatSessionBase(BaseModel):
    course_id: UUID
    title: Optional[str] = None


class ChatSession(ChatSessionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    content: str
    role: str  # user or assistant


class ChatMessage(ChatMessageBase):
    id: UUID
    session_id: UUID
    sources: List[Dict[str, Any]] = []
    used_web_search: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    message: ChatMessage
    session_id: UUID
    sources: Dict[str, List[Dict]] = {}


# Validation Models
class ValidationIssue(BaseModel):
    type: str  # error, warning, info
    message: str
    line: Optional[int] = None
    suggestion: Optional[str] = None


class CodeValidationResult(BaseModel):
    status: ValidationStatus
    score: float
    syntax_valid: bool
    lint_issues: List[ValidationIssue]
    execution_result: Optional[Dict[str, Any]] = None
    suggestions: List[str]


class ContentValidationResult(BaseModel):
    status: ValidationStatus
    score: float
    grounding_score: float
    structure_score: float
    relevance_score: float
    issues: List[ValidationIssue]
    web_sources_valid: bool
    suggestions: List[str]


# User Models
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    role: Role = Role.STUDENT


class User(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
