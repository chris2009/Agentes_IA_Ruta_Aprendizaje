# Criterio de evaluación · e5 (binario)

- [ ] **≥ 4 de 5 clasificadas correctamente** según la clave de abajo.
- [ ] **Cada tarea tiene justificación** de ≤ 1 línea.
- [ ] **Nombra el tradeoff de coste/latencia** al menos una vez (más pasos = más tokens de salida =
      más caro y más lento).
- [ ] **Sin sobre-ingeniería** — marcar "CoT sí" en una tarea de un solo paso (1, 3 o 5) cuenta como
      **error conceptual**.

## Clave de respuestas
| # | Tarea | Veredicto | Por qué |
|---|-------|-----------|---------|
| 1 | Clasificar ticket | **CoT no** | Un solo paso; clasificación trivial, CoT solo agrega ruido y costo. |
| 2 | Total con descuentos+IGV+cupón | **CoT sí** | Varias operaciones encadenadas y orden que importa: aquí se gana exactitud. |
| 3 | Extraer un correo del texto | **CoT no** | Extracción directa de un dato; no hay sub-pasos donde equivocarse. |
| 4 | Ruta óptima con ventanas y capacidad | **CoT sí** | Optimización con múltiples restricciones; descomponer ayuda. |
| 5 | Traducir "gato" al inglés | **CoT no** | Tarea atómica de una palabra; el razonamiento es puro overhead. |

**Aprueba** si acierta ≥ 4/5, justifica cada una, y nombra el tradeoff de coste/latencia. Marcar
"CoT sí" en 1, 3 o 5 (sobre-ingeniería) baja la nota aunque el resto esté bien.
