# MODOS DE AGENTE ARA (CONGELADOS)

## Objetivo
Definir los modos de operación de ARA, estableciendo el nivel de autonomía e interacción con el usuario. Estos modos determinan el flujo de trabajo, no el "estado de ánimo" del sistema.

## 1. Modos Definidos

### 1.1 Modo Guiado (Guided)
**Condición de Operación:** Diseñado para nuevos usuarios o campañas donde la estrategia no está clara.
**Alcance Funcional:**
- El sistema lleva la iniciativa mediante preguntas paso a paso (Wizard).
- Requiere confirmación en cada etapa crítica (Estrategia -> Generación -> Aprobación).
- La generación es conservadora y estrictamente apegada a las respuestas del usuario.
**Restricciones:** No permite saltar pasos de validación. La autonomía de publicación es nula (siempre requiere aprobación manual).
**Uso:** Onboarding, definición de nuevas líneas editoriales.

### 1.2 Modo Colaborador (Collaborator)
**Condición de Operación:** Diseñado para trabajo conjunto en tiempo real entre usuario y sistema.
**Alcance Funcional:**
- El usuario y ARA co-crean. El usuario puede editar directamente los borradores y ARA sugiere mejoras.
- Ciclos de iteración rápidos (Generar -> Editar -> Regenerar).
- Permite ajustes finos de tono y contenido antes de la programación.
**Restricciones:** Requiere intervención humana activa. No es apto para "set and forget".
**Uso:** Refinamiento de copy, campañas de alta sensibilidad, gestión diaria de contenido.

### 1.3 Modo Experto (Expert / Autonomous)
**Condición de Operación:** Diseñado para usuarios avanzados con estrategias validadas y confianza en el sistema.
**Alcance Funcional:**
- El usuario define objetivos de alto nivel y restricciones (presupuesto, frecuencia).
- ARA asume la responsabilidad de la generación y programación con mínima supervisión.
- Puede operar bajo lógica de "aprobación por silencio" o "publicación directa" si las políticas lo permiten.
**Restricciones:** Estrictamente vigilado por el Rol de Guardián Ético. Requiere historial previo de campañas exitosas (en versiones futuras, para MVP requiere configuración explícita).
**Uso:** Mantenimiento de presencia digital, contenido Evergreen, escalado de campañas validadas.

---
*No se agregarán nuevos modos operativos en la fase MVP.*
