"""
Tests for backtesting engine.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.domain.models import OHLCV, MarketType, Timeframe
from src.application import BacktestEngine, BacktestConfig, IndicatorCalculator
from src.strategies.examples.sma_crossover import SMACrossoverStrategy


class TestIndicatorCalculator:
    """Tests for indicator calculator."""
    
    def test_sma(self):
        """Test SMA calculation."""
        prices = [Decimal(str(p)) for p in [10, 20, 30, 40, 50]]
        
        sma = IndicatorCalculator.sma(prices, 3)
        
        assert sma == Decimal("40")  # (30 + 40 + 50) / 3
    
    def test_sma_insufficient_data(self):
        """Test SMA with insufficient data."""
        prices = [Decimal("10"), Decimal("20")]
        
        sma = IndicatorCalculator.sma(prices, 5)
        
        assert sma is None
    
    def test_rsi(self):
        """Test RSI calculation."""
        # Prices going up should give RSI > 50
        prices = [Decimal(str(p)) for p in [40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
                                            50, 51, 52, 53, 54, 55]]
        
        rsi = IndicatorCalculator.rsi(prices, 14)
        
        assert rsi is not None
        assert rsi > Decimal("50")


@pytest.fixture
def sample_candles():
    """Generate sample candle data."""
    candles = []
    price = Decimal("40000")
    
    for i in range(100):
        # Simple trend: up first half, down second half
        if i < 50:
            price += Decimal("50")
        else:
            price -= Decimal("30")
        
        candles.append(OHLCV(
            symbol="BTC/USDT",
            market_type=MarketType.CRYPTO,
            timeframe=Timeframe.H1,
            timestamp=datetime(2024, 1, 1, i % 24, 0, tzinfo=timezone.utc),
            open=price - Decimal("10"),
            high=price + Decimal("20"),
            low=price - Decimal("20"),
            close=price,
            volume=Decimal("1000"),
        ))
    
    return candles


class TestBacktestEngine:
    """Tests for BacktestEngine."""
    
    @pytest.mark.asyncio
    async def test_run_backtest(self, sample_candles):
        """Test running a basic backtest."""
        strategy = SMACrossoverStrategy(fast_period=5, slow_period=20)
        
        config = BacktestConfig(
            strategy=strategy,
            symbol="BTC/USDT",
            timeframe=Timeframe.H1,
            start_date=sample_candles[0].timestamp,
            end_date=sample_candles[-1].timestamp,
            initial_capital=Decimal("10000"),
        )
        
        engine = BacktestEngine()
        result = await engine.run(config, sample_candles)
        
        assert result.strategy_name == "sma_crossover"
        assert result.symbol == "BTC/USDT"
        assert result.initial_capital == Decimal("10000")
        assert len(result.equity_curve) > 0
    
    @pytest.mark.asyncio
    async def test_backtest_generates_signals(self, sample_candles):
        """Test that backtest generates signals."""
        strategy = SMACrossoverStrategy(fast_period=5, slow_period=20)
        
        config = BacktestConfig(
            strategy=strategy,
            symbol="BTC/USDT",
            timeframe=Timeframe.H1,
            start_date=sample_candles[0].timestamp,
            end_date=sample_candles[-1].timestamp,
        )
        
        engine = BacktestEngine()
        result = await engine.run(config, sample_candles)
        
        assert len(result.signals) > 0
    
    @pytest.mark.asyncio
    async def test_backtest_with_empty_candles(self):
        """Test backtest with insufficient data."""
        strategy = SMACrossoverStrategy()
        
        config = BacktestConfig(
            strategy=strategy,
            symbol="BTC/USDT",
            timeframe=Timeframe.H1,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc),
        )
        
        engine = BacktestEngine()
        result = await engine.run(config, [])
        
        # Should complete without error even with empty data
        assert result.total_trades == 0
