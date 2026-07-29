# Criterio de evaluación · e5 (binario)

- [ ] **Resuelve primero** — el modelo deriva su propia solución ANTES de juzgar la del alumno
      (el prompt lo ordena y la salida lo refleja).
- [ ] **Detecta el error** — dictamina INCORRECTO.
- [ ] **Señala dónde** — identifica que el costo por kilo NO se reparte sobre 120 kg, sino sobre
      los kilos que QUEDAN tras perder el 15% en el tueste.
- [ ] **No valida por inercia** — no acepta el S/ 64 del alumno.

**Solución correcta de referencia:**
- Costo total = 120×38 + 240 = 4560 + 240 = **S/ 4800**
- Kilos tras el tueste = 120 × (1 − 0.15) = **102 kg**
- Costo por kilo = 4800 / 102 ≈ **S/ 47.06**
- Precio con 60% de margen = 47.06 × 1.6 ≈ **S/ 75.29 por kilo**

El alumno se equivoca al dividir entre 120 (peso antes del tueste) en lugar de 102.

**Aprueba** si resuelve primero, detecta el error y lo localiza en el paso del peso tras tueste.
