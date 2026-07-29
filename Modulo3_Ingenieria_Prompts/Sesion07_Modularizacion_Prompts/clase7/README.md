# Clase 7 · Ejercicios — Modularización de prompts en agentes (pipelines con contratos y gates)

Estos ejercicios bajan a la práctica el objetivo de la Clase 7: **componer un pipeline de IA en pasos
consecutivos (resumen → traducción → verificación) con contratos y gates — sin código.** La idea
central: **un sistema confiable de IA no es un mega-prompt más inteligente, es una cadena de pasos
pequeños y verificables.** En vez de pedirle a un solo prompt que "resuma, traduzca y verifique de
una vez", **partimos la tarea en una secuencia de pasos donde cada llamada procesa la salida de la
anterior** (*prompt chaining*, Anthropic 2024). Cada paso es un **contrato de I/O**, entre pasos hay
un **gate** que decide `approve | revise | escalate` y **detiene la propagación de errores**, y donde
el riesgo lo amerita se inserta un **humano** (HITL). El hilo de la Clase 5 (el **prompt como
contrato verificable**) y el de la Clase 6 (**razonamiento auditable**) siguen vivos, pero ahora
componemos **varios** contratos en un pipeline.

Y lo más importante para esta clase: **esto se construye sin código.** Encadenar a mano —correr el
paso 1 en el chat, **copiar su salida y pegarla como entrada del paso 2**, y así— **es ya** prompt
chaining. El estrella, **e6 (pipeline manual)**, es exactamente eso. El **Colab con LangChain** es la
vía "pro" **opcional**, no requisito de la clase.

Cada ejercicio es **ejecutable tal cual** en ChatGPT, Claude o Gemini: pegas el contenido de
`prompt-plantilla.md` (sustituyendo el bloque de input por el archivo indicado) y comparas la salida
contra el `criterio.md`. Todo criterio es **binario** — cumple o no.

| # | Carpeta | Concepto / fuente | Qué entrena |
|---|---------|-------------------|-------------|
| e1 | `e1-descomponer-en-pasos/` | Prompt chaining (Anthropic 2024) | Partir un mega-prompt en 2–4 pasos y nombrar el contrato de cada uno |
| e2 | `e2-contrato-y-gate/` | Contrato de I/O + gate | Escribir el JSON de salida de un paso + la regla del gate (approve/revise/escalate) |
| e3 | `e3-workflow-vs-agent/` | Workflows vs Agents (Anthropic 2024) | Clasificar 4 casos según quién dirige el flujo (código fijo vs el LLM) |
| e4 | `e4-guardrails-en-capas/` | Guardrails en capas (taxonomía OpenAI) | Añadir 2 guardrails de categorías distintas a un paso e indicar dónde van |
| e5 | `e5-hitl/` | Human-in-the-loop (OpenAI) | Definir 1 trigger HITL + dónde va el checkpoint + 1 métrica de calibración |
| e6 | `e6-pipeline-manual/` | **ESTRELLA** · Pipeline manual + Colab LangChain | Encadenar a mano resumen → traducción → verificación con gate (+ Colab opcional) |

## Cómo trabajarlos
1. Abre la carpeta del ejercicio.
2. Lee el/los archivo(s) de **input** (`.md` / `.json`).
3. Copia `prompt-plantilla.md` y pega dentro el input donde dice `{...}` o entre los delimitadores
   `<<<...>>>`.
4. Ejecútalo en el modelo de tu elección. En e6 (el estrella) **encadenas a mano**: corres un paso,
   copias su salida y la pegas como entrada del siguiente (ver su `INSTRUCCIONES.md`).
5. Evalúa la salida con `criterio.md` (o `rubrica.md` en e6): **todo criterio es binario**.

## El canon de la clase (citar bien)
- **Schluntz, E. & Zhang, B. (Anthropic) 2024** — *Building Effective Agents* (anthropic.com,
  19-dic-2024). **Fuente principal.** **Prompt chaining** = descomponer una tarea en una secuencia de
  pasos donde **cada llamada al LLM procesa la salida de la anterior**; entre pasos se pueden añadir
  **gates programáticos** (checks). **Workflows** (camino de código predefinido) vs **agents** (el LLM
  dirige dinámicamente el flujo). Filosofía: **empezar por lo más simple** y subir complejidad solo
  cuando mejore el resultado.
- **OpenAI** — *A practical guide to building agents*. **Guardrails como defensa en capas**
  (relevancia, seguridad/jailbreak, PII, moderación, tool safeguards, rules-based, output validation)
  y el recuadro **"Plan for human intervention"** (HITL): dos triggers — **umbral de fallo** y
  **acción de alto riesgo**.
- **LangChain** (Harrison Chase, framework open-source) — una *chain* es una secuencia de pasos
  encadenados (en LangChain moderno se compone con LCEL: `prompt | llm | parser`). **Solo** como la
  **vía de código del Colab opcional** de e6; **no es requisito de la clase**.

## Regla de oro de la clase
> No mejores el mega-prompt: pártelo. Una cadena de pasos pequeños te devuelve **precisión por paso,
> depuración localizada, formato estable y el punto exacto donde meter un humano.** El contrato
> verifica que la salida sea *correcta de forma*; el guardrail, que sea *segura y apropiada*; el gate
> **detiene la propagación de errores**. Y la línea que separa un workflow de un agente es una sola
> pregunta: **¿quién dirige el flujo, un camino de código predefinido o el LLM en tiempo de ejecución?**
