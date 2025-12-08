"""
MMATS Settings Management

Pydantic-based settings loaded from environment variables and .env files.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Environment variables are prefixed with MMATS_ for the main settings.
    Broker credentials use their own prefixes (BINANCE_, OANDA_, etc.)
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,  # Allow both field name and alias
    )
    
    # Application Settings
    environment: str = Field(
        default="development",
        alias="MMATS_ENV",
        description="Environment: development, staging, production"
    )
    debug: bool = Field(
        default=True,
        alias="MMATS_DEBUG",
        description="Enable debug mode"
    )
    log_level: str = Field(
        default="INFO",
        alias="MMATS_LOG_LEVEL",
        description="Log level: DEBUG, INFO, WARNING, ERROR"
    )
    
    # Trading Mode
    mode: str = Field(
        default="advisory",
        alias="MMATS_MODE",
        description="Trading mode: advisory, operator, backtest"
    )
    
    # Market Configuration
    markets_enabled: str = Field(
        default="crypto",
        alias="MMATS_MARKETS_ENABLED",
        description="Comma-separated list of enabled markets"
    )
    default_timeframe: str = Field(
        default="1h",
        alias="MMATS_DEFAULT_TIMEFRAME",
        description="Default chart timeframe"
    )
    
    # Database
    database_url: str = Field(
        default="sqlite:///./data/mmats.db",
        alias="DATABASE_URL",
        description="Database connection URL"
    )
    
    # Risk Management
    risk_max_position_pct: float = Field(
        default=2.0,
        alias="RISK_MAX_POSITION_PCT",
        description="Maximum position size as % of capital"
    )
    risk_max_drawdown_pct: float = Field(
        default=15.0,
        alias="RISK_MAX_DRAWDOWN_PCT",
        description="Maximum allowed drawdown %"
    )
    risk_daily_loss_limit_pct: float = Field(
        default=3.0,
        alias="RISK_DAILY_LOSS_LIMIT_PCT",
        description="Maximum daily loss %"
    )
    risk_max_leverage: float = Field(
        default=3.0,
        alias="RISK_MAX_LEVERAGE",
        description="Maximum leverage allowed"
    )
    
    @property
    def enabled_markets_list(self) -> List[str]:
        """Parse comma-separated markets into a list."""
        return [m.strip().lower() for m in self.markets_enabled.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_live_trading(self) -> bool:
        """Check if live trading is enabled (operator mode + production)."""
        return self.mode.lower() == "operator" and self.is_production


class BinanceSettings(BaseSettings):
    """Binance exchange settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    api_key: str = Field(default="", alias="BINANCE_API_KEY")
    api_secret: str = Field(default="", alias="BINANCE_API_SECRET")
    testnet: bool = Field(default=True, alias="BINANCE_TESTNET")


class OandaSettings(BaseSettings):
    """OANDA broker settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    api_key: str = Field(default="", alias="OANDA_API_KEY")
    account_id: str = Field(default="", alias="OANDA_ACCOUNT_ID")
    practice: bool = Field(default=True, alias="OANDA_PRACTICE")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


@lru_cache()
def get_binance_settings() -> BinanceSettings:
    """Get cached Binance settings."""
    return BinanceSettings()


@lru_cache()
def get_oanda_settings() -> OandaSettings:
    """Get cached OANDA settings."""
    return OandaSettings()
