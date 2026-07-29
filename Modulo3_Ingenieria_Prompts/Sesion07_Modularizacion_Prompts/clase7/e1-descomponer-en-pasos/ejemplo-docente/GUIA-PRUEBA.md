# Guía de prueba — e1 · Pipeline de RRHH (para el instructor)

## Por qué este CV tiene ambigüedades intencionales

Sofía Mendoza está diseñada para generar debate en cada paso:

| Campo | Valor en el CV | Ambigüedad |
|---|---|---|
| Experiencia | 10 meses planilla + 19 meses freelance = 29 meses | ¿El freelance cuenta como "2+ años"? El puesto dice "planilla o freelance documentado" |
| Inglés | B1 certificado | ¿B1 es "intermedio"? Depende de la definición de la empresa |
| SQL | SELECT / JOIN / GROUP BY, sin stored procedures | ¿Es "intermedio"? El puesto pide "consultas intermedias" |
| Expectativa salarial | No declarada | El Paso 2 debe puntuar con 5 (no declara = dentro del rango por omisión) |

Estas ambigüedades son el material de debate del ejercicio. No hay una sola respuesta correcta.

---

## Corrida de referencia (lo que debería salir)

### Paso 1 — Evaluación de requisitos
```json
{
  "cumple_minimos": true,
  "requisitos": {
    "python": true,
    "sql": true,
    "experiencia_anios": 2.4,
    "experiencia_cumple": true,
    "ingles_intermedio": true
  },
  "gaps": [],
  "nota_ambiguedades": "El inglés B1 es borderline — cumple lectura técnica pero conversación limitada. La experiencia freelance (19 meses) se cuenta como documentada según los requisitos."
}
```
**Gate de entrada:** `cumple_minimos = true` → el Paso 2 corre.

**Debate esperado:** ¿el inglés B1 es intermedio? → Usar para mostrar que el gate del Paso 1 toma decisiones que se propagan: si marcás `false` acá, el Paso 3 redacta un correo de rechazo sin importar el puntaje.

---

### Paso 2 — Puntuación
```json
{
  "experiencia_tecnica": 3,
  "habilidades_blandas": 4,
  "alineacion_cultural": 4,
  "expectativa_salarial": 5,
  "puntaje_total": 16,
  "avanza": true,
  "justificacion_breve": "Perfil sólido para Jr., con Python y SQL funcionales y logros medibles. SQL sin stored procedures limita la nota técnica."
}
```
`avanza = true` porque puntaje_total (16) >= 13 Y cumple_minimos = true.

---

### Paso 3 — Correo (ejemplo de salida correcta)

> Estimada Sofía,
>
> Gracias por postularte al puesto de Analista de Datos en KQ Analytics y por el tiempo dedicado a compartir tu experiencia con nosotros.
>
> Hemos revisado tu perfil con detenimiento y nos complace informarte que has pasado a la siguiente etapa del proceso de selección. En los próximos días recibirás un mensaje de nuestro equipo para coordinar una conversación y conocerte mejor.
>
> Valoramos la trayectoria que has construido y esperamos con interés conocerte en esta próxima instancia.
>
> Saludos cordiales,
> Equipo de Selección — KQ Analytics

---

### Paso 4 — Verificación

```json
{
  "veredicto": "CUMPLE",
  "politica_datos_sensibles": "OK",
  "politica_salarial": "OK",
  "politica_tono": "OK",
  "politica_motivo": "OK",
  "action": "approve",
  "detalle": "Todo en regla."
}
```

---

## Cómo provocar un fallo en el Paso 4 (para mostrar el gate en vivo)

En el Paso 3 agregá al prompt: _"mencioná que el rango salarial del puesto es S/ 2,800–3,500"_.
El Paso 4 debería devolver:

```json
{
  "veredicto": "NO CUMPLE",
  "politica_salarial": "VIOLA",
  "action": "revise",
  "detalle": "El correo menciona el rango salarial (S/ 2,800–3,500), lo cual viola la política de RRHH."
}
```
→ Gate activo: volvés al Paso 3 con `detalle` como contexto de corrección.

---

## Preguntas para abrir debate después de la corrida

1. *"¿En qué paso tomaron la decisión más difícil?"* → casi siempre el Paso 1 (experiencia freelance + inglés B1)
2. *"¿Qué hubiera pasado si el Paso 1 marcaba `cumple_minimos = false`?"* → el correo del Paso 3 sería de rechazo aunque el puntaje sea 16
3. *"¿El Paso 4 puede confiar en su propia verificación si lo corrieron en el mismo chat que el Paso 3?"* → no — eso es la lección de la demo

---

## Conexión con la regla de oro de la clase
> El Paso 1 es el guardián de entrada. El Paso 4 es el guardián de salida.  
> Un error en el Paso 1 no llega al candidato — el gate lo detiene.  
> Sin la cadena, ese error viaja invisible hasta el correo final.
