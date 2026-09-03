"""
Utilidades compartidas del equipo publicitario de Cafe.AI.

Mismo patron que `_utils.py` del `lab_equipo_editorial` (Sesion 14): un unico
punto donde se resuelve el backend de LLM (Large Language Model, modelo de
lenguaje de gran escala), para poder comparar modelos sin tocar el codigo de
los agentes ni del grafo.

Backend por defecto: `llama3.2` en Ollama, que es el modelo que trae el lab
`campanapub.ipynb` de la Sesion 15.
"""

import os

from dotenv import load_dotenv

# Carga el .env de esta carpeta si existe (API keys de Anthropic / LangSmith),
# igual que los notebooks de clase.
load_dotenv()

# Conmutar backend sin tocar el resto del codigo: exportar AGENT_MODEL antes
# de correr, o cambiar este valor por defecto.
#   llama3.2       -> Ollama local (default del lab de clase)
#   phi4-mini      -> Ollama local
#   gemma-lmstudio -> LM Studio (servidor local con API compatible con OpenAI)
#   claude         -> API de Anthropic (de pago, mejor calidad de copy)
AGENT_MODEL = os.environ.get("AGENT_MODEL", "llama3.2")

# Nombre real de cada modelo dentro de Ollama.
MODELOS_OLLAMA = {
    "llama3.2": "llama3.2:latest",
    "llama3.2:1b": "llama3.2:1b",
    "phi4-mini": "phi4-mini:latest",
    "qwen3": "qwen3:0.6b",
}


def resolver_modelo(temperature: float = 0.7):
    """
    Devuelve el chat model ya instanciado segun AGENT_MODEL.

    `temperature` se recibe por parametro porque en este grafo no todos los
    nodos quieren la misma: el enrutador clasifica y necesita temperatura baja
    (decision estable), mientras que los roles creativos necesitan temperatura
    alta (variedad de ideas).
    """
    if AGENT_MODEL in MODELOS_OLLAMA:
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=MODELOS_OLLAMA[AGENT_MODEL],
            temperature=temperature,
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    if AGENT_MODEL == "gemma-lmstudio":
        # LM Studio expone un servidor local compatible con la API
        # (Application Programming Interface) de OpenAI.
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.environ.get("LMSTUDIO_MODEL", "google/gemma-4-e4b"),
            base_url=os.environ.get("LMSTUDIO_BASE_URL", "http://172.30.32.1:8666/v1"),
            api_key="lm-studio",
            temperature=temperature,
        )

    if AGENT_MODEL == "claude":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"),
            temperature=temperature,
        )

    raise ValueError(
        f"AGENT_MODEL desconocido: {AGENT_MODEL!r}. "
        f"Opciones: {', '.join(list(MODELOS_OLLAMA) + ['gemma-lmstudio', 'claude'])}"
    )


def extraer_texto(mensaje) -> str:
    """
    Extrae solo el texto de un AIMessage, ignorando bloques de 'thinking'
    (razonamiento extendido) que algunos modelos incluyen cuando `.content`
    es una lista de bloques en vez de un string plano.
    """
    contenido = mensaje.content
    if isinstance(contenido, str):
        return contenido.strip()
    partes = [
        bloque["text"]
        for bloque in contenido
        if isinstance(bloque, dict) and bloque.get("type") == "text"
    ]
    return "\n".join(partes).strip()
