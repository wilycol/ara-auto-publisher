# Ara Neuro Post

## Visión General
Ara Neuro Post es una plataforma de marketing automatizado impulsada por Inteligencia Artificial Nativa. Su objetivo es generar, gestionar y publicar contenido en redes sociales de manera autónoma pero supervisada.

## Arquitectura
El sistema sigue una arquitectura de **Multiservicios** desacoplada para garantizar escalabilidad y mantenibilidad.

### 1. Frontend (La Cara)
- **Tecnología**: React + Vite (Propuesta).
- **Responsabilidad**: Interfaz de usuario para dar indicaciones, revisar borradores y confirmar publicaciones. Totalmente independiente del backend.

### 2. Backend (El Cerebro Operativo)
- **Tecnología**: Python (FastAPI) o Node.js.
- **Responsabilidad**: 
  - Orquestación de servicios.
  - Gestión de usuarios y autenticación.
  - Conexión con APIs de Redes Sociales (Dispatcher).
  - Gestión de Base de Datos.

### 3. AI Engine / Conector (La Creatividad)
- **Tecnología**: Cliente compatible con OpenAI API / DeepSeek (Self-hosted).
- **Responsabilidad**: 
  - Generación de texto (Copywriting).
  - Generación de prompts para imágenes.
  - Conexión con servidor de IA público/privado (DeepSeek).

### 4. Persistencia y Storage
- **Base de Datos**: Relacional (PostgreSQL/SQLite) para historial de URLs, usuarios y logs.
- **Storage**: Sistema de archivos o S3-compatible para guardar imágenes/videos generados.

## Seguridad (Jack-SafeRefactor Protocol)
- **Confirmación Obligatoria**: Ninguna publicación sale a producción sin "OK" humano.
- **Trazabilidad**: Registro de todas las acciones de la IA.
- **Datos**: Manejo seguro de credenciales y tokens.
