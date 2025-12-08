"""
Order Model

Represents a trading order submitted to a broker/exchange.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.domain.models.enums import (
    MarketType,
    OrderSide,
    OrderStatus,
    OrderType,
)


class Order(BaseModel):
    """
    Trading order to be submitted to a broker/exchange.
    
    Orders are created from signals after risk validation.
    They track the full lifecycle from creation to fill/cancel.
    
    Attributes:
        order_id: Unique order identifier
        strategy_id: Strategy that originated this order
        signal_id: Original signal ID (for tracing)
        timestamp: Order creation time
        symbol: Trading pair/symbol
        market_type: Market type
        side: Order direction (BUY/SELL)
        order_type: Execution type (MARKET/LIMIT/etc.)
        quantity: Amount to trade
        price: Limit price (for limit orders)
        stop_price: Trigger price (for stop orders)
        status: Current order status
        filled_quantity: Amount filled so far
        filled_price: Average fill price
        broker_order_id: Order ID from broker
        error_message: Error if rejected
    """
    
    # Identifiers
    order_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique order ID"
    )
    strategy_id: str = Field(..., description="Strategy that created this order")
    signal_id: Optional[str] = Field(
        default=None,
        description="Original signal ID"
    )
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = Field(default=None)
    filled_at: Optional[datetime] = Field(default=None)
    
    # Order details
    symbol: str = Field(..., min_length=1)
    market_type: MarketType
    side: OrderSide
    order_type: OrderType = Field(default=OrderType.MARKET)
    
    # Quantities and prices
    quantity: Decimal = Field(..., gt=0, description="Order quantity")
    price: Optional[Decimal] = Field(
        default=None,
        description="Limit price (required for LIMIT orders)"
    )
    stop_price: Optional[Decimal] = Field(
        default=None,
        description="Stop trigger price"
    )
    
    # Risk management
    stop_loss: Optional[Decimal] = Field(default=None)
    take_profit: Optional[Decimal] = Field(default=None)
    
    # Status tracking
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    filled_quantity: Decimal = Field(default=Decimal("0"))
    filled_price: Optional[Decimal] = Field(default=None)
    commission: Decimal = Field(default=Decimal("0"))
    
    # Broker integration
    broker_order_id: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    
    @property
    def is_pending(self) -> bool:
        """Check if order is waiting to be submitted."""
        return self.status == OrderStatus.PENDING
    
    @property
    def is_active(self) -> bool:
        """Check if order is active (submitted but not filled)."""
        return self.status in (OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED)
    
    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled."""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_closed(self) -> bool:
        """Check if order is in a terminal state."""
        return self.status in (
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        )
    
    @property
    def remaining_quantity(self) -> Decimal:
        """Calculate remaining quantity to fill."""
        return self.quantity - self.filled_quantity
    
    @property
    def fill_percentage(self) -> float:
        """Calculate fill percentage."""
        if self.quantity == 0:
            return 0.0
        return float(self.filled_quantity / self.quantity) * 100
    
    def mark_submitted(self, broker_order_id: str) -> None:
        """Mark order as submitted to broker."""
        self.status = OrderStatus.SUBMITTED
        self.broker_order_id = broker_order_id
        self.submitted_at = datetime.utcnow()
    
    def mark_filled(
        self,
        filled_quantity: Decimal,
        filled_price: Decimal,
        commission: Decimal = Decimal("0"),
    ) -> None:
        """Update order with fill information."""
        self.filled_quantity = filled_quantity
        self.filled_price = filled_price
        self.commission = commission
        self.filled_at = datetime.utcnow()
        
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
    
    def mark_cancelled(self) -> None:
        """Mark order as cancelled."""
        self.status = OrderStatus.CANCELLED
    
    def mark_rejected(self, reason: str) -> None:
        """Mark order as rejected."""
        self.status = OrderStatus.REJECTED
        self.error_message = reason
    
    def __str__(self) -> str:
        return (
            f"Order({self.order_id[:8]}: {self.side.value} "
            f"{self.quantity} {self.symbol} @ {self.order_type.value} "
            f"[{self.status.value}])"
        )
