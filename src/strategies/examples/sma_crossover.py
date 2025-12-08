"""
SMA Crossover Example Strategy

A simple moving average crossover strategy for demonstration.
Buys when fast SMA crosses above slow SMA, sells on opposite.
"""

from decimal import Decimal
from typing import List

from src.domain.ports.strategy import (
    IStrategy,
    StrategyMetadata,
    RiskParams,
    IndicatorConfig,
)
from src.domain.models.signal import Signal
from src.domain.models.strategy_context import StrategyContext
from src.domain.models.enums import MarketType, SignalAction, Timeframe


class SMACrossoverStrategy(IStrategy):
    """
    Simple Moving Average Crossover Strategy.
    
    This is an example strategy that demonstrates the IStrategy interface.
    
    Logic:
    - BUY when fast SMA crosses above slow SMA
    - SELL (close) when fast SMA crosses below slow SMA
    - HOLD otherwise
    
    Parameters:
    - fast_period: Period for fast SMA (default: 10)
    - slow_period: Period for slow SMA (default: 50)
    """
    
    def __init__(
        self,
        fast_period: int = 10,
        slow_period: int = 50,
    ):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self._last_crossover = None  # Track last crossover direction
    
    def get_metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            name="sma_crossover",
            version="1.0.0",
            author="MMATS",
            description="Simple SMA crossover strategy",
            markets_supported=[MarketType.CRYPTO, MarketType.FOREX, MarketType.STOCK],
            timeframes_supported=[
                Timeframe.M15,
                Timeframe.M30,
                Timeframe.H1,
                Timeframe.H4,
                Timeframe.D1,
            ],
        )
    
    def get_required_indicators(self) -> List[IndicatorConfig]:
        return [
            IndicatorConfig(
                name="sma_fast",
                indicator_type="SMA",
                params={"period": self.fast_period},
            ),
            IndicatorConfig(
                name="sma_slow",
                indicator_type="SMA",
                params={"period": self.slow_period},
            ),
        ]
    
    def get_risk_parameters(self) -> RiskParams:
        return RiskParams(
            max_position_size=0.02,   # 2% of capital per trade
            stop_loss_pct=0.02,       # 2% stop-loss
            take_profit_pct=0.04,     # 4% take-profit (2:1 R:R)
            max_positions=1,          # Only one position at a time
            max_leverage=1.0,         # No leverage
        )
    
    def get_required_candles(self) -> int:
        # Need enough candles to compute the slow SMA
        return self.slow_period + 10
    
    def initialize(self) -> None:
        """Reset strategy state."""
        self._last_crossover = None
    
    def on_bar(self, context: StrategyContext) -> Signal:
        """
        Process a new bar and generate trading signal.
        
        Args:
            context: Market data and account state
            
        Returns:
            Trading signal
        """
        # Get indicator values
        sma_fast = context.get_indicator("sma_fast")
        sma_slow = context.get_indicator("sma_slow")
        
        # Default signal (HOLD)
        signal = Signal(
            strategy_id=self.name,
            symbol=context.symbol,
            market_type=context.market_type,
            action=SignalAction.HOLD,
            timeframe=context.timeframe,
            confidence=0.0,
        )
        
        # Need both indicators
        if sma_fast is None or sma_slow is None:
            return signal
        
        # Determine crossover
        is_bullish = sma_fast > sma_slow
        is_bearish = sma_fast < sma_slow
        
        # Detect crossover (change from previous state)
        crossover_bullish = is_bullish and self._last_crossover == "bearish"
        crossover_bearish = is_bearish and self._last_crossover == "bullish"
        
        # Update last crossover state
        if is_bullish:
            self._last_crossover = "bullish"
        elif is_bearish:
            self._last_crossover = "bearish"
        
        # Generate signal based on crossover
        if crossover_bullish and not context.has_position:
            # Bullish crossover - BUY
            signal = Signal(
                strategy_id=self.name,
                symbol=context.symbol,
                market_type=context.market_type,
                action=SignalAction.BUY,
                position_size=0.02,  # 2% of capital
                entry_price=context.current_price,
                stop_loss=context.current_price * Decimal("0.98"),   # -2%
                take_profit=context.current_price * Decimal("1.04"), # +4%
                confidence=0.7,
                timeframe=context.timeframe,
                metadata={
                    "sma_fast": float(sma_fast),
                    "sma_slow": float(sma_slow),
                    "reason": "bullish_crossover",
                },
            )
        elif crossover_bearish and context.has_position:
            # Bearish crossover - CLOSE position
            signal = Signal(
                strategy_id=self.name,
                symbol=context.symbol,
                market_type=context.market_type,
                action=SignalAction.CLOSE,
                confidence=0.7,
                timeframe=context.timeframe,
                metadata={
                    "sma_fast": float(sma_fast),
                    "sma_slow": float(sma_slow),
                    "reason": "bearish_crossover",
                },
            )
        
        return signal
    
    def on_order_filled(self, order) -> None:
        """Log when orders are filled."""
        pass  # Could track fill statistics here
    
    def on_position_closed(self, pnl: float, reason: str) -> None:
        """Track closed positions."""
        pass  # Could track win rate, average P&L, etc.
