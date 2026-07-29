# Instrucciones de demo — El mega-prompt que hace 4 cosas a la vez

## Por qué este correo

Michael Torres pide reembolso + compensación, pero su pedido tiene **45 días** (fuera del plazo de 30), pide compensación económica (requiere aprobación de Gerencia) y escribe en inglés.

La Regla 4 agrega la trampa más detectable: si el pedido supera los 30 días, está **prohibido** usar las palabras "reembolso" o "devolución" — hay que usar "evaluación de excepción". El mega-prompt casi siempre usa los términos prohibidos en algún punto y luego su propio verificador dice CUMPLE. Eso es buscable con Ctrl+F en 5 segundos.

---

## Parte A — El mega-prompt (caja negra) · ~3 min

1. Abrir un chat nuevo en Claude.ai / ChatGPT / Gemini.
2. Pegar el contenido de `A-mega-prompt.md`.
3. Reemplazar los bloques `{pegar...}` con el contenido de `correo-cliente.md` y `politica-empresa.md`.
4. Ejecutar.

### Preguntas para hacer MIENTRAS los alumnos leen el output

> "¿Pueden decirme si la clasificación fue correcta sin leer todo el bloque de texto?" → No

> "¿Confían en que el modelo verificó sus propias reglas honestamente? ¿Es el mismo proceso que redactó la respuesta?" → Sí — eso es un problema

> "Buscá en el output las palabras 'reembolso' o 'devolución'." → Ctrl+F → aparecen → el verificador del mismo prompt dijo CUMPLE

**El punto no es que el output esté mal — es que no podés auditarlo.**
El mega-prompt puede dar un resultado correcto y aun así ser una caja negra. Si la semana que viene falla con otro email, no sabés en cuál de los 4 pasos buscar.

---

## Parte B — La cadena de 4 pasos · ~5 min

Abrí **4 chats separados**, uno por paso. En cada paso copiás la salida y la pegás como input del siguiente.

### Paso 1 — Clasificar
- Prompt: `B-paso1-clasificar.md` + contenido de `correo-cliente.md`
- Salida esperada:
```json
{
  "tipos": ["queja_producto", "solicitud_reembolso", "solicitud_compensacion"],
  "resumen_una_linea": "Cliente reporta cámara dañada al llegar y solicita reembolso completo, compensación y reposición urgente."
}
```
→ **Verificable en 5 segundos.** ¿Captó las tres solicitudes?

### Paso 2 — Traducir
- Prompt: `B-paso2-traducir.md` + contenido de `correo-cliente.md`
- Salida: correo en español
→ **Verificable en 5 segundos.** ¿La traducción es fiel? ¿Mantiene el tono urgente?

### Paso 3 — Redactar respuesta
- Prompt: `B-paso3-responder.md` + JSON del Paso 1 + correo traducido del Paso 2
- Salida: borrador de respuesta al cliente
→ **Leer antes de avanzar.** ¿Aparece "reembolso" o "devolución"? Si sí — ya sabés que el Paso 4 lo va a atrapar.

### Paso 4 — Verificar (el gate)
- Prompt: `B-paso4-verificar.md` + borrador del Paso 3 + contenido de `politica-empresa.md`
- El gate tiene **contexto aislado**: solo ve el borrador y la política — sin el historial de los pasos anteriores.
- Salida esperada si el borrador violó la Regla 4:
```json
{
  "veredicto": "NO CUMPLE",
  "regla_1_reembolsos": "OK",
  "regla_2_compensaciones": "OK",
  "regla_3_formato": "OK",
  "regla_4_terminologia": "VIOLA",
  "detalle": "El borrador usa la palabra 'reembolso' en el segundo párrafo. Debe reemplazarse por 'evaluación de excepción'."
}
```
→ **El gate detiene el correo.** Se vuelve al Paso 3 con el detalle como contexto adicional.

---

## La pregunta de cierre para el aula

> "En el mega-prompt: ¿dónde buscan el error cuando falla?"
> "En la cadena: ¿en qué paso supieron que algo iba a fallar?"

Con la cadena, la respuesta es **el Paso 3** — cuando leyeron el borrador antes de ejecutar la verificación. Con el mega-prompt esa ventana no existe.

---

## Qué conecta esto con el resto de la clase

| Lo que vieron en la demo | Concepto de Clase 7 |
|---|---|
| Los 4 pasos separados | Prompt chaining (Anthropic 2024) |
| El JSON de salida de cada paso | Contrato de I/O |
| El Paso 4 que dice CUMPLE / NO CUMPLE | Gate: approve / escalate |
| "Volvemos al Paso 3 con el detalle" | El gate detiene la propagación del error |
| Si el Paso 4 escala a Gerencia | HITL — Human in the Loop |
| Ctrl+F en el mega-prompt no encuentra nada | Caja negra — sin pasos visibles |
