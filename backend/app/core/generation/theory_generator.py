"""Theory content generator for notes, summaries, and study guides."""
from typing import Optional, Dict, Any, List
from uuid import UUID
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_settings
from app.core.generation.prompts import THEORY_PROMPTS
from app.core.rag.retriever import get_retriever


class TheoryGenerator:
    """Generate theory learning materials."""
    
    def __init__(self):
        settings = get_settings()
        self.llm = ChatOpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            temperature=settings.GENERATION_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
            max_tokens=settings.MAX_GENERATION_TOKENS
        )
        self.retriever = get_retriever()
    
    async def generate(
        self,
        topic: str,
        course_id: UUID,
        generation_type: str = "notes",  # notes, summary, study_guide
        course_context: Optional[str] = None,
        web_context: Optional[str] = None,
        max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate theory learning material.
        
        Args:
            topic: The topic to generate content about
            course_id: Course ID for context retrieval
            generation_type: Type of content to generate
            course_context: Pre-retrieved course context (optional)
            web_context: Web search context (optional)
            max_length: Maximum length in words
        
        Returns:
            Generated content with metadata
        """
        # Get course context if not provided
        if course_context is None:
            course_context = await self.retriever.get_context_for_generation(
                topic=topic,
                course_id=course_id,
                max_chunks=10
            )
        
        # Get appropriate prompt template
        prompt_template = THEORY_PROMPTS.get(generation_type, THEORY_PROMPTS["notes"])
        
        # Build the system message
        system_message = self._build_system_message(
            generation_type=generation_type,
            course_context=course_context,
            web_context=web_context
        )
        
        # Build the user message
        user_message = prompt_template.format(
            topic=topic,
            max_length=max_length or "appropriate length"
        )
        
        # Generate content
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        content = response.content
        
        # Extract source attribution
        sources = self._extract_sources(content, course_context, web_context)
        
        return {
            "content": content,
            "type": generation_type,
            "topic": topic,
            "sources": sources,
            "course_context_used": bool(course_context),
            "web_context_used": bool(web_context),
            "source_mix_ratio": self._calculate_source_ratio(content, course_context, web_context)
        }
    
    def _build_system_message(
        self,
        generation_type: str,
        course_context: Optional[str],
        web_context: Optional[str]
    ) -> str:
        """Build the system message with context."""
        base = f"""You are an expert educational content creator for university courses.
You are generating {generation_type} for students.

Your content should be:
- Clear and educational
- Well-structured with proper headings and sections
- Grounded in the provided course materials
- Academically appropriate
- Include proper citations using 📚 for course materials and 🌐 for web sources

"""
        
        if course_context:
            base += f"""
COURSE MATERIALS CONTEXT:
{course_context}

Use the above course materials as your PRIMARY source. Cite them with 📚.
"""
        
        if web_context:
            base += f"""
SUPPLEMENTARY WEB RESEARCH:
{web_context}

Use web research only to supplement course materials. Cite them with 🌐.
"""
        
        return base
    
    def _extract_sources(
        self,
        content: str,
        course_context: Optional[str],
        web_context: Optional[str]
    ) -> Dict[str, List[str]]:
        """Extract source references from content."""
        sources = {
            "course": [],
            "web": []
        }
        
        # Extract course material references
        if course_context:
            import re
            source_pattern = r"\[Source \d+: ([^\]]+)\]"
            course_sources = re.findall(source_pattern, course_context)
            sources["course"] = list(set(course_sources))
        
        # Count citation types in generated content
        course_citations = content.count("📚")
        web_citations = content.count("🌐")
        
        sources["course_citation_count"] = course_citations
        sources["web_citation_count"] = web_citations
        
        return sources
    
    def _calculate_source_ratio(
        self,
        content: str,
        course_context: Optional[str],
        web_context: Optional[str]
    ) -> float:
        """Calculate ratio of course vs web sources used."""
        if not web_context:
            return 1.0  # 100% course
        if not course_context:
            return 0.0  # 100% web
        
        course_citations = content.count("📚")
        web_citations = content.count("🌐")
        total = course_citations + web_citations
        
        if total == 0:
            # Default to course-heavy
            return 0.7
        
        return course_citations / total


# Singleton instance
_theory_generator = None


def get_theory_generator() -> TheoryGenerator:
    """Get or create theory generator singleton."""
    global _theory_generator
    if _theory_generator is None:
        _theory_generator = TheoryGenerator()
    return _theory_generator
