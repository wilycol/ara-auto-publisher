# ROADMAP - ETAPA 2 (Post-MVP)

Este documento define el alcance de la Etapa 2 de Ara Auto Publisher, congelado tras el lanzamiento del MVP estable.

## Objetivos
- Ajustes finos de copy y micro-fluidez.
- Pulido de transiciones para usuarios expertos.
- Optimización de cierre de campañas.
- Persistencia de sesiones.

## Tareas Pendientes (Backlog)

### UX/UI & Copy
- [ ] **Micro-fluidez:** Revisar y suavizar los textos de transición entre pasos del asistente.
- [ ] **Transiciones Experto:** Reducir la verbosidad para usuarios que ya conocen el flujo ("Atajos de teclado" mentales).

### Funcionalidad Core
- [ ] **Cierre Automático:** Mejorar la detección de "fin de campaña" para sugerir proactivamente el siguiente paso sin intervención manual.
- [ ] **Persistencia de Sesión:** Implementar recuperación robusta del historial de chat y estado al recargar la página (actualmente validado por sesión en memoria).

### Infraestructura
- [ ] **Protección de Main:** Establecer reglas de protección de rama para evitar commits directos sin PR (Policy).

---
*Documento generado automáticamente al cierre del MVP.*
