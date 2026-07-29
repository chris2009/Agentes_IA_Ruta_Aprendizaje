# Criterio de evaluación · e3 (binario)

- [ ] **≥ 3 de 4 correctos** según la clave de abajo.
- [ ] **Cada justificación se apoya en "¿secuencia fija de código o el LLM decide el orden?"** — no en
      preferencia, "es más moderno" o "usa herramientas". Una respuesta correcta con justificación
      equivocada (p. ej. "Agent porque es más potente") **no cuenta** como bien justificada.
- [ ] **Justificación de ≤ 2 líneas por caso.**
- [ ] **Línea de cierre** — nombra qué tendría que cambiar para que un Workflow pase a Agent
      (respuesta esperada: que el **LLM** —no el desarrollador— pase a decidir el orden y qué
      herramienta usar en tiempo de ejecución).

## Clave de respuestas (con la razón canónica)
| Caso | Respuesta | Por qué |
|------|-----------|---------|
| **A — Soporte** | **Workflow** | Orden **fijo y conocido** (clasificar→traducir→redactar→verificar); el desarrollador fijó la secuencia. Es el pipeline de la clase. |
| **B — Ventas** | **Workflow** | "Mismos pasos, mismo orden, cada vez." Proceso determinista; camino de código predefinido. |
| **C — Operaciones** | **Agent** | "No se sabe de antemano cuántos pasos ni en qué orden"; el LLM **decide qué revisar después** según lo que encuentra. |
| **D — Due diligence** | **Agent** | "El asistente decide qué fuente consultar y cuándo cerrar"; el orden lo dirige el LLM, no un camino fijo. Es el ejemplo del propio guion. |

## El matiz (lo que se discute en clase)
A y B se ven distintos (uno es texto, otro cálculo) pero **ambos son workflows**: lo que los define es
que **el orden está fijado de antemano**. C y D también se ven distintos, pero **ambos son agents**
porque **el LLM decide el orden en runtime**. La tecnología (usar herramientas, ser texto o cálculo)
no clasifica; **quién dirige el flujo, sí**. Y por la filosofía de Anthropic: si A o B se pueden
resolver con un workflow, **no** conviene "subirlos" a agente — pagarían latencia y coste sin ganar
nada.

**Aprueba** si acierta ≥ 3/4 **y** las justificaciones se apoyan en quién dirige el flujo (orden fijo
vs LLM decide), no en preferencia.
