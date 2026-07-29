# B · Paso 4 de 4 — Verificar políticas de RRHH

> Chat nuevo. Pegá el borrador del Paso 3 y los requisitos.
> Este es el gate final: si devuelve "NO CUMPLE" → volvés al Paso 3 con el detalle como contexto.

---

Actuás como auditor de políticas de RRHH. Verificá si el siguiente correo cumple todas las políticas de la empresa.

Devolvé ÚNICAMENTE este JSON, sin texto adicional:

```json
{
  "veredicto": "CUMPLE" | "NO CUMPLE",
  "politica_datos_sensibles": "OK" | "VIOLA",
  "politica_salarial": "OK" | "VIOLA",
  "politica_tono": "OK" | "VIOLA",
  "politica_motivo": "OK" | "VIOLA",
  "action": "approve" | "revise",
  "detalle": "<qué viola exactamente, o 'Todo en regla' si cumple>"
}
```

Políticas a verificar:
- **datos_sensibles**: el correo NO menciona edad, género, estado civil ni religión
- **salarial**: el correo NO hace promesas de sueldo ni menciona el rango salarial
- **tono**: empático y profesional, sin frases genéricas como "Lamentamos informarle que…"
- **motivo**: si no avanza, da UN motivo general (no detalla puntuaciones ni compara candidatos)

<borrador>
{pegar correo del Paso 3}
</borrador>

<politicas>
{pegar contenido de requisitos-puesto.md — sección "Políticas de RRHH"}
</politicas>
