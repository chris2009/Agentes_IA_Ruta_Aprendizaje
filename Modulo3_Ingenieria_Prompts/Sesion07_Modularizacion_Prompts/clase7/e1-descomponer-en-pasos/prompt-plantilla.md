# Prompt-plantilla · e1 — Descomponer una tarea grande en pasos (prompt chaining)

> El objetivo es **convertir un mega-prompt en un pipeline**: una secuencia de pasos donde cada paso
> hace UNA cosa y **procesa la salida del anterior** (*prompt chaining*, Anthropic 2024). No buscamos
> "mejorar" el mega-prompt; buscamos **partirlo**. Pega la tarea de `tarea-grande.md` donde dice
> `<<<...>>>`. Puedes correr esta plantilla en cualquier chat para que te ayude a descomponer, pero el
> entregable lo decides tú con el criterio.

---

```
Eres un arquitecto de pipelines de IA. Te doy una tarea que hoy se resuelve con UN solo prompt que
hace varias cosas a la vez. Tu trabajo NO es mejorar ese prompt, sino DESCOMPONERLO en una secuencia
de 2 a 4 pasos consecutivos, donde cada paso:
  - hace UNA sola cosa, nombrable con un verbo (clasificar, traducir, redactar, verificar...);
  - recibe como entrada la SALIDA del paso anterior (el primero recibe la entrada original);
  - expone un CONTRATO DE SALIDA explícito: qué entrega y en qué formato (texto plano, JSON con
    estas claves, lista, etc.).

Tarea a descomponer:
<<<
{pega aquí el contenido de tarea-grande.md}
>>>

Devuelve EXACTAMENTE este formato, sin texto extra:

PIPELINE PROPUESTO
- Paso 1 · <verbo + objeto>
  - Entrada: <qué recibe>
  - Salida (contrato): <qué entrega y en qué formato exacto>
- Paso 2 · <verbo + objeto>
  - Entrada: salida del Paso 1
  - Salida (contrato): <...>
- (Paso 3 / Paso 4 si aplica, mismo formato)

PUNTO DE GATE
- Entre el Paso __ y el Paso __, porque un error del primero contaminaría al segundo así: <explica en
  1 línea cómo se propagaría el error>.
```

---

**Entregable del alumno:** el pipeline de 2–4 pasos con el contrato de salida de cada uno + la línea
del punto de gate. Identifica explícitamente que partir el mega-prompt en pasos encadenados es
**prompt chaining** (Anthropic 2024) y que cada paso "procesa la salida del anterior".
