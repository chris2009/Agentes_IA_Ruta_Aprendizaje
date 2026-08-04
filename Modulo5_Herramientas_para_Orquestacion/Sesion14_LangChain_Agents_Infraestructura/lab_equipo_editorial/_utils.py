import os

# Comparar backends: descomenta uno u otro (o exporta AGENT_MODEL antes de
# correr). Ver TESTING_MODELOS_EQUIPO_EDITORIAL.md para los resultados de
# cada uno en esta arquitectura de agentes anidados.
# AGENT_MODEL = os.environ.get("AGENT_MODEL", "llama3.2")
# AGENT_MODEL = os.environ.get("AGENT_MODEL", "phi4-mini")
AGENT_MODEL = os.environ.get("AGENT_MODEL", "gemma-lmstudio")


def resolver_modelo(temperature: float = 0.3):
    """
    Resuelve el modelo compartido por los 3 agentes del equipo editorial
    segun AGENT_MODEL, sin tocar el resto del codigo -- mismo patron que
    01_simple_reflex_agent.py (Sesion 10).
    """
    if AGENT_MODEL == "gemma-lmstudio":
        # LM Studio expone un servidor local compatible con la API de OpenAI.
        from langchain_openai import ChatOpenAI

        base_url = os.environ.get("LMSTUDIO_BASE_URL", "http://172.30.32.1:8666/v1")
        return ChatOpenAI(
            model=os.environ.get("LMSTUDIO_MODEL", "google/gemma-4-e4b"),
            base_url=base_url,
            api_key="lm-studio",
            temperature=temperature,
        )
    if AGENT_MODEL in ("llama3.2", "phi4-mini"):
        return f"ollama:{AGENT_MODEL}"
    raise ValueError(
        f"AGENT_MODEL desconocido: {AGENT_MODEL!r}. "
        "Opciones: llama3.2, phi4-mini, gemma-lmstudio"
    )


def extraer_texto(mensaje) -> str:
    """
    Extrae solo el texto de respuesta de un AIMessage, ignorando bloques de
    'thinking' (razonamiento extendido) que Claude puede incluir en .content
    cuando .content es una lista de bloques en vez de un string plano.
    """
    contenido = mensaje.content
    if isinstance(contenido, str):
        return contenido
    partes = [bloque["text"] for bloque in contenido if isinstance(bloque, dict) and bloque.get("type") == "text"]
    return "\n".join(partes)
