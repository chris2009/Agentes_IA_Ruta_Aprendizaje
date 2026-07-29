# CLAUDE.md — Proyecto Final: Clemente para Restaurantes

Contexto persistente para trabajar en este proyecto en sesiones futuras.
Programa en Diseño e Implementación de Agentes IA (UTEC Posgrado),
Módulo 4 — Agentes Cognitivos. Proyecto grupal; colaborador conocido:
Jesús Barboza (`github.com/JesusBarboza1994/ai_agents_utec`).

## Qué es Clemente

Asistente conversacional para restaurantes. El caso de estudio completo
está en [`Idea - Clemente para Restaurantes Caso de Estudio.md`](Idea%20-%20Clemente%20para%20Restaurantes%20Caso%20de%20Estudio.md).
Resumen: Clemente ya resuelve atención conversacional, reservas,
conocimiento operativo (FAQs/políticas), perfil de cliente y feedback.
**Pendiente** (fuera del alcance de las Tareas 1-2, no implementar sin que
se pida explícitamente): flujo de delivery/recojo, sistema de incidencias
con seguimiento, visión computacional para ocupación de mesas, y evolución
hacia un sistema **multiagente** orquestado (hoy es un solo agente).

## Dónde está "lo mejor de la clase" (leer antes de tocar Tarea 2+)

Cada sesión del curso tiene un `..._ANALISIS_COMPLETO.md` en
`../Modulo4_Agentes_Cognitivos/`. Son la fuente de verdad de la rúbrica —
antes de generar o corregir un Profile Card o un script, releer:

- `Sesion8_Arquitectura_Agentes/Sesion08_..._ANALISIS_COMPLETO.md` — las 5
  capas del Agent Profile Card (Communication → Context → Environment →
  Autonomy → Criticality) y la plantilla exacta del Lab 1.
- `Sesion9_Agentes_Memoria_Contextual/Sesion09_..._ANALISIS_COMPLETO.md` —
  Context Window (ventana de contexto: el espacio de tokens que realmente
  llega al modelo en una llamada) como recurso escaso, las 5 memorias de
  **CoALA** (*Cognitive Architectures for Language Agents*, arquitecturas
  cognitivas para agentes de lenguaje — framework académico de Sumers et
  al. 2023 que formaliza la memoria episódica, semántica, procedimental,
  de largo plazo y de corto plazo de un agente), y la plantilla del Lab 3
  (§16.1) que exige declarar presupuesto de tokens + las 5 memorias.
- `Sesion10_Agentes_Reflexivos/Sesion10_..._ANALISIS_COMPLETO.md` — los 5
  tipos de agente reflexivo IBM/Russell-Norvig (Simple Reflex,
  Model-Based, Goal-Based, Utility-Based, Learning), su formalización y la
  tarea final: "Actualizar el Profile Card acorde a memoria y tipo(s) de
  agentes reflexivos. Deadline 22-07."

## Estructura de este directorio

```
Proyecto_Final/
  Idea - Clemente para Restaurantes Caso de Estudio.md   # caso de estudio / alcance
  clemente-restaurantes.html                              # mockup visual temprano
  Tarea_1/
    agent_card_profile_reserva_v2.html                    # ENTREGABLE Tarea 1 (canónico)
    agent_card_profile_reserva_v1.html                    # borrador anterior
    clemente-nuevos-agentes-card-profile.html              # exploración de agentes adicionales
  Tarea_2/
    agent_card_profile_reserva_context_memory_reflex_v3.html  # ENTREGABLE Tarea 2 (canónico)
    agent_card_profile_reserva_context_memory_reflex_v2.html  # borrador "Fase 2 Corregido"
    agent_card_profile_reserva_context_memory_reflex_v1.html  # borrador "Fase 2" (más completo en CoALA/tokens)
    agente_reservas_clemente_langchain.py                  # prototipo alterno (Anthropic + JSON), NO canónico
    pruebas/Agente_Reservas/
      01_model_based_reflex_agent.py                       # ENTREGABLE — Model-Based Reflex
      02_goal_based_agent.py                                # ENTREGABLE — Goal-Based
      03_utility_based_agent.py                             # ENTREGABLE — Utility-Based
      04_unified_agent.py                                   # ENTREGABLE — unifica 1+2+3 (agente de producto)
      README.md                                             # justificación de la elección de tipos
  repositorio_proyecto_final/ai_agents_utec/                # clon del repo del compañero Jesús Barboza (referencia)
```

## Decisiones de diseño ya tomadas (no re-litigar sin nueva evidencia)

1. **Solo 3 de los 5 tipos de agente reflexivo se implementan**:
   Model-Based, Goal-Based, Utility-Based. Simple Reflex se descarta como
   arquitectura base porque el Profile Card exige memoria explícita (un
   reflejo simple no tiene estado); sobrevive como *patrón* dentro de los
   guardrails de los otros agentes (ej. "sin confirmación explícita → no
   registrar"). Learning se descarta porque no hay señal de feedback real
   definida todavía (no-show, cancelación, corrección del staff) — es
   roadmap v2, no un olvido. Esta decisión está documentada en
   `pruebas/Agente_Reservas/README.md` y en la card v3, sección 4.
2. **Los scripts `01/02/03` son deliberadamente didácticos** (un tipo de
   agente por archivo, sin apilar) y **el `04` es el agente de producto**
   que los une. No colapsar `01/02/03` en uno solo: la separación es el
   valor pedagógico pedido por el lab.
3. **Convención de scripts**: LangChain 1.x `create_agent` + Ollama
   `llama3.2`, cada archivo 100% autocontenido (sin imports entre sí),
   mini-entorno de restaurante simulado con diccionarios en memoria
   (`MESAS`, `TURNOS_VALIDOS`, `RESERVAS_OCUPADAS`, `PERFILES_CLIENTES`).
   Mantener esta convención en cualquier script nuevo de esta carpeta.
4. **`agente_reservas_clemente_langchain.py`** (raíz de Tarea_2) es un
   prototipo alterno e independiente: usa Anthropic en vez de Ollama y
   persistencia en JSON/JSONL real (no diccionarios en memoria). Se
   documenta como referencia, **no es el entregable canónico** — no
   asumir que hay que mantenerlo sincronizado con `pruebas/Agente_Reservas`.
5. **Idioma de las cards**: Tarea 1 está en inglés (mismo idioma del
   template original de Sesión 8). Tarea 2 está en español. No traducir
   una a la otra sin que se pida.
6. **`repositorio_proyecto_final/ai_agents_utec/`** es un clon del repo de
   un compañero de equipo (Jesús Barboza), no un fork propio. Útil como
   referencia/diff, pero no editar ahí directamente — cualquier mejora que
   valga la pena se porta a `Tarea_2/pruebas/Agente_Reservas/`.

## Estado de las entregas

| Tarea | Entregable | Estado |
|---|---|---|
| Tarea 1 | Agent Profile Card (arquitectura de 5 capas) | Completo |
| Tarea 2 | Profile Card actualizado con Context Engineering + memoria CoALA + tipos reflexivos | Completo (`v3`) |
| Tarea 2 | Script(s) Python en LangChain de los tipos reflexivos elegidos | Completo (`01-04` en `pruebas/Agente_Reservas`) |
| — | Delivery/recojo, incidencias, visión computacional, multiagente | No iniciado (ver caso de estudio) |

## Convenciones al documentar avances aquí

Actualizar [`README.md`](README.md) de esta carpeta (bitácora legible) cada
vez que se cierre una tarea nueva, y este `CLAUDE.md` solo cuando cambien
decisiones de arquitectura o la estructura de carpetas — no duplicar
contenido entre ambos: el README cuenta la historia, este archivo fija las
reglas que no hay que romper.
