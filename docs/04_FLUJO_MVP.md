# FLUJO MÍNIMO DE CAMPAÑA (MVP REAL)

## Objetivo
Definir el camino crítico funcional para la creación y ejecución de una campaña en la versión MVP de ARA NeuroPost.

## Diagrama del Flujo

1.  **Input del Usuario (Inicio)**
    *   El usuario define el objetivo de la campaña (ej. "Promocionar webinar").
    *   Ingresa parámetros básicos: Temática, Tono (Profesional, Casual, etc.), Red Social destino.

2.  **Validación Ética Inicial (Guard)**
    *   El sistema evalúa el input contra el Mapa Ético.
    *   *Pasa:* Continúa al paso 3.
    *   *Falla:* Rechaza el input y solicita reformulación (ej. "No se permite contenido de odio").

3.  **Selección de Estrategia y Rol (Wizard)**
    *   El sistema (Arquitecto de Estrategia) propone una estructura de posts.
    *   El usuario confirma o ajusta la cantidad de posts y fechas.

4.  **Generación de Contenido (Generator)**
    *   El sistema genera borradores (título, cuerpo, sugerencia visual) basados en la estrategia.
    *   Se generan múltiples variantes (por defecto 3 en MVP).

5.  **Revisión y Ajuste (Human Loop)**
    *   El usuario visualiza los borradores.
    *   **Acciones:**
        *   *Editar:* Modificar texto o fecha.
        *   *Regenerar:* Solicitar nueva versión.
        *   *Aprobar:* Marcar como listo para publicación.
    *   *Restricción:* No se puede aprobar contenido sin fecha de programación válida.

6.  **Programación y Publicación (Scheduler)**
    *   Los posts aprobados entran en cola.
    *   El Gestor de Publicación ejecuta el envío a la API de la red social (o Mock en desarrollo) en la fecha/hora programada.
    *   Opción de "Publicar Ahora" para ejecución inmediata.

7.  **Feedback Básico (Tracker)**
    *   El sistema confirma el éxito o fallo de la publicación.
    *   Se registra el estado final (Publicado/Fallido) en el dashboard.

---
*Este flujo representa la funcionalidad mínima viable garantizada y no incluye automatizaciones complejas de respuesta o análisis profundo de métricas.*
