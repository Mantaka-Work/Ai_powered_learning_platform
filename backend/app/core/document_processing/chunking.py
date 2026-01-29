"""Text chunking strategies for document processing."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Chunk:
    """A document chunk with metadata."""
    content: str
    index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]


class TextChunker:
    """Split text into chunks for embedding."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separator: str = "\n\n"
    ):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Overlap between chunks
            separator: Primary separator to split on
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
        
        Returns:
            List of Chunk objects
        """
        if not text.strip():
            return []
        
        # First, split by separator
        segments = text.split(self.separator)
        
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        char_pos = 0
        
        for segment in segments:
            segment_with_sep = segment + self.separator
            
            # If adding this segment exceeds chunk size, finalize current chunk
            if len(current_chunk) + len(segment_with_sep) > self.chunk_size and current_chunk:
                chunks.append(Chunk(
                    content=current_chunk.strip(),
                    index=chunk_index,
                    start_char=current_start,
                    end_char=char_pos,
                    metadata=metadata or {}
                ))
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                current_chunk = current_chunk[overlap_start:]
                current_start = char_pos - len(current_chunk)
            
            current_chunk += segment_with_sep
            char_pos += len(segment_with_sep)
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                index=chunk_index,
                start_char=current_start,
                end_char=char_pos,
                metadata=metadata or {}
            ))
        
        return chunks
    
    def chunk_code(
        self,
        code: str,
        language: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Chunk code with awareness of code structure.
        
        Tries to keep functions/classes together.
        """
        # Language-specific delimiters
        delimiters = {
            "python": ["\ndef ", "\nclass ", "\n\n"],
            "javascript": ["\nfunction ", "\nclass ", "\nconst ", "\n\n"],
            "typescript": ["\nfunction ", "\nclass ", "\nconst ", "\ninterface ", "\n\n"],
            "java": ["\npublic ", "\nprivate ", "\nprotected ", "\nclass ", "\n\n"],
            "cpp": ["\nvoid ", "\nint ", "\nclass ", "\n\n"],
        }
        
        seps = delimiters.get(language, ["\n\n"])
        
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        # Split by function/class definitions
        lines = code.split("\n")
        char_pos = 0
        
        for line in lines:
            line_with_newline = line + "\n"
            
            # Check if this line starts a new code block
            is_new_block = any(line.startswith(sep.strip()) for sep in seps if sep.strip())
            
            if is_new_block and len(current_chunk) > self.chunk_size // 2:
                # Save current chunk
                if current_chunk.strip():
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        index=chunk_index,
                        start_char=current_start,
                        end_char=char_pos,
                        metadata={**(metadata or {}), "language": language}
                    ))
                    chunk_index += 1
                
                current_chunk = ""
                current_start = char_pos
            
            current_chunk += line_with_newline
            char_pos += len(line_with_newline)
            
            # Force split if chunk too large
            if len(current_chunk) > self.chunk_size:
                chunks.append(Chunk(
                    content=current_chunk.strip(),
                    index=chunk_index,
                    start_char=current_start,
                    end_char=char_pos,
                    metadata={**(metadata or {}), "language": language}
                ))
                chunk_index += 1
                current_chunk = ""
                current_start = char_pos
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                index=chunk_index,
                start_char=current_start,
                end_char=char_pos,
                metadata={**(metadata or {}), "language": language}
            ))
        
        return chunks


# Singleton instance
_chunker = None


def get_chunker() -> TextChunker:
    """Get or create chunker singleton."""
    global _chunker
    if _chunker is None:
        _chunker = TextChunker()
    return _chunker
