# Input · cadena de razonamiento con un error inyectado

Esta es una cadena CoT que resuelve el carrito de e1. **Tiene un error inyectado.** Pégala donde lo
indique `prompt-plantilla.md`. El alumno (o el modelo) debe hallar el paso roto, explicar por qué y
recalcular el total correcto.

> **El enunciado original** (mismas reglas que e1): Cámara S/ 1,200 con −20% y luego −10% adicional;
> Libro S/ 90 exento de IGV; Envío S/ 25 sin IGV; IGV 18% solo sobre la cámara; cupón de S/ 50 al
> final. Orden: descuentos → IGV → cupón.

---

**Cadena a auditar:**

- Paso 1 — Descuentos sobre la cámara: 20% + 10% = 30% de descuento total. 1,200 × (1 − 0.30) = **840**.
- Paso 2 — IGV 18% sobre la cámara con descuento: 840 × 1.18 = **991.20**.
- Paso 3 — Sumo libro y envío (sin IGV): 991.20 + 90 + 25 = **1,106.20**.
- Paso 4 — Aplico el cupón al final: 1,106.20 − 50 = **1,056.20**.
- **Respuesta final: S/ 1,056.20.**

---

## SOLUCIÓN (solo para el docente — no mostrar al alumno antes de tiempo)

- **El error está en el Paso 1.** Los descuentos son **en cascada** (uno después del otro), no
  sumables. Sumar 20% + 10% = 30% es el error clásico. Lo correcto:
  1,200 × 0.80 = **960**, y luego 960 × 0.90 = **864** (equivale a un descuento efectivo del 28%,
  no del 30%).
- Como el Paso 1 alimenta a todos los siguientes, **el error contamina la cadena entera** (la cadena
  es tan fuerte como su eslabón más débil).
- **Recálculo correcto desde el Paso 1:**
  - Paso 1: 1,200 × 0.80 × 0.90 = **864**.
  - Paso 2: 864 × 1.18 = **1,019.52**.
  - Paso 3: 1,019.52 + 90 + 25 = **1,134.52**.
  - Paso 4: 1,134.52 − 50 = **1,084.52**.
- **Respuesta final correcta: S/ 1,084.52.**
