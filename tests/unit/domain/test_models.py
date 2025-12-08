"""
Unit tests for domain models.
"""

from datetime import datetime
from decimal import Decimal

import pytest

from src.domain.models import (
    Signal,
    Order,
    Position,
    OHLCV,
    Tick,
    MarketInfo,
    MarketType,
    SignalAction,
    OrderSide,
    OrderType,
    OrderStatus,
    PositionSide,
    Timeframe,
)


class TestSignal:
    """Tests for Signal model."""
    
    def test_create_signal(self):
        """Test basic signal creation."""
        signal = Signal(
            strategy_id="momentum_v1",
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            action=SignalAction.BUY,
            position_size=0.5,
            confidence=0.75,
        )
        
        assert signal.strategy_id == "momentum_v1"
        assert signal.symbol == "BTCUSDT"
        assert signal.action == SignalAction.BUY
        assert signal.position_size == 0.5
        assert signal.confidence == 0.75
    
    def test_signal_is_actionable(self):
        """Test is_actionable property."""
        buy_signal = Signal(
            strategy_id="test",
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            action=SignalAction.BUY,
        )
        hold_signal = Signal(
            strategy_id="test",
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            action=SignalAction.HOLD,
        )
        
        assert buy_signal.is_actionable is True
        assert hold_signal.is_actionable is False
    
    def test_signal_risk_reward_ratio(self):
        """Test risk/reward ratio calculation."""
        signal = Signal(
            strategy_id="test",
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            action=SignalAction.BUY,
            entry_price=Decimal("100"),
            stop_loss=Decimal("95"),
            take_profit=Decimal("115"),
        )
        
        # Risk: 100-95=5, Reward: 115-100=15
        assert signal.risk_reward_ratio == 3.0


class TestOrder:
    """Tests for Order model."""
    
    def test_create_order(self):
        """Test basic order creation."""
        order = Order(
            strategy_id="momentum_v1",
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.01"),
        )
        
        assert order.strategy_id == "momentum_v1"
        assert order.symbol == "BTCUSDT"
        assert order.side == OrderSide.BUY
        assert order.status == OrderStatus.PENDING
    
    def test_order_lifecycle(self):
        """Test order status transitions."""
        order = Order(
            strategy_id="test",
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY,
            quantity=Decimal("1.0"),
        )
        
        # Initial state
        assert order.is_pending is True
        
        # Submit
        order.mark_submitted("BROKER123")
        assert order.is_active is True
        assert order.broker_order_id == "BROKER123"
        
        # Fill
        order.mark_filled(
            filled_quantity=Decimal("1.0"),
            filled_price=Decimal("42000"),
            commission=Decimal("0.42"),
        )
        assert order.is_filled is True
        assert order.fill_percentage == 100.0


class TestPosition:
    """Tests for Position model."""
    
    def test_create_position(self):
        """Test basic position creation."""
        position = Position(
            strategy_id="momentum_v1",
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            side=PositionSide.LONG,
            entry_price=Decimal("42000"),
            quantity=Decimal("0.1"),
            current_price=Decimal("43000"),
        )
        
        assert position.symbol == "BTCUSDT"
        assert position.side == PositionSide.LONG
        assert position.is_open is True
    
    def test_position_pnl_long(self):
        """Test P&L calculation for long position."""
        position = Position(
            strategy_id="test",
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            side=PositionSide.LONG,
            entry_price=Decimal("100"),
            quantity=Decimal("10"),
            current_price=Decimal("110"),
        )
        
        # Long: (110-100) * 10 = 100
        assert position.unrealized_pnl == Decimal("100")
        assert position.is_profitable is True
    
    def test_position_pnl_short(self):
        """Test P&L calculation for short position."""
        position = Position(
            strategy_id="test",
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            side=PositionSide.SHORT,
            entry_price=Decimal("100"),
            quantity=Decimal("10"),
            current_price=Decimal("90"),
        )
        
        # Short: (100-90) * 10 = 100
        assert position.unrealized_pnl == Decimal("100")
        assert position.is_profitable is True
    
    def test_position_close(self):
        """Test closing a position."""
        position = Position(
            strategy_id="test",
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            side=PositionSide.LONG,
            entry_price=Decimal("100"),
            quantity=Decimal("1"),
            current_price=Decimal("100"),
        )
        
        position.close(exit_price=Decimal("120"), reason="take_profit")
        
        assert position.is_closed is True
        assert position.exit_price == Decimal("120")
        assert position.exit_reason == "take_profit"


class TestOHLCV:
    """Tests for OHLCV model."""
    
    def test_create_ohlcv(self):
        """Test basic OHLCV creation."""
        candle = OHLCV(
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            timeframe=Timeframe.H1,
            timestamp=datetime.utcnow(),
            open=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("95"),
            close=Decimal("105"),
            volume=Decimal("1000"),
        )
        
        assert candle.symbol == "BTCUSDT"
        assert candle.is_bullish is True
        assert candle.range == Decimal("15")
    
    def test_ohlcv_bearish(self):
        """Test bearish candle detection."""
        candle = OHLCV(
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            timeframe=Timeframe.H1,
            timestamp=datetime.utcnow(),
            open=Decimal("105"),
            high=Decimal("110"),
            low=Decimal("95"),
            close=Decimal("100"),
            volume=Decimal("1000"),
        )
        
        assert candle.is_bearish is True
        assert candle.body_size == Decimal("5")


class TestTick:
    """Tests for Tick model."""
    
    def test_create_tick(self):
        """Test basic tick creation."""
        tick = Tick(
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            bid=Decimal("41995"),
            ask=Decimal("42005"),
        )
        
        assert tick.symbol == "BTCUSDT"
        assert tick.spread == Decimal("10")
        assert tick.mid_price == Decimal("42000")


class TestMarketInfo:
    """Tests for MarketInfo model."""
    
    def test_create_market_info(self):
        """Test basic market info creation."""
        info = MarketInfo(
            symbol="BTCUSDT",
            market_type=MarketType.CRYPTO,
            base_asset="BTC",
            quote_asset="USDT",
            price_precision=2,
            quantity_precision=4,
            min_quantity=Decimal("0.0001"),
        )
        
        assert info.symbol == "BTCUSDT"
        assert info.round_price(Decimal("42000.12345")) == Decimal("42000.12")
        assert info.validate_quantity(Decimal("0.001")) is True
        assert info.validate_quantity(Decimal("0.00001")) is False
