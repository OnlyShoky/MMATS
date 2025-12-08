"""
Unit tests for domain models and enums.
"""

import pytest

from src.domain.models.enums import (
    MarketType,
    OrderSide,
    OrderType,
    OrderStatus,
    SignalAction,
    Timeframe,
    Environment,
    TradingMode,
)


class TestMarketType:
    """Tests for MarketType enum."""
    
    def test_market_types_exist(self):
        """Verify all market types are defined."""
        assert MarketType.CRYPTO == "crypto"
        assert MarketType.FOREX == "forex"
        assert MarketType.STOCK == "stock"
    
    def test_market_type_values(self):
        """Verify market types can be used as strings."""
        assert str(MarketType.CRYPTO) == "MarketType.CRYPTO"
        assert MarketType.CRYPTO.value == "crypto"


class TestOrderEnums:
    """Tests for order-related enums."""
    
    def test_order_sides(self):
        """Verify order sides."""
        assert OrderSide.BUY == "buy"
        assert OrderSide.SELL == "sell"
    
    def test_order_types(self):
        """Verify order types."""
        assert OrderType.MARKET == "market"
        assert OrderType.LIMIT == "limit"
        assert OrderType.STOP_LOSS == "stop_loss"
        assert OrderType.TAKE_PROFIT == "take_profit"
    
    def test_order_statuses(self):
        """Verify all order statuses exist."""
        statuses = [s.value for s in OrderStatus]
        assert "pending" in statuses
        assert "filled" in statuses
        assert "cancelled" in statuses


class TestSignalAction:
    """Tests for SignalAction enum."""
    
    def test_signal_actions(self):
        """Verify signal actions."""
        assert SignalAction.BUY == "buy"
        assert SignalAction.SELL == "sell"
        assert SignalAction.HOLD == "hold"
        assert SignalAction.CLOSE == "close"


class TestTimeframe:
    """Tests for Timeframe enum."""
    
    def test_timeframes(self):
        """Verify timeframe values."""
        assert Timeframe.M1 == "1m"
        assert Timeframe.H1 == "1h"
        assert Timeframe.D1 == "1d"


class TestEnvironment:
    """Tests for Environment enum."""
    
    def test_environments(self):
        """Verify environment values."""
        assert Environment.BACKTEST == "backtest"
        assert Environment.PAPER == "paper"
        assert Environment.LIVE == "live"


class TestTradingMode:
    """Tests for TradingMode enum."""
    
    def test_trading_modes(self):
        """Verify trading mode values."""
        assert TradingMode.ADVISORY == "advisory"
        assert TradingMode.OPERATOR == "operator"
        assert TradingMode.BACKTEST == "backtest"
