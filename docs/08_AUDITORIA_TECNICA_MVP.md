# AUDITORÍA TÉCNICA DEL BACKEND (MVP LOCAL)

## 1. API Contracts Actuales

A continuación se detallan los contratos de los endpoints principales implementados en el MVP actual.

### Módulo: Auth (`/api/v1/auth`)
*   **GET /linkedin/login**
    *   **Propósito:** Iniciar flujo OAuth con LinkedIn.
    *   **Input:** `project_id` (Query param, default=1).
    *   **Output:** `{"url": "https://www.linkedin.com/..."}`.
    *   **Dependencia:** Requiere `LINKEDIN_CLIENT_ID` en .env.
*   **GET /linkedin/callback**
    *   **Propósito:** Recibir código de autorización, intercambiar por token y crear/actualizar `ConnectedAccount`.
    *   **Input:** `code`, `state` (Query params).
    *   **Output:** Redirección al Frontend (`/connections`).
    *   **Nota:** Maneja encriptación de tokens antes de guardar.
*   **GET /accounts**
    *   **Propósito:** Listar cuentas conectadas activas.
    *   **Output:** Lista de `ConnectedAccountResponse`.
*   **DELETE /accounts/{account_id}**
    *   **Propósito:** Desconexión lógica (Soft Delete) de una cuenta.
    *   **Output:** `true`.

### Módulo: Campaigns (`/api/v1/campaigns`)
*   **GET /**
    *   **Propósito:** Listar campañas de un proyecto.
    *   **Input:** `project_id` (Query param).
    *   **Output:** Lista de `CampaignRead`.
*   **POST /**
    *   **Propósito:** Crear nueva campaña.
    *   **Input:** `CampaignCreate` (name, objective, tone, etc.).
    *   **Output:** `CampaignRead` (Objeto creado).
*   **POST /{campaign_id}/generate**
    *   **Propósito:** Trigger de IA para generar borradores.
    *   **Input:** `{"count": 3, "platform": "linkedin"}`.
    *   **Output:** `{"status": "success", "generated_count": n}`.
    *   **Efecto:** Crea registros en tabla `posts` con estado `PENDING`.

### Módulo: Posts (`/api/v1/posts`)
*   **GET /**
    *   **Propósito:** Listar posts con filtros.
    *   **Input:** `project_id`, `status`, `limit` (Query params).
    *   **Output:** Lista de `PostRead`.
*   **PUT /{post_id}**
    *   **Propósito:** Editar contenido o aprobar post.
    *   **Input:** `PostUpdate` (title, content, status, scheduled_for).
    *   **Regla de Negocio:**
        *   Bloquea edición de contenido si `status` ya es `APPROVED`.
        *   Exige `scheduled_for` para pasar a `APPROVED`.
*   **POST /{post_id}/publish**
    *   **Propósito:** Publicación inmediata (Bypass scheduler).
    *   **Input:** Ninguno (usa ID de URL).
    *   **Output:** Post actualizado con estado `PUBLISHED`.
    *   **Dependencia:** Usa `LinkedInPublisher` (Mock o Real según config).

### Módulo: Guide (`/api/v1/guide`)
*   **POST /next**
    *   **Propósito:** Motor conversacional del Wizard.
    *   **Input:** Estado actual de la conversación y respuesta del usuario.
    *   **Output:** Siguiente paso y opciones sugeridas.

## 2. Flujo Backend → Database

### Modelo de Datos (SQLAlchemy)
*   **Tablas Principales:**
    *   `projects`: Entidad raíz.
    *   `connected_accounts`: Credenciales OAuth encriptadas.
    *   `campaigns`: Agrupador lógico.
    *   `posts`: Unidad de contenido central.
    *   `topics`: Temáticas y keywords.
*   **Operaciones:**
    *   **Write:** Creación de campañas, guardado de tokens OAuth, inserción masiva de posts generados por IA (`db.add_all`).
    *   **Update:** Edición de posts (con validación de estado), Soft-delete de cuentas (`active = False`).
    *   **Read:** Consultas filtradas por `project_id` o `campaign_id`.

### Motor de Base de Datos
*   **Actual:** SQLite (`sqlite:///./ara_neuro_post.db`).
*   **ORM:** SQLAlchemy con sesiones síncronas (`Session = Depends(get_db)`).

## 3. Suposiciones Implícitas del MVP

1.  **Monousuario / "Single Team":** Aunque existe la tabla `projects`, no hay un sistema de login para usuarios del dashboard (email/pass). Se asume que quien accede a la API tiene permiso total sobre los recursos.
2.  **Entorno Local:**
    *   Uso de SQLite (archivo en disco).
    *   Validación de seguridad (`validate_security_config`) que detiene el servidor si faltan variables, asumiendo control total sobre el entorno de despliegue.
3.  **Persistencia de Estado en Memoria:**
    *   El `SchedulerService` se inicia como un proceso en segundo plano dentro de la misma instancia de FastAPI (`lifespan`). Esto asume que el servidor es persistente (VPS/Local) y no efímero (Serverless).
4.  **Mock por Defecto:**
    *   Si no hay cuenta de LinkedIn conectada, el endpoint de publicación crea una cuenta "Mock" al vuelo para no fallar en demos.

## 4. Qué NO está implementado aún

1.  **Autenticación de Usuario del Dashboard:**
    *   No hay endpoints `/login`, `/register` o middleware JWT para proteger las rutas de la API. Actualmente, cualquiera con acceso a la red puede invocar los endpoints.
2.  **Gestión de Medios Real (S3/CDN):**
    *   La tabla `media` existe, pero no hay endpoints para subir imágenes (`upload`) ni integración con AWS S3/Cloudinary. Se asume texto puro o URLs externas por ahora.
3.  **Roles y Permisos (RBAC):**
    *   No hay distinción entre "Editor", "Aprobador" o "Admin".
4.  **Manejo de Errores de API Externa Robusto:**
    *   El manejo de tokens expirados (Refresh Token flow) está parcialmente estructurado en el modelo de datos pero no plenamente visible en la lógica de publicación automática.
5.  **Webhooks Reales:**
    *   No hay endpoints para recibir notificaciones de LinkedIn (ej. comentarios, métricas).

## 5. Riesgos al migrar a Supabase + Render + Vercel

### Riesgos Críticos (Romperán la app)
1.  **Scheduler en Vercel:**
    *   **Riesgo:** Vercel (Frontend/Serverless Functions) congela o mata los procesos después de responder. El `SchedulerService` que corre en el `lifespan` de FastAPI **NO funcionará** en Vercel.
    *   **Solución:** Mover el scheduler a un servicio externo (Cron Job de Render/Supabase o GitHub Actions) que llame a un endpoint de la API.
2.  **SQLite en la Nube:**
    *   **Riesgo:** SQLite es un archivo. En Render/Vercel, el sistema de archivos es efímero. Los datos se perderán en cada despliegue.
    *   **Solución:** Migrar obligatoriamente a PostgreSQL (Supabase). Requiere cambiar la URL de conexión y verificar tipos de datos incompatibles (generalmente SQLAlchemy abstrae bien esto, pero hay que validar migraciones).
3.  **Almacenamiento de Archivos:**
    *   **Riesgo:** Si se implementa subida de imágenes localmente, se perderán.
    *   **Solución:** Usar Supabase Storage o AWS S3 desde el día 1.

### Adaptaciones Necesarias
1.  **Variables de Entorno:**
    *   La validación estricta en `main.py` (`sys.exit(1)`) hará fallar el despliegue si no se configuran TODAS las variables (LinkedIn, Encryption Key) en el panel de control de Render/Vercel.
2.  **CORS:**
    *   La configuración de CORS en `main.py` tiene orígenes hardcodeados (`localhost`). Debe actualizarse para aceptar el dominio de producción del Frontend.
