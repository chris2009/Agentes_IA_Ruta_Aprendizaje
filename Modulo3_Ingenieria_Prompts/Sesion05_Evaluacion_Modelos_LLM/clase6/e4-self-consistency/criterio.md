# Criterio de evaluación · e4 (binario)

- [ ] **≥ 3 muestras independientes** — corre el prompt CoT al menos 3 veces (la consigna pide 5),
      con temperatura > 0 o en chats separados.
- [ ] **Extrae la respuesta final de cada corrida** y la anota en la tabla de `plantilla-resultados.md`.
- [ ] **Reporta el voto mayoritario** — declara la respuesta más frecuente.
- [ ] **Reporta la dispersión** — cuántas corridas coincidieron con la ganadora (p. ej. "4 de 5").

## Solución de referencia
- Respuesta correcta = **S/ 1,084.52** (cámara 1,200 → 960 → 864; IGV 864×1.18 = 1,019.52; +90 +25;
  cupón −50). Es el mismo cálculo que en e1.
- El **error común** es **S/ 1,056.20** (aplicar 30% de descuento de una sola pasada). Es esperable
  que aparezca en 0–2 corridas; el voto mayoritario debería favorecer S/ 1,084.52.

**Aprueba** si hay ≥ 3 muestras, se extrae la respuesta de cada una, y se reporta tanto el voto
mayoritario como la dispersión. (No se exige que la mayoría sea siempre la correcta —el aprendizaje
es el procedimiento de votar— pero se discute en clase qué pasa si la mayoría se equivoca.)
