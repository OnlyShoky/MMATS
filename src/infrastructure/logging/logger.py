"""
MMATS Structured Logging

Provides structured JSON logging with context support.
"""

import logging
import sys
from typing import Any

import structlog


def setup_logging(log_level: str = "INFO", debug: bool = False) -> None:
    """
    Configure structlog for structured logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        debug: Enable debug mode (pretty printing in console)
    """
    # Set the log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    
    if debug:
        # Development: Pretty console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Also configure standard logging for libraries
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def with_context(**context: Any) -> None:
    """
    Add context to all subsequent log messages in the current context.
    
    Args:
        **context: Key-value pairs to add to log context
        
    Example:
        with_context(strategy_id="momentum_v1", symbol="BTCUSDT")
        logger.info("Processing signal")  # Will include strategy_id and symbol
    """
    structlog.contextvars.bind_contextvars(**context)


def clear_context() -> None:
    """Clear all context variables."""
    structlog.contextvars.clear_contextvars()
