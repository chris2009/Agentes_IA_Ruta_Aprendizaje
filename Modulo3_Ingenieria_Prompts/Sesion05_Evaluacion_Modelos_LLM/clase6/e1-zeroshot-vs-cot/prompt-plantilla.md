# Prompt-plantilla · e1 — Zero-shot vs zero-shot-CoT (el salto)

> El objetivo es **ver el delta** con tus propios ojos: el mismo modelo, el mismo problema, dos
> formas de pedirlo. La versión B solo añade un **disparador** — "pensemos paso a paso" (Kojima
> et al. 2022, *zero-shot-CoT*). Corre primero A, luego B (idealmente en chats separados para que
> A no contamine a B). Pega el enunciado de `problema.md` donde dice `{...}`.

---

## Versión A — prompt directo (zero-shot, sin razonamiento)

```
Resuelve el siguiente problema y responde SOLO con el total final en soles, sin explicación.

{pega aquí problema.md}
```

---

## Versión B — zero-shot-CoT (el disparador de Kojima)

```
Resuelve el siguiente problema. Pensemos paso a paso: muestra tu razonamiento numerado, una
operación por paso, y al final escribe la respuesta en una línea separada con el formato exacto
"Respuesta final: S/ ___".

{pega aquí problema.md}
```

---

**Entregable del alumno:** las dos salidas (A y B) + **1 línea** explicando qué cambió y por qué.
Identifica explícitamente que la frase "pensemos paso a paso" es el disparador del **zero-shot-CoT**
(Kojima et al. 2022).
