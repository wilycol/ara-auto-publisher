# Guía de Despliegue - Ara Auto Publisher (Fase 12.2)

Este documento detalla cómo desplegar el sistema en un entorno productivo controlado.

## 🏗️ Arquitectura Final

*   **Backend**: Python/FastAPI (Railway / Render)
*   **Frontend**: React/Vite (Vercel / Netlify)
*   **Base de Datos**: SQLite (En disco persistente de Railway) o PostgreSQL (Recomendado para Prod real)
*   **Comunicación**: REST API protegida por CORS.

## 1️⃣ Backend Deployment (Opción: Railway)

Railway es ideal porque detecta automáticamente el `Procfile` y gestiona variables de entorno fácilmente.

1.  Conecta tu repositorio a Railway.
2.  Configura el servicio para usar el directorio `/backend` como root.
3.  **Variables de Entorno (Obligatorias)**:
    *   `ENVIRONMENT`: `production`
    *   `FRONTEND_URL`: `https://tu-app-frontend.vercel.app` (URL final del frontend)
    *   `AUTONOMY_ENABLED`: `true`
    *   `LINKEDIN_CLIENT_ID`: (Tu credencial real)
    *   `LINKEDIN_CLIENT_SECRET`: (Tu credencial real)
    *   `ENCRYPTION_KEY`: (Tu clave generada)
4.  Deploy.

**Nota sobre Persistencia**: Si usas SQLite en Railway, necesitas un volumen persistente montado en la ruta de la DB, o los datos se perderán en cada deploy. Para producción real, añade un servicio PostgreSQL en Railway y cambia `DATABASE_URL`.

## 2️⃣ Frontend Deployment (Opción: Vercel)

1.  Instala Vercel CLI o conecta tu repo a Vercel Dashboard.
2.  Configura el servicio para usar el directorio `/frontend` como root.
3.  **Build Command**: `npm run build`
4.  **Output Directory**: `dist`
5.  **Variables de Entorno**:
    *   `VITE_API_URL`: `https://tu-app-backend.up.railway.app/api/v1` (URL final del backend)
6.  Deploy.

## 3️⃣ Verificaciones Post-Deploy (Checklist)

Una vez todo esté verde (online), realiza estas pruebas manuales desde tu móvil:

1.  [ ] **Dashboard Load**: Abre la app. ¿Ves los contadores de campañas?
2.  [ ] **Connectivity**: Si sale "Error de red", verifica CORS en backend y `VITE_API_URL` en frontend.
3.  [ ] **Emergency Stop**: Ve a `/overrides`. ¿El botón rojo está habilitado?
4.  [ ] **Logs**: Revisa los logs del backend en Railway. ¿Ves `Health check` exitosos?

## 🚨 Protocolo de Apagado de Emergencia

Si la IA se comporta de forma errática en producción:

1.  **Opción A (Soft Kill)**:
    *   Entra a la Web App -> Zona Roja -> **EMERGENCY STOP**.
    *   Esto pausa todas las campañas en la base de datos.

2.  **Opción B (Hard Kill - Backend)**:
    *   Entra al dashboard de Railway/Render.
    *   Apaga/Suspende el servicio del Backend.
    *   Esto "desenchufa" el cerebro. Nada se publicará.

3.  **Opción C (Nuclear - LinkedIn)**:
    *   Revoca los tokens de la aplicación en developers.linkedin.com.

## ⚠️ Riesgos Conocidos

*   **Persistencia SQLite**: Si no configuras volumen, reiniciar el backend borra la historia. **SOLUCIÓN**: Usar PostgreSQL.
*   **CORS Estricto**: Si `FRONTEND_URL` no coincide exactamente (slash final, https), fallará.
*   **Timeouts**: El proceso de generación de contenido puede tardar >30s. Configura timeouts altos en el servidor.
