# B · Paso 1 de 4 — Clasificar el correo

> Abrí un chat nuevo. Pegá este prompt con el correo de `correo-cliente.md`.
> Copiá la salida completa — la vas a necesitar en el Paso 3.

---

Leé el siguiente correo de un cliente y clasificá el tipo de solicitud.

Devolvé ÚNICAMENTE un JSON con este formato exacto, sin texto adicional:

```json
{
  "tipos": ["<tipo1>", "<tipo2>"],
  "resumen_una_linea": "<qué pide el cliente en una oración>"
}
```

Tipos posibles: "queja_producto", "solicitud_reembolso", "solicitud_compensacion", "consulta".

<correo>
{pegar contenido de correo-cliente.md}
</correo>
