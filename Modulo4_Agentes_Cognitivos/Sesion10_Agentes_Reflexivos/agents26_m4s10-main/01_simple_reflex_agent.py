"""
01_simple_reflex_agent.py
--------------------------
SIMPLE REFLEX AGENT (IBM: https://www.ibm.com/think/topics/simple-reflex-agent)

"Sigue reglas condición-acción fijas, actuando solo sobre la percepción
ACTUAL, sin memoria de estados pasados ni planificación futura."

Ejemplo: un termostato de almacén. El agente lee la temperatura de una
zona y decide, con una regla simple, si debe encender o apagar la
climatización. Cada llamada es un evento aislado: el agente no recuerda
lo que decidió antes.

Este archivo es completamente autocontenido: no depende de ningún otro
archivo del repositorio (solo de librerías externas). Puedes ejecutarlo
de forma independiente.

Ejecutar:
    ollama pull llama3.2
    python 01_simple_reflex_agent.py

Comparar backends de modelo (sin tocar código):
    AGENT_MODEL=llama3.2        python 01_simple_reflex_agent.py   # default
    AGENT_MODEL=phi4-mini       python 01_simple_reflex_agent.py   # ollama, ya descargado
    AGENT_MODEL=gemma-lmstudio  python 01_simple_reflex_agent.py   # requiere LM Studio
                                                                    # con el "Local Server"
                                                                    # iniciado y
                                                                    # pip install langchain-openai
"""

import os
import random

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()
random.seed(42)

#AGENT_MODEL = os.environ.get("AGENT_MODEL", "llama3.2")
#AGENT_MODEL = os.environ.get("AGENT_MODEL", "phi4-mini")
AGENT_MODEL = os.environ.get("AGENT_MODEL", "gemma-lmstudio")


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

ZONAS = {
    "zona_A_congelados": {"temp_objetivo": -18.0},
    "zona_B_refrigerados": {"temp_objetivo": 4.0},
    "zona_C_ambiente": {"temp_objetivo": 21.0},
}

print(ZONAS)
for zona in ZONAS:
    print(f"{zona}: objetivo {ZONAS[zona]['temp_objetivo']}°C")


def _leer_sensor(zona: str) -> float:
    """Simula la lectura instantánea y ruidosa de un sensor de temperatura."""
    objetivo = ZONAS[zona]["temp_objetivo"]
    deriva = random.uniform(-3.5, 3.5)  # el clima real se desvía del objetivo
    return round(objetivo + deriva, 1)


# --- Tools que percibe/acciona el agente -----------------------------------

@tool
def sensor_temperatura(zona: str) -> str:
    """Lee la temperatura ACTUAL de una zona del almacén.
    Zonas válidas: zona_A_congelados, zona_B_refrigerados, zona_C_ambiente."""
    print(f"[TOOL CALL] sensor_temperatura(zona={zona!r})")
    if zona not in ZONAS:
        resultado = f"Zona desconocida: {zona}. Opciones: {list(ZONAS)}"
    else:
        temp = _leer_sensor(zona)
        resultado = f"Temperatura actual en {zona}: {temp}°C (objetivo: {ZONAS[zona]['temp_objetivo']}°C)"
    print(f"[TOOL RESULT] sensor_temperatura -> {resultado}")
    return resultado


@tool
def actuador_climatizacion(zona: str, accion: str) -> str:
    """Ejecuta una acción sobre el sistema de climatización de una zona.
    accion debe ser 'encender_frio', 'encender_calor' o 'apagar'."""
    print(f"[TOOL CALL] actuador_climatizacion(zona={zona!r}, accion={accion!r})")
    resultado = f"[ACTUADOR] Zona {zona}: se ejecutó '{accion}'."
    print(f"[TOOL RESULT] actuador_climatizacion -> {resultado}")
    return resultado


# --- Definición del agente ---------------------------------------------------

REGLAS = """
Eres el controlador reflejo del sistema de climatización de un almacén.
No tienes memoria de decisiones anteriores: cada mensaje es un evento
aislado. Aplica EXACTAMENTE estas reglas condición-acción sobre la
percepción actual (no planifiques, no razones sobre el futuro):

1. Lee la temperatura de la zona con la tool `sensor_temperatura`.
2. Si temperatura > objetivo + 2°C  -> actuador_climatizacion(zona, "encender_frio")
3. Si temperatura < objetivo - 2°C  -> actuador_climatizacion(zona, "encender_calor")
4. En cualquier otro caso          -> actuador_climatizacion(zona, "apagar")
5. Responde en una sola línea confirmando la acción tomada.
"""

# Sin checkpointer, sin estado persistido entre invocaciones: cada
# .invoke() es un episodio 100% independiente, tal como exige la
# definición de IBM ("sin memoria de estados pasados").
agent = create_agent(
    model=_resolver_modelo(AGENT_MODEL),
    tools=[sensor_temperatura, actuador_climatizacion],
    system_prompt=REGLAS,
)


def _imprimir_secuencia_mensajes(mensajes: list) -> None:
    """Imprime, paso a paso, qué hizo el agente: si llamó a una tool (y con
    qué argumentos) o si solo produjo texto. Sirve para verificar en la
    terminal -- sin depender de LangSmith -- si actuador_climatizacion
    realmente se invocó."""
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


def revisar_zona(zona: str) -> str:
    """Cada llamada es un episodio nuevo: no se reutiliza historial previo."""
    print(f"\n[AGENTE] Invocando episodio nuevo para {zona!r}")
    resultado = agent.invoke(
        {"messages": [{"role": "user", "content": f"Revisa la zona {zona}."}]}
    )
    _imprimir_secuencia_mensajes(resultado["messages"])
    return resultado["messages"][-1].content


if __name__ == "__main__":
    for zona in ZONAS:
        print(f"\n=== {zona} ===")
        print(revisar_zona(zona))
