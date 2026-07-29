# B · Paso 2 de 4 — Puntuar en 4 dimensiones

> Chat nuevo. Pegá el CV, los requisitos y el JSON del Paso 1.
> Copiá el JSON de salida — lo necesitás en el Paso 3.
> GATE DE ENTRADA: si el Paso 1 devolvió "cumple_minimos": false → no corras este paso.
> Anotá la decisión del gate y pasá directo al Paso 3 con avanza = false.

---

Eres un evaluador de selección. Usá el CV y la evaluación de requisitos para puntuar a la candidata en 4 dimensiones del 1 al 5.

Devolvé ÚNICAMENTE este JSON, sin texto adicional:

```json
{
  "experiencia_tecnica": <1-5>,
  "habilidades_blandas": <1-5>,
  "alineacion_cultural": <1-5>,
  "expectativa_salarial": <1-5>,
  "puntaje_total": <suma>,
  "avanza": true | false,
  "justificacion_breve": "<1 línea explicando la decisión de avanza>"
}
```

Criterio de `avanza`: puntaje_total >= 13 Y cumple_minimos = true.

<cv>
{pegar contenido de cv-candidato.md}
</cv>

<requisitos>
{pegar contenido de requisitos-puesto.md}
</requisitos>

<evaluacion_paso1>
{pegar JSON del Paso 1}
</evaluacion_paso1>
