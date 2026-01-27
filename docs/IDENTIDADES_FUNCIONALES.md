# Identidades Funcionales (MVP)

## Visión Estratégica
En el MVP, las Identidades Funcionales son **capas estratégicas de configuración**, no agentes operativos independientes. Actúan como un "filtro de intención" que modifica CÓMO Ara comunica el conocimiento del usuario, sin fragmentar el conocimiento en sí.

### Principios Fundamentales
1.  **Identidad Funcional vs. Operativa:**
    *   **MVP (Funcional):** Define estilo, tono, límites y propósito.
    *   **Fase 2 (Operativa):** Definirá credenciales, canales específicos y automatización.
2.  **Seguridad y Alcance:**
    *   ❌ No gestiona credenciales (passwords, tokens, OAuth).
    *   ❌ No almacena datos de contacto (emails, teléfonos).
    *   ❌ No realiza acciones autónomas en redes externas.

## Modelo de Datos (Campos Finales MVP)
Para mantener el foco estratégico, la identidad se define estrictamente por:

*   **`name`**: Nombre identificativo (ej. "Experto Técnico").
*   **`purpose`**: Para qué existe esta identidad (ej. "Educar sobre arquitectura de software").
*   **`tone`**: Tono de voz (ej. "Serio, analítico").
*   **`preferred_platforms`**: Dónde suele publicar (ej. ["LinkedIn", "Medium"]).
*   **`communication_style`**: Estilo narrativo (ej. "Storytelling", "Directo", "Educativo", "Hilos cortos").
*   **`content_limits`**: Restricciones explícitas (ej. "No usar emojis", "No vender agresivamente", "No hablar en primera persona").
*   **`status`**: Estado de gestión (`active`, `draft`, `archived`).

## Modelo de Memoria (Regla de Oro)
> **"Ninguna base de conocimiento de la IA aislada por identidad"**

*   **Memoria Global:** Todas las identidades acceden a la misma base de conocimiento del usuario (perfil, historial, contexto de negocio).
*   **Filtro de Salida:** La identidad solo procesa esa información para darle forma en la salida. No "aprende" hechos privados que otras identidades desconozcan.
*   **Beneficio:** Garantiza coherencia y evita que el usuario tenga que "reeducar" a Ara para cada identidad.

---

# Modo Colaborador (MVP)

El "Modo Colaborador" es el motor de interacción principal para la creación de valor.

## Flujo de Trabajo
1.  **Conversación Libre:** El usuario conversa con Ara para organizar ideas, definir estrategias o pedir contenido.
2.  **Propuesta Proactiva:** Ara estructura esas ideas en Campañas y Posts potenciales.
3.  **Confirmación Explícita:** Ara **siempre** pide confirmación antes de guardar ("¿Creo esta campaña?").
4.  **Ejecución Inmediata (Backend):**
    *   Al recibir el "Sí", Ara escribe directamente en la base de datos (`campaigns`, `posts`).
    *   El contenido aparece inmediatamente en la UI (listas de posts).
    *   **Importante:** NO publica en redes, NO envía notificaciones externas. Solo deja todo listo ("Pending Review").

---

# Scheduling y Ejecución (MVP)

El sistema de planificación se limita a un modelo de "Ejecución Manual Asistida".

## Capacidades
*   **Planificación Manual:** Asignación de fechas y horas sugeridas a los posts.
*   **Estados de Contenido:**
    *   `DRAFT` / `GENERATED`: Borrador creado por IA.
    *   `READY_MANUAL`: Listo para ser publicado por el usuario.
    *   `PUBLISHED`: Marcado manualmente por el usuario como "Ya publicado" (cierra el ciclo).
    *   `SKIPPED`: Descartado.

## Lo que NO incluye el MVP
*   ❌ Notificaciones por WhatsApp/Email.
*   ❌ Publicación automática (cron jobs conectados a APIs).
*   ❌ Reprogramación inteligente automática.

---

# Fase 2 (Roadmap - Promesa de Valor)

Estas funcionalidades están explícitamente fuera del MVP para garantizar estabilidad, pero son el siguiente paso natural:

1.  **Identidades Operativas:**
    *   Vinculación de cuentas reales (LinkedIn OAuth, Twitter API).
    *   Gestión de tokens y seguridad (Vault).
2.  **Automatización Total:**
    *   "Auto-pilot": Publicación sin intervención humana.
    *   Reprogramación basada en métricas.
3.  **Sistema de Alertas:**
    *   Notificaciones push/email/WhatsApp cuando un post requiere aprobación o se ha publicado.
4.  **Agentes Semi-Autónomos:**
    *   Identidades que proponen contenido proactivamente basado en tendencias (crawler).

---
*Documento actualizado: 2026-01-26 - Alineación Final MVP*
