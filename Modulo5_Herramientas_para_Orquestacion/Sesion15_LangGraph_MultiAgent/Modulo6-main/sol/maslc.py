
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
import os

from dotenv import load_dotenv
load_dotenv()
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.2)
llm = ChatOllama(model="llama3.2:latest", temperature=0.2)

########################################## AGENT DECLARATION PART #####################################################
from langchain_core.tools import tool
from datetime import datetime

@tool
def get_current_datetime() -> str:
    """OBTIENE FECHA Y HORA ACTUALES"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

########################################## LANGGRAPH PART #####################################################

class MessageClassifier(BaseModel):
    message_type: Literal["emocional", "racional"] = Field(
            ...,
        description="Clasifica si el mensaje debe ser de tono emocional(terapeuta) o logico (racional)"
    )

class State(TypedDict):
    messages: Annotated[list, add_messages] # Nos permite almacenar los mensajes de conversacion en esta lista
    message_type: str | None

graph_builder = StateGraph(State)

def classify_message(state:State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Clasifica el mensaje del usuario en:
            - 'emocional': si el usuario solicita soporte emocional, terapia, problemas con sus sentimientos o problemas personales
            - 'racional': si el usuario solicita hechos concretos, informacion verificable, analisis logico, o soluciones practicas
            """
        },
        {"role": "user", "content": last_message.content}
    ])
    print("[CLASSIFIER]:"+str(result.message_type))
    return {"message_type": result.message_type}

def router(state:State):
    
    message_type = state.get("message_type", "racional") # si es que no se logra la clasificacion correctamente, por defecto tomar opcion racional
    print("[ROUTER] > "+str(message_type))
    if message_type == "emocional":
        return {"next": "emocional"}

    return {"next": "racional"}

def therapist_agent(state:State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """Eres un terapeuta compasivo. Céntrate en los aspectos emocionales del mensaje del usuario.
            Muestra empatía, valida sus sentimientos y ayúdalo a procesarlos.
            Haz preguntas reflexivas para ayudarlo a explorar sus sentimientos con mayor profundidad.
            Evita dar soluciones lógicas a menos que se te pida explícitamente."""
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    print("[EMOCIONAL]")
    return {"messages": [{"role": "assistant", "content": reply.content}]}


def logical_agent(state:State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """Eres un asistente puramente lógico. Céntrate únicamente en los hechos y la información.
            Ofrece respuestas claras y concisas basadas en la lógica y la evidencia.
            Usas tus herramientas para obtener el punto en el tiempo actual y en base a ello soportar tus respuestas
            No abordes las emociones ni ofrezcas apoyo emocional.
            Sé directo y directo en tus respuestas.."""
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    llm_tools = llm.bind_tools(tools=[get_current_datetime])
    reply = llm_tools.invoke(messages)
    print("[RACIONAL]...")
    return {"messages": [{"role": "assistant", "content": reply.content}]}



graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("emocional", therapist_agent)
graph_builder.add_node("racional", logical_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"emocional": "emocional", "racional": "racional"}
)

graph_builder.add_edge("emocional", END)
graph_builder.add_edge("racional", END)

graph = graph_builder.compile()


def run_mas():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Bye")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")


if __name__ == "__main__":
    run_mas()