# ¿Agente, workflow o cadena de llamadas a un LLM? — Justificación teórica

Documento de respaldo académico para las 5 versiones del agente personal
(`Tarea_Agente_Personal` v1 a v5, Sesiones 12 y 13). Responde a una pregunta central que el
docente enfatiza en el curso: **¿cuándo vale la pena construir un agente, y qué es exactamente
lo que se construyó aquí?**

Este documento complementa a `EXPLICACION_CODIGO_COMPLETO.md` (qué hace el código) con el
**por qué arquitectónico** (por qué ese código es un agente y no otra cosa).

---

## 1. Marco teórico: "Building Effective Agents" (Anthropic, diciembre 2024)

El material del curso (capturas de patrones como *orquestador → workers → sintetizador* o
*generar_plan → crítica → aprobado/rechazado*) usa exactamente la terminología y los patrones
publicados por Anthropic en su artículo de ingeniería
[**"Building Effective Agents"**](https://www.anthropic.com/research/building-effective-agents)
(diciembre 2024). Esto no es coincidencia de nombres: **"orquestador" + "workers" es literalmente
el nombre que Anthropic le da al patrón *Orchestrator-Workers*", y el flujo con nodo "crítica" que
aprueba o rechaza es el patrón *Evaluator-Optimizer*. Es razonable asumir que el docente construyó
esa parte del curso directamente sobre ese framework.

### 1.1 La distinción central: Workflow vs. Agente

Anthropic define los dos términos de forma precisa y los distingue **por dónde vive el control de
flujo**, no por cuántos pasos tiene el sistema ni cuántas veces se llama a un LLM (*Large Language
Model*, modelo de lenguaje de gran escala — el modelo que genera texto, como Claude o Gemma):

> **Workflows** son "sistemas donde los LLM y las herramientas son orquestados a través de
> caminos de código predefinidos" (*predefined code paths*).
>
> **Agentes** son "sistemas donde los LLM dirigen dinámicamente su propio proceso y el uso de
> herramientas, manteniendo control sobre cómo cumplen la tarea".

La pregunta operativa que se deriva de esto **no es** "¿usa varios pasos?" ni "¿usa tools?" —
un workflow también puede usar muchos pasos y muchas tools. La pregunta es: **¿quién decide, en
tiempo de ejecución, qué paso sigue — el desarrollador (en el código) o el modelo (en cada
respuesta)?**

### 1.2 Los cinco patrones de *workflow* (control fijo por código)

Estos son los patrones que aparecen en las capturas del curso — todos comparten que **el grafo de
pasos ya está decidido antes de correr**, el LLM solo rellena contenido dentro de cada nodo:

| Patrón | Qué hace | Ejemplo en las capturas del curso |
|---|---|---|
| **Prompt Chaining** (encadenamiento de prompts) | Descompone una tarea en pasos secuenciales fijos; la salida de un LLM alimenta al siguiente, con puntos de control programáticos entre etapas. | — |
| **Routing** (enrutamiento) | Clasifica la entrada y la dirige a una rama especializada entre varias predefinidas. | — |
| **Parallelization** (paralelización) | Corre varias llamadas al LLM en simultáneo, por *sectioning* (subtareas independientes) o *voting* (varios intentos para tener más confianza). | `__start__` → (`animal` / `femenino` / `masculino` en paralelo) → `composicion` |
| **Orchestrator-Workers** (orquestador-trabajadores) | Un LLM orquestador central descompone la tarea y delega a LLM "worker" (trabajador), luego sintetiza resultados. | `orquestador` → `workers` → `sintetizador` |
| **Evaluator-Optimizer** (evaluador-optimizador) | Un LLM genera, otro LLM evalúa y da retroalimentación en un bucle de refinamiento hasta que se aprueba. | `generar_plan` → `edicion` → `critica` → (`Aprobado` → `edicion_final` / `Rechazado` → vuelve a intentar) |

En los tres casos de las capturas, **las flechas del grafo (quién llama a quién) están fijas por
diseño**: no existe un mundo donde `workers` decida saltarse `sintetizador`, ni donde `composicion`
decida no esperar a las tres ramas paralelas. Eso es control de flujo en código (o en el grafo de
LangGraph), no en el modelo.

### 1.3 Definición de *agente autónomo*

Sobre los agentes propiamente dichos, Anthropic precisa que:

> Los agentes "comienzan su trabajo con una orden de, o una discusión interactiva con, el usuario
> humano" y luego "planifican y operan de forma independiente, pudiendo regresar al humano para
> pedir más información" — sin que el número de pasos, ni el orden, ni las herramientas usadas
> estén decididos de antemano.

Esto es, técnicamente, el patrón **ReAct** (*Reasoning + Acting* — razonamiento + actuación),
formalizado académicamente antes del artículo de Anthropic en Yao et al., *"ReAct: Synergizing
Reasoning and Acting in Language Models"* (ICLR 2023): el modelo alterna, en el mismo bucle,
entre "pensar" (razonar sobre qué hacer) y "actuar" (invocar una herramienta), observando el
resultado de cada acción antes de decidir la siguiente — hasta que decide que ya puede responder.
`create_agent` de LangChain (usado en las 5 versiones del agente personal) es una implementación
directa de ese bucle ReAct: no es una capa cosmética sobre un grafo fijo, es literalmente el
patrón agente de la teoría.

### 1.4 Principios rectores (por qué "simplicidad primero")

Tres principios que Anthropic remarca, y que son la base de la pregunta del docente sobre "cuándo
vale la pena":

1. **Simplicidad**: "empezar simple, aumentando complejidad solo cuando sea necesario" — agregar
   complejidad (de workflow o de agente) únicamente cuando **demostrablemente** mejora el
   resultado.
2. **Transparencia**: el proceso de razonamiento del sistema debe poder inspeccionarse, no ser
   una caja negra.
3. **Documentación y testing cuidadoso de las herramientas**: la calidad de un agente depende
   tanto de las tools que se le dan como del modelo mismo.

Y la advertencia de costo explícita: los agentes cambian "latencia y costo por mejor desempeño en
la tarea" — usarlos solo cuando "se necesita flexibilidad y toma de decisiones dirigida por el
modelo, a escala". Esta es la frase clave para responder la pregunta del docente: un agente **no
es gratis**, se paga en previsibilidad, en tokens, y en tiempo de respuesta — por eso la decisión
de usarlo debe justificarse, no darse por defecto.

---

## 2. Aplicación al caso: ¿qué es `Tarea_Agente_Personal` (v1–v5)?

### 2.1 Clasificación

Las 5 versiones son, sin ambigüedad, **agentes** según la definición de la sección 1.1 — no
workflows y no una simple cadena secuencial de llamadas al LLM:

- El control de flujo (qué tool llamar, en qué orden, cuántas veces, cuándo detenerse y
  responder) **no está en el código** de `agente_planificacion_*.py`. El código define las
  tools (`consultar_tareas`, `buscar_en_documentos`, `buscar_en_la_web`, `agendar_actividad`,
  etc.) y se las entrega todas al modelo a la vez, vía `create_agent(...)`.
- En cada turno, el modelo decide: ¿contesto ya, o llamo una tool? ¿cuál? ¿con qué argumentos?
  Esa decisión se repite en bucle (ReAct) hasta que el modelo mismo decide que ya puede dar la
  respuesta final.
- No hay un grafo de nodos con aristas fijas (a diferencia de `orquestador → workers →
  sintetizador`). Hay **una sola** instancia de LLM con una bolsa de herramientas y libertad
  para decidir su propio camino.

### 2.2 Por qué no es un *workflow*

Si `Tarea_Agente_Personal` fuera un workflow, el código tendría que anticipar explícitamente
combinaciones como:

```
si la pregunta es sobre tareas       → llamar consultar_tareas
si la pregunta es sobre documentos   → llamar buscar_en_documentos
si buscar_en_documentos no encontró  → llamar buscar_en_la_web
si la pregunta mezcla ambas cosas    → llamar ambas, en algún orden
```

Ese `if/else` (o grafo de routing) sería frágil ante cualquier combinación no anticipada — y el
espacio real de preguntas de un asistente personal (tareas + calendario + documentos + web, en
cualquier orden y combinación) es demasiado grande para enumerar como árbol de casos fijo. Por
eso el agente delega esa decisión al modelo en vez de codificarla.

### 2.3 Por qué tampoco es "solo una cadena de llamadas al LLM"

Una cadena de llamadas (*LLM chain*) sería, por ejemplo, "llamar al modelo una vez para
resumir, tomar esa salida y llamarlo otra vez para traducir" — secuencial, sin ramas, sin
tools condicionales, sin bucle. Eso tampoco describe a `Tarea_Agente_Personal`: hay una sola
"conversación" con el modelo por turno de usuario, pero dentro de ese turno puede haber **N**
iteraciones internas del bucle ReAct (pensar → llamar tool → observar resultado → pensar de
nuevo), un número que **no está fijado de antemano** y que varía según la pregunta.

### 2.4 Tabla comparativa aplicada

| | Workflow (capturas del curso) | `Tarea_Agente_Personal` (v1–v5) |
|---|---|---|
| Quién decide el orden de pasos | El desarrollador, en el grafo/código | El modelo, en cada turno |
| Número de pasos | Fijo (conocido antes de correr) | Variable (decidido en tiempo real) |
| Puede "saltarse" un paso previsto | No | Sí, si el modelo decide que no hace falta |
| Previsibilidad | Alta | Menor — depende del criterio del modelo |
| Patrón teórico | Prompt Chaining / Routing / Parallelization / Orchestrator-Workers / Evaluator-Optimizer | ReAct (Reasoning + Acting) |
| Mecanismo en LangChain | `StateGraph` de LangGraph con aristas fijas | `create_agent(...)` (bucle ReAct) |

---

## 3. ¿Se justificaba construir un agente aquí? (los 4 criterios)

Anthropic (y por extensión el enfoque del curso) plantea evaluar la decisión con cuatro
criterios antes de optar por un agente en vez de un workflow más simple:

1. **Complejidad** — ¿la tarea es multi-paso y difícil de especificar por completo de
   antemano? **Sí**: el espacio de preguntas de un asistente personal (tareas, calendario,
   documentos propios, web) no es enumerable como un árbol fijo de casos.
2. **Valor** — ¿el resultado justifica el costo/latencia extra? **Sí**, para un asistente de
   uso personal donde la flexibilidad de responder cualquier combinación de pedidos vale más
   que la latencia de unos segundos extra.
3. **Viabilidad** — ¿el modelo es suficientemente capaz en este tipo de tarea? **Sí**: llamado
   de herramientas simples (tool calling) con esquemas claros es una tarea en la que tanto
   Claude como modelos locales (Gemma vía LM Studio) tienen buen desempeño.
4. **Costo del error** — ¿un error se puede detectar y recuperar? **Sí**: es uso personal, no
   producción crítica; un error del agente (p. ej. no escalar a búsqueda web) es observable y
   corregible, no catastrófico.

Los cuatro criterios se cumplen — por eso la elección de agente (y no workflow) está
justificada, no es complejidad gratuita.

---

## 4. Matices honestos (para no sobrevender la conclusión)

1. **Es un solo agente, no un sistema multiagente.** No hay orquestador ni sub-agentes
   separados como en el patrón *Orchestrator-Workers* de las capturas. Es el patrón agéntico
   más simple posible (un LLM + una bolsa de tools) — coherente con el principio de "empezar
   simple" de la sección 1.4, no una limitación oculta.
2. **La autonomía del agente tuvo que "domesticarse" con reglas explícitas en el prompt del
   sistema** (`PROMPT_SISTEMA`): una regla para prohibir responder sin llamar tools primero, y
   otra para forzar la escalada a `buscar_en_la_web` cuando el material local no basta. Esto
   **no** convierte al sistema en un workflow (el control de flujo real sigue sin estar en
   código), pero sí es evidencia concreta de la contrapartida que menciona Anthropic: más
   libertad de decisión implica menos previsibilidad, y esa previsibilidad perdida hay que
   recuperarla con ingeniería de prompt y testing — el "costo" real de elegir agente sobre
   workflow.
3. **Dentro del agente, algunas tools individuales SÍ son mini-workflows deterministas** (por
   ejemplo, `calcular_prioridad` combina fecha límite y prioridad con una fórmula fija — eso es
   código normal, no un LLM decidiendo). Esto es correcto y esperado: un agente no significa que
   *todo* dentro de él deba pasar por el LLM. Las partes que tienen una respuesta algorítmica
   clara y determinista deben resolverse en código (más rápido, más barato, 100% predecible); el
   LLM solo decide **cuándo y con qué argumentos** invocar esa función.

---

## 5. Conclusión

`Tarea_Agente_Personal` (v1–v5) es un **agente** en el sentido estricto del framework de
Anthropic: el control de flujo — qué herramienta llamar, en qué orden, cuántas veces, y cuándo
responder — vive en el modelo, decidido dinámicamente en cada turno, no en un grafo de código
predefinido como los patrones *Orchestrator-Workers*, *Evaluator-Optimizer* o *Parallelization*
vistos en clase. La elección se justifica con los cuatro criterios estándar (complejidad, valor,
viabilidad, costo del error) y no es un caso de complejidad injustificada: dentro del agente, la
lógica que sí es determinista (cálculo de prioridad, persistencia en JSON, chunking de
documentos) se mantiene en código plano, y solo la decisión de **qué** hacer y **en qué orden**
se delega al modelo.

---

## Referencias

- Anthropic. (2024). [*Building Effective Agents*](https://www.anthropic.com/research/building-effective-agents). Anthropic Engineering Blog.
- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). [*ReAct: Synergizing Reasoning and Acting in Language Models*](https://arxiv.org/abs/2210.03629). ICLR 2023.
- LangChain. [*Agents*](https://python.langchain.com/docs/concepts/agents/) — documentación conceptual sobre `create_agent` y el bucle de tool-calling.
- LangGraph. [*Workflows and Agents*](https://langchain-ai.github.io/langgraph/tutorials/workflows/) — implementación de los 5 patrones de workflow de Anthropic sobre `StateGraph` (la base técnica de las capturas del curso: orquestador-workers, evaluador-optimizador, paralelización).
