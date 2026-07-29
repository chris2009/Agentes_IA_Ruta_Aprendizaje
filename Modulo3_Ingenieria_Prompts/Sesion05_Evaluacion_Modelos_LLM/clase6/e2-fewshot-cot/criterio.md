# Criterio de evaluación · e2 (binario)

Sobre el DISEÑO del prompt (lo que entrena el ejercicio):
- [ ] **Exactamente 2 exemplars** resueltos antes del caso nuevo.
- [ ] **Cada exemplar muestra los pasos** (≥ 2 pasos intermedios numerados, no solo el resultado).
- [ ] **Formato de respuesta final consistente** — los dos ejemplos terminan en "Respuesta final: ___".
- [ ] **El caso a resolver NO está entre los ejemplos** (es el de `tarea.md`, con 6 máquinas y 180 piezas).

Sobre la SALIDA (sanity check con la clave de respuestas):
- La tasa heredada de los ejemplos es **3 piezas por máquina por hora**.
- Con 6 máquinas: 6 × 3 = **18 piezas/hora**.
- Para 180 piezas: 180 ÷ 18 = **10 horas**.
- **Respuesta final esperada: 10 horas.**

**Aprueba** si el prompt cumple las 4 condiciones de diseño y la salida imita el formato (pasos
numerados + "Respuesta final:") llegando a **10 horas**. Que el modelo copie el patrón de pasos es
la verificación de que el few-shot CoT funcionó.
