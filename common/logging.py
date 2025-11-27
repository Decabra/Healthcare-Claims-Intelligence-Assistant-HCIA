"""
Structured logging configuration
Enterprise-grade logging setup
"""

import logging
import sys
import structlog
from typing import Any


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if _is_production() else structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _is_production() -> bool:
    """Check if running in production environment"""
    import os
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a configured logger instance
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)

