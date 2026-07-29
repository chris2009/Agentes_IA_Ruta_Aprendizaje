"""
05_learning_agent.py
-----------------------
LEARNING AGENT (IBM: https://www.ibm.com/think/topics/ai-agent-types)

"Mejora su desempeño con el tiempo adaptándose a nueva experiencia y
feedback, en vez de depender de reglas o modelos fijos." Se compone de:
  - elemento de desempeño (decide acciones con el conocimiento actual)
  - elemento de aprendizaje  (ajusta el conocimiento con feedback)
  - crítico                  (evalúa si la acción fue buena o mala)
  - generador de problemas   (sugiere probar cosas nuevas para explorar)

Ejemplo: un agente de reposición de inventario que, con el tiempo, va
aprendiendo (vía un archivo JSON local que persiste ENTRE ejecuciones)
qué estantes tienden a acertar o fallar sus recomendaciones, y ajusta su
confianza en consecuencia (refuerzo simple).

Este archivo es completamente autocontenido: no depende de ningún otro
archivo del repositorio (solo de librerías externas). Puedes ejecutarlo
de forma independiente.

Ejecutar:
    ollama pull llama3.2
    python 05_learning_agent.py

Comparar backends de modelo (sin tocar código):
    AGENT_MODEL=llama3.2        python 05_learning_agent.py   # default
    AGENT_MODEL=phi4-mini       python 05_learning_agent.py   # ollama, ya descargado
    AGENT_MODEL=gemma-lmstudio  python 05_learning_agent.py   # requiere LM Studio
                                                                # con el "Local Server"
                                                                # iniciado y
                                                                # pip install langchain-openai
"""

import json
import os
from pathlib import Path

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

# --- "Entorno" simulado + memoria de aprendizaje persistente --------------

SHELVES = {
    "E-12": {"producto": "auriculares bluetooth", "stock": 40},
    "E-27": {"producto": "cargador USB-C", "stock": 12},
    "E-33": {"producto": "mouse inalámbrico", "stock": 3},
    "E-41": {"producto": "teclado mecánico", "stock": 0},
}

LEARNING_STORE_PATH = Path(__file__).parent / "05_learning_store.json"


def _cargar_aprendizaje() -> dict:
    if LEARNING_STORE_PATH.exists():
        return json.loads(LEARNING_STORE_PATH.read_text())
    return {}


def _guardar_aprendizaje(data: dict) -> None:
    LEARNING_STORE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _consultar_confianza(estante: str) -> dict:
    data = _cargar_aprendizaje()
    return data.get(estante, {"aciertos": 0, "fallos": 0, "confianza": 0.5,
                               "nota": "sin historial previo, usando confianza neutra"})


def _registrar_resultado(estante: str, acierto: bool) -> dict:
    """El 'crítico' del agente: registra si una decisión fue correcta o no,
    y ajusta un score de confianza por estante (refuerzo simple)."""
    data = _cargar_aprendizaje()
    registro = data.setdefault(estante, {"aciertos": 0, "fallos": 0, "confianza": 0.5})
    if acierto:
        registro["aciertos"] += 1
    else:
        registro["fallos"] += 1
    total = registro["aciertos"] + registro["fallos"]
    registro["confianza"] = round(registro["aciertos"] / total, 2) if total else 0.5
    data[estante] = registro
    _guardar_aprendizaje(data)
    return registro


# --- Tools que percibe/acciona/aprende el agente ----------------------------

@tool
def consultar_estado_estante(codigo_estante: str) -> str:
    """Consulta stock actual y CONFIANZA APRENDIDA (histórico de aciertos/
    fallos) para las recomendaciones de reposición de un estante."""
    print(f"[TOOL CALL] consultar_estado_estante(codigo_estante={codigo_estante!r})")
    info = SHELVES.get(codigo_estante)
    if info is None:
        resultado = f"Estante {codigo_estante} no existe."
    else:
        conf = _consultar_confianza(codigo_estante)
        resultado = (
            f"{codigo_estante} ({info['producto']}): stock={info['stock']}. "
            f"Historial aprendido -> aciertos={conf.get('aciertos', 0)}, "
            f"fallos={conf.get('fallos', 0)}, confianza={conf.get('confianza', 0.5)}"
        )
    print(f"[TOOL RESULT] consultar_estado_estante -> {resultado!r}")
    return resultado


@tool
def recomendar_cantidad_reposicion(codigo_estante: str, cantidad_sugerida: int) -> str:
    """Elemento de desempeño: dada una cantidad sugerida, la ajusta según
    la confianza aprendida (si la confianza es baja, sugiere ser más
    conservador y probar una cantidad menor -- esto es el 'generador de
    problemas' explorando una alternativa)."""
    print(
        f"[TOOL CALL] recomendar_cantidad_reposicion(codigo_estante={codigo_estante!r}, "
        f"cantidad_sugerida={cantidad_sugerida!r})"
    )
    conf = _consultar_confianza(codigo_estante).get("confianza", 0.5)
    if conf < 0.4:
        ajustada = max(1, cantidad_sugerida // 2)
        resultado = (f"Confianza baja ({conf}) para {codigo_estante}: en vez de "
                     f"{cantidad_sugerida}, se recomienda EXPLORAR con {ajustada} "
                     "unidades para reducir riesgo de sobre-stock.")
    else:
        resultado = f"Confianza aceptable ({conf}) para {codigo_estante}: se mantiene la cantidad sugerida ({cantidad_sugerida})."
    print(f"[TOOL RESULT] recomendar_cantidad_reposicion -> {resultado!r}")
    return resultado


@tool
def registrar_feedback_reposicion(codigo_estante: str, fue_correcta: bool) -> str:
    """Crítico + elemento de aprendizaje: registra si una reposición pasada
    fue correcta o no, y actualiza la confianza aprendida para ese estante
    de forma PERSISTENTE (sobrevive a futuras ejecuciones del script)."""
    print(
        f"[TOOL CALL] registrar_feedback_reposicion(codigo_estante={codigo_estante!r}, "
        f"fue_correcta={fue_correcta!r})"
    )
    if codigo_estante not in SHELVES:
        resultado = f"Estante {codigo_estante} no existe."
    else:
        registro = _registrar_resultado(codigo_estante, fue_correcta)
        resultado = f"Feedback registrado para {codigo_estante}. Nueva confianza aprendida: {registro['confianza']}"
    print(f"[TOOL RESULT] registrar_feedback_reposicion -> {resultado!r}")
    return resultado


# --- Definición del agente ---------------------------------------------------

SYSTEM_PROMPT = """
Eres un agente de reposición de inventario que APRENDE con el tiempo.
Antes de recomendar, consulta siempre el historial aprendido con
`consultar_estado_estante`. Usa `recomendar_cantidad_reposicion` para
ajustar tu sugerencia según la confianza histórica (no según reglas
fijas). Si el usuario te da feedback sobre una reposición pasada (si fue
correcta o no), regístralo con `registrar_feedback_reposicion` para que
el agente sea mejor la próxima vez que se le consulte por ese estante.
"""

agent = create_agent(
    model=_resolver_modelo(AGENT_MODEL),
    tools=[consultar_estado_estante, recomendar_cantidad_reposicion, registrar_feedback_reposicion],
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


def consultar(instruccion: str) -> str:
    print(f"\n[AGENTE] Invocando episodio nuevo para: {instruccion!r}")
    resultado = agent.invoke({"messages": [{"role": "user", "content": instruccion}]})
    _imprimir_secuencia_mensajes(resultado["messages"])
    return resultado["messages"][-1].content


if __name__ == "__main__":
    # Primera consulta: sin historial, confianza neutra (0.5)
    print(consultar("¿Cuánto debería reponer del estante E-33? Sugiero 20 unidades."))

    # El usuario informa que una reposición anterior de E-33 fue un error
    # (se generó sobre-stock) -> el agente aprende de ese feedback.
    print("\n" + consultar(
        "La última reposición de 20 unidades en E-33 fue un ERROR, generó "
        "sobre-stock. Registra ese feedback."
    ))

    # Segunda consulta sobre el mismo estante: la recomendación ya debería
    # reflejar la confianza aprendida (más conservadora).
    print("\n" + consultar("¿Cuánto debería reponer ahora del estante E-33? Sugiero 20 unidades."))
