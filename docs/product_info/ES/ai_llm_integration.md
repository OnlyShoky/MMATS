# Integración de IA/LLM

Este documento explica la arquitectura futura de integración de **IA y Modelos de Lenguaje Grande (LLM)** en MMATS para análisis de sentimiento de noticias y evaluación de impacto de mercado.

> [!NOTE]
> La integración IA/LLM es una **característica futura planificada** (Fase 11). Este documento describe la arquitectura y cómo se integrará con los sistemas existentes.

---

## Visión y Propósito

### ¿Por qué Integrar IA?

Los mercados son influenciados por noticias, sentimiento y eventos externos. La integración IA/LLM permite:

1. **Monitoreo Automatizado de Noticias**: Procesar noticias 24/7
2. **Análisis de Sentimiento**: Entender el mood del mercado
3. **Evaluación de Impacto**: Predecir cómo las noticias afectan activos
4. **Mejora de Estrategias**: Modificar confianza basada en contexto
5. **Detección de Eventos**: Identificar eventos que mueven el mercado

---

## Arquitectura del Pipeline

```
┌─────────────────────────────────────────────────────────┐
│              PIPELINE DE SENTIMIENTO                     │
│                                                          │
│  ┌───────────────┐                                       │
│  │ Fuentes       │ RSS, APIs de noticias, Twitter/X     │
│  └───────┬───────┘                                       │
│          ▼                                               │
│  ┌───────────────┐                                       │
│  │  Agregador    │  Recopilar, deduplicar, filtrar      │
│  └───────┬───────┘                                       │
│          ▼                                               │
│  ┌───────────────┐                                       │
│  │ Analizador LLM│  Sentimiento + Relevancia + Impacto  │
│  └───────┬───────┘                                       │
│          ▼                                               │
│  ┌───────────────┐                                       │
│  │ Score Impacto │  Traducir a efectos de mercado       │
│  └───────┬───────┘                                       │
│          ▼                                               │
│  ┌───────────────┐                                       │
│  │ Integración   │  Modificar scores de confianza       │
│  │ con Estrategia│                                       │
│  └───────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

---

## Capa de Análisis LLM

### Dimensiones de Scoring

| Dimensión | Rango | Descripción |
|-----------|-------|-------------|
| **Sentimiento** | -1.0 a +1.0 | Negativo/Neutral/Positivo |
| **Relevancia** | 0.0 a 1.0 | Relación con activos objetivo |
| **Magnitud** | 0.0 a 1.0 | Fuerza del impacto potencial |
| **Confianza** | 0.0 a 1.0 | Certeza del LLM en evaluación |

### Ejemplo de Output

```json
{
  "news_id": "abc123",
  "headline": "Fed Anuncia Recorte de Tasas",
  "analysis": {
    "sentiment": 0.65,
    "relevance": {
      "BTCUSDT": 0.85,
      "EUR_USD": 0.95
    },
    "magnitude": 0.75,
    "timeframe": "immediato",
    "confidence": 0.88
  }
}
```

---

## Modelo de Impacto de Mercado

```python
@dataclass
class MarketImpact:
    symbol: str
    sentiment: float      # -1.0 a +1.0
    magnitude: float      # 0.0 a 1.0
    confidence: float     # 0.0 a 1.0
    timeframe: str        # inmediato, corto-plazo, largo-plazo
    summary: str
    sources: List[str]
```

### Categorías de Impacto

| Categoría | Descripción | Efecto Típico |
|-----------|-------------|---------------|
| **Alcista Alto-Impacto** | Noticia muy positiva | Aumentar confianza de compra |
| **Alcista Bajo-Impacto** | Noticia ligeramente positiva | Leve boost de confianza |
| **Neutral** | Sin dirección clara | Sin modificación |
| **Bajista Bajo-Impacto** | Noticia ligeramente negativa | Leve reducción |
| **Bajista Alto-Impacto** | Noticia muy negativa | Reducir posiciones |

---

## Integración con Estrategias

### Modificación de Confianza

```
Señal Original:
  Acción: BUY
  Confianza: 0.70
  
Impacto de Noticias (Alcista, Alta Magnitud):
  Sentimiento: +0.8
  Magnitud: 0.75
  
Señal Modificada:
  Confianza = 0.70 + (0.8 × 0.75 × 0.3) = 0.88
```

### Configuración

```yaml
ai_integration:
  enabled: true
  
  confidence_modification:
    sensitivity: 0.3
    max_boost: 0.2
    max_reduction: 0.3
    
  extreme_sentiment_actions:
    threshold: 0.9
    action: pause_strategy
    duration_minutes: 30
```

---

## Manejo de Condiciones Extremas

| Condición | Acción |
|-----------|--------|
| Sentimiento < -0.9 | Pausar todas las señales de compra |
| Sentimiento > +0.9 | Puede activar filtro FOMO |
| Múltiples fuentes conflictivas | Reducir confianza general |
| Sin noticias relevantes | Usar señales sin modificar |

---

## Extensiones Futuras

| Característica | Descripción | Timeline |
|----------------|-------------|----------|
| Análisis On-Chain | Movimientos de wallets, smart contracts | Fase 12+ |
| Transcripciones de Earnings | Parsear earnings calls | Fase 12+ |
| Discursos de Bancos Centrales | Análisis Fed, ECB, BOJ | Fase 12+ |
| Sentimiento Social | Reddit, Telegram | Fase 12+ |

---

## Mejores Prácticas

### Guías de Implementación

1. **Empezar Conservador**: Baja sensibilidad, observar antes de aumentar
2. **Validar Fuentes**: No todas las fuentes de noticias son confiables
3. **Override Manual**: Siempre permitir juicio humano
4. **Loguear Todo**: Rastrear qué noticias afectaron qué trades
5. **Backtestear**: Incluir datos de noticias en backtests históricos

> [!WARNING]
> El análisis IA/LLM es probabilístico. Nunca seguir ciegamente recomendaciones de IA.

---

## Documentación Relacionada

- [[architecture_overview.md]] — Arquitectura del sistema
- [[risk_management.md]] — Controles de riesgo y manejo de emergencias
- [[backtesting_and_simulation.md]] — Testing con datos de noticias
