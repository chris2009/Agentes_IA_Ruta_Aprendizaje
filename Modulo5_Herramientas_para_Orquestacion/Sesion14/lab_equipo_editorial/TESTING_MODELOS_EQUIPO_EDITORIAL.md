# Testing de modelos — Equipo Editorial Multiagente (`main.py`)

## Contexto

Este documento registra un testing comparativo de distintos backends de **LLM** (Large Language Model, modelo de lenguaje grande) sobre el equipo editorial multiagente de este lab: un **Agente Editor en Jefe** que orquesta a otros dos agentes — **Agente Investigador** y **Agente Editor de Estilo** — invocándolos como *tools*.

**Por qué esta prueba es más exigente que la de `01_simple_reflex_agent.py` (Sesión 10):** en aquel testing, el modelo solo debía invocar una tool "plana" (una función Python simple). Acá, el Editor en Jefe debe invocar tools cuya ejecución implica correr **otro agente completo** (`investigador.invoke(...)`, `editor_estilo.invoke(...)`), y encadenar correctamente varios pasos: investigar → redactar → pulir estilo → entregar. Un fallo de *tool calling* acá no solo pierde un dato: rompe toda la cadena de colaboración entre agentes.

Tarea usada en las 3 corridas (idéntica): `TEMA = "El impacto de la IA generativa en los empleos de desarrollo de software junior"`.

El script permite cambiar de backend sin tocar el resto del código, vía la variable `AGENT_MODEL` en `_utils.py` (o la variable de entorno del mismo nombre).

## Backends evaluados

| `AGENT_MODEL` | Nombre completo / descripción | Proveedor | Costo |
|---|---|---|---|
| `gemma-lmstudio` | Gemma 4 E4B (Google) | LM Studio (servidor local en GPU, **API** — Application Programming Interface — compatible con OpenAI) | Gratis (hardware propio) |
| `llama3.2` | Llama 3.2 (Meta) | Ollama (local) | Gratis (hardware propio) |
| `phi4-mini` | Phi-4-mini (Microsoft) | Ollama (local) | Gratis (hardware propio) |
| *(referencia)* `claude-sonnet-5` | Claude Sonnet 5 (Anthropic) | API de Anthropic (nube) | De pago (créditos) |

La fila de Claude se incluye solo como referencia de comportamiento "ideal" — fue el backend usado antes de migrar el lab a LM Studio para no gastar créditos (ver conversación).

---

## Resultado: `gemma-lmstudio` (Gemma 4 E4B vía LM Studio)

**Flujo ejecutado:** 1 llamada real a `consultar_investigador` → redacción de borrador → 1 llamada real a `consultar_editor_estilo` → artículo final entregado.

| Paso | ¿Se ejecutó de verdad? |
|---|---|
| `consultar_investigador` | ✅ Sí (1 vez) |
| Redacción de borrador con los datos recibidos | ✅ Sí |
| `consultar_editor_estilo` | ✅ Sí (1 vez) |
| Entrega de artículo final pulido | ✅ Sí |

Artículo final entregado: *"Más allá del código repetitivo: Cómo la IA está redefiniendo las habilidades esenciales para el desarrollador junior"* — 5 secciones, coherente, sin datos inventados fuera de lo que trajo el investigador.

**Resultado: flujo completo 100% correcto**, igual que en el testing de la Sesión 10.

---

## Resultado: `llama3.2` (Ollama)

**Flujo ejecutado:** 1 llamada real a `consultar_investigador` → redacción de un borrador → **nunca llamó a `consultar_editor_estilo`** → entregó el borrador sin pulir como si fuera el artículo final.

```
[TOOL CALL] consultar_investigador(pregunta='El impacto de la IA generativa en los empleos de desarrollo de software junior')
[TOOL RESULT] consultar_investigador -> **Breve de Investigación** ...

ARTICULO FINAL
**Borrador del Artículo**
...
```

| Paso | ¿Se ejecutó de verdad? |
|---|---|
| `consultar_investigador` | ✅ Sí (1 vez) |
| Redacción de borrador | ✅ Sí |
| `consultar_editor_estilo` | ❌ No — se saltó el paso obligatorio |
| Entrega de artículo final pulido | ❌ No — entregó el borrador sin pasar por edición de estilo |

**Además, alucinó una cita**: el texto final incluye *"según un estudio de McKinsey, 'El impacto de la IA en el mercado laboral'"* — un título de estudio específico que **no existe** en `fuentes_investigacion.json` ni fue devuelto por el investigador (la base solo menciona a McKinsey de forma genérica, sin ese título). El modelo inventó una fuente con apariencia de cita real.

**Resultado: flujo incompleto (se saltó un paso obligatorio del protocolo) + alucinación de una cita académica falsa.**

---

## Resultado: `phi4-mini` (Ollama)

**Flujo ejecutado:** ninguno. El modelo nunca invocó ninguna tool real.

```
ARTICULO FINAL
[{"name": "consultar_investigador", "arguments": {"pregunta": "¿Qué impactos tiene la IA generativa sobre los empleos de desarrolladores juniors, especialmente en el área del desarrollo de software?"}}]
```

| Paso | ¿Se ejecutó de verdad? |
|---|---|
| `consultar_investigador` | ❌ No — solo generó el JSON como texto plano |
| Redacción de borrador | ❌ No |
| `consultar_editor_estilo` | ❌ No |
| Entrega de artículo final pulido | ❌ No |

El "artículo final" entregado es literalmente el JSON crudo que *debería* haber sido una tool call real, pero quedó como texto sin interpretar — el mismo patrón de falla ya diagnosticado en la Sesión 10 (el modelo no logra emitir los tokens especiales `<|tool_call|>...<|/tool_call|>` que Ollama necesita para reconocerlo como invocación real).

**Resultado: 0% funcional — ni siquiera arrancó el flujo.**

---

## Tabla comparativa final

| Backend | `consultar_investigador` real | `consultar_editor_estilo` real | Artículo final entregado | Observaciones |
|---|---|---|---|---|
| `gemma-lmstudio` (Gemma 4 E4B) | ✅ | ✅ | ✅ Completo y pulido | 100% confiable, igual que en la Sesión 10 |
| `llama3.2` | ✅ | ❌ | ⚠️ Borrador sin pulir, entregado como si fuera final | Se salta un paso del protocolo + alucina una cita académica falsa |
| `phi4-mini` | ❌ | ❌ | ❌ JSON crudo sin ejecutar | No logra emitir ninguna tool call real, ni la primera |
| *(ref.)* `claude-sonnet-5` | ✅ (3 veces) | ✅ | ✅ Completo y pulido | Más exhaustivo investigando (3 consultas vs. 1), pero de pago |

### Conclusión

En una arquitectura de **agentes anidados** (un agente que invoca a otros agentes como tools), la brecha de confiabilidad entre backends se agranda respecto al testing de tool-calling simple de la Sesión 10:

- `phi4-mini` repite exactamente su patrón de falla total ya diagnosticado.
- `llama3.2` mejora respecto a su resultado anterior (sí ejecuta la primera tool call), pero **introduce un riesgo nuevo y más grave que un simple "no ejecutó la tool": alucina una fuente académica con apariencia de real**, y encima incumple el protocolo saltándose la revisión de estilo — en un flujo editorial real esto podría publicar una cita falsa sin que nadie lo note.
- `gemma-lmstudio` vuelve a ser el único backend local 100% confiable ejecutando la cadena completa, confirmando el hallazgo de la Sesión 10 en un escenario más complejo.

Para esta arquitectura de multiagentes con tools anidadas, **Gemma 4 E4B vía LM Studio es, otra vez, la única opción local viable**; `llama3.2` es utilizable solo con supervisión humana estricta de las citas que genera, y `phi4-mini` no es viable en absoluto para tool calling en este pipeline.
