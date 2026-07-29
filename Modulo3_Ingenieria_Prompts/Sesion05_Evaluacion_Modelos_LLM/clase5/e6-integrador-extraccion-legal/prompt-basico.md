# Prompt — e6 nivel BÁSICO (Individual)

> Aplica delimitadores + salida estructurada + faltantes=`null`. Input: `contrato-basico.md`
> (Servicios Globales). Objetivo: extraer los campos pedidos y devolver un JSON que cumpla
> `esquema-basico.json`. Pega el contrato entre `<doc></doc>`.

```
Actúa como un asistente legal junior. Extrae los datos del contrato laboral que está entre
<doc></doc> y devuélvelos EXCLUSIVAMENTE como un JSON que cumpla EXACTAMENTE este molde:
mismas claves, misma estructura, mismos tipos. No agregues claves ni texto fuera del JSON.

Reglas:
- Si un dato NO aparece explícitamente en el contrato, asigna null. NO inventes (p. ej. no inventes
  un RUC o un DNI).
- `duracion_meses` es un entero (meses de vigencia). `beneficios` es un array de strings.
- `remuneracion.monto` es número; `remuneracion.moneda` el código de moneda (p. ej. "PEN").

Molde de salida (cumple esquema-basico.json):
{
  "empleador": { "razon_social": "", "ruc": "", "representante": "" },
  "trabajadora": { "nombre": "", "dni": "", "domicilio": "" },
  "cargo": "",
  "fecha_inicio": "",
  "fecha_fin": null,
  "remuneracion": { "monto": 0, "moneda": "PEN" },
  "duracion_meses": 0,
  "beneficios": []
}

<doc>
{pega aquí el contenido de contrato-basico.md}
</doc>
```

**Datos esperados** (del contrato Servicios Globales): empleador `Servicios Globales S.A.C.` /
RUC `20123456789` / representante `Luis Alberto Ramírez Vargas`; trabajadora `Ana Sofía Morales Pérez`
/ DNI `87654321` / `Jr. Los Jazmines 456, Surco, Lima`; cargo `Coordinadora de Proyectos Digitales`;
inicio `2025-03-01`, fin `2026-02-28`; remuneración `7500 PEN`; duración `12` meses; beneficios
`["Gratificaciones de julio y diciembre", "Vacaciones 30 días", "EsSalud"]`.
