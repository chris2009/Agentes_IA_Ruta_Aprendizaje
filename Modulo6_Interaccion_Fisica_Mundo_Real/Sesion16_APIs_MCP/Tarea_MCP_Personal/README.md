# Tarea Sesion 16 — MCP Server Personal: Agenda + Notas

> **Tipo:** PERSONAL. **Entregable:** definicion del MCP Server en Python + screenshots de Claude/terminal + PDF. **Fecha limite:** 15/08.

## Que es

Un **MCP** (*Model Context Protocol*, protocolo de contexto de modelo) es el estandar que permite que Claude (u otra app de IA) se conecte a un sistema externo sin que alguien tenga que programar una integracion a medida para esa combinacion especifica — la comparacion del propio material del curso es el USB-C: un solo conector que sirve para todo. Este proyecto es un **MCP Server** (el "sistema externo" del otro lado de esa conexion) construido con **FastMCP**, que expone una agenda personal: tareas pendientes y notas rapidas de texto libre. Ver `Sesion16_APIs_MCP_ANALISIS_COMPLETO.md` (carpeta padre) para la teoria completa.

## Por que esta idea

Parti del ejemplo mas simple que trae el material de la Sesion 16 (`mcpdesktop.py`), que solo guardaba notas en un archivo. Al leerlo con cuidado encontre dos errores reales que solo aparecen al ejecutarlo — `f.readlines` sin `()` (queda apuntando al metodo, no a la lista de lineas) y una concatenacion invalida `str + {set}` — y los evite desde el diseno de mi version. Ademas del arreglo, amplie el alcance: en vez de solo notas sueltas, agregue tareas de verdad (con ID, estado y fecha limite), para terminar usando las tres piezas que puede exponer un MCP Server (Tools, Resources, Prompts) sobre algo que uso en el dia a dia.

## Arquitectura

- **Transporte:** STDIO (local) — el mismo patron de `sample.py`/`mcpdesktop.py` del material: Claude Desktop lanza el script como proceso hijo, no hace falta levantar un puerto HTTP.
- **Persistencia:** `agenda_personal.json` en la misma carpeta (tareas + notas), se crea solo en el primer uso.
- **Framework:** FastMCP — el schema JSON de entrada/salida de cada tool se infiere automaticamente de los *type hints* de Python.

## Tools, Resource y Prompt expuestos

| Primitiva | Nombre | Que hace |
|---|---|---|
| Tool | `agregar_tarea(descripcion, fecha_limite="")` | Agrega una tarea pendiente, devuelve el ID asignado. |
| Tool | `listar_tareas(solo_pendientes=True)` | Lista tareas (por default, solo las no completadas). |
| Tool | `completar_tarea(task_id)` | Marca una tarea como completada. |
| Tool | `eliminar_tarea(task_id)` | Elimina una tarea (irreversible). |
| Tool | `agregar_nota(contenido)` | Guarda una nota de texto libre. |
| Tool | `buscar_notas(query)` | Busca notas que contengan un texto dado. |
| Resource | `agenda://resumen` | Resumen en texto de tareas pendientes + cantidad de notas. |
| Prompt | `planificar_mi_dia()` | Arma un prompt para que el modelo priorice el dia segun las tareas pendientes actuales. |

## Como probarlo

### 1) Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2) Prueba en memoria (sin Claude Desktop)

Corre servidor y cliente en el mismo proceso — util para verificar que las tools funcionan antes de conectar Claude:

```bash
python test_client.py
```

### 3) Conectarlo a Claude Code (CLI) — paso a paso, con capturas

Esta es la via recomendada para esta tarea: no requiere instalar nada nuevo (Claude Desktop **no esta instalado** en esta maquina — se verifico, no hay carpeta de config ni ejecutable) y ya quedo probada de punta a punta. El servidor **ya esta registrado** (se hizo una vez con `claude mcp add`), asi que estos pasos son solo para que tu lo verifiques y saques tus propias capturas.

**Paso 1 — Abrir la terminal correcta (WSL, no PowerShell ni git-bash):**

En VS Code: click en el icono `+` de la pestaña de terminal → click en la flechita `v` al lado → elegir **"Ubuntu (WSL)"** de la lista.
Si no aparece, abre el menu Windows y escribe `Ubuntu` — se abre una terminal WSL directamente.
(Es obligatorio que sea WSL: ahi es donde estan instalados `claude`, `uv` y el venv con `fastmcp`/`mcp`. En PowerShell o git-bash de Windows esos comandos no existen.)

**Paso 2 — Ir a la carpeta del proyecto:**

```bash
cd /mnt/d/APRENDIZAJE/PROGRAMA_IMPLEMENTACION_AGENTES_IA
```

**Paso 3 — Verificar que el servidor sigue conectado → CAPTURA #1:**

```bash
claude mcp list
```

Debe mostrar:
```
agenda-personal: ... - ✓ Connected
```

📸 **Captura de pantalla aqui.**

**Paso 4 — Entrar a un chat real de Claude Code:**

```bash
claude
```

Si pide iniciar sesion, sigue el flujo (se abre el navegador, inicias sesion, vuelve solo a la terminal).

**Paso 5 — Pedirle que use la tool → CAPTURA #2 (la mas importante):**

Dentro del chat, escribir:

```
Agrega una tarea a mi agenda personal: "Entregar tarea de MCP", fecha limite 2026-08-15
```

Va a aparecer un cuadro pidiendo aprobacion antes de ejecutar la tool (tipo *"Claude wants to use mcp__agenda-personal__agregar_tarea — Allow?"*). **Esa pantalla es la captura clave** — es el paso de *"MCP Tool approval"* que distingue a MCP del *function calling* clasico (ver §4.3 del analisis de la sesion).

📸 **Captura de pantalla aqui.**

**Paso 6 — Aprobar y ver la respuesta → CAPTURA #3:**

Aceptar (`y` o "Allow"). Capturar la respuesta final donde Claude confirma que agrego la tarea.

📸 **Captura de pantalla aqui.**

**Paso 7 (opcional) — Ver el panel MCP completo:**

Dentro del mismo chat:

```
/mcp
```

Muestra el servidor conectado con sus 6 tools, 1 resource y 1 prompt listados.

📸 **Captura opcional.**

**Para quitar el servidor despues (no es necesario para la entrega):**

```bash
claude mcp remove agenda-personal -s local
```

### 4) Conectarlo a Claude Desktop (opcional, no instalado en esta maquina)

Si en algun momento instalas Claude Desktop (`claude.ai/download`), la conexion es asi — pero **no hace falta para esta tarea**, ya que Claude Code (paso 3) ya cubre la misma verificacion (conexion real + tool approval):

```bash
uv run mcp install mcp_agenda_personal.py
```

Correr ese comando en la misma terminal WSL del paso 3 (ahi es donde esta `uv` instalado), y despues reiniciar la **ventana** de la app Claude Desktop (es una app de escritorio, no tiene consola propia — el comando de arriba se corre afuera, en la terminal). El servidor "Agenda Personal" aparece en su lista de MCP Servers conectados.

## Screenshots

Checklist de capturas para el entregable (ver Paso a Paso arriba):

1. Terminal corriendo `python test_client.py` con la salida de las tools, el resource y el prompt.
2. Terminal corriendo `claude mcp list` mostrando `agenda-personal: ... ✓ Connected`.
3. Chat de Claude Code mostrando el cuadro de aprobacion de la tool (*"MCP Tool approval"*).
4. Chat de Claude Code mostrando la respuesta final confirmando que la tarea se agrego.
