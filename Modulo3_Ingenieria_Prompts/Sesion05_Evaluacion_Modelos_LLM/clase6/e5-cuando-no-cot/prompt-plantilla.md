# Prompt-plantilla · e5 — Cuándo NO usar CoT (el matiz crítico)

> CoT **no es para todo**. La pregunta no es "¿uso CoT?" sino **"¿este problema tiene sub-pasos
> donde puedo equivocarme?"**. En tareas de un solo paso (clasificar, extraer un dato, traducir una
> palabra) el razonamiento solo agrega **ruido, coste y latencia** (más tokens = más caro y más
> lento). En tareas multietapa (cálculo en cascada, planificación con restricciones) CoT ayuda.
>
> Puedes resolverlo **tú mismo** (es un ejercicio de criterio) o pedírselo a un modelo con el prompt
> de abajo. Pega la lista de `tareas.md` donde dice `{...}`.

```
Para cada tarea de la lista, decide si conviene forzar razonamiento paso a paso (Chain-of-Thought)
o no. Responde en una tabla con estas columnas:

| # | Tarea | CoT sí / CoT no | Justificación (≤ 1 línea) |

Regla: marca "CoT sí" solo si la tarea tiene varios sub-pasos donde el modelo podría equivocarse;
marca "CoT no" si es de un solo paso (clasificar, extraer un dato, traducir). Después de la tabla,
escribe UNA frase nombrando el tradeoff de forzar CoT donde no aporta (coste en tokens y latencia).

Lista de tareas:
{pega aquí tareas.md}
```
