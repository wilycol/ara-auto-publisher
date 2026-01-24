# Ara Neuro Post

## Documentación de IA & Estrategia Multi‑Proveedor (Free‑First)

> Objetivo: operar **bien, estable y gratis** el mayor tiempo posible. Monetizar después. Glamour luego.

---

## 1. Principio Rector

La IA **no es el producto**. Es un **recurso intercambiable**.

Ara Neuro Post está diseñado para:

* Cambiar de proveedor de IA **sin tocar el core**.
* Priorizar proveedores **gratuitos o con free‑tier**.
* Escalar a IA paga **solo cuando haya ingresos**.

Si una IA cae → otra entra. Sin drama.

---

## 2. Contrato de IA (la regla del juego)

Todo proveedor debe cumplir esto:

### Entrada

* `prompt: str`

### Salida (`AIResponse`)

* `title: str`
* `content: str`
* `raw_response: dict`

Mientras cumpla eso, **entra al sistema**.

---

## 3. Arquitectura IA (simple y elegante)

```
AutoPublisherService
        ↓
      AIClient  ← interfaz
        ↓
┌──────────────────────────┐
│ MockAIClient             │  (tests)
│ OpenAICompatibleClient   │  (OpenAI, DeepSeek, etc.)
│ GeminiAdapter (futuro)   │
│ LocalLLMClient (futuro)  │
└──────────────────────────┘
```

Nada depende de una IA específica.

---

## 4. Estrategia Multi‑IA (Gratis Primero)

### 🥇 Prioridad #1 — OpenAI‑Compatible Free Tier

Incluye:

* DeepSeek
* OpenRouter (modelos gratis)
* Otros endpoints compatibles

**Ventajas**

* Ya soportado por el backend
* Cero cambios de código
* Free tiers reales

**Configuración ejemplo**

```
AI_PROVIDER=openai
AI_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat
AI_API_KEY=sk-xxxx
```

---

### 🥈 Prioridad #2 — Mock + Cache Inteligente

Mientras no haya llamadas:

* MockAIClient
* Contenido base reutilizable
* Variaciones simples (templates)

👉 Ideal para pruebas, demos, staging.

---

### 🥉 Prioridad #3 — Gemini (cuando se requiera)

* Requiere adaptador
* No 100% OpenAI‑compatible
* Gratis pero con límites

Se integra **cuando haga falta**, no antes.

---

## 5. Fallback Automático (Diseño Recomendado)

Orden sugerido:

1. IA Principal (gratis)
2. IA Secundaria (otro free tier)
3. MockAIClient (emergencia)

Nunca se bloquea un Job.
Nunca se pierde el sistema.

---

## 6. Estados del Post (Importante)

* `pending`
* `generated`
* `failed_ai`
* `scheduled`
* `published`

Un fallo de IA **NO es un fallo del sistema**.

---

## 7. Cuándo pasar a IA de Pago

Checklist obligatoria:

* Frontend funcionando
* Usuarios activos
* Jobs ejecutándose solos
* Algún ingreso real

Si no hay dinero → **no hay IA paga**. Fin.

---

## 8. Roadmap IA

### Fase 1 (actual)

* OpenAI‑compatible gratis
* Mock estable

### Fase 2

* Fallback multi‑proveedor
* Cache de respuestas

### Fase 3

* IA paga selectiva

### Fase 4

* IA local (solo si escala)

---

## 9. Regla de Oro

> Si la IA se cae, el negocio no.

Ese es el diseño.

---

Documento vivo. Se ajusta cuando el dinero entre.
