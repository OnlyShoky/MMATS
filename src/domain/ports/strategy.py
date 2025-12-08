"""
Strategy Port (Interface)

Abstract interface for trading strategies.
All trading strategies must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models.signal import Signal
from src.domain.models.order import Order
from src.domain.models.strategy_context import StrategyContext
from src.domain.models.enums import MarketType, Timeframe


class StrategyMetadata:
    """Metadata describing a strategy."""
    
    def __init__(
        self,
        name: str,
        version: str,
        author: str = "Unknown",
        description: str = "",
        markets_supported: Optional[List[MarketType]] = None,
        timeframes_supported: Optional[List[Timeframe]] = None,
    ):
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.markets_supported = markets_supported or [MarketType.CRYPTO]
        self.timeframes_supported = timeframes_supported or [Timeframe.H1]


class RiskParams:
    """Strategy-specific risk parameters."""
    
    def __init__(
        self,
        max_position_size: float = 0.02,  # 2% of capital
        stop_loss_pct: float = 0.02,      # 2% stop-loss
        take_profit_pct: float = 0.04,    # 4% take-profit
        max_positions: int = 1,           # Max concurrent positions
        max_leverage: float = 1.0,        # No leverage by default
    ):
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_positions = max_positions
        self.max_leverage = max_leverage


class IndicatorConfig:
    """Configuration for an indicator."""
    
    def __init__(
        self,
        name: str,
        indicator_type: str,  # e.g., "SMA", "RSI", "MACD"
        params: Optional[dict] = None,
    ):
        self.name = name
        self.indicator_type = indicator_type
        self.params = params or {}


class IStrategy(ABC):
    """
    Abstract interface for trading strategies.
    
    All trading strategies must implement this interface to be loaded
    and executed by the Strategy Orchestration Engine.
    
    The interface follows a standardized pattern:
    1. Metadata: Define strategy properties
    2. Configuration: Declare required indicators and risk parameters
    3. Lifecycle: Initialize and cleanup
    4. Execution: Process bars and generate signals
    5. Event handling: React to order fills and rejections
    
    Example:
        class MomentumStrategy(IStrategy):
            def get_metadata(self) -> StrategyMetadata:
                return StrategyMetadata(
                    name="momentum_v1",
                    version="1.0.0",
                    author="MMATS",
                    markets_supported=[MarketType.CRYPTO],
                )
            
            def on_bar(self, context: StrategyContext) -> Signal:
                # Strategy logic here
                return Signal(...)
    """
    
    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------
    
    @abstractmethod
    def get_metadata(self) -> StrategyMetadata:
        """
        Return strategy metadata.
        
        Returns:
            StrategyMetadata with name, version, supported markets, etc.
        """
        pass
    
    @property
    def name(self) -> str:
        """Convenience property to get strategy name."""
        return self.get_metadata().name
    
    @property
    def version(self) -> str:
        """Convenience property to get strategy version."""
        return self.get_metadata().version
    
    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------
    
    @abstractmethod
    def get_required_indicators(self) -> List[IndicatorConfig]:
        """
        Declare indicators needed by this strategy.
        
        The orchestrator will compute these indicators and include them
        in the StrategyContext.
        
        Returns:
            List of IndicatorConfig objects
            
        Example:
            return [
                IndicatorConfig("sma_fast", "SMA", {"period": 10}),
                IndicatorConfig("sma_slow", "SMA", {"period": 50}),
                IndicatorConfig("rsi", "RSI", {"period": 14}),
            ]
        """
        pass
    
    @abstractmethod
    def get_risk_parameters(self) -> RiskParams:
        """
        Return default risk settings for this strategy.
        
        These can be overridden by global risk management settings.
        
        Returns:
            RiskParams object
        """
        pass
    
    def get_required_candles(self) -> int:
        """
        Return minimum number of candles needed for strategy to work.
        
        This ensures warm-up period is respected.
        Default is 100 candles.
        """
        return 100
    
    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------
    
    def initialize(self) -> None:
        """
        Called once when strategy is loaded.
        
        Override to perform initialization (load models, state, etc.)
        """
        pass
    
    def cleanup(self) -> None:
        """
        Called when strategy is unloaded.
        
        Override to perform cleanup (save state, close resources, etc.)
        """
        pass
    
    # -------------------------------------------------------------------------
    # Core Execution
    # -------------------------------------------------------------------------
    
    @abstractmethod
    def on_bar(self, context: StrategyContext) -> Signal:
        """
        Called on each new bar/candle.
        
        This is the main strategy method where trading logic lives.
        
        Args:
            context: Standardized input containing:
                - candles: Recent OHLCV data
                - indicators: Pre-computed indicator values
                - account: Balance and equity
                - positions: Current open positions
                - environment: BACKTEST | PAPER | LIVE
                
        Returns:
            Signal indicating recommended action (BUY/SELL/HOLD/CLOSE)
        """
        pass
    
    # -------------------------------------------------------------------------
    # Event Handlers (Optional)
    # -------------------------------------------------------------------------
    
    def on_order_filled(self, order: Order) -> None:
        """
        Called when an order from this strategy is filled.
        
        Override to track fills, update internal state, etc.
        
        Args:
            order: The filled order
        """
        pass
    
    def on_order_rejected(self, order: Order, reason: str) -> None:
        """
        Called when an order from this strategy is rejected.
        
        Override to handle rejections (adjust strategy, log, etc.)
        
        Args:
            order: The rejected order
            reason: Rejection reason
        """
        pass
    
    def on_position_closed(self, pnl: float, reason: str) -> None:
        """
        Called when a position from this strategy is closed.
        
        Override to track performance, adjust behavior, etc.
        
        Args:
            pnl: Realized profit/loss
            reason: Close reason (take_profit, stop_loss, manual, etc.)
        """
        pass
