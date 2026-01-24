# Guía de Deploy y Ejecución (MVP - Fase Final)

Sigue estos pasos estrictos para desplegar el entorno DEV y validarlo.

## 1. Configuración de Supabase (DEV)

Como Jack (AI) no tiene permisos para crear proyectos, debes realizar esto manualmente:

1.  Crea un nuevo proyecto en [Supabase](https://supabase.com) llamado `ara-neuropost-dev`.
2.  Ve al **SQL Editor** y ejecuta el contenido del archivo:
    *   `docs/10_SUPABASE_SCHEMA.sql`
3.  Ve a **Project Settings -> API** y copia:
    *   Project URL
    *   anon public key
    *   JWT Secret (¡Importante!)
4.  Ve a **Project Settings -> Database -> Connection String** y copia la URI (usa la opción "Transaction Pooler" puerto 6543 si es posible, o Session puerto 5432). Recuerda tu contraseña de DB.

## 2. Configuración Local (Para Pruebas)

Edita el archivo `backend/.env` con las credenciales de Supabase DEV que acabas de obtener:

```ini
DATABASE_URL=postgresql://postgres.[ref]:[pass]@...:6543/postgres
SUPABASE_URL=https://[ref].supabase.co
SUPABASE_KEY=[anon-key]
SUPABASE_JWT_SECRET=[jwt-secret]
```

## 3. Seeding de Datos (DEV)

Para poblar la base de datos con datos de prueba seguros:

1.  Crea un usuario en Supabase Auth (Authentication -> Users -> Add User).
2.  Copia su `User UID`.
3.  Ejecuta el script de seed desde la terminal (en carpeta raíz):

```powershell
# Windows PowerShell
$env:SEED_USER_ID="pega-tu-uuid-aqui"
python backend/scripts/seed_dev_data.py
```

Si ves `✅ [SEED DEV] Completed successfully`, la base de datos y la conexión funcionan.

## 4. Deploy Backend (Render)

1.  Crea un **Web Service** en Render conectado a tu repo.
2.  **Runtime**: Python 3.
3.  **Build Command**: `pip install -r backend/requirements.txt`.
4.  **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5.  **Environment Variables**: Copia todas las variables de tu `.env` (incluyendo las de Supabase).

## 5. Deploy Frontend (Vercel)

1.  Importa el proyecto en Vercel.
2.  **Build Settings**:
    *   Framework Preset: Vite
    *   Root Directory: `frontend`
3.  **Environment Variables**:
    *   `VITE_API_URL`: La URL de tu backend en Render (ej: `https://ara-backend-dev.onrender.com/api/v1`)
    *   `VITE_SUPABASE_URL`: Tu URL de Supabase.
    *   `VITE_SUPABASE_ANON_KEY`: Tu Anon Key.

## 6. Validación Final

1.  Abre la URL del Frontend.
2.  Loguéate (o regístrate si implementaste el flow de UI, o usa el usuario creado manualmente).
3.  Verifica que veas el "Project" y "Campaign" creados por el seed.

---
**¿Problemas?** Revisa `docs/11_CHECKLIST_PRODUCCION.md` para riesgos conocidos.
