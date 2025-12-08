# Conceptos de Trading

Este documento proporciona una visión completa de los conceptos financieros y de trading esenciales para entender y trabajar con el **Sistema Automatizado de Trading Multi-Mercado (MMATS)**.

> [!TIP]
> Este documento está diseñado para desarrolladores y usuarios que pueden no tener experiencia extensa en trading. Todos los conceptos se explican con contexto específico de MMATS.

---

## Visión General de los Mercados Financieros

### ¿Qué es un Mercado Financiero?

Un mercado financiero es un lugar donde compradores y vendedores comercian activos como acciones, divisas, materias primas y derivados. MMATS soporta tres tipos principales de mercados:

| Tipo de Mercado | Descripción | Horario | Ejemplos |
|-----------------|-------------|---------|----------|
| **Crypto** | Criptomonedas descentralizadas | 24/7 | Bitcoin (BTC), Ethereum (ETH) |
| **Forex** | Divisas | 24/5 (Lun-Vie) | EUR/USD, GBP/JPY |
| **Acciones** | Participaciones en empresas | Horario de bolsa | AAPL, GOOGL, TSLA |

---

## Participantes Clave del Mercado

### Brokers vs Exchanges

```
┌─────────────────────────────────────────────────────┐
│                  USUARIO/TRADER                      │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                     BROKER                           │
│  (Binance, OANDA, Interactive Brokers)              │
│  - Proporciona acceso API                           │
│  - Gestiona cuentas                                 │
│  - Ejecuta órdenes                                  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                    EXCHANGE                          │
│  (NYSE, NASDAQ, Mercado Forex)                       │
│  - Empareja órdenes de compra/venta                 │
│  - Determina precios de mercado                     │
└─────────────────────────────────────────────────────┘
```

- **Broker**: Intermediario que proporciona acceso a mercados. MMATS se conecta a brokers vía APIs.
- **Exchange**: El mercado real donde se emparejan las órdenes.

---

## Tipos de Órdenes

### Orden de Mercado (Market Order)
- **Definición**: Ejecutar inmediatamente al mejor precio disponible
- **Ventajas**: Ejecución garantizada
- **Desventajas**: El precio puede deslizarse (slippage)

### Orden Límite (Limit Order)
- **Definición**: Ejecutar solo al precio especificado o mejor
- **Ventajas**: Control del precio
- **Desventajas**: Puede no ejecutarse

### Stop-Loss
- **Definición**: Activa una orden cuando el precio alcanza un nivel
- **Propósito**: Limitar pérdidas en posiciones existentes

### Take-Profit
- **Definición**: Cierra automáticamente la posición al alcanzar beneficio objetivo
- **Propósito**: Asegurar ganancias

---

## Conceptos de Posición

### Posición Larga (Long)
Abrir una posición **larga** significa comprar un activo esperando que su precio **suba**.

```
COMPRAR a $100 → Precio sube a $120 → VENDER → Beneficio: $20
```

### Posición Corta (Short)
Abrir una posición **corta** significa vender un activo (prestado) esperando que su precio **baje**.

```
VENDER (prestado) a $100 → Precio baja a $80 → RECOMPRAR → Beneficio: $20
```

---

## Conceptos de Riesgo y Recompensa

### Apalancamiento (Leverage)

El apalancamiento permite operar con capital prestado, amplificando ganancias y pérdidas.

| Apalancamiento | Margen Requerido | Tamaño Posición | $100 → $110 | $100 → $90 |
|----------------|------------------|-----------------|-------------|------------|
| 1x | $100 | $100 | +$10 (10%) | -$10 (10%) |
| 5x | $100 | $500 | +$50 (50%) | -$50 (50%) |
| 10x | $100 | $1000 | +$100 (100%) | -$100 (100%) |

> [!WARNING]
> Alto apalancamiento puede llevar a pérdida rápida de capital.

Ver: [[risk_management.md]] para controles de riesgo.

### Drawdown

**Drawdown** mide la caída desde un pico en el capital.

```
Capital Pico: $10,000
Capital Actual: $8,500
Drawdown: ($10,000 - $8,500) / $10,000 = 15%
```

### Ratio Riesgo-Recompensa

```
Entrada: $100
Stop-Loss: $95 (Riesgo: $5)
Take-Profit: $115 (Recompensa: $15)

Ratio: 15:5 = 3:1
```

---

## Conceptos de Datos de Mercado

### Datos OHLCV

Formato estándar de velas usado en MMATS:

| Campo | Descripción |
|-------|-------------|
| **O**pen (Apertura) | Primer precio del intervalo |
| **H**igh (Máximo) | Precio más alto del intervalo |
| **L**ow (Mínimo) | Precio más bajo del intervalo |
| **C**lose (Cierre) | Último precio del intervalo |
| **V**olume (Volumen) | Cantidad total negociada |

### Temporalidades (Timeframes)

| Temporalidad | Código | Uso |
|--------------|--------|-----|
| 1 Minuto | 1m | Scalping |
| 5 Minutos | 5m | Trading a corto plazo |
| 1 Hora | 1H | Swing trading |
| 1 Día | 1D | Análisis a largo plazo |

---

## Indicadores Técnicos

### Medias Móviles

#### Media Móvil Simple (SMA)
Promedio de precios de cierre durante N períodos.

#### Media Móvil Exponencial (EMA)
Promedio ponderado dando más importancia a precios recientes.

### RSI (Índice de Fuerza Relativa)
Oscilador de momentum que mide condiciones de sobrecompra/sobreventa.

- **RSI > 70**: Sobrecompra (posible señal de venta)
- **RSI < 30**: Sobreventa (posible señal de compra)

---

## Conceptos de Estrategia

### Generación de Señales

Las estrategias MMATS generan **señales**—recomendaciones operables:

| Acción | Significado |
|--------|-------------|
| **BUY** | Entrar o añadir posición larga |
| **SELL** | Entrar o añadir posición corta |
| **HOLD** | Sin acción recomendada |
| **CLOSE** | Cerrar posición actual |

Ver: [[architecture_overview.md]] para detalles técnicos.

---

## Conceptos de Ejecución

### Slippage (Deslizamiento)

Diferencia entre precio esperado y precio real de ejecución.

```
Precio Esperado: $100.00
Ejecución Real: $100.15
Slippage: $0.15 (0.15%)
```

### Comisiones

| Tipo | Descripción |
|------|-------------|
| **Maker** | Añadir liquidez (órdenes límite) |
| **Taker** | Quitar liquidez (órdenes mercado) |
| **Spread** | Diferencia bid-ask (forex) |

---

## Documentación Relacionada

- [[architecture_overview.md]] — Arquitectura del sistema
- [[risk_management.md]] — Controles de riesgo
- [[backtesting_and_simulation.md]] — Pruebas en datos históricos
- [[multi_market_operations.md]] — Trading multi-mercado

---

> [!IMPORTANT]
> El trading conlleva riesgo significativo de pérdida. Esta documentación es educativa y no constituye asesoramiento financiero.
