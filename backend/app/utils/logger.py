"""Logging configuration for the application."""
import logging
import sys
from typing import Optional

from app.config import settings


def setup_logger(
    name: str = "app",
    level: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with standard formatting.
    
    Args:
        name: Logger name
        level: Log level (uses settings.LOG_LEVEL if not provided)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        # Already configured
        return logger
    
    log_level = getattr(logging, (level or settings.LOG_LEVEL).upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger


# Pre-configured loggers
app_logger = setup_logger("app")
api_logger = setup_logger("api")
rag_logger = setup_logger("rag")
generation_logger = setup_logger("generation")
validation_logger = setup_logger("validation")


def log_request(method: str, path: str, status: int, duration_ms: float) -> None:
    """Log an API request."""
    api_logger.info(f"{method} {path} - {status} ({duration_ms:.2f}ms)")


def log_search(query: str, course_id: str, results: int, web_used: bool) -> None:
    """Log a search operation."""
    web_str = " [+web]" if web_used else ""
    rag_logger.info(f"Search{web_str}: '{query[:50]}...' in {course_id} -> {results} results")


def log_generation(gen_type: str, topic: str, duration: float, validated: bool) -> None:
    """Log a generation operation."""
    val_str = " [validated]" if validated else ""
    generation_logger.info(f"Generated {gen_type}{val_str}: '{topic[:50]}...' ({duration:.2f}s)")


def log_validation(content_type: str, status: str, score: float) -> None:
    """Log a validation result."""
    validation_logger.info(f"Validation {content_type}: {status} (score: {score:.2f})")


def log_error(logger_name: str, error: Exception, context: str = "") -> None:
    """Log an error with context."""
    logger = logging.getLogger(logger_name)
    context_str = f" [{context}]" if context else ""
    logger.error(f"Error{context_str}: {type(error).__name__}: {str(error)}")
