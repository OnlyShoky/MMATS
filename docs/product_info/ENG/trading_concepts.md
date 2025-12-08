# Trading Concepts

This document provides a comprehensive overview of financial and trading concepts essential for understanding and working with the **Multi-Market Automated Trading System (MMATS)**.

> [!TIP]
> This document is designed for developers and users who may not have an extensive background in trading. All concepts are explained with MMATS-specific context.

---

## Financial Markets Overview

### What is a Financial Market?

A financial market is a marketplace where buyers and sellers trade assets such as stocks, currencies, commodities, and derivatives. MMATS supports three main types of markets:

| Market Type | Description | Trading Hours | Examples |
|-------------|-------------|---------------|----------|
| **Crypto** | Decentralized digital currencies | 24/7 | Bitcoin (BTC), Ethereum (ETH) |
| **Forex** | Foreign exchange currencies | 24/5 (Mon-Fri) | EUR/USD, GBP/JPY |
| **Stocks** | Equity shares in companies | Exchange hours | AAPL, GOOGL, TSLA |

---

## Key Market Participants

### Brokers vs Exchanges

```
┌─────────────────────────────────────────────────────┐
│                    USER/TRADER                       │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                     BROKER                           │
│  (Binance, OANDA, Interactive Brokers)              │
│  - Provides API access                               │
│  - Manages accounts                                  │
│  - Executes orders                                   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                    EXCHANGE                          │
│  (NYSE, NASDAQ, Forex Market)                        │
│  - Matches buy/sell orders                           │
│  - Determines market prices                          │
└─────────────────────────────────────────────────────┘
```

- **Broker**: An intermediary that provides access to markets. MMATS connects to brokers via APIs.
- **Exchange**: The actual marketplace where orders are matched.

In crypto, the distinction is blurred—exchanges like Binance act as both broker and exchange.

---

## Order Types

Understanding order types is critical for automated trading:

### Market Order
- **Definition**: Execute immediately at the best available price
- **Pros**: Guaranteed execution
- **Cons**: Price may slip, especially in volatile markets
- **MMATS Usage**: Default for urgent signals

### Limit Order
- **Definition**: Execute only at specified price or better
- **Pros**: Price control
- **Cons**: May not fill if price doesn't reach target
- **MMATS Usage**: Precise entry/exit points

### Stop-Loss Order
- **Definition**: Triggers a market order when price reaches a specified level
- **Purpose**: Limit losses on existing positions
- **MMATS Usage**: Risk management, capital protection

### Take-Profit Order
- **Definition**: Automatically close position when target profit is reached
- **Purpose**: Lock in gains
- **MMATS Usage**: Exit strategy automation

---

## Position Concepts

### Long Position
Opening a **long** position means buying an asset expecting its price to **increase**.

```
BUY at $100 → Price rises to $120 → SELL → Profit: $20
```

### Short Position
Opening a **short** position means selling an asset (borrowed) expecting its price to **decrease**.

```
SELL (borrow) at $100 → Price falls to $80 → BUY back → Profit: $20
```

> [!NOTE]
> Not all markets support short selling. Crypto spot markets typically don't, but futures do.

---

## Risk and Reward Concepts

### Leverage

Leverage allows trading with borrowed capital, amplifying both gains and losses.

| Leverage | Margin Required | Position Size | $100 → $110 | $100 → $90 |
|----------|-----------------|---------------|-------------|------------|
| 1x | $100 | $100 | +$10 (10%) | -$10 (10%) |
| 5x | $100 | $500 | +$50 (50%) | -$50 (50%) |
| 10x | $100 | $1000 | +$100 (100%) | -$100 (100%) |

> [!WARNING]
> High leverage can lead to rapid account depletion. MMATS enforces **MaxLeverageRule** to prevent excessive risk.

See: [[risk_management.md]] for detailed risk controls.

### Drawdown

**Drawdown** measures the decline from a peak in account equity.

```
Peak Equity: $10,000
Current Equity: $8,500
Drawdown: ($10,000 - $8,500) / $10,000 = 15%
```

**Max Drawdown (MDD)** is the largest peak-to-trough decline during a period.

### Risk-Reward Ratio

The relationship between potential profit and potential loss:

```
Entry: $100
Stop-Loss: $95 (Risk: $5)
Take-Profit: $115 (Reward: $15)

Risk-Reward Ratio: 15:5 = 3:1
```

MMATS strategies should ideally target ratios of 2:1 or higher.

---

## Market Data Concepts

### OHLCV Data

Standard candlestick format used in MMATS:

| Field | Description |
|-------|-------------|
| **O**pen | First price at the interval start |
| **H**igh | Highest price during the interval |
| **L**ow | Lowest price during the interval |
| **C**lose | Last price at the interval end |
| **V**olume | Total traded quantity |

### Timeframes

Time intervals for candlestick data:

| Timeframe | Code | Use Case |
|-----------|------|----------|
| 1 Minute | 1m | Scalping, high-frequency |
| 5 Minutes | 5m | Short-term trading |
| 1 Hour | 1H | Swing trading |
| 4 Hours | 4H | Position trading |
| 1 Day | 1D | Long-term analysis |

### Tick Data

A **tick** represents a single price update:
- Timestamp
- Price
- Volume (optional)

Real-time tick data is essential for live trading in MMATS.

---

## Technical Indicators

MMATS supports indicator calculation through TA-Lib and pandas-ta:

### Moving Averages

#### Simple Moving Average (SMA)
Average of closing prices over N periods.

```
SMA(5) = (P1 + P2 + P3 + P4 + P5) / 5
```

#### Exponential Moving Average (EMA)
Weighted average giving more importance to recent prices.

### Relative Strength Index (RSI)
Momentum oscillator measuring overbought/oversold conditions.

- **RSI > 70**: Overbought (potential sell signal)
- **RSI < 30**: Oversold (potential buy signal)

### MACD (Moving Average Convergence Divergence)
Trend-following momentum indicator.

---

## Trading Strategy Concepts

### Signal Generation

MMATS strategies generate **signals**—tradeable recommendations:

| Signal Action | Meaning |
|---------------|---------|
| **BUY** | Enter or add to long position |
| **SELL** | Enter or add to short position |
| **HOLD** | No action recommended |
| **CLOSE** | Exit current position |

See: [[architecture_overview.md#Strategy-Interface]] for technical details.

### Confidence Score

Each signal includes a **confidence** value (0.0 to 1.0):
- Used for position sizing
- Filters low-quality signals
- Enables weighted signal aggregation

---

## Execution Concepts

### Slippage

The difference between expected and actual execution price.

```
Expected Price: $100.00
Actual Fill: $100.15
Slippage: $0.15 (0.15%)
```

**Causes**: Market volatility, order size, liquidity

### Commission/Fees

Trading costs that affect profitability:

| Fee Type | Description |
|----------|-------------|
| **Maker Fee** | Adding liquidity (limit orders) |
| **Taker Fee** | Removing liquidity (market orders) |
| **Spread** | Bid-ask difference (forex) |

MMATS backtesting includes realistic fee modeling.

### Latency

Time delay in order execution:

```
Signal Generation → Risk Validation → Order Submission → Broker → Exchange → Fill
        50ms              10ms              200ms         variable    variable
```

See: [[architecture_overview.md#Performance-Requirements]] for latency targets.

---

## Related Documentation

- [[architecture_overview.md]] — System architecture and components
- [[risk_management.md]] — Risk controls and position sizing
- [[backtesting_and_simulation.md]] — Testing strategies on historical data
- [[multi_market_operations.md]] — Trading across multiple markets

---

## Glossary

| Term | Definition |
|------|------------|
| **Ask** | Lowest price a seller will accept |
| **Bid** | Highest price a buyer will pay |
| **Spread** | Difference between bid and ask |
| **Lot** | Standard trading unit (forex: 100,000 units) |
| **Pip** | Minimum price movement (forex: 0.0001) |
| **Satoshi** | Smallest Bitcoin unit (0.00000001 BTC) |
| **Volatility** | Measure of price variability |
| **Liquidity** | Ease of executing trades without price impact |

---

> [!IMPORTANT]
> Trading involves significant risk of loss. This documentation is educational and does not constitute financial advice. See: [[security_and_compliance.md#Risk-Disclosures]]
