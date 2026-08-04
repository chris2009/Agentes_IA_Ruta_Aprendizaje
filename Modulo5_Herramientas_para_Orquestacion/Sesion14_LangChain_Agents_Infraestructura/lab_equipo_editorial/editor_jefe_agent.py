import os
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv

from investigador_agent import investigador
from editor_estilo_agent import editor_estilo
from _utils import extraer_texto, resolver_modelo, AGENT_MODEL

load_dotenv()


@tool
def consultar_investigador(pregunta: str) -> str:
    """
    Delega una pregunta de investigacion al Agente Investigador del equipo editorial.

    Args:
        pregunta: la pregunta o tema puntual sobre el que se necesitan datos
            (por ejemplo: "que sectores estan mas expuestos a automatizacion?").

    Returns:
        El brief de investigacion elaborado por el Agente Investigador.
    """
    print(f"\n[TOOL CALL] consultar_investigador(pregunta={pregunta!r})")
    resultado = investigador.invoke({"messages": pregunta})
    respuesta = extraer_texto(resultado["messages"][-1])
    print(f"[TOOL RESULT] consultar_investigador -> {respuesta[:200]}...")
    return respuesta


@tool
def consultar_editor_estilo(borrador: str) -> str:
    """
    Envia un borrador de articulo al Agente Editor de Estilo para que lo revise y pula.

    Args:
        borrador: el texto completo del borrador del articulo (titular + parrafos).

    Returns:
        La version corregida y pulida del articulo, lista para publicar.
    """
    print(f"\n[TOOL CALL] consultar_editor_estilo(borrador={len(borrador)} caracteres)")
    resultado = editor_estilo.invoke({"messages": borrador})
    respuesta = extraer_texto(resultado["messages"][-1])
    print(f"[TOOL RESULT] consultar_editor_estilo -> {respuesta[:200]}...")
    return respuesta


print(f"[CONFIG] Usando modelo: {AGENT_MODEL}")
MODELO = resolver_modelo(temperature=0.4)

with open(os.path.join(os.path.dirname(__file__), "editor_jefe.prompt"), "r", encoding="utf-8") as file:
    editor_jefe_prompt = file.read()

editor_jefe = create_agent(
    model=MODELO,
    system_prompt=editor_jefe_prompt,
    tools=[consultar_investigador, consultar_editor_estilo],
)
