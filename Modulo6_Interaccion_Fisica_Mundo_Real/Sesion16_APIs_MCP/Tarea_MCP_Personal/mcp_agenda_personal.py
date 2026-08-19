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
