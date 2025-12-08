
## 📌 MASTER PROMPT — TRADING MULTI-MARKET AUTOMATED SYSTEM PRS

I want you to act as a **senior software architect and fintech product manager** specialized in **algorithmic trading platforms**.
Your task is to **write a complete, professional PRS (Product Requirements Specification)** for the following product.

This system is intended to be **used personally at first**, with small capital (100–200€), and later may be shared with friends or commercialized.

The PRS must include:

* Functional requirements
* Non-functional requirements
* System architecture
* Modular design
* Security requirements
* Risk management
* Backtesting and simulation
* Broker/exchange integrations
* Data pipelines
* Future AI and LLM extensions
* Multi-market orchestration
* UI/UX considerations
* Legal and compliance considerations (high-level)
* Roadmap and phases

The tone should be **professional, technical, and precise**, suitable for being handed directly to a development team.

---

## 🎯 PRODUCT GOAL

The product is a **fully modular, multi-market automated trading system** that can:

1. Operate in:

   * Cryptocurrencies
   * Forex
   * Stocks (future extension)
2. Run **multiple markets in parallel**
3. Run **multiple mathematical models simultaneously**, each using:

   * The same standardized inputs
   * The same standardized outputs
4. Support two operating modes:

   * **Advisory Mode** → Generates trade signals only (no real execution)
   * **Operator Mode** → Executes real trades via broker/exchange APIs
5. Include:

   * Historical backtesting
   * Real-time paper trading (simulation)
   * Real-time live trading
6. Be designed for:

   * Medium-frequency trading (not HFT initially)
   * Future extension to High-Frequency Trading (HFT)
7. Be:

   * Highly modular
   * Highly scalable
   * Easily extendable with new models and new markets

---

## 🧱 CORE ARCHITECTURE PRINCIPLES

The system must be designed using:

* Clean Architecture
* Hexagonal / Ports & Adapters
* Strong Separation of Concerns
* Model-agnostic strategy engine
* Market-agnostic execution engine

Each trading model must:

* Respect a **standardized template (interface)**
* Receive standardized inputs:

  * Market data (price, volume, timestamp, indicators)
  * Account state (balance, positions)
  * Environment (backtest, paper, live)
* Return standardized outputs:

  * Action: BUY / SELL / HOLD
  * Symbol
  * Position size
  * Stop-loss
  * Take-profit

The internal mathematical logic of each model can vary freely.

---

## 🔁 MULTI-MARKET REQUIREMENTS

The system must allow:

* Running:

  * Crypto only
  * Forex only
  * Stocks only
  * Or **all simultaneously**
* Each market may:

  * Use different models
  * Use different risk rules
  * Use different brokers/exchanges

Switching from one market to another (e.g., Crypto → Forex) must:

* Require changing ONLY:

  * DataFeed adapter
  * Broker/Exchange execution adapter
* NOT require changes to:

  * Core engine
  * Models
  * UI

---

## 🧠 FUTURE AI & NEWS INTEGRATION

The architecture must be ready for:

* A secondary AI system that:

  * Ingests real-time financial news
  * Uses an LLM to analyze sentiment and impact
  * Converts news into **numerical market impact scores**
* These scores will:

  * Modify model confidence
  * Modify position sizing
  * Enable/disable some strategies dynamically

This AI News Engine must be:

* Independent
* Pluggable
* Optional

---

## 🧪 BACKTESTING & SIMULATION REQUIREMENTS

The system must support:

* Historical backtesting
* Walk-forward analysis
* Monte Carlo simulations
* Real-time paper trading using live data
* Exact same pipeline between:

  * Backtest
  * Paper trading
  * Live trading

This guarantees identical behavior across environments.

---

## ⚠️ RISK MANAGEMENT REQUIREMENTS

The system must include:

* Global risk manager
* Per-market risk profiles
* Per-model risk profiles
* Max drawdown limits
* Daily loss limits
* Position sizing rules
* Leverage control
* Emergency shutdown system
* Manual override

---

## 🖥 UI / INTERFACE PHILOSOPHY

The PRS must propose:

* A local system running on a personal computer
* UI options comparison:

  * Web-based dashboard
  * Desktop application
* Features:

  * Live charts
  * Open positions
  * Model outputs
  * Risk metrics
  * Multi-market monitoring
  * Manual intervention panel

---

## 🔐 SECURITY REQUIREMENTS

Include security requirements for:

* API key management
* Encrypted credential storage
* Environment isolation (dev / test / prod)
* Logging
* Audit trails
* Fail-safe modes

---

## ⚠️ LEGAL & COMPLIANCE (HIGH LEVEL)

The PRS must include a non-legal high-level overview of:

* Personal trading vs commercial distribution
* Broker API terms
* Liability limitations
* Data privacy
* Market regulations awareness (no legal advice needed)

---

## 🛣 DEVELOPMENT ROADMAP

The PRS must include phases such as:

1. Core engine & architecture
2. First single-market implementation (Crypto or Forex)
3. Backtesting engine
4. Advisory mode first
5. Operator mode later
6. Risk engine
7. Multi-market expansion
8. UI dashboard
9. AI news module (future)

---

## ✅ FINAL DELIVERABLE

I want a **full professional PRS document**, structured with:

* Executive summary
* Product scope
* User personas
* System architecture diagram (described in text)
* Functional requirements
* Non-functional requirements
* API abstraction layers
* Model interface definition
* Market adapter design
* Risk management framework
* UI requirements
* Security
* Compliance
* Deployment
* Roadmap


