# 👔 Guía de Configuración de LinkedIn Developer

Esta guía te explica paso a paso cómo obtener las credenciales de LinkedIn (`Client ID` y `Client Secret`) necesarias para que **Ara Auto Publisher** pueda publicar contenido automáticamente y permitir inicio de sesión.

---

## 1. Crear una App en LinkedIn Developers

1.  Ve al portal de [LinkedIn Developers](https://www.linkedin.com/developers/apps).
2.  Inicia sesión con tu cuenta de LinkedIn.
3.  Haz clic en el botón azul **"Create app"**.
4.  Completa el formulario:
    *   **App name**: `Ara Auto Publisher` (o el nombre que prefieras).
    *   **LinkedIn Page**: Debes asociar una página de empresa de LinkedIn. Si no tienes una, tendrás que crearla primero.
    *   **Privacy policy URL**: Puedes poner una URL temporal si no tienes (ej. `https://tu-dominio.com/privacy`).
    *   **App logo**: Sube una imagen (obligatorio).
5.  Acepta los términos y haz clic en **"Create app"**.

## 2. Solicitar Permisos (Products)

Una vez creada la app, necesitas pedir acceso a las funcionalidades:

1.  Ve a la pestaña **"Products"**.
2.  Busca y solicita ("Request access") para:
    *   **Sign In with LinkedIn using OpenID Connect**: Para que los usuarios puedan iniciar sesión.
    *   **Share on LinkedIn**: Para poder publicar contenido.
    *   *(Opcional)* **Advertising API**: Si planeas funciones de anuncios en el futuro.
3.  Estos permisos suelen aprobarse automáticamente de inmediato.

## 3. Obtener Credenciales (Client ID y Secret)

1.  Ve a la pestaña **"Auth"**.
2.  Allí verás:
    *   **Client ID**: Una cadena de texto (ej. `77xyz...`).
    *   **Client Secret**: Una cadena oculta. Haz clic en el ojo para verla.
3.  **¡IMPORTANTE!** Copia estos valores, los necesitarás para tus variables de entorno.

## 4. Configurar Redirect URLs

En la misma pestaña **"Auth"**, baja a la sección **"OAuth 2.0 settings"**.

1.  En **Authorized redirect URLs for your app**, debes añadir las URLs de callback de tu backend.
2.  Añade las siguientes URLs (una por línea):

    *   **Para Desarrollo Local:**
        ```
        http://localhost:8000/api/v1/auth/linkedin/callback
        ```

    *   **Para Producción (Render):**
        ```
        https://ara-auto-publisher.onrender.com/api/v1/auth/linkedin/callback
        ```
        *(Asegúrate de que este dominio coincida exactamente con tu URL de Render).*

## 5. Configurar Variables de Entorno

Ahora, lleva estos valores a tus archivos `.env` y al panel de Render.

### En tu archivo local `backend/.env`:

```ini
LINKEDIN_CLIENT_ID=tu_client_id_real
LINKEDIN_CLIENT_SECRET=tu_client_secret_real
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/v1/auth/linkedin/callback
```

### En Render (Environment Variables):

1.  Ve a tu Dashboard de Render -> Tu servicio Backend -> **Environment**.
2.  Añade/Edita las variables:
    *   `LINKEDIN_CLIENT_ID`: `tu_client_id_real`
    *   `LINKEDIN_CLIENT_SECRET`: `tu_client_secret_real`
    *   `LINKEDIN_REDIRECT_URI`: `https://ara-auto-publisher.onrender.com/api/v1/auth/linkedin/callback`
    *   *(Nota: La URI en Render DEBE ser la de producción, no localhost)*

---

## ⚠️ ¿Solo quieres probar sin conectar LinkedIn real?

Si solo quieres que el backend arranque para probar otras cosas (crear posts manuales, ver el dashboard) y **NO** necesitas publicar en LinkedIn todavía, puedes usar valores "dummy" (falsos) para engañar a la validación de seguridad:

*   **LINKEDIN_CLIENT_ID**: `dummy_client_id`
*   **LINKEDIN_CLIENT_SECRET**: `dummy_client_secret`
*   **LINKEDIN_REDIRECT_URI**: `http://localhost:8000/callback`

El backend funcionará, pero si intentas hacer login con LinkedIn o publicar, dará error.
