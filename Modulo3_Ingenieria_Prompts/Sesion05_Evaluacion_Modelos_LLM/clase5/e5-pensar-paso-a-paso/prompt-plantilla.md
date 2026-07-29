# Prompt-plantilla · e5 — Resolver antes de concluir (Principio 2 / CoT)

> Táctica 2 del Principio 2. Si le pides directo "¿está bien esta solución?", el modelo tiende a
> ESTAR DE ACUERDO. Forzarlo a resolver primero por su cuenta lo hace contrastar en vez de validar
> por inercia. Pega el problema y la solución del alumno en sus bloques.

```
Vas a evaluar la solución de un alumno a un problema. NO digas todavía si es correcta.

Paso 1: resuelve el problema TÚ MISMO desde cero, mostrando todo tu razonamiento paso a paso.
Paso 2: recién entonces compara tu resultado con el del alumno, número a número.
Paso 3: dictamina CORRECTO o INCORRECTO. Si es incorrecto, señala el paso exacto donde está el
        error y cuál sería el valor correcto.

<problema>
{pega aquí problema.md}
</problema>

<solucion_alumno>
{pega aquí solucion-alumno.md}
</solucion_alumno>
```
