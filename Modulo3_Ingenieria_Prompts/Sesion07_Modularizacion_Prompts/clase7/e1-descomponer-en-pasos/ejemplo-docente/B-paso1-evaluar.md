# B · Paso 1 de 4 — Evaluar requisitos mínimos

> Chat nuevo. Pegá el CV y los requisitos. Copiá el JSON de salida — lo necesitás en el Paso 2.

---

Eres un evaluador de selección. Leé el CV y determiná si la candidata cumple cada requisito mínimo del puesto.

Devolvé ÚNICAMENTE este JSON, sin texto adicional:

```json
{
  "cumple_minimos": true | false,
  "requisitos": {
    "python": true | false,
    "sql": true | false,
    "experiencia_anios": <número calculado>,
    "experiencia_cumple": true | false,
    "ingles_intermedio": true | false
  },
  "gaps": ["<requisito que no cumple o es dudoso, con una línea explicando por qué>"],
  "nota_ambiguedades": "<si algo no está claro en el CV, indicarlo aquí>"
}
```

<cv>
{pegar contenido de cv-candidato.md}
</cv>

<requisitos>
{pegar contenido de requisitos-puesto.md}
</requisitos>
