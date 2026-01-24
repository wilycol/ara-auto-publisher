# ROLES FUNCIONALES (AMPLIADOS Y CONGELADOS)

## Objetivo
Definir las identidades funcionales del sistema ARA NeuroPost. Estos roles describen responsabilidades técnicas y operativas, no personalidades creativas.

## 1. Roles del Sistema

### 1.1 Guardián Ético (Policy Layer)
**Propósito Funcional:** Asegurar que todas las operaciones cumplan con el Mapa Ético y las restricciones de seguridad (Budget Guard, Content Safety).
- **Límites Claros:** Actúa como filtro final bloqueante. No genera contenido, solo lo evalúa.
- **Decisiones Permitidas:** Bloquear generación, rechazar publicación, alertar sobre violaciones de política.
- **Decisiones NO Permitidas:** Modificar el contenido creativamente (solo puede rechazar), aprobar excepciones éticas.

### 1.2 Arquitecto de Estrategia (The Guide)
**Propósito Funcional:** Estructurar la intención comunicacional de la campaña basándose en los inputs del usuario.
- **Límites Claros:** Define el "qué" y el "cómo" a nivel macro, no escribe el copy final.
- **Decisiones Permitidas:** Definir tono, audiencia, pilares temáticos, frecuencia de publicación y canales.
- **Decisiones NO Permitidas:** Escribir el texto final del post, publicar directamente sin generación previa.

### 1.3 Generador de Contenido (The Generator)
**Propósito Funcional:** Producir los activos creativos (texto, sugerencias de imagen) siguiendo las directrices del Arquitecto de Estrategia.
- **Límites Claros:** Su creatividad está acotada por la estrategia definida. No tiene memoria de largo plazo fuera del contexto de la campaña.
- **Decisiones Permitidas:** Redacción de variantes, selección de emojis, estructuración de párrafos, adaptación de longitud por red social.
- **Decisiones NO Permitidas:** Cambiar la estrategia de la campaña, auto-aprobar su propio contenido, violar las directrices del Guardián Ético.

### 1.4 Gestor de Publicación (The Scheduler)
**Propósito Funcional:** Ejecutar la distribución del contenido aprobado en los tiempos y canales definidos.
- **Límites Claros:** Es un ejecutor logístico. No tiene capacidad de juicio sobre el contenido.
- **Decisiones Permitidas:** Conectar con APIs de redes sociales, reintentar en caso de fallo técnico, reportar estado de publicación.
- **Decisiones NO Permitidas:** Modificar el contenido del post, publicar contenido en estado "Borrador" o "Rechazado", alterar la frecuencia más allá de los límites técnicos.

### 1.5 Analista de Impacto (The Tracker)
**Propósito Funcional:** Recopilar y procesar métricas de rendimiento para cerrar el ciclo de feedback.
- **Límites Claros:** Observador pasivo. No interactúa con la audiencia.
- **Decisiones Permitidas:** Agregar datos de likes, shares, comentarios; calcular KPIs básicos.
- **Decisiones NO Permitidas:** Responder comentarios, inferir datos privados de usuarios, modificar datos históricos.

---
*Este documento define la arquitectura funcional de roles y no debe ser modificado sin una revisión estructural del sistema.*
