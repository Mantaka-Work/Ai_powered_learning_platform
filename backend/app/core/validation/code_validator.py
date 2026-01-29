"""Code validation for generated code."""
from typing import Dict, Any, List, Optional
import subprocess
import tempfile
import os
from pathlib import Path


class CodeValidator:
    """Validate generated code for syntax, style, and correctness."""
    
    LANGUAGE_EXTENSIONS = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "java": ".java",
        "cpp": ".cpp",
        "c": ".c",
        "csharp": ".cs",
        "go": ".go",
        "rust": ".rs"
    }
    
    async def validate(
        self,
        code: str,
        language: str,
        run_tests: bool = False
    ) -> Dict[str, Any]:
        """
        Validate code for correctness.
        
        Args:
            code: The code to validate
            language: Programming language
            run_tests: Whether to attempt execution
        
        Returns:
            Validation results
        """
        language = language.lower()
        
        results = {
            "status": "validated",
            "score": 100.0,
            "syntax_valid": True,
            "lint_issues": [],
            "execution_result": None,
            "suggestions": []
        }
        
        # Syntax check
        syntax_result = await self._check_syntax(code, language)
        results["syntax_valid"] = syntax_result["valid"]
        if not syntax_result["valid"]:
            results["status"] = "failed"
            results["score"] = 0
            results["lint_issues"].append({
                "type": "error",
                "message": syntax_result.get("error", "Syntax error"),
                "line": syntax_result.get("line"),
                "suggestion": "Fix the syntax error"
            })
            return results
        
        # Lint check
        lint_result = await self._lint_code(code, language)
        results["lint_issues"].extend(lint_result.get("issues", []))
        
        # Adjust score based on lint issues
        error_count = sum(1 for i in results["lint_issues"] if i["type"] == "error")
        warning_count = sum(1 for i in results["lint_issues"] if i["type"] == "warning")
        
        results["score"] = max(0, 100 - (error_count * 20) - (warning_count * 5))
        
        if error_count > 0:
            results["status"] = "warning"
        
        # Optional execution
        if run_tests and language in ["python", "javascript"]:
            exec_result = await self._try_execute(code, language)
            results["execution_result"] = exec_result
            if not exec_result.get("success", False):
                results["status"] = "warning"
                results["score"] = max(0, results["score"] - 20)
        
        # Add suggestions
        results["suggestions"] = self._generate_suggestions(results)
        
        # Final status
        if results["score"] >= 80:
            results["status"] = "validated"
        elif results["score"] >= 50:
            results["status"] = "warning"
        else:
            results["status"] = "failed"
        
        return results
    
    async def _check_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """Check code syntax."""
        if language == "python":
            return self._check_python_syntax(code)
        elif language in ["javascript", "typescript"]:
            return self._check_js_syntax(code)
        elif language == "java":
            return self._check_java_syntax(code)
        else:
            # Basic check - assume valid
            return {"valid": True}
    
    def _check_python_syntax(self, code: str) -> Dict[str, Any]:
        """Check Python syntax."""
        import ast
        try:
            ast.parse(code)
            return {"valid": True}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": str(e.msg),
                "line": e.lineno
            }
    
    def _check_js_syntax(self, code: str) -> Dict[str, Any]:
        """Check JavaScript syntax (basic)."""
        # Basic bracket matching
        brackets = {"(": ")", "[": "]", "{": "}"}
        stack = []
        
        in_string = False
        string_char = None
        
        for i, char in enumerate(code):
            if char in ['"', "'", "`"] and (i == 0 or code[i-1] != "\\"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            
            if not in_string:
                if char in brackets:
                    stack.append(char)
                elif char in brackets.values():
                    if not stack:
                        return {"valid": False, "error": f"Unmatched '{char}'", "line": code[:i].count("\n") + 1}
                    if brackets[stack[-1]] != char:
                        return {"valid": False, "error": f"Mismatched brackets", "line": code[:i].count("\n") + 1}
                    stack.pop()
        
        if stack:
            return {"valid": False, "error": "Unclosed brackets", "line": None}
        
        return {"valid": True}
    
    def _check_java_syntax(self, code: str) -> Dict[str, Any]:
        """Check Java syntax (basic)."""
        # Similar bracket check
        return self._check_js_syntax(code)
    
    async def _lint_code(self, code: str, language: str) -> Dict[str, Any]:
        """Run linting on code."""
        issues = []
        
        if language == "python":
            issues = self._lint_python(code)
        elif language in ["javascript", "typescript"]:
            issues = self._lint_javascript(code)
        
        return {"issues": issues}
    
    def _lint_python(self, code: str) -> List[Dict[str, Any]]:
        """Lint Python code."""
        issues = []
        lines = code.split("\n")
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                issues.append({
                    "type": "warning",
                    "message": f"Line too long ({len(line)} > 120)",
                    "line": i,
                    "suggestion": "Consider breaking this line"
                })
            
            # Check for print statements (might be debug)
            if "print(" in line and "#" not in line.split("print(")[0]:
                issues.append({
                    "type": "info",
                    "message": "Print statement found - ensure it's intentional",
                    "line": i,
                    "suggestion": "Use logging for production code"
                })
            
            # Check for TODO comments
            if "TODO" in line or "FIXME" in line:
                issues.append({
                    "type": "info",
                    "message": "TODO/FIXME comment found",
                    "line": i,
                    "suggestion": "Complete or remove TODO items"
                })
        
        return issues
    
    def _lint_javascript(self, code: str) -> List[Dict[str, Any]]:
        """Lint JavaScript code."""
        issues = []
        lines = code.split("\n")
        
        for i, line in enumerate(lines, 1):
            # Check for var usage
            if "var " in line:
                issues.append({
                    "type": "warning",
                    "message": "Use 'let' or 'const' instead of 'var'",
                    "line": i,
                    "suggestion": "Replace 'var' with 'let' or 'const'"
                })
            
            # Check for console.log
            if "console.log" in line:
                issues.append({
                    "type": "info",
                    "message": "console.log found - ensure it's intentional",
                    "line": i,
                    "suggestion": "Remove debug statements for production"
                })
        
        return issues
    
    async def _try_execute(self, code: str, language: str) -> Dict[str, Any]:
        """Try to execute code in a safe environment."""
        if language == "python":
            return await self._execute_python(code)
        return {"success": False, "error": "Execution not supported for this language"}
    
    async def _execute_python(self, code: str) -> Dict[str, Any]:
        """Execute Python code safely."""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=10  # 10 second timeout
            )
            
            os.unlink(temp_path)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:1000] if result.stdout else None,
                "stderr": result.stderr[:500] if result.stderr else None,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_suggestions(self, results: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        if not results["syntax_valid"]:
            suggestions.append("Fix syntax errors before deployment")
        
        error_issues = [i for i in results["lint_issues"] if i["type"] == "error"]
        warning_issues = [i for i in results["lint_issues"] if i["type"] == "warning"]
        
        if error_issues:
            suggestions.append(f"Address {len(error_issues)} error(s) in the code")
        
        if warning_issues:
            suggestions.append(f"Consider fixing {len(warning_issues)} warning(s)")
        
        if results["score"] == 100:
            suggestions.append("Code looks good! Ready for use.")
        
        return suggestions


# Singleton instance
_validator = None


def get_code_validator() -> CodeValidator:
    """Get or create validator singleton."""
    global _validator
    if _validator is None:
        _validator = CodeValidator()
    return _validator
