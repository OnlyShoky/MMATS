# Backtesting y Simulación

Este documento explica las capacidades de backtesting, análisis walk-forward, simulaciones Monte Carlo y paper trading en **MMATS**.

---

## Propósito del Backtesting

### ¿Por qué hacer Backtest?

El backtesting valida estrategias de trading contra datos históricos antes de arriesgar capital real:

| Beneficio | Descripción |
|-----------|-------------|
| **Validación** | Testear lógica sin riesgo financiero |
| **Optimización** | Encontrar parámetros óptimos |
| **Evaluación de Riesgo** | Entender drawdowns potenciales |
| **Construcción de Confianza** | Ganar confianza en el comportamiento |
| **Comparación** | Evaluar múltiples estrategias objetivamente |

> [!IMPORTANT]
> El rendimiento pasado NO garantiza resultados futuros. Los backtests son necesarios pero no suficientes.

---

## Configuración de Backtesting

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

---

## Simulación de Ejecución

### Modelado de Slippage

| Modelo | Descripción | Caso de Uso |
|--------|-------------|-------------|
| **Porcentaje** | % fijo del precio | Simple, propósito general |
| **Fijo** | Cantidad fija en $ | Activos de baja volatilidad |
| **Basado en ATR** | Basado en volatilidad | Se adapta al mercado |

### Simulación de Llenado de Órdenes

```
TIPO ORDEN      LÓGICA DE LLENADO
───────────────────────────────────
MARKET          Llenar al cierre + slippage

LIMIT BUY       Llenar si low ≤ precio límite

LIMIT SELL      Llenar si high ≥ precio límite

STOP LOSS       Disparar si precio cruza nivel stop
```

---

## Métricas de Rendimiento

### Métricas Core

| Métrica | Fórmula | Valor Bueno |
|---------|---------|-------------|
| **Retorno Total** | (Final - Inicial) / Inicial | Positivo |
| **Retorno Anualizado** | (1 + Total)^(365/días) - 1 | > Tasa libre de riesgo |
| **Ratio de Sharpe** | (Retorno - LibreRiesgo) / StdDev | > 1.0 |
| **Ratio de Sortino** | (Retorno - LibreRiesgo) / StdDev Bajista | > 1.5 |
| **Max Drawdown** | Mayor caída pico-a-valle | < 20% |
| **Win Rate** | Trades ganadores / Total trades | > 50%* |
| **Factor de Beneficio** | Beneficio Bruto / Pérdida Bruta | > 1.5 |

---

## Análisis Walk-Forward

### ¿Qué es Walk-Forward?

El testing walk-forward previene overfitting mediante:

1. **Optimizar** en datos in-sample
2. **Testear** en datos out-of-sample
3. **Avanzar** y repetir

```
Paso 1:
├── IN-SAMPLE (Optimizar) ──┤── OUT-OF-SAMPLE (Test) ──│
│      6 meses              │       1 mes              │

Paso 2:
     ├── IN-SAMPLE ───────────┤── OUT-OF-SAMPLE ───────│
     │      6 meses           │       1 mes            │

→ Combinar todos los resultados out-of-sample
```

### Interpretación de Resultados

| Escenario | Implicación |
|-----------|-------------|
| In-sample >> Out-of-sample | Probable overfitting |
| In-sample ≈ Out-of-sample | Buena generalización |
| Consistente entre ventanas | Estrategia robusta |

---

## Simulación Monte Carlo

### Propósito

Stress-test de robustez mediante:

1. **Reorganización de Trades**: Aleatorizar orden
2. **Muestreo Bootstrap**: Remuestrear con reemplazo
3. **Variación de Parámetros**: Pequeños cambios aleatorios

### Intervalos de Confianza

| Percentil | Caso de Uso |
|-----------|-------------|
| 5° | Peor escenario realista |
| 25° | Estimación conservadora |
| 50° (Mediana) | Resultado esperado |
| 75° | Estimación optimista |
| 95° | Mejor escenario realista |

---

## Paper Trading

### ¿Qué es Paper Trading?

Paper trading usa **datos de mercado en vivo** con **ejecución simulada**:

| Aspecto | Paper Trading | Backtesting |
|---------|---------------|-------------|
| Datos | En vivo, tiempo real | Históricos |
| Timing | Tiempo real | Instantáneo |
| Ejecución | Simulada | Simulada |
| Propósito | Validación en tiempo real | Validación histórica |

### Configuración

```yaml
paper_trading:
  enabled: true
  
  capital:
    initial: 10000
    currency: USD
    
  execution:
    slippage_pct: 0.1
    
  persistence:
    save_state: true
```

---

## Evitar Errores Comunes

### Sesgo de Look-Ahead

> [!CAUTION]
> El sesgo de look-ahead ocurre cuando información futura "filtra" a decisiones pasadas.

**Prevención MMATS**: Los datos están estrictamente ordenados en tiempo; los indicadores solo acceden a barras pasadas.

### Overfitting

**Síntomas**:
- Retornos de backtest extremadamente altos
- Muchos parámetros optimizados (>5)
- In-sample >> Out-of-sample
- Mal rendimiento en diferentes períodos

**Prevención**:
- Usar análisis walk-forward
- Limitar número de parámetros
- Testear en múltiples mercados/timeframes

---

## Reporte de Backtest

```
┌─────────────────────────────────────────────────────────┐
│      REPORTE BACKTEST: Momentum v1 en BTCUSDT           │
│               2023-01-01 a 2024-01-01                   │
├─────────────────────────────────────────────────────────┤
│  Capital Inicial:     $10,000                           │
│  Capital Final:       $12,450                           │
│  Retorno Total:       24.5%                             │
│  Max Drawdown:        12.3%                             │
│  Ratio Sharpe:        1.45                              │
│  Total Trades:        87                                │
│  Win Rate:            56.3%                             │
│  Factor Beneficio:    1.78                              │
└─────────────────────────────────────────────────────────┘
```

---

## Mejores Prácticas

### Antes de Trading en Vivo

- [ ] Backtest en 2+ años de datos
- [ ] Walk-forward muestra consistencia
- [ ] Monte Carlo percentil 5° es aceptable
- [ ] Paper trade por 2+ semanas
- [ ] Resultados alineados con expectativas

---

## Documentación Relacionada

- [[trading_concepts.md]] — Fundamentos de trading
- [[architecture_overview.md]] — Arquitectura del sistema
- [[risk_management.md]] — Controles de riesgo
