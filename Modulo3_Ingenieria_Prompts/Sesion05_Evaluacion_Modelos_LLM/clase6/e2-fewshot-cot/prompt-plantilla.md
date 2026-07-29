# Prompt-plantilla · e2 — Few-shot CoT (2 exemplars resueltos con pasos)

> Few-shot CoT (Wei et al. 2022): en lugar de *decir* "razona paso a paso", le **enseñamos la forma
> exacta** del razonamiento con ejemplos resueltos. Los 2 exemplars fijan el **patrón de pasos** y
> el **formato de respuesta final** ("Respuesta final: ___") sin enunciar una sola regla. El caso
> a resolver (de `tarea.md`) **no** aparece entre los ejemplos. Pega el caso nuevo donde dice `{...}`.

```
Resuelve cada problema mostrando el razonamiento paso a paso, igual que en los ejemplos.

Ejemplo 1:
P: 4 máquinas iguales fabrican 96 piezas en 8 horas. ¿Cuál es la tasa de producción por máquina y por hora?
R: Paso 1 — piezas totales por hora: 96 ÷ 8 = 12 piezas/hora (entre las 4 máquinas).
   Paso 2 — tasa por máquina: 12 ÷ 4 = 3 piezas por máquina por hora.
   Respuesta final: 3 piezas por máquina por hora.

Ejemplo 2:
P: Si cada máquina produce 3 piezas por hora, ¿cuántas piezas hacen 5 máquinas en 6 horas?
R: Paso 1 — piezas por hora con 5 máquinas: 5 × 3 = 15 piezas/hora.
   Paso 2 — en 6 horas: 15 × 6 = 90 piezas.
   Respuesta final: 90 piezas.

Ahora resuelve este caso con el mismo formato (pasos numerados + "Respuesta final:"):
P: {pega aquí tarea.md}
R:
```
