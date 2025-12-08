"""
Tests for configuration settings.
"""

import pytest
from unittest.mock import patch
import os


class TestSettings:
    """Tests for Settings class."""
    
    def test_default_settings(self):
        """Verify default settings load correctly."""
        from src.infrastructure.config.settings import Settings
        
        settings = Settings()
        
        assert settings.environment == "development"
        assert settings.debug is True
        assert settings.mode == "advisory"
    
    def test_enabled_markets_list(self):
        """Verify markets_enabled parses correctly."""
        from src.infrastructure.config.settings import Settings
        
        settings = Settings(markets_enabled="crypto,forex,stock")
        
        assert settings.enabled_markets_list == ["crypto", "forex", "stock"]
    
    def test_is_production(self):
        """Verify production environment detection."""
        from src.infrastructure.config.settings import Settings
        
        dev_settings = Settings(environment="development")
        assert dev_settings.is_production is False
        
        prod_settings = Settings(environment="production")
        assert prod_settings.is_production is True
    
    def test_is_live_trading(self):
        """Verify live trading detection."""
        from src.infrastructure.config.settings import Settings
        
        # Advisory mode = no live trading
        advisory = Settings(mode="advisory", environment="production")
        assert advisory.is_live_trading is False
        
        # Operator + development = no live trading
        operator_dev = Settings(mode="operator", environment="development")
        assert operator_dev.is_live_trading is False
        
        # Operator + production = live trading
        live = Settings(mode="operator", environment="production")
        assert live.is_live_trading is True
