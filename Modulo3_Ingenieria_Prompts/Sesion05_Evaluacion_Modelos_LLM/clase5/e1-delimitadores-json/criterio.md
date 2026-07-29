# Criterio de evaluación · e1 (binario)

El ejercicio se construye en **dos pasos sobre el mismo prompt**. Cada paso tiene su criterio.

## Parte 1 · Delimitadores (`prompt-plantilla-1-delimitadores.md`)
Salida libre (lista en texto). Lo que se evalúa es el **aislamiento del input como dato**.

- [ ] **Demarcado** — el input va dentro de los delimitadores `<texto></texto>` y la instrucción se
      refiere a ese bloque.
- [ ] **Trató el ruido como dato** — NO ejecutó ni obedeció el spam embebido ("GANA UN IPHONE…") ni
      la firma; nada fuera del bloque se interpretó como instrucción.
- [ ] **Filtró el ruido** — listó las **3 reseñas reales** (RunFlex Pro, TrekLite 30L, AromaOne) y
      descartó spam, firmas y metadatos.

**Aprueba la parte 1** si demarcó + ignoró el ruido + listó las 3 reseñas reales.

## Parte 2 · Salida estructurada (`prompt-plantilla-2-json.md`)
La misma extracción, ahora con **contrato de salida verificable**.

- [ ] **Parsea** — la salida es JSON válido (carga con `json.loads` sin error). *Eliminatorio.*
- [ ] **Solo JSON** — no hay texto fuera del JSON (ni "Aquí tienes:", ni explicaciones).
- [ ] **Esquema** — clave raíz `reseñas` = array; cada item tiene exactamente
      `producto`, `valoracion`, `sentimiento`, `recomendaria` (cumple `esquema.json`).
- [ ] **Tipos** — `producto` string · `valoracion` number 1..5 · `sentimiento` en
      {positivo, neutro, negativo} · `recomendaria` boolean.

**Aprueba la parte 2** si parsea + solo JSON + esquema + tipos (sobre las mismas 3 reseñas).

**Solución de referencia** (los valores pueden variar levemente en redacción del nombre):
- RunFlex Pro → valoracion 5, sentimiento positivo, recomendaria true
- TrekLite 30L → valoracion 2, sentimiento negativo, recomendaria false
- AromaOne → valoracion 3, sentimiento neutro, recomendaria true
