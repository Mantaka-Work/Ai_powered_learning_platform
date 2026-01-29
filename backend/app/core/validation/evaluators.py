"""Scoring and evaluation logic."""
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    """Evaluation result with score and details."""
    score: float  # 0-100
    status: str  # validated, warning, failed
    details: Dict[str, Any]
    suggestions: List[str]


class Evaluator:
    """Unified evaluator for content and code."""
    
    def evaluate_code(
        self,
        validation_result: Dict[str, Any]
    ) -> EvaluationResult:
        """
        Evaluate code validation results.
        
        Scoring:
        - Syntax: 40%
        - Lint: 30%
        - Execution: 30%
        """
        score = 0
        
        # Syntax score (40%)
        if validation_result.get("syntax_valid", False):
            score += 40
        
        # Lint score (30%)
        lint_issues = validation_result.get("lint_issues", [])
        errors = sum(1 for i in lint_issues if i.get("type") == "error")
        warnings = sum(1 for i in lint_issues if i.get("type") == "warning")
        
        lint_score = max(0, 30 - (errors * 10) - (warnings * 3))
        score += lint_score
        
        # Execution score (30%)
        exec_result = validation_result.get("execution_result")
        if exec_result:
            if exec_result.get("success", False):
                score += 30
            else:
                score += 10  # Partial credit for attempting
        else:
            score += 15  # Neutral if not tested
        
        # Determine status
        if score >= 80:
            status = "validated"
        elif score >= 50:
            status = "warning"
        else:
            status = "failed"
        
        return EvaluationResult(
            score=score,
            status=status,
            details={
                "syntax_score": 40 if validation_result.get("syntax_valid") else 0,
                "lint_score": lint_score,
                "execution_tested": exec_result is not None
            },
            suggestions=validation_result.get("suggestions", [])
        )
    
    def evaluate_content(
        self,
        validation_result: Dict[str, Any]
    ) -> EvaluationResult:
        """
        Evaluate content validation results.
        
        Scoring:
        - Grounding: 40%
        - Structure: 30%
        - Relevance: 30%
        """
        grounding = validation_result.get("grounding_score", 70) * 0.4
        structure = validation_result.get("structure_score", 70) * 0.3
        relevance = validation_result.get("relevance_score", 70) * 0.3
        
        score = grounding + structure + relevance
        
        # Determine status
        if score >= 80:
            status = "validated"
        elif score >= 50:
            status = "warning"
        else:
            status = "failed"
        
        return EvaluationResult(
            score=score,
            status=status,
            details={
                "grounding_score": validation_result.get("grounding_score"),
                "structure_score": validation_result.get("structure_score"),
                "relevance_score": validation_result.get("relevance_score"),
                "web_sources_valid": validation_result.get("web_sources_valid", True)
            },
            suggestions=validation_result.get("suggestions", [])
        )
    
    def combine_evaluations(
        self,
        evaluations: List[EvaluationResult]
    ) -> EvaluationResult:
        """Combine multiple evaluations into one."""
        if not evaluations:
            return EvaluationResult(
                score=0,
                status="failed",
                details={},
                suggestions=["No evaluations provided"]
            )
        
        # Average scores
        avg_score = sum(e.score for e in evaluations) / len(evaluations)
        
        # Worst status wins
        statuses = [e.status for e in evaluations]
        if "failed" in statuses:
            status = "failed"
        elif "warning" in statuses:
            status = "warning"
        else:
            status = "validated"
        
        # Combine details and suggestions
        combined_details = {}
        combined_suggestions = []
        
        for i, e in enumerate(evaluations):
            combined_details[f"evaluation_{i+1}"] = e.details
            combined_suggestions.extend(e.suggestions)
        
        return EvaluationResult(
            score=avg_score,
            status=status,
            details=combined_details,
            suggestions=list(set(combined_suggestions))  # Deduplicate
        )


# Singleton instance
_evaluator = None


def get_evaluator() -> Evaluator:
    """Get or create evaluator singleton."""
    global _evaluator
    if _evaluator is None:
        _evaluator = Evaluator()
    return _evaluator
