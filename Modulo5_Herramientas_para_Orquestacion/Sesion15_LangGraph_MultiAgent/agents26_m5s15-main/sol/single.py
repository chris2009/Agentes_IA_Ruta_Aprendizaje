
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

class State(TypedDict):
    messages: Annotated[list, add_messages] # Nos permite almacenar los mensajes de conversacion en esta lista

graph_builder = StateGraph(State)

def chatbot(state: State):
    # Retorna la respuesta de la invocacion al llm como append a la lista de mensajes, considerando como entrada la misma lista de mensajes
    return {"messages":[llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

user_input = input("Enter a message> ")
state = graph.invoke({"messages": [{"role": "user", "content": user_input}]})

print(state["messages"])
print(state["messages"][-1].content)