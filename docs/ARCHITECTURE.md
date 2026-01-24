# Ara Neuro Post - Documentación de Arquitectura

## Estructura de Microservicios

El sistema se compone de los siguientes módulos independientes:

### 1. Backend Core (`/backend`)
- **Responsabilidad**: Orquestador central. No genera contenido, lo solicita. Gestiona reglas de negocio, base de datos y programación de tareas.
- **Stack**: Python, FastAPI, SQLAlchemy.
- **Base de Datos**: Relacional (SQLite dev / PostgreSQL prod).
- **Modelos Principales**:
  - `Project`: Multitenancy lógico.
  - `Topic`: Temas de interés.
  - `Post`: Unidad de contenido.
  - `AutoPublisherJob`: Reglas de frecuencia.

### 2. AI Engine (`/ai_engine`)
- **Responsabilidad**: Interfaz pura de generación. Recibe prompts, devuelve texto/imágenes.
- **Conectividad**: Compatible con OpenAI API (para conectar con DeepSeek self-hosted).
- **Estado**: Stateless (No guarda nada, solo procesa).

### 3. Storage Service (Integrado en Backend por ahora)
- **Responsabilidad**: Abstracción del sistema de archivos.
- **Interface**: `save_media(file)`, `get_media_url(id)`.
- **Implementación**: Filesystem local (`/media`) escalable a S3.

### 4. Frontend (`/frontend`)
- **Responsabilidad**: UI para humanos.
- **Comunicación**: Solo habla con Backend Core API.

## Flujo de Datos (Auto Publisher)
1. `AutoPublisherJob` se despierta (cron/schedule).
2. Verifica si se alcanzó la cuota diaria (`posts_per_day`).
3. Selecciona un `Topic` basado en pesos (`weight`).
4. Recopila `EditorialRule`s del proyecto.
5. Envía solicitud a `AI Engine`: "Genera post sobre [Topic] con reglas [Rules]".
6. Recibe borrador.
7. Guarda `Post` en BD con estado `DRAFT` o `GENERATED`.
8. (Opcional) Notifica al humano para revisión.
