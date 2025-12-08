# Risk Management

This document explains the comprehensive risk management system in **MMATS**, designed to protect capital and enforce disciplined trading.

> [!CAUTION]
> Trading involves significant risk of financial loss. Risk management does not eliminate risk—it manages exposure within acceptable limits.

---

## Risk Management Philosophy

### Core Principles

1. **Capital Preservation First**: Protect principal before seeking profits
2. **Pre-Trade Validation**: Block risky trades BEFORE execution
3. **Multi-Level Controls**: Global, market, strategy, and position limits
4. **Fail-Safe Defaults**: Unknown states default to safest behavior
5. **Circuit Breakers**: Automatic shutdown on extreme conditions

---

## Risk Hierarchy

MMATS implements a hierarchical risk structure:

```
┌─────────────────────────────────────────────────────────┐
│                    GLOBAL LIMITS                         │
│              (Entire System Level)                       │
│  • Total portfolio exposure                              │
│  • Maximum drawdown from peak                            │
│  • Daily loss limit (all markets)                        │
├─────────────────────────────────────────────────────────┤
│                  PER-MARKET LIMITS                       │
│           (Crypto | Forex | Stocks)                      │
│  • Maximum capital allocation per market                 │
│  • Market-specific leverage limits                       │
│  • Market-specific position limits                       │
├─────────────────────────────────────────────────────────┤
│                PER-STRATEGY LIMITS                       │
│        (Within each market allocation)                   │
│  • Capital allocated to each strategy                    │
│  • Strategy-specific risk parameters                     │
│  • Maximum positions per strategy                        │
├─────────────────────────────────────────────────────────┤
│                 PER-SYMBOL LIMITS                        │
│           (Position Concentration)                       │
│  • Maximum size per individual asset                     │
│  • Correlation-aware limits                              │
└─────────────────────────────────────────────────────────┘
```

---

## Risk Limit Types

### Position Size Limits

**MaxPositionSizeRule**: Limits capital per single trade.

| Setting | Description | Example |
|---------|-------------|---------|
| `max_position_pct` | Maximum % of capital per trade | 2% |
| `max_position_usd` | Maximum $ amount per trade | $100 |

```
Example:
Capital: $10,000
Max Position: 2%
Maximum Trade Size: $200
```

### Leverage Limits

**MaxLeverageRule**: Restricts borrowed capital multiplier.

| Market | Recommended Max | Aggressive Max |
|--------|-----------------|----------------|
| Crypto Spot | 1x | 1x |
| Crypto Futures | 3x | 10x |
| Forex | 10x | 30x |
| Stocks | 2x | 4x |

> [!WARNING]
> Higher leverage amplifies both gains and losses. Start conservative.

See: [[trading_concepts.md#Leverage]] for leverage explanation.

### Drawdown Limits

**MaxDrawdownRule**: Stops trading when equity drops too far from peak.

```
┌─────────────────────────────────────────────────────────┐
│                  DRAWDOWN MONITORING                     │
│                                                          │
│  Peak Equity: $12,000                                    │
│  └─> Drawdown Limit: 10%                                 │
│      └─> Trigger at: $10,800                             │
│                                                          │
│  Current Equity: $11,200                                 │
│  └─> Current Drawdown: 6.7%                              │
│      └─> Status: TRADING ACTIVE                          │
│                                                          │
│  If Current Equity drops to $10,800:                     │
│  └─> Action: PAUSE ALL STRATEGIES                        │
└─────────────────────────────────────────────────────────┘
```

| Threshold | Action |
|-----------|--------|
| 80% of limit | Warning notification |
| 90% of limit | Alert + reduce position sizes |
| 100% of limit | Pause all trading |

### Daily Loss Limits

**DailyLossLimitRule**: Maximum loss allowed per trading day.

| Setting | Description | Default |
|---------|-------------|---------|
| `daily_loss_pct` | Max daily loss as % of equity | 3% |
| `daily_loss_usd` | Max daily loss in $ | $50 |

**Behavior**:
- Resets at configured time (default: 00:00 UTC)
- Breached → All strategies paused until next day
- Logged for analysis

### Open Position Limits

**MaxOpenPositionsRule**: Limits concurrent trades.

| Scope | Typical Limit | Purpose |
|-------|---------------|---------|
| Global | 10 | Manage overall exposure |
| Per Market | 5 | Diversify across markets |
| Per Strategy | 3 | Prevent strategy over-trading |

### Exposure Limits

**MaxExposureRule**: Total capital at risk as percentage.

```
Total Capital: $10,000
Maximum Exposure: 50%

Current Positions:
- BTC: $500 at risk
- ETH: $300 at risk
- EUR/USD: $400 at risk

Total Exposure: $1,200 (12%)
└─> Status: WITHIN LIMITS (50% max)
```

---

## Risk Rule Engine

### Architecture

```python
class RiskRule:
    """Base class for all risk rules"""
    
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
                modified_signal: Optional[Signal]
            }
        """
        pass
```

### Built-In Rules

| Rule | Description |
|------|-------------|
| `MaxPositionSizeRule` | Limit single position to X% of capital |
| `MaxDrawdownRule` | Stop trading if DD exceeds threshold |
| `DailyLossLimitRule` | Stop if daily loss > $X or Y% |
| `MaxOpenPositionsRule` | Limit concurrent trades |
| `MaxLeverageRule` | Limit borrowed capital |
| `CorrelationRule` | Prevent over-concentration in correlated assets |
| `MaxExposurePerMarketRule` | Limit % of capital per market |
| `TimeOfDayRule` | Restrict trading to certain hours |

### Rule Execution Order

```
1. PRE-VALIDATION (Fast Checks)
   └─> Balance check, basic limits

2. COMPLEX VALIDATION
   └─> Correlation analysis, exposure calculation

3. POSITION SIZE ADJUSTMENT
   └─> Reduce size if rules recommend

4. FINAL DECISION
   └─> APPROVE, REJECT, or MODIFY
```

---

## Position Sizing

### Fixed Percentage Method

Allocate fixed % of capital per trade:

```
Capital: $10,000
Position Size: 2%
Trade Size: $200
```

### Volatility-Based (ATR) Method

Adjust size based on market volatility:

```
Capital: $10,000
Base Risk: 1%
ATR (14): $50

Position Size = (Capital × Risk%) / ATR
Position Size = ($10,000 × 0.01) / $50 = 2 units
```

### Kelly Criterion

Mathematically optimal sizing based on win rate:

```
Kelly % = W - [(1 - W) / R]

Where:
W = Win probability
R = Win/Loss ratio

Example:
Win Rate: 55% (W = 0.55)
Risk-Reward: 2:1 (R = 2)
Kelly % = 0.55 - (0.45 / 2) = 0.325 (32.5%)

Practical: Use ½ or ¼ Kelly = 8-16%
```

> [!TIP]
> Full Kelly is aggressive. Most traders use fractional Kelly (½ or ¼) for safety.

---

## Emergency Shutdown System

### Trigger Conditions

| Trigger | Severity | Default Action |
|---------|----------|----------------|
| Manual emergency stop | CRITICAL | HARD shutdown |
| Critical error detection | CRITICAL | FREEZE |
| Max drawdown breach | HIGH | SOFT shutdown |
| API connection loss >60s | HIGH | SOFT shutdown |
| Anomaly detection | MEDIUM | Alert + review |
| Daily loss limit breach | MEDIUM | SOFT shutdown |

### Shutdown Modes

```
┌─────────────────────────────────────────────────────────┐
│                    SOFT SHUTDOWN                         │
│  • Stop new order generation                             │
│  • Manage existing positions normally                    │
│  • Honor stop-loss and take-profit orders               │
│  • Allow manual intervention                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    HARD SHUTDOWN                         │
│  • Stop all new orders immediately                       │
│  • Close ALL positions at market price                   │
│  • Cancel ALL pending orders                             │
│  • Priority: Close riskiest positions first              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                       FREEZE                             │
│  • Stop EVERYTHING                                       │
│  • No automatic position management                      │
│  • Manual intervention REQUIRED                          │
│  • Full system audit before restart                      │
└─────────────────────────────────────────────────────────┘
```

### Response Time Requirements

| Action | Target Time |
|--------|-------------|
| Emergency stop button response | <1 second |
| Position closing initiation | <5 seconds |
| Notification dispatch | <60 seconds |

---

## Risk Configuration

### Example Configuration

```yaml
risk_management:
  global:
    max_drawdown_pct: 15
    daily_loss_limit_pct: 3
    max_open_positions: 10
    max_leverage: 5
    max_exposure_pct: 50
    
  markets:
    crypto:
      max_allocation_pct: 40
      max_leverage: 3
      max_positions: 5
      
    forex:
      max_allocation_pct: 40
      max_leverage: 10
      max_positions: 3
      
    stocks:
      max_allocation_pct: 20
      max_leverage: 2
      max_positions: 5
      
  strategies:
    momentum_v1:
      max_position_pct: 2
      max_positions: 3
      drawdown_limit_pct: 10
      
    mean_reversion_v2:
      max_position_pct: 1.5
      max_positions: 4
      drawdown_limit_pct: 8
```

### Environment-Specific Limits

| Environment | Strictness | Purpose |
|-------------|------------|---------|
| BACKTEST | Loose | Explore strategy behavior |
| PAPER | Moderate | Realistic simulation |
| LIVE | Strict | Capital protection |

---

## Monitoring and Alerts

### Risk Dashboard

The risk monitoring panel displays:

```
┌─────────────────────────────────────────────────────────┐
│                  RISK MONITOR                            │
│                                                          │
│  GLOBAL EXPOSURE     ████████░░░░░░░░░░░░  42% / 50%    │
│  DAILY P&L           -$35 / -$150 limit   ⚠️ 23%        │
│  DRAWDOWN            6.2% / 15% limit     ✅ OK         │
│  OPEN POSITIONS      7 / 10               ✅ OK         │
│                                                          │
│  MARKET BREAKDOWN                                        │
│  ├─ Crypto           $2,100 (42%)         ✅ OK         │
│  ├─ Forex            $1,800 (36%)         ✅ OK         │
│  └─ Stocks           $1,100 (22%)         ✅ OK         │
│                                                          │
│  RECENT ALERTS                                           │
│  [WARN] 09:45 - Approaching daily loss limit (75%)      │
│  [INFO] 09:30 - Position closed: ETH/USDT               │
└─────────────────────────────────────────────────────────┘
```

See: [[ui_and_user_experience.md]] for complete UI documentation.

### Alert Channels

| Channel | Use Case |
|---------|----------|
| Dashboard | Real-time monitoring |
| Email | Critical errors, daily summaries |
| Telegram/Discord | Real-time notifications |
| SMS | Emergency situations only |

---

## Best Practices

### For Conservative Traders

- [ ] Start with 1% max position size
- [ ] Use 5% max drawdown limit
- [ ] Trade only 2-3 markets initially
- [ ] Use paper trading for 2+ weeks first

### For Aggressive Traders

> [!WARNING]
> Higher risk tolerances require more experience and active monitoring.

- [ ] Never exceed 5% per position
- [ ] Monitor correlations closely
- [ ] Have emergency plan documented
- [ ] Review risk metrics daily

### General Guidelines

1. **Never override risk limits** without documented reason
2. **Review losing streaks** — adjust before drawdown limit hit
3. **Backtest risk settings** — see how limits would have performed historically
4. **Scale gradually** — increase limits only after consistent success

---

## Related Documentation

- [[trading_concepts.md]] — Fundamental concepts (leverage, drawdown)
- [[architecture_overview.md]] — Risk engine architecture
- [[backtesting_and_simulation.md]] — Testing risk settings
- [[security_and_compliance.md]] — Security aspects of risk management

---

> [!IMPORTANT]
> Risk management is not optional. Every trade should pass through the risk validation pipeline. Never disable risk checks in live trading.
