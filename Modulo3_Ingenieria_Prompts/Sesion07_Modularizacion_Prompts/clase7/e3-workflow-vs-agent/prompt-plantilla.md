# Prompt-plantilla · e3 — Workflow vs Agent (¿quién dirige el flujo?)

> El objetivo es afinar el criterio de Anthropic (2024): **un workflow tiene un camino de código
> predefinido; un agent deja que el LLM dirija el flujo dinámicamente.** Clasifica cada caso por
> **quién decide el orden**, no por preferencia. Pega `casos.md` donde dice `<<<...>>>`. Puedes
> resolverlo a mano o usar esta plantilla en un chat para contrastar tu respuesta.

---

```
Eres un instructor de diseño de sistemas con LLMs. Clasifica cada caso como WORKFLOW o AGENT según
UN solo criterio (Anthropic, "Building Effective Agents", 2024):

  - WORKFLOW: la secuencia de pasos está fijada de antemano por un camino de CÓDIGO PREDEFINIDO; el
    LLM ejecuta cada paso pero NO elige el orden ni qué herramienta usar. Predecible, fácil de testear.
  - AGENT: el LLM DIRIGE dinámicamente el proceso: decide qué hacer a continuación, qué herramienta
    usar y cuándo terminar. El número de pasos no se conoce de antemano.

Pregunta guía: ¿hay una secuencia fija de pasos (código) o el LLM decide el orden en tiempo de
ejecución?

Casos:
<<<
{pega aquí el contenido de casos.md}
>>>

Devuelve EXACTAMENTE este formato, sin texto extra:

- Caso A: <Workflow|Agent> — <justificación en <= 2 líneas, citando si el orden es fijo o lo decide el LLM>
- Caso B: <Workflow|Agent> — <...>
- Caso C: <Workflow|Agent> — <...>
- Caso D: <Workflow|Agent> — <...>

CIERRE (1 línea): ¿qué tendría que cambiar para que un Workflow se convierta en Agent?
```

---

**Entregable del alumno:** los 4 casos clasificados con justificación de ≤ 2 líneas + la línea de
cierre. Recuerda la filosofía de Anthropic: **empieza por lo más simple** — si la tarea tiene
subtareas fijas y orden conocido, un workflow encadenado es más predecible, barato y testeable; el
agente solo gana cuando hace falta que el LLM dirija el flujo.
