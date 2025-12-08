"""
MMATS Logging Configuration

Provides structured logging using structlog.
"""

from src.infrastructure.logging.logger import setup_logging, get_logger

__all__ = ["setup_logging", "get_logger"]
