# Criterio de evaluación · e1 (binario)

- [ ] **Corre las dos versiones** — entrega la salida del prompt directo (A) y la del zero-shot-CoT (B).
- [ ] **La versión B muestra ≥ 2 pasos** intermedios numerados antes de la respuesta final.
- [ ] **La versión B llega al resultado correcto** — total **S/ 1,084.52** (ver cálculo abajo).
- [ ] **Identifica el disparador** — el alumno nombra "pensemos paso a paso" como **zero-shot-CoT**
      (Kojima et al. 2022) y explica en 1 línea qué cambió (forzar el razonamiento evitó el atajo).

## Solución correcta de referencia
- Cámara con descuentos en cascada: 1,200 × 0.80 = **960**, luego 960 × 0.90 = **864**.
- IGV 18% solo sobre la cámara: 864 × 1.18 = **1,019.52**.
- Libro (exento, sin descuento) = 90 · Envío (sin IGV) = 25.
- Subtotal antes del cupón: 1,019.52 + 90 + 25 = **1,134.52**.
- Cupón al final: 1,134.52 − 50 = **S/ 1,084.52**.

## El error común (lo que suele dar el prompt directo A)
Aplicar 20% + 10% = **30%** de una sola pasada (1,200 × 0.70 = 840 → IGV 991.20 → +90 +25 −50),
y/o mezclar el orden de descuento/IGV/cupón. Ese atajo produce **S/ 1,056.20**. El punto del
ejercicio es que el **mismo modelo** acierta cuando se le obliga a razonar y falla cuando salta
directo al resultado.

**Aprueba** si corre A y B, B tiene ≥ 2 pasos y da S/ 1,084.52, y el alumno nombra el disparador
zero-shot-CoT.
