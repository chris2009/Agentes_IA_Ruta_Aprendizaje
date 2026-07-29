# agents26_m4s10 — Tipos de agentes de IA con LangChain + Ollama

Repositorio **tutorial**: cada tipo de agente se explica y ejecuta **por
separado**. No hay ningún sistema conectado entre archivos — cada script
y su notebook gemelo son 100% autocontenidos y pueden ejecutarse de
forma independiente.

Implementa, con la API **actual** de LangChain (`create_agent`,
LangChain 1.x sobre LangGraph 1.x) y un modelo local **`llama3.2`
servido por Ollama**, los 5 tipos de agentes de IA descritos por IBM:

> https://www.ibm.com/think/topics/ai-agent-types

## Requisitos previos

1. [Ollama](https://ollama.com) instalado y corriendo localmente.
2. Descargar el modelo:
   ```bash
   ollama pull llama3.2
   ```
3. Instalar dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```

## Estructura

Cada tipo de agente vive en **un único archivo autocontenido** (script +
notebook), con su propio mini "entorno" simulado incluido — sin
dependencias de otros archivos del repo:

| # | Tipo de agente (IBM)     | Script                            | Notebook                              |
|---|----------------------------|-------------------------------------|------------------------------------------|
| 1 | Simple reflex agent        | `01_simple_reflex_agent.py`         | `01_simple_reflex_agent.ipynb`            |
| 2 | Model-based reflex agent   | `02_model_based_reflex_agent.py`    | `02_model_based_reflex_agent.ipynb`       |
| 3 | Goal-based agent           | `03_goal_based_agent.py`            | `03_goal_based_agent.ipynb`               |
| 4 | Utility-based agent        | `04_utility_based_agent.py`         | `04_utility_based_agent.ipynb`            |
| 5 | Learning agent             | `05_learning_agent.py`              | `05_learning_agent.ipynb`                 |

## Cómo se mapea cada tipo de agente a LangChain

| Tipo IBM | Idea central según IBM | Cómo se implementa aquí |
|---|---|---|
| Simple reflex | Reacciona a la percepción actual con reglas condición-acción; **sin memoria** | `create_agent` sin `checkpointer`/estado persistente; cada invocación es independiente; `system_prompt` con reglas explícitas de umbral |
| Model-based reflex | Mantiene un **modelo interno** del estado del mundo para decidir | `state_schema` propio (`mapa_conocido`) actualizado por una tool que devuelve `Command`, y `@dynamic_prompt` que inyecta ese modelo interno en cada paso |
| Goal-based | Planifica una secuencia de acciones para alcanzar un **objetivo explícito** | Bucle ReAct estándar de `create_agent` con tools de navegación (BFS) y `system_prompt` orientado a la meta |
| Utility-based | Compara **múltiples opciones** con una función de utilidad y elige la de mayor score | Tool `evaluar_opcion_envio` que pondera tiempo/costo/seguridad; el `system_prompt` exige comparar antes de decidir |
| Learning | **Aprende de feedback** (crítico + refuerzo) y ajusta su comportamiento futuro | Tools de lectura/escritura sobre un JSON local (`05_learning_store.json`), que persiste entre ejecuciones de ese mismo script |

## Notas

- El identificador de modelo `"ollama:llama3.2"` se resuelve automáticamente
  a `ChatOllama(model="llama3.2")` gracias a la inferencia de proveedor de
  `init_chat_model` (usada internamente por `create_agent`).
- Cada script imprime resultados al ejecutarse directamente
  (`python 0X_....py`) y también expone funciones reutilizables
  (p. ej. `revisar_zona`, `cumplir_orden`) por si quieres importarlas o
  llamarlas desde el notebook correspondiente.
- Todo el código fue validado sintáctica y estructuralmente (compilación
  + construcción real del agente) contra `langchain==1.3.13`,
  `langgraph==1.2.9` y `langchain-ollama==1.1.0`.
# agents26_m4s10
