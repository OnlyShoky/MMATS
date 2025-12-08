# Multi-Market Operations

This document explains how **MMATS** handles simultaneous trading across multiple financial markets, market switching, and the different operational modes available.

---

## Multi-Market Philosophy

### Market Agnosticism

MMATS is designed to be **market agnostic**—the core engine contains **zero market-specific code**. This is achieved through:

1. **Standardized Interfaces**: All markets implement the same ports
2. **Configuration-Driven**: Markets enabled/disabled via config files
3. **Adapter Pattern**: Market-specific logic isolated in adapters
4. **Unified Data Format**: All market data normalized to common structure

### Supported Markets

| Market | Provider Examples | Asset Types | Trading Hours |
|--------|-------------------|-------------|---------------|
| **Crypto** | Binance, Coinbase, Kraken | BTC, ETH, altcoins | 24/7 |
| **Forex** | OANDA, Interactive Brokers | Currency pairs | 24/5 (Mon-Fri) |
| **Stocks** | Interactive Brokers | Equities, ETFs | Exchange hours |

---

## Market Configuration

### Configuration Structure

```yaml
markets:
  crypto:
    enabled: true
    provider: binance
    symbols:
      - BTCUSDT
      - ETHUSDT
      - SOLUSDT
    strategies:
      - momentum_v1
      - mean_reversion_v2
    timeframe: 5m
    risk_allocation_pct: 40
    
  forex:
    enabled: true
    provider: oanda
    symbols:
      - EUR_USD
      - GBP_USD
      - USD_JPY
    strategies:
      - breakout_v1
      - trend_following_v1
    timeframe: 1H
    risk_allocation_pct: 40
    
  stocks:
    enabled: false
    provider: interactive_brokers
    symbols: []
    strategies: []
    risk_allocation_pct: 20
```

### Key Configuration Options

| Option | Description |
|--------|-------------|
| `enabled` | Toggle market on/off without code changes |
| `provider` | Which broker/exchange adapter to use |
| `symbols` | List of tradeable assets |
| `strategies` | Which strategies run on this market |
| `timeframe` | Data granularity (1m, 5m, 1H, 1D) |
| `risk_allocation_pct` | Maximum % of capital for this market |

---

## Market Independence

### Isolation Principles

```
┌─────────────────────────────────────────────────────────┐
│                    CORE ENGINE                           │
│           (Market-Independent Logic)                     │
│                                                          │
│  • Signal processing                                     │
│  • Risk validation                                       │
│  • Portfolio management                                  │
│  • Performance tracking                                  │
└──────────────────────┬──────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│    CRYPTO    │ │    FOREX     │ │    STOCKS    │
│    ADAPTER   │ │    ADAPTER   │ │    ADAPTER   │
│              │ │              │ │              │
│  • Binance   │ │  • OANDA     │ │  • IB API    │
│  • WebSocket │ │  • REST API  │ │  • TWS       │
│  • 8 decimal │ │  • 5 decimal │ │  • Variable  │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Failure Isolation

> [!IMPORTANT]
> A failure in one market does NOT affect other markets.

| Scenario | Behavior |
|----------|----------|
| Binance API down | Crypto strategies pause, Forex continues |
| OANDA auth error | Forex stops, Crypto unaffected |
| Network timeout | Affected market retries, others unaffected |

---

## Unified Data Pipeline

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                  MARKET DATA SOURCES                     │
│                                                          │
│  Binance ──┐                                             │
│            │                                             │
│  OANDA  ───┼───> NORMALIZATION ───> STANDARDIZED DATA   │
│            │          │                                  │
│  IB ───────┘          ▼                                  │
│                                                          │
│              ┌─────────────────────┐                     │
│              │    MarketData       │                     │
│              │    • symbol         │                     │
│              │    • timestamp      │                     │
│              │    • OHLCV          │                     │
│              │    • market_type    │                     │
│              │    • timeframe      │                     │
│              └─────────────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

### Market-Specific Normalization

| Aspect | Crypto | Forex | Stocks |
|--------|--------|-------|--------|
| Price Precision | 8 decimals | 5 decimals | 2-4 decimals |
| Lot Size | Variable | 100,000 units | 1 share |
| Symbol Format | BTCUSDT | EUR_USD | AAPL |
| Volume Unit | Coins | Lots | Shares |

All differences are handled in adapters—strategies see standardized data.

---

## Operating Modes

### Advisory Mode

**Purpose**: Generate signals WITHOUT executing orders.

```
┌─────────────────────────────────────────────────────────┐
│                   ADVISORY MODE                          │
│                                                          │
│  Market   │ Symbol    │ Signal   │ Confidence │ Time    │
│  ─────────┼───────────┼──────────┼────────────┼──────── │
│  Crypto   │ BTCUSDT   │ BUY      │ 0.75       │ 10:05   │
│  Forex    │ EUR_USD   │ HOLD     │ 0.60       │ 10:05   │
│  Crypto   │ ETHUSDT   │ SELL     │ 0.82       │ 10:05   │
│                                                          │
│  [All signals logged - NO orders executed]              │
└─────────────────────────────────────────────────────────┘
```

**Use Cases**:
- Strategy validation before live trading
- Building confidence in new models
- Manual execution based on signals
- Educational purposes

**Features**:
- Optional "paper tracking" — simulate what would have happened
- Export signals to CSV/JSON
- Clear visual indication of advisory mode

See: [[architecture_overview.md#Operating-Modes]] for mode architecture.

### Operator Mode

**Purpose**: Full automated trading with real order execution.

```
┌─────────────────────────────────────────────────────────┐
│                   OPERATOR MODE                          │
│                     ⚠️ LIVE TRADING                      │
│                                                          │
│  Signal → Risk Validation → Order Execution              │
│                                                          │
│  Safety Requirements:                                    │
│  ✓ Double confirmation before first trade               │
│  ✓ Daily loss limit active                              │
│  ✓ Emergency stop button accessible                     │
│  ✓ All orders logged before execution                   │
└─────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> Operator mode uses real capital. Ensure you understand the risks and have tested thoroughly in paper mode first.

**Safety Checklist**:
- [ ] Paper traded for minimum 2 weeks
- [ ] Risk limits configured appropriately
- [ ] Emergency contacts set up
- [ ] Understand all active strategies
- [ ] Double confirmation completed

---

## Multi-Strategy Execution

### Concurrent Strategies

MMATS can run multiple strategies simultaneously:

```
┌─────────────────────────────────────────────────────────┐
│                MULTI-STRATEGY EXECUTION                  │
│                                                          │
│  CRYPTO MARKET                                           │
│  ├─ momentum_v1 ──────> [BTC: BUY, ETH: HOLD]           │
│  └─ mean_reversion_v2 ─> [BTC: HOLD, ETH: SELL]         │
│                                                          │
│  FOREX MARKET                                            │
│  ├─ breakout_v1 ──────> [EUR_USD: BUY]                  │
│  └─ trend_v1 ──────────> [EUR_USD: HOLD]                │
│                                                          │
│              ↓                                           │
│      SIGNAL AGGREGATION                                  │
│              ↓                                           │
│      RISK VALIDATION                                     │
│              ↓                                           │
│      ORDER EXECUTION                                     │
└─────────────────────────────────────────────────────────┘
```

### Signal Conflict Resolution

When multiple strategies signal on the same symbol:

| Mode | Behavior |
|------|----------|
| **CONSENSUS** | Execute if >50% of strategies agree |
| **WEIGHTED** | Weight by strategy confidence scores |
| **PRIORITY** | Execute highest-priority strategy only |
| **INDEPENDENT** | Execute all (separate position per strategy) |

```yaml
# Configuration example
signal_aggregation:
  mode: CONSENSUS
  threshold: 0.5  # 50% agreement required
  
  # Or for weighted mode:
  # mode: WEIGHTED
  # weights:
  #   momentum_v1: 0.6
  #   mean_reversion_v2: 0.4
```

---

## Cross-Market Risk Management

### Global Limits

Risk limits apply across ALL markets:

```
┌─────────────────────────────────────────────────────────┐
│              CROSS-MARKET RISK LIMITS                    │
│                                                          │
│  GLOBAL EXPOSURE: 45% of $10,000 = $4,500               │
│  ├─ Crypto:  $2,000 (44%)                               │
│  ├─ Forex:   $1,800 (40%)                               │
│  └─ Stocks:  $700  (16%)                                │
│                                                          │
│  MAX EXPOSURE LIMIT: 50%                                 │
│  STATUS: ✅ WITHIN LIMITS                                │
└─────────────────────────────────────────────────────────┘
```

### Per-Market Allocation

Each market has its own allocation limit:

| Market | Allocation | Max Leverage | Max Positions |
|--------|------------|--------------|---------------|
| Crypto | 40% | 3x | 5 |
| Forex | 40% | 10x | 3 |
| Stocks | 20% | 2x | 5 |

See: [[risk_management.md]] for complete risk documentation.

---

## Market Switching

### Adding a New Market

To add a new market (e.g., stocks after crypto/forex):

1. **Implement Adapter**: Create new execution and data providers
2. **Configure Market**: Add market section to config file
3. **Assign Strategies**: Map compatible strategies
4. **Set Risk Limits**: Configure market-specific limits
5. **Test**: Paper trade before live

```yaml
# Enable a previously disabled market
stocks:
  enabled: true  # Changed from false
  provider: interactive_brokers
  symbols:
    - AAPL
    - GOOGL
    - MSFT
  strategies:
    - swing_trading_v1
  risk_allocation_pct: 20
```

### Disabling a Market

```yaml
# Temporary disable without removing config
forex:
  enabled: false  # Just flip this flag
  # ... rest of config preserved
```

**Behavior on Disable**:
- New signals not generated
- Existing positions managed normally (can close)
- Risk allocation freed for other markets

---

## Dashboard Multi-Market View

### Market Tabs

```
┌─────────────────────────────────────────────────────────┐
│  [ CRYPTO ]  [ FOREX ]  [ STOCKS ]  [ ALL MARKETS ]     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CRYPTO OVERVIEW                                         │
│  ────────────────                                        │
│  Active Strategies: 2                                    │
│  Open Positions: 3                                       │
│  Daily P&L: +$45.20                                      │
│  Exposure: $2,000 (40% of allocation)                   │
│                                                          │
│  RECENT SIGNALS                                          │
│  10:15 - BTCUSDT - BUY - momentum_v1 - Conf: 0.78       │
│  10:10 - ETHUSDT - HOLD - mean_reversion - Conf: 0.45   │
│                                                          │
│  OPEN POSITIONS                                          │
│  ┌──────────┬────────┬──────────┬──────────┬──────────┐ │
│  │ Symbol   │ Side   │ Entry    │ Current  │ P&L      │ │
│  ├──────────┼────────┼──────────┼──────────┼──────────┤ │
│  │ BTCUSDT  │ LONG   │ $42,100  │ $42,350  │ +$25.00  │ │
│  │ ETHUSDT  │ SHORT  │ $2,250   │ $2,220   │ +$15.00  │ │
│  └──────────┴────────┴──────────┴──────────┴──────────┘ │
└─────────────────────────────────────────────────────────┘
```

See: [[ui_and_user_experience.md]] for complete UI documentation.

---

## Best Practices

### Starting Multi-Market Trading

1. **Start Single-Market**: Master one market before adding others
2. **Paper Trade First**: Test cross-market interaction
3. **Conservative Allocation**: Don't over-allocate initially
4. **Monitor Correlations**: Avoid correlated assets across markets
5. **Stagger Additions**: Add markets one at a time

### Monitoring Multi-Market Operations

- [ ] Check global exposure daily
- [ ] Review per-market P&L separately
- [ ] Monitor correlation between positions
- [ ] Verify each market's connection status
- [ ] Review signal conflicts and resolutions

---

## Related Documentation

- [[architecture_overview.md]] — System architecture
- [[risk_management.md]] — Cross-market risk controls
- [[trading_concepts.md]] — Market fundamentals
- [[ui_and_user_experience.md]] — Dashboard monitoring

---

> [!TIP]
> Multi-market trading provides diversification benefits but requires careful monitoring. Use the "ALL MARKETS" dashboard view for holistic oversight.
