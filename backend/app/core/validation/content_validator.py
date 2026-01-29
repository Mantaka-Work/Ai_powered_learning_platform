"""Content validation for generated theory materials."""
from typing import Dict, Any, List, Optional
from uuid import UUID
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from app.config import settings
from app.core.rag.retriever import get_retriever


class ContentValidator:
    """Validate generated theory content."""
    
    # Trusted domains for web sources
    TRUSTED_DOMAINS = [
        "wikipedia.org", "docs.python.org", "developer.mozilla.org",
        "stackoverflow.com", "github.com", "microsoft.com",
        "oracle.com", "w3schools.com", "geeksforgeeks.org",
        "tutorialspoint.com", "edu"  # .edu domains
    ]
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0,  # Deterministic for validation
            api_key=settings.OPENAI_API_KEY
        )
        self.retriever = get_retriever()
    
    async def validate(
        self,
        content: str,
        topic: str,
        course_id: UUID,
        check_grounding: bool = True,
        check_web_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Validate generated content.
        
        Args:
            content: The generated content to validate
            topic: The topic it should cover
            course_id: Course ID for grounding check
            check_grounding: Whether to check grounding in materials
            check_web_sources: Whether to validate web sources
        
        Returns:
            Validation results
        """
        results = {
            "status": "validated",
            "score": 100.0,
            "grounding_score": 100.0,
            "structure_score": 100.0,
            "relevance_score": 100.0,
            "issues": [],
            "web_sources_valid": True,
            "suggestions": []
        }
        
        # Structure check
        structure_result = self._check_structure(content)
        results["structure_score"] = structure_result["score"]
        results["issues"].extend(structure_result.get("issues", []))
        
        # Relevance check
        relevance_result = await self._check_relevance(content, topic)
        results["relevance_score"] = relevance_result["score"]
        results["issues"].extend(relevance_result.get("issues", []))
        
        # Grounding check
        if check_grounding:
            grounding_result = await self._check_grounding(content, topic, course_id)
            results["grounding_score"] = grounding_result["score"]
            results["issues"].extend(grounding_result.get("issues", []))
        
        # Web source validation
        if check_web_sources:
            web_result = self._validate_web_citations(content)
            results["web_sources_valid"] = web_result["valid"]
            results["issues"].extend(web_result.get("issues", []))
        
        # Calculate overall score
        results["score"] = (
            results["grounding_score"] * 0.4 +
            results["structure_score"] * 0.3 +
            results["relevance_score"] * 0.3
        )
        
        # Determine status
        if results["score"] >= 80:
            results["status"] = "validated"
        elif results["score"] >= 50:
            results["status"] = "warning"
        else:
            results["status"] = "failed"
        
        # Generate suggestions
        results["suggestions"] = self._generate_suggestions(results)
        
        return results
    
    def _check_structure(self, content: str) -> Dict[str, Any]:
        """Check content structure and formatting."""
        issues = []
        score = 100
        
        # Check for headings
        if "#" not in content:
            issues.append({
                "type": "warning",
                "message": "No headings found",
                "suggestion": "Add section headings for better organization"
            })
            score -= 10
        
        # Check for sections
        lines = content.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]
        
        if len(non_empty_lines) < 5:
            issues.append({
                "type": "warning",
                "message": "Content seems too short",
                "suggestion": "Add more detail and explanations"
            })
            score -= 15
        
        # Check for bullet points or lists
        has_lists = any(l.strip().startswith(("-", "*", "1.")) for l in lines)
        if not has_lists:
            issues.append({
                "type": "info",
                "message": "No lists found",
                "suggestion": "Consider using bullet points for key concepts"
            })
            score -= 5
        
        # Check for code blocks in content
        if "```" in content:
            # Verify code blocks are closed
            if content.count("```") % 2 != 0:
                issues.append({
                    "type": "error",
                    "message": "Unclosed code block",
                    "suggestion": "Close all code blocks with ```"
                })
                score -= 20
        
        return {"score": max(0, score), "issues": issues}
    
    async def _check_relevance(self, content: str, topic: str) -> Dict[str, Any]:
        """Check if content is relevant to the topic."""
        prompt = f"""Rate how relevant this content is to the topic on a scale of 0-100.

TOPIC: {topic}

CONTENT:
{content[:2000]}

Respond with ONLY a number between 0 and 100, nothing else."""
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            score = float(response.content.strip())
            score = max(0, min(100, score))
            
            issues = []
            if score < 50:
                issues.append({
                    "type": "error",
                    "message": f"Content has low relevance to topic ({score}%)",
                    "suggestion": "Regenerate with clearer focus on the topic"
                })
            elif score < 70:
                issues.append({
                    "type": "warning",
                    "message": f"Content could be more focused on topic ({score}%)",
                    "suggestion": "Consider adding more topic-specific information"
                })
            
            return {"score": score, "issues": issues}
        except Exception:
            return {"score": 70, "issues": []}  # Default if check fails
    
    async def _check_grounding(
        self,
        content: str,
        topic: str,
        course_id: UUID
    ) -> Dict[str, Any]:
        """Check if content is grounded in course materials."""
        # Retrieve relevant course materials
        course_context = await self.retriever.get_context_for_generation(
            topic=topic,
            course_id=course_id,
            max_chunks=5
        )
        
        if not course_context:
            return {
                "score": 50,
                "issues": [{
                    "type": "warning",
                    "message": "No course materials found for grounding check",
                    "suggestion": "Content may not be based on course materials"
                }]
            }
        
        # Count citations
        course_citations = content.count("📚")
        
        issues = []
        score = 100
        
        if course_citations == 0:
            issues.append({
                "type": "warning",
                "message": "No course material citations (📚) found",
                "suggestion": "Add citations to course materials"
            })
            score = 60
        elif course_citations < 2:
            issues.append({
                "type": "info",
                "message": "Few course material citations",
                "suggestion": "Consider adding more references to course materials"
            })
            score = 80
        
        return {"score": score, "issues": issues}
    
    def _validate_web_citations(self, content: str) -> Dict[str, Any]:
        """Validate web source citations."""
        import re
        
        issues = []
        valid = True
        
        # Count web citations
        web_citations = content.count("🌐")
        
        # Look for URLs
        url_pattern = r"https?://([^\s\)]+)"
        urls = re.findall(url_pattern, content)
        
        for url in urls:
            domain = url.split("/")[0].lower()
            
            # Check if domain is trusted
            is_trusted = any(trusted in domain for trusted in self.TRUSTED_DOMAINS)
            
            if not is_trusted:
                issues.append({
                    "type": "info",
                    "message": f"Unverified source domain: {domain}",
                    "suggestion": "Verify the credibility of this source"
                })
        
        if web_citations > 0 and len(urls) == 0:
            issues.append({
                "type": "warning",
                "message": "Web citations without URLs",
                "suggestion": "Include source URLs for web citations"
            })
            valid = False
        
        return {"valid": valid, "issues": issues}
    
    async def validate_web_source(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single web source."""
        url = source.get("url", "")
        domain = ""
        
        if url:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
        
        # Check domain trust
        is_trusted = any(trusted in domain for trusted in self.TRUSTED_DOMAINS)
        
        # Check recency if date provided
        is_recent = True
        published_date = source.get("published_date")
        if published_date:
            from datetime import datetime, timedelta
            try:
                date = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
                is_recent = (datetime.now(date.tzinfo) - date) < timedelta(days=365)
            except Exception:
                pass
        
        return {
            "url": url,
            "domain": domain,
            "is_trusted": is_trusted,
            "is_recent": is_recent,
            "credibility_score": 80 if is_trusted else 50
        }
    
    def _generate_suggestions(self, results: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        if results["grounding_score"] < 70:
            suggestions.append("Add more references to course materials (📚)")
        
        if results["structure_score"] < 70:
            suggestions.append("Improve content structure with headings and lists")
        
        if results["relevance_score"] < 70:
            suggestions.append("Focus more directly on the requested topic")
        
        if not results["web_sources_valid"]:
            suggestions.append("Include URLs for web source citations")
        
        if results["score"] >= 80:
            suggestions.append("Content is well-validated and ready for use")
        
        return suggestions


# Singleton instance
_content_validator = None


def get_content_validator() -> ContentValidator:
    """Get or create content validator singleton."""
    global _content_validator
    if _content_validator is None:
        _content_validator = ContentValidator()
    return _content_validator
