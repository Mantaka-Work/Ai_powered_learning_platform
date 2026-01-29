"""Helper utilities for the application."""
import hashlib
import re
from typing import Optional, List, Dict, Any, TypeVar
from datetime import datetime
import json

T = TypeVar("T")


def generate_hash(content: str, length: int = 16) -> str:
    """Generate a hash from content."""
    return hashlib.sha256(content.encode()).hexdigest()[:length]


def generate_query_hash(query: str) -> str:
    """Generate a hash for caching search queries."""
    normalized = query.lower().strip()
    return hashlib.md5(normalized.encode()).hexdigest()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters."""
    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:\'"()\-]', '', text)
    return text.strip()


def extract_code_blocks(content: str) -> List[Dict[str, str]]:
    """Extract code blocks from markdown content."""
    pattern = r'```(\w*)\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    return [
        {"language": lang or "text", "code": code.strip()}
        for lang, code in matches
    ]


def format_sources(
    course_sources: List[Dict],
    web_sources: List[Dict]
) -> Dict[str, Any]:
    """Format sources for response."""
    return {
        "course": [
            {
                "type": "📚 Course Material",
                "title": s.get("title", "Unknown"),
                "relevance": round(s.get("relevance", 0), 2)
            }
            for s in course_sources
        ],
        "web": [
            {
                "type": "🌐 Web Source",
                "title": s.get("title", "Unknown"),
                "url": s.get("url", ""),
                "domain": s.get("domain", "")
            }
            for s in web_sources
        ]
    }


def calculate_source_ratio(
    course_count: int,
    web_count: int
) -> float:
    """Calculate the ratio of course sources to total sources."""
    total = course_count + web_count
    if total == 0:
        return 1.0
    return round(course_count / total, 2)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime to ISO string."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp string."""
    # Handle Z suffix
    ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely parse JSON with default fallback."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks of specified size."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries, later ones override earlier."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def extract_week_from_string(text: str) -> Optional[int]:
    """Extract week number from a string like 'Week 5' or 'w5'."""
    patterns = [
        r'week\s*(\d+)',
        r'w(\d+)',
        r'lecture\s*(\d+)',
        r'lec\s*(\d+)',
    ]
    
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            week = int(match.group(1))
            if 1 <= week <= 52:
                return week
    
    return None


def detect_language_from_extension(ext: str) -> str:
    """Detect programming language from file extension."""
    mapping = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'go': 'go',
        'rs': 'rust',
        'rb': 'ruby',
        'php': 'php',
        'swift': 'swift',
        'kt': 'kotlin',
        'cs': 'csharp',
    }
    return mapping.get(ext.lower(), 'text')


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_validation_emoji(status: str) -> str:
    """Get emoji for validation status."""
    mapping = {
        "validated": "✅",
        "warning": "⚠️",
        "failed": "❌",
        "pending": "⏳"
    }
    return mapping.get(status.lower(), "❓")


def create_search_highlight(
    text: str,
    query: str,
    tag: str = "mark"
) -> str:
    """Add highlight tags around query matches in text."""
    if not query:
        return text
    
    # Escape special regex characters
    escaped_query = re.escape(query)
    
    # Case-insensitive replacement
    pattern = re.compile(f'({escaped_query})', re.IGNORECASE)
    return pattern.sub(f'<{tag}>\\1</{tag}>', text)
