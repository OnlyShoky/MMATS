"""
Simulated Execution Adapter

Provides simulated order execution for paper trading and backtesting.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import uuid4

from src.domain.ports.execution_provider import IExecutionProvider, Balance
from src.domain.models.order import Order
from src.domain.models.position import Position
from src.domain.models.enums import (
    MarketType,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionSide,
)
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class SimulatedBalance(Balance):
    """Simulated account balance."""
    pass


class SimulatedExecutionAdapter(IExecutionProvider):
    """
    Simulated execution provider for paper trading and backtesting.
    
    Features:
    - Instant order fills at current market price
    - Simulated slippage and commission
    - Position tracking
    - Balance management
    
    Used for:
    - Backtesting strategies
    - Paper trading with real market data
    - Unit testing
    """
    
    def __init__(
        self,
        initial_balance: Decimal = Decimal("10000"),
        currency: str = "USDT",
        commission_rate: Decimal = Decimal("0.001"),  # 0.1%
        slippage_rate: Decimal = Decimal("0.0005"),   # 0.05%
    ):
        """
        Initialize simulated execution adapter.
        
        Args:
            initial_balance: Starting balance
            currency: Base currency
            commission_rate: Commission as fraction (0.001 = 0.1%)
            slippage_rate: Slippage as fraction (0.0005 = 0.05%)
        """
        self._initial_balance = initial_balance
        self._currency = currency
        self._commission_rate = commission_rate
        self._slippage_rate = slippage_rate
        
        # State
        self._connected = False
        self._balance = initial_balance
        self._orders: Dict[str, Order] = {}
        self._positions: Dict[str, Position] = {}  # symbol -> Position
        self._trade_history: List[Order] = []
        
        # Current prices (set externally for backtesting)
        self._current_prices: Dict[str, Decimal] = {}
    
    @property
    def provider_name(self) -> str:
        return "simulated"
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    @property
    def is_paper_trading(self) -> bool:
        return True
    
    # -------------------------------------------------------------------------
    # Price Management (for backtesting)
    # -------------------------------------------------------------------------
    
    def set_current_price(self, symbol: str, price: Decimal) -> None:
        """Set current price for a symbol (used in backtesting)."""
        self._current_prices[symbol] = price
        
        # Update position P&L
        if symbol in self._positions:
            self._positions[symbol].update_price(price)
    
    def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current price for a symbol."""
        return self._current_prices.get(symbol)
    
    def reset(self) -> None:
        """Reset adapter to initial state."""
        self._balance = self._initial_balance
        self._orders.clear()
        self._positions.clear()
        self._trade_history.clear()
        self._current_prices.clear()
        logger.info("simulated_execution_reset")
    
    # -------------------------------------------------------------------------
    # Connection Management
    # -------------------------------------------------------------------------
    
    async def connect(self) -> None:
        """Simulated connection."""
        self._connected = True
        logger.info(
            "simulated_execution_connected",
            initial_balance=str(self._balance),
            currency=self._currency,
        )
    
    async def disconnect(self) -> None:
        """Simulated disconnection."""
        self._connected = False
        logger.info("simulated_execution_disconnected")
    
    # -------------------------------------------------------------------------
    # Order Management
    # -------------------------------------------------------------------------
    
    async def place_order(self, order: Order) -> Order:
        """
        Place and immediately fill a market order.
        
        For limit orders, the order is stored and filled when price reaches limit.
        """
        if not self._connected:
            raise ConnectionError("Not connected")
        
        # Get current price
        current_price = self._current_prices.get(order.symbol)
        if current_price is None:
            order.mark_rejected("No price data for symbol")
            return order
        
        # Calculate fill price with slippage
        if order.side == OrderSide.BUY:
            fill_price = current_price * (1 + self._slippage_rate)
        else:
            fill_price = current_price * (1 - self._slippage_rate)
        
        # For limit orders, check if price is acceptable
        if order.order_type == OrderType.LIMIT and order.price:
            if order.side == OrderSide.BUY and fill_price > order.price:
                # Store order, don't fill yet
                order.status = OrderStatus.SUBMITTED
                order.broker_order_id = f"SIM_{uuid4().hex[:8]}"
                self._orders[order.order_id] = order
                return order
            elif order.side == OrderSide.SELL and fill_price < order.price:
                order.status = OrderStatus.SUBMITTED
                order.broker_order_id = f"SIM_{uuid4().hex[:8]}"
                self._orders[order.order_id] = order
                return order
        
        # Calculate order value and commission
        order_value = order.quantity * fill_price
        commission = order_value * self._commission_rate
        
        # Check balance for buy orders
        if order.side == OrderSide.BUY:
            total_cost = order_value + commission
            if total_cost > self._balance:
                order.mark_rejected(f"Insufficient balance: {self._balance} < {total_cost}")
                return order
            self._balance -= total_cost
        
        # Mark order as filled
        order.broker_order_id = f"SIM_{uuid4().hex[:8]}"
        order.mark_submitted(order.broker_order_id)
        order.mark_filled(
            filled_quantity=order.quantity,
            filled_price=fill_price,
            commission=commission,
        )
        
        # Update positions
        self._update_position(order, fill_price)
        
        # Store order
        self._orders[order.order_id] = order
        self._trade_history.append(order)
        
        logger.info(
            "simulated_order_filled",
            order_id=order.order_id[:8],
            symbol=order.symbol,
            side=order.side.value,
            quantity=str(order.quantity),
            price=str(fill_price),
            commission=str(commission),
        )
        
        return order
    
    def _update_position(self, order: Order, fill_price: Decimal) -> None:
        """Update position based on filled order."""
        symbol = order.symbol
        
        if order.side == OrderSide.BUY:
            # Opening or adding to long position
            if symbol in self._positions:
                # Add to existing position (simplified - averaging)
                pos = self._positions[symbol]
                if pos.side == PositionSide.LONG:
                    # Average entry price
                    total_qty = pos.quantity + order.quantity
                    avg_price = (
                        (pos.entry_price * pos.quantity + fill_price * order.quantity)
                        / total_qty
                    )
                    pos.entry_price = avg_price
                    pos.quantity = total_qty
                    pos.current_price = fill_price
                else:
                    # Closing short position
                    self._close_position_internal(symbol, order, fill_price)
            else:
                # New long position
                self._positions[symbol] = Position(
                    strategy_id=order.strategy_id,
                    symbol=symbol,
                    market_type=order.market_type,
                    side=PositionSide.LONG,
                    entry_price=fill_price,
                    quantity=order.quantity,
                    current_price=fill_price,
                    stop_loss=order.stop_loss,
                    take_profit=order.take_profit,
                )
        
        else:  # SELL
            if symbol in self._positions:
                pos = self._positions[symbol]
                if pos.side == PositionSide.LONG:
                    # Closing long position
                    self._close_position_internal(symbol, order, fill_price)
                else:
                    # Adding to short (not implemented for simplicity)
                    pass
    
    def _close_position_internal(
        self,
        symbol: str,
        order: Order,
        fill_price: Decimal,
    ) -> None:
        """Close a position and realize P&L."""
        if symbol not in self._positions:
            return
        
        pos = self._positions[symbol]
        
        # Calculate P&L
        if pos.side == PositionSide.LONG:
            pnl = (fill_price - pos.entry_price) * pos.quantity
        else:
            pnl = (pos.entry_price - fill_price) * pos.quantity
        
        # Add P&L to balance (minus commission already deducted)
        self._balance += (fill_price * pos.quantity) + pnl
        
        # Close position
        pos.close(exit_price=fill_price, reason="order")
        del self._positions[symbol]
        
        logger.info(
            "simulated_position_closed",
            symbol=symbol,
            pnl=str(pnl),
            balance=str(self._balance),
        )
    
    async def cancel_order(self, order_id: str) -> Order:
        """Cancel a pending order."""
        if order_id not in self._orders:
            raise ValueError(f"Order not found: {order_id}")
        
        order = self._orders[order_id]
        
        if order.is_closed:
            raise ValueError(f"Order already closed: {order_id}")
        
        order.mark_cancelled()
        return order
    
    async def get_order_status(self, order_id: str) -> Order:
        """Get order status."""
        if order_id not in self._orders:
            raise ValueError(f"Order not found: {order_id}")
        return self._orders[order_id]
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders."""
        orders = [o for o in self._orders.values() if o.is_active]
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        return orders
    
    # -------------------------------------------------------------------------
    # Position Management
    # -------------------------------------------------------------------------
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Get all open positions."""
        positions = list(self._positions.values())
        if symbol:
            positions = [p for p in positions if p.symbol == symbol]
        return positions
    
    async def close_position(
        self,
        symbol: str,
        quantity: Optional[Decimal] = None,
    ) -> Order:
        """Close a position by creating a market order."""
        if symbol not in self._positions:
            raise ValueError(f"No position for symbol: {symbol}")
        
        pos = self._positions[symbol]
        close_qty = quantity or pos.quantity
        
        # Create closing order
        order = Order(
            strategy_id=pos.strategy_id,
            symbol=symbol,
            market_type=pos.market_type,
            side=OrderSide.SELL if pos.side == PositionSide.LONG else OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=close_qty,
        )
        
        return await self.place_order(order)
    
    # -------------------------------------------------------------------------
    # Account Management
    # -------------------------------------------------------------------------
    
    async def get_account_balance(self) -> List[Balance]:
        """Get account balances."""
        # Calculate equity (balance + unrealized P&L)
        unrealized_pnl = sum(
            p.unrealized_pnl for p in self._positions.values()
        )
        
        return [
            SimulatedBalance(
                currency=self._currency,
                total=self._balance + unrealized_pnl,
                available=self._balance,
                locked=Decimal("0"),
            )
        ]
    
    async def get_available_balance(self, currency: str) -> Decimal:
        """Get available balance for a currency."""
        if currency == self._currency:
            return self._balance
        return Decimal("0")
    
    # -------------------------------------------------------------------------
    # Statistics (for reporting)
    # -------------------------------------------------------------------------
    
    def get_statistics(self) -> dict:
        """Get trading statistics."""
        filled_orders = [o for o in self._trade_history if o.is_filled]
        
        total_commission = sum(o.commission for o in filled_orders)
        
        return {
            "initial_balance": str(self._initial_balance),
            "current_balance": str(self._balance),
            "total_orders": len(self._trade_history),
            "filled_orders": len(filled_orders),
            "open_positions": len(self._positions),
            "total_commission": str(total_commission),
        }
