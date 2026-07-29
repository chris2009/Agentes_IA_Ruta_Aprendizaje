"""
03_goal_based_agent.py
------------------------
GOAL-BASED AGENT (IBM: https://www.ibm.com/think/topics/goal-based-agent)

"Considera objetivos futuros y usa razonamiento/planificación para elegir
acciones que lo acerquen a alcanzar esa meta, en lugar de solo reaccionar
al estímulo inmediato."

Ejemplo: un robot de picking que recibe una orden de compra y debe
planificar la ruta más corta (BFS sobre el mapa del almacén) hasta el
estante correcto, en vez de simplemente reaccionar celda a celda.

Este archivo es completamente autocontenido: no depende de ningún otro
archivo del repositorio (solo de librerías externas). Puedes ejecutarlo
de forma independiente.

Ejecutar:
    ollama pull llama3.2
    python 03_goal_based_agent.py

Comparar backends de modelo (sin tocar código):
    AGENT_MODEL=llama3.2        python 03_goal_based_agent.py   # default
    AGENT_MODEL=phi4-mini       python 03_goal_based_agent.py   # ollama, ya descargado
    AGENT_MODEL=gemma-lmstudio  python 03_goal_based_agent.py   # requiere LM Studio
                                                                  # con el "Local Server"
                                                                  # iniciado y
                                                                  # pip install langchain-openai
"""

import os
from collections import deque
from typing import Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

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

WAREHOUSE_GRID = [
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
]

SHELVES = {
    "E-12": {"pos": (1, 5), "producto": "auriculares bluetooth", "stock": 40},
    "E-27": {"pos": (5, 2), "producto": "cargador USB-C", "stock": 12},
    "E-33": {"pos": (7, 6), "producto": "mouse inalámbrico", "stock": 3},
    "E-41": {"pos": (3, 7), "producto": "teclado mecánico", "stock": 0},
}

POSICION_INICIAL = (0, 0)


def _celda_libre(pos: tuple[int, int]) -> bool:
    x, y = pos
    if not (0 <= y < len(WAREHOUSE_GRID) and 0 <= x < len(WAREHOUSE_GRID[0])):
        return False
    return WAREHOUSE_GRID[y][x] == 0


def _vecinos(pos: tuple[int, int]) -> list[tuple[int, int]]:
    x, y = pos
    candidatos = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [c for c in candidatos if _celda_libre(c)]


def _bfs_shortest_path(inicio: tuple[int, int], destino: tuple[int, int]) -> Optional[list]:
    """BFS clásico: la 'razón' interna de un agente basado en objetivos
    para planificar una ruta óptima hacia su meta."""
    if not _celda_libre(inicio) or not _celda_libre(destino):
        return None
    frontera = deque([[inicio]])
    visitados = {inicio}
    while frontera:
        camino = frontera.popleft()
        actual = camino[-1]
        if actual == destino:
            return camino
        for vecino in _vecinos(actual):
            if vecino not in visitados:
                visitados.add(vecino)
                frontera.append(camino + [vecino])
    return None


# --- Tools que percibe/acciona el agente -----------------------------------

@tool
def buscar_producto(nombre_producto: str) -> str:
    """Busca en qué estante está un producto por nombre (coincidencia parcial)."""
    print(f"[TOOL CALL] buscar_producto(nombre_producto={nombre_producto!r})")
    coincidencias = [
        (codigo, info) for codigo, info in SHELVES.items()
        if nombre_producto.lower() in info["producto"].lower()
    ]
    if not coincidencias:
        resultado = f"No se encontró ningún producto que coincida con '{nombre_producto}'."
    else:
        resultado = "\n".join(
            f"{codigo}: {info['producto']} (stock={info['stock']}, posición={info['pos']})"
            for codigo, info in coincidencias
        )
    print(f"[TOOL RESULT] buscar_producto -> {resultado!r}")
    return resultado


@tool
def planificar_ruta_a_estante(codigo_estante: str) -> str:
    """Planifica la ruta más corta desde la posición inicial (0,0) del robot
    hasta el estante indicado, evitando obstáculos del almacén."""
    print(f"[TOOL CALL] planificar_ruta_a_estante(codigo_estante={codigo_estante!r})")
    info = SHELVES.get(codigo_estante)
    if info is None:
        resultado = f"Estante desconocido: {codigo_estante}. Opciones: {list(SHELVES)}"
    else:
        camino = _bfs_shortest_path(POSICION_INICIAL, info["pos"])
        if camino is None:
            resultado = f"No existe una ruta libre de obstáculos hasta {codigo_estante}."
        else:
            resultado = f"Ruta hacia {codigo_estante} ({len(camino) - 1} pasos): {camino}"
    print(f"[TOOL RESULT] planificar_ruta_a_estante -> {resultado!r}")
    return resultado


@tool
def confirmar_recogida(codigo_estante: str, cantidad: int) -> str:
    """Confirma que se recogió una cantidad de producto del estante indicado."""
    print(f"[TOOL CALL] confirmar_recogida(codigo_estante={codigo_estante!r}, cantidad={cantidad!r})")
    info = SHELVES.get(codigo_estante)
    if info is None:
        resultado = f"Estante {codigo_estante} no existe."
    elif info["stock"] < cantidad:
        resultado = f"Stock insuficiente en {codigo_estante}: hay {info['stock']}, se pidieron {cantidad}."
    else:
        info["stock"] -= cantidad
        resultado = f"Recogidas {cantidad} unidades de {info['producto']} en {codigo_estante}. Stock restante: {info['stock']}."
    print(f"[TOOL RESULT] confirmar_recogida -> {resultado!r}")
    return resultado


# --- Definición del agente ---------------------------------------------------

SYSTEM_PROMPT = """
Eres un robot de picking en un almacén. Tu OBJETIVO explícito es cumplir
la orden de compra que te da el usuario:
1. Localiza el producto pedido con `buscar_producto`.
2. Planifica el camino más corto con `planificar_ruta_a_estante`.
3. Ejecuta la recogida con `confirmar_recogida`.
4. Si el estante no tiene stock suficiente, informa claramente que la
   meta no se pudo cumplir del todo y sugiere una alternativa si existe.
Razona paso a paso persiguiendo la meta, no solo reacciones al último dato.
"""

agent = create_agent(
    model=_resolver_modelo(AGENT_MODEL),
    tools=[buscar_producto, planificar_ruta_a_estante, confirmar_recogida],
    system_prompt=SYSTEM_PROMPT,
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


def cumplir_orden(pedido: str) -> str:
    print(f"\n[AGENTE] Invocando episodio nuevo para el pedido: {pedido!r}")
    resultado = agent.invoke({"messages": [{"role": "user", "content": pedido}]})
    _imprimir_secuencia_mensajes(resultado["messages"])
    return resultado["messages"][-1].content


if __name__ == "__main__":
    while True:
        # print(cumplir_orden("Necesito 2 unidades de 'mouse inalámbrico'. Consíguelas."))
        pedido = input("\nIngrese la orden de compra (o 'salir' para terminar): ")
        if pedido.lower() == "salir":
            break
        print(cumplir_orden(pedido))
    
