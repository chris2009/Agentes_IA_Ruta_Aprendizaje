# Criterio de evaluación · e1 (binario)

- [ ] **Pipeline de 2–4 pasos** — la tarea se partió en una secuencia de entre 2 y 4 pasos (no uno
      solo, no diez).
- [ ] **Cada paso hace UNA cosa nombrable con un verbo** — p. ej. *clasificar*, *traducir*,
      *redactar*, *verificar*. Un paso que "clasifica y traduce" a la vez **no cumple**: debe partirse.
- [ ] **Cada paso explicita su contrato de salida** — qué entrega y **en qué formato** (texto plano,
      JSON con estas claves, lista numerada...). Decir solo "devuelve el resultado" **no cumple**.
- [ ] **Encadenamiento real** — se ve que el Paso N recibe como entrada la **salida** del Paso N−1
      (no la entrada original repetida).
- [ ] **Punto de gate identificado** — se marca al menos **un** punto donde un error de un paso
      contaminaría al siguiente, con una línea que explica cómo se propagaría.

## Descomposición de referencia (una posible — no la única)
El mega-prompt de soporte se parte limpiamente en 4 pasos:

1. **Clasificar** → entrada: correo del cliente · salida (contrato):
   `{"tipo": "reclamo|consulta|reembolso|otro", "urgencia": "alta|media|baja", "idioma": string}`
2. **Traducir** (solo si `idioma != "es"`) → entrada: correo + idioma detectado · salida: el texto
   del correo en español (texto plano).
3. **Redactar respuesta** → entrada: tipo + urgencia + correo en español · salida: borrador de
   respuesta al cliente (texto plano).
4. **Verificar política** → entrada: el borrador del Paso 3 · salida (contrato):
   `{"cumple_politica": bool, "violaciones": [string], "action": "approve|revise|escalate"}`

**Punto de gate natural:** entre el Paso 3 (redactar) y el envío al cliente, el Paso 4 actúa como
gate — si el borrador promete un reembolso de S/ 500, el verificador lo marca y dispara `revise`
antes de que salga al cliente. Sin ese gate, el error del Paso 3 llega directo al cliente.

## Por qué importa (lo que se discute en clase)
El mega-prompt fallaba "en algún lado". Partido en pasos, si falla, **sabes en cuál**: ¿clasificó
mal el Paso 1?, ¿tradujo mal el 2?, ¿inventó política el 4? Eso es lo que el chaining recupera:
**precisión por paso, depuración localizada y formato estable entre pasos.**

**Aprueba** si hay 2–4 pasos, cada uno hace una cosa con verbo y declara su formato de salida, se ve
el encadenamiento, y se marca al menos un punto de gate con su justificación de propagación.
