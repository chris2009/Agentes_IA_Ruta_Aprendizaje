# MCP Server Personal: Agenda + Notas

**Tarea Sesión 16 (APIs & MCP) — Programa Diseño e Implementación de Agentes IA, UTEC Posgrado.**
Tipo: PERSONAL. Fecha límite: 15/08.

## Objetivo

Construir y probar, de principio a fin, un **MCP Server** (*Model Context Protocol Server*, servidor del **MCP** — *Model Context Protocol*, protocolo de contexto de modelo: el estándar abierto que permite que una aplicación de IA como Claude descubra y use herramientas externas de forma estandarizada) de autoría propia que ayude en el día a día, conectado a Claude tanto en modo desarrollo (prueba en memoria) como en un cliente MCP real (Claude Desktop y Claude Code).

## Qué es un MCP Server y por qué me importa

Hasta ahora, si quería que Claude hiciera algo con un sistema externo mío — mis archivos, mi calendario, lo que sea — tenía que programar una integración específica para esa combinación. Si mañana cambiaba de aplicación de IA, tocaba rehacerla desde cero. **MCP** (*Model Context Protocol*, protocolo de contexto de modelo) resuelve justo ese problema: es un estándar abierto para que cualquier aplicación de IA se conecte a cualquier sistema externo de la misma forma. La comparación que usa el material del curso es literal: MCP es para el contexto de una IA lo que el **USB-C** es para un cable — un solo conector que sirve para todo, en vez de uno distinto por cada dispositivo.

En la práctica, un **MCP Server** es un programa que expone tres cosas a la aplicación de IA que se conecta a él (el **MCP Host**, por ejemplo Claude Desktop o Claude Code): herramientas que el modelo puede ejecutar (siempre pidiendo tu aprobación antes de cada llamada — MCP nunca deja que el modelo actúe a tus espaldas), datos de contexto que puede leer, y plantillas de prompts reutilizables. Eso es exactamente lo que construí para esta tarea: un servidor MCP propio, chico, que resuelve algo que uso de verdad — llevar mis pendientes del curso y anotar ideas sueltas — y que Claude puede operar directamente desde el chat, con aprobación mía en cada acción.

El detalle completo de la teoría (arquitectura Host/Client/Server, capas de datos/transporte, MCP vs *function calling* clásico, autenticación) está en `Sesion16_APIs_MCP_ANALISIS_COMPLETO.md`, en la carpeta padre de esta tarea.

## De dónde salió la idea: agenda de tareas + notas rápidas

En vez de inventar un caso de uso desde cero, partí del ejemplo más simple que trae el material de la Sesión 16 (`mcpdesktop.py`, dentro de `agents26_m6s16-main/`), que solo guarda notas de texto en un archivo. Lo tomé como punto de partida y lo llevé un poco más lejos, en dos sentidos.

Primero, leyendo ese archivo de ejemplo con cuidado encontré dos errores reales — del tipo que solo se nota si de verdad lo corres, no leyéndolo por encima. `f.readlines` está escrito sin los paréntesis, así que queda apuntando al método en sí en vez de a la lista de líneas que devuelve. Y hay una línea que intenta sumar un texto con un conjunto (`f"Summarize current notes: " + {content}`), algo que en Python explota apenas se ejecuta. Los evité desde el diseño de mi versión.

Segundo, en vez de quedarme solo con notas sueltas, le agregué tareas de verdad: con ID, estado (pendiente o completada) y fecha límite. Con eso mi servidor termina usando las tres piezas que puede exponer un MCP Server —herramientas, un recurso de resumen y un prompt de planificación— sobre algo que realmente uso día a día, no un ejemplo de juguete.

## Arquitectura

- **Transporte:** **STDIO** (*Standard Input/Output*, entrada/salida estándar) — local. El host (Claude Desktop o Claude Code) lanza el script como proceso hijo y le habla por sus canales de entrada/salida; no hace falta levantar un puerto HTTP.
- **Persistencia:** un único archivo `agenda_personal.json` (tareas + notas), en la misma carpeta del servidor. Se crea automáticamente en el primer uso.
- **Framework:** **FastMCP** — la capa de alto nivel sobre el SDK oficial de MCP. El schema **JSON** (*JavaScript Object Notation*, formato de intercambio de datos estructurado) de entrada/salida de cada tool se infiere automáticamente de los *type hints* de Python — no se escribe el protocolo **JSON-RPC** (*JSON Remote Procedure Call*, invocación remota de funciones codificada en JSON) a mano.

```
Claude (Host: Desktop o Code)
        │  STDIO
        ▼
mcp_agenda_personal.py (FastMCP)
        │
        ▼
agenda_personal.json  (tareas + notas, persistente en disco)
```

## Tools, Resource y Prompt expuestos

| Primitiva | Nombre completo | Qué hace |
|---|---|---|
| Tool | `agregar_tarea(descripcion, fecha_limite="")` | Agrega una tarea pendiente, devuelve el ID asignado. |
| Tool | `listar_tareas(solo_pendientes=True)` | Lista tareas (por default, solo las no completadas). |
| Tool | `completar_tarea(task_id)` | Marca una tarea como completada. |
| Tool | `eliminar_tarea(task_id)` | Elimina una tarea (acción irreversible). |
| Tool | `agregar_nota(contenido)` | Guarda una nota de texto libre. |
| Tool | `buscar_notas(query)` | Busca notas que contengan un texto dado. |
| Resource | `agenda://resumen` | Resumen en texto de tareas pendientes + cantidad de notas guardadas. |
| Prompt | `planificar_mi_dia()` | Arma un prompt para que el modelo priorice el día según las tareas pendientes actuales. |

## Cómo se probó (tres niveles, de menor a mayor integración real)

### 1) Prueba en memoria — servidor y cliente MCP en el mismo proceso

Usando el mismo patrón que `allinone.py` del material de la sesión (`create_connected_server_and_client_session`), sin abrir ningún puerto ni depender de Claude:

```bash
python test_client.py
```

**Resultado real de la corrida** (extracto):

```
Tools disponibles: ['agregar_tarea', 'listar_tareas', 'completar_tarea',
                     'eliminar_tarea', 'agregar_nota', 'buscar_notas']

agregar_tarea -> Tarea #1 agregada: 'Entregar tarea de MCP' (vence 2026-08-15)
agregar_tarea -> Tarea #2 agregada: 'Repasar Sesion 16 antes del lab'
agregar_nota -> Nota guardada.

listar_tareas -> [ {"id": 1, "descripcion": "Entregar tarea de MCP", ...},
                    {"id": 2, "descripcion": "Repasar Sesion 16 antes del lab", ...} ]

completar_tarea -> Tarea #2 marcada como completada.

buscar_notas -> [ {"texto": "MCP agrega discovery + approval sobre function calling", ...} ]

resource agenda://resumen ->
Tareas pendientes: 1
  - #1 Entregar tarea de MCP (vence 2026-08-15)
Notas guardadas: 1

prompt planificar_mi_dia ->
Estas son mis tareas pendientes:
- #1 Entregar tarea de MCP (vence 2026-08-15)

Ayudame a priorizarlas para hoy y sugiereme un orden razonable.
```

**Bug real encontrado y corregido durante esta prueba:** la primera versión de `test_client.py` leía `r.structured_content` (snake_case) y falló con `AttributeError: 'CallToolResult' object has no attribute 'structured_content'. Did you mean: 'structuredContent'?`. El atributo correcto es `structuredContent` (camelCase) — se corrigió y se volvió a correr, confirmando que las 6 tools, el resource y el prompt responden bien.

### 2) Registro real con Claude Code (CLI)

Se registró el servidor con el comando oficial de Claude Code y se verificó su conexión sin depender de una captura de pantalla de un chat — con el propio CLI:

```bash
claude mcp add --scope local --transport stdio agenda-personal -- \
    /ruta/a/tu/venv/bin/python /ruta/completa/a/mcp_agenda_personal.py

claude mcp list
```

**Resultado real:**

```
Checking MCP server health…
agenda-personal: .../mcp_agenda_personal.py - ✓ Connected
```

```
agenda-personal:
  Scope: Local config (private to you in this project)
  Status: ✓ Connected
  Type: stdio
  Command: .../.venv/bin/python
  Args: .../mcp_agenda_personal.py
```

Esto confirma, con Claude Code real (no solo con el cliente de prueba propio), que el servidor arranca, responde al *handshake* del protocolo y queda listo para que el modelo descubra sus tools.

### 3) Conectarlo a Claude Desktop o a un chat real de Claude Code

```bash
uv run mcp install mcp_agenda_personal.py     # Claude Desktop
claude                                         # Claude Code, dentro de un chat
```

En ambos casos, al pedirle a Claude algo como *"agrega una tarea a mi agenda: entregar la tarea de MCP, vence 2026-08-15"*, el modelo propone invocar `agregar_tarea` y **pide aprobación explícita del usuario antes de ejecutarla** — el paso de *"MCP Tool approval"* que distingue a MCP del *function calling* clásico (donde el modelo invoca la función directamente, sin ese paso intermedio). Instrucciones completas, con el detalle de rutas en Windows/WSL, en `README.md` de esta misma carpeta.

## Código completo

### `mcp_agenda_personal.py` — el servidor MCP

```python
"""
MCP Server personal: Agenda + Notas rapidas.

Tarea Sesion 16 (APIs & MCP) - Programa Diseno e Implementacion de Agentes IA, UTEC Posgrado.

Para conectarlo a Claude Desktop:
    uv run mcp install mcp_agenda_personal.py
    (y reiniciar Claude Desktop)

Para probarlo sin Claude Desktop (cliente + servidor en memoria):
    python test_client.py
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime

from fastmcp import FastMCP

DATA_FILE = os.path.join(os.path.dirname(__file__), "agenda_personal.json")

mcp = FastMCP("Agenda Personal")


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"tareas": [], "notas": [], "next_id": 1}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@dataclass
class Tarea:
    id: int
    descripcion: str
    fecha_limite: str
    completada: bool
    creada: str


@mcp.tool()
def agregar_tarea(descripcion: str, fecha_limite: str = "") -> str:
    """
    Agrega una nueva tarea pendiente a la agenda personal.

    Args:
        descripcion: que hay que hacer (ej. "Entregar tarea de MCP").
        fecha_limite: fecha limite en formato YYYY-MM-DD, opcional.

    Returns:
        Confirmacion con el ID asignado a la tarea.
    """
    data = _load()
    tarea = Tarea(
        id=data["next_id"],
        descripcion=descripcion,
        fecha_limite=fecha_limite,
        completada=False,
        creada=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    data["tareas"].append(asdict(tarea))
    data["next_id"] += 1
    _save(data)
    sufijo = f" (vence {fecha_limite})" if fecha_limite else ""
    return f"Tarea #{tarea.id} agregada: '{descripcion}'{sufijo}"


@mcp.tool()
def listar_tareas(solo_pendientes: bool = True) -> list[dict]:
    """
    Lista las tareas de la agenda personal.

    Args:
        solo_pendientes: si es True (default), omite las tareas ya completadas.

    Returns:
        Lista de tareas con id, descripcion, fecha_limite, completada y creada.
    """
    data = _load()
    tareas = data["tareas"]
    if solo_pendientes:
        tareas = [t for t in tareas if not t["completada"]]
    return tareas


@mcp.tool()
def completar_tarea(task_id: int) -> str:
    """
    Marca una tarea como completada.

    Args:
        task_id: el ID de la tarea (ver listar_tareas).

    Returns:
        Confirmacion, o mensaje indicando que el ID no existe.
    """
    data = _load()
    for t in data["tareas"]:
        if t["id"] == task_id:
            t["completada"] = True
            _save(data)
            return f"Tarea #{task_id} marcada como completada."
    return f"No existe una tarea con ID {task_id}."


@mcp.tool()
def eliminar_tarea(task_id: int) -> str:
    """
    Elimina una tarea de la agenda (accion irreversible).

    Args:
        task_id: el ID de la tarea a eliminar.

    Returns:
        Confirmacion, o mensaje indicando que el ID no existe.
    """
    data = _load()
    antes = len(data["tareas"])
    data["tareas"] = [t for t in data["tareas"] if t["id"] != task_id]
    if len(data["tareas"]) == antes:
        return f"No existe una tarea con ID {task_id}."
    _save(data)
    return f"Tarea #{task_id} eliminada."


@mcp.tool()
def agregar_nota(contenido: str) -> str:
    """
    Guarda una nota rapida de texto libre (idea, recordatorio, enlace, etc).

    Args:
        contenido: el texto de la nota.

    Returns:
        Confirmacion de que la nota fue guardada.
    """
    data = _load()
    data["notas"].append(
        {"texto": contenido, "creada": datetime.now().strftime("%Y-%m-%d %H:%M")}
    )
    _save(data)
    return "Nota guardada."


@mcp.tool()
def buscar_notas(query: str) -> list[dict]:
    """
    Busca notas que contengan un texto dado (sin distinguir mayusculas/minusculas).

    Args:
        query: texto a buscar dentro de las notas.

    Returns:
        Lista de notas que coinciden, con su fecha de creacion.
    """
    data = _load()
    q = query.lower()
    return [n for n in data["notas"] if q in n["texto"].lower()]


@mcp.resource("agenda://resumen")
def resumen_agenda() -> str:
    """Resumen en texto plano de tareas pendientes y cantidad de notas guardadas."""
    data = _load()
    pendientes = [t for t in data["tareas"] if not t["completada"]]
    lineas = [f"Tareas pendientes: {len(pendientes)}"]
    for t in pendientes:
        venc = f" (vence {t['fecha_limite']})" if t["fecha_limite"] else ""
        lineas.append(f"  - #{t['id']} {t['descripcion']}{venc}")
    lineas.append(f"Notas guardadas: {len(data['notas'])}")
    return "\n".join(lineas)


@mcp.prompt()
def planificar_mi_dia() -> str:
    """Genera un prompt para que el modelo priorice el dia en base a la agenda actual."""
    data = _load()
    pendientes = [t for t in data["tareas"] if not t["completada"]]
    if not pendientes:
        return "No hay tareas pendientes. Pregunta al usuario si quiere agregar alguna para hoy."
    detalle = "\n".join(
        f"- #{t['id']} {t['descripcion']}"
        + (f" (vence {t['fecha_limite']})" if t["fecha_limite"] else "")
        for t in pendientes
    )
    return (
        "Estas son mis tareas pendientes:\n"
        f"{detalle}\n\n"
        "Ayudame a priorizarlas para hoy y sugiereme un orden razonable."
    )


if __name__ == "__main__":
    mcp.run()
```

### `test_client.py` — prueba en memoria (servidor + cliente en el mismo proceso)

```python
"""
Prueba del MCP Server 'Agenda Personal' sin necesidad de Claude Desktop.
Corre servidor y cliente en el mismo proceso, en memoria (mismo patron que
allinone.py de agents26_m6s16-main, Seccion 6.4 del analisis de la Sesion 16).

Uso:
    python test_client.py
"""

import asyncio
import json

from mcp.shared.memory import create_connected_server_and_client_session as client_session

from mcp_agenda_personal import mcp


async def main():
    async with client_session(mcp._mcp_server) as client:
        tools = await client.list_tools()
        print("Tools disponibles:", [t.name for t in tools.tools])
        print()

        r = await client.call_tool(
            "agregar_tarea",
            {"descripcion": "Entregar tarea de MCP", "fecha_limite": "2026-08-15"},
        )
        print("agregar_tarea ->", r.content[0].text)

        r = await client.call_tool(
            "agregar_tarea", {"descripcion": "Repasar Sesion 16 antes del lab"}
        )
        print("agregar_tarea ->", r.content[0].text)

        r = await client.call_tool(
            "agregar_nota",
            {"contenido": "MCP agrega discovery + approval sobre function calling"},
        )
        print("agregar_nota ->", r.content[0].text)

        r = await client.call_tool("listar_tareas", {"solo_pendientes": True})
        print("\nlistar_tareas ->")
        print(json.dumps(r.structuredContent, indent=2, ensure_ascii=False))

        r = await client.call_tool("completar_tarea", {"task_id": 2})
        print("\ncompletar_tarea ->", r.content[0].text)

        r = await client.call_tool("buscar_notas", {"query": "function calling"})
        print("\nbuscar_notas ->")
        print(json.dumps(r.structuredContent, indent=2, ensure_ascii=False))

        r = await client.read_resource("agenda://resumen")
        print("\nresource agenda://resumen ->")
        print(r.contents[0].text)

        r = await client.get_prompt("planificar_mi_dia")
        print("\nprompt planificar_mi_dia ->")
        print(r.messages[0].content.text)


if __name__ == "__main__":
    asyncio.run(main())
```

## Declaración de transparencia de IA

Usé Claude Code (Anthropic) como asistente para esta tarea. El alcance lo decidí yo: el asistente me propuso varias opciones de MCP Server personal (notas simples, envolver el RAG de mis materiales, envolver Google Calendar, o algo nuevo), y elegí la agenda de tareas y notas, partiendo del ejemplo más simple del material del curso en vez de mi proyecto `AgentePersonal-Web`, por el plazo de entrega.

A partir de esa decisión, el asistente escribió el código (`mcp_agenda_personal.py`, `test_client.py`), el `README.md` y esta documentación — incluyendo la corrección de los dos bugs reales que encontramos en el `mcpdesktop.py` del material del curso.
