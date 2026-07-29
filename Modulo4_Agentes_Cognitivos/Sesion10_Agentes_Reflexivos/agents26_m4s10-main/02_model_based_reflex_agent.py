"""
02_model_based_reflex_agent.py
--------------------------------
MODEL-BASED REFLEX AGENT
(IBM: https://www.ibm.com/think/topics/model-based-reflex-agent)

"Incorpora un modelo interno del mundo que le permite recordar cómo sus
interacciones pasadas afectaron el entorno, incluso cuando este es
parcialmente observable."

Ejemplo: un robot que explora el almacén celda por celda. A diferencia
del agente reflejo simple, aquí SÍ hay memoria: el robot va construyendo
un mapa interno (`mapa_conocido`) de qué celdas ya visitó y cuáles son
obstáculos, y ese mapa se usa para no repetir errores.

Este archivo es completamente autocontenido: no depende de ningún otro
archivo del repositorio (solo de librerías externas). Puedes ejecutarlo
de forma independiente.

Ejecutar:
    ollama pull llama3.2
    python 02_model_based_reflex_agent.py

Comparar backends de modelo (sin tocar código):
    AGENT_MODEL=llama3.2        python 02_model_based_reflex_agent.py   # default
    AGENT_MODEL=phi4-mini       python 02_model_based_reflex_agent.py   # ollama, ya descargado
    AGENT_MODEL=gemma-lmstudio  python 02_model_based_reflex_agent.py   # requiere LM Studio
                                                                         # con el "Local Server"
                                                                         # iniciado y
                                                                         # pip install langchain-openai
"""

import os
from typing import Annotated

from dotenv import load_dotenv
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.tools import tool, InjectedState, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command

load_dotenv()

AGENT_MODEL = os.environ.get("AGENT_MODEL", "llama3.2")


def _resolver_modelo(nombre: str):
    """Permite comparar el mismo agente con distintos backends de modelo
    sin tocar el resto del código -- solo cambia la variable de entorno
    AGENT_MODEL antes de correr el script."""
    if nombre == "gemma-lmstudio":
        # LM Studio expone un servidor local compatible con la API de
        # OpenAI (pestaña "Local Server" dentro de LM Studio). Import
        # diferido: si no vas a usar este backend, no hace falta tener
        # langchain-openai instalado.
        #
        # Si corres este script en WSL y LM Studio está en Windows,
        # "localhost" puede no resolver hacia el host. En ese caso define
        # LMSTUDIO_BASE_URL con la IP del host Windows visto desde WSL
        # (cat /etc/resolv.conf | grep nameserver), ej:
        #   LMSTUDIO_BASE_URL=http://172.x.x.1:1234/v1
        from langchain_openai import ChatOpenAI

        # Default ya apuntado a la IP de Windows vista desde WSL en esta
        # máquina (confirmado con: ip route show | grep -i default).
        base_url = os.environ.get("LMSTUDIO_BASE_URL", "http://172.30.32.1:1234/v1")
        return ChatOpenAI(
            model="google/gemma-4-e4b",
            base_url=base_url,
            api_key="lm-studio",  # LM Studio no valida la key, pero el cliente exige un valor no vacío
        )
    if nombre in ("llama3.2", "phi4-mini"):
        return f"ollama:{nombre}"
    raise ValueError(
        f"AGENT_MODEL desconocido: {nombre!r}. "
        "Opciones: llama3.2, phi4-mini, gemma-lmstudio"
    )


print(f"[CONFIG] Usando modelo: {AGENT_MODEL}")

# --- "Entorno" simulado (mínimo, solo lo que este agente necesita) --------

# Grid del almacén: 0 = pasillo libre, 1 = obstáculo (estantería / caja caída)
WAREHOUSE_GRID = [
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0],
]

DIRECCIONES = {"norte": (0, -1), "sur": (0, 1), "este": (1, 0), "oeste": (-1, 0)}


def _celda_libre(pos: tuple[int, int]) -> bool:
    x, y = pos
    if not (0 <= y < len(WAREHOUSE_GRID) and 0 <= x < len(WAREHOUSE_GRID[0])):
        return False
    return WAREHOUSE_GRID[y][x] == 0


# --- Estado del agente: aquí vive el MODELO INTERNO del mundo --------------
#
# IMPORTANTE: algunos modelos (incluido llama3.2 a veces) pueden emitir
# más de un tool call de `mover_robot` en un mismo turno (llamadas en
# "paralelo"). Si el campo del estado no tiene un reducer, LangGraph
# lanza `InvalidUpdateError: Can receive only one value per step` porque
# el canal por defecto (LastValue) solo acepta UNA escritura por paso.
# La solución recomendada por el propio error es usar una clave
# `Annotated[tipo, reducer]` que sepa combinar varias escrituras
# concurrentes dentro del mismo paso.


def _ultimo_valor(izquierda, derecha):
    """Reducer simple: si llegan varias escrituras en el mismo paso,
    nos quedamos con la última (equivalente al comportamiento que se
    esperaría de LastValue, pero sin lanzar error si hay >1)."""
    return derecha


def _fusionar_mapas(izquierda: dict, derecha: dict) -> dict:
    """Reducer para el mapa conocido: si dos tool calls concurrentes
    descubren celdas distintas en el mismo paso, se combinan ambas
    en vez de perder una."""
    combinado = dict(izquierda or {})
    combinado.update(derecha or {})
    return combinado


class EstadoRobot(AgentState):
    """Extiende el estado estándar del agente con el modelo interno."""
    posicion_actual: Annotated[tuple[int, int], _ultimo_valor]
    mapa_conocido: Annotated[dict[str, str], _fusionar_mapas]  # "x,y" -> "libre" | "obstaculo"


# --- Tool que percibe/actúa Y actualiza el modelo interno -------------------

@tool
def mover_robot(
    direccion: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Intenta mover el robot un paso en una dirección (norte/sur/este/oeste).
    Actualiza el modelo interno del mundo con lo que el robot percibe."""
    print(f"[TOOL CALL] mover_robot(direccion={direccion!r})")
    if direccion not in DIRECCIONES:
        contenido = f"Dirección inválida: {direccion}. Usa norte/sur/este/oeste."
        print(f"[TOOL RESULT] mover_robot -> {contenido}")
        return Command(update={"messages": [ToolMessage(contenido, tool_call_id=tool_call_id)]})

    x0, y0 = state.get("posicion_actual", (0, 0))
    dx, dy = DIRECCIONES[direccion]
    nueva_pos = (x0 + dx, y0 + dy)
    mapa = dict(state.get("mapa_conocido", {}))
    clave = f"{nueva_pos[0]},{nueva_pos[1]}"

    if _celda_libre(nueva_pos):
        mapa[clave] = "libre"
        contenido = f"Movimiento OK hacia {direccion}. Nueva posición: {nueva_pos}."
        posicion_final = nueva_pos
    else:
        mapa[clave] = "obstaculo"
        contenido = f"Obstáculo detectado en {nueva_pos} al ir hacia {direccion}. El robot no se movió."
        posicion_final = (x0, y0)

    print(f"[TOOL RESULT] mover_robot -> {contenido}")
    return Command(update={
        "posicion_actual": posicion_final,
        "mapa_conocido": mapa,
        "messages": [ToolMessage(contenido, tool_call_id=tool_call_id)],
    })


@dynamic_prompt
def prompt_con_modelo_interno(request: ModelRequest) -> str:
    """Inyecta el modelo interno del mundo en el prompt en cada paso, para
    que el agente 'recuerde' lo ya explorado antes de decidir."""
    mapa = request.state.get("mapa_conocido", {})
    pos = request.state.get("posicion_actual", (0, 0))
    resumen_mapa = ", ".join(f"{k}={v}" for k, v in mapa.items()) or "todavía nada explorado"
    return (
        "Eres un robot explorador de un almacén con memoria de lo ya recorrido. "
        f"Tu posición actual es {pos}. Tu modelo interno del mundo indica: {resumen_mapa}. "
        "Usa la tool `mover_robot` para explorar. NO intentes moverte hacia una celda que "
        "tu modelo interno ya marcó como 'obstaculo': elige otra dirección. "
        "IMPORTANTE: llama a `mover_robot` UNA sola vez por turno (un movimiento a la vez) "
        "y espera el resultado antes de decidir el siguiente movimiento; nunca pidas varios "
        "movimientos en paralelo en el mismo turno. "
        "Explora de forma eficiente y, cuando creas haber cubierto suficiente terreno "
        "(o tras varios intentos), resume qué encontraste."
    )


# --- Definición del agente ---------------------------------------------------

agent = create_agent(
    model=_resolver_modelo(AGENT_MODEL),
    tools=[mover_robot],
    middleware=[prompt_con_modelo_interno],
    state_schema=EstadoRobot,
)


def _imprimir_secuencia_mensajes(mensajes: list) -> None:
    """Imprime, paso a paso, qué hizo el agente: si llamó a una tool (y con
    qué argumentos) o si solo produjo texto. Sirve para verificar en la
    terminal -- sin depender de LangSmith -- qué tools se invocaron y en
    qué orden."""
    print("  --- secuencia de mensajes del agente ---")
    for i, msg in enumerate(mensajes):
        tipo = type(msg).__name__
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            for tc in tool_calls:
                print(f"    [{i}] {tipo} -> TOOL_CALL {tc['name']}(args={tc['args']})")
        elif tipo == "ToolMessage":
            print(f"    [{i}] {tipo} (resultado de {msg.name}): {msg.content!r}")
        else:
            contenido = getattr(msg, "content", "")
            print(f"    [{i}] {tipo}: {contenido!r}")
    print("  --- fin secuencia ---")


def explorar(pasos_sugeridos: int = 5) -> str:
    print(f"\n[AGENTE] Invocando exploración (hasta {pasos_sugeridos} movimientos)")
    resultado = agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"Explora el almacén dando hasta {pasos_sugeridos} movimientos "
                       "y evita repetir obstáculos ya conocidos.",
        }],
        "posicion_actual": (0, 0),
        "mapa_conocido": {},
    })
    _imprimir_secuencia_mensajes(resultado["messages"])
    print("Modelo interno final:", resultado.get("mapa_conocido"))
    return resultado["messages"][-1].content


if __name__ == "__main__":
    print(explorar())