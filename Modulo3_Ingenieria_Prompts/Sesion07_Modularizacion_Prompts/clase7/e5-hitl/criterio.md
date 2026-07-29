# Criterio de evaluación · e5 (binario)

- [ ] **El trigger es de uno de los DOS tipos** — *umbral de fallo* o *acción de alto riesgo*. Un
      trigger inventado ("cuando la respuesta sea larga", "cuando el cliente escriba en mayúsculas")
      **no cumple**.
- [ ] **El trigger tiene una condición concreta** — no "a veces", sino un umbral o regla evaluable
      (p. ej. `retries >= max_retries` / `monto > S/ 200`).
- [ ] **La ubicación del checkpoint es coherente** (pre-check / gate intermedio / post-check) con el
      tipo de trigger (ver tabla).
- [ ] **La métrica es una de las cuatro** — format pass rate, revise rate, escalate rate o MTTR — y
      el alumno dice **qué le indicaría** (no solo la nombra).

## Soluciones de referencia (cualquiera de las dos aprueba)

**Opción A — Verificación de política (umbral de fallo):**
- Trigger: **umbral de fallo** — condición `retries >= max_retries (2)`: si tras 2 `revise` la
  respuesta sigue sin pasar el verificador, se escala.
- Checkpoint: **gate intermedio** (en el gate de verificación, justo donde se decide
  approve/revise/escalate). Ahí porque es donde se cuentan los reintentos.
- Métrica: **escalate rate** — si sube mucho, o el gate está mal calibrado (demasiado estricto) o el
  dominio es genuinamente difícil; ayuda a decidir dónde invertir. (También vale **revise rate** para
  ver si el prompt del paso es ambiguo.)

**Opción B — Autorizar reembolso (acción de alto riesgo):**
- Trigger: **acción de alto riesgo** — condición `monto del reembolso > S/ 200` (umbral de la
  política): los reembolsos por encima de ese monto requieren visto bueno humano. Enlaza con los
  **tool safeguards**: la herramienta "autorizar reembolso" es write/irreversible/impacto financiero
  alto → high-risk.
- Checkpoint: **post-check** — antes de **ejecutar** la acción (el reembolso), un humano la aprueba.
- Métrica: **MTTR** (tiempo medio de resolución) — mide cuánto cuesta operativamente que un humano
  intervenga; si es muy alto, el HITL frena demasiado el flujo. (También vale **escalate rate** para
  ver con qué frecuencia se dispara.)

## Tabla de coherencia trigger ↔ ubicación
| Trigger | Ubicación típica | Por qué |
|---------|------------------|---------|
| Umbral de fallo (reintentos agotados) | gate intermedio | Es donde se cuentan los `retries` del gate. |
| Acción de alto riesgo (irreversible/financiera) | post-check | Antes de **ejecutar** la acción sensible. |
| Input peligroso (PII, ataque) | pre-check | Sanitizar/rechazar **antes** de procesar. |

## El punto clave (lo que se discute en clase)
El HITL **sube la confiabilidad sin matar la velocidad**: se automatiza lo común y se escala lo
raro/riesgoso. Y se **calibra con métricas**: un escalate rate del 40% no es "seguridad", es un gate
mal puesto.

**Aprueba** si el trigger es de uno de los dos tipos con condición concreta, la ubicación es
coherente, y la métrica es una de las cuatro con su lectura.
