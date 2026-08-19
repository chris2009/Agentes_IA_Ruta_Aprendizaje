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
