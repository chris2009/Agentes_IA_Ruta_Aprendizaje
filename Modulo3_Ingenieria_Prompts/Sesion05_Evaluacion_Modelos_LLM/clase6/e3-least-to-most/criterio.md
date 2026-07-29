# Criterio de evaluación · e3 (binario)

- [ ] **¿Descompuso en subproblemas?** — la salida incluye una lista NUMERADA de subproblemas
      ordenados (Fase 1), enunciados antes de resolverlos.
- [ ] **¿Los resolvió en orden reusando los previos?** — resuelve S1, S2, … en secuencia, y al menos
      en los subproblemas dependientes **indica explícitamente** qué resultado anterior reusa
      (p. ej. "usa: S1", "usa: S2").
- [ ] **¿La respuesta final es correcta/completa?** — responde las tres preguntas (cuántos bloques,
      gasto total, presupuesto restante) y coincide con la solución de referencia.

## Solución de referencia

| Subproblema | Operación | Resultado |
|---|---|---|
| S1 · Facilitadores por bloque | ceil(12 / 4) | **3** |
| S2 · Costo por bloque | 200 (sala) + 3 × 120 (facilitadores) | **S/ 560** (usa S1) |
| S3 · Bloques que caben por TIEMPO | 6 h = 360 min ; 360 / 90 | **4 bloques** |
| S4 · Bloques que caben por PRESUPUESTO | floor(1000 / 560) | **1 bloque** (usa S2) |
| S5 · Componer | min(tiempo, presupuesto) = min(4, 1) | **1 bloque** (usa S3 + S4) |

- **Bloques:** **1** · **Gasto total:** **S/ 560** · **Presupuesto restante:** 1,000 − 560 = **S/ 440**.
- **Cuello de botella:** el **presupuesto** (solo alcanza 1 bloque), no el tiempo (que permitiría 4).

## El error común (lo que suele dar el atajo "a ojo")

Asumir que el límite es el **tiempo** y responder **4 bloques** (360 / 90), olvidando que cada bloque
cuesta S/ 560 y el presupuesto solo cubre **1**. También es común olvidar que se necesitan **3**
facilitadores (ceil(12/4)) y costear con menos.

**Aprueba** si: (a) hay una lista explícita de subproblemas ordenados, (b) se resuelven en orden
reusando los previos, y (c) la respuesta final es **1 bloque · S/ 560 · sobran S/ 440**. (El
aprendizaje central es el **procedimiento** de descomponer y encadenar; si combinó con
self-consistency, debería converger a esta misma respuesta.)
