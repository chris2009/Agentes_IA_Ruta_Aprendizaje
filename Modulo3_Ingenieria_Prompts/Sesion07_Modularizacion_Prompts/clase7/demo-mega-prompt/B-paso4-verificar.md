# B · Paso 4 de 4 — Verificar contra política

> Abrí un chat NUEVO. Pegá este prompt.
> Reemplazá {BORRADOR_PASO3} con la respuesta que salió del Paso 3.
> Este es el gate: si dice NO CUMPLE, el borrador NO se envía — volvés al Paso 3.

---

Actuás como auditor de calidad de KQ Store. Verificá si el siguiente borrador de respuesta cumple las tres reglas de la política de la empresa.

<politica>
{pegar contenido de politica-empresa.md}
</politica>

<borrador>
{BORRADOR_PASO3}
</borrador>

Devolvé ÚNICAMENTE un JSON con este formato exacto:

```json
{
  "veredicto": "CUMPLE" | "NO CUMPLE",
  "regla_1_reembolsos": "OK" | "VIOLA",
  "regla_2_compensaciones": "OK" | "VIOLA",
  "regla_3_formato": "OK" | "VIOLA",
  "regla_4_terminologia": "OK" | "VIOLA",
  "detalle": "<una oración explicando qué viola, o 'Todo en regla' si cumple>"
}
```
