"""
Position Model

Represents an open trading position.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field

from src.domain.models.enums import MarketType, OrderSide, PositionSide


class Position(BaseModel):
    """
    Open trading position.
    
    Tracks an active position from entry to exit,
    including P&L calculations and risk levels.
    
    Attributes:
        position_id: Unique position identifier
        strategy_id: Strategy that opened this position
        symbol: Trading pair/symbol
        market_type: Market type
        side: Position direction (LONG/SHORT)
        entry_price: Average entry price
        quantity: Position size
        current_price: Latest market price
        stop_loss: Stop-loss price level
        take_profit: Take-profit price level
        opened_at: When position was opened
        closed_at: When position was closed (if closed)
    """
    
    # Identifiers
    position_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique position ID"
    )
    strategy_id: str = Field(..., description="Strategy that owns this position")
    
    # Position details
    symbol: str = Field(..., min_length=1)
    market_type: MarketType
    side: PositionSide
    
    # Quantities and prices
    entry_price: Decimal = Field(..., gt=0)
    quantity: Decimal = Field(..., gt=0)
    current_price: Decimal = Field(..., gt=0)
    
    # Risk levels
    stop_loss: Optional[Decimal] = Field(default=None)
    take_profit: Optional[Decimal] = Field(default=None)
    
    # Lifecycle
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = Field(default=None)
    
    # Cost tracking
    entry_commission: Decimal = Field(default=Decimal("0"))
    exit_commission: Decimal = Field(default=Decimal("0"))
    
    # Exit tracking
    exit_price: Optional[Decimal] = Field(default=None)
    exit_reason: Optional[str] = Field(default=None)
    
    @computed_field
    @property
    def unrealized_pnl(self) -> Decimal:
        """Calculate unrealized P&L based on current price."""
        if self.side == PositionSide.LONG:
            return (self.current_price - self.entry_price) * self.quantity
        else:  # SHORT
            return (self.entry_price - self.current_price) * self.quantity
    
    @computed_field
    @property
    def unrealized_pnl_pct(self) -> float:
        """Calculate unrealized P&L as percentage."""
        if self.entry_price == 0:
            return 0.0
        cost_basis = self.entry_price * self.quantity
        return float(self.unrealized_pnl / cost_basis) * 100
    
    @property
    def realized_pnl(self) -> Optional[Decimal]:
        """Calculate realized P&L (only if closed)."""
        if not self.is_closed or self.exit_price is None:
            return None
        
        if self.side == PositionSide.LONG:
            gross_pnl = (self.exit_price - self.entry_price) * self.quantity
        else:
            gross_pnl = (self.entry_price - self.exit_price) * self.quantity
        
        return gross_pnl - self.entry_commission - self.exit_commission
    
    @property
    def is_open(self) -> bool:
        """Check if position is still open."""
        return self.closed_at is None
    
    @property
    def is_closed(self) -> bool:
        """Check if position is closed."""
        return self.closed_at is not None
    
    @property
    def is_profitable(self) -> bool:
        """Check if position is currently profitable."""
        return self.unrealized_pnl > 0
    
    @property
    def notional_value(self) -> Decimal:
        """Calculate current notional value of position."""
        return self.current_price * self.quantity
    
    @property
    def cost_basis(self) -> Decimal:
        """Calculate original cost of position."""
        return self.entry_price * self.quantity
    
    @property
    def duration_seconds(self) -> float:
        """Calculate how long position has been open."""
        end_time = self.closed_at or datetime.utcnow()
        return (end_time - self.opened_at).total_seconds()
    
    @property
    def stop_loss_distance(self) -> Optional[Decimal]:
        """Calculate distance to stop-loss in price."""
        if self.stop_loss is None:
            return None
        return abs(self.current_price - self.stop_loss)
    
    @property
    def take_profit_distance(self) -> Optional[Decimal]:
        """Calculate distance to take-profit in price."""
        if self.take_profit is None:
            return None
        return abs(self.take_profit - self.current_price)
    
    def update_price(self, price: Decimal) -> None:
        """Update current market price."""
        self.current_price = price
    
    def close(
        self,
        exit_price: Decimal,
        exit_commission: Decimal = Decimal("0"),
        reason: str = "manual",
    ) -> None:
        """Close the position."""
        self.exit_price = exit_price
        self.exit_commission = exit_commission
        self.exit_reason = reason
        self.closed_at = datetime.utcnow()
        self.current_price = exit_price
    
    def __str__(self) -> str:
        pnl_pct = self.unrealized_pnl_pct
        pnl_sign = "+" if pnl_pct >= 0 else ""
        return (
            f"Position({self.side.value} {self.quantity} {self.symbol} "
            f"@ {self.entry_price} [{pnl_sign}{pnl_pct:.2f}%])"
        )
