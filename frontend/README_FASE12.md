# Frontend Operativo - Ara Auto Publisher (Fase 12.1)

Este es el panel de control humano ("Cockpit") para supervisar y controlar el sistema de publicación autónoma.

## 🚀 Cómo correrlo

1.  Asegúrate de que el Backend esté corriendo en `http://localhost:8000`.
2.  Instala dependencias (si es la primera vez):
    ```bash
    cd frontend
    npm install
    ```
3.  Inicia el servidor de desarrollo:
    ```bash
    npm run dev
    ```
4.  Abre `http://localhost:5173` en tu navegador.

## 🧩 Funcionalidades Clave

### 1. Dashboard Principal (`/`)
*   Muestra el estado global del sistema (AUTONOMOUS / RESTRICTED / OVERRIDE).
*   Métricas en tiempo real de campañas activas vs pausadas.
*   Conteo de intervenciones manuales activas.

### 2. Panel de Control Humano (`/control`)
*   Lista recomendaciones de optimización pendientes (generadas por la IA).
*   Permite **APROBAR** o **RECHAZAR** cada recomendación.
*   Muestra el razonamiento y los valores sugeridos antes de actuar.

### 3. Zona Roja / Overrides (`/overrides`)
*   **Emergency Stop**: Botón de pánico que pausa TODAS las campañas activas.
*   Indicadores visuales claros de peligro.

## ⚠️ Lo que NO hace aún (Fuera de alcance)

*   **Mobile Support**: La interfaz está optimizada para escritorio.
*   **Auth Real**: No hay login screen, se asume acceso local seguro.
*   **Edición Granular**: Para editar detalles de campañas, usa la vista de campañas existente.
*   **Estilos**: El diseño es funcional ("Brutalist utility"), no estético.

## 🔌 Endpoints Utilizados
*   `GET /internal/control/dashboard/stats`
*   `GET /internal/control/recommendations`
*   `POST /internal/control/recommendation/{id}/{action}`
*   `POST /internal/control/emergency-stop`
