# Criterio de evaluación · e2 (binario)

- [ ] **Estructural (forma)** — el contrato lista **claves + tipos** explícitos (p. ej.
      `faithful: boolean`, `missing_info: string[]`, `action: string`). No basta nombrar las claves
      sin el tipo.
- [ ] **Semántica (contenido)** — incluye **≥ 1 regla verificable del dominio** (p. ej. "si
      `faithful=false`, entonces `missing_info` o `changes_of_meaning` debe tener ≥ 1 elemento", o
      "`confidence` ∈ [0,1]").
- [ ] **Operativa (gate)** — define la **acción** `approve | revise | escalate` con un **umbral o
      condición** explícita, **cubriendo los tres casos** (no solo approve/revise).
- [ ] **El escalado depende de los reintentos** — la regla usa `retries`/`max_retries` (o un umbral
      equivalente): se escala cuando se agotan los reintentos, no de forma arbitraria.
- [ ] **El ejemplo de JSON parsea** — el objeto de muestra es JSON válido y **cumple el contrato que
      el alumno acaba de escribir** (las claves y tipos coinciden).

## Contrato + gate de referencia (uno válido — no el único)

**Contrato de salida:**
```json
{
  "faithful": true,
  "missing_info": [],
  "changes_of_meaning": [],
  "confidence": 0.0,
  "action": "approve",
  "retries": 0,
  "max_retries": 2
}
```
- Estructural: `faithful: boolean`, `missing_info: string[]`, `changes_of_meaning: string[]`,
  `confidence: number`, `action: "approve"|"revise"|"escalate"`, `retries: number`,
  `max_retries: number`.
- Semántica: si `faithful=false`, entonces `missing_info` o `changes_of_meaning` tiene ≥ 1 elemento;
  `confidence` ∈ [0, 1].

**Regla del gate:**
```
if faithful == true:                         -> "approve"
elif faithful == false and retries <  max_retries:  -> "revise"   (reintentar la traducción)
elif faithful == false and retries >= max_retries:  -> "escalate" (a un revisor humano)
```

**Ejemplo de salida válida (caso revise):**
```json
{
  "faithful": false,
  "missing_info": ["se omitió la cifra de S/ 200 del original"],
  "changes_of_meaning": [],
  "confidence": 0.55,
  "action": "revise",
  "retries": 1,
  "max_retries": 2
}
```

## El punto clave (lo que se discute en clase)
La acción es **separable y chequeable**: nadie opina si "quedó bien"; el campo `faithful` lo decide y
el gate lo traduce a un movimiento del pipeline. El gate **detiene la propagación**: sin él, una mala
traducción avanza al cliente.

**Aprueba** si el contrato tiene estructural + ≥ 1 regla semántica + gate con los tres casos
(approve/revise/escalate) atado a un umbral/reintentos, y el JSON de ejemplo parsea y cumple ese
contrato.
