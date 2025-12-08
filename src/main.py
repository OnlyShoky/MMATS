"""
MMATS Main Entry Point

This module provides the main entry point for the MMATS trading system.
"""

import sys
from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging.logger import setup_logging, get_logger


def main() -> int:
    """
    Main entry point for MMATS.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    # Load settings
    settings = get_settings()
    
    # Setup logging
    setup_logging(settings.log_level, settings.debug)
    logger = get_logger(__name__)
    
    # Log startup
    logger.info(
        "mmats_startup",
        version="0.1.0",
        environment=settings.environment,
        mode=settings.mode,
        debug=settings.debug,
    )
    
    print(f"MMATS v0.1.0 - System initialized")
    print(f"Environment: {settings.environment}")
    print(f"Mode: {settings.mode}")
    print(f"Debug: {settings.debug}")
    
    # TODO: Initialize core components based on mode
    # - Advisory Mode: Generate signals only
    # - Operator Mode: Execute trades
    # - Backtest Mode: Historical simulation
    
    logger.info("mmats_ready", status="initialized")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
