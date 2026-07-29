# Espectro de Sistemas de IA: LLM Features → Workflows → Agents → MultiAgents

> La imagen muestra la evolución de complejidad y autonomía de los sistemas basados en LLMs. No son categorías aisladas — son puntos en un espectro donde cada nivel hereda lo anterior y agrega una nueva capacidad fundamental.

---

## El espectro completo

```
Menos autónomo ◄──────────────────────────────────────────────► Más autónomo

  LLM Augmented          Workflows              Agents           MultiAgents
    Features
       │                     │                     │                  │
  LLM como             Plan fijo +           Plan autónomo +    Plan autónomo +
  función en           pasos con             herramientas,      delegación a
  un pipeline          genAI                 memoria y          otros agentes
                                             conocimiento
```

---

## Las dos dimensiones que definen la autonomía

La imagen marca dos rectángulos de colores que cruzan horizontalmente las categorías. Cada rectángulo representa una **dimensión de orquestación** que juntas definen el nivel de autonomía del sistema:

```
┌─────────────────────────────────────────────────────────────────────┐
│  ORQUESTACIÓN DEL PLAN DE RESOLUCIÓN  (quién decide los pasos)      │  ← naranja
│                                                                     │
│   Workflows: pasos DISEÑADOS por el humano                          │
│   Agents / MultiAgents: pasos CREADOS de forma autónoma por la IA   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  ORQUESTACIÓN DE HERRAMIENTAS Y CONOCIMIENTO  (quién ejecuta)       │  ← morado
│                                                                     │
│   Workflows: cada paso potenciado con genAI                         │
│   Agents: pasos ejecutados por herramientas + conocimiento          │
│   MultiAgents: pasos delegados a otros agentes especializados       │
└─────────────────────────────────────────────────────────────────────┘
```

**La intersección de ambas dimensiones define la autonomía real del sistema.**

---

## Nivel 1 — LLM Augmented Features

### ¿Qué es?

Un **pipeline de datos tradicional** (código, scripts, ETL, procesos batch) que invoca a un LLM en uno o más pasos específicos para potenciar una tarea concreta.

El LLM **no decide nada**: es tratado como una función más dentro del pipeline. Alguien llamó a `gpt.complete(texto)` igual que llamaría a `str.upper()`.

### Características clave

| Aspecto | Descripción |
|---|---|
| **Plan de resolución** | No existe — el pipeline completo fue diseñado y codificado por el desarrollador |
| **Ejecución de pasos** | Código determinista; el LLM aparece como un nodo de transformación de texto |
| **Autonomía** | Ninguna — cada paso, orden y condición está hardcodeado |
| **Quién diseña la lógica** | El desarrollador humano, completamente |

### Qué hace el LLM dentro de este nivel

- Clasificar texto en categorías predefinidas
- Resumir un documento antes de guardarlo
- Extraer entidades (nombres, fechas, montos) de un texto
- Traducir o reformatear contenido
- Generar una descripción a partir de datos estructurados

### Ejemplo concreto

```
Pipeline de procesamiento de emails:
  1. Leer emails del inbox (código)
  2. Invocar LLM → "clasifica este email como: soporte / ventas / spam" (LLM)
  3. Guardar en la tabla correspondiente según clasificación (código)
  4. Enviar confirmación (código)
```

El LLM hizo una sola cosa en un paso fijo. No decidió qué hacer a continuación. No tiene herramientas. No recuerda nada. No tiene objetivo propio.

### Por qué NO es un agente ni un workflow

- No hay **plan autónomo**
- No hay **orquestación de herramientas**
- La secuencia de pasos no cambia según el contexto
- Es software tradicional con una llamada a API de IA

---

## Nivel 2 — Workflows

### ¿Qué es?

Un sistema donde el **plan de pasos está prediseñado por un humano** (igual que el nivel anterior), pero cada uno de esos pasos está **potenciado con genAI** para lograr autonomía dentro del paso.

La diferencia crítica con LLM Augmented Features: aquí hay **orquestación explícita** — existe un motor que coordina la ejecución de los pasos, y cada paso puede usar genAI para razonar, decidir o generar contenido.

### Las dos capas del Workflow

```
CAPA 1 — EL PLAN (naranja): diseñado por el humano
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│  Paso 1   │ →  │  Paso 2   │ →  │  Paso 3   │ →  │  Paso 4   │
│ (fijo)    │    │ (fijo)    │    │ (fijo)    │    │ (fijo)    │
└───────────┘    └───────────┘    └───────────┘    └───────────┘

CAPA 2 — LA EJECUCIÓN (morado): potenciada con genAI
Dentro de cada paso el LLM puede razonar, generar, clasificar o tomar micro-decisiones
```

### Características clave

| Aspecto | Descripción |
|---|---|
| **Plan de resolución** | Predeterminado y diseñado por el humano — los pasos no cambian |
| **Ejecución de pasos** | Cada paso es potenciado con genAI (puede haber LLM calls, RAG, clasificadores ML) |
| **Autonomía** | Parcial — dentro de cada paso el sistema tiene flexibilidad, pero la secuencia es rígida |
| **Quién diseña la lógica** | El desarrollador define el flujo; la IA ejecuta con flexibilidad dentro de cada nodo |

### Diferencia fundamental con un Agente

En un Workflow, si ocurre algo inesperado que no estaba contemplado en el diseño, el sistema **falla o ignora** la situación porque no hay capacidad de replanificar.

Un Agente, ante lo inesperado, **ajusta su plan** de forma autónoma.

### Herramientas típicas para construir Workflows

- **n8n** / **Zapier** con nodos de IA
- **LangChain** con chains fijas (no agents)
- **Apache Airflow** + llamadas a LLM en operadores específicos
- **Make (Integromat)** con pasos de AI

### Ejemplo concreto

```
Workflow de generación de reportes de ventas:
  1. Extraer datos de ventas del CRM (paso fijo)
  2. Invocar LLM → generar análisis narrativo de los números (paso fijo con genAI)
  3. Invocar LLM → identificar 3 insights principales (paso fijo con genAI)
  4. Generar PDF del reporte con plantilla (paso fijo)
  5. Enviar por email a la lista de distribución (paso fijo)
```

Si en el paso 3 el LLM detecta una anomalía que requeriría investigar más datos, no puede hacerlo: el paso 4 ya está programado y se ejecutará de todas formas.

---

## Nivel 3 — Agents

### ¿Qué es?

Un sistema donde el **LLM crea el plan de resolución de forma autónoma** y luego **ejecuta los pasos usando herramientas, conocimiento y memoria**.

Esta es la diferencia fundamental respecto al Workflow: el plan no existe antes de que el agente empiece. El agente recibe el objetivo y **decide él mismo** qué pasos dar, en qué orden, y si necesita replantear.

### Las dos capas del Agente

```
CAPA 1 — EL PLAN (naranja): creado por el agente en tiempo real
El LLM recibe el objetivo y genera autónomamente:
  - ¿Qué pasos necesito dar?
  - ¿En qué orden?
  - ¿Qué herramientas necesito en cada paso?
  - ¿Ya terminé o necesito más pasos?

CAPA 2 — LA EJECUCIÓN (morado): por asociación a herramientas, conocimiento y memoria
Cada paso es ejecutado por el agente invocando:
  - Herramientas (APIs, búsqueda web, lectura de archivos, ejecución de código)
  - Conocimiento (base vectorial, documentos, ontologías)
  - Memoria (corto plazo: contexto actual / largo plazo: información persistente entre sesiones)
```

### El ciclo Percepción → Razonamiento → Acción → Observación (ReAct)

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   Objetivo recibido                                              │
│        │                                                         │
│        ▼                                                         │
│   [RAZONA] ──► ¿Qué herramienta necesito ahora?                 │
│        │                                                         │
│        ▼                                                         │
│   [ACTÚA] ──► Invoca herramienta (tool call)                    │
│        │                                                         │
│        ▼                                                         │
│   [OBSERVA] ──► Lee el resultado de la herramienta              │
│        │                                                         │
│        ▼                                                         │
│   [RAZONA] ──► ¿Ya alcancé el objetivo? ¿Qué sigue?            │
│        │                                                         │
│        ├── No terminé → vuelve a ACTÚA (nuevo paso autónomo)    │
│        └── Terminé → entrega resultado final                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Características clave

| Aspecto | Descripción |
|---|---|
| **Plan de resolución** | Creado autónomamente por el LLM al recibir el objetivo — no existe antes |
| **Ejecución de pasos** | El agente invoca herramientas, consulta conocimiento y usa memoria según necesite |
| **Autonomía** | Alta — puede replanificar ante resultados inesperados |
| **Quién diseña la lógica** | El desarrollador define herramientas disponibles y el system prompt; el agente decide el plan |

### Qué tiene un Agente que un Workflow no tiene

| Capacidad | Workflow | Agente |
|---|---|---|
| Plan adaptable | No — fijo | Sí — lo crea en tiempo real |
| Reacción a lo inesperado | No — falla o ignora | Sí — replantea su plan |
| Encadenamiento dinámico de herramientas | No — predefinido | Sí — decide qué tool usar según el resultado anterior |
| Memoria entre pasos | Limitada | Sí — corto y largo plazo |
| Decisión de cuándo terminar | No — el workflow termina en el último paso | Sí — el agente decide cuándo el objetivo está cumplido |

### Ejemplo concreto

```
Agente de investigación de mercado:
  Objetivo: "Analiza la posición competitiva de nuestra empresa en el mercado peruano de fintech"

  Plan generado autónomamente:
  1. [decide] Buscar en web los principales competidores fintech en Perú
  2. [decide] Para cada competidor encontrado, buscar precios y productos
  3. [decide] Comparar contra nuestra oferta (consulta base de conocimiento interna)
  4. [decide] Detectó un competidor nuevo no conocido → decide buscar más info sobre él
  5. [decide] Generar reporte comparativo con hallazgos
  6. [decide] El reporte está completo → terminar

  Ninguno de estos pasos estaba programado de antemano.
  El paso 4 (buscar más info sobre el competidor nuevo) surgió de un resultado inesperado.
```

---

## Nivel 4 — MultiAgents

### ¿Qué es?

Un sistema donde el **plan de resolución es creado de forma autónoma** (igual que el Agente), pero los pasos **no los ejecuta un solo agente** sino que son **delegados a otros agentes especializados**, cada uno con sus propias herramientas, conocimiento y memoria.

### La diferencia clave respecto al Agente

| | Agent | MultiAgent |
|---|---|---|
| **¿Quién crea el plan?** | El propio agente | El agente orquestador |
| **¿Quién ejecuta los pasos?** | El mismo agente con sus tools | **Otros agentes especializados** |
| **¿Qué tiene cada ejecutor?** | Herramientas + conocimiento + memoria | Herramientas + conocimiento + memoria **propios** |

En MultiAgents hay dos roles:

```
ORQUESTADOR (planifica)
     │
     ├──► Agente Especialista A (tools + knowledge + memory propios)
     ├──► Agente Especialista B (tools + knowledge + memory propios)
     └──► Agente Especialista C (tools + knowledge + memory propios)
```

### Las dos capas del MultiAgent

```
CAPA 1 — EL PLAN (naranja): creado autónomamente por el orquestador
El LLM orquestador recibe el objetivo y decide:
  - ¿Qué subobjetivos necesito resolver?
  - ¿A qué agente especialista le delego cada subobjetivo?
  - ¿En qué orden los convoco?
  - ¿Los resultados son suficientes o necesito más agentes?

CAPA 2 — LA EJECUCIÓN (morado): por otros agentes con sus propias capacidades
Cada agente especialista es, en sí mismo, un agente completo:
  - Tiene su propio plan de ejecución
  - Tiene sus propias herramientas
  - Tiene su propio conocimiento
  - Tiene su propia memoria
```

### ¿Por qué MultiAgent y no un solo Agente grande?

| Razón | Explicación |
|---|---|
| **Especialización** | Un agente experto en análisis legal no necesita saber de finanzas — los agentes especializados son más precisos |
| **Paralelismo** | Varios agentes pueden trabajar en paralelo en subproblemas independientes, reduciendo el tiempo total |
| **Límites de contexto** | Un único agente con todo el conocimiento y todas las herramientas excede el contexto del LLM — dividir en agentes resuelve este límite |
| **Modularidad** | Puedes actualizar o reemplazar un agente especialista sin afectar al orquestador ni a los demás |
| **Resiliencia** | Si un agente especialista falla, el orquestador puede intentar con otro o replanificar |

### Ejemplo concreto

```
MultiAgent de due diligence para fusión de empresas:
  Objetivo: "Evalúa si debemos adquirir la empresa X"

  Orquestador genera plan autónomo y delega:
  ├── Agente Legal → analiza contratos, litigios, propiedad intelectual
  │     (tiene tools: lector de PDFs, base normativa, buscador de litigios)
  ├── Agente Financiero → analiza estados financieros, flujo de caja, deuda
  │     (tiene tools: lector de Excel, calculadora financiera, benchmarks de industria)
  ├── Agente Técnico → evalúa la arquitectura de software y deuda técnica
  │     (tiene tools: acceso a repositorios de código, scanners de seguridad)
  └── Agente de Mercado → analiza posición competitiva y clientes
        (tiene tools: búsqueda web, CRM externo, análisis de reseñas)

  Orquestador recibe todos los resultados →
  genera reporte ejecutivo de recomendación de adquisición
```

Ningún agente individual podría hacer este trabajo con la misma profundidad porque requeriría conocimiento y herramientas de dominios completamente distintos.

---

## Cuadro comparativo completo

| Dimensión | LLM Aug. Features | Workflows | Agents | MultiAgents |
|---|---|---|---|---|
| **¿Quién crea el plan?** | El desarrollador (hardcoded) | El desarrollador (diseñado) | El LLM (autónomo) | El LLM orquestador (autónomo) |
| **¿Cómo se ejecutan los pasos?** | Código + llamadas a LLM | Pasos fijos potenciados con genAI | Agente con tools + knowledge + memory | Otros agentes especializados |
| **Adaptabilidad ante lo inesperado** | Ninguna | Ninguna | Alta | Muy alta |
| **Orquestación del plan** | No existe | Humano la diseña | IA la genera en tiempo real | IA la genera y delega |
| **Orquestación de tools/knowledge** | No existe | Dentro de cada paso fijo | El agente decide qué tool usar | Cada sub-agente decide sus tools |
| **Autonomía** | Nula | Parcial (dentro del paso) | Alta | Máxima |
| **Paralelismo** | No | Limitado | Limitado (un agente) | Sí (múltiples agentes en paralelo) |
| **Complejidad de tareas que resuelve** | Baja (transformaciones puntuales) | Media (flujos conocidos) | Alta (objetivos abiertos) | Muy alta (objetivos complejos multidisciplinarios) |
| **Ejemplo de herramienta** | Script Python + OpenAI API | n8n, LangChain chains | LangGraph, AutoGen, Claude Agents | CrewAI, AutoGen multiagent, LangGraph multi-node |

---

## La definición de autonomía según la imagen

La imagen coloca el botón **"Definición de Autonomía"** en la intersección de las dos dimensiones de orquestación. Esto no es casualidad: la autonomía de un sistema se define exactamente por la combinación de ambas:

```
                      ¿Quién crea el plan?
                   Humano          IA autónoma
                     │                 │
¿Quién    Código ────┼─────────────────┤
ejecuta   fijo       │ LLM Aug.        │
los       │          │ Features        │
pasos?    │          │                 │
          genAI ─────┼─────────────────┤
          potenciado  │ Workflows       │    Agents
          │          │                 │
          Otros ─────┼─────────────────┤
          agentes     │                 │    MultiAgents
                     │                 │
```

- **Autonomía baja** = plan humano + ejecución codificada → LLM Augmented Features
- **Autonomía media** = plan humano + ejecución con genAI → Workflows
- **Autonomía alta** = plan autónomo + ejecución con tools propios → Agents
- **Autonomía máxima** = plan autónomo + ejecución delegada a otros agentes → MultiAgents

---

## Implicaciones para el diseño de sistemas

### ¿Cuándo elegir cada nivel?

| Usa este nivel cuando... | Nivel recomendado |
|---|---|
| La tarea es siempre la misma y bien definida, solo necesitas IA para una transformación | LLM Augmented Features |
| El flujo tiene pasos conocidos pero cada paso necesita flexibilidad de lenguaje | Workflows |
| El problema puede tener muchos caminos posibles y no sabes de antemano cuántos pasos necesitas | Agents |
| El problema requiere expertise en múltiples dominios o puede descomponerse en subtareas paralelas independientes | MultiAgents |

### Progresión de complejidad y riesgo

```
Complejidad de implementación:  ████░░░░  ██████░░  ████████  ████████████
Potencia de resolución:         ████░░░░  ██████░░  ████████  ████████████
Riesgo de comportamiento inesperado: ░░░░  ████░░░░  ████████  ████████████
Costo de inferencia (tokens):   ████░░░░  ██████░░  ████████  ████████████
```

A mayor autonomía, mayor potencia pero también mayor riesgo y costo. Por eso la elección del nivel no es "siempre el más avanzado", sino el que **justo resuelve el problema** con el mínimo riesgo necesario.

---

## Relación con los archivos anteriores

- La **columna 6 del cuadro de Conversational Automation** (System Prompt + Context + Input Prompt) corresponde al nivel **Agent** de este espectro. Ver [`taxonomia_conversational_automation.md`](taxonomia_conversational_automation.md)
- Los **4 verbos de Gartner** (percibir, decidir, actuar, lograr objetivos) se cumplen a partir del nivel **Agent**. Los niveles anteriores (Features y Workflows) no los cumplen todos. Ver [`../Modulo1_Introduccion_Motivacion/Sesion01_Introduccion_Agentes/que_es_un_agente_ia.md`](../Modulo1_Introduccion_Motivacion/Sesion01_Introduccion_Agentes/que_es_un_agente_ia.md)
- Las **5 ideas de proyecto final** del lab están en el nivel **Agent** (semi-autónomo). Ver [`ideas_proyecto_final_agent_profile_cards.md`](ideas_proyecto_final_agent_profile_cards.md)
