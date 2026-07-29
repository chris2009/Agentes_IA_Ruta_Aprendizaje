# Rúbrica de comparación · e7 (4 ejes)

Evaluar = dejar de juzgar "a ojo" y medir con una **rúbrica explícita** para que dos personas
lleguen al mismo veredicto. Puntúa **cada salida** (cada celda `modelo × condición`) en estos
4 ejes. Escala **1–5** salvo el eje 1, que es eliminatorio.

| Eje | Qué mide | Escala |
|-----|----------|--------|
| **1. Corrección** | ¿El total final es **S/ 1,084.52**? | **Binario / eliminatorio**: correcto = 5, incorrecto = 1. Si no es correcto, el resto pierde casi todo su valor. |
| **2. Fidelidad de los pasos** | ¿Cada paso del rastro es válido y **realmente lleva** a la respuesta (no es relleno post-hoc)? | 1 (sin pasos o pasos que no cuadran) → 5 (cada paso se verifica y encadena). En la condición directa, sin pasos, este eje no aplica: márcalo "N/A". |
| **3. Claridad** | ¿El rastro es legible, separable y **auditable** por un humano (pasos numerados, respuesta final destacada)? | 1 (confuso) → 5 (impecable). |
| **4. Coste** | Longitud de la salida / tokens / latencia. Más pasos = más tokens = más caro y lento. | 1 (muy largo/lento para lo que aporta) → 5 (eficiente). La condición directa suele ganar aquí; el punto es ver el **tradeoff** contra la corrección. |

## Cómo decidir el ganador
- El ganador se declara **por tarea/condición**, no en abstracto: gana quien maximiza **corrección
  por coste** para *esta* tarea, **no** "el modelo más grande".
- **Regla práctica:** primero filtra por corrección (eje 1). Entre los correctos, prefiere el que dé
  mejor fidelidad + claridad al menor coste.
- Espera ver el patrón de la clase: la condición **CoT** suele subir la **corrección** a costa del
  **coste**; la **directa** es barata pero más propensa al error común (S/ 1,056.20).

## Criterio binario de aprobación del ejercicio
- [ ] **≥ 2 modelos × 2 condiciones** evaluados (mínimo 4 celdas).
- [ ] **Corrección verificada** contra la respuesta de referencia (S/ 1,084.52), no "a ojo".
- [ ] **Cada eje de la rúbrica puntuado** en cada celda (con "N/A" donde corresponda).
- [ ] **Decisión justificada por corrección Y coste** — no por tamaño del modelo.
