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
        code_type: str = "example",  # example, solution, explanation
        course_context: Optional[str] = None,
        web_context: Optional[str] = None,
        include_tests: bool = False,
        include_comments: bool = True
    ) -> Dict[str, Any]:
        """
        Generate code example, solution, or explanation.
        
        Args:
            topic: The topic/problem to generate code for
            course_id: Course ID for context retrieval
            language: Programming language
            code_type: Type of generation (example, solution, explanation)
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
        
        # Build prompts based on code_type
        system_message = self._build_system_message(
            language=language,
            code_type=code_type,
            course_context=course_context,
            web_context=web_context,
            include_comments=include_comments
        )
        
        user_message = self._build_user_message(
            topic=topic,
            language=language,
            code_type=code_type,
            include_tests=include_tests
        )
        
        # Generate code
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        content = response.content
        
        # For explanation type, keep the full response with markdown
        # For code types, extract just the code block
        if code_type != "explanation":
            content = self._extract_code_block(content, language)
        
        return {
            "code": content,
            "language": language,
            "topic": topic,
            "code_type": code_type,
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
        code_type: str,
        course_context: Optional[str],
        web_context: Optional[str],
        include_comments: bool
    ) -> str:
        """Build system message for code generation."""
        
        if code_type == "explanation":
            base = f"""You are an expert {language} programmer and educator specializing in explaining code to students.
Your task is to provide detailed, comprehensive explanations of code concepts.

EXPLANATION REQUIREMENTS:
- Explain the code LINE BY LINE in great detail
- Describe what each part does and WHY it does it
- Explain the logic, algorithms, and data structures used
- Use simple language that university students can understand
- Include analogies and real-world examples where helpful
- Point out common pitfalls and best practices
- Explain time and space complexity if relevant
- Format your explanation in clear sections with markdown
- Include the code with detailed inline comments

Your explanation should be THOROUGH and EDUCATIONAL - treat this as if you're teaching the concept to someone learning it for the first time.
"""
        elif code_type == "solution":
            base = f"""You are an expert {language} programmer helping students solve programming problems.
You generate complete, working solutions with clear explanations.

SOLUTION REQUIREMENTS:
- Provide a complete, optimal solution to the problem
- Explain your approach before the code
- Code MUST be syntactically correct and compile/run without errors
- Follow {language} best practices and conventions
- {"Include helpful comments explaining key parts" if include_comments else "Keep comments minimal"}
- Handle edge cases appropriately
- Explain the time and space complexity
"""
        else:  # example
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
        code_type: str,
        include_tests: bool
    ) -> str:
        """Build user message for code generation."""
        
        if code_type == "explanation":
            msg = f"""Please provide a DETAILED, COMPREHENSIVE explanation of the following {language} code/concept:

TOPIC: {topic}

Your explanation should include:
1. **Overview**: What is this code/concept about?
2. **Step-by-Step Breakdown**: Explain each line/section in detail
3. **How It Works**: Describe the underlying logic and flow
4. **Key Concepts**: Highlight important programming concepts used
5. **Example Code**: Show the code with detailed comments
6. **Common Mistakes**: What errors do beginners often make?
7. **Best Practices**: How to write this code properly
8. **Practice Suggestions**: How can students practice this?

Make your explanation thorough, clear, and educational. Use markdown formatting with headers, bullet points, and code blocks.
"""
        elif code_type == "solution":
            msg = f"""Provide a complete solution for:

TOPIC: {topic}

Requirements:
- First explain your approach and strategy
- Provide the complete, working {language} code
- Include comments explaining key parts
- Explain the time and space complexity
- Mention any assumptions made
"""
            if include_tests:
                msg += """- Include test cases demonstrating the solution works
"""
        else:  # example
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
Wrap code in markdown code blocks with the language specified.
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
