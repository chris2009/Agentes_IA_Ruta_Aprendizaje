# Prompt-plantilla · e4 — Self-consistency (N=5 + voto mayoritario)

> Self-consistency (Wang et al. 2022): en vez de fiarte de **una** cadena de razonamiento, generas
> **varias** con **temperatura > 0** (para que difieran) y te quedas con la respuesta por **voto
> mayoritario**. Las cadenas correctas tienden a converger al mismo número; los errores, al ser
> aleatorios, se dispersan y no se ponen de acuerdo.
>
> **Cómo correrlo:**
> 1. Si tu interfaz permite ajustar **temperatura**, súbela a **~0.7** (Anthropic Console / Google
>    AI Studio / OpenAI Playground lo permiten). En un chat normal sin control de temperatura, abre
>    **5 conversaciones nuevas** y pega el mismo prompt en cada una (cada chat nuevo re-muestrea).
> 2. Corre el prompt **5 veces**.
> 3. Anota la "Respuesta final" de cada corrida en `plantilla-resultados.md` y aplica el voto.
>
> Pega el enunciado de `problema.md` donde dice `{...}`.

```
Resuelve el siguiente problema pensando paso a paso. Muestra tu razonamiento numerado y termina
SIEMPRE con una línea con el formato exacto "Respuesta final: S/ ___".

{pega aquí problema.md}
```
