"""Metadata extraction from uploaded files."""
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class MetadataExtractor:
    """Extract metadata from uploaded files."""
    
    # File type mappings
    FILE_TYPE_MAP = {
        ".pdf": "pdf",
        ".pptx": "slide",
        ".ppt": "slide",
        ".docx": "document",
        ".doc": "document",
        ".md": "markdown",
        ".txt": "text",
        ".py": "code",
        ".js": "code",
        ".ts": "code",
        ".java": "code",
        ".cpp": "code",
        ".c": "code",
        ".cs": "code",
        ".json": "data",
        ".yaml": "data",
        ".yml": "data"
    }
    
    # Language detection
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".cs": "csharp",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php"
    }
    
    def extract(
        self,
        filename: str,
        file_size: int,
        content_preview: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata from a file.
        
        Args:
            filename: Original filename
            file_size: File size in bytes
            content_preview: Optional preview of file content
        
        Returns:
            Extracted metadata
        """
        path = Path(filename)
        ext = path.suffix.lower()
        
        metadata = {
            "original_filename": filename,
            "file_extension": ext,
            "file_type": self.FILE_TYPE_MAP.get(ext, "other"),
            "file_size": file_size,
            "file_size_human": self._format_size(file_size),
            "extracted_at": datetime.utcnow().isoformat()
        }
        
        # Add programming language if applicable
        if ext in self.LANGUAGE_MAP:
            metadata["programming_language"] = self.LANGUAGE_MAP[ext]
        
        # Try to extract title from filename
        metadata["suggested_title"] = self._suggest_title(path.stem)
        
        # Try to extract week number from filename
        week = self._extract_week(filename)
        if week:
            metadata["suggested_week"] = week
        
        # Try to detect category from filename/content
        metadata["suggested_category"] = self._suggest_category(filename, ext)
        
        return metadata
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _suggest_title(self, filename_stem: str) -> str:
        """Suggest a title from filename."""
        # Replace common separators with spaces
        title = filename_stem.replace("_", " ").replace("-", " ")
        
        # Remove common prefixes
        for prefix in ["lecture", "lec", "week", "lab", "assignment"]:
            if title.lower().startswith(prefix):
                parts = title.split()
                if len(parts) > 1:
                    # Remove prefix and number if present
                    title = " ".join(parts[1:])
                    if title and title[0].isdigit():
                        title = " ".join(title.split()[1:])
        
        # Title case
        return title.title() if title else filename_stem
    
    def _extract_week(self, filename: str) -> Optional[int]:
        """Try to extract week number from filename."""
        import re
        
        # Common patterns
        patterns = [
            r"week[_\s-]?(\d+)",
            r"w(\d+)",
            r"lecture[_\s-]?(\d+)",
            r"lec[_\s-]?(\d+)"
        ]
        
        filename_lower = filename.lower()
        for pattern in patterns:
            match = re.search(pattern, filename_lower)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        
        return None
    
    def _suggest_category(self, filename: str, ext: str) -> str:
        """Suggest category (theory/lab) based on filename and extension."""
        filename_lower = filename.lower()
        
        # Check for explicit lab indicators
        lab_keywords = ["lab", "practical", "exercise", "assignment", "code", "program"]
        if any(kw in filename_lower for kw in lab_keywords):
            return "lab"
        
        # Code files are lab
        if ext in self.LANGUAGE_MAP:
            return "lab"
        
        # Default to theory
        return "theory"
    
    def extract_title(self, filename: str, content_preview: Optional[str] = None) -> str:
        """
        Extract/suggest a title from filename and optional content preview.
        
        Args:
            filename: Original filename
            content_preview: Optional preview of file content (unused for now)
        
        Returns:
            Suggested title
        """
        path = Path(filename)
        return self._suggest_title(path.stem)
    
    def extract_week_number(self, filename: str, title: Optional[str] = None) -> Optional[int]:
        """
        Extract week number from filename or title.
        
        Args:
            filename: Original filename
            title: Optional title to check for week number
        
        Returns:
            Week number if found, None otherwise
        """
        # Try filename first
        week = self._extract_week(filename)
        if week:
            return week
        
        # Try title if provided
        if title:
            week = self._extract_week(title)
        
        return week
    
    def detect_programming_language(self, filename: str, file_type: Optional[str] = None) -> Optional[str]:
        """
        Detect programming language from filename.
        
        Args:
            filename: Original filename
            file_type: Optional file type/extension
        
        Returns:
            Programming language if detected, None otherwise
        """
        path = Path(filename)
        ext = path.suffix.lower()
        
        return self.LANGUAGE_MAP.get(ext)


# Singleton instance
_extractor = None


def get_metadata_extractor() -> MetadataExtractor:
    """Get or create metadata extractor singleton."""
    global _extractor
    if _extractor is None:
        _extractor = MetadataExtractor()
    return _extractor
