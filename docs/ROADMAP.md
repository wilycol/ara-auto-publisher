# Roadmap de Producto - Ara Auto Publisher

## Fase 1: MVP (Estado Actual)
- ✅ Generación de contenido asistida por IA.
- ✅ Modos de Guía: Guiado, Colaborador, Experto.
- ✅ Gestión de Campañas Básica.
- 🔄 **Identidades Funcionales (Nivel 1):** Perfiles de tono/estilo sin conexión externa.

## Fase 2: Post-MVP (Identidades Conectadas)
Esta fase transformará las Identidades Funcionales en agentes con capacidad de acción directa.

### Características Planificadas:
1.  **Metadatos Extendidos:**
    *   Asociación de correos electrónicos específicos por identidad.
    *   Notas internas y "memorias" específicas de la identidad (preferencias aprendidas).
2.  **Conectividad (OAuth):**
    *   Vinculación real con cuentas de LinkedIn, X (Twitter), Telegram.
    *   Cada identidad podrá tener sus propios tokens de acceso.
3.  **Publicación Directa:**
    *   Capacidad de enviar el contenido aprobado directamente a la API de la red social.
4.  **Agentes Persistentes:**
    *   Las identidades podrán tener tareas programadas (ej. "Buscar noticias sobre X tema cada mañana").

### Consideraciones Técnicas Futuras:
*   Implementación de gestión segura de secretos (Vault o encriptación DB).
*   Sistema de colas para tareas en segundo plano (Celery/Redis).
*   Expansión del modelo de datos para soportar `OAuthToken` relacionados con `Identity`.

---
*Este documento es una declaración de intenciones y está sujeto a cambios según feedback de usuarios y viabilidad técnica.*
