"""
MMATS Test Suite

Test fixtures and shared utilities.
"""

import pytest


@pytest.fixture
def sample_settings():
    """Provide sample settings for tests."""
    from src.infrastructure.config.settings import Settings
    
    return Settings(
        environment="test",
        debug=True,
        log_level="DEBUG",
        mode="backtest",
    )
