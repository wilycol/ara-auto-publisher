# Checklist de Producción (ARA NeuroPost MVP)

Este documento detalla los requisitos previos y pasos críticos para promover el MVP desde el entorno DEV hacia MAIN (Producción).

## 1. Variables de Entorno Requeridas (MAIN)

Estas variables deben configurarse en el entorno de producción (ej. Render Dashboard) antes del deploy.

| Variable | Descripción | Ejemplo / Notas |
|----------|-------------|-----------------|
| `DATABASE_URL` | String de conexión a Supabase MAIN (Transaction Pooler) | `postgresql://postgres.[ref]:[pass]@aws-0-us-east-1.pooler.supabase.com:6543/postgres` |
| `SUPABASE_URL` | URL del proyecto Supabase MAIN | `https://[ref].supabase.co` |
| `SUPABASE_KEY` | Anon Key (pública) de Supabase MAIN | `eyJ...` |
| `SUPABASE_JWT_SECRET` | Secret para validar tokens JWT | Obtener de: Project Settings -> API -> JWT Secret |
| `AI_API_KEY` | Key real de OpenAI o DeepSeek | `sk-...` |
| `AI_PROVIDER` | Proveedor de IA | `openai` o `deepseek` |
| `LINKEDIN_CLIENT_ID` | Client ID de App LinkedIn Producción | |
| `LINKEDIN_CLIENT_SECRET` | Client Secret de App LinkedIn Producción | |
| `LINKEDIN_REDIRECT_URI` | Callback URL de Producción | `https://[api-domain]/api/v1/auth/linkedin/callback` |
| `ENCRYPTION_KEY` | Key Fernet generada nueva para Prod | Generar con `cryptography.fernet.Fernet.generate_key()` |
| `ENVIRONMENT` | Flag de entorno | `production` |

## 2. Replicación de Esquema en Supabase MAIN

El esquema de base de datos debe ser idéntico al de DEV.

1.  Ir al **SQL Editor** del proyecto Supabase MAIN.
2.  Copiar el contenido de `docs/10_SUPABASE_SCHEMA.sql`.
3.  Ejecutar el script completo.
4.  **Verificación**:
    *   Confirmar que las tablas `projects`, `campaigns`, `posts`, `connected_accounts` existen.
    *   Confirmar que las políticas RLS están activas (candado verde en dashboard).

## 3. Configuración de Auth (Supabase)

1.  En **Authentication -> Providers**, habilitar **Email**.
2.  Deshabilitar "Confirm email" si se desea acceso inmediato para primeros usuarios (o configurar SMTP).
3.  En **URL Configuration**, añadir la URL del Frontend de Producción (Vercel) en "Site URL" y "Redirect URLs".

## 4. Riesgos Conocidos y Mitigación

*   **Migración de Datos**: Este MVP no contempla migración automática de datos desde SQLite local. Se asume "Clean Slate" (base de datos limpia) en Producción.
*   **Rate Limits**: La API de LinkedIn tiene límites estrictos. Monitorear logs de `429 Too Many Requests`.
*   **Costos IA**: Sin sistema de cuotas por usuario implementado en MVP. Riesgo de sobrecosto si se abusa. *Mitigación: Monitoreo manual de dashboard OpenAI.*

## 5. Procedimiento de Rollback

Si el deploy falla:
1.  En Vercel: Revertir al "Previous Deployment" instantáneamente.
2.  En Render: Usar "Rollback" en el dashboard.
3.  Base de Datos: Si el esquema está corrupto, usar `drop schema public cascade; create schema public;` (¡Destructivo!) y re-ejecutar el script SQL v1.0.

---
**Estado Actual**: Listo para deploy a DEV.
**Siguiente Paso**: Validar en DEV antes de tocar MAIN.
