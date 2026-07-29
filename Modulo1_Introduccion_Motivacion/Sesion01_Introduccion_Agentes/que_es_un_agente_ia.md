# ¿Qué es un Agente de IA?

> Definición (Gartner): Los agentes de IA son entidades de software **autónomas o semi-autónomas** que usan técnicas de IA para **percibir**, **tomar decisiones**, **tomar acciones** y **lograr objetivos** en su ambiente digital o físico.

---

## Los 4 verbos que definen a un agente

| Capacidad | Qué significa en la práctica |
|---|---|
| **Percibir** | Lee su entorno: un archivo, un email, una web, una base de datos, un sensor |
| **Tomar decisiones** | Razona sobre lo que percibió y elige qué hacer a continuación |
| **Tomar acciones** | Ejecuta algo concreto: llama una API, escribe código, mueve un archivo, envía un mensaje |
| **Lograr objetivos** | Todo lo anterior apunta a una meta definida, no solo responde a un comando puntual |

La palabra clave es **autónomo/semi-autónomo**: el agente ejecuta ese ciclo *por sí solo*, sin que un humano le indique paso a paso qué hacer.

---

## Lo que NO es un Agente de IA

Es común confundir herramientas inteligentes con agentes. La diferencia está en si el sistema **decide y actúa** o solo **responde y ejecuta**.

| Cosa | Por qué NO es un agente |
|---|---|
| **LLM** (GPT, Claude, Gemini…) | Solo genera texto. No percibe ni actúa por sí solo. Es el "cerebro", pero sin cuerpo ni objetivos propios. |
| **Instrucciones de tareas específicas** | Un prompt muy detallado no convierte algo en agente. El humano sigue siendo quien dirige cada paso. |
| **Funciones de software automatizadas** | Un script que corre cada noche no decide nada; solo ejecuta lo que alguien programó. |
| **Workflows RPA** | Automatización robótica rígida: sigue pasos fijos y predefinidos, no razona ni se adapta a situaciones nuevas. |
| **Asistentes conversacionales** | Un chatbot que responde preguntas no tiene objetivos propios ni actúa en el mundo más allá de generar texto. |
| **Una interfaz a un asistente** | Una ventana de chat es solo la UI; no es el agente en sí. |

---

## La idea central

> **Agente = percepción + razonamiento + acción + objetivo, en un ciclo autónomo.**

- Claude/ChatGPT sin herramientas → **NO es un agente**
- Claude/ChatGPT con acceso a tu correo, calendario y capacidad de enviar emails para cumplir una meta → **SÍ es un agente**

---

## El ciclo de un agente (bucle Percepción–Decisión–Acción)

```
┌─────────────────────────────────────────────┐
│                                             │
│   Entorno  ──percibe──►  LLM / Razonador   │
│      ▲                        │             │
│      │                    decide            │
│      │                        │             │
│      └──────acción────────────┘             │
│                                             │
└─────────────────────────────────────────────┘
```

El agente **no termina** después de una respuesta; sigue en bucle hasta alcanzar su objetivo o recibir señal de parada.

---

## Componentes típicos de un agente

| Componente | Rol |
|---|---|
| **Modelo de lenguaje (LLM)** | Cerebro: razona, planifica y decide |
| **Herramientas (Tools)** | Manos: buscar en la web, ejecutar código, leer archivos, llamar APIs |
| **Memoria** | Corto plazo (contexto de la conversación) y largo plazo (base de datos vectorial) |
| **Objetivo / instrucción del sistema** | El "para qué" que guía todas las decisiones |
| **Orquestador** | Controla el ciclo percepción–decisión–acción |

---

## Espectro de autonomía

```
Menos autónomo ◄─────────────────────────────► Más autónomo

 Chatbot      Asistente       Agente          Agente
 simple       con tools       supervisado     completamente
              (copilot)       (human-in-       autónomo
                               the-loop)
```

La mayoría de aplicaciones empresariales hoy viven en **agente supervisado**: el agente actúa, pero un humano revisa pasos críticos.

---

## Ejemplos concretos

| Ejemplo | ¿Agente? | Por qué |
|---|---|---|
| ChatGPT respondiendo una pregunta | No | Solo genera texto, no actúa |
| ChatGPT con Code Interpreter resolviendo un dataset | Sí (limitado) | Percibe datos, escribe y ejecuta código, entrega resultado |
| Bot de RPA que llena formularios según un script fijo | No | Sigue pasos rígidos, no razona |
| Sistema que monitorea emails, clasifica urgencia y agenda reuniones solo | Sí | Percibe, decide y actúa de forma autónoma hacia un objetivo |
| Copilot de GitHub completando código | No | Sugiere, pero el humano decide y ejecuta cada acción |
| Agente de investigación que busca en la web, resume y redacta un informe | Sí | Ciclo autónomo completo hacia un objetivo definido |

---

## Por qué importa la distinción

Llamar "agente" a cualquier cosa inteligente genera expectativas falsas:

- Un **LLM** puede fallar sin que nadie lo note (no tiene objetivos, no verifica).
- Un **agente mal diseñado** puede tomar acciones irreversibles (borrar archivos, enviar emails, gastar dinero).
- Entender qué es un agente real permite **diseñar salvaguardas** (límites de acción, aprobación humana, auditoría de decisiones).

> La potencia de un agente viene de su autonomía. Su riesgo, también.
