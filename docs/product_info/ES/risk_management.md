# Gestión de Riesgos

Este documento explica el sistema integral de gestión de riesgos en **MMATS**, diseñado para proteger el capital y aplicar trading disciplinado.

> [!CAUTION]
> El trading conlleva riesgo significativo de pérdida financiera. La gestión de riesgos no elimina el riesgo—gestiona la exposición dentro de límites aceptables.

---

## Filosofía de Gestión de Riesgos

### Principios Fundamentales

1. **Preservación del Capital Primero**: Proteger el principal antes de buscar beneficios
2. **Validación Pre-Trade**: Bloquear trades riesgosos ANTES de la ejecución
3. **Controles Multi-Nivel**: Límites globales, por mercado, por estrategia y por posición
4. **Defaults Seguros**: Estados desconocidos defaultean al comportamiento más seguro
5. **Circuit Breakers**: Shutdown automático en condiciones extremas

---

## Jerarquía de Riesgos

```
┌─────────────────────────────────────────────────────────┐
│                   LÍMITES GLOBALES                       │
│              (Nivel de Sistema Completo)                 │
│  • Exposición total del portfolio                        │
│  • Máximo drawdown desde pico                           │
│  • Límite de pérdida diaria (todos los mercados)        │
├─────────────────────────────────────────────────────────┤
│                 LÍMITES POR MERCADO                      │
│           (Crypto | Forex | Acciones)                    │
│  • Máxima asignación de capital por mercado             │
│  • Límites de apalancamiento por mercado                │
├─────────────────────────────────────────────────────────┤
│               LÍMITES POR ESTRATEGIA                     │
│        (Dentro de cada asignación de mercado)            │
│  • Capital asignado a cada estrategia                   │
│  • Máximas posiciones por estrategia                    │
├─────────────────────────────────────────────────────────┤
│                LÍMITES POR SÍMBOLO                       │
│           (Concentración de Posición)                    │
│  • Tamaño máximo por activo individual                  │
└─────────────────────────────────────────────────────────┘
```

---

## Tipos de Límites de Riesgo

### Límites de Tamaño de Posición

| Configuración | Descripción | Ejemplo |
|---------------|-------------|---------|
| `max_position_pct` | Máximo % de capital por trade | 2% |
| `max_position_usd` | Máximo $ por trade | $100 |

### Límites de Apalancamiento

| Mercado | Máximo Recomendado | Máximo Agresivo |
|---------|-------------------|-----------------|
| Crypto Spot | 1x | 1x |
| Crypto Futures | 3x | 10x |
| Forex | 10x | 30x |
| Acciones | 2x | 4x |

> [!WARNING]
> Mayor apalancamiento amplifica tanto ganancias como pérdidas.

### Límites de Drawdown

**MaxDrawdownRule**: Detiene el trading cuando el capital cae demasiado desde el pico.

| Umbral | Acción |
|--------|--------|
| 80% del límite | Notificación de advertencia |
| 90% del límite | Alerta + reducir tamaños |
| 100% del límite | Pausar todo el trading |

### Límites de Pérdida Diaria

**DailyLossLimitRule**: Pérdida máxima permitida por día de trading.

| Configuración | Descripción | Default |
|---------------|-------------|---------|
| `daily_loss_pct` | Máxima pérdida diaria como % | 3% |
| `daily_loss_usd` | Máxima pérdida diaria en $ | $50 |

---

## Sistema de Shutdown de Emergencia

### Condiciones de Activación

| Trigger | Severidad | Acción Default |
|---------|-----------|----------------|
| Botón de emergencia manual | CRÍTICO | Shutdown HARD |
| Detección de error crítico | CRÍTICO | FREEZE |
| Breach de máximo drawdown | ALTO | Shutdown SOFT |
| Pérdida de conexión API >60s | ALTO | Shutdown SOFT |

### Modos de Shutdown

```
SOFT SHUTDOWN
• Detener generación de nuevas órdenes
• Gestionar posiciones existentes normalmente
• Honrar stop-loss y take-profit

HARD SHUTDOWN
• Detener TODAS las órdenes inmediatamente
• Cerrar TODAS las posiciones a precio de mercado
• Cancelar TODAS las órdenes pendientes

FREEZE
• Detener TODO
• Intervención manual REQUERIDA
• Auditoría completa antes de reiniciar
```

---

## Configuración de Riesgos

```yaml
risk_management:
  global:
    max_drawdown_pct: 15
    daily_loss_limit_pct: 3
    max_open_positions: 10
    max_leverage: 5
    
  markets:
    crypto:
      max_allocation_pct: 40
      max_leverage: 3
      
    forex:
      max_allocation_pct: 40
      max_leverage: 10
```

---

## Monitor de Riesgos (Dashboard)

```
┌─────────────────────────────────────────────────────────┐
│                  MONITOR DE RIESGOS                      │
│                                                          │
│  EXPOSICIÓN GLOBAL   ████████░░░░░░░░░░░░  42% / 50%   │
│  P&L DIARIO          -$35 / -$150 límite  ⚠️ 23%       │
│  DRAWDOWN            6.2% / 15% límite    ✅ OK        │
│  POSICIONES ABIERTAS 7 / 10              ✅ OK        │
└─────────────────────────────────────────────────────────┘
```

Ver: [[ui_and_user_experience.md]] para documentación completa de UI.

---

## Mejores Prácticas

### Para Traders Conservadores

- [ ] Empezar con 1% máximo de tamaño de posición
- [ ] Usar 5% máximo de límite de drawdown
- [ ] Operar solo 2-3 mercados inicialmente
- [ ] Usar paper trading por 2+ semanas primero

### Directrices Generales

1. **Nunca sobrepasar límites de riesgo** sin razón documentada
2. **Revisar rachas perdedoras** — ajustar antes de alcanzar límite de drawdown
3. **Backtestear configuraciones de riesgo**
4. **Escalar gradualmente** — aumentar límites solo tras éxito consistente

---

## Documentación Relacionada

- [[trading_concepts.md]] — Conceptos fundamentales
- [[architecture_overview.md]] — Arquitectura del motor de riesgos
- [[backtesting_and_simulation.md]] — Testing de configuraciones de riesgo

---

> [!IMPORTANT]
> La gestión de riesgos no es opcional. Cada trade debe pasar por el pipeline de validación de riesgos.
