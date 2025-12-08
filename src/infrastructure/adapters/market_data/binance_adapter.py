"""
Binance Market Data Adapter

Implements IMarketDataProvider for Binance exchange using ccxt.
"""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable, Dict, List, Optional

import ccxt.async_support as ccxt

from src.domain.ports.market_data_provider import IMarketDataProvider
from src.domain.models.market_data import OHLCV, Tick, MarketInfo
from src.domain.models.enums import MarketType, Timeframe
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


# Timeframe mapping from our enum to ccxt format
TIMEFRAME_MAP = {
    Timeframe.M1: "1m",
    Timeframe.M5: "5m",
    Timeframe.M15: "15m",
    Timeframe.M30: "30m",
    Timeframe.H1: "1h",
    Timeframe.H4: "4h",
    Timeframe.D1: "1d",
    Timeframe.W1: "1w",
}


class BinanceMarketDataAdapter(IMarketDataProvider):
    """
    Binance market data provider using ccxt library.
    
    Supports:
    - Historical OHLCV data fetching
    - Real-time tick data
    - Market information
    
    Note: For production, use Binance's WebSocket API for real-time data.
    This implementation uses REST API polling for simplicity.
    """
    
    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        testnet: bool = True,
    ):
        """
        Initialize Binance adapter.
        
        Args:
            api_key: Binance API key (optional for market data)
            api_secret: Binance API secret (optional for market data)
            testnet: Use testnet if True
        """
        self._api_key = api_key
        self._api_secret = api_secret
        self._testnet = testnet
        self._exchange: Optional[ccxt.binance] = None
        self._subscriptions: Dict[str, asyncio.Task] = {}
        self._market_info_cache: Dict[str, MarketInfo] = {}
    
    @property
    def provider_name(self) -> str:
        return "binance"
    
    @property
    def is_connected(self) -> bool:
        return self._exchange is not None
    
    # -------------------------------------------------------------------------
    # Connection Management
    # -------------------------------------------------------------------------
    
    async def connect(self) -> None:
        """Connect to Binance exchange."""
        try:
            options = {
                "enableRateLimit": True,
                "rateLimit": 50,  # ms between requests
            }
            
            if self._testnet:
                options["sandbox"] = True
            
            self._exchange = ccxt.binance({
                "apiKey": self._api_key or None,
                "secret": self._api_secret or None,
                "options": options,
            })
            
            if self._testnet:
                self._exchange.set_sandbox_mode(True)
            
            # Load markets to populate symbols
            await self._exchange.load_markets()
            
            logger.info(
                "binance_connected",
                testnet=self._testnet,
                symbols_count=len(self._exchange.symbols),
            )
            
        except Exception as e:
            logger.error("binance_connection_failed", error=str(e))
            raise ConnectionError(f"Failed to connect to Binance: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from Binance exchange."""
        # Cancel all subscriptions
        for sub_id, task in self._subscriptions.items():
            task.cancel()
        self._subscriptions.clear()
        
        if self._exchange:
            await self._exchange.close()
            self._exchange = None
            logger.info("binance_disconnected")
    
    # -------------------------------------------------------------------------
    # Historical Data
    # -------------------------------------------------------------------------
    
    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[OHLCV]:
        """Fetch historical OHLCV candles from Binance."""
        if not self._exchange:
            raise ConnectionError("Not connected to Binance")
        
        tf_str = TIMEFRAME_MAP.get(timeframe, "1h")
        since = int(start.timestamp() * 1000)  # Binance uses milliseconds
        
        try:
            # Binance max limit is 1000
            fetch_limit = min(limit or 1000, 1000)
            
            ohlcv_data = await self._exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=tf_str,
                since=since,
                limit=fetch_limit,
            )
            
            candles = []
            for candle in ohlcv_data:
                timestamp_ms, o, h, l, c, v = candle[:6]
                
                # Filter by end date if provided
                candle_time = datetime.fromtimestamp(
                    timestamp_ms / 1000, tz=timezone.utc
                )
                if end and candle_time > end:
                    break
                
                candles.append(OHLCV(
                    symbol=symbol,
                    market_type=MarketType.CRYPTO,
                    timeframe=timeframe,
                    timestamp=candle_time,
                    open=Decimal(str(o)),
                    high=Decimal(str(h)),
                    low=Decimal(str(l)),
                    close=Decimal(str(c)),
                    volume=Decimal(str(v)),
                ))
            
            logger.debug(
                "binance_candles_fetched",
                symbol=symbol,
                timeframe=tf_str,
                count=len(candles),
            )
            
            return candles
            
        except Exception as e:
            logger.error(
                "binance_fetch_candles_failed",
                symbol=symbol,
                error=str(e),
            )
            raise
    
    # -------------------------------------------------------------------------
    # Real-time Data
    # -------------------------------------------------------------------------
    
    async def get_latest_tick(self, symbol: str) -> Tick:
        """Get latest tick/quote for a symbol."""
        if not self._exchange:
            raise ConnectionError("Not connected to Binance")
        
        try:
            ticker = await self._exchange.fetch_ticker(symbol)
            
            return Tick(
                symbol=symbol,
                market_type=MarketType.CRYPTO,
                timestamp=datetime.now(timezone.utc),
                bid=Decimal(str(ticker.get("bid", 0) or 0)),
                ask=Decimal(str(ticker.get("ask", 0) or 0)),
                last=Decimal(str(ticker.get("last", 0) or 0)),
                volume=Decimal(str(ticker.get("quoteVolume", 0) or 0)),
            )
            
        except Exception as e:
            logger.error("binance_fetch_tick_failed", symbol=symbol, error=str(e))
            raise
    
    async def subscribe_to_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        callback: Callable[[OHLCV], None],
    ) -> str:
        """
        Subscribe to real-time candle updates.
        
        Note: This uses polling. For production, use Binance WebSocket.
        """
        sub_id = f"candles_{symbol}_{timeframe.value}"
        
        async def poll_candles():
            tf_str = TIMEFRAME_MAP.get(timeframe, "1h")
            while True:
                try:
                    ohlcv = await self._exchange.fetch_ohlcv(
                        symbol=symbol,
                        timeframe=tf_str,
                        limit=1,
                    )
                    if ohlcv:
                        candle_data = ohlcv[-1]
                        timestamp_ms, o, h, l, c, v = candle_data[:6]
                        
                        candle = OHLCV(
                            symbol=symbol,
                            market_type=MarketType.CRYPTO,
                            timeframe=timeframe,
                            timestamp=datetime.fromtimestamp(
                                timestamp_ms / 1000, tz=timezone.utc
                            ),
                            open=Decimal(str(o)),
                            high=Decimal(str(h)),
                            low=Decimal(str(l)),
                            close=Decimal(str(c)),
                            volume=Decimal(str(v)),
                        )
                        callback(candle)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning("candle_poll_error", error=str(e))
                
                await asyncio.sleep(5)  # Poll every 5 seconds
        
        task = asyncio.create_task(poll_candles())
        self._subscriptions[sub_id] = task
        
        return sub_id
    
    async def subscribe_to_ticks(
        self,
        symbol: str,
        callback: Callable[[Tick], None],
    ) -> str:
        """Subscribe to real-time tick updates."""
        sub_id = f"ticks_{symbol}"
        
        async def poll_ticks():
            while True:
                try:
                    tick = await self.get_latest_tick(symbol)
                    callback(tick)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning("tick_poll_error", error=str(e))
                
                await asyncio.sleep(1)  # Poll every second
        
        task = asyncio.create_task(poll_ticks())
        self._subscriptions[sub_id] = task
        
        return sub_id
    
    async def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from a data stream."""
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id].cancel()
            del self._subscriptions[subscription_id]
            logger.debug("unsubscribed", subscription_id=subscription_id)
    
    # -------------------------------------------------------------------------
    # Market Information
    # -------------------------------------------------------------------------
    
    async def get_market_info(self, symbol: str) -> MarketInfo:
        """Get static market information for a symbol."""
        if not self._exchange:
            raise ConnectionError("Not connected to Binance")
        
        # Check cache
        if symbol in self._market_info_cache:
            return self._market_info_cache[symbol]
        
        try:
            market = self._exchange.market(symbol)
            
            info = MarketInfo(
                symbol=symbol,
                market_type=MarketType.CRYPTO,
                base_asset=market.get("base", ""),
                quote_asset=market.get("quote", ""),
                price_precision=market.get("precision", {}).get("price", 8),
                quantity_precision=market.get("precision", {}).get("amount", 8),
                min_quantity=Decimal(str(
                    market.get("limits", {}).get("amount", {}).get("min", 0) or 0
                )),
                max_quantity=Decimal(str(
                    market.get("limits", {}).get("amount", {}).get("max", 0) or 0
                )) if market.get("limits", {}).get("amount", {}).get("max") else None,
                min_notional=Decimal(str(
                    market.get("limits", {}).get("cost", {}).get("min", 0) or 0
                )),
                is_trading_enabled=market.get("active", True),
            )
            
            self._market_info_cache[symbol] = info
            return info
            
        except Exception as e:
            logger.error("binance_market_info_failed", symbol=symbol, error=str(e))
            raise ValueError(f"Invalid symbol: {symbol}")
    
    async def get_available_symbols(self) -> List[str]:
        """Get list of all available trading symbols."""
        if not self._exchange:
            raise ConnectionError("Not connected to Binance")
        
        return list(self._exchange.symbols)
    
    async def is_market_open(self, symbol: str) -> bool:
        """Check if the market is currently open (crypto is always open)."""
        return True  # Crypto markets are 24/7
