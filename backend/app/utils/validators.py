"""Input validation utilities."""
import re
from typing import Optional, List, Dict, Any
from uuid import UUID
from pathlib import Path

from app.config import get_settings


class ValidationError(Exception):
    """Custom validation error."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def validate_uuid(value: str, field_name: str = "id") -> UUID:
    """Validate and parse a UUID string."""
    try:
        return UUID(value)
    except (ValueError, TypeError):
        raise ValidationError(field_name, "Invalid UUID format")


def validate_email(email: str) -> str:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("email", "Invalid email format")
    return email.lower().strip()


def validate_category(category: str) -> str:
    """Validate category value."""
    valid = ["theory", "lab"]
    if category.lower() not in valid:
        raise ValidationError("category", f"Must be one of: {', '.join(valid)}")
    return category.lower()


def validate_file_type(filename: str) -> str:
    """Validate file type is supported."""
    settings = get_settings()
    ext = Path(filename).suffix.lower().lstrip(".")
    
    if ext not in settings.SUPPORTED_FILE_TYPES:
        raise ValidationError(
            "file",
            f"Unsupported file type: {ext}. Supported: {', '.join(settings.SUPPORTED_FILE_TYPES)}"
        )
    
    return ext


def validate_file_size(size: int, filename: str) -> int:
    """Validate file size is within limits."""
    settings = get_settings()
    if size > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise ValidationError(
            "file",
            f"File too large. Maximum size is {max_mb:.0f}MB"
        )
    return size


def validate_programming_language(language: str) -> str:
    """Validate programming language is supported."""
    supported = ["python", "javascript", "java", "cpp", "c", "typescript", "go", "rust"]
    lang = language.lower().strip()
    
    if lang not in supported:
        raise ValidationError(
            "language",
            f"Unsupported language: {lang}. Supported: {', '.join(supported)}"
        )
    
    return lang


def validate_generation_type(gen_type: str) -> str:
    """Validate generation type."""
    valid_theory = ["notes", "summary", "study_guide"]
    valid_code = ["example", "solution", "explanation"]
    valid = valid_theory + valid_code
    
    if gen_type.lower() not in valid:
        raise ValidationError(
            "type",
            f"Invalid generation type. Must be one of: {', '.join(valid)}"
        )
    
    return gen_type.lower()


def validate_query(query: str, min_length: int = 3, max_length: int = 500) -> str:
    """Validate search/generation query."""
    query = query.strip()
    
    if len(query) < min_length:
        raise ValidationError("query", f"Query must be at least {min_length} characters")
    
    if len(query) > max_length:
        raise ValidationError("query", f"Query must be at most {max_length} characters")
    
    return query


def validate_pagination(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    max_limit: int = 100
) -> Dict[str, int]:
    """Validate pagination parameters."""
    result = {
        "limit": min(limit or 20, max_limit),
        "offset": max(offset or 0, 0)
    }
    
    if result["limit"] < 1:
        raise ValidationError("limit", "Must be at least 1")
    
    return result


def validate_tags(tags: Optional[List[str]]) -> List[str]:
    """Validate and clean tags list."""
    if not tags:
        return []
    
    cleaned = []
    for tag in tags:
        tag = tag.strip().lower()
        if tag and len(tag) <= 50:
            cleaned.append(tag)
    
    return list(set(cleaned))[:20]  # Max 20 unique tags


def validate_week_number(week: Optional[int]) -> Optional[int]:
    """Validate week number."""
    if week is None:
        return None
    
    if week < 1 or week > 52:
        raise ValidationError("week_number", "Must be between 1 and 52")
    
    return week


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove path separators and dangerous characters
    filename = Path(filename).name
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    
    # Limit length
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    name = name[:100]
    
    return f"{name}.{ext}" if ext else name


def validate_content_length(
    content: str,
    min_length: int = 10,
    max_length: int = 100000
) -> str:
    """Validate generated content length."""
    if len(content) < min_length:
        raise ValidationError("content", f"Content too short (min {min_length} chars)")
    
    if len(content) > max_length:
        raise ValidationError("content", f"Content too long (max {max_length} chars)")
    
    return content
