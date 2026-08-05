# LangGraph y Sistemas Multiagente — Análisis completo de la Sesión 15

> **Fuente base:** *Agentes IA — LangGraph MultiAgents* — Módulo 5 (Herramientas para Orquestación), Programa en Diseño e Implementación de Agentes IA, UTEC Posgrado. Dictada por MEng. Boris Alzamora (mismo docente de las Sesiones 9, 13 y 14).
> **Nota técnica:** el PDF original (`SES15_M5_LangGraph_MultiAgent.pdf`, exportado desde PowerPoint) tiene muy poca capa de texto — la mayoría del contenido son diagramas. Este documento se generó extrayendo el texto disponible y **renderizando e interpretando visualmente** las 27 diapositivas.
> **Hallazgo clave de esta sesión:** las páginas 9 y 10 del material citan **directamente** la charla *"How We Build Effective Agents"* de **Barry Zhang** (Research Engineer, Anthropic) — el mismo framework Workflows-vs-Agents y el mismo *checklist* de 4 criterios (complejidad, valor, viabilidad, costo del error) usados en `JUSTIFICACION_AGENTE_VS_WORKFLOW.md` (raíz de este módulo). Esto confirma con evidencia directa del material del curso que el docente construyó esta parte del programa sobre el framework de Anthropic — no es una inferencia, está citado y marcado "ANTHROPIC" en la diapositiva original.

---

## 1. Objetivos y Agenda

**Objetivos declarados:**
1. Comprender **LangGraph** y su uso de nodos y vértices desde llamadas al LLM (*Large Language Model*, modelo de lenguaje de gran escala).
2. Comprender mecanismos de **orquestación de agentes**.

**Agenda — Parte 1:**
| # | Tema |
|---|---|
| 1 | Explicación de ejemplos en VSCode |
| 2 | Lab: Aterrizando a proyectos — configuración de ambiente (Python, VSCode, Ollama / OpenAI / Google AI / otro) |
| 3 | Revisión de un trabajo en VSCode |

**Agenda — Parte 2:**
| # | Tema |
|---|---|
| 4 | Multi Agent Systems (MAS) |
| 5 | Lab: Aterrizando a proyectos — reflexión e implementación en Python |

---

## 2. Arquitectura genérica de un sistema multiagente

Antes de introducir LangGraph, el material presenta un diagrama teórico de **Multi-Agent System Architecture** (independiente de cualquier framework), reconstruido:

```
                    Communication Channels ◀────────────────┐
                       │        ▲                            │
                    Message   Message                    Message
                       │        │                            │
                       ▼        │                     Knowledge Sharing
              ┌──── Agent 1  Agent 3  Agent 2 ─────────────────┘
              │        │        ▲        ▲
         Perception  Feedback  Update   Query
              │        │        │        │
              ▼        │        ▼        ▼
      Physical Environment              Knowledge Base
              └──────── Environment ────────┘

   Collaboration Strategy: Task Allocation + Information Sharing
   (retroalimenta a los 3 agentes con Task Assesment / Knowledge Sharing)
```

**Los tres bloques conceptuales que cualquier sistema multiagente necesita**, según este diagrama:
1. **Communication Channels** — el medio por el que los agentes se pasan mensajes entre sí.
2. **Collaboration Strategy** — cómo se reparten el trabajo (*Task Allocation*) y cómo comparten lo que saben (*Information Sharing*).
3. **Environment** — el mundo con el que los agentes interactúan: un **Physical Environment** (sistemas externos reales) y una **Knowledge Base** (memoria compartida) — los agentes perciben el entorno, actúan sobre él, reciben *feedback*, y consultan/actualizan la base de conocimiento.

Este diagrama es la versión "sin código" del mismo problema que LangGraph (§3) resuelve concretamente: cómo estructurar la comunicación, coordinación y estado compartido entre varios agentes.

---

## 3. Qué es LangGraph

> *"LangGraph es un framework de código abierto desarrollado por LangChain para construir, coordinar y ejecutar flujos de trabajo multiagente basados en modelos de lenguaje (LLMs)."*

**La diferencia visual clave frente a LangChain "clásico"** (diagrama del material, atribuido a *ProjectPro*):

```
LangChain:  A ──▶ B ──▶ C                (cadena lineal)

LangGraph:      A
                / \
               B   C                     (grafo — puede ramificar,
                                           unir, ciclar)
```

**Características clave:**
| Característica | Qué aporta |
|---|---|
| **Arquitectura basada en grafos** | Cada **nodo** representa un agente LLM; las **conexiones** (aristas) definen cómo se comunican y colaboran. |
| **Gestión de estado** | Rastrea y actualiza dinámicamente la información compartida entre agentes, manteniendo el contexto en todo momento. |
| **Coordinación estructurada** | Asegura que los agentes se ejecuten en el orden correcto, intercambiando datos de forma eficiente. |
| **Compatibilidad con LangChain** | Extiende sus capacidades para *"crear sistemas más robustos y controlables"* (resaltado en el material original). |

**¿Para qué sirve LangGraph, según el material?**
- Aplicaciones complejas con múltiples agentes que deben colaborar.
- Sistemas que requieren **transparencia, trazabilidad y control** sobre el flujo de ejecución.
- Casos donde se necesita **observabilidad del estado** y depuración eficiente.

**La analogía visual que usa el material** (supermapa): *tú* eres el **cartógrafo** que diseña el flujo; **LangGraph** es el **navegador** que recorre las rutas óptimas entre agentes; el **estado** es el **cuaderno digital** que registra cada paso del viaje.

### 3.1 Ejemplo real: *Assistant0*

El material muestra un proyecto de referencia que combina LangGraph con autenticación OAuth real:

```
User ◀──▶ UI (Vercel · AI SDK) ◀──▶ AI Agent (LangGraph) ◀──▶ LLM (OpenAI)
                                          │
                          Token request   │   Tool Calling
                                          ▼        │
                                       auth0 ───────┼───────────────┐
                                          │         │               │
                                    Token Exchange   ▼               ▼
                                          ▼      Calculator      SerpApi
                                       Google      (API)      (búsqueda web,
                                    (Gmail, etc.)                API Key)
                                          ▲
                                    Access Token
                                          │
                                        Gmail
```

**Por qué este ejemplo es relevante más allá del diagrama:** muestra un patrón de producción real — el agente no usa una API key fija para acceder a Gmail; usa **Auth0** para hacer *token exchange* con Google y obtener un **Access Token** delegado por el usuario. Esto es exactamente el problema de autorización que cualquier agente que actúe "en nombre de" un usuario real (leer su correo, su calendario) tiene que resolver — el mismo problema que las versiones v2/v4 de `Tarea_Agente_Personal` resuelven con OAuth de Google Calendar, aquí generalizado con un proveedor de identidad dedicado (Auth0) en vez de manejar el flujo OAuth a mano.

---

## 4. El espectro Anthropic: de *Single-LLM* a *Agente* — y el checklist

Esta es la sección más importante de la sesión, y coincide **al detalle** con el framework *"Building Effective Agents"* de Anthropic ya documentado en `JUSTIFICACION_AGENTE_VS_WORKFLOW.md`.

### 4.1 El espectro de agencia

El material presenta una franja con 4 etapas de creciente autonomía:

```
Single-LLM Features → Workflows → Agents → ?
```

| Etapa | Descripción del material | Ejemplo/diagrama |
|---|---|---|
| **Single-LLM Features** | *Summarization, classification, extraction* — una sola llamada al modelo | `In → LLM → Out` |
| **Workflows** | *"LLMs orchestrated by code"* — el código decide el flujo | 3 llamadas LLM en paralelo → `Aggregator` → `Out` |
| **Agents** *(marcado en rojo en el original)* | *"LLMs deciding their own trajectories"* — el LLM decide su propio camino | `Human ↔ LLM Call ↔ Environment`, con `Action`/`Feedback` en bucle hasta `Stop` — el **bucle ReAct** ya descrito en `JUSTIFICACION_AGENTE_VS_WORKFLOW.md` §1.3 |
| **?** | *Agency ↑, Capability ↑, Cost/Latency/Consequences ↑* — lo que viene después de agentes individuales: **sistemas multiagente**, el tema central de esta sesión |

Y la cita textual, atribuida a **Barry Zhang, Research Engineer @ Anthropic**:

> *"¡No construyas Agentes para todo!"*

### 4.2 El checklist "Should I build an agent" (Anthropic)

La diapositiva siguiente, con el logo **ANTHROPIC** explícito, formaliza esa advertencia en una tabla de decisión:

| Pregunta | Respuesta → Recomendación |
|---|---|
| **¿Es la tarea suficientemente compleja?** | No → *Workflows* / Sí → *Agents* |
| **¿Es la tarea suficientemente valiosa?** | < $0.1 → *Workflows* / > $1 → *Agents* |
| **¿Son todas las partes de la tarea realizables?** | No → Reducir el alcance / Sí → *Agents* |
| **¿Cuál es el costo de un error / de descubrir el error?** | Alto → Solo lectura / humano-en-el-bucle / Bajo → *Agents* |

Y, a la derecha, un ejemplo de aplicación de estos 4 criterios al caso de **agentes de codificación** (por qué escribir código es un buen caso de uso para agentes):
1. **Complejidad:** de documento de diseño a *Pull Request* ✓
2. **Valor:** $$$ ✓
3. **Viabilidad:** Claude es muy bueno programando ✓
4. **Costo del error:** *Unit-tests* + CI (*Continuous Integration*, integración continua) ✓

> **Investigación complementaria — la fuente exacta de esta diapositiva:** este material corresponde directamente a la charla pública **"How We Build Effective Agents"** de **Barry Zhang** (Research Engineer, Anthropic), que desarrolla en formato de charla el mismo framework del artículo *"Building Effective Agents"* (Anthropic Engineering, diciembre 2024) ya citado en `JUSTIFICACION_AGENTE_VS_WORKFLOW.md`. Los 4 criterios del checklist (complejidad, valor, viabilidad, costo del error) son **exactamente** los mismos usados en ese documento para justificar por qué `Tarea_Agente_Personal` (v1-v5) es un agente y no un workflow — confirma con evidencia directa del material del curso que el docente construyó el programa sobre este framework específico de Anthropic, incluyendo su recomendación explícita: *"Default to workflows, not agents. Workflows are cheaper, faster, more reliable, and easier to debug. Use agents only when the task is genuinely too ambiguous for deterministic routing."*

---

## 5. Los patrones de LangGraph, en diagramas del propio material

El material incluye capturas reales de grafos de LangGraph construidos en el curso — estas son las mismas imágenes que motivaron la pregunta de si `Tarea_Agente_Personal` es un agente o un workflow (ver `JUSTIFICACION_AGENTE_VS_WORKFLOW.md`):

| Patrón (terminología Anthropic) | Grafo del material | Lectura |
|---|---|---|
| **Evaluator-Optimizer** | `generar_plan → edicion → critica → (Aprobado → edicion_final / Rechazado → vuelve a intentar) → end` | Un nodo genera, otro corrige, un tercero evalúa y decide si aprobar o reintentar — bucle de refinamiento con control fijo por código. |
| **Orchestrator-Workers** | `orquestador → workers → sintetizador → end` (aparece **tres veces** en el material, siempre igual) | Un orquestador reparte trabajo, los *workers* lo ejecutan, un sintetizador combina resultados — control de flujo fijo, sin que ningún nodo decida saltarse al siguiente. |
| **Parallelization (sectioning)** | `start → (animal / femenino / masculino, en paralelo) → composicion → end` | Tres ramas independientes que corren en paralelo y se combinan al final. |
| **Routing** | `start → enrutador → (genera_cancion / genera_parrafo / genera_poema) → nodo respectivo → end` | El enrutador clasifica la entrada y la dirige a **una** rama predefinida entre varias. |
| **ReAct (agente real)** | `start → llm_call → (end / environment, vía "Action") → vuelve a llm_call` | Este es el único de los 5 donde el **LLM decide** si termina o vuelve a actuar — el ciclo se repite un número de veces **no fijado de antemano**, a diferencia de los 4 patrones anteriores. |

**La distinción que separa a los primeros 4 del último es exactamente la de la sección 4.1**: en *Evaluator-Optimizer*, *Orchestrator-Workers*, *Parallelization* y *Routing*, el grafo tiene aristas fijas — es código (`StateGraph` de LangGraph) decidiendo el camino. En el patrón **ReAct**, la arista de vuelta (`environment → llm_call`) se recorre tantas veces como el LLM decida, y es el propio LLM quien decide cuándo llegar a `end` — ahí es donde el sistema pasa de ser un *workflow* a ser un *agente*, según la definición de Anthropic.

---

## 6. Multi-Agent Systems (MAS) en LangGraph

> *"Multi-Agent Systems (MAS) son arquitecturas compuestas por múltiples agentes autónomos que colaboran, se comunican y toman decisiones de forma coordinada para resolver tareas complejas."*

**Cómo se conectan en LangGraph:** un **grafo de ejecución** donde cada **nodo** es un agente con un rol (ej. planificador, ejecutor, verificador), las **aristas** definen el flujo de información entre agentes, y el **estado compartido** se actualiza dinámicamente y se propaga entre nodos.

**Ventajas de los MAS en LangGraph, según el material:**
- **Modularidad** — cada agente cumple un rol claro.
- **Escalabilidad** — se pueden añadir o modificar agentes fácilmente.
- **Auditabilidad** — el flujo es transparente y trazable.
- **Extensibilidad** — permite simular, probar y mejorar el sistema por partes.

### 6.1 Las 6 topologías de MAS (documentación oficial de LangGraph)

El material reproduce la tabla de topologías de la [documentación oficial de LangGraph](https://langchain-ai.github.io/langgraph/concepts/multi_agent/):

| Topología | Estructura | Cuándo usarla |
|---|---|---|
| **Single Agent** | Un LLM con sus *tools* | Caso base — sin multiagencia. |
| **Network** | Todos los agentes interconectados entre sí | Cualquier agente puede hablar con cualquier otro — máxima flexibilidad, mínima estructura. |
| **Supervisor** | Un agente central dirige a los demás, que le responden a él | El patrón *Orchestrator-Workers* de Anthropic, con el supervisor como único punto de coordinación. |
| **Supervisor (as tools)** | El supervisor invoca a los demás agentes **como si fueran tools** | Exactamente el patrón *Agent as Tool* de la Sesión 14 (§5 de ese análisis) — aquí aplicado como una topología MAS más. |
| **Hierarchical** | Un supervisor de supervisores, cada uno coordinando su propio grupo de agentes | Escala el patrón *Supervisor* a más de un nivel — útil cuando un solo supervisor tendría demasiados agentes directos a cargo. |
| **Custom** | Grafo arbitrario definido a medida | Cuando ninguna topología estándar encaja con el problema real. |

---

## 7. El costo de tener demasiadas herramientas

> *"A más herramientas se otorgan al agente, más capacidades. Sin embargo, cuantas más herramientas haya, más difícil será usarlas eficientemente... Añadir herramientas también implica aumentar las descripciones de las mismas, que podrían no encajar en el contexto de un modelo."* — **Chip Huyen**, *AI Engineering* (misma autora citada en el análisis de la Sesión 13, §6.2).

El material acompaña esta advertencia con un diagrama real de **evaluación de un agente** (etiquetado "Evals!"): un grafo donde cada arista entre nodos (`query_generator`, `bing_search`, `text_detector`, `image_captioner`, `knowledge_retrieval`, `solution_generator`, `answer_generator`) tiene una **probabilidad medida empíricamente** (ej. `START → text_detector` ocurre el 30% de las veces, `bing_search → knowledge_retrieval` el 97% de las veces). Esto es una técnica de evaluación: en vez de solo medir si la respuesta final fue correcta, se mide **qué camino tomó realmente el agente** a través de sus herramientas disponibles, y con qué frecuencia — permitiendo detectar, por ejemplo, herramientas que casi nunca se usan (candidatas a eliminar) o transiciones inesperadas que revelan confusión del modelo sobre cuándo usar cada tool.

*(Esta es la misma preocupación que resuelve el patrón de recuperación dinámica de herramientas vía vectorstore, documentado en la Sesión 14 §5 de este módulo.)*

---

## 8. Patrones de orquestación multiagente — ejemplos aplicados

El material dedica varias diapositivas a patrones concretos de orquestación, con ejemplos de negocio reales:

### 8.1 Concurrent orchestration (orquestación concurrente)

```
Ticker symbol → Stock analysis agent
                      │
    ┌─────────────────┼─────────────────┬──────────────┐
    ▼                 ▼                 ▼              ▼
Fundamental       Technical         Sentiment         ESG
analysis agent    analysis agent    analysis agent    agent
    │
┌───┴───┐
▼       ▼
Financials  Competitive
analysis    analysis
```
Un agente principal reparte el análisis de una acción bursátil entre 4 agentes especializados en paralelo (uno de los cuales, *Fundamental*, se subdivide en 2 más), y combina los resultados intermedios en una decisión final con evidencia de respaldo. **Cuándo usar este patrón:** tareas paralelizables (con agentes fijos o seleccionados dinámicamente), tareas que se benefician de múltiples perspectivas independientes (técnicas de decisión multiagente: *lluvia de ideas, razonamiento de conjunto, decisiones por quórum y votación*), y escenarios críticos donde el paralelismo reduce la latencia.

### 8.2 Group chat orchestration (orquestación por chat grupal)

Un `Group chat manager` coordina 3 agentes especializados (compromiso comunitario, planificación ambiental, presupuesto/operaciones de parques) que contribuyen a una conversación acumulada (`Accumulating conversation`) hasta llegar a un consenso (`Park proposal consensus`). **Cuándo usarlo:** sesiones de lluvia de ideas donde agentes con perspectivas distintas se apoyan en las contribuciones de los demás; procesos de decisión que se benefician del debate; refinamiento iterativo mediante discusión; problemas multidisciplinarios; y también **escenarios de control de calidad** (revisión de cumplimiento normativo, flujos editoriales con separación clara entre creación y validación).

### 8.3 Agent handoff pattern (patrón de transferencia entre agentes)

Un agente de triaje (`Triage support agent`) intenta resolver directamente y **transfiere** el problema a un agente especializado (infraestructura técnica, resolución financiera, acceso a cuenta) cuando reconoce sus propios límites — y puede escalar a un humano (`Customer support employee`) si ningún agente de IA puede resolverlo. Cada agente puede terminar la conversación si determina que el cliente quedó satisfecho.

> **Nota regulatoria incluida en el material (contexto Perú):** en el Perú, el uso de chatbots y sistemas automatizados de atención se rige principalmente por la **Ley N° 31601**, que modifica el **Código de Protección y Defensa del Consumidor (Ley 29571)** — establece la obligación de ofrecer canales de atención con **personas reales**, sin depender exclusivamente de asistentes virtuales. Esto hace que el "escalamiento a humano" del patrón *handoff* no sea solo una buena práctica de UX sino, en el contexto peruano, un requisito legal para sistemas de atención al cliente automatizados.

### 8.4 Magentic orchestration

Para **problemas abiertos y complejos sin un plan predefinido**. Un `Manager agent` construye y refina dinámicamente un *Task and progress ledger* (bitácora de tareas y avance) con metas y sub-metas, invoca a los agentes especializados tantas veces como sea necesario, evalúa continuamente si la tarea está completa (`Task complete?`), y entrega el resultado a un participante humano.

**La diferencia clave frente a *Group chat* (según el material):** en *Group chat*, el manager solo **coordina** la conversación; en *Magentic*, el manager **diseña activamente el plan de acción**, mientras que los agentes especializados usan herramientas para **modificar directamente sistemas externos** — no se limitan a aportar su conocimiento interno a una conversación. Es el patrón más autónomo de los cuatro presentados aquí.

*Ref. del material: [learn.microsoft.com/.../ai-agent-design-patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)*

### 8.5 Arquitectura multi-framework (AWS)

Una última diapositiva muestra un patrón de orquestación **agnóstico de framework**: una consulta pasa por *Query re-write* y una capa de *"Graph based agent orchestration"* que reparte el trabajo entre un **agente nativo** (Bedrock Agent), varios **agentes open-source** (Search Agent, LangChain Agent, RAG Agent) y un **agente propietario** (CrewAI Agent) — cada uno pudiendo venir de un framework distinto — cuyos resultados pasan por *Grader Agents* (agentes evaluadores) que verifican si hay coincidencia (`Match?`) antes de involucrar a un humano en el bucle (*Human-in-the-loop*). Refuerza la idea de que la orquestación multiagente no está atada a un único framework — LangGraph, CrewAI y agentes nativos de un proveedor cloud pueden coexistir bajo una misma capa de orquestación.

---

## 9. Laboratorios y tarea de la sesión

| Actividad | Instrucción |
|---|---|
| **Lab — Campaña Publicitaria "café.ai"** | En base al código revisado en clase, proponer un equipo multiagente que desarrolle una campaña publicitaria para un café. El equipo debe contar con un **enrutador**, un **rol creativo**, un **redactor** y un **diseñador**. |
| **Tarea PERSONAL — LangGraph** | Usando LangGraph, definir un **workflow, agente o multiagente** que ayude a resolver una tarea de la vida diaria propia (el mismo ejercicio que dio origen a `Tarea_Agente_Personal`). Entrega: Google Doc o PDF resumiendo el caso y luego el código. **Fecha límite: 12/08.** |

---

## 10. Síntesis — lo que hay que llevarse de esta sesión

1. **El framework de Anthropic (Workflows vs. Agents, y su checklist de 4 criterios) no es una interpretación de este análisis — está citado literalmente en el material del curso**, con atribución directa a Barry Zhang (Anthropic). Es la base teórica explícita sobre la que se construyó esta parte del programa.
2. **LangGraph formaliza el espectro completo**: desde una sola llamada al LLM, pasando por *workflows* con control de flujo fijo por código (secuencial, paralelo, condicional, en bucle-`for`), hasta agentes ReAct donde el propio LLM decide su trayectoria — y de ahí hacia sistemas **multiagente**.
3. **Un sistema multiagente (MAS) tiene 3 piezas conceptuales** (canales de comunicación, estrategia de colaboración, entorno compartido) que LangGraph resuelve concretamente con grafos, estado compartido y aristas de coordinación.
4. **Existen 6 topologías estándar de MAS en LangGraph** (Single Agent, Network, Supervisor, Supervisor-as-tools, Hierarchical, Custom) — la elección depende de cuánta autonomía y cuánta estructura necesita el problema.
5. **Demasiadas herramientas degradan a un agente**, no lo mejoran — y esto se puede medir empíricamente observando las probabilidades de transición reales entre las tools que el agente efectivamente usa.
6. **Existen patrones de orquestación multiagente ya nombrados y documentados** más allá de los 5 básicos de Anthropic: *Concurrent*, *Group chat*, *Handoff*, *Magentic*, y arquitecturas multi-framework — cada uno resuelve un tipo distinto de colaboración (paralelismo, consenso deliberativo, escalamiento por especialización, planificación abierta).
7. **El contexto regulatorio local importa**: en el Perú, un patrón de *handoff* a humano no es solo buena práctica de UX sino una obligación legal para atención al cliente automatizada (Ley N° 31601).

---

## 11. Checklist práctico — decidiendo tu arquitectura (Workflow / Agente / MultiAgente)

- [ ] ¿La tarea es lo bastante compleja como para no poder mapearse como un árbol de decisión fijo? (No → *Workflow*; Sí → considerar *Agente*.)
- [ ] ¿El valor de la tarea justifica el costo/latencia de un agente? (Regla de Anthropic: <$0.1/tarea → *Workflow*; >$1/tarea → *Agente*.)
- [ ] ¿El modelo es capaz de forma confiable en cada sub-tarea que le vas a delegar? (Si no, reducir el alcance antes de construir el agente.)
- [ ] ¿Cuál es el costo de un error, y qué tan fácil es detectarlo? (Alto costo/difícil de detectar → mantener humano-en-el-bucle o solo-lectura.)
- [ ] Si el problema involucra a **más de un agente**: ¿la colaboración es de coordinación central (*Supervisor*), red abierta (*Network*), delegación por especialización (*Handoff*), consenso deliberativo (*Group chat*), paralelismo (*Concurrent*), o planificación abierta sin plan fijo (*Magentic*)?
- [ ] ¿Cuántas herramientas tiene cada agente? Si son muchas, ¿conviene indexarlas en un vectorstore y recuperarlas dinámicamente en vez de pasarlas todas siempre?
- [ ] ¿El caso de uso requiere que un agente hable con agentes de **otro** sistema/organización? (Ahí es donde entra A2A, no *Agent as Tool* — ver Sesión 14 §6.)
- [ ] ¿Hay una obligación regulatoria de ofrecer escalamiento a un humano real? (Aplica directamente si el agente atiende consumidores en el Perú.)

---

## 12. Referencias

**Del material original:**
- Diagramas propios del curso — arquitectura MAS genérica, LangGraph vs. LangChain, ejemplo *Assistant0*, checklist de Anthropic, topologías MAS de LangGraph, patrones de orquestación (Concurrent, Group chat, Handoff, Magentic, multi-framework AWS).
- LangGraph — documentación oficial de *Multi-agent Systems*. [langchain-ai.github.io/langgraph/concepts/multi_agent](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- Chip Huyen — *AI Engineering* (cita sobre el costo de escalar el número de herramientas de un agente).
- Microsoft Learn — *AI agent design patterns* (referencia del patrón *Magentic orchestration*). [learn.microsoft.com/.../ai-agent-design-patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- Ley N° 31601 (Perú) — modifica el Código de Protección y Defensa del Consumidor (Ley 29571): obligación de ofrecer canales de atención con personas reales.

**Investigación complementaria (añadida en este documento):**
- Barry Zhang (Anthropic) — charla *"How We Build Effective Agents"*: fuente exacta del checklist de 4 criterios y la cita "¡No construyas Agentes para todo!" mostrados en el material — desarrolla en formato charla el mismo framework del artículo *Building Effective Agents* (Anthropic Engineering, dic. 2024) ya citado en `JUSTIFICACION_AGENTE_VS_WORKFLOW.md`.
- Arco interno del curso: `JUSTIFICACION_AGENTE_VS_WORKFLOW.md` (raíz de este módulo) — aplica este mismo framework de Anthropic a `Tarea_Agente_Personal` (v1-v5); esta sesión confirma con el material original que dicho framework es, en efecto, la base teórica del curso. Sesión 14 (Infraestructura de Agentes) — el patrón *Agent as Tool* ahí documentado es la misma topología "Supervisor (as tools)" de §6.1 de este análisis.

---

*Documento generado a partir del PDF de la Sesión 15 (Módulo 5, UTEC Posgrado) — texto extraído + diapositivas gráficas interpretadas visualmente — más investigación propia sobre la charla de Barry Zhang (Anthropic) y la documentación oficial de LangGraph.*
