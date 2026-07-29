# Clase 6 · Ejercicios — Razonamiento mediante prompts (Chain-of-Thought)

Estos ejercicios bajan a la práctica el objetivo de la Clase 6: **generar respuestas complejas
usando razonamiento paso a paso**. Pedirle al modelo que **piense paso a paso antes de responder** —y,
cuando el problema es genuinamente complejo, **descomponerlo en subproblemas ordenados**— mejora la
calidad en tareas de varios pasos y deja un **rastro auditable**. El hilo de la Clase 5 (el **prompt
como contrato verificable**) sigue vivo, pero ahora verificamos también el *proceso*, no solo el
*resultado*.

Cada ejercicio es **ejecutable tal cual** en ChatGPT, Claude o Gemini: pegas el contenido de
`prompt-plantilla.md` (sustituyendo el bloque de input por el archivo indicado) y comparas la salida
contra el `criterio.md`. El estrella, **e3 (Least-to-Most)**, alinea con el objetivo: generar una
respuesta compleja descomponiéndola en subproblemas ordenados. El **e7 (evaluar modelos)** pasa a ser
**complementario** (palanca de calidad de apoyo), y se trabaja en herramientas **no-code** (Google AI
Studio Compare / LMArena Side-by-Side / Anthropic Console Evaluate) con un Colab opcional.

> El número `eN` sigue el **orden de dictado en el deck** (no una jerarquía conceptual).

| # | Carpeta | Concepto / fuente | Qué entrena |
|---|---------|-------------------|-------------|
| e1 | `e1-zeroshot-vs-cot/` | Zero-shot vs zero-shot-CoT (Kojima 2022) | Ver el salto: prompt directo vs "pensemos paso a paso" |
| e2 | `e2-fewshot-cot/` | Few-shot CoT (Wei 2022) | Construir 2 exemplars resueltos con pasos + formato fijo |
| e3 | `e3-least-to-most/` | **ESTRELLA** · Least-to-Most (Zhou 2022) | Descomponer un problema complejo en subproblemas ordenados y componer la respuesta |
| e4 | `e4-self-consistency/` | Self-consistency (Wang 2022) | Correr N=5 cadenas (temp>0) + voto mayoritario |
| e5 | `e5-cuando-no-cot/` | Cuándo NO usar CoT (matiz crítico) | Clasificar 5 tareas CoT sí/no + nombrar el tradeoff |
| e6 | `e6-auditar-cadena/` | Trazabilidad y auditoría | Hallar el paso erróneo en una cadena y recalcular |
| e7 | `e7-evaluar-modelos/` | **COMPLEMENTARIO** · Evaluar modelos con rúbrica | Directo vs CoT en 2–3 modelos, rúbrica de 4 ejes, ganador por tarea |

## Cómo trabajarlos
1. Abre la carpeta del ejercicio.
2. Lee el/los archivo(s) de **input** (`.md`).
3. Copia `prompt-plantilla.md` y pega dentro el input donde dice `{...}` o entre los delimitadores
   `<...></...>`.
4. Ejecútalo en el modelo de tu elección. En e4 (y opcionalmente en e3), súbele la **temperatura**
   (~0.7) y córrelo varias veces. En e7, usa las herramientas no-code (ver su `INSTRUCCIONES.md`).
5. Evalúa la salida con `criterio.md` (o `rubrica-comparacion.md` en e7): **todo criterio es
   binario** — cumple o no.

## El canon de la clase (citar bien)
- **Wei et al. 2022** — *Chain-of-Thought Prompting…* (arXiv 2201.11903, NeurIPS 2022): few-shot CoT.
- **Kojima et al. 2022** — *LLMs are Zero-Shot Reasoners* (NeurIPS 2022): "pensemos paso a paso".
- **Zhou et al. 2022** — *Least-to-Most Prompting…* (arXiv 2205.10625): descomponer en subproblemas
  ordenados resueltos en secuencia; generaliza mejor que CoT.
- **Wang et al. 2022** — *Self-Consistency…* (ICLR 2023): varias cadenas + voto mayoritario.
- **Ng & Fulford** — *ChatGPT Prompt Engineering for Developers*: Principio 2, "dar tiempo a pensar".

## Regla de oro de la clase
> El objetivo es GENERAR respuestas complejas correctas: fuerza el razonamiento (CoT) y descompón lo
> complejo en subproblemas ordenados (Least-to-Most). Pero CoT no garantiza la verdad: la cadena es
> tan fuerte como su eslabón más débil. Por eso se vota (self-consistency), se audita (rastro) y, si
> hace falta, se compara con rúbrica — no "a ojo".
