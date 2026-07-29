# Criterio de evaluación · e6 (binario)

- [ ] **Señala el paso exacto** — identifica que el error está en el **Paso 1** (los descuentos).
- [ ] **Explica el porqué** — los descuentos son **en cascada** (20% y luego 10% sobre el resultado),
      no sumables; sumar 20% + 10% = 30% es el error. Lo correcto: 1,200 × 0.80 × 0.90 = 864.
- [ ] **Recalcula el final** — llega a **S/ 1,084.52** rehaciendo desde el paso corregido.
- [ ] **(Conceptual) Reconoce la propagación** — entiende que el error del Paso 1 contaminó toda la
      cadena (la cadena es tan fuerte como su eslabón más débil).

## Solución de referencia
- Paso 1 correcto: 1,200 × 0.80 = 960 → 960 × 0.90 = **864** (no 840).
- Paso 2: 864 × 1.18 = **1,019.52**.
- Paso 3: 1,019.52 + 90 + 25 = **1,134.52**.
- Paso 4: 1,134.52 − 50 = **S/ 1,084.52**.

La cadena con error daba S/ 1,056.20; la diferencia (S/ 28.32) nace toda en el Paso 1.

**Aprueba** si localiza el Paso 1 como la raíz, explica el descuento en cascada y recalcula a
S/ 1,084.52.
