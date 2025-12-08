"""
Execution Provider Port (Interface)

Abstract interface for order execution adapters.
All execution providers (Binance, OANDA, etc.) must implement this interface.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from src.domain.models.order import Order
from src.domain.models.position import Position
from src.domain.models.enums import OrderStatus


class Balance(ABC):
    """Account balance information."""
    
    def __init__(
        self,
        currency: str,
        total: Decimal,
        available: Decimal,
        locked: Decimal = Decimal("0"),
    ):
        self.currency = currency
        self.total = total
        self.available = available
        self.locked = locked


class IExecutionProvider(ABC):
    """
    Abstract interface for execution providers.
    
    This port defines the contract that all execution adapters must implement.
    Handles order placement, cancellation, and account management.
    
    Implementations:
        - BinanceExecutionAdapter (crypto)
        - OandaExecutionAdapter (forex)
        - IBExecutionAdapter (stocks)
        - SimulatedExecutionAdapter (backtesting/paper)
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if provider is connected and ready."""
        pass
    
    @property
    @abstractmethod
    def is_paper_trading(self) -> bool:
        """Check if this is a paper/simulated trading provider."""
        pass
    
    # -------------------------------------------------------------------------
    # Connection Management
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the execution provider.
        
        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If credentials are invalid
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the execution provider."""
        pass
    
    # -------------------------------------------------------------------------
    # Order Management
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def place_order(self, order: Order) -> Order:
        """
        Submit an order to the broker.
        
        Args:
            order: Order to place
            
        Returns:
            Order with updated status and broker_order_id
            
        Raises:
            InsufficientFundsError: If not enough balance
            InvalidOrderError: If order parameters are invalid
            ConnectionError: If not connected
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> Order:
        """
        Cancel an open order.
        
        Args:
            order_id: Local order ID or broker order ID
            
        Returns:
            Order with updated status
            
        Raises:
            OrderNotFoundError: If order doesn't exist
            OrderNotCancellableError: If order is already filled/cancelled
        """
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> Order:
        """
        Get current status of an order.
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Order with current status
        """
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """
        Get all open (unfilled) orders.
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of open orders
        """
        pass
    
    # -------------------------------------------------------------------------
    # Position Management
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """
        Get all open positions.
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of open positions
        """
        pass
    
    @abstractmethod
    async def close_position(
        self,
        symbol: str,
        quantity: Optional[Decimal] = None,
    ) -> Order:
        """
        Close an open position.
        
        Args:
            symbol: Position symbol to close
            quantity: Partial close quantity (None = close all)
            
        Returns:
            Order created to close the position
        """
        pass
    
    # -------------------------------------------------------------------------
    # Account Management
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def get_account_balance(self) -> List[Balance]:
        """
        Get account balance for all currencies.
        
        Returns:
            List of Balance objects for each currency
        """
        pass
    
    @abstractmethod
    async def get_available_balance(self, currency: str) -> Decimal:
        """
        Get available balance for a specific currency.
        
        Args:
            currency: Currency code (e.g., "USDT", "USD")
            
        Returns:
            Available balance
        """
        pass
