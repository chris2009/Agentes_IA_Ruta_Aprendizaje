#!/usr/bin/env python3
"""
Agente simple con streaming usando LangChain (>=1.0) y OpenAI.

LangChain 1.x reemplazó `initialize_agent` (deprecado) por `create_agent`,
que construye el agente sobre LangGraph. El streaming token a token se
obtiene iterando `agent.stream(..., stream_mode="messages")`.

Requiere: langchain>=1.0, langchain-openai
"""

import os
from langchain.agents import create_agent
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()  # Cargar variables de entorno desde .env

# Configurar la API key de OpenAI
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("⚠️  Por favor configura tu OPENAI_API_KEY como variable de entorno")


# --- Definir herramientas personalizadas ---
@tool
def calcular_suma(a: float, b: float) -> float:
    """Suma dos números y devuelve el resultado."""
    return a + b


@tool
def calcular_multiplicacion(a: float, b: float) -> float:
    """Multiplica dos números y devuelve el resultado."""
    return a * b


@tool
def obtener_informacion(tema: str) -> str:
    """Obtiene información básica sobre un tema."""
    informacion = {
        "python": "Python es un lenguaje de programación interpretado, versátil y de alto nivel.",
        "ia": "La Inteligencia Artificial es la simulación de procesos de inteligencia humana por máquinas.",
        "langchain": "LangChain es un framework para desarrollar aplicaciones con modelos de lenguaje.",
    }
    return informacion.get(tema.lower(), f"No tengo información sobre '{tema}'")


def crear_agente():
    """
    Crea un agente con `create_agent`, la API recomendada en LangChain >= 1.0.
    Acepta directamente un string de modelo ("gpt-4o-mini") o una instancia
    de ChatModel.
    """
    herramientas = [calcular_suma, calcular_multiplicacion, obtener_informacion]

    agente = create_agent(
        model="gpt-4o-mini",  # también podrías pasar una instancia ChatOpenAI(...)
        tools=herramientas,
        system_prompt="Eres un asistente útil que usa herramientas cuando es necesario.",
    )
    return agente


def extraer_texto(content) -> str:
    """
    El contenido de un AIMessageChunk puede venir como:
    - un string plano: "Hola"
    - una lista de bloques: [{"type": "text", "text": "Hola"}]
    Esta función normaliza ambos casos a un string.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = []
        for bloque in content:
            if isinstance(bloque, dict):
                partes.append(bloque.get("text", ""))
            else:
                partes.append(str(bloque))
        return "".join(partes)
    return ""


def ejecutar_con_streaming(agente, pregunta: str):
    """
    Ejecuta el agente en modo streaming, imprimiendo:
    - tokens del modelo a medida que se generan
    - qué herramientas se están llamando
    """
    print(f"\n👤 Usuario: {pregunta}\n🤖 Agente: ", end="", flush=True)

    # stream_mode="messages" entrega tuplas (mensaje_parcial, metadata) token a token
    for chunk, metadata in agente.stream(
        {"messages": [{"role": "user", "content": pregunta}]},
        stream_mode="messages",
    ):
        texto = extraer_texto(chunk.content)
        if texto:
            print(texto, end="", flush=True)

        # Si el chunk trae llamadas a herramientas en curso, las mostramos
        tool_calls = getattr(chunk, "tool_call_chunks", None)
        if tool_calls:
            for tc in tool_calls:
                nombre = tc.get("name")
                if nombre:
                    print(f"\n🔧 [Llamando herramienta: {nombre}]", end="", flush=True)

    print()  # salto de línea final


def ejecutar_ejemplo():
    print("🤖 Inicializando agente con streaming...")
    agente = crear_agente()

    ejemplos = [
        "¿Cuánto es 15 + 27?",
        "Multiplica 8 por 6 y luego suma 10 al resultado",
        "¿Qué puedes decirme sobre Python?",
        "Necesito saber información sobre LangChain y luego sumar 100 + 50. ¿Puedes ayudarme?",
    ]

    for i, pregunta in enumerate(ejemplos, 1):
        print("\n" + "=" * 60)
        print(f"Ejemplo {i}")
        print("=" * 60)
        ejecutar_con_streaming(agente, pregunta)


if __name__ == "__main__":
    try:
        ejecutar_ejemplo()
        print("\n✅ Agente completado exitosamente")
    except KeyboardInterrupt:
        print("\n⚠️  Agente interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
