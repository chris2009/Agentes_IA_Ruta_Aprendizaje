"""
# Agente de recepción de reclamos bancarios (LangGraph, memoria persistida a archivo)
######################################################################################

Este script parte del agente de la Sesion9 (`agente_landgraph_memoria_corto_largo_plazo.py`)
y lo adapta a un caso de uso concreto: un chatbot que atiende a clientes de un banco
ficticio ("Banco Andino", nombre inventado solo para esta demo educativa) y registra
sus reclamos sobre un catálogo fijo de productos bancarios.

La diferencia clave frente a la Sesion9 es que ahí la memoria (tanto la de corto
plazo -el checkpointer- como la de largo plazo -el store-) vivía en RAM
(`InMemorySaver` / `InMemoryStore`): al cerrar el proceso, todo se perdía. Un banco
real necesita que el historial de la conversación y el libro de reclamos sobrevivan
a un reinicio del programa, así que aquí ambas piezas quedan respaldadas en disco:

MEMORIA A CORTO PLAZO (el hilo de conversación de un cliente)
    Sigue viviendo en un checkpointer de LangGraph, pero en vez de `InMemorySaver`
    usamos `SqliteSaver`, que guarda cada checkpoint en un archivo `.sqlite`
    (`data/historial_chat.sqlite`). Las 4 estrategias de gestión de mensajes de la
    Sesion9 (full / trim_count / trim_tokens / summary) se mantienen intactas: son
    ortogonales a "dónde" se guarda el checkpoint, solo cambian "qué" se le manda
    al LLM en cada turno.

MEMORIA A LARGO PLAZO (el libro de reclamos, entre distintas conversaciones)
    En la Sesion9 el `store.put(...)` guardaba texto libre en un `InMemoryStore`.
    Aquí lo reemplazamos por `FileStore`, una subclase de `InMemoryStore` que
    reutiliza toda su lógica de namespaces/búsqueda y solo añade una carga inicial
    y un volcado a disco en JSON (`data/reclamos_registrados.json`) cada vez que se
    escribe algo. Así, si el cliente vuelve otro día (nuevo proceso, mismo DNI),
    el agente ya conoce sus reclamos anteriores.

TRASPASO CORTO -> LARGO PLAZO
    En la Sesion9 el disparador era la frase literal "recuerda que" en el mensaje
    del usuario: frágil, pero suficiente para esa demo. Para un caso real (y
    probado aquí en la práctica) esa técnica no es confiable: se probó primero
    pedirle al LLM que agregara un bloque `<RECLAMO_JSON>{...}</RECLAMO_JSON>` al
    terminar de recolectar los datos, y con un modelo local pequeño (llama3.2:3b)
    el modelo simplemente no lo hacía, aunque ya tuviera los 4 datos.
    En su lugar, cada turno se hace una segunda llamada al LLM, independiente de
    la respuesta conversacional, usando salida estructurada
    (`model.with_structured_output(DatosReclamo)`) para extraer del historial los
    4 campos del reclamo. Esta extracción no depende de que el modelo "recuerde"
    seguir una instrucción de formato en su prosa: usa el modo de salida
    estructurada del propio proveedor (function calling / JSON schema), que en
    la práctica es mucho más confiable. El nodo fusiona lo extraído con lo que ya
    se sabía (`state["datos_reclamo"]`) y, en cuanto los 4 campos están completos,
    el propio código Python -no el LLM- decide registrar el ticket en `FileStore`.

Requisitos (ya instalados en el venv compartido del módulo, ver requirements.txt):
    pip install -U langgraph langchain langchain-ollama langgraph-checkpoint-sqlite
    pip install -U langchain-openai python-dotenv   # opcional, solo si usas OpenAI

    # Backend por defecto: Ollama corriendo localmente.
    #   ollama pull llama3.2
    #   ollama serve   (si no se inicia solo)
    #
    # Backend alternativo: OpenAI. Para activarlo, crear un archivo `.env` en esta
    # misma carpeta (Sesion11/.env) con:
    #   LLM_PROVIDER=openai
    #   OPENAI_API_KEY=sk-...
    #   OPENAI_MODEL=gpt-4o-mini      (opcional, este es el valor por defecto)
    # Si `LLM_PROVIDER` no está definido, o vale "ollama", se usa Ollama.

Ejecutar el chat interactivo:
    python main.py
"""

import json
import os
import re
import unicodedata
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.messages import RemoveMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.runtime import Runtime
from langgraph.store.base import Item
from langgraph.store.memory import InMemoryStore

load_dotenv()  # lee Sesion11/.env si existe (LLM_PROVIDER, OPENAI_API_KEY, etc.)


@dataclass
class Context:
    """Configuración de un run: no forma parte del estado del grafo,
    se pasa vía `context=` en invoke() y se lee con `runtime.context`."""
    user_id: str  # aquí usamos el DNI del cliente como identificador
    memory_strategy: str = "full"  # "full" | "trim_count" | "trim_tokens" | "summary"


# ---------------------------------------------------------------------------
# 1. Dominio: catálogo de productos sobre los que se puede reclamar
# ---------------------------------------------------------------------------
NOMBRE_BANCO = "Banco Andino"  # nombre ficticio, solo para esta demo educativa

PRODUCTOS_BANCARIOS = [
    "Tarjeta de crédito",
    "Tarjeta de débito",
    "Cuenta de ahorros",
    "Préstamo personal",
    "Banca por internet / app móvil",
]

CAMPOS_OBLIGATORIOS = ["nombre_completo", "documento_identidad", "producto", "descripcion"]


class DatosReclamo(BaseModel):
    """Esquema de extracción estructurada: los 4 datos que debe reunir el
    agente antes de poder registrar el reclamo. Cada campo es opcional
    porque, a mitad de la conversación, lo normal es que varios sigan
    en `None`."""

    nombre_completo: Optional[str] = None
    documento_identidad: Optional[str] = None
    producto: Optional[str] = None
    descripcion: Optional[str] = None


# ---------------------------------------------------------------------------
# 2. Modelo (Ollama por defecto, OpenAI opcional vía LLM_PROVIDER)
# ---------------------------------------------------------------------------
def construir_modelo(temperature: float = 0.3):
    """Crea el chat model a usar, según la variable de entorno LLM_PROVIDER.

    Mantener la construcción del modelo detrás de una función (en vez de una
    única instancia global, como en la Sesion9) permite elegir el backend en
    tiempo de ejecución sin tocar el resto del código.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "LLM_PROVIDER=openai pero no se encontró OPENAI_API_KEY. "
                "Define ambas en Sesion11/.env, o usa LLM_PROVIDER=ollama."
            )
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
        )

    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        temperature=temperature,
    )


model = construir_modelo(0.3)
summarizer_model = construir_modelo(0.0)  # usado solo por la estrategia "summary"

# Segundo "rol" del mismo tipo de modelo: no conversa, solo extrae datos
# estructurados del historial en cada turno (ver call_model más abajo).
extractor_model = construir_modelo(0.0).with_structured_output(DatosReclamo)


class State(MessagesState):
    summary: str  # solo se usa con la estrategia "summary"
    datos_reclamo: dict  # campos de DatosReclamo ya confirmados, acumulados turno a turno
    reclamo_registrado: bool  # evita registrar el mismo reclamo dos veces en un hilo


# ---------------------------------------------------------------------------
# 3. Memoria a largo plazo persistida en un archivo JSON
# ---------------------------------------------------------------------------
class FileStore(InMemoryStore):
    """`InMemoryStore` que además respalda su contenido en un archivo JSON.

    `InMemoryStore` ya resuelve correctamente namespaces, búsquedas y demás:
    en vez de reimplementar esa lógica, la reutilizamos por herencia y solo
    añadimos dos cosas:
      - al construirse, carga lo que ya existía en el archivo (si existe);
      - después de cada escritura (`batch`, que es el método interno del que
        dependen tanto `put()` como `search()`), vuelca todo el contenido a
        disco.
    Con esto, el resto del código (`store.put(...)`, `store.search(...)`)
    no cambia respecto a la Sesion9: solo cambia qué clase se instancia.
    """

    def __init__(self, ruta_json: Path, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ruta_json = ruta_json
        self._cargar_desde_disco()

    def _cargar_desde_disco(self) -> None:
        if not self._ruta_json.exists():
            return
        contenido = self._ruta_json.read_text(encoding="utf-8").strip()
        if not contenido:
            return
        for entrada in json.loads(contenido):
            item = Item(
                value=entrada["value"],
                key=entrada["key"],
                namespace=tuple(entrada["namespace"]),
                created_at=entrada["created_at"],
                updated_at=entrada["updated_at"],
            )
            self._data[item.namespace][item.key] = item

    def _guardar_en_disco(self) -> None:
        todos_los_items = [
            item.dict()
            for items_por_namespace in self._data.values()
            for item in items_por_namespace.values()
        ]
        self._ruta_json.write_text(
            json.dumps(todos_los_items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def batch(self, ops):
        resultado = super().batch(ops)
        self._guardar_en_disco()
        return resultado


# ---------------------------------------------------------------------------
# 4. Estrategias de memoria a corto plazo (idénticas a la Sesion9)
# ---------------------------------------------------------------------------
def mensajes_full(state: State) -> list:
    """Sin gestión: todo el historial tal cual."""
    return state["messages"]


def mensajes_trim_count(state: State, keep_last: int = 4) -> list:
    """Recorta el ESTADO guardado, dejando solo los últimos `keep_last` mensajes."""
    messages = state["messages"]
    if len(messages) <= keep_last:
        return messages
    return messages[-keep_last:]


def mensajes_trim_tokens(state: State, max_tokens: int = 800) -> list:
    """No toca el estado guardado: solo genera una copia recortada por
    presupuesto de tokens para esta llamada al modelo."""
    return trim_messages(
        state["messages"],
        max_tokens=max_tokens,
        strategy="last",
        token_counter=count_tokens_approximately,
        start_on="human",
        include_system=True,
    )


def resumir_si_hace_falta(state: State, threshold: int = 6) -> Optional[dict]:
    """Si hay demasiados mensajes, resume los antiguos en `summary` y los
    elimina del checkpoint, dejando solo los últimos 2 (turno actual)."""
    messages = state["messages"]
    if len(messages) <= threshold:
        return None

    a_resumir = messages[:-2]
    resto = messages[-2:]

    prompt_resumen = (
        "Resume brevemente los datos relevantes de este reclamo bancario "
        "(nombre del cliente, documento, producto, descripción del problema). "
        f"Resumen previo: {state.get('summary', '(vacío)')}\n\n"
        f"Nuevos mensajes a incorporar: {[m.content for m in a_resumir]}"
    )
    nuevo_resumen = summarizer_model.invoke(prompt_resumen).content

    return {
        "summary": nuevo_resumen,
        "messages": [RemoveMessage(id=m.id) for m in a_resumir],
        "_resto": resto,
    }


# ---------------------------------------------------------------------------
# 5. Prompt del sistema y utilidades del dominio "reclamos"
# ---------------------------------------------------------------------------
NOMBRES_CAMPOS = {
    "nombre_completo": "nombre completo",
    "documento_identidad": "número de documento de identidad (DNI)",
    "producto": "producto sobre el que reclama",
    "descripcion": "descripción del problema",
}


def construir_system_prompt(
    contexto_usuario: str, resumen: str, datos_reclamo: dict, ya_registrado: bool
) -> str:
    catalogo = "\n".join(f"  - {p}" for p in PRODUCTOS_BANCARIOS)
    faltantes = [c for c in CAMPOS_OBLIGATORIOS if not datos_reclamo.get(c)]

    if ya_registrado:
        instrucciones = (
            "El reclamo de esta conversación ya fue registrado. Si el cliente "
            "pregunta algo más, respóndele normalmente (por ejemplo, tiempos de "
            "respuesta o cómo hacer seguimiento)."
        )
    elif faltantes:
        pendientes = ", ".join(NOMBRES_CAMPOS[c] for c in faltantes)
        instrucciones = (
            "Estás recolectando los datos de un reclamo. Todavía falta obtener: "
            f"{pendientes}. Pide uno o dos a la vez, de forma conversacional y "
            "amable, sin abrumar al cliente. No pidas datos que ya se muestran "
            "como conocidos más abajo."
        )
    else:
        instrucciones = (
            "Ya tienes los 4 datos del reclamo (ver más abajo): no pidas nada más "
            "ni sigas indagando. Responde con un mensaje breve confirmando que el "
            "reclamo quedó registrado y agradeciendo al cliente. No menciones "
            "ningún número de ticket ni escribas placeholders como '[número de "
            "ticket]': el sistema agrega el número real automáticamente después "
            "de tu respuesta."
        )

    datos_conocidos = "\n".join(
        f"  - {NOMBRES_CAMPOS[c]}: {datos_reclamo[c]}" for c in CAMPOS_OBLIGATORIOS if datos_reclamo.get(c)
    ) or "  (ninguno todavía)"

    system_msg = (
        f"Eres el asistente virtual de recepción de reclamos de {NOMBRE_BANCO} "
        "(entidad ficticia, demo educativa). Atiendes con cordialidad y en español.\n\n"
        f"Catálogo de productos válidos:\n{catalogo}\n\n"
        f"{instrucciones}\n\n"
        f"Datos del reclamo actual ya confirmados:\n{datos_conocidos}\n\n"
        f"Reclamos anteriores de este cliente (memoria de largo plazo, otras conversaciones):\n"
        f"{contexto_usuario or '  (sin reclamos previos registrados)'}"
    )
    if resumen:
        system_msg += f"\n\nResumen de esta conversación hasta ahora:\n{resumen}"
    return system_msg


def formatear_reclamos_previos(items) -> str:
    if not items:
        return ""
    lineas = []
    for item in items:
        v = item.value
        lineas.append(
            f"  - Ticket {v.get('ticket_id')}: {v.get('producto')} "
            f"(registrado el {v.get('fecha')}) - estado: {v.get('estado')}"
        )
    return "\n".join(lineas)


def generar_ticket_id() -> str:
    fecha = datetime.now().strftime("%Y%m%d")
    sufijo = uuid.uuid4().hex[:6].upper()
    return f"{fecha}-{sufijo}"


# --- Respaldo determinístico para "documento_identidad" y "producto" --------
# En la práctica, un modelo local pequeño (p. ej. llama3.2:3b) no siempre
# completa estos dos campos vía `extractor_model`, aunque el dato esté
# escrito de forma clara en el mensaje del cliente. A diferencia de
# "nombre_completo" o "descripcion" (texto libre, solo un LLM puede
# interpretarlos razonablemente), un DNI y un producto de catálogo tienen
# forma fija: se pueden reconocer con una expresión regular y un match de
# palabras clave, sin depender del LLM. Esto no reemplaza al extractor, solo
# complementa los casos donde se le escapa un dato obvio.
PATRON_DNI = re.compile(r"\b\d{6,10}\b")

PALABRAS_CLAVE_PRODUCTO: dict[str, list[str]] = {
    "Tarjeta de crédito": ["tarjeta de credito", "tarjeta credito"],
    "Tarjeta de débito": ["tarjeta de debito", "tarjeta debito"],
    "Cuenta de ahorros": ["cuenta de ahorro", "cuenta ahorro"],
    "Préstamo personal": ["prestamo personal", "prestamo"],
    "Banca por internet / app móvil": [
        "banca por internet", "banca movil", "app movil", "aplicacion movil", "banca en linea",
    ],
}


def _sin_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c)
    )


def extraer_dni_de_texto(texto: str) -> Optional[str]:
    match = PATRON_DNI.search(texto)
    return match.group(0) if match else None


def extraer_producto_de_texto(texto: str) -> Optional[str]:
    normalizado = _sin_acentos(texto)
    for producto, claves in PALABRAS_CLAVE_PRODUCTO.items():
        if any(clave in normalizado for clave in claves):
            return producto
    return None


# ---------------------------------------------------------------------------
# 6. Nodo del agente
# ---------------------------------------------------------------------------
def call_model(state: State, runtime: Runtime[Context]) -> dict[str, Any]:
    estrategia = runtime.context.memory_strategy
    user_id = runtime.context.user_id
    store = runtime.store
    namespace = ("reclamos", user_id)

    ya_registrado = state.get("reclamo_registrado", False)
    datos_reclamo = dict(state.get("datos_reclamo") or {})

    # --- Aplicar la estrategia de memoria a corto plazo elegida ---
    state_update: dict[str, Any] = {}
    if estrategia == "trim_count":
        mensajes_para_llm = mensajes_trim_count(state)
        a_borrar = (
            state["messages"][: -len(mensajes_para_llm)]
            if len(state["messages"]) > len(mensajes_para_llm)
            else []
        )
        state_update["messages"] = [RemoveMessage(id=m.id) for m in a_borrar]
    elif estrategia == "trim_tokens":
        mensajes_para_llm = mensajes_trim_tokens(state)
    elif estrategia == "summary":
        resultado = resumir_si_hace_falta(state)
        if resultado:
            state_update["summary"] = resultado["summary"]
            state_update["messages"] = resultado["messages"]
            mensajes_para_llm = resultado["_resto"]
        else:
            mensajes_para_llm = state["messages"]
    else:  # "full"
        mensajes_para_llm = mensajes_full(state)

    # --- Extracción estructurada: ¿qué datos del reclamo hay en la conversación? ---
    # Se hace ANTES de generar la respuesta conversacional (y no después) para
    # que, si el mensaje que el cliente acaba de escribir completa el último
    # dato que faltaba, el LLM que conversa ya lo sepa y cierre el turno
    # confirmando el reclamo en vez de seguir preguntando por algo que ya se
    # acaba de responder.
    if not ya_registrado:
        extraido = extractor_model.invoke(mensajes_para_llm)
        for campo in CAMPOS_OBLIGATORIOS:
            valor = getattr(extraido, campo)
            if valor:
                datos_reclamo[campo] = valor

        # Respaldo determinístico (ver comentario junto a las funciones): si el
        # LLM no capturó el DNI o el producto, se intenta reconocerlos con
        # reglas fijas sobre el último mensaje del cliente.
        ultimo_mensaje = state["messages"][-1].content if state["messages"] else ""
        if not datos_reclamo.get("documento_identidad"):
            dni = extraer_dni_de_texto(ultimo_mensaje)
            if dni:
                datos_reclamo["documento_identidad"] = dni
        if not datos_reclamo.get("producto"):
            producto = extraer_producto_de_texto(ultimo_mensaje)
            if producto:
                datos_reclamo["producto"] = producto

        state_update["datos_reclamo"] = datos_reclamo

    # --- Memoria a largo plazo: reclamos previos de este cliente (desde disco) ---
    reclamos_previos = store.search(namespace)
    contexto_usuario = formatear_reclamos_previos(reclamos_previos)

    system_msg = construir_system_prompt(contexto_usuario, state.get("summary", ""), datos_reclamo, ya_registrado)
    respuesta = model.invoke([{"role": "system", "content": system_msg}] + mensajes_para_llm)
    texto_respuesta = respuesta.content

    # --- Traspaso de corto -> largo plazo: ¿ya están los 4 datos y aún no se registró? ---
    if not ya_registrado and all(datos_reclamo.get(c) for c in CAMPOS_OBLIGATORIOS):
        ticket_id = generar_ticket_id()
        store.put(
            namespace,
            ticket_id,
            {
                "ticket_id": ticket_id,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "estado": "recibido",
                **datos_reclamo,
            },
        )
        state_update["reclamo_registrado"] = True
        texto_respuesta = f"{texto_respuesta}\n\n📋 Número de ticket: {ticket_id}"

    state_update["messages"] = state_update.get("messages", []) + [
        respuesta.model_copy(update={"content": texto_respuesta})
    ]
    return state_update


# ---------------------------------------------------------------------------
# 7. Construcción del grafo
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

CHECKPOINT_DB_PATH = DATA_DIR / "historial_chat.sqlite"
RECLAMOS_JSON_PATH = DATA_DIR / "reclamos_registrados.json"

builder = StateGraph(State, context_schema=Context)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")

store = FileStore(RECLAMOS_JSON_PATH)  # memoria a largo plazo -> archivo JSON


def construir_grafo(checkpointer):
    return builder.compile(checkpointer=checkpointer, store=store)


# ---------------------------------------------------------------------------
# 8. Chat interactivo por consola
# ---------------------------------------------------------------------------
def chat_interactivo(memory_strategy: str = "full") -> None:
    print(f"=== Recepción de reclamos - {NOMBRE_BANCO} ===")
    print("(escribe 'salir' para terminar la conversación)\n")

    documento = input("Para identificarte, indica tu número de documento (DNI): ").strip()

    # Usar el DNI tanto como user_id (memoria a largo plazo) como thread_id
    # (memoria a corto plazo) permite que, si el cliente cierra y vuelve a abrir
    # el programa con el mismo DNI, tanto su historial de chat (SqliteSaver)
    # como sus reclamos anteriores (FileStore) se recuperen del disco.
    config = {"configurable": {"thread_id": f"reclamo-{documento}"}}
    context = Context(user_id=documento, memory_strategy=memory_strategy)

    # SqliteSaver.from_conn_string abre (o crea) el archivo .sqlite y debe
    # usarse como context manager para cerrar bien la conexión al terminar.
    with SqliteSaver.from_conn_string(str(CHECKPOINT_DB_PATH)) as checkpointer:
        graph = construir_grafo(checkpointer)

        print("\nAgente: Hola, cuéntame en qué te puedo ayudar con tu reclamo.\n")
        while True:
            texto = input("Tú: ").strip()
            if texto.lower() in {"salir", "exit", "quit"}:
                print("\nAgente: Gracias por contactar a", NOMBRE_BANCO + ". ¡Hasta pronto!")
                break
            if not texto:
                continue

            resultado = graph.invoke(
                {"messages": [{"role": "user", "content": texto}]},
                config=config,
                context=context,
            )
            print(f"Agente: {resultado['messages'][-1].content}\n")


if __name__ == "__main__":
    chat_interactivo(memory_strategy="full")
