"""Generation service for creating theory notes and code examples."""
import time
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from app.core.generation.theory_generator import get_theory_generator
from app.core.generation.code_generator import get_code_generator
from app.core.validation.code_validator import get_code_validator
from app.core.validation.content_validator import get_content_validator
from app.services.search_service import get_search_service
from app.db.repositories.generation_repo import get_generation_repository
from app.config import settings


class GenerationService:
    """Service for generating educational content."""
    
    def __init__(self):
        self.theory_generator = get_theory_generator()
        self.code_generator = get_code_generator()
        self.code_validator = get_code_validator()
        self.content_validator = get_content_validator()
        self.search_service = get_search_service()
        self.generation_repo = get_generation_repository()
    
    async def generate_theory(
        self,
        course_id: UUID,
        topic: str,
        gen_type: str = "notes",  # notes, summary, study_guide
        use_web: bool = False,
        user_id: Optional[UUID] = None,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate theory content (notes, summary, study guide).
        
        Args:
            course_id: Course context
            topic: Topic to generate content about
            gen_type: Type of generation (notes, summary, study_guide)
            use_web: Whether to include web search results
            user_id: Optional user ID for tracking
            validate: Whether to validate the generated content
        """
        start_time = time.time()
        
        # Search for relevant context
        search_results = await self.search_service.hybrid_search(
            query=topic,
            course_id=course_id,
            limit=10,
            include_web=use_web
        )
        
        # Prepare context from search results
        course_context = self._prepare_context(search_results.get("course_results", []))
        web_context = self._prepare_web_context(search_results.get("web_results", []))
        
        # Generate content
        generated = await self.theory_generator.generate(
            topic=topic,
            course_id=course_id,
            generation_type=gen_type,
            course_context=course_context,
            web_context=web_context if use_web else None
        )
        
        # Prepare sources
        sources = {
            "course": [
                {"title": r["material_title"], "type": r["file_type"], "relevance": r["relevance_score"]}
                for r in search_results.get("course_results", [])[:5]
            ]
        }
        
        web_sources = []
        if use_web and search_results.get("web_results"):
            web_sources = [
                {"title": r["title"], "url": r["url"], "domain": r["source_domain"]}
                for r in search_results.get("web_results", [])[:5]
            ]
            sources["web"] = web_sources
        
        # Calculate source mix ratio
        course_count = len(sources.get("course", []))
        web_count = len(sources.get("web", []))
        total = course_count + web_count
        source_mix_ratio = course_count / total if total > 0 else 1.0
        
        # Validate if requested
        validation_result = None
        if validate:
            validation_result = await self.content_validator.validate(
                content=generated["content"],
                topic=topic,
                course_id=course_id
            )
        
        # Store generation
        generation_id = uuid4()
        stored = await self.generation_repo.create_generation(
            course_id=course_id,
            user_id=user_id,
            gen_type=f"theory_{gen_type}",
            topic=topic,
            content=generated["content"],
            validation_status=validation_result["status"] if validation_result else None,
            validation_score=validation_result["score"] if validation_result else None,
            validation_details=validation_result if validation_result else None,
            sources=sources,
            used_web_search=use_web and bool(web_sources),
            web_sources=web_sources,
            source_mix_ratio=source_mix_ratio
        )
        
        elapsed = time.time() - start_time
        
        return {
            "id": stored["id"],
            "status": "completed",
            "type": f"theory_{gen_type}",
            "topic": topic,
            "content": generated["content"],
            "validation_status": validation_result["status"] if validation_result else None,
            "validation_score": validation_result["score"] if validation_result else None,
            "sources": sources,
            "used_web_search": use_web and bool(web_sources),
            "source_mix_ratio": source_mix_ratio,
            "generation_time_seconds": round(elapsed, 2)
        }
    
    async def generate_code(
        self,
        course_id: UUID,
        topic: str,
        language: str,
        code_type: str = "example",  # example, solution, explanation
        use_web: bool = False,
        user_id: Optional[UUID] = None,
        validate: bool = True,
        execute: bool = False
    ) -> Dict[str, Any]:
        """
        Generate code examples with optional validation and execution.
        
        Args:
            course_id: Course context
            topic: Topic/problem to generate code for
            language: Programming language
            code_type: Type of code (example, solution, explanation)
            use_web: Whether to include web search results
            user_id: Optional user ID for tracking
            validate: Whether to validate the generated code
            execute: Whether to execute the code in sandbox
        """
        start_time = time.time()
        
        # Search for relevant context
        search_results = await self.search_service.hybrid_search(
            query=f"{topic} {language} code",
            course_id=course_id,
            limit=10,
            include_web=use_web
        )
        
        # Prepare context
        course_context = self._prepare_context(search_results.get("course_results", []))
        web_context = self._prepare_web_context(search_results.get("web_results", []))
        
        # Generate code
        generated = await self.code_generator.generate(
            topic=topic,
            course_id=course_id,
            language=language,
            course_context=course_context,
            web_context=web_context if use_web else None
        )
        
        # Prepare sources
        sources = {
            "course": [
                {"title": r["material_title"], "type": r["file_type"], "relevance": r["relevance_score"]}
                for r in search_results.get("course_results", [])[:5]
            ]
        }
        
        web_sources = []
        if use_web and search_results.get("web_results"):
            web_sources = [
                {"title": r["title"], "url": r["url"], "domain": r["source_domain"]}
                for r in search_results.get("web_results", [])[:5]
            ]
            sources["web"] = web_sources
        
        # Calculate source mix ratio
        course_count = len(sources.get("course", []))
        web_count = len(sources.get("web", []))
        total = course_count + web_count
        source_mix_ratio = course_count / total if total > 0 else 1.0
        
        # Validate if requested
        validation_result = None
        if validate:
            validation_result = await self.code_validator.validate(
                code=generated["code"],
                language=language,
                run_tests=execute
            )
        
        # Store generation
        stored = await self.generation_repo.create_generation(
            course_id=course_id,
            user_id=user_id,
            gen_type=f"code_{code_type}",
            topic=topic,
            content=generated["code"],
            programming_language=language,
            validation_status=validation_result["status"] if validation_result else None,
            validation_score=validation_result["score"] if validation_result else None,
            validation_details=validation_result if validation_result else None,
            sources=sources,
            used_web_search=use_web and bool(web_sources),
            web_sources=web_sources,
            source_mix_ratio=source_mix_ratio
        )
        
        elapsed = time.time() - start_time
        
        return {
            "id": stored["id"],
            "status": "completed",
            "type": f"code_{code_type}",
            "topic": topic,
            "content": generated["code"],
            "explanation": generated.get("explanation", ""),
            "programming_language": language,
            "validation_status": validation_result["status"] if validation_result else None,
            "validation_score": validation_result["score"] if validation_result else None,
            "validation_details": validation_result if validation_result else {},
            "sources": sources,
            "used_web_search": use_web and bool(web_sources),
            "source_mix_ratio": source_mix_ratio,
            "generation_time_seconds": round(elapsed, 2)
        }
    
    async def get_generation_history(
        self,
        course_id: UUID,
        user_id: Optional[UUID] = None,
        gen_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get generation history for a course/user."""
        return await self.generation_repo.get_by_course(
            course_id=course_id,
            user_id=user_id,
            gen_type=gen_type,
            limit=limit
        )
    
    def _prepare_context(self, results: List[Dict]) -> str:
        """Prepare context string from course search results."""
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results[:5], 1):
            content = result.get("content", "")
            title = result.get("material_title", "Unknown")
            context_parts.append(f"[Source {i}: {title}]\n{content}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def _prepare_web_context(self, results: List[Dict]) -> str:
        """Prepare context string from web search results."""
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results[:3], 1):
            snippet = result.get("snippet", "")
            title = result.get("title", "Unknown")
            url = result.get("url", "")
            context_parts.append(f"[Web Source {i}: {title}]\nURL: {url}\n{snippet}")
        
        return "\n\n---\n\n".join(context_parts)


# Singleton instance
_generation_service = None


def get_generation_service() -> GenerationService:
    """Get or create generation service singleton."""
    global _generation_service
    if _generation_service is None:
        _generation_service = GenerationService()
    return _generation_service
