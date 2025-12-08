# Operaciones Multi-Mercado

Este documento explica cómo **MMATS** maneja el trading simultáneo en múltiples mercados, el cambio entre mercados y los diferentes modos operacionales.

---

## Filosofía Multi-Mercado

### Agnosticismo de Mercado

MMATS está diseñado para ser **agnóstico del mercado**—el motor core contiene **cero código específico de mercado**:

1. **Interfaces Estandarizadas**: Todos los mercados implementan los mismos puertos
2. **Configuración**: Mercados habilitados/deshabilitados via archivos de config
3. **Patrón Adaptador**: Lógica específica aislada en adaptadores
4. **Formato de Datos Unificado**: Todos los datos normalizados a estructura común

### Mercados Soportados

| Mercado | Ejemplos de Proveedores | Tipos de Activos | Horario |
|---------|------------------------|------------------|---------|
| **Crypto** | Binance, Coinbase | BTC, ETH, altcoins | 24/7 |
| **Forex** | OANDA, Interactive Brokers | Pares de divisas | 24/5 |
| **Acciones** | Interactive Brokers | Equity, ETFs | Horario de bolsa |

---

## Configuración de Mercados

```yaml
markets:
  crypto:
    enabled: true
    provider: binance
    symbols:
      - BTCUSDT
      - ETHUSDT
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
    strategies:
      - breakout_v1
    timeframe: 1H
    risk_allocation_pct: 40
```

---

## Aislamiento de Mercados

> [!IMPORTANT]
> Un fallo en un mercado NO afecta a otros mercados.

| Escenario | Comportamiento |
|-----------|----------------|
| API de Binance caída | Estrategias crypto pausan, Forex continúa |
| Error de auth en OANDA | Forex para, Crypto no afectado |
| Timeout de red | Mercado afectado reintenta, otros no afectados |

---

## Modos de Operación

### Modo Advisory

**Propósito**: Generar señales SIN ejecutar órdenes.

```
┌─────────────────────────────────────────────────────────┐
│                   MODO ADVISORY                          │
│                                                          │
│  Mercado │ Símbolo  │ Señal   │ Confianza │ Hora       │
│  ────────┼──────────┼─────────┼───────────┼─────────── │
│  Crypto  │ BTCUSDT  │ BUY     │ 0.75      │ 10:05      │
│  Forex   │ EUR_USD  │ HOLD    │ 0.60      │ 10:05      │
│                                                          │
│  [Todas las señales logueadas - NO se ejecutan órdenes] │
└─────────────────────────────────────────────────────────┘
```

### Modo Operator

**Propósito**: Trading automatizado completo con ejecución de órdenes reales.

> [!CAUTION]
> El modo Operator usa capital real. Asegúrate de entender los riesgos y haber testeado en modo paper primero.

**Checklist de Seguridad**:
- [ ] Paper trading por mínimo 2 semanas
- [ ] Límites de riesgo configurados
- [ ] Contactos de emergencia establecidos
- [ ] Confirmación doble completada

---

## Ejecución Multi-Estrategia

### Estrategias Concurrentes

MMATS puede ejecutar múltiples estrategias simultáneamente:

```
MERCADO CRYPTO
├─ momentum_v1 ──────> [BTC: BUY, ETH: HOLD]
└─ mean_reversion_v2 ─> [BTC: HOLD, ETH: SELL]

MERCADO FOREX
├─ breakout_v1 ──────> [EUR_USD: BUY]
└─ trend_v1 ──────────> [EUR_USD: HOLD]

         ↓
   AGREGACIÓN DE SEÑALES
         ↓
   VALIDACIÓN DE RIESGOS
         ↓
   EJECUCIÓN DE ÓRDENES
```

### Resolución de Conflictos de Señales

| Modo | Comportamiento |
|------|----------------|
| **CONSENSUS** | Ejecutar si >50% de estrategias concuerdan |
| **WEIGHTED** | Ponderar por scores de confianza |
| **PRIORITY** | Ejecutar solo la estrategia de mayor prioridad |
| **INDEPENDENT** | Ejecutar todas (posición separada por estrategia) |

---

## Gestión de Riesgos Cross-Mercado

### Límites Globales

```
EXPOSICIÓN GLOBAL: 45% de $10,000 = $4,500
├─ Crypto:   $2,000 (44%)
├─ Forex:    $1,800 (40%)
└─ Acciones: $700  (16%)

LÍMITE MÁX EXPOSICIÓN: 50%
ESTADO: ✅ DENTRO DE LÍMITES
```

### Asignación por Mercado

| Mercado | Asignación | Apalancamiento Máx | Posiciones Máx |
|---------|------------|-------------------|----------------|
| Crypto | 40% | 3x | 5 |
| Forex | 40% | 10x | 3 |
| Acciones | 20% | 2x | 5 |

Ver: [[risk_management.md]] para documentación completa.

---

## Añadir o Cambiar Mercados

### Añadir un Nuevo Mercado

1. **Implementar Adaptador**: Crear nuevos proveedores de ejecución y datos
2. **Configurar Mercado**: Añadir sección al archivo de config
3. **Asignar Estrategias**: Mapear estrategias compatibles
4. **Configurar Límites de Riesgo**
5. **Testear**: Paper trade antes de live

### Deshabilitar un Mercado

```yaml
forex:
  enabled: false  # Solo cambiar este flag
```

---

## Mejores Prácticas

### Empezando con Multi-Mercado

1. **Empezar con Un Mercado**: Dominar uno antes de añadir otros
2. **Paper Trade Primero**: Testear interacción cross-mercado
3. **Asignación Conservadora**: No sobre-asignar inicialmente
4. **Monitorear Correlaciones**: Evitar activos correlacionados
5. **Añadir Gradualmente**: Agregar mercados uno a la vez

---

## Documentación Relacionada

- [[architecture_overview.md]] — Arquitectura del sistema
- [[risk_management.md]] — Controles de riesgo cross-mercado
- [[trading_concepts.md]] — Fundamentos de mercados
- [[ui_and_user_experience.md]] — Monitoreo en dashboard
