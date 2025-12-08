"""
Simulated Market Data Adapter

Provides simulated market data for backtesting and testing.
"""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable, Dict, List, Optional

from src.domain.ports.market_data_provider import IMarketDataProvider
from src.domain.models.market_data import OHLCV, Tick, MarketInfo
from src.domain.models.enums import MarketType, Timeframe
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class SimulatedMarketDataAdapter(IMarketDataProvider):
    """
    Simulated market data provider for backtesting and testing.
    
    Can be loaded with historical data and replayed for backtesting,
    or generate random data for unit tests.
    """
    
    def __init__(self):
        self._connected = False
        self._candles: Dict[str, List[OHLCV]] = {}  # symbol -> candles
        self._current_index: Dict[str, int] = {}    # symbol -> current position
        self._market_info: Dict[str, MarketInfo] = {}
        self._subscriptions: Dict[str, asyncio.Task] = {}
    
    @property
    def provider_name(self) -> str:
        return "simulated"
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    # -------------------------------------------------------------------------
    # Data Loading (for backtesting)
    # -------------------------------------------------------------------------
    
    def load_candles(self, symbol: str, candles: List[OHLCV]) -> None:
        """
        Load historical candles for backtesting.
        
        Args:
            symbol: Trading symbol
            candles: List of OHLCV candles (chronological order)
        """
        self._candles[symbol] = sorted(candles, key=lambda c: c.timestamp)
        self._current_index[symbol] = 0
        logger.info(
            "simulated_candles_loaded",
            symbol=symbol,
            count=len(candles),
        )
    
    def set_market_info(self, info: MarketInfo) -> None:
        """Set market info for a symbol."""
        self._market_info[info.symbol] = info
    
    def reset(self) -> None:
        """Reset all data positions to the beginning."""
        for symbol in self._current_index:
            self._current_index[symbol] = 0
    
    def advance(self, symbol: str, steps: int = 1) -> Optional[OHLCV]:
        """
        Advance the simulation by N candles.
        
        Returns the new current candle or None if at end.
        """
        if symbol not in self._candles:
            return None
        
        candles = self._candles[symbol]
        current = self._current_index.get(symbol, 0)
        new_index = min(current + steps, len(candles) - 1)
        self._current_index[symbol] = new_index
        
        return candles[new_index] if new_index < len(candles) else None
    
    def get_current_candle(self, symbol: str) -> Optional[OHLCV]:
        """Get the current candle for a symbol."""
        if symbol not in self._candles:
            return None
        
        candles = self._candles[symbol]
        index = self._current_index.get(symbol, 0)
        
        return candles[index] if index < len(candles) else None
    
    # -------------------------------------------------------------------------
    # IMarketDataProvider Implementation
    # -------------------------------------------------------------------------
    
    async def connect(self) -> None:
        """Simulated connection."""
        self._connected = True
        logger.info("simulated_provider_connected")
    
    async def disconnect(self) -> None:
        """Simulated disconnection."""
        for task in self._subscriptions.values():
            task.cancel()
        self._subscriptions.clear()
        self._connected = False
        logger.info("simulated_provider_disconnected")
    
    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[OHLCV]:
        """Return candles from loaded data."""
        if symbol not in self._candles:
            return []
        
        candles = self._candles[symbol]
        
        # Filter by timeframe and date range
        filtered = [
            c for c in candles
            if c.timeframe == timeframe
            and c.timestamp >= start
            and (end is None or c.timestamp <= end)
        ]
        
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    async def get_latest_tick(self, symbol: str) -> Tick:
        """Get tick from current candle."""
        candle = self.get_current_candle(symbol)
        
        if not candle:
            raise ValueError(f"No data for symbol: {symbol}")
        
        # Simulate bid/ask spread (0.1%)
        price = candle.close
        spread = price * Decimal("0.0005")
        
        return Tick(
            symbol=symbol,
            market_type=MarketType.CRYPTO,
            timestamp=candle.timestamp,
            bid=price - spread,
            ask=price + spread,
            last=price,
            volume=candle.volume,
        )
    
    async def subscribe_to_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        callback: Callable[[OHLCV], None],
    ) -> str:
        """Subscribe to candle updates (simulated)."""
        sub_id = f"sim_candles_{symbol}_{timeframe.value}"
        
        async def emit_candles():
            while True:
                candle = self.get_current_candle(symbol)
                if candle and candle.timeframe == timeframe:
                    callback(candle)
                await asyncio.sleep(0.1)  # Fast for testing
        
        task = asyncio.create_task(emit_candles())
        self._subscriptions[sub_id] = task
        
        return sub_id
    
    async def subscribe_to_ticks(
        self,
        symbol: str,
        callback: Callable[[Tick], None],
    ) -> str:
        """Subscribe to tick updates (simulated)."""
        sub_id = f"sim_ticks_{symbol}"
        
        async def emit_ticks():
            while True:
                try:
                    tick = await self.get_latest_tick(symbol)
                    callback(tick)
                except ValueError:
                    pass
                await asyncio.sleep(0.1)
        
        task = asyncio.create_task(emit_ticks())
        self._subscriptions[sub_id] = task
        
        return sub_id
    
    async def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from updates."""
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id].cancel()
            del self._subscriptions[subscription_id]
    
    async def get_market_info(self, symbol: str) -> MarketInfo:
        """Get market info (must be pre-loaded or generate default)."""
        if symbol in self._market_info:
            return self._market_info[symbol]
        
        # Generate default market info
        parts = symbol.replace("/", "").split("USDT")
        base = parts[0] if parts else symbol[:3]
        
        return MarketInfo(
            symbol=symbol,
            market_type=MarketType.CRYPTO,
            base_asset=base,
            quote_asset="USDT",
            price_precision=8,
            quantity_precision=8,
            min_quantity=Decimal("0.00001"),
            min_notional=Decimal("10"),
        )
    
    async def get_available_symbols(self) -> List[str]:
        """Get loaded symbols."""
        return list(self._candles.keys())
    
    async def is_market_open(self, symbol: str) -> bool:
        """Simulated market is always open."""
        return True
