# Prompt-plantilla · e4 — Guardrails en capas (defensa en capas)

> El objetivo es practicar la **defensa en capas** de OpenAI: *"un solo guardrail difícilmente da
> protección suficiente; varios especializados juntos crean agentes más resilientes."* Añades **2
> guardrails de categorías distintas** a un paso y dices **dónde** van (pre-input / gate intermedio /
> pre-output). Pega `paso.md` donde dice `<<<...>>>`. Puedes resolverlo a mano o con esta plantilla en
> un chat.

---

```
Eres un especialista en seguridad de sistemas con LLMs. Te doy un paso de un pipeline y su taxonomía
de guardrails. Añade 2 guardrails de CATEGORÍAS DISTINTAS y ubica cada uno en una capa coherente.

Paso a proteger (incluye la taxonomía de categorías):
<<<
{pega aquí el contenido de paso.md}
>>>

Devuelve EXACTAMENTE este formato, sin texto extra:

GUARDRAIL 1
- Categoría: <una de la taxonomía>
- Qué hace: <1 línea>
- Capa donde se inserta: <pre-input | gate intermedio | pre-output>
- Por qué esa capa: <1 línea coherente con su función>

GUARDRAIL 2
- Categoría: <OTRA categoría, distinta de la 1>
- Qué hace: <1 línea>
- Capa donde se inserta: <pre-input | gate intermedio | pre-output>
- Por qué esa capa: <1 línea coherente con su función>

NOTA (1 línea): por qué dos guardrails de capas distintas protegen mejor que uno solo (defensa en capas).
```

---

**Entregable del alumno:** los 2 guardrails (categorías distintas, ubicación coherente) + la nota de
defensa en capas. Recomendación de OpenAI: **empezar por privacidad + seguridad de contenido** y
añadir guardrails nuevos según los fallos reales que aparezcan.
