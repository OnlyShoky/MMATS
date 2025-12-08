Claude PRS:

# Product Requirements Specification
## Multi-Market Automated Trading System (MMATS)

**Version:** 1.0  
**Date:** December 2025  
**Status:** Draft  
**Classification:** Internal Use

---

## Executive Summary

### Product Vision
MMATS is a modular, extensible automated trading platform designed to execute algorithmic trading strategies across multiple financial markets (cryptocurrencies, forex, and equities). The system prioritizes architectural flexibility, allowing rapid integration of new trading models, market adapters, and risk management rules without core system modifications.

### Target Users
- **Phase 1:** Individual algorithmic trader (personal use, 100-200€ capital)
- **Phase 2:** Small group of trusted users (friends, beta testers)
- **Phase 3:** Potential commercial offering (subject to legal/regulatory review)

### Core Value Proposition
- **Market Agnostic:** Single codebase supports crypto, forex, and stocks simultaneously
- **Model Agnostic:** Plug-and-play architecture for unlimited trading strategies
- **Mode Flexibility:** Advisory-only signals or full automated execution
- **Environment Parity:** Identical behavior across backtesting, paper trading, and live execution
- **AI-Ready:** Architecture prepared for LLM-based news sentiment integration

### Success Metrics
- System uptime >99.5% during trading hours
- <100ms strategy computation latency (medium frequency)
- <500ms order execution latency
- Zero position sizing errors
- Zero unauthorized trades
- Profitable backtests before live deployment

---

## 1. Product Scope

### 1.1 In Scope
- Multi-market trading engine (crypto, forex, stocks)
- Standardized strategy interface for mathematical models
- Historical backtesting with walk-forward analysis
- Real-time paper trading simulation
- Live trading execution (operator mode)
- Advisory signal generation (non-execution mode)
- Multi-strategy concurrent execution
- Broker/exchange API abstraction layer
- Centralized risk management system
- Real-time monitoring dashboard
- Emergency shutdown mechanisms
- Audit logging and trade journal
- Encrypted credential management

### 1.2 Out of Scope (Phase 1)
- High-frequency trading (<100ms latency)
- Options, futures, derivatives (initially)
- Social trading/copy trading features
- Mobile applications
- Multi-user accounts and permissions
- Automated tax reporting
- Regulatory compliance automation
- Cloud-hosted SaaS platform

### 1.3 Future Extensions
- AI-powered news sentiment analysis
- LLM-based market impact scoring
- Multi-account management
- Advanced order types (iceberg, TWAP, VWAP)
- Cross-market arbitrage detection
- Machine learning model training pipeline
- Community strategy marketplace

---

## 2. User Personas

### Persona 1: Alex - The Quantitative Experimenter
**Profile:** Software engineer with algorithmic trading interest, limited capital
**Goals:**
- Test multiple mathematical models simultaneously
- Validate strategies through rigorous backtesting
- Start with paper trading before risking capital
- Monitor performance across different market conditions

**Pain Points:**
- Existing platforms lock into single broker/market
- Difficult to compare multiple strategies objectively
- No clear path from backtest to live trading

**MMATS Solution:**
- Unified backtesting and live execution pipeline
- Parallel strategy execution with performance comparison
- Seamless progression: backtest → paper → live

### Persona 2: Sam - The Multi-Market Trader
**Profile:** Experienced trader seeking automation across asset classes
**Goals:**
- Deploy proven strategies across crypto and forex simultaneously
- Centralized risk management across all positions
- Quick reaction to market opportunities 24/7

**Pain Points:**
- Managing multiple platforms and APIs
- Risk exposure difficult to monitor holistically
- Manual execution prone to errors and delays

**MMATS Solution:**
- Single platform for all markets
- Unified risk dashboard
- Automated execution with manual override

---

## 3. System Architecture

### 3.1 Architectural Principles
The system follows **Clean Architecture** and **Hexagonal (Ports & Adapters)** patterns:

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
│  ┌─────────────────────────────────────────────────┐   │
│  │         Strategy Orchestration Engine            │   │
│  │  - Model Loader                                  │   │
│  │  - Model Executor (parallel/sequential)          │   │
│  │  - Signal Aggregator                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Risk Management Engine                   │   │
│  │  - Position Sizer                                │   │
│  │  - Drawdown Monitor                              │   │
│  │  - Exposure Calculator                           │   │
│  │  - Emergency Shutdown Logic                      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Portfolio Manager                        │   │
│  │  - Position Tracker                              │   │
│  │  - P&L Calculator                                │   │
│  │  - Balance Manager                               │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Infrastructure Layer (Adapters)             │
│                                                           │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────┐ │
│  │  Market Data   │  │   Execution    │  │  Storage  │ │
│  │    Adapters    │  │    Adapters    │  │  Adapters │ │
│  ├────────────────┤  ├────────────────┤  ├───────────┤ │
│  │ - Binance API  │  │ - Binance      │  │ - SQLite  │ │
│  │ - OANDA API    │  │ - OANDA        │  │ - PostgreSQL│
│  │ - IB API       │  │ - Interactive  │  │ - TimescaleDB│
│  │ - CoinGecko    │  │   Brokers      │  │ - InfluxDB│ │
│  │ - Alpha Vantage│  │ - MetaTrader   │  └───────────┘ │
│  └────────────────┘  └────────────────┘                 │
│                                                           │
│  ┌────────────────┐  ┌────────────────┐                 │
│  │  Notification  │  │   External     │                 │
│  │    Adapters    │  │   Services     │                 │
│  ├────────────────┤  ├────────────────┤                 │
│  │ - Email/SMTP   │  │ - News APIs    │                 │
│  │ - Telegram     │  │ - LLM Services │                 │
│  │ - Discord      │  │ - Logging      │                 │
│  │ - SMS          │  │ - Monitoring   │                 │
│  └────────────────┘  └────────────────┘                 │
└───────────────────────────────────────────────────────────┘
```

### 3.2 Core Components

#### 3.2.1 Strategy Orchestration Engine
**Responsibility:** Load, execute, and coordinate multiple trading models

**Key Functions:**
- Dynamic model loading from strategy directory
- Parallel execution of independent strategies
- Input standardization (market data → model format)
- Output aggregation (model signals → execution plan)
- Model performance tracking

#### 3.2.2 Risk Management Engine
**Responsibility:** Enforce risk limits and protect capital

**Key Functions:**
- Pre-trade risk validation
- Position sizing calculations
- Exposure monitoring (per-model, per-market, global)
- Drawdown tracking and limits
- Emergency circuit breaker

#### 3.2.3 Portfolio Manager
**Responsibility:** Track all positions and account state

**Key Functions:**
- Real-time position tracking
- P&L calculation (realized/unrealized)
- Balance management across markets
- Transaction history
- Performance metrics

#### 3.2.4 Market Data Adapters (Ports)
**Responsibility:** Abstract market-specific data retrieval

**Interface Contract:**
```
IMarketDataProvider {
  getHistoricalData(symbol, timeframe, start, end) → OHLCV[]
  getRealtimeData(symbol) → Tick
  subscribeToUpdates(symbol, callback)
  getMarketInfo(symbol) → MarketMetadata
}
```

#### 3.2.5 Execution Adapters (Ports)
**Responsibility:** Abstract broker-specific order execution

**Interface Contract:**
```
IExecutionProvider {
  placeOrder(order) → OrderConfirmation
  cancelOrder(orderId) → CancelConfirmation
  getOpenOrders() → Order[]
  getAccountBalance() → Balance
  getPositions() → Position[]
}
```

---

## 4. Functional Requirements

### 4.1 Strategy Model Interface

#### FR-1: Standardized Strategy Template
**Priority:** CRITICAL  
**Description:** All trading models must implement a standard interface

**Interface Definition:**
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
    
    # Configuration
    def get_required_indicators(self) -> List[Indicator]:
        """Declare indicators needed (SMA, RSI, etc.)"""
        pass
    
    def get_risk_parameters(self) -> RiskParams:
        """Return default risk settings for this strategy"""
        pass
    
    # Core Logic
    def on_bar(self, context: StrategyContext) -> Signal:
        """
        Called on each new bar/candle
        
        Args:
            context: Standardized input containing:
                - market_data: OHLCV + indicators
                - account: balance, positions
                - environment: BACKTEST | PAPER | LIVE
                - timestamp: current bar time
        
        Returns:
            Signal: {
                action: BUY | SELL | HOLD | CLOSE,
                symbol: str,
                position_size: float (0-1, % of capital),
                stop_loss: float (price),
                take_profit: float (price),
                confidence: float (0-1),
                metadata: dict (for logging)
            }
        """
        pass
    
    def on_order_filled(self, order: Order):
        """Called when order executes"""
        pass
    
    def on_order_rejected(self, order: Order, reason: str):
        """Called when order fails"""
        pass
```

**Acceptance Criteria:**
- Models can be written in Python (primary) or wrapped from other languages
- No direct market/broker dependencies in model code
- Same model code runs in backtest, paper, and live
- Model hot-reloading without system restart

---

#### FR-2: Multi-Strategy Concurrent Execution
**Priority:** HIGH  
**Description:** System can run multiple strategies simultaneously on different or same symbols

**Requirements:**
- Each strategy instance isolated (separate state)
- Parallel execution when strategies are independent
- Signal conflict resolution when strategies target same symbol
- Per-strategy P&L tracking
- Per-strategy risk allocation

**Signal Aggregation Logic:**
```
IF multiple strategies signal same symbol:
  - Advisory Mode: Show all signals
  - Operator Mode: 
    - CONSENSUS: Execute if >50% agree (configurable threshold)
    - WEIGHTED: Weight by strategy confidence scores
    - PRIORITY: Execute highest-priority strategy only
    - INDEPENDENT: Execute all (separate position per strategy)
```

**Acceptance Criteria:**
- Run 10+ strategies concurrently without performance degradation
- Strategy crash isolation (one failure doesn't affect others)
- Clear signal attribution in logs
- Conflict resolution configurable per deployment

---

### 4.2 Operating Modes

#### FR-3: Advisory Mode
**Priority:** HIGH  
**Description:** Generate trade signals without executing orders

**Behavior:**
- Compute all strategy signals normally
- Display signals in UI with timestamp, symbol, action, reasoning
- Log signals to database
- NO orders sent to broker
- Track "paper performance" if enabled

**Use Cases:**
- Strategy validation
- Confidence building before live trading
- Signal monitoring for manual execution
- Education and learning

**Acceptance Criteria:**
- Clear visual indication system is in advisory mode
- Export signals to CSV/JSON
- Optional paper tracking of "what would have happened"

---

#### FR-4: Operator Mode
**Priority:** CRITICAL  
**Description:** Full automated trading with real order execution

**Behavior:**
- Generate signals → Risk validation → Execute orders
- Real money at risk
- Requires explicit user confirmation to enable
- Emergency stop button always accessible

**Safety Requirements:**
- Double confirmation before first live trade
- Daily loss limit enforcement
- Manual override capability
- Automatic mode downgrade on repeated errors

**Acceptance Criteria:**
- Cannot accidentally enable (requires config + UI confirmation)
- All orders logged before execution
- Position limits strictly enforced
- Graceful degradation on API errors

---

### 4.3 Multi-Market Orchestration

#### FR-5: Market Independence
**Priority:** CRITICAL  
**Description:** Adding a new market requires only adapter implementation

**Requirements:**
- Core engine has ZERO market-specific code
- Market selection via configuration file
- Each market operates independently
- Shared risk limits across markets (optional)

**Configuration Example:**
```yaml
markets:
  crypto:
    enabled: true
    provider: binance
    symbols: [BTCUSDT, ETHUSDT]
    strategies: [momentum_v1, mean_reversion_v2]
    
  forex:
    enabled: true
    provider: oanda
    symbols: [EUR_USD, GBP_USD]
    strategies: [breakout_v1]
    
  stocks:
    enabled: false
    provider: interactive_brokers
```

**Acceptance Criteria:**
- Enable/disable markets without code changes
- Markets can run on different timeframes (1m crypto, 1h forex)
- Market failure isolation (forex crash doesn't stop crypto)

---

#### FR-6: Unified Market Data Pipeline
**Priority:** HIGH  
**Description:** Consistent data handling regardless of source

**Standardized Data Format:**
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
    market_type: MarketType
    timeframe: Timeframe
```

**Pipeline Stages:**
1. **Raw Data Fetch** (market-specific adapter)
2. **Normalization** (to standard format)
3. **Indicator Calculation** (TA-Lib, pandas-ta)
4. **Context Assembly** (data + account state)
5. **Strategy Execution**

**Acceptance Criteria:**
- Indicator library supports all markets
- Price precision handled correctly (crypto: 8 decimals, forex: 5 decimals)
- Timezone consistency (UTC everywhere)
- Missing data handling (gaps, holidays)

---

### 4.4 Backtesting Engine

#### FR-7: Historical Simulation
**Priority:** HIGH  
**Description:** Test strategies on historical data with realistic execution simulation

**Features:**
- Date range selection
- Slippage modeling (configurable per market)
- Commission modeling (maker/taker fees)
- Order fill simulation (market/limit logic)
- Walk-forward optimization
- Multiple strategy comparison

**Metrics Reported:**
- Total return, annualized return
- Sharpe ratio, Sortino ratio
- Max drawdown, average drawdown
- Win rate, profit factor
- Number of trades
- Average trade duration

**Acceptance Criteria:**
- Backtest results match manual calculation
- No look-ahead bias in indicators
- Realistic fill assumptions (limit orders may not fill)
- Performance: backtest 2 years data in <5 minutes

---

#### FR-8: Paper Trading (Live Simulation)
**Priority:** HIGH  
**Description:** Real-time simulation using live market data without real orders

**Behavior:**
- Connects to live data feeds
- Generates signals in real-time
- Simulates order execution with current prices
- Tracks "paper portfolio" separately from live
- Can run alongside live trading for comparison

**Acceptance Criteria:**
- <500ms latency from data to signal
- Paper and live use identical strategy code
- Paper performance tracking persistent across restarts
- Easy comparison: paper vs live results

---

### 4.5 Risk Management

#### FR-9: Multi-Level Risk Limits
**Priority:** CRITICAL  
**Description:** Configurable risk controls at multiple hierarchical levels

**Risk Hierarchy:**
```
Global Limits (Entire System)
  ├── Per-Market Limits (Crypto, Forex, Stocks)
  │    ├── Per-Strategy Limits (within market)
  │    └── Per-Symbol Limits (position concentration)
  └── Time-Based Limits (daily, weekly)
```

**Limit Types:**
- **Max Position Size:** % of capital per trade
- **Max Leverage:** Multiplier limit
- **Max Drawdown:** From peak equity
- **Daily Loss Limit:** Dollar or % loss
- **Max Open Positions:** Number of concurrent trades
- **Max Exposure:** Total capital at risk

**Acceptance Criteria:**
- Limits enforced BEFORE order submission
- Breach triggers alert + optional system pause
- Limits adjustable per environment (backtest loose, live strict)
- Override requires administrator password

---

#### FR-10: Emergency Shutdown System
**Priority:** CRITICAL  
**Description:** Immediate system halt with position liquidation options

**Trigger Conditions:**
- Manual emergency stop button
- Critical error detection
- Drawdown limit breach
- API connection loss >N seconds
- Anomaly detection (unusual order volume)

**Shutdown Modes:**
1. **SOFT:** Stop new orders, manage existing positions normally
2. **HARD:** Stop new orders, close all positions at market
3. **FREEZE:** Stop everything, manual intervention required

**Acceptance Criteria:**
- Emergency stop responds within 1 second
- Positions closed in priority order (riskiest first)
- Full audit log of shutdown event
- Notification sent to all configured channels

---

### 4.6 User Interface Requirements

#### FR-11: Real-Time Monitoring Dashboard
**Priority:** HIGH  
**Description:** Live visualization of system state and performance

**Core Screens:**

**1. Overview Dashboard**
- System status (operational, advisory, stopped)
- Global P&L (daily, total)
- Active positions count
- Current signals
- Risk utilization (% of limits used)

**2. Market View**
- Per-market tabs (Crypto | Forex | Stocks)
- Live price charts with indicator overlays
- Open positions on charts
- Recent signals timeline

**3. Strategy Performance**
- Strategy comparison table (P&L, win rate, trades)
- Individual strategy detail view
- Strategy enable/disable toggles

**4. Risk Monitor**
- Current vs limit bars (visual)
- Exposure breakdown (pie chart)
- Drawdown chart
- Alert history

**5. Order Management**
- Pending orders list
- Order history with filters
- Manual order entry (override)
- Bulk cancel functionality

**6. Logs & Audit**
- Real-time log stream
- Filterable by level, module, market
- Trade journal (all fills with reasoning)

**Acceptance Criteria:**
- Dashboard updates every 1 second (WebSocket)
- Responsive design (1920x1080 minimum)
- Accessible via localhost (not internet-facing initially)
- Export capabilities (charts, tables)

---

#### FR-12: Configuration Management
**Priority:** MEDIUM  
**Description:** User-friendly configuration without code editing

**Configurable Items:**
- Market enables/disables
- Strategy assignments per market
- Risk limits and parameters
- Data providers and credentials
- Notification preferences
- Logging verbosity

**Interface:**
- Web form or desktop settings panel
- Validation on save (prevent invalid configs)
- Config versioning (rollback capability)
- Import/export configs (backup/share)

**Acceptance Criteria:**
- No manual JSON/YAML editing required for common tasks
- Changes apply without restart when possible
- Validation prevents system breakage
- Config history tracked (who changed what when)

---

## 5. Non-Functional Requirements

### 5.1 Performance

#### NFR-1: Latency Requirements
**Priority:** HIGH

| Operation | Target Latency | Maximum Latency |
|-----------|---------------|-----------------|
| Strategy computation | <50ms | 100ms |
| Risk validation | <10ms | 25ms |
| Order submission | <200ms | 500ms |
| Market data ingestion | <100ms | 200ms |
| Dashboard update | <1s | 2s |

**Measurement:** 95th percentile under normal load (5 strategies, 10 symbols)

---

#### NFR-2: Throughput
**Priority:** MEDIUM
- Process 100+ signals per second
- Handle 1000+ market data updates per second
- Support 50+ concurrent open positions

---

#### NFR-3: Resource Utilization
**Priority:** MEDIUM
- CPU: <50% average on modern laptop (4-core, 2.5GHz)
- RAM: <2GB for core system + 500MB per strategy
- Disk I/O: <10MB/s sustained writes (logging)
- Network: <1Mbps (data feeds + API calls)

**Scalability Target:** Support 20 strategies before hardware upgrade needed

---

### 5.2 Reliability

#### NFR-4: Availability
**Priority:** CRITICAL
- System uptime: 99.5% during trading hours
- Planned maintenance window: Weekends only
- Crash recovery: Automatic restart with state restoration
- Mean time to recovery: <5 minutes

---

#### NFR-5: Data Integrity
**Priority:** CRITICAL
- Zero data loss on clean shutdown
- Transaction atomicity (order + position update together)
- Daily automated backups (database, configs)
- Backup retention: 30 days minimum

---

#### NFR-6: Fault Tolerance
**Priority:** HIGH
- Graceful degradation on API failures
- Retry logic with exponential backoff
- Circuit breaker pattern for external services
- Fallback data sources when primary unavailable

---

### 5.3 Security

#### NFR-7: Credential Management
**Priority:** CRITICAL
- API keys encrypted at rest (AES-256)
- Never logged or displayed in UI
- Stored separately from code repository
- Key rotation support

---

#### NFR-8: Access Control
**Priority:** HIGH  
**Phase 1 (Personal Use):**
- Local-only access (no network exposure)
- Single user (system owner)
- Operating system authentication

**Phase 2+ (Multi-User):**
- Password-protected dashboard
- Role-based access (admin, viewer)
- Session management with timeout

---

#### NFR-9: Audit Trail
**Priority:** HIGH
- All trades logged (before and after execution)
- Configuration changes logged
- Manual interventions logged
- Log retention: 12 months minimum
- Tamper-evident logging (append-only)

---

### 5.4 Maintainability

#### NFR-10: Code Quality
**Priority:** MEDIUM
- Test coverage: >80% for core engine
- Linting compliance: PEP8 (Python)
- Documentation: Docstrings for all public methods
- Type hints: Required for all function signatures

---

#### NFR-11: Modularity
**Priority:** HIGH
- Strategy hot-reload without restart
- Adapter replacement without core changes
- Feature flags for gradual rollout
- Backward compatibility for config files (1 year)

---

### 5.5 Usability

#### NFR-12: Learnability
**Priority:** MEDIUM
- Quick start guide: 15 minutes to first backtest
- Example strategies provided (3+ different styles)
- In-app help and tooltips
- Video tutorials (external, YouTube)

---

#### NFR-13: Error Handling
**Priority:** HIGH
- User-friendly error messages (no stack traces in UI)
- Suggested fixes for common errors
- Categorized errors (critical, warning, info)
- Error recovery guidance

---

## 6. Technical Design Specifications

### 6.1 Technology Stack Recommendations

#### Core Application
**Language:** Python 3.11+  
**Rationale:** Rich ecosystem (pandas, NumPy, TA-Lib), rapid development, extensive finance libraries

**Alternative:** Rust or Go for future HFT engine rewrite (performance-critical paths)

#### Data Storage
**Time-Series Database:** InfluxDB or TimescaleDB (PostgreSQL extension)  
**Rationale:** Optimized for OHLCV data, fast queries on time ranges

**Relational Database:** PostgreSQL  
**Rationale:** Transactions, positions, configs, audit logs

**Caching:** Redis  
**Rationale:** Real-time data, session state, rate limiting

#### Message Queue
**Choice:** RabbitMQ or Apache Kafka  
**Rationale:** Decouple components, async processing, event sourcing

**Use Cases:**
- Market data distribution
- Order flow
- Notification dispatch

#### Web Framework (Dashboard)
**Backend:** FastAPI  
**Frontend:** React or Svelte  
**Real-Time:** WebSocket (Socket.io)

**Alternative:** Electron for desktop app (cross-platform)

#### Infrastructure
**Deployment:** Docker Compose (Phase 1)  
**Future:** Kubernetes (Phase 3, if cloud migration)

---

### 6.2 Data Models

#### Strategy Signal Model
```python
@dataclass
class Signal:
    strategy_id: str
    timestamp: datetime
    symbol: str
    action: Enum[BUY, SELL, HOLD, CLOSE]
    position_size: float  # 0.0 - 1.0 (% of allocated capital)
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]
    confidence: float  # 0.0 - 1.0
    reasoning: str  # Human-readable explanation
    metadata: Dict[str, Any]  # Custom strategy data
```

#### Order Model
```python
@dataclass
class Order:
    order_id: str
    strategy_id: str
    symbol: str
    side: Enum[BUY, SELL]
    order_type: Enum[MARKET, LIMIT, STOP_LOSS]
    quantity: Decimal
    price: Optional[Decimal]  # For limit orders
    status: Enum[PENDING, FILLED, CANCELLED, REJECTED]
    created_at: datetime
    filled_at: Optional[datetime]
    filled_price: Optional[Decimal]
    commission: Decimal
    market: Enum[CRYPTO, FOREX, STOCK]
    broker: str
```

#### Position Model
```python
@dataclass
class Position:
    position_id: str
    strategy_id: str
    symbol: str
    side: Enum[LONG, SHORT]
    quantity: Decimal
    entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    opened_at: datetime
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]
    market: Enum[CRYPTO, FOREX, STOCK]
```

---

### 6.3 API Abstraction Design

#### Market Data Provider Interface
```python
class IMarketDataProvider(ABC):
    @abstractmethod
    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime,
        end: datetime
    ) -> List[OHLCV]:
        """Fetch historical data"""
        pass
    
    @abstractmethod
    async def get_latest_price(self, symbol: str) -> Tick:
        """Get current market price"""
        pass
    
    @abstractmethod
    async def subscribe_to_updates(
        self,
        symbol: str,
        callback: Callable[[Tick], None]
    ):
        """WebSocket subscription for real-time data"""
        pass
    
    @abstractmethod
    async def get_market_metadata(self, symbol: str) -> MarketMetadata:
        """Get symbol info (min order size, tick size, etc.)"""
        pass
```

**Implementations:**
- `BinanceMarketDataProvider`
- `OandaMarketDataProvider`
- `InteractiveBrokersMarketDataProvider`
- `SimulatedMarketDataProvider` (for backtesting)

---

#### Execution Provider Interface
```python
class IExecutionProvider(ABC):
    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderConfirmation:
        """Submit order to broker"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> CancelConfirmation:
        """Cancel pending order"""
        pass
    
    @abstractmethod
    async def get_open_orders(self) -> List[Order]:
        """Fetch all pending orders"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Fetch all open positions"""
        pass
    
    @abstractmethod
    async def get_account_balance(self) -> AccountBalance:
        """Get current account balance"""
        pass
```

**Implementations:**
- `BinanceExecutionProvider`
- `OandaExecutionProvider`
- `InteractiveBrokersExecutionProvider`
- `SimulatedExecutionProvider` (paper trading)

---

### 6.4 Risk Management Framework

#### Risk Rule Engine
```python
class RiskRule(ABC):
    """Base class for all risk rules"""
    
    @abstractmethod
    def validate(
        self,
        signal: Signal,
        portfolio: Portfolio,
        config: RiskConfig
    ) -> RiskDecision:
        """
        Returns:
            RiskDecision {
                approved: bool,
                reason: str,
                modified_signal: Optional[Signal]  # Adjusted position size
            }
        """
        pass
```

**Built-In Rules:**
1. **MaxPositionSizeRule:** Limit single position to X% of capital
2. **MaxDrawdownRule:** Stop trading if DD exceeds threshold
3. **DailyLossLimitRule:** Stop if daily loss > $X or Y%
4. **MaxOpenPositionsRule:** Limit concurrent trades
5. **MaxLeverageRule:** Limit borrowed capital
6. **CorrelationRule:** Prevent over-concentration in correlated assets
7. **MaxExposurePerMarketRule:** Limit % of capital per market
8. **TimeOfDayRule:** Restrict trading to certain hours

**Rule Execution Order:**
1. Pre-validation (fast checks: balance, limits)
2. Complex validation (correlation, exposure)
3. Position sizing adjustment (if rules recommend reduction)
4. Final approval/rejection

---

### 6.5 Future AI/LLM Integration Architecture

#### News Sentiment Module (Future)
```
┌──────────────────────────────────────────────────────┐
│             News Sentiment Pipeline                   │
│                                                        │
│  News Sources → Aggregator → LLM Analyzer →          │
│  Sentiment Scorer → Impact Calculator → Strategy      │
│  Confidence Modifier                                   │
└──────────────────────────────────────────────────────┘
```

**Architecture:**
1. **News Aggregation Layer**
   - RSS feeds (Bloomberg, Reuters, CoinDesk)
   - Twitter/X API (key accounts)
   - Financial news APIs (NewsAPI, Alpha Vantage)

2. **LLM Analysis Layer**
   - Prompt engineering for financial impact assessment
   - Multi-source validation
   - Sentiment scoring: -1.0 (very negative) to +1.0 (very positive)
   - Relevance scoring: 0.0 (irrelevant) to 1.0 (highly relevant)

3. **Impact Translation Layer**
   ```python
   @dataclass
   class MarketImpact:
       symbol: str
       sentiment: float  # -1.0 to +1.0
       magnitude: float  # 0.0 to 1.0 (how big is the impact)
       confidence: float  # 0.0 to 1.0 (LLM confidence)
       timeframe: str  # immediate, short-term, long-term
       summary: str
       sources: List[str]
   ```

4. **Strategy Integration**
   - News impact modifies strategy confidence scores
   - Extreme negative sentiment can pause strategies
   - Positive sentiment can increase position sizing
   - Configurable per-strategy sensitivity to news

**Future Extensions:**
- On-chain analysis (crypto)
- Earnings call transcripts
- Central bank speeches
- Social media sentiment

---

## 7. Security Requirements

### 7.1 Credential Management

#### SEC-1: API Key Storage
**Requirements:**
- Encrypted at rest using AES-256-GCM
- Encryption keys stored in OS keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- Never committed to version control
- Environment-specific credentials (dev keys ≠ prod keys)

**Implementation:**
```python
# Example secure config structure
credentials/
  ├── .gitignore          # Exclude this directory
  ├── dev.encrypted       # Development API keys
  ├── prod.encrypted      # Production API keys
  └── master.key          # Stored in OS keychain only
```

---

#### SEC-2: Secure Configuration
**Requirements:**
- Separate config files per environment
- Sensitive values encrypted
- Config validation on load (type checking, range validation)
- Version control: commit templates only, not actual values

**Configuration Template:**
```yaml
# config.template.yaml (version controlled)
binance:
  api_key: ${BINANCE_API_KEY}  # Loaded from encrypted store
  api_secret: ${BINANCE_API_SECRET}
  testnet: ${USE_TESTNET}

oanda:
  api_key: ${OANDA_API_KEY}
  account_id: ${OANDA_ACCOUNT_ID}
```

---

### 7.2 System Security

#### SEC-3: Network Security
**Phase 1 (Local Use):**
- Dashboard bound to localhost only (127.0.0.1)
- No external network exposure
- Firewall rules (if configured): allow outbound only

**Phase 2+ (Remote Access):**
- HTTPS with TLS 1.3
- SSH tunnel or VPN access only
- Rate limiting on authentication endpoints
- IP whitelisting

---

#### SEC-4: Logging Security
**Requirements:**
- Never log API keys, passwords, or secrets
- Sanitize logs before storage (regex filters)
- Sensitive data masking: `binance_key: ********3a2f`
- Audit logs append-only (prevent tampering)
- Log rotation with compression and archival

---

#### SEC-5: Fail-Safe Mechanisms
**Requirements:**
- System defaults to safest state on error
- Authentication failure → deny access (not grant)
- Risk limit parsing error → use strictest limits
- Unknown signal → HOLD (do not trade)
- API connection loss → close positions and stop trading

---

## 8. Deployment Architecture

### 8.1 Phase 1: Local Development Environment

**Deployment Method:** Docker Compose

**Services:**
- `trading-engine`: Core application (Python)
- `postgres`: Relational database
- `timescaledb`: Time-series data
- `redis`: Caching and pub/sub
- `dashboard`: Web UI (FastAPI + React)

**Docker Compose Structure:**
```yaml
version: '3.8'

services:
  trading-engine:
    build: ./engine
    environment:
      - ENV=development
      - LOG_LEVEL=DEBUG
    volumes:
      - ./credentials:/app/credentials:ro
      - ./strategies:/app/strategies:ro
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: timescale/timescaledb:latest-pg14
    volumes:
      - pgdata:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
  
  dashboard:
    build: ./dashboard
    ports:
      - "127.0.0.1:8080:8080"  # Localhost only
    depends_on:
      - trading-engine
```

---

### 8.2 Hardware Requirements

**Minimum Specifications (Phase 1):**
- CPU: 4 cores, 2.0 GHz
- RAM: 8 GB
- Storage: 100 GB SSD (for historical data)
- Network: 10 Mbps upload/download

**Recommended Specifications:**
- CPU: 8 cores, 3.0 GHz
- RAM: 16 GB
- Storage: 500 GB NVMe SSD
- Network: 50 Mbps with low latency (<50ms to exchange)

**Operating System:**
- Linux (Ubuntu 22.04 LTS preferred)
- macOS 12+ (for development)
- Windows 10/11 with WSL2 (acceptable)

---

### 8.3 Backup & Disaster Recovery

#### Backup Strategy
**Daily Automated Backups:**
- Database dump (full backup)
- Configuration files
- Strategy code snapshot
- Log archives (compressed)

**Backup Retention:**
- Daily: 7 days
- Weekly: 4 weeks
- Monthly: 12 months

**Backup Storage:**
- Local: External drive or NAS
- Remote: Encrypted cloud storage (AWS S3, Backblaze)

**Recovery Procedures:**
1. Fresh system setup
2. Restore database from backup
3. Restore configuration files
4. Decrypt credentials
5. Verify system state before resuming trading

**Recovery Time Objective (RTO):** <1 hour  
**Recovery Point Objective (RPO):** <24 hours (daily backups)

---

## 9. Legal & Compliance Considerations

### 9.1 Regulatory Landscape (High-Level Overview)

**Disclaimer:** This section provides general awareness, NOT legal advice. Consult licensed attorneys and financial regulators before commercial deployment.

#### Personal Trading (Phase 1)
**Status:** Generally unrestricted for personal use
- Trading your own capital is legal in most jurisdictions
- No special licenses required for self-directed trading
- Tax obligations: Capital gains/losses must be reported
- Broker terms: Ensure automated trading is permitted by your broker

#### Sharing with Friends (Phase 2)
**Status:** Gray area, potentially problematic
- **Risk:** Managing others' money may require investment adviser registration
- **Safe approach:** Friends use your software but trade their own accounts
- **Unsafe approach:** Pooling capital or executing trades on behalf of others

**Recommendations:**
- Each user maintains separate broker account
- Software provides signals/advisory only
- Clear disclaimers: "Not financial advice"
- No profit-sharing or management fees

#### Commercial Distribution (Phase 3)
**Status:** Highly regulated, varies by jurisdiction

**Potential Requirements:**
- **Investment Adviser Registration:** SEC (US), FCA (UK), ASIC (Australia)
- **Software Licensing:** Financial services software may need certification
- **Disclaimers:** Risk warnings, past performance disclosures
- **Data Protection:** GDPR (EU), CCPA (California) compliance
- **Anti-Money Laundering (AML):** KYC procedures if handling funds

**Red Flags to Avoid:**
- Guaranteeing returns
- Managing client funds directly
- Offering advice to the public without registration
- Misleading performance claims

---

### 9.2 Broker API Terms of Service

**Key Considerations:**
- **Rate Limits:** Respect API call limits (usually 1200-5000 requests/hour)
- **Prohibited Activities:** Market manipulation, spoofing, wash trading
- **Account Flags:** Excessive orders may trigger restrictions
- **API Abuse:** Automated ban for violating terms
- **Liability:** User responsible for software bugs and losses

**Best Practices:**
- Read full TOS for each broker/exchange
- Implement rate limiting on client side
- Start with paper trading accounts
- Monitor for suspicious activity patterns

---

### 9.3 Liability & Risk Disclosure

**System Liability:**
- Software provided "AS IS" without warranties
- Developers not liable for trading losses
- Users accept full financial risk
- Bugs or errors may result in losses

**Required Disclosures:**
- "Trading involves risk of loss"
- "Past performance does not guarantee future results"
- "Algorithmic trading can amplify losses"
- "System errors may occur"

**Insurance Considerations:**
- Personal liability insurance (Phase 2+)
- Errors & omissions insurance (Phase 3)
- Cyber liability insurance (if storing user data)

---

### 9.4 Data Privacy

**Personal Data Handling:**
- **Phase 1:** No user data (single user, local only)
- **Phase 2+:** 
  - Collect only necessary data (email, account IDs)
  - Secure storage (encrypted databases)
  - No selling or sharing of user data
  - Clear privacy policy

**Broker Data:**
- API credentials never shared with third parties
- Trade data stored locally (not in cloud)
- Compliance with broker data policies

---

## 10. Testing Strategy

### 10.1 Unit Testing
**Scope:** Individual components and functions  
**Coverage Target:** >80% for core engine  
**Framework:** pytest (Python)

**Critical Test Cases:**
- Risk rule validation logic
- Position sizing calculations
- Order transformation (signal → order)
- Market data normalization
- Indicator calculations

---

### 10.2 Integration Testing
**Scope:** Component interactions  
**Approach:** Mocked external APIs

**Test Scenarios:**
- Strategy → Signal → Risk → Order → Execution flow
- Market data ingestion → Strategy execution pipeline
- Emergency shutdown triggers
- Multi-strategy conflict resolution

---

### 10.3 End-to-End Testing
**Scope:** Full system in simulated environment  
**Approach:** Testnet accounts and replay data

**Test Scenarios:**
1. **Backtest Validation:** Known historical data, verify expected trades
2. **Paper Trading:** Run for 2 weeks, verify no real orders placed
3. **Live Testing (Minimal Capital):** Deploy with €10-50, verify correct execution

---

### 10.4 Performance Testing
**Load Testing:**
- Simulate 20 concurrent strategies
- 100+ symbols subscribed
- 1000 data updates per second

**Latency Testing:**
- Measure p50, p95, p99 latencies
- Identify bottlenecks (profiling)

**Stress Testing:**
- Network interruptions
- API failures and retries
- Database connection loss

---

### 10.5 Security Testing
**Penetration Testing:**
- Attempt unauthorized dashboard access
- SQL injection attempts
- Credential extraction attempts

**Vulnerability Scanning:**
- Dependency audit (npm audit, safety check)
- Static code analysis (Bandit, SonarQube)

---

## 11. Monitoring & Observability

### 11.1 Metrics Collection

**System Metrics:**
- CPU, RAM, disk usage
- Network latency to exchanges
- Request/response times
- Error rates

**Trading Metrics:**
- Signals generated per hour
- Orders placed vs filled
- Slippage (expected vs actual fill price)
- P&L (real-time and cumulative)

**Strategy Metrics:**
- Per-strategy P&L
- Win rate, profit factor
- Average trade duration
- Current drawdown

---

### 11.2 Alerting

**Alert Channels:**
- Email (critical errors)
- Telegram/Discord (real-time notifications)
- Dashboard notifications (in-app)
- SMS (optional, for emergencies)

**Alert Triggers:**
- System crash or restart
- API connection loss >60 seconds
- Daily loss limit approaching (80%, 90%, 100%)
- Max drawdown exceeded
- Unusual order activity detected
- Manual intervention required

**Alert Levels:**
- **INFO:** Routine events (position opened)
- **WARNING:** Attention needed (approaching limit)
- **ERROR:** Problem occurred (order rejected)
- **CRITICAL:** Immediate action required (emergency stop)

---

### 11.3 Logging

**Log Levels:**
- DEBUG: Verbose internal state (development only)
- INFO: Normal operations (order placed, position closed)
- WARNING: Degraded performance (high latency, retry attempts)
- ERROR: Failures (API error, order rejection)
- CRITICAL: System-threatening issues (crash, emergency stop)

**Log Storage:**
- Console output (development)
- File rotation (production): daily files, 30-day retention
- Centralized logging (future): ELK stack, Grafana Loki

**Structured Logging:**
```json
{
  "timestamp": "2025-12-08T14:35:22Z",
  "level": "INFO",
  "module": "execution_engine",
  "market": "CRYPTO",
  "symbol": "BTCUSDT",
  "event": "order_filled",
  "order_id": "12345",
  "strategy_id": "momentum_v1",
  "price": 42000.50,
  "quantity": 0.01
}
```

---

## 12. Development Roadmap

### Phase 0: Foundation (Weeks 1-4)
**Goal:** Core architecture and design finalization

**Deliverables:**
- [ ] Finalize technology stack decisions
- [ ] Set up development environment (Docker, CI/CD)
- [ ] Define all interfaces (IStrategy, IMarketData, IExecution)
- [ ] Create project structure and repositories
- [ ] Write architecture documentation
- [ ] Set up testing framework

**Team:** 1-2 developers

---

### Phase 1: Core Engine (Weeks 5-12)
**Goal:** Build foundational trading engine

**Deliverables:**
- [ ] Strategy orchestration engine
- [ ] Signal standardization and validation
- [ ] Portfolio manager (position tracking, P&L)
- [ ] Basic risk management (position size limits)
- [ ] Configuration system
- [ ] Logging infrastructure
- [ ] Unit tests for core components

**Milestone:** Can load and execute strategies (no real market data yet)

---

### Phase 2: Single-Market Implementation (Weeks 13-20)
**Goal:** Integrate first market (recommend Crypto for ease of access)

**Deliverables:**
- [ ] Binance market data adapter
- [ ] Binance execution adapter
- [ ] Data normalization pipeline
- [ ] Indicator calculation engine (TA-Lib integration)
- [ ] Historical data downloader
- [ ] Example strategy implementation (SMA crossover)
- [ ] Integration tests with Binance testnet

**Milestone:** Can fetch real crypto data and place testnet orders

---

### Phase 3: Backtesting Engine (Weeks 21-28)
**Goal:** Enable historical strategy validation

**Deliverables:**
- [ ] Simulated market data provider
- [ ] Simulated execution engine (slippage, fees)
- [ ] Backtest runner with date range selection
- [ ] Performance metrics calculation
- [ ] Walk-forward analysis
- [ ] Backtest result export (CSV, JSON)
- [ ] Example backtest reports

**Milestone:** Successfully backtest example strategy over 2+ years

---

### Phase 4: Paper Trading (Weeks 29-34)
**Goal:** Real-time simulation with live data

**Deliverables:**
- [ ] Real-time market data subscriptions (WebSocket)
- [ ] Simulated order execution with live prices
- [ ] Paper portfolio tracking
- [ ] Real-time signal generation
- [ ] Latency monitoring
- [ ] Paper vs live comparison tools

**Milestone:** Run paper trading for 2 weeks without errors

---

### Phase 5: Risk Management System (Weeks 35-40)
**Goal:** Production-grade risk controls

**Deliverables:**
- [ ] Rule-based risk engine
- [ ] Multi-level risk limits (global, market, strategy)
- [ ] Drawdown tracking and limits
- [ ] Daily loss limits
- [ ] Emergency shutdown system
- [ ] Risk dashboard UI
- [ ] Risk rule testing suite

**Milestone:** Risk system blocks all invalid trades in testing

---

### Phase 6: Advisory Mode (Weeks 41-46)
**Goal:** Signal generation without execution

**Deliverables:**
- [ ] Advisory mode toggle
- [ ] Signal display dashboard
- [ ] Signal export functionality
- [ ] Signal history and analysis
- [ ] "What if" paper tracking
- [ ] User documentation for advisory mode

**Milestone:** Generate signals for 1 week, manually verify quality

---

### Phase 7: Operator Mode (Weeks 47-54)
**Goal:** Full automated trading with real capital

**Deliverables:**
- [ ] Operator mode with safety confirmations
- [ ] Order execution pipeline
- [ ] Order status tracking
- [ ] Position management
- [ ] Emergency stop button
- [ ] Live trading dashboard
- [ ] Comprehensive integration tests

**Milestone:** Execute first real trade successfully with €10

---

### Phase 8: Multi-Market Expansion (Weeks 55-64)
**Goal:** Add Forex and prepare for Stocks

**Deliverables:**
- [ ] OANDA market data adapter
- [ ] OANDA execution adapter
- [ ] Market-agnostic strategy templates
- [ ] Multi-market dashboard view
- [ ] Per-market risk configuration
- [ ] Cross-market position monitoring
- [ ] Market-specific backtests

**Milestone:** Run crypto + forex simultaneously for 1 week

---

### Phase 9: UI/UX Enhancement (Weeks 65-72)
**Goal:** Professional monitoring dashboard

**Deliverables:**
- [ ] React/Svelte frontend
- [ ] Real-time chart library integration (TradingView, Lightweight Charts)
- [ ] WebSocket updates
- [ ] Interactive strategy controls
- [ ] Responsive design
- [ ] Dark mode
- [ ] Mobile-friendly layout (tablet support)

**Milestone:** Dashboard usable for daily monitoring

---

### Phase 10: Optimization & Scaling (Weeks 73-80)
**Goal:** Performance tuning for 20+ strategies

**Deliverables:**
- [ ] Performance profiling and optimization
- [ ] Database query optimization
- [ ] Caching implementation (Redis)
- [ ] Parallel strategy execution
- [ ] Resource usage monitoring
- [ ] Load testing results

**Milestone:** Support 20 strategies + 50 symbols without degradation

---

### Phase 11: Advanced Features (Weeks 81-90)
**Goal:** Preparation for AI integration

**Deliverables:**
- [ ] News API integrations (Alpha Vantage, NewsAPI)
- [ ] Placeholder for LLM sentiment analysis
- [ ] Impact score interface definition
- [ ] Strategy confidence modification system
- [ ] News dashboard panel
- [ ] Documentation for AI extension

**Milestone:** Architecture ready for AI module integration

---

### Phase 12: Production Hardening (Weeks 91-100)
**Goal:** Stability and reliability for continuous operation

**Deliverables:**
- [ ] 24/7 monitoring setup
- [ ] Automated alerting
- [ ] Backup automation
- [ ] Disaster recovery testing
- [ ] Security audit
- [ ] Penetration testing
- [ ] Complete user documentation

**Milestone:** System runs unattended for 1 month (95%+ uptime)

---

## 13. Success Criteria & KPIs

### 13.1 Technical KPIs
- **Uptime:** >99.5% during trading hours
- **Latency:** p95 strategy execution <100ms
- **Error Rate:** <0.1% of operations result in errors
- **Test Coverage:** >80% for core engine
- **Deployment Time:** <5 minutes for updates

### 13.2 Trading KPIs
- **Signal Accuracy:** Backtest win rate ≥50% before live deployment
- **Slippage:** <0.1% average deviation from expected price
- **Order Fill Rate:** >95% of orders filled successfully
- **Risk Compliance:** 100% of risk rules enforced (zero violations)

### 13.3 User Experience KPIs
- **Time to First Backtest:** <15 minutes (new user)
- **Dashboard Load Time:** <2 seconds
- **Critical Alert Delivery:** <60 seconds
- **System Recovery Time:** <5 minutes after crash

### 13.4 Financial KPIs
**Note:** Performance will vary by strategy and market conditions

**Realistic Expectations (First 6 Months):**
- **Goal:** Don't lose money (capital preservation)
- **Stretch Goal:** Beat buy-and-hold benchmark
- **Risk-Adjusted Goal:** Sharpe ratio >1.0

---

## 14. Risk Assessment & Mitigation

### 14.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API rate limiting | Medium | High | Client-side rate limiting, request queuing |
| Exchange downtime | High | Medium | Fallback exchanges, graceful degradation |
| Data quality issues | High | Medium | Data validation, outlier detection |
| Software bugs | Critical | Medium | Comprehensive testing, staged rollout |
| Database corruption | High | Low | Daily backups, transaction logging |

### 14.2 Financial Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Flash crash losses | Critical | Low | Stop-loss orders, circuit breakers |
| Overnight gap risk | Medium | Medium | Position sizing, reduced overnight exposure |
| Model overfitting | High | High | Walk-forward testing, out-of-sample validation |
| Black swan events | Critical | Very Low | Position limits, diversification |
| API execution delay | Medium | Medium | Latency monitoring, fallback manual execution |

### 14.3 Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Credential theft | Critical | Low | Encryption, OS keyring, 2FA on exchanges |
| Accidental live trading | High | Medium | Confirmation dialogs, separate environments |
| Configuration errors | High | Medium | Validation, version control, rollback capability |
| Hardware failure | Medium | Low | Cloud backup, redundant systems (future) |

### 14.4 Legal/Compliance Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Unauthorized advice | High | Low (Phase 1) | Clear disclaimers, advisory-only mode |
| Regulatory violation | Critical | Low (Phase 1) | Legal consultation before Phase 3 |
| Tax reporting issues | Medium | Medium | Transaction logging, export for accountants |
| Broker TOS violation | Medium | Low | Read and comply with all broker terms |

---

## 15. Appendices

### Appendix A: Glossary

**Advisory Mode:** System generates trade signals without executing orders  
**Backtest:** Historical simulation of strategy performance  
**Operator Mode:** Full automated trading with real order execution  
**Paper Trading:** Real-time simulation using live data without real money  
**Signal:** Trading recommendation generated by a strategy  
**Slippage:** Difference between expected and actual execution price  
**Strategy:** Algorithmic trading model implementing IStrategy interface  
**Tick:** Single price update (timestamp + price)  
**OHLCV:** Open, High, Low, Close, Volume (candlestick data)

### Appendix B: References

**Clean Architecture:**
- Martin, Robert C. "Clean Architecture" (2017)

**Algorithmic Trading:**
- Chan, Ernest. "Algorithmic Trading" (2009)
- Pardo, Robert. "The Evaluation and Optimization of Trading Strategies" (2008)

**Risk Management:**
- Tharp, Van K. "Trade Your Way to Financial Freedom" (2006)

**APIs & Documentation:**
- Binance API: https://binance-docs.github.io/apidocs/
- OANDA API: https://developer.oanda.com/
- Interactive Brokers API: https://www.interactivebrokers.com/api

---

## 16. Document Control

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-08 | System Architect | Initial PRS creation |

**Approval:**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | [Name] | [Date] | _________ |
| Technical Lead | [Name] | [Date] | _________ |
| Compliance | [Name] | [Date] | _________ |

**Distribution:**
- Development Team
- Product Management
- Legal/Compliance (for review)

---

**END OF DOCUMENT**