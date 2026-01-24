# Ara Neuro Post - Frontend Handoff

> Este documento detalla la especificación para la construcción del Frontend.

## 1. Stack Tecnológico (Recomendado)
*   **Framework**: React (Vite)
*   **Lenguaje**: TypeScript
*   **UI Library**: Tailwind CSS + Shadcn/UI (opcional)
*   **Estado**: React Query (TanStack Query) para gestión de datos de servidor.

## 2. Conexión con Backend
*   **Base URL**: `http://localhost:8000/api/v1`
*   **Documentación API**: `http://localhost:8000/docs` (Swagger UI)

## 3. Pantallas Requeridas

### A. Dashboard Principal
*   Resumen de Jobs activos.
*   Lista de últimos posts generados.
*   Botón para "Ejecutar Ahora" (Run Job).

### B. Gestión de Posts
*   Tabla/Lista de posts.
*   Filtros por estado: `generated`, `published`, `failed`.
*   **Acción Clave**: Editar Post (Título, Contenido) -> Guardar.
*   **Acción Clave**: Aprobar/Publicar Post.

### C. Configuración (Jobs & Topics)
*   Crear/Editar Proyectos.
*   Crear/Editar Temas (Topics) y sus pesos.
*   Configurar Jobs (frecuencia, horarios).

## 4. Flujo de Datos Crítico
1.  Frontend solicita `GET /posts`.
2.  Usuario revisa un post `GENERATED`.
3.  Usuario edita si es necesario.
4.  Usuario da click en "Aprobar".
5.  Frontend envía `PUT /posts/{id}` (Futuro).

## 5. Notas de Seguridad
*   El backend tiene CORS habilitado para `*` (dev mode).
*   No hay autenticación implementada aún (Fase 1).

---
**Estado del Backend**: Congelado ❄️. Listo para integración.
