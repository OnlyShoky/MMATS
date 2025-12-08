"""
Tests for market data adapters.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.domain.models.market_data import OHLCV
from src.domain.models.enums import MarketType, Timeframe
from src.infrastructure.adapters.market_data import SimulatedMarketDataAdapter


class TestSimulatedMarketDataAdapter:
    """Tests for SimulatedMarketDataAdapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create adapter instance."""
        return SimulatedMarketDataAdapter()
    
    @pytest.fixture
    def sample_candles(self):
        """Create sample candle data."""
        base_time = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        candles = []
        
        for i in range(10):
            candles.append(OHLCV(
                symbol="BTC/USDT",
                market_type=MarketType.CRYPTO,
                timeframe=Timeframe.H1,
                timestamp=datetime(
                    2024, 1, 1, i, 0, tzinfo=timezone.utc
                ),
                open=Decimal(str(40000 + i * 100)),
                high=Decimal(str(40100 + i * 100)),
                low=Decimal(str(39900 + i * 100)),
                close=Decimal(str(40050 + i * 100)),
                volume=Decimal("1000"),
            ))
        
        return candles
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, adapter):
        """Test connection lifecycle."""
        assert adapter.is_connected is False
        
        await adapter.connect()
        assert adapter.is_connected is True
        
        await adapter.disconnect()
        assert adapter.is_connected is False
    
    def test_load_candles(self, adapter, sample_candles):
        """Test loading historical candles."""
        adapter.load_candles("BTC/USDT", sample_candles)
        
        assert "BTC/USDT" in adapter._candles
        assert len(adapter._candles["BTC/USDT"]) == 10
    
    def test_get_current_candle(self, adapter, sample_candles):
        """Test getting current candle."""
        adapter.load_candles("BTC/USDT", sample_candles)
        
        current = adapter.get_current_candle("BTC/USDT")
        assert current is not None
        assert current.open == Decimal("40000")
    
    def test_advance(self, adapter, sample_candles):
        """Test advancing through candles."""
        adapter.load_candles("BTC/USDT", sample_candles)
        
        # Initial position
        c1 = adapter.get_current_candle("BTC/USDT")
        assert c1.open == Decimal("40000")
        
        # Advance by 1
        c2 = adapter.advance("BTC/USDT", 1)
        assert c2.open == Decimal("40100")
        
        # Advance by 3
        c3 = adapter.advance("BTC/USDT", 3)
        assert c3.open == Decimal("40400")
    
    def test_reset(self, adapter, sample_candles):
        """Test resetting to beginning."""
        adapter.load_candles("BTC/USDT", sample_candles)
        
        adapter.advance("BTC/USDT", 5)
        adapter.reset()
        
        current = adapter.get_current_candle("BTC/USDT")
        assert current.open == Decimal("40000")
    
    @pytest.mark.asyncio
    async def test_get_historical_candles(self, adapter, sample_candles):
        """Test fetching historical candles."""
        adapter.load_candles("BTC/USDT", sample_candles)
        await adapter.connect()
        
        start = datetime(2024, 1, 1, 2, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 5, 0, tzinfo=timezone.utc)
        
        candles = await adapter.get_historical_candles(
            symbol="BTC/USDT",
            timeframe=Timeframe.H1,
            start=start,
            end=end,
        )
        
        assert len(candles) == 4  # Hours 2, 3, 4, 5
        assert candles[0].timestamp.hour == 2
        
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_get_latest_tick(self, adapter, sample_candles):
        """Test getting latest tick."""
        adapter.load_candles("BTC/USDT", sample_candles)
        await adapter.connect()
        
        tick = await adapter.get_latest_tick("BTC/USDT")
        
        assert tick.symbol == "BTC/USDT"
        assert tick.bid < tick.ask  # Spread exists
        assert tick.last == Decimal("40050")  # First candle close
        
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_get_market_info(self, adapter):
        """Test getting market info."""
        await adapter.connect()
        
        info = await adapter.get_market_info("BTC/USDT")
        
        assert info.symbol == "BTC/USDT"
        assert info.base_asset == "BTC"
        assert info.quote_asset == "USDT"
        
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_get_available_symbols(self, adapter, sample_candles):
        """Test getting available symbols."""
        adapter.load_candles("BTC/USDT", sample_candles)
        adapter.load_candles("ETH/USDT", sample_candles)
        await adapter.connect()
        
        symbols = await adapter.get_available_symbols()
        
        assert "BTC/USDT" in symbols
        assert "ETH/USDT" in symbols
        
        await adapter.disconnect()
