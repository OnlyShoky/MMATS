# Seguridad y Cumplimiento

Este documento cubre prácticas de seguridad, gestión de credenciales, separación de entornos, logging de auditoría y conciencia de cumplimiento para **MMATS**.

> [!CAUTION]
> La seguridad en sistemas de trading es crítica. Credenciales comprometidas pueden llevar a pérdida financiera.

---

## Principios de Seguridad

1. **Defensa en Profundidad**: Múltiples capas de seguridad
2. **Mínimo Privilegio**: Acceso mínimo requerido
3. **Defaults Seguros**: Seguro por defecto
4. **Auditar Todo**: Logging completo de actividad
5. **Encriptación**: Proteger datos en reposo y en tránsito

---

## Gestión de Credenciales

### Seguridad de Claves API

```
┌─────────────────────────────────────────────────────────┐
│               GESTIÓN DE CREDENCIALES                    │
│                                                          │
│  ENCRIPTACIÓN: AES-256-GCM                              │
│  ALMACENAMIENTO:                                         │
│  credentials/                                            │
│  ├── .gitignore         ← Excluir directorio            │
│  ├── dev.encrypted      ← Claves desarrollo             │
│  ├── prod.encrypted     ← Claves producción             │
│  └── master.key        ← SOLO en keychain del SO        │
└─────────────────────────────────────────────────────────┘
```

### Integración con Keyring del SO

| Sistema Operativo | Keyring |
|-------------------|---------|
| Windows | Credential Manager |
| macOS | Keychain |
| Linux | Secret Service |

> [!IMPORTANT]
> Nunca habilitar permisos de retiro en claves API. Acceso solo-trading limita el daño potencial.

---

## Separación de Entornos

| Entorno | Propósito | Credenciales |
|---------|-----------|--------------|
| **Desarrollo** | Desarrollo de código | Claves testnet |
| **Paper** | Simulación en vivo | Solo-lectura si es posible |
| **Producción** | Trading en vivo | Claves de producción |

### Nunca Subir Secretos

```gitignore
credentials/
*.encrypted
.env
config/prod.yaml
```

---

## Seguridad de Red

### Uso Local (Fase 1)

- Dashboard: `127.0.0.1:8080` SOLAMENTE
- Sin exposición de red externa
- Solo conexiones salientes (APIs de Brokers)

### Acceso Remoto Futuro

- TLS 1.3 requerido
- Túnel SSH o VPN
- Whitelist de IPs

---

## Logging de Auditoría

### Eventos Logueados

| Categoría | Eventos |
|-----------|---------|
| **Trading** | Todas las señales, órdenes, ejecuciones |
| **Configuración** | Cambios de settings |
| **Riesgo** | Breaches de límites |
| **Sistema** | Inicios, paradas, errores |

### Formato de Log

```json
{
  "timestamp": "2024-12-08T14:35:22Z",
  "level": "INFO",
  "module": "execution_engine",
  "event": "order_placed",
  "data": { "symbol": "BTCUSDT", "side": "BUY" }
}
```

### Prácticas de Seguridad

- **Enmascaramiento**: `api_key: ****3a2f`
- **Solo-Append**: Prevenir manipulación
- **Retención**: 12 meses mínimo

---

## Mecanismos Fail-Safe

| Escenario | Comportamiento Default |
|-----------|------------------------|
| Fallo de auth | Denegar acceso |
| Error de parsing de límite de riesgo | Usar límites más estrictos |
| Señal desconocida | HOLD (no operar) |
| Pérdida de conexión API | Pausar trading |

---

## Conciencia de Cumplimiento

> [!WARNING]
> Esta sección es solo conciencia general. Consultar asesores legales para requisitos específicos.

### Divulgaciones Requeridas

- "El trading conlleva riesgo significativo de pérdida"
- "El rendimiento pasado no garantiza resultados futuros"
- "El trading algorítmico puede amplificar pérdidas"
- "Esto no es asesoramiento financiero"

### Términos de Brokers

- Verificar que trading automatizado está permitido
- Respetar límites de rate de API
- Evitar actividades prohibidas

---

## Checklist de Seguridad

### Setup Inicial

- [ ] Claves API encriptadas
- [ ] Master key en keyring del SO
- [ ] Git ignorando credenciales
- [ ] Testnet para desarrollo
- [ ] Dashboard solo en localhost

### Mantenimiento Continuo

- [ ] Rotar claves API cada 90 días
- [ ] Revisar logs de auditoría semanalmente
- [ ] Actualizar dependencias

---

## Documentación Relacionada

- [[architecture_overview.md]] — Arquitectura del sistema
- [[risk_management.md]] — Controles de emergencia
