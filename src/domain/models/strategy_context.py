"""
Strategy Context Model

Provides standardized context passed to strategies during execution.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.domain.models.market_data import OHLCV
from src.domain.models.position import Position
from src.domain.models.enums import Environment, MarketType, Timeframe


class AccountState(BaseModel):
    """Current account state provided to strategies."""
    
    balance: Decimal = Field(..., description="Available balance")
    equity: Decimal = Field(..., description="Total equity including positions")
    margin_used: Decimal = Field(default=Decimal("0"))
    margin_available: Decimal = Field(default=Decimal("0"))
    currency: str = Field(default="USDT")


class StrategyContext(BaseModel):
    """
    Context passed to strategy on each bar/tick.
    
    Contains everything a strategy needs to make trading decisions:
    - Current market data and indicators
    - Account state and open positions
    - Environment information
    
    Attributes:
        symbol: Current trading symbol
        market_type: Type of market
        timeframe: Current timeframe
        timestamp: Current bar/tick timestamp
        environment: Execution environment (backtest/paper/live)
        candles: Recent OHLCV data (most recent last)
        current_price: Latest price
        indicators: Pre-computed indicator values
        account: Current account state
        positions: Open positions for this symbol
        all_positions: All open positions
        metadata: Additional context data
    """
    
    # Symbol and market info
    symbol: str
    market_type: MarketType
    timeframe: Timeframe
    timestamp: datetime
    
    # Environment
    environment: Environment = Field(default=Environment.BACKTEST)
    
    # Market data
    candles: List[OHLCV] = Field(default_factory=list)
    current_price: Decimal = Field(..., gt=0)
    
    # Indicators (name -> value)
    indicators: Dict[str, Any] = Field(default_factory=dict)
    
    # Account state
    account: AccountState
    
    # Positions
    positions: List[Position] = Field(
        default_factory=list,
        description="Positions for this symbol"
    )
    all_positions: List[Position] = Field(
        default_factory=list,
        description="All open positions"
    )
    
    # Extensible metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def has_position(self) -> bool:
        """Check if there's an open position for this symbol."""
        return len(self.positions) > 0
    
    @property
    def current_candle(self) -> Optional[OHLCV]:
        """Get the most recent candle."""
        if self.candles:
            return self.candles[-1]
        return None
    
    @property
    def previous_candle(self) -> Optional[OHLCV]:
        """Get the previous candle."""
        if len(self.candles) >= 2:
            return self.candles[-2]
        return None
    
    def get_indicator(self, name: str, default: Any = None) -> Any:
        """Get indicator value by name."""
        return self.indicators.get(name, default)
    
    def get_candles(self, count: int) -> List[OHLCV]:
        """Get the last N candles."""
        return self.candles[-count:] if self.candles else []
    
    def get_closes(self, count: Optional[int] = None) -> List[Decimal]:
        """Get close prices from candles."""
        candles = self.candles[-count:] if count else self.candles
        return [c.close for c in candles]
    
    def get_highs(self, count: Optional[int] = None) -> List[Decimal]:
        """Get high prices from candles."""
        candles = self.candles[-count:] if count else self.candles
        return [c.high for c in candles]
    
    def get_lows(self, count: Optional[int] = None) -> List[Decimal]:
        """Get low prices from candles."""
        candles = self.candles[-count:] if count else self.candles
        return [c.low for c in candles]
