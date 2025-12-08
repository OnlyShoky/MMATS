"""
Tests for execution adapters.
"""

from decimal import Decimal

import pytest

from src.domain.models.order import Order
from src.domain.models.enums import MarketType, OrderSide, OrderType, OrderStatus
from src.infrastructure.adapters.execution import SimulatedExecutionAdapter


class TestSimulatedExecutionAdapter:
    """Tests for SimulatedExecutionAdapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create adapter with default settings."""
        return SimulatedExecutionAdapter(
            initial_balance=Decimal("10000"),
            currency="USDT",
            commission_rate=Decimal("0.001"),
            slippage_rate=Decimal("0.0005"),
        )
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, adapter):
        """Test connection lifecycle."""
        assert adapter.is_connected is False
        
        await adapter.connect()
        assert adapter.is_connected is True
        assert adapter.is_paper_trading is True
        
        await adapter.disconnect()
        assert adapter.is_connected is False
    
    @pytest.mark.asyncio
    async def test_initial_balance(self, adapter):
        """Test initial balance."""
        await adapter.connect()
        
        balance = await adapter.get_available_balance("USDT")
        assert balance == Decimal("10000")
        
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_place_market_buy_order(self, adapter):
        """Test placing a market buy order."""
        await adapter.connect()
        adapter.set_current_price("BTC/USDT", Decimal("40000"))
        
        order = Order(
            strategy_id="test_strategy",
            symbol="BTC/USDT",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
        )
        
        filled_order = await adapter.place_order(order)
        
        assert filled_order.status == OrderStatus.FILLED
        assert filled_order.filled_quantity == Decimal("0.1")
        assert filled_order.filled_price > Decimal("0")
        assert filled_order.commission > Decimal("0")
        
        # Check balance decreased
        balance = await adapter.get_available_balance("USDT")
        assert balance < Decimal("10000")
        
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_position_created_on_buy(self, adapter):
        """Test that position is created on buy order."""
        await adapter.connect()
        adapter.set_current_price("BTC/USDT", Decimal("40000"))
        
        order = Order(
            strategy_id="test_strategy",
            symbol="BTC/USDT",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
        )
        
        await adapter.place_order(order)
        
        positions = await adapter.get_positions("BTC/USDT")
        assert len(positions) == 1
        assert positions[0].symbol == "BTC/USDT"
        assert positions[0].quantity == Decimal("0.1")
        
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_close_position(self, adapter):
        """Test closing a position."""
        await adapter.connect()
        adapter.set_current_price("BTC/USDT", Decimal("40000"))
        
        # Open position
        buy_order = Order(
            strategy_id="test_strategy",
            symbol="BTC/USDT",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
        )
        await adapter.place_order(buy_order)
        
        # Price goes up
        adapter.set_current_price("BTC/USDT", Decimal("42000"))
        
        # Close position
        close_order = await adapter.close_position("BTC/USDT")
        
        assert close_order.status == OrderStatus.FILLED
        
        # Position should be gone
        positions = await adapter.get_positions()
        assert len(positions) == 0
        
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_insufficient_balance_rejection(self, adapter):
        """Test order rejection due to insufficient balance."""
        await adapter.connect()
        adapter.set_current_price("BTC/USDT", Decimal("40000"))
        
        # Try to buy more than we can afford
        order = Order(
            strategy_id="test_strategy",
            symbol="BTC/USDT",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1.0"),  # 1 BTC = $40,000, but we only have $10,000
        )
        
        filled_order = await adapter.place_order(order)
        
        assert filled_order.status == OrderStatus.REJECTED
        assert "Insufficient balance" in filled_order.error_message
        
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_reset(self, adapter):
        """Test resetting adapter state."""
        await adapter.connect()
        adapter.set_current_price("BTC/USDT", Decimal("40000"))
        
        # Place order
        order = Order(
            strategy_id="test_strategy",
            symbol="BTC/USDT",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
        )
        await adapter.place_order(order)
        
        # Reset
        adapter.reset()
        
        # Balance should be restored
        balance = await adapter.get_available_balance("USDT")
        assert balance == Decimal("10000")
        
        # Positions should be cleared
        positions = await adapter.get_positions()
        assert len(positions) == 0
        
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, adapter):
        """Test getting trading statistics."""
        await adapter.connect()
        adapter.set_current_price("BTC/USDT", Decimal("40000"))
        
        order = Order(
            strategy_id="test_strategy",
            symbol="BTC/USDT",
            market_type=MarketType.CRYPTO,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
        )
        await adapter.place_order(order)
        
        stats = adapter.get_statistics()
        
        assert stats["total_orders"] == 1
        assert stats["filled_orders"] == 1
        assert stats["open_positions"] == 1
        assert Decimal(stats["total_commission"]) > 0
        
        await adapter.disconnect()
