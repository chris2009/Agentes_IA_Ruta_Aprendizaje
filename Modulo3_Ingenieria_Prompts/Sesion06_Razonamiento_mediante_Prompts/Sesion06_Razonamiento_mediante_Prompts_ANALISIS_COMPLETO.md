# Razonamiento mediante Prompts — Análisis completo de la Sesión 6

> **Fuente base:** *Razonamiento mediante prompts [C6 - 2026]* — Módulo 3, Programa en Diseño e Implementación de Agentes IA, UTEC Posgrado.
> **Complementado con:** investigación propia sobre ReAct, Tree of Thoughts, y cómo el razonamiento inducido por prompt evolucionó hacia el "adaptive thinking" nativo de los modelos actuales (Claude, 2026).
> **Propósito de este documento:** que sirva como referencia operativa para decidir *cuándo* y *cómo* forzar razonamiento explícito en un prompt — y, sobre todo, para entender por qué esta técnica es el **motor de decisión** de cualquier agente que deba elegir qué herramienta invocar.
> **Nota de formato:** las expresiones matemáticas usan notación LaTeX (`$...$` inline, `$$...$$` en bloque). Se ven renderizadas en GitHub, Obsidian, Typora, Jupyter, o VS Code con una extensión de math (p. ej. "Markdown+Math" o "Markdown Preview Enhanced"). El preview nativo de VS Code sin extensión muestra el código LaTeX literal en vez de renderizarlo.

---

## 0. Dónde se ubica esta sesión y qué la conecta con la Clase 5

```
Clase 5 → Clase 6 (esta) → Clase 7 → Agentes
Contrato +   Razonamiento      Modularizar
2 principios explícito dentro   contratos con
             del contrato (CoT) gates/guardrails
```

La Clase 5 estableció el **Principio 2** de Ng & Fulford: *"dar tiempo al modelo para pensar"*. La Clase 6 toma ese principio y lo convierte en un conjunto de técnicas concretas, con evidencia empírica publicada, para saber exactamente **cuándo, cómo y con qué forzar ese razonamiento** — y cómo comparar qué tan bien lo hace un modelo frente a otro.

La tesis central de la sesión:

> **El resultado correcto no estaba en "usar un modelo más caro". Estaba en forzar el razonamiento y dejar la cadena a la vista para poder auditarla.**

Toda la clase gira en torno a responder tres preguntas:
1. ¿Cuándo forzar el razonamiento?
2. ¿Cómo hacerlo?
3. ¿Cómo comparar quién lo hace mejor?

---

## 1. La demostración de apertura: "misma pregunta, distinto pedido"

**El problema:** calcular el total de un carrito con descuentos en cascada (20% + 10% adicional) + IGV (18%, solo sobre un ítem) + cupón final.

| Método | Resultado | Qué pasó |
|---|---|---|
| **A ojo (respuesta directa)** | S/ 1,056.20 | Aplicó 20%+10% = 30% en una sola pasada — error común, pero *plausible* |
| **Paso a paso (Chain-of-Thought)** | S/ 1,084.52 | Descuentos secuenciales, IGV solo al ítem correcto, cupón al final |

**Mismo modelo, mismo prompt de fondo — ~S/28 de diferencia.** La única variable que cambió fue **cómo se lo pidieron**. Este es el ancla empírica de toda la sesión: la ganancia no vino de cambiar de modelo, vino de cambiar la forma de la instrucción.

---

## 2. Canon de autores — quién aportó qué

Esta sesión amplía el canon de la Clase 5 con dos autores nuevos, formando un cuarteto de referencia:

| Autor | Paper | Aporte concreto |
|---|---|---|
| **Jason Wei et al.** (2022) | *Chain-of-Thought Prompting Elicits Reasoning in LLMs* — arXiv:2201.11903; NeurIPS 2022 | **Few-shot CoT**: ejemplos con razonamiento paso a paso. Con 8 exemplars, PaLM 540B alcanzó SOTA en GSM8K. El razonamiento **emerge con la escala + CoT**. |
| **Takeshi Kojima et al.** (2022) | *Large Language Models are Zero-Shot Reasoners* — NeurIPS 2022 | **Zero-shot CoT**: basta anteponer *"pensemos paso a paso"* ("Let's think step by step"), **sin ejemplos**, para disparar razonamiento. Una frase, gran salto. |
| **Denny Zhou et al.** (2022) | *Least-to-Most Prompting Enables Complex Reasoning in LLMs* — arXiv:2205.10625 | **Descomposición**: dividir un problema complejo en una lista de subproblemas **ordenados** y resolverlos en secuencia, cada uno usando los previos. Supera a CoT en tareas más difíciles que los ejemplos: **generaliza mejor**. |
| **Xuezhi Wang et al.** (2022/2023) | *Self-Consistency Improves Chain of Thought Reasoning* — ICLR 2023 | **Muestreo + voto**: correr varias cadenas de razonamiento y quedarse con la respuesta más frecuente. |

---

## 3. Concepto 1 — Qué es Chain-of-Thought

**Definición:** Chain-of-Thought (CoT) guía al modelo a generar **pasos intermedios de razonamiento** antes de la respuesta final.

**Por qué funciona:** el LLM no "piensa todo de una vez". No es que el modelo "piense" en sentido humano — es que **descomponer hace cada sub-paso más predecible**. Cada paso individual es una predicción de token mucho más restringida (y por tanto más precisa) que intentar saltar directo de la pregunta a la respuesta final.

### Ejemplo canónico: 23 × 17

| Método | Resultado |
|---|---|
| **Directo** | $391$ → puede fallar si el modelo no descompone internamente |
| **Con CoT** | ver desarrollo abajo → **Respuesta final: 391** |

$$23 \times 17 = 23 \times 10 + 23 \times 7 = 230 + 161 = 391$$

Ambos pueden llegar al mismo resultado si aciertan, pero con CoT **el camino es verificable**: si hubiera un error, se sabe exactamente en qué paso ocurrió. Esta es la diferencia que importa para producción — no la respuesta en sí, sino la posibilidad de auditarla.

> **Ejercicio e1 del curso (zero-shot vs. zero-shot-CoT):** tomar un problema multietapa, correrlo directo y luego con "pensemos paso a paso" (Kojima). Criterio de éxito: (a) ≥2 pasos intermedios, (b) cada paso atómico y verificable, (c) la respuesta final aparece etiquetada y separable del razonamiento.

---

## 4. Concepto 2 — Zero-shot CoT vs. Few-shot CoT

Son **dos formas distintas de inducir el mismo razonamiento**, y elegir entre ellas es una decisión de diseño, no un empate:

| | **Zero-shot CoT (Kojima)** | **Few-shot CoT (Wei)** |
|---|---|---|
| **Cómo se induce** | Sin ejemplos — solo la frase disparadora *"pensemos paso a paso"* | Se incluyen ejemplos ya resueltos, mostrando su razonamiento paso a paso |
| **Cuándo usarlo** | Para **desbloquear rápido** el razonamiento sin preparar nada | Cuando necesitas que los pasos salgan con una **estructura fija** (el formato de salida importa) |
| **Regla mnemotécnica** | velocidad → zero-shot | estructura → few-shot |

**Ejemplo few-shot CoT (2 exemplars):**

```text
P: ¿Cuánto es 12 + 15?
R: Primero 10 + 15 = 25. Luego agrego 2 → 27. Respuesta final: 27.

P: ¿Cuánto es 28 + 39?
R: Primero 20 + 39 = 59. Luego agrego 8 → 67. Respuesta final: 67.

P: ¿Cuánto es 35 + 46?
R: ____   # el modelo imita el patrón Y el formato "Respuesta final: N"
```

> **Ejercicio e2:** para una tarea con formato de pasos deseado, escribir 2 exemplars resueltos con su razonamiento y pedir el caso nuevo. Criterio: (a) 2 ejemplos con pasos, (b) formato de respuesta final consistente, (c) el caso a resolver NO está entre los ejemplos.

> **Vínculo directo con la Clase 5:** esto es exactamente la Táctica 4 (few-shot) del Principio 1, aplicada específicamente para inducir un *patrón de razonamiento*, no solo un patrón de formato de salida.

---

## 5. Concepto 3 — Least-to-Most: descomposición en subproblemas

Este es, según el propio material del curso, **el corazón del objetivo de la sesión**: generar respuestas complejas paso a paso.

**Definición:** la clave es **descomponer**. En vez de resolver todo de una vez o solo mostrar pasos (como CoT), Least-to-Most **planifica** una lista de subproblemas ordenados y los resuelve en secuencia, donde cada uno se apoya en el resultado del anterior.

**Por qué funciona (tres razones):**
1. Descompone lo complejo → cada subproblema es mucho más fácil de acertar que el todo.
2. Cada subpaso **se apoya** explícitamente en el previo.
3. **Generaliza** a tareas más difíciles que los ejemplos del prompt, porque enseña a *descomponer*, no a *imitar un patrón fijo* — esto es lo que lo distingue de few-shot CoT.

> **Diferencia clave con CoT:** CoT **muestra** los pasos de razonamiento; Least-to-Most los **planifica** como subproblemas explícitos antes de resolverlos. Uno es narrativo, el otro es arquitectónico.

### Ejemplo del curso: planificación de un taller con restricciones

**Problema:** S/1,000 y 6 horas disponibles; 12 participantes. Cada bloque dura 90 min, la sala cuesta S/200, y se necesita 1 facilitador por cada 4 participantes a S/120/bloque cada uno. ¿Cuántos bloques caben sin pasar el presupuesto ni el tiempo?

Subproblemas ordenados (cada uno usa los previos):

$$S_1:\ \text{facilitadores por bloque} = \left\lceil \frac{12}{4} \right\rceil = 3$$

$$S_2:\ \text{costo por bloque} = 200 + 3 \times 120 = 560 \quad (\text{usa } S_1)$$

$$S_3:\ \text{bloques que caben en 6h} = \frac{360}{90} = 4$$

$$S_4:\ \text{bloques según presupuesto} = \left\lfloor \frac{1000}{560} \right\rfloor = 1 \quad (\text{usa } S_2)$$

$$S_5:\ \text{componer} = \min(4,\,1) = 1 \text{ bloque};\ \text{costo } 560;\ \text{sobra } 440 \quad (\text{usa } S_3, S_4)$$

**Respuesta final:** 1 bloque, S/560 gastados, S/440 de margen.

El error típico "a ojo" es olvidar que **el cuello de botella real es el presupuesto**, no el tiempo — algo que solo aparece al descomponer explícitamente en subproblemas y compararlos.

> **Ejercicio e3 (ESTRELLA del curso):** resolver un problema complejo (a) listando los subproblemas en orden, (b) resolviéndolos uno a uno reusando los previos, (c) componiendo la respuesta final. Criterio: ¿descompuso en subproblemas? ¿los resolvió EN ORDEN reusando los previos? ¿la respuesta final es correcta y completa?

---

## 6. Concepto 4 — Self-Consistency: votar para elegir la mejor respuesta

**Definición:** muestreo. Correr el mismo prompt CoT **varias veces** (con temperatura > 0) y quedarse con la respuesta que aparece con más frecuencia (**voto mayoritario**).

**Por qué funciona:** un problema multietapa tiene muchos caminos de razonamiento correctos que convergen en la **misma** respuesta, mientras que los errores son **idiosincráticos** y se dispersan aleatoriamente. Si varias cadenas independientes llegan al mismo número, esa respuesta es probablemente correcta — **los errores aleatorios no se ponen de acuerdo entre sí**.

Es la primera palanca del curso para **elegir la mejor respuesta compleja**: generar varias y quedarse con la que más se repite.

### Ejemplo del curso: self-consistency en el problema del carrito

```
Mismo prompt CoT, corrido 5 veces con temperatura ~0.7:
 cadena 1 → S/ 1,084.52
 cadena 2 → S/ 1,084.52
 cadena 3 → S/ 1,056.20   (cayó en el error común)
 cadena 4 → S/ 1,084.52
 cadena 5 → S/ 1,084.52

 VOTO MAYORITARIO = S/ 1,084.52   (4 de 5)
 → una sola corrida pudo errar; el voto lo corrige.
```

> **Ejercicio e4:** correr el mismo prompt CoT N=5 veces, extraer la respuesta de cada una y aplicar voto mayoritario. Criterio: (a) ≥3 muestras, (b) respuesta más frecuente reportada, (c) se reporta la dispersión (cuántas coincidieron).

> **Costo real de esta técnica:** self-consistency multiplica el costo por N (5 corridas = 5x el gasto en tokens de salida). Es una palanca de **calidad**, no gratis — hay que reservarla para decisiones donde el error tiene consecuencias reales (cálculos financieros, decisiones legales, extracción crítica), no aplicarla por defecto a todo.

---

## 7. Concepto 5 — Cuándo NO usar CoT (el matiz más importante de la clase)

Este es, junto con Least-to-Most, uno de los puntos más valiosos de la sesión porque corrige un instinto común: pensar que "más razonamiento siempre es mejor".

**Tres situaciones donde omitir CoT:**

| Situación | Por qué omitirlo |
|---|---|
| **Tarea simple/directa** (clasificación trivial, dato factual) | El razonamiento agrega **ruido** y puede degradar la respuesta |
| **Importan coste y latencia** | Más pasos = más tokens de salida = más caro y más lento |
| **Modelo pequeño** | Tiende a generar pasos incoherentes que **arrastran** el error en vez de corregirlo — el beneficio de CoT escala con el tamaño del modelo (hallazgo original de Wei et al.) |

> **La pregunta correcta no es "¿uso CoT?" sino "¿este problema tiene sub-pasos donde puedo equivocarme?"**

### El reverso de la medalla: CoT no garantiza verdad

Los mismos mecanismos que ayudan en problemas multietapa se vuelven **costo puro** cuando no hay etapas que descomponer. CoT no es una bala de plata: **un paso erróneo contamina todo el resultado final**, porque cada paso es el input del siguiente.

```
Clasifica este ticket             El carrito con descuentos + IGV + cupón
Email del cliente                 S/ 1,200
     ↓                              ↓ (−20%)
  [Modelo]                        S/ 960   ← input del siguiente paso
     ↓                              ↓ (−10% sobre 960, no sobre 1200)
 spam / no spam                  S/ 864   ← input del siguiente paso
                                    ↓ (×1.18 IGV)
                                 S/ 1,019.52 ← input del siguiente paso
                                    ↓ (−50 cupón)
                                 S/ 969.52
```

La diferencia real: clasificar un email es una tarea de **un solo salto** (no hay encadenamiento de números que dependan unos de otros); el carrito es una **cadena de dependencias** donde cada número alimenta al siguiente. CoT ayuda en el segundo caso, no en el primero.

> **Ejercicio e5:** dadas 5 tareas (clasificar email, ROI con retenciones, capital de Francia, sprint con dependencias, traducir oración simple), marcar "CoT sí/no" con justificación en ≤1 línea, nombrando el tradeoff de coste al menos una vez.

---

## 8. Concepto 6 — Trazabilidad y auditoría del rastro

**Qué es el "rastro":** la salida explícita de los pasos intermedios que produce CoT. Su valor tiene tres componentes:

1. **Verificar** — ¿cada paso es correcto?
2. **Depurar** — ¿en qué paso se rompió la lógica?
3. **Confiar** — se detectó el error en vez de aceptar un número a ciegas.

> **Conexión explícita con la Clase 5:** esto es el "formato de salida verificable" del contrato I/O, pero aplicado al **proceso**, no solo al resultado final. Convierte una caja negra en un objeto auditable.

### El trade-off de tokens (el precio de la trazabilidad)

Las APIs cobran por token, y CoT infla la salida:

$$\text{Costo} \approx \frac{\text{tokens}_{\text{entrada}}}{10^6} \times \text{Precio}_{\text{in}} \;+\; \frac{\text{tokens}_{\text{salida}}}{10^6} \times \text{Precio}_{\text{out}}$$

| | Tokens de salida | Resultado |
|---|---|---|
| **Directo** | ~30 tokens | barata, MAL resultado |
| **Con CoT** | ~300 tokens | ~10× más cara en salida, resultado CORRECTO y AUDITABLE |

Para una tarea como facturación, esos ~270 tokens extra son **el seguro más barato disponible**. Mitigaciones concretas que sugiere el curso:
- No pedir CoT donde no aporta (ver §7).
- Pedir solo la respuesta final cuando no necesitas el rastro para auditoría.
- Cachear prefijos repetidos (relevante en APIs con *prompt caching*, como la de Anthropic).

> **Ejercicio e6:** se entrega una cadena CoT del carrito **con un error inyectado**. Criterio: (a) señala el paso erróneo exacto, (b) explica por qué es un error, (c) recalcula el resultado final correcto desde ese paso en adelante. Esto es, literalmente, el ejercicio de "auditar un agente" en miniatura.

---

## 9. Complemento del curso — elegir la mejor respuesta comparando modelos

Además de self-consistency (votar dentro de un mismo modelo), el curso propone una **vía complementaria**: comparar entre modelos distintos usando una rúbrica de 4 ejes.

| Eje | Qué evalúa | Prioridad |
|---|---|---|
| 1. Corrección | ¿La respuesta es correcta? | **Eliminatorio** |
| 2. Fidelidad de pasos | ¿El razonamiento mostrado es consistente y no se auto-contradice? | — |
| 3. Claridad | ¿El rastro es legible y fácil de auditar? | — |
| 4. Coste | Tokens y latencia consumidos | — |

**Principio:** no se busca "el modelo más grande", sino **el mejor por corrección/coste** — la misma lógica de retornos decrecientes que rige el diseño de agentes en producción.

Herramientas de apoyo mencionadas (no-code, siguen siendo válidas en 2026): Google AI Studio Compare, LMArena Side-by-Side, Anthropic Console Evaluate.

> **Ejercicio e7 (complementario):** correr el mismo problema, directo vs. CoT, en 2-3 modelos distintos; llenar la tabla con la rúbrica y declarar un ganador **por tarea** (no un ganador absoluto).

---

## 10. Demos trabajadas del curso (tres casos íntegros)

### 10.1 Descuentos + IGV (orden de operaciones)

Carrito con cámara S/1,200 (−20% y luego −10% adicional), libro S/90 (exento IGV), envío S/25 (sin IGV), IGV 18%, cupón −S/50 al final. Orden fijo: descuentos → impuestos → cupón.

**Error común:** aplicar $20\% + 10\% = 30\%$ de golpe (en vez de descuentos secuenciales):

$$1200 \times (1 - 0.30) = 840 \quad\Rightarrow\quad 840 \times 1.18 = 991.20 \quad\Rightarrow\quad 991.20 + 90 + 25 - 50 = \mathbf{1{,}056.20} \ \ (\text{incorrecto})$$

**Con CoT (paso a paso):**

$$1200 \xrightarrow{-20\%} 960 \xrightarrow{-10\%} 864$$

$$864 \times 1.18 = 1{,}019.52 \quad (\text{IGV solo a la cámara; libro y envío exentos})$$

$$1{,}019.52 + 90 + 25 = 1{,}134.52 \quad \text{(subtotal)}$$

$$1{,}134.52 - 50 = \mathbf{1{,}084.52} \quad \text{(menos cupón)}$$

### 10.2 Cajas mal rotuladas (deducción por casos)

Tres cajas etiquetadas "Manzanas", "Naranjas", "Mezcla" — **todas** las etiquetas están mal. Sacas una sola fruta de una sola caja.

```
1) Saca de la rotulada "Mezcla": no puede ser mezcla (todas mal) → es manzana o naranja pura.
2) Si sale manzana → esa caja es "Manzanas" (la caja, no la etiqueta).
3) La rotulada "Manzanas" no puede ser manzanas ni mezcla → tiene que ser "Naranjas".
4) La restante es "Mezcla".
```

El razonamiento por casos **encadena deducciones**; sin descomponerlo explícitamente, el modelo tiende a adivinar en vez de deducir.

### 10.3 Tasa de producción (restricción oculta)

3 máquinas hacen 72 piezas en 6h; cada máquina para 30 min de mantenimiento cada 4h. ¿Cuántas horas necesitan 5 máquinas para hacer 300 piezas?

**Error común:** asumir 4 piezas/h sin paradas:

$$\frac{300}{5 \times 4} = 15\text{h} \quad (\text{incorrecto — ignora el mantenimiento})$$

**Con CoT (paso a paso):**

$$\text{tasa base} = \frac{72}{3 \times 6} = 4 \ \text{piezas/h por máquina}$$

$$\text{con mantenimiento, ciclo real} = 4.5\text{h} \;\Rightarrow\; \frac{4 \times 4}{4.5} \approx 3.56 \ \text{piezas/h por máquina}$$

$$5 \text{ máquinas} \approx 5 \times 3.56 = 17.78 \ \text{piezas/h}$$

$$\frac{300}{17.78} \approx 16.875\text{h} \;\Rightarrow\; \mathbf{17\text{h}} \ (\text{redondeando al bloque de 30 min})$$

Las restricciones ocultas (el mantenimiento) cambian el resultado real; CoT las saca a la luz porque obliga a enumerar explícitamente todos los factores antes de calcular.

---

## 11. Frontera — hacia dónde sigue (mención, no profundizado en esta clase)

El material señala explícitamente dos técnicas que están más allá del alcance de esta sesión, como puente hacia la Clase 7 (agentes):

| Técnica | Qué es | Por qué es la frontera |
|---|---|---|
| **Tree of Thoughts** (Yao et al., 2023) | Explorar **varias ramas** de razonamiento en paralelo y podar (búsqueda sobre pensamientos), no una sola cadena ni una secuencia lineal de subproblemas | Generaliza CoT de una cadena lineal a un **árbol de búsqueda** con backtracking |
| **ReAct** (razonar + actuar) | Intercalar pasos de razonamiento con **acciones/herramientas** reales | Es exactamente el puente al agente: el modelo no solo piensa, también actúa y observa el resultado de esa acción antes de seguir pensando |

> Nota curricular: Least-to-Most **ya no es frontera** en este punto del curso — fue el Concepto 3, el corazón del objetivo de la sesión. Solo Tree of Thoughts y ReAct quedan como horizonte para más adelante.

### 11.1 Investigación complementaria — profundizando Tree of Thoughts y ReAct

Estas dos técnicas no se explican en detalle en el material (son solo mencionadas como frontera), así que vale la pena ampliarlas porque son las que efectivamente vas a usar al construir agentes:

**Tree of Thoughts (ToT)** — Yao, Yu, Zhao, Shafran, Griffiths, Cao, Narasimhan (NeurIPS 2023, arXiv:2305.10601):
- Generaliza CoT permitiendo que el modelo explore **múltiples caminos de razonamiento** ("thoughts") como nodos de un árbol, autoevaluando cada rama y decidiendo si seguir explorándola, retroceder (backtrack) o abandonarla.
- Usa algoritmos de búsqueda estándar (BFS o DFS) sobre ese árbol de pensamientos.
- Resultado citado: en el juego "Game of 24", GPT-4 con CoT resolvía solo el 4% de los problemas; con ToT, el éxito subió a **74%**. Es la evidencia de que para problemas que requieren planificación real (no solo una secuencia de cálculos), una sola cadena lineal no basta.
- Relevancia para agentes: cuando un agente debe **planificar** una secuencia de acciones con incertidumbre sobre cuál es el mejor camino (por ejemplo, qué estrategia de búsqueda seguir, o qué orden de sub-tareas resolver primero), ToT es el marco conceptual detrás de arquitecturas de agentes que exploran y comparan planes antes de comprometerse con uno.

**ReAct (Reason + Act)** — Yao et al. (2022):
- Intercala pasos de **Thought → Action → Observation**: el modelo genera un pensamiento interno, ejecuta una acción (llamar una herramienta, hacer una búsqueda, ejecutar código), observa el resultado real de esa acción, y continúa razonando con esa nueva información.
- Esto es literalmente cómo funciona el bucle de un agente moderno con *tool use*: el modelo no solo predice texto — alterna entre pensar y actuar en el mundo real, actualizando su plan según lo que efectivamente descubre.
- Diferencia clave con CoT puro: CoT razona sobre lo que el modelo *ya sabe*; ReAct permite que el modelo **descubra información nueva** a través de acciones y ajuste su razonamiento en consecuencia — esto reduce la alucinación porque el modelo puede verificar hechos externamente en vez de inventarlos.

---

## 12. Puente explícito hacia el agente (Clase 7)

Esta es la sección que conecta directamente esta sesión con tu objetivo de construir agentes.

> **Cita textual del curso:** *"Lo que hoy aprendimos a inducir a mano (CoT) será el MOTOR DE DECISIÓN del agente de la Clase 7: razona paso a paso para decidir qué herramienta invocar."*

```
Input → [Razonamiento paso a paso] → [Agente decide: tool / db / web] → Output
```

Puente citado con la guía de OpenAI (*A practical guide to building agents*): las frases *"make decisions"* / *"selects tools"* que describen la capacidad de decisión de un agente son, en el fondo, **razonamiento** — y CoT es el mecanismo concreto que lo implementa cuando el modelo decide qué acción tomar a continuación.

### 12.1 Los tres movimientos de razonamiento que hay que llevarse

El propio material cierra con esta síntesis operativa:

1. **Forzar los pasos** — donde el problema tiene sub-pasos en los que puedes equivocarte, pide CoT zero-shot ("pensemos paso a paso") o few-shot (ejemplos con razonamiento).
2. **Descomponer lo complejo** — ante un problema genuinamente complejo, usa Least-to-Most: lista los subproblemas ordenados y resuélvelos en secuencia reusando los previos.
3. **Votar y auditar** — para la mejor respuesta, vota varias cadenas (self-consistency). El rastro permite verificar y depurar; compara entre modelos con rúbrica si hace falta.

---

## 13. Investigación complementaria: cómo evolucionó esto en los modelos de 2026

Esta sección no está en el PDF, pero es directamente relevante para cuando implementes estas técnicas con Claude hoy en vez de con los modelos de 2022 sobre los que se escribieron estos papers.

### 13.1 De CoT manual a "adaptive thinking"

En 2022 (cuando se publicaron Wei, Kojima, Zhou y Wang), forzar el razonamiento requería **escribir explícitamente** en el prompt la frase disparadora ("pensemos paso a paso") o incluir ejemplos con pasos. Los modelos actuales de Claude (Sonnet 5, Opus 4.8, Fable 5/Mythos 5) incorporan esto de forma nativa mediante **adaptive thinking**: el modelo decide internamente cuánto y cómo razonar, calibrado por dos factores — el parámetro `effort` (bajo/medio/alto) que tú controlas, y la complejidad que el propio modelo detecta en la consulta.

Esto no vuelve obsoleto lo aprendido en esta sesión — al contrario, lo hace más importante entender **cuándo** conviene ese razonamiento, porque ahora es una perilla (`effort`) que tú calibras en vez de una frase que escribes a mano. La pregunta del Concepto 5 ("¿este problema tiene sub-pasos donde puedo equivocarme?") sigue siendo exactamente la que determina si subes o bajas el `effort`.

Anthropic documenta explícitamente el mismo matiz del Concepto 5 de este curso, con las mismas palabras: *"Extended thinking adds latency and should only be used when it will meaningfully improve answer quality — typically for problems that require multi-step reasoning. When in doubt, respond directly."*

### 13.2 CoT manual como fallback

El CoT manual explícito ("pensemos paso a paso", con tags `<thinking>` y `<answer>` separados) **sigue siendo relevante** en dos escenarios concretos según la documentación actual de Anthropic:
- Cuando el *thinking* nativo está desactivado y necesitas razonamiento estructurado igualmente.
- Cuando quieres **auditar** el razonamiento de forma explícita y separada de la respuesta final — exactamente el mismo argumento del Concepto 6 de esta sesión (trazabilidad).

### 13.3 Self-consistency y "best-of-N" en producción

La técnica de self-consistency (Wang et al.) del Concepto 4 tiene un equivalente directo en la práctica moderna de agentes: los patrones de **"best-of-N sampling"** o **verificadores externos**, donde se generan N soluciones candidatas y se elige la mejor mediante un criterio de selección (votación, un modelo evaluador, o tests automáticos). La diferencia con 2022 es que hoy este patrón se implementa frecuentemente con **subagentes en paralelo** (cada uno explorando una hipótesis o solución distinta) que devuelven un resumen condensado, en vez de N llamadas idénticas a la misma API — es una versión más rica de la misma idea: múltiples caminos independientes, y una regla de consenso para elegir el resultado final.

### 13.4 ReAct como el patrón de fondo de todo agente con tools

Lo que el material de esta sesión señala como "frontera" (ReAct) es, en 2026, el patrón de facto de cualquier agente construido sobre un modelo con *tool use*: Claude native alterna razonamiento interno (a veces visible como *thinking*, a veces implícito) con llamadas a herramientas y observación de resultados, exactamente el ciclo Thought→Action→Observation. La guía de Anthropic sobre *"long-horizon reasoning"* (ver documento de la Clase 5) describe este mismo patrón para tareas que abarcan múltiples ventanas de contexto: el agente razona, actúa (usa una tool), observa el resultado, y ajusta su plan — sin que el desarrollador tenga que escribir manualmente el bucle ReAct, porque ya está incorporado en cómo el modelo usa las herramientas de forma nativa.

---

## 14. Ejercicios de la sesión (mapa completo)

| Ejercicio | Técnica que aísla | Criterio de éxito |
|---|---|---|
| **e1** — Zero-shot vs. zero-shot-CoT | Concepto 1 (CoT básico) | ≥2 pasos intermedios, cada paso atómico y verificable, respuesta final etiquetada y separable |
| **e2** — Few-shot CoT (2 exemplars) | Concepto 2 | 2 ejemplos con pasos, formato de respuesta final consistente, el caso a resolver no está entre los ejemplos |
| **e3** (ESTRELLA) — Least-to-Most | Concepto 3 | Descompuso en subproblemas, los resolvió en orden reusando los previos, respuesta final correcta y completa |
| **e4** — Self-consistency | Concepto 4 | ≥3 muestras, respuesta más frecuente reportada, se reporta la dispersión (cuántas coincidieron) |
| **e5** — Cuándo NO usar CoT | Concepto 5 | 5 tareas evaluadas con "CoT sí/no" + justificación ≤1 línea, nombrando el tradeoff de coste al menos una vez |
| **e6** — Auditar la cadena | Concepto 6 | Señala el paso erróneo exacto, explica por qué, recalcula el resultado correcto desde ese paso |
| **e7** (complementario) — Comparar modelos | §9 (rúbrica de 4 ejes) | Mismo problema directo vs. CoT en 2-3 modelos, tabla con rúbrica, ganador declarado por tarea |

> **Por qué este mapa importa para agentes:** el ejercicio e6 (auditar una cadena con un error inyectado) es, en miniatura, exactamente la habilidad que necesitarás para depurar el *trace* de razonamiento de un agente en producción cuando falla — saber señalar el paso exacto donde se rompió la lógica, no solo que "algo salió mal".

---

## 15. Quiz de la sesión (con respuestas)

| # | Pregunta | Respuesta correcta |
|---|---|---|
| 1 | ¿Qué describe mejor a Chain-of-Thought (CoT)? | **B** — Inducir al modelo a mostrar pasos intermedios de razonamiento antes de la respuesta |
| 2 | La frase gatillo del zero-shot-CoT (Kojima et al., 2022) es... | **B** — "Pensemos paso a paso" ("Let's think step by step") |
| 3 | ¿Qué técnica resuelve un problema complejo descomponiéndolo en subproblemas ordenados? | **B** — Least-to-Most prompting (Zhou et al., 2022) |
| 4 | Self-consistency (Wang et al., 2022) consiste en... | **B** — Muestrear varias cadenas de razonamiento y quedarse con la respuesta por voto mayoritario |
| 5 | ¿Cuándo conviene NO aplicar CoT? | **C** — En tareas simples/directas donde solo añade ruido, coste y latencia |

---

## 16. Síntesis: lo que hay que llevarse de esta sesión

1. **CoT (Wei, 2022)** — pedir pasos intermedios visibles antes de la respuesta final mejora la corrección en tareas multietapa. No es que el modelo "piense": descomponer hace cada sub-paso más predecible.
2. **Zero-shot vs. Few-shot CoT** — dos formas de inducir razonamiento: el disparador "pensemos paso a paso" (Kojima, sin ejemplos, para velocidad) o los ejemplos resueltos que el modelo imita (Wei, para estructura fija).
3. **Least-to-Most (Zhou, 2022)** — para problemas genuinamente complejos: primero descomponer en subproblemas ordenados, luego resolverlos en secuencia reusando cada resultado previo. Generaliza mejor que CoT porque enseña a descomponer, no a imitar.
4. **Self-consistency (Wang, 2022)** — correr el mismo prompt N veces y tomar la respuesta por voto mayoritario. Los errores idiosincrásicos se dispersan; los caminos correctos convergen.
5. **Cuándo NO usar CoT** — si la tarea no tiene sub-pasos donde puedas equivocarte (dato factual, clasificación directa), CoT solo añade ruido, tokens y latencia. La pregunta correcta es "¿este problema tiene sub-pasos?", no "¿debería usar CoT siempre?".
6. **El rastro auditable** — la cadena de pasos que CoT produce permite verificar cada paso, depurar dónde se rompió la lógica, y confiar en el resultado. Es el fundamento del *gate* entre pasos de un pipeline de agentes.
7. **Puente a agentes:** lo aprendido hoy a inducir manualmente (CoT) es el motor de decisión que un agente usa internamente para decidir qué herramienta invocar — la frontera (Tree of Thoughts, ReAct) es hacia donde evoluciona esto cuando el razonamiento se combina con acciones reales sobre el mundo.
8. *(Complemento 2026)* En los modelos actuales, buena parte de este razonamiento ya es nativo (*adaptive thinking*), pero el criterio para decidir cuándo activarlo — o cuánto `effort` asignarle — es exactamente el mismo criterio del Concepto 5: ¿el problema tiene sub-pasos donde el modelo puede equivocarse?

---

## 17. Cómo aplicar esto cuando construyas tus propios agentes — checklist práctico

**Decisión de cuándo forzar razonamiento:**
- [ ] ¿La tarea tiene sub-pasos donde el modelo puede equivocarse (cálculos encadenados, dependencias entre datos, restricciones ocultas)? → forzar razonamiento (CoT o subir `effort`).
- [ ] ¿Es una clasificación directa, un dato factual, o una tarea de un solo salto? → NO forzar razonamiento; el coste/latencia no se justifica.
- [ ] ¿Estoy optimizando por velocidad o por estructura de salida? → zero-shot CoT para velocidad, few-shot CoT si necesito un formato de pasos específico y repetible.

**Diseño de la descomposición:**
- [ ] Para problemas complejos con múltiples restricciones (presupuesto + tiempo + recursos, como el ejemplo del taller), ¿estoy pidiendo explícitamente que se listen subproblemas ORDENADOS antes de resolver? (Least-to-Most, no solo CoT narrativo.)
- [ ] ¿Cada subproblema declara explícitamente qué resultado previo reutiliza?

**Verificación de calidad de la respuesta:**
- [ ] Para decisiones de alto riesgo (cálculos financieros, extracción legal, decisiones irreversibles de un agente), ¿vale la pena pagar el costo de self-consistency (N corridas + voto)?
- [ ] Si no puedo pagar N corridas completas, ¿tengo al menos un paso de autoverificación ("verifica tu respuesta contra estos criterios antes de terminar")?

**Auditoría y depuración (crítico para debug de agentes):**
- [ ] ¿El razonamiento del agente queda registrado en algún lugar auditable (log, trace, `<thinking>` visible) para poder depurar fallos después?
- [ ] Cuando un agente falla, ¿tengo el hábito de identificar el paso exacto donde se rompió la lógica, en vez de solo regenerar la respuesta completa?

**Costo y latencia:**
- [ ] ¿Calculé el costo aproximado del razonamiento extendido (tokens de salida ×10 o más) frente al valor de tener una respuesta auditable?
- [ ] Si el agente corre en un flujo de alto volumen, ¿tengo un mecanismo para aplicar razonamiento solo condicionalmente (solo cuando la tarea lo amerita), no por defecto en cada llamada?

**Hacia arquitecturas más ricas (frontera):**
- [ ] Si el agente necesita planificar entre múltiples estrategias posibles (no solo calcular una cadena de pasos), ¿considero un patrón tipo Tree of Thoughts (explorar y comparar ramas) en vez de una sola cadena lineal?
- [ ] Si el agente necesita descubrir información nueva del entorno antes de poder razonar correctamente, ¿el patrón ReAct (razonar → actuar → observar → seguir razonando) está bien soportado por mis herramientas y por cómo estructuro el bucle del agente?

---

## 18. Referencias

**Del material original:**
- Wei, J. et al. — *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. arXiv:2201.11903 (2022); NeurIPS 2022.
- Kojima, T. et al. — *Large Language Models are Zero-Shot Reasoners*. NeurIPS 2022.
- Zhou, D. et al. — *Least-to-Most Prompting Enables Complex Reasoning in Large Language Models*. arXiv:2205.10625 (2022).
- Wang, X. et al. — *Self-Consistency Improves Chain of Thought Reasoning in Language Models*. ICLR 2023.
- Ng, A. & Fulford, I. — *ChatGPT Prompt Engineering for Developers* (DeepLearning.AI + OpenAI). Principio 2: dar tiempo a pensar.
- OpenAI — *A practical guide to building agents* ("make decisions" / "selects tools" = razonamiento; CoT como motor de decisión).
- Yao, S. et al. — *Tree of Thoughts: Deliberate Problem Solving with Large Language Models*. arXiv:2305.10601 (2023); NeurIPS 2023. (Mención de frontera en el curso.)
- Yao, S. et al. — *ReAct: Synergizing Reasoning and Acting in Language Models* (2022). (Mención de frontera en el curso.)

**Investigación complementaria (añadida en este documento, julio 2026):**
- Anthropic — *Prompting best practices* (Claude Platform Docs), sección "Thinking and reasoning" / adaptive thinking. https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Princeton NLP — repositorio y paper completo de Tree of Thoughts. https://github.com/princeton-nlp/tree-of-thought-llm
- IBM — *What is a ReAct Agent?* (explicación del patrón Thought-Action-Observation). https://www.ibm.com/think/topics/react-agent

---

*Documento generado a partir del PDF de la Sesión 6 (Módulo 3, UTEC Posgrado) más investigación propia sobre ReAct, Tree of Thoughts, y la evolución del razonamiento inducido por prompt hacia el "adaptive thinking" nativo de los modelos actuales. Última actualización: 2026-07-07.*
