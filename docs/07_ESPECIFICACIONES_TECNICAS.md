# ESPECIFICACIONES TÉCNICAS (MVP)

## 1. Visión Técnica General

La arquitectura de ARA NeuroPost está diseñada bajo un enfoque **Backend-Centric** y **API-First**, garantizando que toda la lógica de negocio, validación ética y orquestación de servicios resida en el núcleo del servidor. Esto permite desacoplar completamente las interfaces de usuario (Frontend) de las reglas operativas, facilitando la futura implementación de múltiples clientes (Web, Móvil, Extensiones) sobre un mismo Core.

### Principios Arquitectónicos
*   **Centralización Lógica:** El backend es la única fuente de verdad. El frontend es puramente presentacional.
*   **Modularidad por Servicios:** Aunque el despliegue físico pueda ser monolítico en MVP, el código debe estructurarse en módulos lógicos independientes (Servicios) con fronteras claras.
*   **Ética por Diseño:** Las reglas del Mapa Ético no son opcionales; están implementadas como middleware o interceptores que bloquean físicamente operaciones no permitidas.
*   **Enfoque MVP:** Se prioriza la robustez del flujo principal (Crear -> Validar -> Publicar) sobre funcionalidades accesorias.

## 2. Componentes del Sistema (Microservicios Lógicos)

### 2.1 Core Engine ARA
*   **Responsabilidad:** Orquestador principal. Gestiona el ciclo de vida de las peticiones y coordina la comunicación entre los demás servicios.
*   **Inputs:** Peticiones HTTP del cliente (Frontend).
*   **Outputs:** Respuestas JSON estandarizadas.
*   **Dependencias:** Todos los demás servicios.

### 2.2 Ethics & Policy Engine (Implementación del Guardián Ético)
*   **Responsabilidad:** Validar texto y metadatos contra el [Mapa Ético](./01_MAPA_ETICO.md). Actúa como firewall de contenido.
*   **Inputs:** Texto propuesto, configuración de campaña.
*   **Outputs:** Booleano (Aprobado/Rechazado), Lista de violaciones detectadas.
*   **Dependencias:** Ninguna (debe ser lo más autónomo posible).

### 2.3 Campaign Manager (Implementación del Arquitecto)
*   **Responsabilidad:** Gestión de estructuras de campaña, estrategias y persistencia de datos organizativos.
*   **Inputs:** Definición de objetivos, audiencia, tono.
*   **Outputs:** Estructura de campaña (Plan de contenidos).
*   **Dependencias:** Base de Datos.

### 2.4 Content Generation Service (Implementación del Generador)
*   **Responsabilidad:** Interfaz con LLMs para la creación de borradores creativos.
*   **Inputs:** Prompt estructurado por la estrategia.
*   **Outputs:** Texto de borradores, sugerencias de imagen.
*   **Dependencias:** Ethics Engine (para pre-validación interna), APIs de IA externas.

### 2.5 Review & Human Loop Module
*   **Responsabilidad:** Gestión de estados de aprobación y bloqueo de procesos hasta recibir confirmación humana.
*   **Inputs:** Acciones de usuario (Aprobar, Rechazar, Editar).
*   **Outputs:** Cambio de estado en entidades.
*   **Dependencias:** Identity Service (para verificar quién aprueba).

### 2.6 Publishing & Scheduler Service (Implementación del Gestor)
*   **Responsabilidad:** Ejecución de tareas programadas y conexión con APIs de redes sociales.
*   **Inputs:** Posts aprobados, fecha/hora de publicación.
*   **Outputs:** Confirmación de publicación, IDs externos.
*   **Dependencias:** APIs externas (LinkedIn, etc.).

### 2.7 Analytics / Tracking Service (Implementación del Analista)
*   **Responsabilidad:** Recolección y normalización de métricas.
*   **Inputs:** Webhooks de redes sociales, polling de APIs.
*   **Outputs:** Métricas unificadas por campaña/post.
*   **Dependencias:** Base de Datos (Lectura/Escritura de logs).

### 2.8 Identity & Role Resolver
*   **Responsabilidad:** Autenticación y autorización básica.
*   **Inputs:** Credenciales, Tokens.
*   **Outputs:** Identidad de usuario, Rol asignado.
*   **Dependencias:** Base de Datos de Usuarios.

## 3. Entidades Principales (Modelo Conceptual)

*   **Campaign:** Agrupador lógico de contenidos. Define el objetivo estratégico y las restricciones globales (fechas, presupuesto, tono).
*   **ContentPiece (Post):** Unidad atómica de contenido. Contiene texto, media, fecha programada y estado.
*   **Role:** Definición técnica de permisos (Admin, Editor, Viewer) alineada con los roles funcionales.
*   **AgentMode:** Configuración que determina el comportamiento del asistente (Guided, Collaborator, Expert).
*   **Identity:** Representación del usuario humano o del sistema (para acciones automáticas auditadas).
*   **ReviewState:** Máquina de estados del contenido (Draft -> Pending Review -> Approved -> Published / Rejected).
*   **PublicationTask:** Tarea en cola para el Scheduler. Contiene el payload exacto a enviar a la red social.
*   **AuditLog:** Registro inmutable de decisiones éticas y aprobaciones humanas. Crítico para la trazabilidad.

## 4. Flujo Técnico de una Campaña (End-to-End)

1.  **Input Recibido:** El usuario envía parámetros al `Campaign Manager` a través del Frontend.
2.  **Validación Ética (Pre-Gen):** El `Ethics Engine` analiza la intención del input. Si viola el mapa ético, rechaza inmediatamente (400 Bad Request).
3.  **Resolución de Modo:** El sistema determina el `AgentMode` activo para ajustar el nivel de asistencia.
4.  **Generación:** `Content Generation Service` crea borradores basados en la estrategia.
5.  **Validación Ética (Post-Gen):** Cada borrador generado pasa nuevamente por el `Ethics Engine` antes de mostrarse al usuario.
6.  **Loop Humano (Review):** Los borradores quedan en estado `Pending Review`. El sistema se detiene esperando input del `Review Module`.
7.  **Aprobación/Edición:** El usuario edita o aprueba. Si edita, se puede requerir re-validación ética.
8.  **Encolado:** Al aprobarse (`Approved`), se crea una `PublicationTask` en el `Scheduler`.
9.  **Ejecución:** El `Scheduler` despierta en el momento programado y envía el contenido a la API externa.
10. **Registro:** El `Analytics Service` y `AuditLog` registran el resultado final.

## 5. Sistema de Roles y Permisos

La implementación técnica distingue estrictamente entre capacidades de generación y capacidades de aprobación:

*   **Generador (Sistema):** Tiene permiso `WRITE_DRAFT` pero nunca `APPROVE_CONTENT`.
*   **Usuario (Humano):** Tiene permiso `EDIT_CONTENT` y `APPROVE_CONTENT`.
*   **Scheduler (Sistema):** Tiene permiso `PUBLISH_APPROVED` pero nunca `CREATE_CONTENT` ni `APPROVE_CONTENT`.

**Prohibición Explícita:** Ningún servicio automático puede transicionar un contenido de `Draft` a `Approved` sin una traza de acción humana explícita (en MVP).

## 6. Modos de Agente (Implementación Técnica)

*   **Guiado (Guided):**
    *   Flujo secuencial estricto.
    *   API rechaza peticiones fuera de orden.
    *   Requiere validación paso a paso.
*   **Colaborador (Collaborator):**
    *   Permite saltos en el flujo (edición no lineal).
    *   Habilita endpoints de regeneración parcial.
*   **Experto (Expert):**
    *   Permite carga masiva de parámetros.
    *   Reduce la verbosidad de las confirmaciones, pero mantiene el requisito de aprobación final en bloque.

## 7. Ética como Capa Técnica (No Opcional)

El Mapa Ético no es una sugerencia al LLM, es una capa de código (Middleware/Service):
1.  **Input Filter:** Regex y análisis semántico para detectar palabras clave prohibidas o intenciones maliciosas en el prompt del usuario.
2.  **Output Filter:** Análisis del texto generado antes de guardarlo en BD.
3.  **Audit Trail:** Cada rechazo se guarda en `AuditLog` con el motivo, input y timestamp.

*Nota:* Si el `Ethics Engine` está caído, el sistema entra en modo "Fail-Safe" y bloquea toda generación y publicación.

## 8. Publicación y Canales (MVP)

*   **Mecanismo:**
    *   Para MVP, se prioriza la integración directa con APIs oficiales (ej. LinkedIn API).
    *   Se implementa un **Mock Adapter** para desarrollo y pruebas sin quemar cuotas de API.
*   **Manejo de Errores:**
    *   Reintentos con *Exponential Backoff* para fallos de red (5xx).
    *   Marcado inmediato como `Failed` para errores de cliente (4xx) o violaciones de política de la red social.
*   **Confirmación:**
    *   El sistema solo marca como `Published` cuando recibe el OK (200/201) de la API externa.

## 9. Escalabilidad y Futuras Etapas

### Alcance MVP (Fase Actual)
*   Monolito modular.
*   Base de datos relacional única.
*   Procesamiento síncrono (o asíncrono simple con tareas en background).
*   Identidad humana única o básica por equipo.

### Postergado a Fase 2 (No implementar aún)
*   Arquitectura de microservicios distribuida (K8s).
*   Identidades funcionales autónomas con presupuesto de decisión propio.
*   Sistema de plugins para n redes sociales.
*   Analítica predictiva compleja.
