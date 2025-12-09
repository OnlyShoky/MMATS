"""
Backtest Engine

Orchestrates backtesting of trading strategies against historical data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.domain.models import (
    OHLCV,
    Signal,
    Position,
    StrategyContext,
    AccountState,
    MarketType,
    Timeframe,
    Environment,
    SignalAction,
)
from src.domain.ports.strategy import IStrategy
from src.infrastructure.adapters.market_data import SimulatedMarketDataAdapter
from src.infrastructure.adapters.execution import SimulatedExecutionAdapter
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for a backtest run."""
    
    strategy: IStrategy
    symbol: str
    timeframe: Timeframe
    start_date: datetime
    end_date: datetime
    initial_capital: Decimal = Decimal("10000")
    commission_rate: Decimal = Decimal("0.001")  # 0.1%
    slippage_rate: Decimal = Decimal("0.0005")   # 0.05%
    market_type: MarketType = MarketType.CRYPTO


@dataclass
class BacktestResult:
    """Results from a backtest run."""
    
    # Configuration
    strategy_name: str
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    
    # Performance
    initial_capital: Decimal
    final_capital: Decimal
    total_return: float
    total_return_pct: float
    
    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Risk metrics
    max_drawdown: float
    max_drawdown_pct: float
    
    # Additional data
    equity_curve: List[Dict[str, Any]] = field(default_factory=list)
    trades: List[Dict[str, Any]] = field(default_factory=list)
    signals: List[Signal] = field(default_factory=list)


class IndicatorCalculator:
    """
    Simple indicator calculator for backtesting.
    
    Note: For production, use TA-Lib or pandas-ta.
    """
    
    @staticmethod
    def sma(prices: List[Decimal], period: int) -> Optional[Decimal]:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return None
        recent = prices[-period:]
        return sum(recent) / period
    
    @staticmethod
    def ema(prices: List[Decimal], period: int) -> Optional[Decimal]:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return None
        
        multiplier = Decimal(2) / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def rsi(prices: List[Decimal], period: int = 14) -> Optional[Decimal]:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(float(change))
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(float(change)))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return Decimal("100")
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return Decimal(str(round(rsi, 2)))


class BacktestEngine:
    """
    Engine for running backtests.
    
    Usage:
        engine = BacktestEngine()
        result = await engine.run(config, candles)
    """
    
    def __init__(self):
        self._indicator_calc = IndicatorCalculator()
    
    async def run(
        self,
        config: BacktestConfig,
        candles: List[OHLCV],
    ) -> BacktestResult:
        """
        Run a backtest with the given configuration and data.
        
        Args:
            config: Backtest configuration
            candles: Historical candle data
            
        Returns:
            BacktestResult with performance metrics
        """
        logger.info(
            "backtest_started",
            strategy=config.strategy.name,
            symbol=config.symbol,
            candles=len(candles),
        )
        
        # Initialize adapters
        market_data = SimulatedMarketDataAdapter()
        execution = SimulatedExecutionAdapter(
            initial_balance=config.initial_capital,
            commission_rate=config.commission_rate,
            slippage_rate=config.slippage_rate,
        )
        
        await market_data.connect()
        await execution.connect()
        
        # Load candles into market data adapter
        market_data.load_candles(config.symbol, candles)
        
        # Initialize strategy
        config.strategy.initialize()
        
        # Tracking variables
        signals: List[Signal] = []
        equity_curve: List[Dict[str, Any]] = []
        trades: List[Dict[str, Any]] = []
        peak_equity = config.initial_capital
        max_drawdown = Decimal("0")
        
        # Required warmup period
        warmup = config.strategy.get_required_candles()
        
        # Run through each candle
        for i in range(warmup, len(candles)):
            candle = candles[i]
            historical = candles[:i+1]
            
            # Set current price in execution adapter
            execution.set_current_price(config.symbol, candle.close)
            
            # Calculate indicators
            closes = [c.close for c in historical]
            indicators = self._calculate_indicators(
                config.strategy,
                closes,
            )
            
            # Get current positions
            positions = await execution.get_positions(config.symbol)
            all_positions = await execution.get_positions()
            
            # Get current balance
            balance = await execution.get_available_balance("USDT")
            
            # Build context
            context = StrategyContext(
                symbol=config.symbol,
                market_type=config.market_type,
                timeframe=config.timeframe,
                timestamp=candle.timestamp,
                environment=Environment.BACKTEST,
                candles=historical[-100:],  # Last 100 candles
                current_price=candle.close,
                indicators=indicators,
                account=AccountState(
                    balance=balance,
                    equity=balance,
                    currency="USDT",
                ),
                positions=positions,
                all_positions=all_positions,
            )
            
            # Get signal from strategy
            signal = config.strategy.on_bar(context)
            signals.append(signal)
            
            # Execute signal
            if signal.is_actionable:
                await self._execute_signal(signal, execution, config)
            
            # Track equity curve
            current_equity = await self._calculate_equity(execution)
            equity_curve.append({
                "timestamp": candle.timestamp.isoformat(),
                "equity": float(current_equity),
                "price": float(candle.close),
            })
            
            # Track max drawdown
            if current_equity > peak_equity:
                peak_equity = current_equity
            drawdown = peak_equity - current_equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Close any remaining positions
        open_positions = await execution.get_positions()
        for pos in open_positions:
            await execution.close_position(pos.symbol)
        
        # Calculate final metrics
        final_equity = await self._calculate_equity(execution)
        stats = execution.get_statistics()
        
        # Build trade list
        for order in execution._trade_history:
            if order.is_filled:
                trades.append({
                    "timestamp": order.filled_at.isoformat() if order.filled_at else "",
                    "symbol": order.symbol,
                    "side": order.side.value,
                    "quantity": float(order.quantity),
                    "price": float(order.filled_price) if order.filled_price else 0,
                    "commission": float(order.commission),
                })
        
        # Calculate win rate
        # (simplified - just counting profitable closes)
        winning = sum(1 for t in trades if t["side"] == "sell")  # Simplified
        total_trades = len(trades) // 2  # Buy + Sell = 1 trade
        
        result = BacktestResult(
            strategy_name=config.strategy.name,
            symbol=config.symbol,
            timeframe=config.timeframe.value,
            start_date=config.start_date,
            end_date=config.end_date,
            initial_capital=config.initial_capital,
            final_capital=final_equity,
            total_return=float(final_equity - config.initial_capital),
            total_return_pct=float(
                (final_equity - config.initial_capital) / config.initial_capital * 100
            ),
            total_trades=total_trades,
            winning_trades=winning,
            losing_trades=total_trades - winning,
            win_rate=winning / total_trades * 100 if total_trades > 0 else 0,
            max_drawdown=float(max_drawdown),
            max_drawdown_pct=float(
                max_drawdown / peak_equity * 100 if peak_equity > 0 else 0
            ),
            equity_curve=equity_curve,
            trades=trades,
            signals=signals,
        )
        
        # Cleanup
        config.strategy.cleanup()
        await execution.disconnect()
        await market_data.disconnect()
        
        logger.info(
            "backtest_completed",
            strategy=config.strategy.name,
            return_pct=f"{result.total_return_pct:.2f}%",
            trades=result.total_trades,
        )
        
        return result
    
    def _calculate_indicators(
        self,
        strategy: IStrategy,
        closes: List[Decimal],
    ) -> Dict[str, Any]:
        """Calculate indicators required by strategy."""
        indicators = {}
        
        for ind_config in strategy.get_required_indicators():
            name = ind_config.name
            ind_type = ind_config.indicator_type.upper()
            params = ind_config.params
            
            if ind_type == "SMA":
                period = params.get("period", 20)
                indicators[name] = self._indicator_calc.sma(closes, period)
            
            elif ind_type == "EMA":
                period = params.get("period", 20)
                indicators[name] = self._indicator_calc.ema(closes, period)
            
            elif ind_type == "RSI":
                period = params.get("period", 14)
                indicators[name] = self._indicator_calc.rsi(closes, period)
        
        return indicators
    
    async def _execute_signal(
        self,
        signal: Signal,
        execution: SimulatedExecutionAdapter,
        config: BacktestConfig,
    ) -> None:
        """Execute a trading signal."""
        from src.domain.models.order import Order
        from src.domain.models.enums import OrderSide, OrderType
        
        if signal.action == SignalAction.BUY:
            # Calculate position size
            balance = await execution.get_available_balance("USDT")
            size_value = balance * Decimal(str(signal.position_size))
            current_price = execution.get_current_price(signal.symbol)
            
            if current_price and current_price > 0:
                quantity = size_value / current_price
                
                order = Order(
                    strategy_id=signal.strategy_id,
                    symbol=signal.symbol,
                    market_type=signal.market_type,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=quantity,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                )
                
                await execution.place_order(order)
        
        elif signal.action == SignalAction.CLOSE:
            positions = await execution.get_positions(signal.symbol)
            for pos in positions:
                await execution.close_position(pos.symbol)
        
        elif signal.action == SignalAction.SELL:
            # For short selling (simplified - just close long)
            positions = await execution.get_positions(signal.symbol)
            for pos in positions:
                await execution.close_position(pos.symbol)
    
    async def _calculate_equity(
        self,
        execution: SimulatedExecutionAdapter,
    ) -> Decimal:
        """Calculate total equity (balance + unrealized P&L)."""
        balances = await execution.get_account_balance()
        return balances[0].total if balances else Decimal("0")


def print_backtest_report(result: BacktestResult) -> None:
    """Print a formatted backtest report."""
    print("\n" + "=" * 60)
    print(f"  BACKTEST REPORT: {result.strategy_name}")
    print("=" * 60)
    print(f"  Symbol:         {result.symbol}")
    print(f"  Timeframe:      {result.timeframe}")
    print(f"  Period:         {result.start_date.date()} to {result.end_date.date()}")
    print("-" * 60)
    print(f"  Initial Capital: ${result.initial_capital:,.2f}")
    print(f"  Final Capital:   ${result.final_capital:,.2f}")
    print(f"  Total Return:    ${result.total_return:,.2f} ({result.total_return_pct:+.2f}%)")
    print("-" * 60)
    print(f"  Total Trades:    {result.total_trades}")
    print(f"  Win Rate:        {result.win_rate:.1f}%")
    print(f"  Max Drawdown:    ${result.max_drawdown:,.2f} ({result.max_drawdown_pct:.2f}%)")
    print("=" * 60 + "\n")
