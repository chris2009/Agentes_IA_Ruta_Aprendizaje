#!/usr/bin/env python3
"""
Agente avanzado con streaming detallado usando LangChain (>=1.0) y OpenAI.

En vez de callbacks tipo `BaseCallbackHandler` (útiles pero más verbosos),
este ejemplo usa `astream_events`, la forma recomendada en LangChain >= 1.0
para observar eventos granulares: inicio/fin del modelo, tokens, inicio/fin
de herramientas, etc.

Requiere: langchain>=1.0, langchain-openai
"""

import asyncio
import os
from langchain.agents import create_agent
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()  # Cargar variables de entorno desde .env

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("⚠️  Por favor configura tu OPENAI_API_KEY")


# --- Herramientas personalizadas ---
@tool
def calcular_area_rectangulo(largo: float, ancho: float) -> float:
    """Calcula el área de un rectángulo dado largo y ancho."""
    return largo * ancho


@tool
def calcular_perimetro_rectangulo(largo: float, ancho: float) -> float:
    """Calcula el perímetro de un rectángulo dado largo y ancho."""
    return 2 * (largo + ancho)


@tool
def obtener_formula(forma: str) -> str:
    """Obtiene la fórmula para calcular el área de una forma geométrica."""
    formulas = {
        "cuadrado": "Área = lado²",
        "rectángulo": "Área = largo × ancho",
        "círculo": "Área = π × radio²",
        "triángulo": "Área = (base × altura) / 2",
    }
    return formulas.get(forma.lower(), f"No conozco la fórmula para '{forma}'")


def crear_agente():
    herramientas = [
        calcular_area_rectangulo,
        calcular_perimetro_rectangulo,
        obtener_formula,
    ]
    return create_agent(
        model="gpt-4o-mini",
        tools=herramientas,
        system_prompt="Eres un asistente de matemáticas. Usa las herramientas cuando sea necesario.",
    )


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


async def ejecutar_con_eventos(agente, pregunta: str):
    """
    Recorre `astream_events`, mostrando cada tipo de evento relevante:
    - on_chat_model_stream: tokens del LLM
    - on_tool_start / on_tool_end: ejecución de herramientas
    """
    print(f"\n👤 Usuario: {pregunta}")
    print("🤖 Agente: ", end="", flush=True)

    async for event in agente.astream_events(
        {"messages": [{"role": "user", "content": pregunta}]},
        version="v2",
    ):
        tipo = event["event"]

        if tipo == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            texto = extraer_texto(chunk.content)
            if texto:
                print(texto, end="", flush=True)

        elif tipo == "on_tool_start":
            nombre = event["name"]
            entrada = event["data"].get("input")
            print(f"\n🔧 [HERRAMIENTA] Ejecutando: {nombre}")
            print(f"   Entrada: {entrada}")

        elif tipo == "on_tool_end":
            salida = event["data"].get("output")
            print(f"   Resultado: {salida}")
            print("🤖 Agente: ", end="", flush=True)

    print()


async def ejecutar_ejemplos():
    print("🤖 Inicializando agente avanzado con streaming de eventos...")
    agente = crear_agente()

    ejemplos = [
        "¿Cuál es el área y perímetro de un rectángulo de 5m x 3m?",
        "Necesito las fórmulas de área para cuadrado, círculo y triángulo",
        "Tengo un rectángulo de 10m de largo y 6m de ancho. "
        "¿Cuál es su área, perímetro y la fórmula general que usaste?",
    ]

    for i, pregunta in enumerate(ejemplos, 1):
        print("\n" + "=" * 70)
        print(f"EJEMPLO {i}")
        print("=" * 70)
        await ejecutar_con_eventos(agente, pregunta)


if __name__ == "__main__":
    try:
        asyncio.run(ejecutar_ejemplos())
        print("\n✅ Todos los ejemplos completados")
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
