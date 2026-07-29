# Input · problema (e3 — Least-to-Most, problema complejo de varios pasos)

> Este es un problema genuinamente complejo: tiene **varias restricciones acopladas** y un **cuello
> de botella no obvio**. Resolverlo "a ojo" casi siempre falla porque la gente asume que el límite es
> el tiempo, cuando en realidad lo fija el presupuesto. El objetivo de e3 es **generar la respuesta
> correcta descomponiendo el problema en subproblemas ordenados** (Least-to-Most, Zhou et al. 2022),
> resolviéndolos en secuencia y reusando cada resultado en el siguiente.
>
> Pégalo donde lo indique `prompt-plantilla.md`.

---

Tengo que planificar un **taller** con estas condiciones:

- **Presupuesto total:** S/ 1,000.
- **Tiempo disponible:** 6 horas.
- **Participantes:** 12.
- El taller se dicta en **bloques de 90 minutos** cada uno.
- Cada bloque tiene un **costo de sala de S/ 200**.
- Necesito **1 facilitador por cada 4 participantes**, y cada facilitador cobra **S/ 120 por bloque**.
- Quiero el **máximo número de bloques posible** sin pasarme del **presupuesto** ni del **tiempo**.

**Preguntas a responder:** ¿cuántos bloques puedo dictar?, ¿cuánto gasto en total?, y ¿cuánto
presupuesto me sobra?
