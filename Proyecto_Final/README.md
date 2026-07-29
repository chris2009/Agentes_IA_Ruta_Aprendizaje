# Proyecto Final — Clemente para Restaurantes

Bitácora del proyecto final del Programa en Diseño e Implementación de
Agentes IA (UTEC Posgrado, Módulo 4 — Agentes Cognitivos). Este archivo
registra qué se entregó en cada tarea y por qué; las reglas de diseño que
no hay que romper están en [`CLAUDE.md`](CLAUDE.md).

## El proyecto: Clemente

Clemente es un agente conversacional para restaurantes. El alcance completo
del caso de estudio (qué ya resuelve, qué falta, y la propuesta de
evolución a un sistema multiagente) está en
[`Idea - Clemente para Restaurantes Caso de Estudio.md`](Idea%20-%20Clemente%20para%20Restaurantes%20Caso%20de%20Estudio.md).
En resumen: hoy Clemente atiende conversaciones, gestiona reservas,
centraliza conocimiento operativo (horarios, políticas), conserva perfil
de cliente y recoge feedback. Quedan pendientes: delivery/recojo,
seguimiento de incidencias, visión computacional para ocupación de mesas,
y una arquitectura multiagente (hoy es un solo agente).

## Tarea 1 — Agent Profile Card (arquitectura del agente)

**Entregable:** [`Tarea_1/agent_card_profile_reserva_v2.html`](Tarea_1/agent_card_profile_reserva_v2.html)

Primer Profile Card de "Clemente Reservations", siguiendo la arquitectura
de 5 capas enseñada en la Sesión 8 del curso (Communication Layer →
Context Definition → Environment Definition → Autonomy Dimension →
Criticality Dimension). Define:

- Canal: WhatsApp, Messenger, Instagram, Webchat.
- Objetivo: capturar intención, ofrecer horarios disponibles, confirmar
  reservas y reducir carga operativa del equipo humano.
- Memoria: Long Term (nombre, teléfono, preferencias, alergias, zona
  favorita, historial) y Short Term (fecha, hora, personas, ocasión,
  notas, opción elegida) — declaradas, pero todavía sin especificar *cómo*
  se implementan.
- Autonomía: semi-autónomo (evalúa y recomienda, guía y escala casos
  especiales).
- Criticidad: riesgos declarados (disponibilidad desactualizada, alergias,
  alucinación) con sus guardrails asociados (verificación en tiempo real,
  confirmación explícita, trazabilidad, escalamiento tras fallos).

Esta card fue la base para todo lo que sigue: Tarea 2 no la reemplaza,
la profundiza.

## Tarea 2 — Context Engineering, Memoria y Agentes Reflexivos

**Entregables:**
- [`Tarea_2/agent_card_profile_reserva_context_memory_reflex_v3.html`](Tarea_2/agent_card_profile_reserva_context_memory_reflex_v3.html) — Profile Card actualizado (canónico).
- [`Tarea_2/pruebas/Agente_Reservas/`](Tarea_2/pruebas/Agente_Reservas/) — 4 scripts en LangChain.

### Qué pide la Sesión 9 y la Sesión 10

La Sesión 9 pide declarar el **Context Engineering** (presupuesto de
tokens del Context Window por componente: system prompt, input, RAG,
docstrings de tools, output) y la **arquitectura de memoria** completa
(las 5 memorias del framework CoALA: episódica, semántica, procedimental,
largo plazo y corto plazo). La Sesión 10 pide clasificar el agente según
los 5 tipos de **agente reflexivo** de IBM / Russell-Norvig (Simple
Reflex, Model-Based, Goal-Based, Utility-Based, Learning) y justificar la
elección con un script en Python que lo implemente con LangChain.

### Iteración del Profile Card: v1 → v2 → v3

1. **v1** ("Fase 2"): versión más rica — declara los 5 memorias CoALA y
   los 5 tipos de agente reflexivo con su estado, más un presupuesto de
   tokens detallado por componente del Context Window.
2. **v2** ("Fase 2 Corregido"): simplifica v1 para alinearse 1:1 con los
   3 scripts que ya existían en `pruebas/Agente_Reservas` (Model-Based,
   Goal-Based, Utility-Based), descartando explícitamente Simple Reflex y
   Learning. Gana consistencia código-documento, pero pierde el
   presupuesto de tokens y la mención explícita de memoria episódica y
   semántica.
3. **v3** (actual, canónica): recupera de v1 el presupuesto de Context
   Window y las 5 memorias CoALA (declarando cuáles son primarias —
   short-term y long-term— y cuáles son parciales o roadmap — procedural,
   semantic, episodic), mantiene la decisión de v2 de solo 3 tipos de
   agente reflexivo implementados, y agrega el inventario de los 4 scripts
   Python (incluyendo el nuevo agente unificado).

### Los 3 tipos de agente reflexivo elegidos (de 5 posibles)

| Tipo IBM | Estado | Por qué |
|---|---|---|
| Model-Based Reflex | Implementado (`01`) | El Profile Card exige memoria explícita (long/short term) — es, literalmente, la definición de agente con modelo interno del mundo. |
| Goal-Based | Implementado (`02`) | La Autonomy Dimension dice que el agente "guía la reserva y escala casos especiales" — persigue una meta, no solo reacciona. |
| Utility-Based | Implementado (`03`) | Cuando hay varias franjas válidas, el agente debe recomendar una sopesando horario, zona y uso eficiente de la mesa. |
| Simple Reflex | Descartado como base | No tiene memoria; choca con la exigencia de memoria explícita del Profile Card. Sobrevive como *patrón* dentro de los guardrails de los otros 3 (ej. "sin confirmación explícita → no registrar"). |
| Learning | Descartado por ahora | No existe todavía una señal de feedback real (no-show, cancelación, corrección del staff) que un crítico pueda usar. Es la evolución v2 más clara del sistema. |

### Los 4 scripts en `pruebas/Agente_Reservas/`

- `01_model_based_reflex_agent.py` — mantiene `perfil_cliente` (long-term)
  y `borrador_reserva` (short-term) en el estado del grafo, inyectados en
  cada turno vía `dynamic_prompt`.
- `02_goal_based_agent.py` — persigue la meta de una reserva confirmada:
  busca alternativas si la hora pedida no está libre, exige confirmación
  explícita, y escala tras fallos repetidos.
- `03_utility_based_agent.py` — calcula una función de utilidad explícita
  (score de horario + zona + ajuste de capacidad) para recomendar entre
  varias opciones válidas.
- `04_unified_agent.py` — **agente de producto**: colapsa los tres
  anteriores en un solo flujo coherente, con utilidad adaptable (cliente
  conocido vs. nuevo) y una regla reactiva de orientación temprana.
  Adaptado del aporte de equipo de Jesús Barboza
  (`github.com/JesusBarboza1994/ai_agents_utec`), que construyó este
  agente unificado sobre los mismos `01/02/03`.

Justificación completa, tabla de cumplimiento de rúbrica y cómo ejecutar
cada script: [`Tarea_2/pruebas/Agente_Reservas/README.md`](Tarea_2/pruebas/Agente_Reservas/README.md).

### Prototipo alterno (no canónico)

[`Tarea_2/agente_reservas_clemente_langchain.py`](Tarea_2/agente_reservas_clemente_langchain.py)
es una exploración independiente: un solo archivo con Anthropic (en vez de
Ollama) y persistencia real en JSON/JSONL (en vez de diccionarios en
memoria), con el set completo de tools de la card (`check_availability`,
`create_reservation_request`, `escalate_to_staff`, etc.). Se documenta
como referencia; el entregable evaluable de la Tarea 2 son los 4 scripts
de `pruebas/Agente_Reservas/`.

## Próximos pasos (fuera del alcance de Tareas 1-2)

Del caso de estudio, en orden de prioridad sugerido:
1. Flujo completo de delivery y recojo en tienda.
2. Sistema de seguimiento de incidencias (`incidencia → responsable →
   plazo → solución → confirmación`).
3. Piloto de visión computacional para eventos de ocupación (sin
   reconocimiento facial ni identificación individual persistente).
4. Evolución de agente único a sistema multiagente orquestado (separar
   primero Reservas/Capacidad de Pedidos/Fulfillment).
