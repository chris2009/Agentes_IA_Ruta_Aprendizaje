# Input · problema de razonamiento (para evaluar modelos)

Este es el problema que vas a pasar por **2–3 modelos** en dos condiciones (directo vs CoT). Es el
carrito de e1, con reglas inequívocas para que la corrección sea verificable contra una sola
respuesta numérica.

---

Calcula el total a pagar de este carrito. Reglas y **orden obligatorio**: primero los descuentos,
luego el IGV, y al final el cupón.

- **Cámara**: precio S/ 1,200. Tiene un descuento del **20%** y, sobre el resultado, un descuento
  **adicional del 10%** (descuentos en cascada).
- **Libro**: precio S/ 90. **Exento de IGV**, sin descuentos.
- **Envío**: S/ 25, **sin IGV** y sin descuentos.
- El **IGV es 18%** y se aplica solo sobre la cámara.
- Hay un **cupón de S/ 50** que se resta del total, al final de todo.

¿Cuál es el total a pagar en soles?

---

> **Respuesta correcta (solo docente):** **S/ 1,084.52**. (Cámara: 1,200 → 960 → 864; IGV: 864 ×
> 1.18 = 1,019.52; + libro 90 + envío 25 = 1,134.52; − cupón 50 = **1,084.52**.) El error común es
> **S/ 1,056.20** (descuento 30% de una sola pasada).
