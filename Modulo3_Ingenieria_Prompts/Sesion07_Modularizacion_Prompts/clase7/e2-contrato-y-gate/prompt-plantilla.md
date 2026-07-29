# Prompt-plantilla · e2 — Contrato de I/O + regla del gate

> El objetivo es convertir "¿quedó bien la traducción?" (opinión, no escalable) en "¿parsea y cumple
> el contrato?" (criterio **binario**, automatizable). Un **contrato** especifica qué devuelve el paso
> (claves, tipos, reglas); un **gate** es la regla que se evalúa **sobre esa salida** para decidir
> `approve | revise | escalate`. Pega `paso-ejemplo.md` donde dice `<<<...>>>` y usa `esquema.json`
> como base. Esta plantilla te ayuda a redactarlo; el entregable lo decides con el criterio.

---

```
Eres un diseñador de contratos de I/O para pasos de un pipeline de IA. Te doy la descripción de un
paso. Define su CONTRATO DE SALIDA (un objeto JSON) y la REGLA DEL GATE que se evalúa sobre ese JSON.

Paso a contratar:
<<<
{pega aquí el contenido de paso-ejemplo.md}
>>>

Esquema base de partida (puedes ajustarlo, pero conserva faithful y action):
{pega aquí el contenido de esquema.json}

Devuelve EXACTAMENTE este formato, sin texto extra:

CONTRATO DE SALIDA (JSON)
- Estructural (forma): lista cada clave con su tipo. Ej.: faithful: boolean, missing_info: string[].
- Semántica (contenido): >= 1 regla del dominio que la salida debe cumplir. Ej.: "si faithful es
  false, missing_info o changes_of_meaning debe tener >= 1 elemento".

REGLA DEL GATE (operativa)
- Escribe la condición que mapea la salida a una acción. Cubre los tres casos:
  - approve: <condición>
  - revise:  <condición que incluye un umbral o el conteo de reintentos>
  - escalate: <condición de escalado a humano>

EJEMPLO DE SALIDA VÁLIDA
- Un objeto JSON concreto que cumpla el contrato (debe poder parsearse tal cual).
```

---

**Entregable del alumno:** el contrato (estructural + semántica), la regla del gate
(approve/revise/escalate con umbral o reintentos) y un ejemplo de JSON válido. El contrato materializa
los **gates programáticos** que Anthropic (2024) describe entre los pasos de un chain.
