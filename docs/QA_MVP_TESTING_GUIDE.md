# Guía de Pruebas QA - MVP Ara Auto Publisher

**Versión:** MVP 1.0 (Ready for Pilot)  
**Fecha:** 26 Enero 2026  
**Objetivo:** Validar que el MVP cumple estrictamente con la promesa de valor: "Estrategia asistida y ejecución manual segura", sin funcionalidades operativas ocultas ni riesgos de seguridad.

---

## 1. Cobertura Mínima Obligatoria
Antes de aprobar el piloto, se deben validar estos 5 pilares:
1.  ✅ **Identidades Funcionales:** Persistencia y uso correcto de `communication_style` y `content_limits`.
2.  ✅ **Chat Colaborativo:** Flujo de conversación libre → Confirmación explícita (`confirm_create`).
3.  ✅ **Creación Real:** La base de datos refleja las campañas y posts creados desde el chat.
4.  ✅ **Ciclo de Vida del Post:** Transición correcta: `GENERATED` → `READY_MANUAL` → `PUBLISHED`.
5.  ✅ **Seguridad:** Ausencia total de credenciales externas (OAuth/Passwords) en el flujo.

---

## 2. Casos de Prueba (Test Cases)

### Bloque A: Identidades Funcionales (Estratégicas)

| ID | Título | Pasos | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC-001** | **Creación de Identidad MVP PRO** | 1. Ir a "Identidades" -> "Nueva Identidad".<br>2. Completar chat definiendo: Nombre, Propósito, Tono, Plataformas, **Estilo** y **Límites**.<br>3. Confirmar creación. | La identidad se guarda con todos los campos. En la DB, `communication_style` y `content_limits` no son nulos. |
| **TC-002** | **Visualización de Detalles** | 1. Abrir lista de Identidades.<br>2. Clic en botón "Ver" de la identidad creada en TC-001. | Se abre un modal de solo lectura. Se muestran claramente las secciones **"Estilo"** y **"Límites (Lo que NO hace)"**. |
| **TC-003** | **Edición vía Chat** | 1. Clic en "Editar" en una identidad existente.<br>2. Cambiar solo el "Tono" a través del chat.<br>3. Confirmar cambios. | El chat reconoce la identidad previa. Al finalizar, solo el tono se actualiza; el resto de campos (incluyendo límites) se mantienen. |
| **TC-004** | **Memoria Compartida (Perfil)** | 1. Asegurar que el perfil de usuario tiene "Profesión: Arquitecto".<br>2. Crear nueva identidad "Divulgador".<br>3. Preguntar a la identidad: "¿A qué me dedico?". | La identidad responde "Eres Arquitecto" (o similar), confirmando acceso a la memoria base del usuario. |

### Bloque B: Chat Colaborativo y Creación

| ID | Título | Pasos | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC-005** | **Propuesta sin Creación** | 1. En Ara Post Manager, pedir: "Dame 3 ideas para LinkedIn".<br>2. Esperar respuesta.<br>3. **NO** confirmar creación. | La IA da las ideas en el chat. **NO** se crea nada en la pestaña "Campañas" ni en la DB. |
| **TC-006** | **Inyección de Identidad** | 1. Seleccionar Identidad con límite "No usar emojis".<br>2. Pedir crear una campaña.<br>3. Revisar el contenido generado en el chat. | El texto generado **NO** contiene emojis, respetando el campo `content_limits`. |
| **TC-007** | **Confirmación y Creación Real** | 1. En el flujo anterior, hacer clic en botón "Sí, crear campaña".<br>2. Esperar confirmación del chat ("He creado la campaña...").<br>3. Ir a pestaña "Campañas". | Aparece la nueva campaña con el nombre correcto. Al entrar, existe al menos 1 post en estado `GENERATED` o `DRAFT`. |

### Bloque C: Modo Manual Asistido

| ID | Título | Pasos | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC-008** | **Visualización de Post Generado** | 1. Entrar al detalle de la campaña creada en TC-007.<br>2. Localizar el post generado. | El post muestra el contenido, hashtags y estado (color gris/azul). Botón "Ya lo publiqué" visible. |
| **TC-009** | **Exportación Manual** | 1. Hacer clic en botón "Copiar" o "Exportar".<br>2. Pegar en un bloc de notas. | El texto pegado incluye título, cuerpo y hashtags, listo para usar. |
| **TC-010** | **Cierre de Ciclo (Publicación)** | 1. Hacer clic en el botón **"Ya lo publiqué"** (Check icon).<br>2. Confirmar si pide confirmación (opcional). | El estado del post cambia a **PUBLISHED** (verde). La fecha de publicación se registra como "Ahora". |

### Bloque D: Seguridad y Límites

| ID | Título | Pasos | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC-011** | **Verificación de Credenciales** | 1. Revisar configuración de Identidad.<br>2. Revisar configuración de Usuario.<br>3. Intentar encontrar campos de "Password", "Token" o "OAuth". | **No existen** campos ni formularios para ingresar credenciales de redes sociales. |
| **TC-012** | **Intento de Publicación Auto** | 1. (Prueba de Caja Blanca) Revisar logs al marcar "Ya lo publiqué". | El sistema solo actualiza la DB local. **No** hay intentos de conexión saliente a APIs de LinkedIn/Twitter. |

---

## 3. Plantilla de Reporte de QA

**Fecha de Ejecución:** _______________  
**Tester:** _______________  

### Resumen Ejecutivo
| Métrica | Valor |
| :--- | :--- |
| Total Casos Ejecutados | / 12 |
| Casos Exitosos (Pass) | |
| Casos Fallidos (Fail) | |
| Bloqueantes para Piloto | (Sí/No) |

### Detalle de Fallos (Si existen)
| ID Caso | Descripción del Error | Severidad (Alta/Media/Baja) | Comentarios |
| :--- | :--- | :--- | :--- |
| | | | |

### Evaluación de Riesgos
*   [ ] **Riesgo de Confusión:** ¿El usuario entiende que "Ya lo publiqué" es manual?
*   [ ] **Riesgo de Datos:** ¿Se mezclan identidades incorrectamente?
*   [ ] **Riesgo Técnico:** ¿Errores 500 en flujos normales?

### Recomendación Final
*   [ ] **APROBADO PARA PILOTO** (El MVP cumple su promesa funcional y de seguridad).
*   [ ] **APROBADO CON OBSERVACIONES** (Errores menores cosméticos, funcionalidad core intacta).
*   [ ] **NO APROBADO** (Fallo en creación, persistencia o seguridad).

---

> **Nota para el Tester:** Este MVP es una herramienta de **productividad**, no de automatización. Si el software ayuda al usuario a escribir y organizar, pero le obliga a copiar-pegar, **es un comportamiento correcto y esperado**. Cualquier intento de automatización oculta debe reportarse como bug.
