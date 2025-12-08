"""
Market Data Models

Represents market data (OHLCV candles and ticks).
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, computed_field

from src.domain.models.enums import MarketType, Timeframe


class OHLCV(BaseModel):
    """
    OHLCV (Open, High, Low, Close, Volume) candle data.
    
    Standard candlestick format used across all markets.
    
    Attributes:
        symbol: Trading pair/symbol
        market_type: Market type
        timeframe: Candle timeframe
        timestamp: Candle open time
        open: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        volume: Trading volume
    """
    
    symbol: str = Field(..., min_length=1)
    market_type: MarketType
    timeframe: Timeframe
    timestamp: datetime
    
    open: Decimal = Field(..., gt=0)
    high: Decimal = Field(..., gt=0)
    low: Decimal = Field(..., gt=0)
    close: Decimal = Field(..., gt=0)
    volume: Decimal = Field(..., ge=0)
    
    # Optional additional data
    trades_count: Optional[int] = Field(default=None)
    vwap: Optional[Decimal] = Field(default=None, description="Volume-weighted average price")
    
    @computed_field
    @property
    def is_bullish(self) -> bool:
        """Check if candle is bullish (close > open)."""
        return self.close > self.open
    
    @computed_field
    @property
    def is_bearish(self) -> bool:
        """Check if candle is bearish (close < open)."""
        return self.close < self.open
    
    @property
    def body_size(self) -> Decimal:
        """Calculate candle body size."""
        return abs(self.close - self.open)
    
    @property
    def upper_wick(self) -> Decimal:
        """Calculate upper wick size."""
        return self.high - max(self.open, self.close)
    
    @property
    def lower_wick(self) -> Decimal:
        """Calculate lower wick size."""
        return min(self.open, self.close) - self.low
    
    @property
    def range(self) -> Decimal:
        """Calculate full candle range (high - low)."""
        return self.high - self.low
    
    @property
    def midpoint(self) -> Decimal:
        """Calculate candle midpoint."""
        return (self.high + self.low) / 2
    
    @property
    def typical_price(self) -> Decimal:
        """Calculate typical price (HLC/3)."""
        return (self.high + self.low + self.close) / 3
    
    def __str__(self) -> str:
        direction = "↑" if self.is_bullish else "↓"
        return (
            f"OHLCV({self.symbol} {self.timeframe.value} {direction} "
            f"O:{self.open} H:{self.high} L:{self.low} C:{self.close})"
        )


class Tick(BaseModel):
    """
    Real-time tick/quote data.
    
    Represents a single price update from the market.
    
    Attributes:
        symbol: Trading pair/symbol
        market_type: Market type
        timestamp: Tick timestamp
        bid: Best bid price
        ask: Best ask price
        last: Last traded price
        volume: Volume at this tick (if available)
    """
    
    symbol: str = Field(..., min_length=1)
    market_type: MarketType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    bid: Decimal = Field(..., gt=0, description="Best bid price")
    ask: Decimal = Field(..., gt=0, description="Best ask price")
    last: Optional[Decimal] = Field(default=None, description="Last traded price")
    volume: Optional[Decimal] = Field(default=None, description="Volume at tick")
    
    @computed_field
    @property
    def spread(self) -> Decimal:
        """Calculate bid-ask spread."""
        return self.ask - self.bid
    
    @computed_field
    @property
    def spread_pct(self) -> float:
        """Calculate spread as percentage of mid price."""
        mid = self.mid_price
        if mid == 0:
            return 0.0
        return float(self.spread / mid) * 100
    
    @property
    def mid_price(self) -> Decimal:
        """Calculate mid price between bid and ask."""
        return (self.bid + self.ask) / 2
    
    def __str__(self) -> str:
        return f"Tick({self.symbol} bid:{self.bid} ask:{self.ask})"


class MarketInfo(BaseModel):
    """
    Static market/symbol information.
    
    Contains exchange-specific details about a trading pair.
    
    Attributes:
        symbol: Trading pair/symbol
        market_type: Market type
        base_asset: Base currency (e.g., "BTC" in BTCUSDT)
        quote_asset: Quote currency (e.g., "USDT" in BTCUSDT)
        price_precision: Decimal places for price
        quantity_precision: Decimal places for quantity
        min_quantity: Minimum order size
        max_quantity: Maximum order size
        min_notional: Minimum order value
    """
    
    symbol: str = Field(..., min_length=1)
    market_type: MarketType
    
    base_asset: str = Field(..., min_length=1)
    quote_asset: str = Field(..., min_length=1)
    
    # Precision
    price_precision: int = Field(default=8, ge=0)
    quantity_precision: int = Field(default=8, ge=0)
    
    # Limits
    min_quantity: Decimal = Field(default=Decimal("0"))
    max_quantity: Optional[Decimal] = Field(default=None)
    min_notional: Decimal = Field(default=Decimal("0"))
    
    # Trading status
    is_trading_enabled: bool = Field(default=True)
    
    def round_price(self, price: Decimal) -> Decimal:
        """Round price to valid precision."""
        return round(price, self.price_precision)
    
    def round_quantity(self, quantity: Decimal) -> Decimal:
        """Round quantity to valid precision."""
        return round(quantity, self.quantity_precision)
    
    def validate_quantity(self, quantity: Decimal) -> bool:
        """Check if quantity is within valid range."""
        if quantity < self.min_quantity:
            return False
        if self.max_quantity and quantity > self.max_quantity:
            return False
        return True
    
    def __str__(self) -> str:
        return f"MarketInfo({self.symbol}: {self.base_asset}/{self.quote_asset})"
