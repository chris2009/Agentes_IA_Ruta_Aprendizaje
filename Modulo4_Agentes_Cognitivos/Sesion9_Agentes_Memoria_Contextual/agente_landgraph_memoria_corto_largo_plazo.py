"""
# Agente LangGraph con memoria a corto y largo plazo
####################################################

Ejemplo: Agente LangGraph con memoria a corto plazo configurable
(varias estrategias) + traspaso a memoria a largo plazo.

MEMORIA A CORTO PLAZO (thread-scoped, vive en el checkpointer)
Se puede gestionar de varias formas. Este ejemplo implementa 4 estrategias
seleccionables en caliente vía el objeto `Context` (parámetro `context=`
de graph.invoke(), accesible dentro del nodo como `runtime.context`):

  "full"        -> Sin gestión: se envía todo el historial al LLM.
                   Simple, pero crece sin límite (tokens/costo/latencia).

  "trim_count"  -> Se borran físicamente del checkpoint los mensajes más
                   antiguos, quedándose con las últimas N interacciones
                   (usa RemoveMessage). Barato y predecible, pero pierde
                   contexto antiguo sin dejar rastro.

  "trim_tokens" -> NO se modifica el estado guardado. Justo antes de
                   llamar al modelo se genera una copia recortada por
                   presupuesto de tokens (trim_messages). El historial
                   completo se conserva en el checkpoint.

  "summary"     -> Los mensajes antiguos se condensan en un resumen
                   (campo `summary` en el estado) y luego se eliminan
                   del historial. Comprime en vez de descartar sin más.

MEMORIA A LARGO PLAZO (cross-thread, vive en el store)
Sigue igual que antes: namespaced por user_id, sobrevive a nuevos threads.
El traspaso corto -> largo plazo ocurre cuando detectamos un dato que vale
la pena persistir y lo escribimos con store.put(...).

Requisitos:
    pip install -U langgraph langchain langchain-ollama

    # Ollama debe estar corriendo localmente y con el modelo descargado:
    #   ollama pull llama3.2
    #   ollama serve   (si no se inicia solo)
    #
    # Opcional: un modelo más chico/rápido para resumir (estrategia "summary").
    # Si no lo descargas, el código usa llama3.2 también para eso.
    #   ollama pull llama3.2:1b

"""

import uuid
from dataclasses import dataclass
from typing import Any, Optional

from langchain_ollama import ChatOllama
from langchain_core.messages import RemoveMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.runtime import Runtime


@dataclass
class Context:
    """Configuración de un run: no forma parte del estado del grafo,
    se pasa vía `context=` en invoke() y se lee con `runtime.context`."""
    user_id: str
    memory_strategy: str = "full"  # "full" | "trim_count" | "trim_tokens" | "summary"

# ---------------------------------------------------------------------------
# 1. Modelo y estado
# ---------------------------------------------------------------------------
# Modelo principal para conversar. Si tienes suficiente RAM/VRAM y quieres
# más calidad, puedes usar "llama3.2:3b" (por defecto) o "llama3.1:8b".
model = ChatOllama(model="llama3.2", temperature=0.3)

# Modelo para generar resúmenes cuando se usa la estrategia "summary".
# Por defecto reutiliza el mismo modelo que ya tienes descargado (llama3.2)
# para no depender de un segundo pull. Si más adelante descargas un modelo
# más chico (ollama pull llama3.2:1b), puedes apuntar aquí para que sea
# más rápido/barato.
summarizer_model = ChatOllama(model="llama3.2", temperature=0)


class State(MessagesState):
    summary: str  # solo se usa con la estrategia "summary"


# ---------------------------------------------------------------------------
# 2. Estrategias de memoria a corto plazo
# ---------------------------------------------------------------------------
def mensajes_full(state: State) -> list:
    """Sin gestión: todo el historial tal cual."""
    return state["messages"]


def mensajes_trim_count(state: State, keep_last: int = 4) -> list:
    """Recorta el ESTADO guardado, dejando solo los últimos `keep_last`
    mensajes. Devuelve además las instrucciones de borrado para el nodo."""
    messages = state["messages"]
    if len(messages) <= keep_last:
        return messages
    return messages[-keep_last:]


def mensajes_trim_tokens(state: State, max_tokens: int = 800) -> list:
    """No toca el estado guardado: solo genera una copia recortada por
    presupuesto de tokens para esta llamada al modelo."""
    return trim_messages(
        state["messages"],
        max_tokens=max_tokens,
        strategy="last",          # se queda con los mensajes más recientes
        token_counter=count_tokens_approximately,
        start_on="human",         # evita cortar a mitad de un turno
        include_system=True,
    )


def resumir_si_hace_falta(state: State, threshold: int = 6) -> Optional[dict]:
    """Si hay demasiados mensajes, resume los antiguos en `summary` y
    los elimina del checkpoint, dejando solo los últimos 2 (turno actual)."""
    messages = state["messages"]
    if len(messages) <= threshold:
        return None

    a_resumir = messages[:-2]
    resto = messages[-2:]

    prompt_resumen = (
        "Resume brevemente los datos relevantes de esta conversación "
        "(nombres, preferencias, hechos importantes). "
        f"Resumen previo: {state.get('summary', '(vacío)')}\n\n"
        f"Nuevos mensajes a incorporar: {[m.content for m in a_resumir]}"
    )
    nuevo_resumen = summarizer_model.invoke(prompt_resumen).content

    return {
        "summary": nuevo_resumen,
        "messages": [RemoveMessage(id=m.id) for m in a_resumir],
        "_resto": resto,
    }


# ---------------------------------------------------------------------------
# 3. Nodo del agente
# ---------------------------------------------------------------------------
def call_model(state: State, runtime: Runtime[Context]) -> dict[str, Any]:
    estrategia = runtime.context.memory_strategy
    user_id = runtime.context.user_id
    store = runtime.store
    namespace = ("memorias", user_id)

    # --- Memoria a largo plazo: leer datos persistentes del usuario ---
    memorias_guardadas = store.search(namespace)
    contexto_usuario = "\n".join(m.value["dato"] for m in memorias_guardadas)

    system_msg = (
        "Eres un asistente útil. Datos que recuerdas de este usuario "
        f"de conversaciones pasadas:\n{contexto_usuario or '(sin datos aún)'}"
    )
    if state.get("summary"):
        system_msg += f"\n\nResumen de la conversación actual hasta ahora:\n{state['summary']}"

    # --- Aplicar la estrategia de memoria a corto plazo elegida ---
    state_update: dict[str, Any] = {}
    if estrategia == "trim_count":
        mensajes_para_llm = mensajes_trim_count(state)
        # también recortamos el estado persistido (borrado real)
        a_borrar = state["messages"][: -len(mensajes_para_llm)] if len(state["messages"]) > len(mensajes_para_llm) else []
        state_update["messages"] = [RemoveMessage(id=m.id) for m in a_borrar]
    elif estrategia == "trim_tokens":
        mensajes_para_llm = mensajes_trim_tokens(state)  # no modifica el estado
    elif estrategia == "summary":
        resultado = resumir_si_hace_falta(state)
        if resultado:
            state_update["summary"] = resultado["summary"]
            state_update["messages"] = resultado["messages"]
            mensajes_para_llm = resultado["_resto"]
        else:
            mensajes_para_llm = state["messages"]
    else:  # "full"
        mensajes_para_llm = mensajes_full(state)

    respuesta = model.invoke([{"role": "system", "content": system_msg}] + mensajes_para_llm)

    # --- Traspaso de corto -> largo plazo -------------------------------
    ultimo_mensaje = state["messages"][-1].content if state["messages"] else ""
    if isinstance(ultimo_mensaje, str) and "recuerda que" in ultimo_mensaje.lower():
        dato = ultimo_mensaje.lower().split("recuerda que", 1)[1].strip()
        store.put(namespace, str(uuid.uuid4()), {"dato": dato})

    state_update["messages"] = state_update.get("messages", []) + [respuesta]
    return state_update


# ---------------------------------------------------------------------------
# 4. Construcción del grafo
# ---------------------------------------------------------------------------
builder = StateGraph(State, context_schema=Context)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")

checkpointer = InMemorySaver()   # memoria a corto plazo (thread_id, vía config)
store = InMemoryStore()          # memoria a largo plazo (user_id, vía context)

graph = builder.compile(checkpointer=checkpointer, store=store)

# ---------------------------------------------------------------------------
# 5. Demo: la misma conversación con distintas estrategias
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    for estrategia in ["full", "trim_count", "trim_tokens", "summary"]:
        print(f"\n=== Estrategia: {estrategia} ===")
        # config: identifica el hilo de conversación (para el checkpointer)
        config = {"configurable": {"thread_id": f"conv-{estrategia}"}}
        # context: parámetros de este run (se leen con runtime.context dentro del nodo)
        context = Context(user_id="usuario-123", memory_strategy=estrategia)

        for texto in [
            "Hola, me llamo Marta.",
            "Trabajo como ingeniera de datos.",
            "Recuerda que soy alérgica al maní.",
            "¿De qué trabajo te dije que trabajaba?",
        ]:
            resultado = graph.invoke(
                {"messages": [{"role": "user", "content": texto}]},
                config=config,
                context=context,
            )
            print(f"Usuario: {texto}\nAgente: {resultado['messages'][-1].content}\n")