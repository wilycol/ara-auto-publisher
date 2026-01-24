# Selección de Proveedor de IA (Free-First Strategy)

> **Decisión:** El proveedor seleccionado para la Fase 1 es **OpenRouter**.

## 1. Análisis de Opciones

### A. DeepSeek (Directo)
*   **Pros**:
    *   Precios extremadamente bajos ($0.14/1M tokens).
    *   Compatible 100% con OpenAI.
    *   Rendimiento excelente (rivaliza con GPT-4).
*   **Contras**:
    *   **No tiene Free Tier de API permanente** (solo Chat es gratis, la API es prepago aunque barata).
    *   Requiere tarjeta/créditos desde el día 1.
    *   Riesgo de disponibilidad en horas pico (según región).

### B. OpenRouter (Agregador) 🏆 **GANADOR**
*   **Pros**:
    *   **Verdadero Free Tier**: Ofrece modelos gratuitos (marcados como `:free`) incluyendo versiones de DeepSeek, Gemini, Llama, etc.
    *   **Un solo Endpoint**: `https://openrouter.ai/api/v1`.
    *   **Cero Lock-in**: Cambias de `deepseek/deepseek-r1:free` a `google/gemini-2.0-flash-exp:free` solo cambiando un string. No tocas código.
    *   Compatibilidad OpenAI total.
*   **Contras**:
    *   Rate limits estrictos en modelos gratuitos (aprox 20 req/min, 50-200 req/día).
    *   La privacidad depende de los proveedores subyacentes.

---

## 2. Estrategia de Implementación

### Fase 1: Desarrollo & Pruebas (Actual)
*   **Proveedor**: OpenRouter
*   **Modelo Sugerido**: `deepseek/deepseek-chat:free` o `google/gemini-2.0-flash-exp:free` (vía OpenRouter para no usar adaptador nativo).
*   **Configuración**:
    ```env
    AI_PROVIDER=openai  # Usamos el cliente OpenAICompatible
    AI_BASE_URL=https://openrouter.ai/api/v1
    AI_API_KEY=sk-or-xxxx (Tu Key de OpenRouter)
    AI_MODEL=deepseek/deepseek-chat:free
    ```

### Fase 2: Producción (Low Cost)
*   Si el Free Tier se queda corto, simplemente cambiamos a un modelo de pago en OpenRouter o DeepSeek Directo.
*   Costo estimado para 100 posts/día: < $0.05 USD/mes.

---

## 3. Arquitectura de Seguridad

1.  **Intento 1**: Llamada a OpenRouter (Modelo Gratis).
2.  **Fallo/Límite**: El sistema captura el error.
3.  **Fallback**: No hay fallback automático a pago (por diseño "Free-First").
4.  **Red de Seguridad**: `MockAIClient` siempre disponible para desarrollo local si no hay internet o keys.

## 4. Próximos Pasos
1.  Obtener API Key en [OpenRouter](https://openrouter.ai/).
2.  Configurar `.env` con los valores de OpenRouter.
3.  Probar generación con `deepseek/deepseek-chat:free`.
