"""
04_utility_based_agent.py
----------------------------
UTILITY-BASED AGENT (IBM: https://www.ibm.com/think/topics/utility-based-agent)

"Va más allá de simplemente cumplir un objetivo: usa una función de
utilidad para evaluar y comparar MÚLTIPLES opciones, sopesando trade-offs
(tiempo, costo, seguridad) y elige la de mayor beneficio esperado."

Ejemplo: elegir el vehículo y la ruta de despacho que maximizan una
utilidad combinada de tiempo + costo + seguridad, en vez de solo llegar
al destino (eso sería un agente basado en objetivos).

Este archivo es completamente autocontenido: no depende de ningún otro
archivo del repositorio (solo de librerías externas). Puedes ejecutarlo
de forma independiente.

Ejecutar:
    ollama pull llama3.2
    python 04_utility_based_agent.py

Comparar backends de modelo (sin tocar código):
    AGENT_MODEL=llama3.2        python 04_utility_based_agent.py   # default
    AGENT_MODEL=phi4-mini       python 04_utility_based_agent.py   # ollama, ya descargado
    AGENT_MODEL=gemma-lmstudio  python 04_utility_based_agent.py   # requiere LM Studio
                                                                     # con el "Local Server"
                                                                     # iniciado y
                                                                     # pip install langchain-openai
"""

import os

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

VEHICLES = {
    "furgon_1": {"costo_km": 0.9, "vel_kmh": 60, "seguridad": 0.95},
    "moto_1": {"costo_km": 0.4, "vel_kmh": 45, "seguridad": 0.80},
    "van_electrica_1": {"costo_km": 0.6, "vel_kmh": 50, "seguridad": 0.97},
}

ROUTES = {
    "ruta_norte": {"km": 18, "trafico": 0.7},
    "ruta_centro": {"km": 9, "trafico": 0.9},
    "ruta_perimetral": {"km": 26, "trafico": 0.2},
}


def _calcular_utilidad(vehiculo: str, ruta: str,
                        peso_tiempo: float, peso_costo: float, peso_seguridad: float) -> dict:
    """Combina tiempo, costo y seguridad en un único score de utilidad
    (0 a 1, mayor es mejor). Los pesos son configurables, lo que ilustra
    el trade-off explícito de un agente basado en utilidad."""
    v, r = VEHICLES[vehiculo], ROUTES[ruta]
    tiempo_h = r["km"] / v["vel_kmh"] * (1 + r["trafico"])
    costo = r["km"] * v["costo_km"]

    score_tiempo = max(0.0, 1 - tiempo_h / 2.0)
    score_costo = max(0.0, 1 - costo / 30.0)
    score_seguridad = v["seguridad"]

    utilidad = (peso_tiempo * score_tiempo
                + peso_costo * score_costo
                + peso_seguridad * score_seguridad)

    return {
        "tiempo_horas": round(tiempo_h, 2),
        "costo_estimado": round(costo, 2),
        "seguridad": v["seguridad"],
        "utilidad": round(utilidad, 3),
    }


# --- Tools que percibe/acciona el agente -----------------------------------

@tool
def listar_opciones_envio() -> str:
    """Lista los vehículos y rutas disponibles para un despacho."""
    print("[TOOL CALL] listar_opciones_envio()")
    vehiculos = ", ".join(VEHICLES.keys())
    rutas = ", ".join(ROUTES.keys())
    resultado = f"Vehículos disponibles: {vehiculos}\nRutas disponibles: {rutas}"
    print(f"[TOOL RESULT] listar_opciones_envio -> {resultado!r}")
    return resultado


@tool
def evaluar_opcion_envio(vehiculo: str, ruta: str,
                          peso_tiempo: float = 0.4,
                          peso_costo: float = 0.35,
                          peso_seguridad: float = 0.25) -> str:
    """Calcula la utilidad (0-1, mayor es mejor) de una combinación
    vehículo+ruta, combinando tiempo, costo y seguridad según los pesos
    dados (deben sumar aprox. 1.0)."""
    print(
        f"[TOOL CALL] evaluar_opcion_envio(vehiculo={vehiculo!r}, ruta={ruta!r}, "
        f"peso_tiempo={peso_tiempo!r}, peso_costo={peso_costo!r}, peso_seguridad={peso_seguridad!r})"
    )
    if vehiculo not in VEHICLES:
        resultado = f"Vehículo desconocido: {vehiculo}. Opciones: {list(VEHICLES)}"
    elif ruta not in ROUTES:
        resultado = f"Ruta desconocida: {ruta}. Opciones: {list(ROUTES)}"
    else:
        r = _calcular_utilidad(vehiculo, ruta, peso_tiempo, peso_costo, peso_seguridad)
        resultado = (
            f"{vehiculo} + {ruta} -> tiempo={r['tiempo_horas']}h, "
            f"costo=${r['costo_estimado']}, seguridad={r['seguridad']}, "
            f"UTILIDAD={r['utilidad']}"
        )
    print(f"[TOOL RESULT] evaluar_opcion_envio -> {resultado!r}")
    return resultado


# --- Definición del agente ---------------------------------------------------

SYSTEM_PROMPT = """
Eres el planificador de despachos de un almacén. NO te conformas con
encontrar "una" forma de llegar al destino: debes EVALUAR varias
combinaciones de vehículo+ruta usando `evaluar_opcion_envio` y elegir la
de mayor utilidad. Sigue estos pasos:
1. Llama a `listar_opciones_envio` para ver las opciones disponibles.
2. Evalúa AL MENOS 3 combinaciones distintas de vehículo+ruta.
3. Compara las utilidades obtenidas.
4. Recomienda la combinación con mayor utilidad, explicando el trade-off
   (por qué no elegiste la más barata o la más rápida si no maximizaba
   la utilidad total).
Si el usuario da preferencias (por ejemplo "prioriza seguridad"), ajusta
los pesos peso_tiempo/peso_costo/peso_seguridad en consecuencia antes de
evaluar.
"""

agent = create_agent(
    model=_resolver_modelo(AGENT_MODEL),
    tools=[listar_opciones_envio, evaluar_opcion_envio],
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


def elegir_mejor_despacho(instruccion: str) -> str:
    print(f"\n[AGENTE] Invocando episodio nuevo para: {instruccion!r}")
    resultado = agent.invoke({"messages": [{"role": "user", "content": instruccion}]})
    _imprimir_secuencia_mensajes(resultado["messages"])
    return resultado["messages"][-1].content


if __name__ == "__main__":
    while True:
        # "Necesito despachar un pedido urgente pero sin descuidar la seguridad. "
        # "¿Qué vehículo y ruta me recomiendas?"
        instruccion = input("\nIngrese la instrucción de despacho (o 'salir' para terminar): ")
        if instruccion.lower() == "salir":
            break
        print(elegir_mejor_despacho(instruccion))
    
