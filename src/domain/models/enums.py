"""
MMATS Domain Enumerations

Core enums used throughout the trading system.
"""

from enum import Enum, auto


class MarketType(str, Enum):
    """Supported market types."""
    CRYPTO = "crypto"
    FOREX = "forex"
    STOCK = "stock"


class OrderSide(str, Enum):
    """Order direction."""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order execution type."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(str, Enum):
    """Order lifecycle status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class SignalAction(str, Enum):
    """Trading signal actions."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"


class PositionSide(str, Enum):
    """Position direction."""
    LONG = "long"
    SHORT = "short"


class Timeframe(str, Enum):
    """Chart timeframes."""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


class Environment(str, Enum):
    """Execution environment."""
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


class TradingMode(str, Enum):
    """System operating mode."""
    ADVISORY = "advisory"
    OPERATOR = "operator"
    BACKTEST = "backtest"
