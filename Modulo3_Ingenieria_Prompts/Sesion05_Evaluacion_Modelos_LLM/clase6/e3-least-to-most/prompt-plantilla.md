# Prompt-plantilla · e3 — Least-to-Most (descomponer en subproblemas ordenados)

> **Least-to-Most prompting (Zhou et al. 2022, arXiv 2205.10625):** ante un problema complejo, no lo
> ataques entero. Primero pídele al modelo que **descomponga** el problema en una **lista de
> subproblemas ordenados** (de lo más básico a lo que depende de ello); luego que los **resuelva uno
> a uno en secuencia**, reusando en cada subproblema las **respuestas de los anteriores**; y al final
> que **componga** la respuesta. Es la técnica que materializa el objetivo de la clase: *generar
> respuestas complejas paso a paso*. Generaliza mejor que un CoT plano en problemas largos/duros.
>
> Pega el enunciado de `problema.md` entre los delimitadores `<problema>...</problema>`.

---

## Plantilla (lista para pegar)

```
Vas a resolver un problema complejo usando descomposición (Least-to-Most). Sigue EXACTAMENTE estas
tres fases y respeta el formato de salida.

FASE 1 — DESCOMPONER:
  Lee el problema y escribe una lista NUMERADA de subproblemas en el ORDEN en que deben resolverse,
  del más básico al que depende de los anteriores. No los resuelvas todavía; solo enúncialos.

FASE 2 — RESOLVER EN SECUENCIA:
  Resuelve los subproblemas uno por uno, EN ORDEN. En cada subproblema:
   - muestra la operación,
   - indica explícitamente qué resultado(s) de subproblemas anteriores estás reusando,
   - escribe el resultado del subproblema.

FASE 3 — COMPONER:
  Combina los resultados de los subproblemas para construir la respuesta final.

FORMATO DE SALIDA (obligatorio):
  Subproblemas (orden):
    S1) ...
    S2) ...  (etc.)
  Resolución:
    S1 -> resultado
    S2 -> resultado  (usa: S1)   (etc.)
  Respuesta final: <una sola línea con las cifras pedidas>

Problema:
<problema>
{pega aquí problema.md}
</problema>
```

---

**Entregable del alumno:** la salida completa (las tres fases) + **1 línea** indicando cuál era el
**cuello de botella** (qué restricción fija el resultado).

**Opcional · combinar con self-consistency:** corre esta plantilla **3–5 veces** con temperatura
~0.7 y aplica **voto mayoritario** sobre la "Respuesta final" (ver e4). Si la descomposición es
buena, las corridas deberían converger.
