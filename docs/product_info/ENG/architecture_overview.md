# Architecture Overview

This document explains the system architecture of the **Multi-Market Automated Trading System (MMATS)**, its modular design, and how components interact.

> [!NOTE]
> MMATS follows **Clean Architecture** and **Hexagonal (Ports & Adapters)** patterns to ensure flexibility, testability, and maintainability.

---

## Architectural Principles

### Clean Architecture

Clean Architecture separates concerns into distinct layers, with dependencies pointing inward:

```
┌─────────────────────────────────────────────────────────┐
│                     Presentation Layer                   │
│              (Web Dashboard / Desktop UI)                │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Application Layer                       │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│   │   Advisory   │  │   Operator   │  │  Backtesting │ │
│   │     Mode     │  │     Mode     │  │    Engine    │ │
│   └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Domain Layer (Core)                   │
│         Strategy Orchestration | Risk Management         │
│              Portfolio Manager | Position Tracker        │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Infrastructure Layer (Adapters)             │
│    Market Data | Execution | Storage | Notifications     │
└─────────────────────────────────────────────────────────┘
```

### Hexagonal Architecture (Ports & Adapters)

The system defines **ports** (interfaces) that **adapters** implement:

| Port Type | Purpose | Example Adapters |
|-----------|---------|------------------|
| **Inbound** | External triggers | REST API, WebSocket, CLI |
| **Outbound** | External services | Binance, OANDA, PostgreSQL |

---

## Core Components

### 1. Strategy Orchestration Engine

**Responsibility**: Load, execute, and coordinate multiple trading models.

```
┌────────────────────────────────────────────────────────┐
│           STRATEGY ORCHESTRATION ENGINE                 │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Model     │  │   Model     │  │   Signal    │    │
│  │   Loader    │  │  Executor   │  │ Aggregator  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  Features:                                              │
│  • Dynamic model loading from strategy directory        │
│  • Parallel execution of independent strategies         │
│  • Input standardization (market data → model format)   │
│  • Output aggregation (model signals → execution plan)  │
│  • Model performance tracking                           │
└────────────────────────────────────────────────────────┘
```

See: [[trading_concepts.md#Signal-Generation]] for signal details.

### 2. Risk Management Engine

**Responsibility**: Enforce risk limits and protect capital.

```
┌────────────────────────────────────────────────────────┐
│             RISK MANAGEMENT ENGINE                      │
│                                                         │
│  • Position Sizer      - Calculate safe position sizes  │
│  • Drawdown Monitor    - Track peak-to-trough decline   │
│  • Exposure Calculator - Monitor capital at risk        │
│  • Emergency Shutdown  - Circuit breaker logic          │
└────────────────────────────────────────────────────────┘
```

See: [[risk_management.md]] for complete risk documentation.

### 3. Portfolio Manager

**Responsibility**: Track all positions and account state.

| Function | Description |
|----------|-------------|
| Position Tracking | Real-time position updates |
| P&L Calculator | Realized and unrealized profit/loss |
| Balance Manager | Account balance across markets |
| Transaction History | Complete trade journal |
| Performance Metrics | Returns, Sharpe ratio, etc. |

---

## Strategy Interface

All trading models implement a standardized interface:

```python
class IStrategy:
    """
    Base interface for all trading strategies
    """
    
    # Metadata
    name: str
    version: str
    author: str
    description: str
    markets_supported: List[MarketType]  # CRYPTO, FOREX, STOCK
    timeframes_supported: List[Timeframe]
    
    # Core Method
    def on_bar(self, context: StrategyContext) -> Signal:
        """
        Called on each new bar/candle
        
        Returns:
            Signal: {
                action: BUY | SELL | HOLD | CLOSE,
                symbol: str,
                position_size: float (0-1, % of capital),
                stop_loss: float (price),
                take_profit: float (price),
                confidence: float (0-1)
            }
        """
        pass
```

### Strategy Context

Standardized input provided to every strategy:

| Field | Description |
|-------|-------------|
| `market_data` | OHLCV + computed indicators |
| `account` | Balance, open positions |
| `environment` | BACKTEST, PAPER, or LIVE |
| `timestamp` | Current bar time (UTC) |

### Benefits

- ✅ Same code runs in backtest, paper, and live
- ✅ No direct market/broker dependencies
- ✅ Hot-reloading without system restart
- ✅ Easy testing with mock data

---

## Adapter Interfaces

### Market Data Provider

Interface for fetching market data:

```python
class IMarketDataProvider:
    async def get_historical_candles(
        symbol: str, 
        timeframe: Timeframe, 
        start: datetime, 
        end: datetime
    ) -> List[OHLCV]
    
    async def get_latest_price(symbol: str) -> Tick
    
    async def subscribe_to_updates(
        symbol: str, 
        callback: Callable[[Tick], None]
    )
    
    async def get_market_metadata(symbol: str) -> MarketMetadata
```

**Implementations**:
- `BinanceMarketDataProvider` — Crypto
- `OandaMarketDataProvider` — Forex
- `InteractiveBrokersMarketDataProvider` — Stocks
- `SimulatedMarketDataProvider` — Backtesting

### Execution Provider

Interface for order execution:

```python
class IExecutionProvider:
    async def place_order(order: OrderRequest) -> OrderConfirmation
    async def cancel_order(order_id: str) -> CancelConfirmation
    async def get_open_orders() -> List[Order]
    async def get_positions() -> List[Position]
    async def get_account_balance() -> AccountBalance
```

**Implementations**:
- `BinanceExecutionProvider`
- `OandaExecutionProvider`
- `InteractiveBrokersExecutionProvider`
- `SimulatedExecutionProvider` — Paper trading

---

## Data Pipeline

The unified data pipeline ensures consistent handling regardless of source:

```
┌─────────────────────────────────────────────────────────┐
│                    DATA PIPELINE                         │
│                                                          │
│  1. RAW DATA FETCH                                       │
│     └─> Market-specific adapter (Binance, OANDA, etc.)  │
│                                                          │
│  2. NORMALIZATION                                        │
│     └─> Convert to standard MarketData format           │
│                                                          │
│  3. INDICATOR CALCULATION                                │
│     └─> TA-Lib, pandas-ta (SMA, RSI, MACD, etc.)        │
│                                                          │
│  4. CONTEXT ASSEMBLY                                     │
│     └─> Combine data + account state + environment      │
│                                                          │
│  5. STRATEGY EXECUTION                                   │
│     └─> Pass context to registered strategies           │
└─────────────────────────────────────────────────────────┘
```

### Standardized Data Format

```python
class MarketData:
    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    indicators: Dict[str, float]  # Computed indicators
    market_type: MarketType       # CRYPTO, FOREX, STOCK
    timeframe: Timeframe          # 1m, 5m, 1H, 1D, etc.
```

---

## Operating Modes

MMATS supports three distinct operating modes:

### Advisory Mode

```
┌──────────────────────────────────────┐
│         ADVISORY MODE                 │
│                                       │
│  • Compute strategy signals           │
│  • Display in dashboard               │
│  • Log to database                    │
│  • NO orders sent to broker           │
│  • Optional paper performance track   │
└──────────────────────────────────────┘
```

**Use Cases**: Strategy validation, learning, manual execution

### Operator Mode

```
┌──────────────────────────────────────┐
│         OPERATOR MODE                 │
│                                       │
│  • Generate signals                   │
│  • Risk validation                    │
│  • Execute real orders                │
│  • REAL MONEY AT RISK                 │
│  • Emergency stop always accessible   │
└──────────────────────────────────────┘
```

**Safety Requirements**:
- Double confirmation before first trade
- Daily loss limit enforcement
- Manual override capability
- Automatic mode downgrade on errors

### Backtesting Mode

See: [[backtesting_and_simulation.md]] for complete details.

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Core Application** | Python 3.11+ | Rich ecosystem, rapid development |
| **Time-Series DB** | TimescaleDB/InfluxDB | Optimized for OHLCV data |
| **Relational DB** | PostgreSQL | Transactions, positions, configs |
| **Caching** | Redis | Real-time data, session state |
| **Message Queue** | RabbitMQ/Kafka | Decouple components, async processing |
| **Web Backend** | FastAPI | Modern, async, auto-docs |
| **Web Frontend** | React/Svelte | Real-time dashboard |
| **Real-Time** | WebSocket | Live updates |
| **Deployment** | Docker Compose | Containerized services |

---

## Performance Requirements

| Operation | Target Latency | Maximum Latency |
|-----------|----------------|-----------------|
| Strategy computation | <50ms | 100ms |
| Risk validation | <10ms | 25ms |
| Order submission | <200ms | 500ms |
| Market data ingestion | <100ms | 200ms |
| Dashboard update | <1s | 2s |

**Measurement**: 95th percentile under normal load (5 strategies, 10 symbols)

---

## Modularity Benefits

| Aspect | Benefit |
|--------|---------|
| **Adding Markets** | Implement adapter, no core changes |
| **Adding Strategies** | Drop into strategies folder, auto-discovered |
| **Replacing Brokers** | Swap adapter, same interface |
| **Testing** | Mock adapters for isolated unit tests |
| **Scaling** | Parallel strategy execution |

---

## Related Documentation

- [[trading_concepts.md]] — Trading fundamentals
- [[risk_management.md]] — Risk controls
- [[multi_market_operations.md]] — Multi-market orchestration
- [[backtesting_and_simulation.md]] — Historical testing
- [[security_and_compliance.md]] — Security architecture

---

## References

> [!TIP]
> For deeper understanding of the architectural patterns:
> - Martin, Robert C. "Clean Architecture" (2017)
> - Cockburn, Alistair. "Hexagonal Architecture"
