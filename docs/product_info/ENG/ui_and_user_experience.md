# UI and User Experience

This document explains the dashboard, monitoring capabilities, and user interface features of **MMATS**.

---

## Dashboard Overview

### Core Screens

| Screen | Purpose |
|--------|---------|
| **Overview** | System status, global P&L, quick stats |
| **Market View** | Per-market charts and positions |
| **Strategy Performance** | Strategy comparison and metrics |
| **Risk Monitor** | Risk limit utilization |
| **Order Management** | Pending orders, manual intervention |
| **Logs & Audit** | Real-time logs, trade journal |

---

## Overview Dashboard

```
┌─────────────────────────────────────────────────────────┐
│                 MMATS DASHBOARD                          │
│                                                          │
│  SYSTEM STATUS: ● OPERATIONAL (Operator Mode)           │
│                                                          │
│  ┌─────────────────┬─────────────────┬────────────────┐ │
│  │  Daily P&L      │  Total P&L      │  Win Rate      │ │
│  │    +$125.40     │   +$1,245       │    58%         │ │
│  └─────────────────┴─────────────────┴────────────────┘ │
│                                                          │
│  ACTIVE POSITIONS: 5                                     │
│  PENDING SIGNALS: 2                                      │
│  RISK UTILIZATION: 42% ████████░░░░░░░░░░░░             │
│                                                          │
│  [EMERGENCY STOP]  [Switch to Advisory]  [Settings]     │
└─────────────────────────────────────────────────────────┘
```

### Key Indicators

| Indicator | Description |
|-----------|-------------|
| System Status | Operational, Advisory, Stopped |
| Daily P&L | Today's profit/loss |
| Total P&L | All-time performance |
| Active Positions | Current open trades |
| Risk Utilization | % of risk limits used |

---

## Market View

### Per-Market Tabs

```
┌─────────────────────────────────────────────────────────┐
│  [ CRYPTO ]  [ FOREX ]  [ STOCKS ]  [ ALL ]             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  BTCUSDT - 1H                    Price: $42,350         │
│  ┌───────────────────────────────────────────────────┐ │
│  │                                        ╭──────────│ │
│  │                              ╭─────────╯          │ │
│  │  ───────────╮    ╭───────────╯                    │ │
│  │             ╰────╯          ▲ Entry               │ │
│  │                             █ Position            │ │
│  └───────────────────────────────────────────────────┘ │
│                                                          │
│  INDICATORS: SMA(20): 41,800 | RSI(14): 62             │
│                                                          │
│  OPEN POSITIONS                                          │
│  ┌──────────┬────────┬──────────┬──────────┐           │
│  │ Symbol   │ Side   │ Entry    │ P&L      │           │
│  ├──────────┼────────┼──────────┼──────────┤           │
│  │ BTCUSDT  │ LONG   │ $42,100  │ +$25.00  │           │
│  └──────────┴────────┴──────────┴──────────┘           │
└─────────────────────────────────────────────────────────┘
```

### Chart Features

- Candlestick charts with indicator overlays
- Position markers (entry, stop-loss, take-profit)
- Recent signal annotations
- Zoom and pan controls

See: [[trading_concepts.md#OHLCV-Data]] for data format.

---

## Strategy Performance

```
┌─────────────────────────────────────────────────────────┐
│               STRATEGY PERFORMANCE                       │
│                                                          │
│  ┌────────────────┬────────┬────────┬────────┬───────┐ │
│  │ Strategy       │ P&L    │ Trades │ Win %  │ Status│ │
│  ├────────────────┼────────┼────────┼────────┼───────┤ │
│  │ momentum_v1    │ +$520  │ 45     │ 58%    │ ● ON  │ │
│  │ mean_revert_v2 │ +$320  │ 32     │ 62%    │ ● ON  │ │
│  │ breakout_v1    │ -$45   │ 12     │ 42%    │ ○ OFF │ │
│  └────────────────┴────────┴────────┴────────┴───────┘ │
│                                                          │
│  [Enable/Disable]  [View Details]  [Backtest]           │
└─────────────────────────────────────────────────────────┘
```

### Strategy Controls

- Enable/disable individual strategies
- View detailed performance metrics
- Launch backtests from dashboard
- Compare multiple strategies

---

## Risk Monitor

```
┌─────────────────────────────────────────────────────────┐
│                   RISK MONITOR                           │
│                                                          │
│  GLOBAL EXPOSURE    ████████░░░░░░░░░░░░  42% / 50%    │
│  DAILY P&L          -$35 / -$150 limit   ⚠️ 23%        │
│  DRAWDOWN           6.2% / 15% limit     ✅ OK         │
│  OPEN POSITIONS     7 / 10               ✅ OK         │
│                                                          │
│  MARKET BREAKDOWN                                        │
│  ├─ Crypto          $2,100 (42%)         ✅ OK         │
│  ├─ Forex           $1,800 (36%)         ✅ OK         │
│  └─ Stocks          $1,100 (22%)         ✅ OK         │
│                                                          │
│  ALERT HISTORY                                           │
│  [WARN] 09:45 - Approaching daily loss limit (75%)      │
└─────────────────────────────────────────────────────────┘
```

See: [[risk_management.md]] for complete risk documentation.

---

## Order Management

### Pending Orders

- View all pending orders
- Cancel individual or bulk orders
- Modify order parameters

### Manual Order Entry

```
┌─────────────────────────────────────────────────────────┐
│                MANUAL ORDER ENTRY                        │
│                                                          │
│  Symbol:    [BTCUSDT     ▼]                             │
│  Side:      [BUY ●] [SELL ○]                            │
│  Type:      [MARKET ▼]                                  │
│  Quantity:  [0.01        ]                              │
│  Stop-Loss: [41,500      ]                              │
│  Take-Profit: [44,000    ]                              │
│                                                          │
│  [Preview Order]  [Submit Order]                        │
└─────────────────────────────────────────────────────────┘
```

> [!WARNING]
> Manual orders bypass strategy logic but still go through risk validation.

---

## Logs and Audit Trail

### Real-Time Log Stream

```
┌─────────────────────────────────────────────────────────┐
│                    SYSTEM LOGS                           │
│                                                          │
│  Filter: [All ▼] [INFO ▼] [Crypto ▼]  [🔍 Search]      │
│                                                          │
│  10:45:22 INFO  execution  Order filled: BTC BUY 0.01  │
│  10:45:21 INFO  risk       Pre-trade validation passed  │
│  10:45:20 INFO  strategy   Signal: momentum_v1 → BUY    │
│  10:45:15 DEBUG data       Candle received: BTCUSDT     │
│  10:44:00 WARN  risk       Approaching daily loss (75%) │
│                                                          │
│  [Export Logs]  [Clear Filters]  [Pause Stream]        │
└─────────────────────────────────────────────────────────┘
```

### Trade Journal

Complete record of all executed trades with:
- Entry/exit timestamps
- Strategy that generated signal
- Risk metrics at time of trade
- Outcome and P&L

---

## Configuration Panel

### Settings Categories

| Category | Settings |
|----------|----------|
| **Markets** | Enable/disable, symbols, timeframes |
| **Strategies** | Assignments, parameters |
| **Risk** | Limits, thresholds |
| **Notifications** | Channels, triggers |
| **Credentials** | API key management |

### Validation

- Changes validated before save
- Invalid configurations blocked
- Version history with rollback

---

## Notifications

### Channels

| Channel | Use Case |
|---------|----------|
| Dashboard | Real-time alerts |
| Email | Daily summaries, critical errors |
| Telegram | Real-time notifications |
| Discord | Team notifications |

### Alert Types

| Type | Example |
|------|---------|
| INFO | Position opened |
| WARNING | Approaching risk limit |
| ERROR | Order rejected |
| CRITICAL | Emergency stop triggered |

---

## Technical Specifications

| Aspect | Specification |
|--------|---------------|
| Update Rate | 1 second (WebSocket) |
| Resolution | 1920x1080 minimum |
| Access | Localhost only (Phase 1) |
| Export | Charts, tables, logs |

---

## Related Documentation

- [[architecture_overview.md]] — System architecture
- [[risk_management.md]] — Risk monitoring details
- [[multi_market_operations.md]] — Market views
