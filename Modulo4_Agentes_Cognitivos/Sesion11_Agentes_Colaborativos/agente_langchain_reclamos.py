"""
# Agente de recepción de reclamos bancarios (LangChain, memoria persistida a archivo)
######################################################################################

Misma tarea que `main.py` (LangGraph) pero construida con la API de agentes de
LangChain: `langchain.agents.create_agent`. Mismo alcance: catálogo completo de
5 productos bancarios, memoria a corto y largo plazo persistidas en disco, en
vez de en memoria RAM.

DIFERENCIA CLAVE DE ARQUITECTURA FRENTE A main.py
    `create_agent` está construido sobre LangGraph (por eso acepta los mismos
    parámetros `checkpointer=` y `store=`), pero expone un nivel de abstracción
    más alto: uno no escribe un nodo `call_model` a mano, sino que declara un
    `system_prompt` (fijo, se define una sola vez al crear el agente) y una
    lista de `tools`. El propio LangChain arma el bucle "modelo -> decide
    llamar una tool -> ejecuta la tool -> vuelve al modelo" por dentro.

    La consecuencia práctica: como el `system_prompt` no se puede reconstruir
    turno a turno (a diferencia del nodo de main.py, que sí regeneraba el
    prompt con los datos ya conocidos), la memoria de largo plazo aquí se
    expone como una TOOL (`consultar_reclamos_previos`) que el propio agente
    decide llamar, en vez de inyectarse "a la fuerza" en cada prompt. Es el
    patrón idiomático de LangChain: si el agente necesita un dato externo,
    se le da una tool para pedirlo.

MEMORIA A CORTO PLAZO (conversación de un cliente)
    `SqliteSaver` (idéntico a main.py) -> `data/historial_chat_langchain.sqlite`.
    Aquí no se reimplementan las 4 estrategias de gestión de mensajes de la
    Sesion9: `create_agent` no expone ese nivel de detalle sin escribir
    middleware propio, y no es el foco de este archivo (comparar LangGraph vs.
    LangChain). El historial completo del hilo se persiste tal cual.

MEMORIA A LARGO PLAZO (reclamos de otras conversaciones)
    Mismo `FileStore` que en main.py (subclase de `InMemoryStore` que además
    escribe a `data/reclamos_registrados_langchain.json`). Las tools acceden
    a él con `langgraph.config.get_store()`, que funciona dentro de cualquier
    grafo compilado con `store=...` -- y `create_agent` es justamente eso.

TRASPASO CORTO -> LARGO PLAZO
    Una tool, `registrar_reclamo`, hace el `store.put(...)`. El propio LLM
    decide cuándo llamarla (tras reunir los 4 datos Y pedir confirmación
    explícita al cliente) -- es el patrón de tool-calling estándar de
    LangChain, no una extracción estructurada paralela como en main.py.

Identificar al cliente entre tools: como `create_agent` no tiene un objeto de
contexto por-invocación como el `Context` de LangGraph, el DNI del cliente se
pasa en `config={"configurable": {"user_id": ...}}` al invocar, y cada tool lo
lee con `langgraph.config.get_config()`.

Requisitos (ya instalados en el venv compartido, ver requirements.txt):
    pip install -U langchain langgraph langgraph-checkpoint-sqlite langchain-anthropic python-dotenv

    Backend: Anthropic (Claude). Requiere en Sesion11/.env:
        ANTHROPIC_API_KEY=sk-ant-...
    Modelo: claude-sonnet-4-6 (ver ANTHROPIC_MODEL para cambiarlo).

Ejecutar el chat interactivo:
    python agente_langchain_reclamos.py
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.config import get_config, get_store
from langgraph.store.base import Item
from langgraph.store.memory import InMemoryStore

load_dotenv()  # lee Sesion11/.env (ANTHROPIC_API_KEY, ANTHROPIC_MODEL opcional)


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


# ---------------------------------------------------------------------------
# 2. Memoria a largo plazo persistida en un archivo JSON (igual que main.py)
# ---------------------------------------------------------------------------
class FileStore(InMemoryStore):
    """`InMemoryStore` que además respalda su contenido en un archivo JSON.

    Reutiliza toda la lógica de namespaces/búsqueda de `InMemoryStore` y solo
    añade una carga inicial desde disco y un volcado tras cada escritura
    (`batch`, el método interno del que dependen `put()` y `search()`).
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
# 3. Tools: acceso a la memoria de largo plazo (store) y al cliente actual
# ---------------------------------------------------------------------------
def _namespace_del_cliente() -> tuple[str, ...]:
    """El DNI viaja en config.configurable.user_id (ver chat_interactivo)."""
    user_id = get_config()["configurable"]["user_id"]
    return ("reclamos", user_id)


@tool
def consultar_reclamos_previos() -> str:
    """Consulta los reclamos que este cliente ya registró en conversaciones
    anteriores. Úsala al comienzo de la conversación (o si el cliente
    menciona un reclamo anterior) para no pedirle datos que ya se conocen
    y para poder responder sobre el estado de reclamos previos."""
    items = get_store().search(_namespace_del_cliente())
    if not items:
        return "Este cliente no tiene reclamos previos registrados."
    return "\n".join(
        f"- Ticket {i.value['ticket_id']}: {i.value['producto']} "
        f"(registrado el {i.value['fecha']}) - estado: {i.value['estado']}"
        for i in items
    )


@tool
def registrar_reclamo(
    nombre_completo: str,
    documento_identidad: str,
    producto: str,
    descripcion: str,
) -> str:
    """Registra un reclamo bancario ya confirmado.

    Solo debe llamarse cuando ya se reunieron los 4 datos (nombre completo,
    documento de identidad, producto, descripción del problema) Y el cliente
    confirmó expresamente que quiere registrar el reclamo. `producto` debe
    ser exactamente uno de los productos del catálogo (ver el system prompt).
    """
    if producto not in PRODUCTOS_BANCARIOS:
        return (
            "No se registró el reclamo: 'producto' debe ser exactamente uno de: "
            + ", ".join(PRODUCTOS_BANCARIOS)
        )
    if not documento_identidad.strip().isdigit():
        return "No se registró el reclamo: el documento de identidad debe contener solo números."

    ticket_id = f"{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"
    get_store().put(
        _namespace_del_cliente(),
        ticket_id,
        {
            "ticket_id": ticket_id,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "estado": "recibido",
            "nombre_completo": nombre_completo,
            "documento_identidad": documento_identidad,
            "producto": producto,
            "descripcion": descripcion,
        },
    )
    return f"Reclamo registrado correctamente. Número de ticket: {ticket_id}."


# ---------------------------------------------------------------------------
# 4. Prompt del sistema
# ---------------------------------------------------------------------------
PROMPT_SISTEMA = f"""
Eres el asistente virtual de recepción de reclamos de {NOMBRE_BANCO}
(entidad ficticia, demo educativa). Atiendes con cordialidad y en español.

Catálogo de productos válidos (usa el texto exacto al registrar un reclamo):
{chr(10).join(f"  - {p}" for p in PRODUCTOS_BANCARIOS)}

Al comienzo de la conversación, usa la herramienta consultar_reclamos_previos
para saber si este cliente ya tiene reclamos registrados anteriormente.

Para registrar un nuevo reclamo debes reunir, de forma conversacional y sin
abrumar al cliente (pide uno o dos datos a la vez):
  1. Nombre completo
  2. Número de documento de identidad (DNI)
  3. Producto sobre el que reclama (debe ser uno de la lista de arriba)
  4. Descripción del problema

Reglas obligatorias:
  - Nunca pidas el número completo de una tarjeta, ni contraseñas, PIN, CVV
    o códigos enviados por SMS/email.
  - No inventes datos que el cliente no haya proporcionado.
  - Antes de registrar, resume el reclamo y pregunta al cliente si confirma.
  - Solo después de una confirmación explícita, usa la herramienta
    registrar_reclamo.
  - Al finalizar, comunica el número de ticket devuelto por la herramienta
    (no inventes uno tú mismo).
  - Si el reclamo es sobre un consumo no reconocido en una tarjeta,
    recomienda al cliente contactar los canales oficiales para bloquearla
    temporalmente; no afirmes haber bloqueado nada, ya que no tienes esa
    capacidad.
"""


# ---------------------------------------------------------------------------
# 5. Construcción del agente
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

CHECKPOINT_DB_PATH = DATA_DIR / "historial_chat_langchain.sqlite"
RECLAMOS_JSON_PATH = DATA_DIR / "reclamos_registrados_langchain.json"

store = FileStore(RECLAMOS_JSON_PATH)  # memoria a largo plazo -> archivo JSON


def construir_agente(checkpointer):
    return create_agent(
        model=f"anthropic:{os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-6')}",
        system_prompt=PROMPT_SISTEMA,
        tools=[consultar_reclamos_previos, registrar_reclamo],
        checkpointer=checkpointer,
        store=store,
    )


# ---------------------------------------------------------------------------
# 6. Chat interactivo por consola
# ---------------------------------------------------------------------------
def chat_interactivo() -> None:
    print(f"=== Recepción de reclamos - {NOMBRE_BANCO} (LangChain) ===")
    print("(escribe 'salir' para terminar la conversación)\n")

    documento = input("Para identificarte, indica tu número de documento (DNI): ").strip()

    # El DNI se usa como thread_id (memoria a corto plazo, vía checkpointer) y
    # como user_id en config.configurable (memoria a largo plazo, lo leen las
    # tools con get_config()). Así, si el cliente vuelve otro día con el mismo
    # DNI, ambas memorias se recuperan del disco.
    config = {"configurable": {"thread_id": f"reclamo-{documento}", "user_id": documento}}

    with SqliteSaver.from_conn_string(str(CHECKPOINT_DB_PATH)) as checkpointer:
        agent = construir_agente(checkpointer)

        print("\nAgente: Hola, cuéntame en qué te puedo ayudar con tu reclamo.\n")
        while True:
            texto = input("Tú: ").strip()
            if texto.lower() in {"salir", "exit", "quit"}:
                print("\nAgente: Gracias por contactar a", NOMBRE_BANCO + ". ¡Hasta pronto!")
                break
            if not texto:
                continue

            resultado = agent.invoke(
                {"messages": [{"role": "user", "content": texto}]},
                config=config,
            )
            print(f"Agente: {resultado['messages'][-1].content}\n")


if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "No se encontró ANTHROPIC_API_KEY. Agrégala a Sesion11/.env."
        )
    chat_interactivo()
