"""
Example: Running a Backtest

This script demonstrates how to run a backtest with the SMA Crossover strategy.
"""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from src.domain.models import OHLCV, MarketType, Timeframe
from src.strategies.examples.sma_crossover import SMACrossoverStrategy
from src.application import BacktestEngine, BacktestConfig, print_backtest_report


def generate_sample_data(
    symbol: str = "BTC/USDT",
    days: int = 100,
    start_price: float = 40000,
) -> list[OHLCV]:
    """
    Generate sample OHLCV data for testing.
    
    Creates a price series with some trend and noise.
    """
    import random
    random.seed(42)  # Reproducible
    
    candles = []
    price = start_price
    
    for day in range(days):
        for hour in range(24):
            # Add trend and noise
            trend = 0.0002 if day < days // 2 else -0.0001
            noise = random.uniform(-0.005, 0.005)
            
            price *= (1 + trend + noise)
            
            # Generate OHLC from price
            volatility = price * 0.005
            open_price = Decimal(str(round(price, 2)))
            high_price = Decimal(str(round(price + random.uniform(0, volatility), 2)))
            low_price = Decimal(str(round(price - random.uniform(0, volatility), 2)))
            close_price = Decimal(str(round(price + random.uniform(-volatility/2, volatility/2), 2)))
            
            candles.append(OHLCV(
                symbol=symbol,
                market_type=MarketType.CRYPTO,
                timeframe=Timeframe.H1,
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc) + 
                         __import__("datetime").timedelta(days=day, hours=hour),
                open=open_price,
                high=max(open_price, close_price, high_price),
                low=min(open_price, close_price, low_price),
                close=close_price,
                volume=Decimal(str(random.randint(100, 1000))),
            ))
    
    return candles


async def main():
    """Run example backtest."""
    print("=" * 60)
    print("  MMATS Backtest Example")
    print("=" * 60)
    
    # Generate sample data
    print("\n[1] Generating sample market data...")
    candles = generate_sample_data(days=90)
    print(f"    Generated {len(candles)} hourly candles")
    print(f"    Start price: ${candles[0].close}")
    print(f"    End price: ${candles[-1].close}")
    
    # Create strategy
    print("\n[2] Initializing SMA Crossover strategy...")
    strategy = SMACrossoverStrategy(fast_period=10, slow_period=50)
    print(f"    Strategy: {strategy.name} v{strategy.version}")
    print(f"    Fast SMA: 10, Slow SMA: 50")
    
    # Configure backtest
    print("\n[3] Configuring backtest...")
    config = BacktestConfig(
        strategy=strategy,
        symbol="BTC/USDT",
        timeframe=Timeframe.H1,
        start_date=candles[0].timestamp,
        end_date=candles[-1].timestamp,
        initial_capital=Decimal("10000"),
        commission_rate=Decimal("0.001"),
        slippage_rate=Decimal("0.0005"),
    )
    print(f"    Initial capital: ${config.initial_capital}")
    print(f"    Commission: {config.commission_rate * 100}%")
    print(f"    Slippage: {config.slippage_rate * 100}%")
    
    # Run backtest
    print("\n[4] Running backtest...")
    engine = BacktestEngine()
    result = await engine.run(config, candles)
    
    # Print results
    print_backtest_report(result)
    
    # Show some signals
    actionable_signals = [s for s in result.signals if s.is_actionable]
    print(f"Total signals generated: {len(result.signals)}")
    print(f"Actionable signals: {len(actionable_signals)}")
    
    if actionable_signals[:5]:
        print("\nFirst 5 actionable signals:")
        for signal in actionable_signals[:5]:
            print(f"  {signal.timestamp}: {signal.action.value} @ {signal.confidence:.0%}")


if __name__ == "__main__":
    asyncio.run(main())
