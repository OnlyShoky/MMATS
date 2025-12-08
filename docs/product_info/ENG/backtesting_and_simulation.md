# Backtesting and Simulation

This document explains the backtesting, walk-forward analysis, Monte Carlo simulations, and paper trading capabilities in **MMATS**.

---

## Purpose of Backtesting

### Why Backtest?

Backtesting validates trading strategies against historical data before risking real capital:

| Benefit | Description |
|---------|-------------|
| **Validation** | Test strategy logic without financial risk |
| **Optimization** | Find optimal parameters |
| **Risk Assessment** | Understand potential drawdowns |
| **Confidence Building** | Gain trust in strategy behavior |
| **Comparison** | Evaluate multiple strategies objectively |

> [!IMPORTANT]
> Past performance does NOT guarantee future results. Backtests are necessary but not sufficient for strategy validation.

---

## Backtesting Architecture

### System Flow

```
┌─────────────────────────────────────────────────────────┐
│                  BACKTESTING ENGINE                      │
│                                                          │
│  1. CONFIGURATION                                        │
│     └─> Strategy, date range, initial capital            │
│                                                          │
│  2. DATA LOADING                                         │
│     └─> Historical OHLCV from database/files             │
│                                                          │
│  3. SIMULATION LOOP                                      │
│     For each bar in date range:                          │
│       • Calculate indicators                             │
│       • Generate strategy signal                         │
│       • Validate through risk engine                     │
│       • Simulate order execution                         │
│       • Update portfolio state                           │
│                                                          │
│  4. RESULTS CALCULATION                                  │
│     └─> Performance metrics, trade journal               │
│                                                          │
│  5. REPORTING                                            │
│     └─> Charts, tables, export files                     │
└─────────────────────────────────────────────────────────┘
```

### Environment Parity

> [!TIP]
> The same strategy code runs in backtest, paper, and live modes. Only the data source and execution adapter change.

| Component | Backtest | Paper | Live |
|-----------|----------|-------|------|
| Strategy Code | ✓ Identical | ✓ Identical | ✓ Identical |
| Risk Rules | ✓ Identical | ✓ Identical | ✓ Identical |
| Data Source | Historical | Live | Live |
| Execution | Simulated | Simulated | Real |

See: [[architecture_overview.md#Operating-Modes]] for mode details.

---

## Backtesting Configuration

### Basic Configuration

```yaml
backtest:
  strategy: momentum_v1
  market: crypto
  symbol: BTCUSDT
  timeframe: 1H
  
  date_range:
    start: 2023-01-01
    end: 2024-01-01
    
  capital:
    initial: 10000
    currency: USD
    
  execution:
    slippage_pct: 0.1
    commission_maker_pct: 0.1
    commission_taker_pct: 0.1
```

### Advanced Options

```yaml
backtest:
  # ... basic config ...
  
  execution:
    slippage_model: PERCENTAGE  # or FIXED, ATR_BASED
    slippage_pct: 0.1
    
    fill_model: REALISTIC  # or INSTANT
    partial_fills: true
    max_fill_pct_per_bar: 50
    
  risk_config:
    use_live_limits: true  # Apply same limits as live
    max_position_pct: 2
    max_drawdown_pct: 15
    
  walk_forward:
    enabled: true
    in_sample_days: 180
    out_sample_days: 30
    step_days: 30
```

---

## Execution Simulation

### Slippage Modeling

Slippage accounts for price movement between signal and fill:

| Model | Description | Use Case |
|-------|-------------|----------|
| **Percentage** | Fixed % of price | Simple, general purpose |
| **Fixed** | Fixed dollar amount | Low volatility assets |
| **ATR-Based** | Based on volatility | Adapts to market conditions |

```
Example (Percentage Model):
  Signal Price: $42,000
  Slippage: 0.1%
  
  BUY Fill: $42,042 (worse for buyer)
  SELL Fill: $41,958 (worse for seller)
```

### Commission Modeling

Account for trading fees:

| Fee Type | Typical Crypto | Typical Forex | Impact |
|----------|----------------|---------------|--------|
| Maker | 0.1% | Spread | Limit orders |
| Taker | 0.1% | Spread | Market orders |
| Spread | N/A | 1-3 pips | Built into price |

### Fill Simulation

```
ORDER TYPE      FILL LOGIC
───────────────────────────────────
MARKET          Fill at current bar close + slippage

LIMIT BUY       Fill if low ≤ limit price
                Fill price = min(low, limit)

LIMIT SELL      Fill if high ≥ limit price
                Fill price = max(high, limit)

STOP LOSS       Trigger if price crosses stop level
                Fill at stop price + slippage (gap possible)
```

---

## Performance Metrics

### Core Metrics

| Metric | Formula | Good Value |
|--------|---------|------------|
| **Total Return** | (Final - Initial) / Initial | Positive |
| **Annualized Return** | (1 + Total)^(365/days) - 1 | > Risk-free rate |
| **Sharpe Ratio** | (Return - RiskFree) / StdDev | > 1.0 |
| **Sortino Ratio** | (Return - RiskFree) / Downside StdDev | > 1.5 |
| **Max Drawdown** | Largest peak-to-trough decline | < 20% |
| **Win Rate** | Winning trades / Total trades | > 50%* |
| **Profit Factor** | Gross Profit / Gross Loss | > 1.5 |

*Win rate depends on risk-reward ratio. Lower win rates are fine with high R:R.

### Trade Statistics

| Statistic | Description |
|-----------|-------------|
| Total Trades | Number of round-trip trades |
| Average Trade | Average P&L per trade |
| Average Winner | Average profit on winning trades |
| Average Loser | Average loss on losing trades |
| Largest Winner | Best single trade |
| Largest Loser | Worst single trade |
| Average Duration | Mean time positions held |
| Max Consecutive Wins | Longest winning streak |
| Max Consecutive Losses | Longest losing streak |

### Equity Curve

```
┌─────────────────────────────────────────────────────────┐
│     EQUITY CURVE (BTCUSDT Momentum v1, 2023)            │
│                                                          │
│  $12k ┤                                        ╭───────  │
│  $11k ┤                              ╭────────╯          │
│  $10k ┼────────╮     ╭───────────────╯                   │
│   $9k ┤        ╰─────╯                                   │
│   $8k ┤   ← Max Drawdown (12%)                          │
│       └──────────────────────────────────────────────── │
│         Jan    Mar    May    Jul    Sep    Nov          │
└─────────────────────────────────────────────────────────┘
```

---

## Walk-Forward Analysis

### What is Walk-Forward?

Walk-forward testing prevents overfitting by:

1. **Optimizing** on in-sample data
2. **Testing** on out-of-sample data
3. **Rolling** forward and repeating

```
┌─────────────────────────────────────────────────────────┐
│               WALK-FORWARD ANALYSIS                      │
│                                                          │
│  Step 1:                                                 │
│  ├── IN-SAMPLE (Optimize) ──┤── OUT-OF-SAMPLE (Test) ──│
│  │      6 months            │       1 month            │
│                                                          │
│  Step 2:                                                 │
│       ├── IN-SAMPLE ──────────┤── OUT-OF-SAMPLE ──────│
│       │      6 months         │       1 month          │
│                                                          │
│  Step 3:                                                 │
│            ├── IN-SAMPLE ───────┤── OUT-OF-SAMPLE ────│
│            │      6 months       │       1 month        │
│                                                          │
│  → Combine all out-of-sample results for true performance│
└─────────────────────────────────────────────────────────┘
```

### Configuration

```yaml
walk_forward:
  enabled: true
  in_sample_days: 180      # Optimization period
  out_sample_days: 30      # Testing period
  step_days: 30            # Roll forward by this amount
  optimization_metric: sharpe_ratio
  
  parameters_to_optimize:
    - name: sma_fast
      min: 5
      max: 20
      step: 5
    - name: sma_slow
      min: 20
      max: 50
      step: 10
```

### Interpreting Results

| Scenario | Implication |
|----------|-------------|
| In-sample >> Out-of-sample | Likely overfitting |
| In-sample ≈ Out-of-sample | Good generalization |
| Consistent across windows | Robust strategy |
| High variance across windows | May need refinement |

---

## Monte Carlo Simulation

### Purpose

Monte Carlo simulation stress-tests strategy robustness by:

1. **Trade Shuffling**: Randomize order of trades
2. **Bootstrap Sampling**: Resample with replacement
3. **Parameter Variation**: Small random parameter changes

### Methodology

```
┌─────────────────────────────────────────────────────────┐
│              MONTE CARLO SIMULATION                      │
│                                                          │
│  Original Trade Sequence:                                │
│  [+$50, -$20, +$30, -$10, +$80, -$40, ...]              │
│                                                          │
│  1000 Simulations (shuffled order):                      │
│  ├── Sim 1: [-$20, +$80, -$10, +$30, ...]               │
│  ├── Sim 2: [+$30, -$40, +$50, -$20, ...]               │
│  ├── ...                                                 │
│  └── Sim 1000: [-$10, +$50, -$20, +$80, ...]            │
│                                                          │
│  Statistics:                                             │
│  ├── Median Final Equity: $11,250                       │
│  ├── 5th Percentile: $9,100                             │
│  ├── 95th Percentile: $13,400                           │
│  └── Max Drawdown Range: 8% - 22%                       │
└─────────────────────────────────────────────────────────┘
```

### Confidence Intervals

| Percentile | Use Case |
|------------|----------|
| 5th | Worst-case realistic scenario |
| 25th | Conservative estimate |
| 50th (Median) | Expected outcome |
| 75th | Optimistic estimate |
| 95th | Best-case realistic scenario |

### Configuration

```yaml
monte_carlo:
  enabled: true
  simulations: 1000
  method: BOOTSTRAP  # or SHUFFLE, PARAMETER_VARIATION
  confidence_intervals: [5, 25, 50, 75, 95]
  
  parameter_variation:
    enabled: true
    variance_pct: 5  # ±5% variation on parameters
```

---

## Paper Trading

### What is Paper Trading?

Paper trading uses **live market data** with **simulated execution**:

| Aspect | Paper Trading | Backtesting |
|--------|---------------|-------------|
| Data | Live, real-time | Historical |
| Timing | Real-time | Instant |
| Execution | Simulated | Simulated |
| Purpose | Real-time validation | Historical validation |
| Duration | Days/weeks | Minutes/hours |

### Benefits

1. **Market Reality**: Experience real market conditions
2. **Latency Testing**: Measure actual signal-to-execution time
3. **Psychology**: Practice without financial risk
4. **Comparison**: Run alongside live for verification

### Configuration

```yaml
paper_trading:
  enabled: true
  
  capital:
    initial: 10000
    currency: USD
    
  execution:
    slippage_pct: 0.1      # Assume slippage
    commission_pct: 0.1
    
  persistence:
    save_state: true        # Remember positions on restart
    database: paper_portfolio
    
  comparison:
    track_vs_live: true     # Compare paper vs live performance
```

### Paper vs Live Comparison

```
┌─────────────────────────────────────────────────────────┐
│            PAPER vs LIVE COMPARISON                      │
│                                                          │
│                      Paper        Live       Difference  │
│  ───────────────────────────────────────────────────────│
│  Total Trades        42           38          +4        │
│  Win Rate           58%          52%          +6%       │
│  Avg Slippage      0.10%        0.15%       -0.05%      │
│  Net P&L          +$520        +$380        +$140       │
│                                                          │
│  Analysis: Paper outperforms due to lower slippage.     │
│            Consider adjusting slippage model.           │
└─────────────────────────────────────────────────────────┘
```

---

## Avoiding Common Pitfalls

### Look-Ahead Bias

> [!CAUTION]
> Look-ahead bias occurs when future information "leaks" into past decisions.

| Example | Problem |
|---------|---------|
| Using close price for signal, then close for entry | Entry at close is unrealistic |
| Indicator using future bars | Impossible in live trading |
| Survivorship bias in stock universe | Ignores delisted stocks |

**MMATS Prevention**: Data is strictly time-ordered; indicators only access past bars.

### Overfitting

```
┌─────────────────────────────────────────────────────────┐
│                 OVERFITTING WARNING                      │
│                                                          │
│  Symptoms:                                               │
│  • Extremely high backtest returns                       │
│  • Many optimized parameters (>5)                        │
│  • In-sample >> Out-of-sample performance               │
│  • Poor performance on different time periods            │
│                                                          │
│  Prevention:                                             │
│  • Use walk-forward analysis                             │
│  • Limit number of parameters                            │
│  • Test on multiple markets/timeframes                   │
│  • Use out-of-sample validation                          │
└─────────────────────────────────────────────────────────┘
```

### Unrealistic Assumptions

| Assumption | Reality |
|------------|---------|
| Zero slippage | Always some slippage in live |
| Instant fills | Fills take time, may not fill |
| Unlimited liquidity | Large orders move markets |
| No fees | Fees erode returns |

---

## Reporting and Export

### Backtest Report

```
┌─────────────────────────────────────────────────────────┐
│         BACKTEST REPORT: Momentum v1 on BTCUSDT         │
│                   2023-01-01 to 2024-01-01              │
├─────────────────────────────────────────────────────────┤
│  SUMMARY                                                 │
│  ────────────────────────────────────────────────       │
│  Initial Capital:     $10,000                           │
│  Final Capital:       $12,450                           │
│  Total Return:        24.5%                             │
│  Annualized Return:   24.5%                             │
│  Max Drawdown:        12.3%                             │
│  Sharpe Ratio:        1.45                              │
│  Sortino Ratio:       1.82                              │
├─────────────────────────────────────────────────────────┤
│  TRADE STATISTICS                                        │
│  ────────────────────────────────────────────────       │
│  Total Trades:        87                                 │
│  Win Rate:            56.3%                             │
│  Profit Factor:       1.78                              │
│  Average Trade:       $28.16                            │
│  Average Winner:      $95.40                            │
│  Average Loser:       -$54.20                           │
├─────────────────────────────────────────────────────────┤
│  MONTE CARLO (1000 simulations)                         │
│  ────────────────────────────────────────────────       │
│  5th Percentile:      $9,800 (-2%)                      │
│  Median:              $12,100 (+21%)                    │
│  95th Percentile:     $15,200 (+52%)                    │
│  Max DD Range:        8% - 18%                          │
└─────────────────────────────────────────────────────────┘
```

### Export Options

| Format | Use Case |
|--------|----------|
| JSON | Integration with other tools |
| CSV | Spreadsheet analysis |
| PDF | Formal reporting |
| HTML | Interactive viewing |

---

## Best Practices

### Before Live Trading

- [ ] Backtest on 2+ years of data
- [ ] Walk-forward test shows consistency
- [ ] Monte Carlo 5th percentile is acceptable
- [ ] Paper trade for 2+ weeks
- [ ] Results align with expectations

### Ongoing Validation

- [ ] Re-backtest quarterly with new data
- [ ] Compare live vs paper performance
- [ ] Monitor for regime changes
- [ ] Update risk parameters based on results

---

## Related Documentation

- [[trading_concepts.md]] — Trading fundamentals
- [[architecture_overview.md]] — System architecture
- [[risk_management.md]] — Risk controls for backtesting
- [[ai_llm_integration.md]] — Including news in backtests

---

> [!TIP]
> Good backtesting is an iterative process. Start simple, validate assumptions, and gradually increase complexity.
