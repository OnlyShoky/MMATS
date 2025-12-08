# Arquitectura del Sistema

Este documento explica la arquitectura del **Sistema Automatizado de Trading Multi-Mercado (MMATS)**, su diseño modular y cómo interactúan los componentes.

> [!NOTE]
> MMATS sigue patrones de **Arquitectura Limpia** y **Hexagonal (Puertos y Adaptadores)** para asegurar flexibilidad, testabilidad y mantenibilidad.

---

## Principios Arquitectónicos

### Arquitectura Limpia

La Arquitectura Limpia separa responsabilidades en capas distintas:

```
┌─────────────────────────────────────────────────────────┐
│                    Capa de Presentación                  │
│              (Dashboard Web / UI de Escritorio)          │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Capa de Aplicación                    │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│   │    Modo      │  │    Modo      │  │   Motor de   │ │
│   │   Advisory   │  │   Operator   │  │  Backtesting │ │
│   └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Capa de Dominio (Core)                  │
│    Orquestación de Estrategias | Gestión de Riesgos     │
│         Gestor de Portfolio | Tracker de Posiciones      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│            Capa de Infraestructura (Adaptadores)         │
│   Datos de Mercado | Ejecución | Almacenamiento          │
└─────────────────────────────────────────────────────────┘
```

---

## Componentes Principales

### 1. Motor de Orquestación de Estrategias

**Responsabilidad**: Cargar, ejecutar y coordinar múltiples modelos de trading.

| Función | Descripción |
|---------|-------------|
| Model Loader | Carga dinámica desde directorio de estrategias |
| Model Executor | Ejecución paralela de estrategias independientes |
| Signal Aggregator | Agregación de señales para plan de ejecución |

### 2. Motor de Gestión de Riesgos

**Responsabilidad**: Aplicar límites de riesgo y proteger el capital.

- Position Sizer — Calcular tamaños seguros de posición
- Drawdown Monitor — Rastrear caída desde pico
- Exposure Calculator — Monitorear capital en riesgo
- Emergency Shutdown — Lógica de circuit breaker

Ver: [[risk_management.md]] para documentación completa de riesgos.

### 3. Gestor de Portfolio

| Función | Descripción |
|---------|-------------|
| Tracking de Posiciones | Actualizaciones en tiempo real |
| Calculador de P&L | Beneficio/pérdida realizado y no realizado |
| Gestor de Balance | Balance de cuenta por mercado |
| Historial de Transacciones | Journal completo de trades |

---

## Interfaz de Estrategia

Todos los modelos implementan una interfaz estandarizada:

```python
class IStrategy:
    """Interfaz base para todas las estrategias"""
    
    # Metadatos
    name: str
    version: str
    markets_supported: List[MarketType]
    timeframes_supported: List[Timeframe]
    
    # Método Principal
    def on_bar(self, context: StrategyContext) -> Signal:
        """
        Llamado en cada nueva vela
        
        Returns:
            Signal: {
                action: BUY | SELL | HOLD | CLOSE,
                symbol: str,
                position_size: float (0-1),
                stop_loss: float,
                take_profit: float,
                confidence: float (0-1)
            }
        """
        pass
```

### Beneficios

- ✅ Mismo código ejecuta en backtest, paper y live
- ✅ Sin dependencias directas de mercado/broker
- ✅ Hot-reloading sin reiniciar sistema
- ✅ Fácil testing con datos mock

---

## Interfaces de Adaptadores

### Proveedor de Datos de Mercado

```python
class IMarketDataProvider:
    async def get_historical_candles(symbol, timeframe, start, end) -> List[OHLCV]
    async def get_latest_price(symbol) -> Tick
    async def subscribe_to_updates(symbol, callback)
```

**Implementaciones**: Binance, OANDA, Interactive Brokers, Simulado

### Proveedor de Ejecución

```python
class IExecutionProvider:
    async def place_order(order) -> OrderConfirmation
    async def cancel_order(order_id) -> CancelConfirmation
    async def get_positions() -> List[Position]
```

---

## Pipeline de Datos

```
1. FETCH DE DATOS CRUDOS
   └─> Adaptador específico de mercado

2. NORMALIZACIÓN
   └─> Convertir a formato MarketData estándar

3. CÁLCULO DE INDICADORES
   └─> TA-Lib, pandas-ta

4. ENSAMBLAJE DE CONTEXTO
   └─> Combinar datos + estado de cuenta

5. EJECUCIÓN DE ESTRATEGIA
   └─> Pasar contexto a estrategias registradas
```

---

## Modos de Operación

### Modo Advisory

- Computa señales de estrategia
- Muestra en dashboard
- NO envía órdenes al broker
- Tracking opcional de rendimiento paper

### Modo Operator

- Genera señales
- Validación de riesgos
- Ejecuta órdenes reales
- **DINERO REAL EN RIESGO**

Ver: [[multi_market_operations.md]] para detalles de modos.

---

## Stack Tecnológico

| Capa | Tecnología | Razón |
|------|------------|-------|
| Aplicación Core | Python 3.11+ | Ecosistema rico, desarrollo rápido |
| BD Time-Series | TimescaleDB/InfluxDB | Optimizada para datos OHLCV |
| BD Relacional | PostgreSQL | Transacciones, posiciones |
| Caché | Redis | Datos en tiempo real |
| Backend Web | FastAPI | Moderno, async |
| Frontend | React/Svelte | Dashboard en tiempo real |
| Deployment | Docker Compose | Servicios containerizados |

---

## Requisitos de Rendimiento

| Operación | Latencia Objetivo | Latencia Máxima |
|-----------|-------------------|-----------------|
| Cómputo de estrategia | <50ms | 100ms |
| Validación de riesgo | <10ms | 25ms |
| Envío de orden | <200ms | 500ms |
| Ingestión de datos | <100ms | 200ms |

---

## Documentación Relacionada

- [[trading_concepts.md]] — Fundamentos de trading
- [[risk_management.md]] — Controles de riesgo
- [[multi_market_operations.md]] — Orquestación multi-mercado
- [[backtesting_and_simulation.md]] — Testing histórico
