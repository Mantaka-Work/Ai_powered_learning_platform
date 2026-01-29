"""Syntax-aware code parser for code analysis."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CodeElement:
    """Represents a code element (function, class, etc.)."""
    type: str  # function, class, method, variable, import
    name: str
    content: str
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    parameters: Optional[List[str]] = None


class CodeParser:
    """Parse code to extract structure and elements."""
    
    def __init__(self):
        self.supported_languages = ["python", "javascript", "typescript", "java"]
    
    def parse(self, code: str, language: str) -> Dict[str, Any]:
        """
        Parse code and extract structure.
        
        Args:
            code: Source code
            language: Programming language
        
        Returns:
            Parsed structure with functions, classes, imports, etc.
        """
        language = language.lower()
        
        if language == "python":
            return self._parse_python(code)
        elif language in ["javascript", "typescript"]:
            return self._parse_javascript(code)
        elif language == "java":
            return self._parse_java(code)
        else:
            # Generic parsing
            return self._parse_generic(code)
    
    def _parse_python(self, code: str) -> Dict[str, Any]:
        """Parse Python code."""
        import ast
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "error": str(e),
                "valid": False,
                "elements": []
            }
        
        elements = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                elements.append(CodeElement(
                    type="function",
                    name=node.name,
                    content=ast.unparse(node) if hasattr(ast, 'unparse') else "",
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    docstring=docstring,
                    parameters=[arg.arg for arg in node.args.args]
                ))
            
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                elements.append(CodeElement(
                    type="class",
                    name=node.name,
                    content=ast.unparse(node) if hasattr(ast, 'unparse') else "",
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    docstring=docstring
                ))
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    elements.append(CodeElement(
                        type="import",
                        name=alias.name,
                        content=f"import {alias.name}",
                        start_line=node.lineno,
                        end_line=node.lineno
                    ))
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    elements.append(CodeElement(
                        type="import",
                        name=f"{module}.{alias.name}",
                        content=f"from {module} import {alias.name}",
                        start_line=node.lineno,
                        end_line=node.lineno
                    ))
        
        return {
            "valid": True,
            "language": "python",
            "elements": [self._element_to_dict(e) for e in elements],
            "functions": [e.name for e in elements if e.type == "function"],
            "classes": [e.name for e in elements if e.type == "class"],
            "imports": [e.name for e in elements if e.type == "import"]
        }
    
    def _parse_javascript(self, code: str) -> Dict[str, Any]:
        """Parse JavaScript/TypeScript code (basic regex-based)."""
        import re
        
        elements = []
        lines = code.split("\n")
        
        # Function patterns
        func_patterns = [
            r"function\s+(\w+)\s*\((.*?)\)",
            r"const\s+(\w+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>",
            r"const\s+(\w+)\s*=\s*function\s*\((.*?)\)",
        ]
        
        # Class pattern
        class_pattern = r"class\s+(\w+)"
        
        for i, line in enumerate(lines):
            # Check functions
            for pattern in func_patterns:
                match = re.search(pattern, line)
                if match:
                    elements.append(CodeElement(
                        type="function",
                        name=match.group(1),
                        content=line.strip(),
                        start_line=i + 1,
                        end_line=i + 1,
                        parameters=match.group(2).split(",") if match.group(2) else []
                    ))
                    break
            
            # Check classes
            match = re.search(class_pattern, line)
            if match:
                elements.append(CodeElement(
                    type="class",
                    name=match.group(1),
                    content=line.strip(),
                    start_line=i + 1,
                    end_line=i + 1
                ))
        
        return {
            "valid": True,
            "language": "javascript",
            "elements": [self._element_to_dict(e) for e in elements],
            "functions": [e.name for e in elements if e.type == "function"],
            "classes": [e.name for e in elements if e.type == "class"]
        }
    
    def _parse_java(self, code: str) -> Dict[str, Any]:
        """Parse Java code (basic regex-based)."""
        import re
        
        elements = []
        
        # Class pattern
        class_matches = re.finditer(r"(?:public|private|protected)?\s*class\s+(\w+)", code)
        for match in class_matches:
            elements.append(CodeElement(
                type="class",
                name=match.group(1),
                content=match.group(0),
                start_line=code[:match.start()].count("\n") + 1,
                end_line=code[:match.end()].count("\n") + 1
            ))
        
        # Method pattern
        method_pattern = r"(?:public|private|protected)?\s*(?:static\s+)?(?:\w+)\s+(\w+)\s*\((.*?)\)"
        method_matches = re.finditer(method_pattern, code)
        for match in method_matches:
            if match.group(1) not in ["if", "while", "for", "switch", "class"]:
                elements.append(CodeElement(
                    type="function",
                    name=match.group(1),
                    content=match.group(0),
                    start_line=code[:match.start()].count("\n") + 1,
                    end_line=code[:match.end()].count("\n") + 1,
                    parameters=match.group(2).split(",") if match.group(2) else []
                ))
        
        return {
            "valid": True,
            "language": "java",
            "elements": [self._element_to_dict(e) for e in elements],
            "functions": [e.name for e in elements if e.type == "function"],
            "classes": [e.name for e in elements if e.type == "class"]
        }
    
    def _parse_generic(self, code: str) -> Dict[str, Any]:
        """Generic code parsing."""
        return {
            "valid": True,
            "language": "unknown",
            "elements": [],
            "line_count": len(code.split("\n")),
            "char_count": len(code)
        }
    
    def _element_to_dict(self, element: CodeElement) -> Dict[str, Any]:
        """Convert CodeElement to dictionary."""
        return {
            "type": element.type,
            "name": element.name,
            "start_line": element.start_line,
            "end_line": element.end_line,
            "docstring": element.docstring,
            "parameters": element.parameters
        }


# Singleton instance
_code_parser = None


def get_code_parser() -> CodeParser:
    """Get or create code parser singleton."""
    global _code_parser
    if _code_parser is None:
        _code_parser = CodeParser()
    return _code_parser
