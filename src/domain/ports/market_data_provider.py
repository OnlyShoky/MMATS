"""
Market Data Provider Port (Interface)

Abstract interface for market data adapters.
All market data providers (Binance, OANDA, etc.) must implement this interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator, Callable, List, Optional

from src.domain.models.market_data import OHLCV, Tick, MarketInfo
from src.domain.models.enums import Timeframe


class IMarketDataProvider(ABC):
    """
    Abstract interface for market data providers.
    
    This port defines the contract that all market data adapters must implement.
    The core system depends only on this interface, not on specific implementations.
    
    Implementations:
        - BinanceMarketDataAdapter (crypto)
        - OandaMarketDataAdapter (forex)
        - IBMarketDataAdapter (stocks)
        - SimulatedMarketDataAdapter (backtesting)
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider (e.g., 'binance', 'oanda')."""
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if provider is connected and ready."""
        pass
    
    # -------------------------------------------------------------------------
    # Connection Management
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the data provider.
        
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the data provider."""
        pass
    
    # -------------------------------------------------------------------------
    # Historical Data
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[OHLCV]:
        """
        Fetch historical OHLCV candles.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            timeframe: Candle timeframe
            start: Start datetime (inclusive)
            end: End datetime (inclusive), defaults to now
            limit: Maximum number of candles to fetch
            
        Returns:
            List of OHLCV candles, ordered by timestamp ascending
            
        Raises:
            ValueError: If symbol is invalid
            ConnectionError: If provider is not connected
        """
        pass
    
    # -------------------------------------------------------------------------
    # Real-time Data
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def get_latest_tick(self, symbol: str) -> Tick:
        """
        Get the latest tick/quote for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Latest Tick data
        """
        pass
    
    @abstractmethod
    async def subscribe_to_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        callback: Callable[[OHLCV], None],
    ) -> str:
        """
        Subscribe to real-time candle updates.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle timeframe
            callback: Function called on each new candle
            
        Returns:
            Subscription ID for unsubscribing
        """
        pass
    
    @abstractmethod
    async def subscribe_to_ticks(
        self,
        symbol: str,
        callback: Callable[[Tick], None],
    ) -> str:
        """
        Subscribe to real-time tick updates.
        
        Args:
            symbol: Trading symbol
            callback: Function called on each new tick
            
        Returns:
            Subscription ID for unsubscribing
        """
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> None:
        """
        Unsubscribe from a data stream.
        
        Args:
            subscription_id: ID returned from subscribe methods
        """
        pass
    
    # -------------------------------------------------------------------------
    # Market Information
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def get_market_info(self, symbol: str) -> MarketInfo:
        """
        Get static market information for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            MarketInfo with precision, limits, etc.
        """
        pass
    
    @abstractmethod
    async def get_available_symbols(self) -> List[str]:
        """
        Get list of all available trading symbols.
        
        Returns:
            List of symbol strings
        """
        pass
    
    @abstractmethod
    async def is_market_open(self, symbol: str) -> bool:
        """
        Check if the market is currently open for trading.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if market is open
        """
        pass
