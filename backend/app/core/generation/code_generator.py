"""Code example generator."""
from typing import Optional, Dict, Any, List
from uuid import UUID
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.core.generation.prompts import CODE_PROMPTS
from app.core.rag.retriever import get_retriever


class CodeGenerator:
    """Generate code examples and solutions."""
    
    SUPPORTED_LANGUAGES = [
        "python", "javascript", "typescript", "java", 
        "cpp", "c", "csharp", "go", "rust", "sql"
    ]
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0.3,  # Lower temperature for code
            api_key=settings.OPENAI_API_KEY,
            max_tokens=settings.MAX_GENERATION_TOKENS
        )
        self.retriever = get_retriever()
    
    async def generate(
        self,
        topic: str,
        course_id: UUID,
        language: str,
        course_context: Optional[str] = None,
        web_context: Optional[str] = None,
        include_tests: bool = False,
        include_comments: bool = True
    ) -> Dict[str, Any]:
        """
        Generate code example.
        
        Args:
            topic: The topic/problem to generate code for
            course_id: Course ID for context retrieval
            language: Programming language
            course_context: Pre-retrieved course context
            web_context: Web search context
            include_tests: Include test cases
            include_comments: Include code comments
        
        Returns:
            Generated code with metadata
        """
        # Normalize language name
        language = language.lower()
        if language not in self.SUPPORTED_LANGUAGES:
            language = "python"  # Default
        
        # Get course context if not provided
        if course_context is None:
            course_context = await self.retriever.get_context_for_generation(
                topic=f"{topic} {language}",
                course_id=course_id,
                max_chunks=8
            )
        
        # Build prompts
        system_message = self._build_system_message(
            language=language,
            course_context=course_context,
            web_context=web_context,
            include_comments=include_comments
        )
        
        user_message = self._build_user_message(
            topic=topic,
            language=language,
            include_tests=include_tests
        )
        
        # Generate code
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        code = response.content
        
        # Extract just the code if wrapped in markdown
        code = self._extract_code_block(code, language)
        
        return {
            "code": code,
            "language": language,
            "topic": topic,
            "sources": {
                "course": bool(course_context),
                "web": bool(web_context)
            },
            "includes_tests": include_tests,
            "includes_comments": include_comments
        }
    
    def _build_system_message(
        self,
        language: str,
        course_context: Optional[str],
        web_context: Optional[str],
        include_comments: bool
    ) -> str:
        """Build system message for code generation."""
        base = f"""You are an expert {language} programmer and educator.
You generate high-quality, working code examples for university students.

REQUIREMENTS:
- Code MUST be syntactically correct and compile/run without errors
- Follow {language} best practices and conventions
- Use clear, descriptive variable and function names
- {"Include helpful comments explaining the code" if include_comments else "Minimize comments"}
- Handle edge cases appropriately
- Make code educational and easy to understand

"""
        
        if course_context:
            base += f"""
REFERENCE CODE FROM COURSE MATERIALS:
{course_context}

Base your code style and patterns on the course materials above.
"""
        
        if web_context:
            base += f"""
CURRENT BEST PRACTICES (from web):
{web_context}

Consider modern best practices when appropriate.
"""
        
        return base
    
    def _build_user_message(
        self,
        topic: str,
        language: str,
        include_tests: bool
    ) -> str:
        """Build user message for code generation."""
        msg = f"""Generate a complete, working {language} code example for:

TOPIC: {topic}

Requirements:
- Provide a complete, runnable code file
- Include example usage that demonstrates the code
"""
        
        if include_tests:
            msg += """- Include unit tests or test cases
- Show expected output
"""
        
        msg += """
Wrap the code in a markdown code block with the language specified.
"""
        
        return msg
    
    def _extract_code_block(self, response: str, language: str) -> str:
        """Extract code from markdown code blocks."""
        import re
        
        # Try to find code block with language
        pattern = rf"```{language}?\n?(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[0].strip()
        
        # Try generic code block
        pattern = r"```\n?(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Return as-is if no code blocks
        return response.strip()


# Singleton instance
_code_generator = None


def get_code_generator() -> CodeGenerator:
    """Get or create code generator singleton."""
    global _code_generator
    if _code_generator is None:
        _code_generator = CodeGenerator()
    return _code_generator
