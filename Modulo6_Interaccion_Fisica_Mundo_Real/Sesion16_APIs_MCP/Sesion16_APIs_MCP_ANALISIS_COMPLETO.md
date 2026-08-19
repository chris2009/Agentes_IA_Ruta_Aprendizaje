# APIs vs MCP — Análisis completo de la Sesión 16

> **Fuente base:** *Agentes IA — Tooling [APIs, MCPs]* — Módulo 5 (Herramientas para Orquestación), Programa en Diseño e Implementación de Agentes IA, UTEC Posgrado. Dictada por MEng. Boris Alzamora (mismo docente de las Sesiones 9, 13, 14 y 15).
> **Nota técnica:** el PDF original (`SES16_M6_APIs_MCP.pdf`) traía una restricción de permisos que impedía leerlo con herramientas estándar de extracción; se regeneró una copia sin esa restricción, se extrajo el texto disponible y se **renderizó e interpretó visualmente** cada una de las 26 diapositivas (varias son solo diagramas, sin capa de texto). Además del PDF, esta sesión trae una carpeta de código real (`agents26_m6s16-main/`) que se revisó archivo por archivo — no solo se resume la teoría, se contrasta contra el código de ejemplo.
> **Hallazgo clave de esta sesión:** la diapositiva 20 (§7) conserva, sin limpiar, una respuesta conversacional típica de un asistente de IA ("¿Quieres que formalice esta tabla en JSON...? También puedo ayudarte a diseñar un benchmark...") — evidencia directa, dentro del propio material del curso, de que esa diapositiva se generó con un LLM y no se editó antes de publicarse. Es un recordatorio útil del mismo punto que trae la Sesión 14 sobre verificar lo que un modelo genera antes de darlo por bueno.

---

## 1. Objetivos y Agenda

**Objetivos declarados:**
1. Entender las diferencias entre integrar **API** (*Application Programming Interface*, interfaz de programación de aplicaciones — el mecanismo estándar por el que dos programas se comunican) vs **MCP** (*Model Context Protocol*, protocolo de contexto de modelo) con agentes.
2. Comprender cómo implementar un **MCP Server** y conectar agentes a estos.

**Agenda — Parte 1:**
| # | Tema |
|---|---|
| 1 | ¿Qué es MCP? |
| 2 | Conceptos fundamentales |
| 3 | Arquitectura |
| 4 | MCP Tools, Resources, Prompts |
| 5 | Lab: Aterrizando a proyectos — ¿MCP Server de un proveedor, o implementar el propio? |

**Agenda — Parte 2:**
| # | Tema |
|---|---|
| 6 | APIs vs MCPs |
| 7 | MCP Authentication |

---

## 2. Qué es MCP

> *"MCP (Model Context Protocol): Estándar Open Source para conectar aplicaciones de IA a sistemas externos."*

Mediante MCP, aplicaciones de IA como Claude o ChatGPT pueden conectarse a:
- **Fuentes de datos** (ej. archivos locales, bases de datos).
- **Herramientas** (ej. motores de búsqueda, calculadoras).
- **Workflows** (ej. prompts especializados) — lo que les permite acceder a información clave y realizar tareas.

**La analogía del material:** *"MCP es como un puerto USB-C para aplicaciones de IA. Así como USB-C proporciona una forma estandarizada de conectar dispositivos electrónicos, MCP también proporciona una forma estandarizada de conectar aplicaciones de IA a sistemas externos."*

El diagrama original (el mismo que usa Anthropic en su anuncio de MCP) lo muestra como un hub central — el logo de Anthropic actuando de concentrador — con varios **MCP Servers** (A, B, C) conectados por el mismo protocolo a distintos sistemas (una computadora, una base de datos, la web), con la nota: *"All the integrations follow the same protocol making easy to build connectors to provide information."* La idea central: **un solo protocolo, muchos conectores intercambiables** — no una integración a medida por cada combinación app↔sistema.

**¿Qué puede habilitar MCP?** (ejemplos del material):
- Un agente accede a tu Google Calendar y Notion, actuando como asistente personalizado.
- Claude Code genera una aplicación web completa a partir de un diseño de Figma.
- Un chatbot empresarial se conecta a múltiples bases de datos de una organización para que los usuarios analicen datos por chat.
- Un modelo de IA crea diseños 3D en Blender y los manda a imprimir.

**¿Por qué importa, según a quién beneficia?**
| Rol | Beneficio |
|---|---|
| **Desarrolladores** | Reduce tiempo de desarrollo y complejidad al crear/integrar una app o agente de IA. |
| **Aplicaciones o agentes de IA** | Acceso a un ecosistema de fuentes de datos, herramientas y aplicaciones que mejora sus capacidades. |
| **Usuarios finales** | Agentes más capaces, que acceden a sus datos y actúan en su nombre cuando hace falta. |

---

## 3. Conceptos fundamentales y arquitectura

### 3.1 Los tres participantes

| Rol | Qué es |
|---|---|
| **MCP Host** | Aplicación de IA que coordina **múltiples** clientes MCP (ej. Claude Desktop, VS Code). |
| **MCP Client** | Mantiene una conexión **uno-a-uno** con un servidor MCP y gestiona el intercambio de contexto. |
| **MCP Server** | Provee contexto (herramientas, recursos, prompts) a los clientes MCP. |

**Relación cliente-servidor:** cada cliente MCP se conecta a un único servidor MCP. Los servidores pueden ser **locales** (**STDIO** — *Standard Input/Output*, entrada/salida estándar: el host lanza el servidor como proceso hijo y le habla por sus canales de entrada/salida) o **remotos** (**HTTP Streamable**).

**Ejemplo del material:** VS Code (host) se conecta a Sentry (servidor remoto) y a Filesystem (servidor local) — creando **un cliente MCP por cada servidor**, no uno compartido.

El diagrama de la diapositiva 11 lo deja explícito: dentro de un mismo **MCP Host**, hay 3 **MCP Client** distintos, cada uno con su propia conexión "one-to-one" hacia su propio **MCP Server** (Sentry / Filesystem / Database). Un host con *n* servidores conectados mantiene *n* clientes, no un cliente que hable con todos.

### 3.2 Las dos capas de MCP

MCP se define en dos capas independientes (diapositiva 12):

| Capa | Qué define |
|---|---|
| **Capa de datos** (*Data Layer*) | Basada en **JSON-RPC 2.0** (*JSON Remote Procedure Call*, protocolo ligero para invocar funciones remotas codificando la petición/respuesta en JSON). Define el protocolo de intercambio, la gestión del ciclo de vida de la conexión y las primitivas principales (herramientas, recursos, prompts, notificaciones). |
| **Capa de transporte** (*Transport Layer*) | Gestiona la conexión, autenticación y el canal de comunicación físico (STDIO o HTTP). |

*Conceptualmente: la capa de datos es la capa interna (el "qué se dice"); la capa de transporte es la capa externa (el "por dónde se dice").* Esta separación es la misma razón por la que un mismo servidor MCP puede exponerse tanto por STDIO (para un cliente local como Claude Desktop) como por HTTP (para un cliente remoto) sin cambiar ni una línea de las tools que expone — solo cambia el transporte.

### 3.3 Primitivas del servidor y del cliente

**Primitivas del servidor** (lo que el servidor *ofrece*):
- **Tools** — funciones ejecutables (ej. consultas, operaciones de archivo).
- **Resources** — datos contextuales (ej. contenido de archivos, registros).
- **Prompts** — plantillas reutilizables para interacción con LLMs.

**Primitivas del cliente** (lo que el cliente *puede pedirle al host*):
- **Sampling** — solicita completaciones del modelo del host.
- **Elicitation** — solicita input adicional del usuario.
- **Logging** — envía logs al cliente para monitoreo.
- **Notificaciones en tiempo real** — permiten actualizaciones dinámicas (ej. `tools/list_changed`) sin necesidad de *polling*.

Cada tipo de primitiva tiene métodos asociados para descubrimiento (`*/list`), recuperación (`*/get`) y, en algunos casos, ejecución (`tools/call`). Un cliente puede, por ejemplo, listar todas las herramientas disponibles (`tools/list`) y luego ejecutarlas — este diseño permite que los listados sean **dinámicos**: un servidor puede agregar o quitar tools en caliente y notificarlo, sin que el cliente tenga el catálogo *hardcodeado*.

### 3.4 Las cuatro combinaciones de "Functionality and Problem Solving" (diapositiva 17)

El material resume el valor de MCP en un cuadrante 2×2:

| | Perspectiva del *protocolo* | Perspectiva del *agente* |
|---|---|---|
| **Metáfora / estandarización** | **USB-C metaphor for AI connectivity** — conectividad universal para herramientas de IA. | **AI agent invoking tools** — el agente descubre e invoca tools dinámicamente, en tiempo de ejecución. |
| **Datos** | **Structured data provision** — provisión de datos estructurados, asegura que la IA tenga el contexto necesario. | **AI agent querying server capabilities** — el agente consulta las capacidades del servidor para obtener contexto dinámico. |

La lectura de conjunto: MCP no es solo "un protocolo más estandarizado" — es estandarización **más** *discoverability* en tiempo real, que es justo lo que una API tradicional no ofrece (ver §4).

---

## 4. MCP vs APIs tradicionales

### 4.1 El iceberg — qué falla en integrar agentes vía API "a mano" (diapositiva 19)

El material usa un iceberg: por encima de la línea de flotación, la limitación visible es **"API Limitations for AI"**; debajo, cuatro causas raíz:
- **Lack of Discovery** — el agente no puede preguntarle a la API qué operaciones existen; alguien tiene que documentarlo y mantenerlo sincronizado a mano.
- **No Standardization** — cada API tiene su propio esquema de auth, de errores, de paginación — no hay un contrato común entre integraciones.
- **Static Integration** — el código de integración asume una forma fija de la API; si la API cambia, la integración se rompe.
- **Historical Context** — el contexto (rol, historial, metas) vive fuera del protocolo, hay que cargarlo aparte en cada llamada.

### 4.2 Tabla comparativa completa (diapositiva 18)

| Dimensión | API Tradicionales | MCP (Model Context Protocol) |
|---|---|---|
| **Nivel de abstracción** | Bajo: expone funciones específicas, requiere lógica externa | Alto: encapsula intenciones, contexto y roles en un solo paquete |
| **Modelo mental** | Procedural: invoca funciones con parámetros | Declarativo: define objetivos, contexto y comportamiento esperado |
| **Contextualización** | Limitada: el contexto se gestiona fuera del API | Integrada: el contexto es parte del protocolo, incluyendo rol, historial y metas |
| **Interoperabilidad** | Fragmentada: cada API tiene su propio contrato | Uniforme: MCP define un estándar común para múltiples modelos y agentes |
| **Extensibilidad** | Requiere nuevas rutas o *endpoints* | Se extiende mediante nuevos roles, contextos o intenciones sin cambiar la estructura base |
| **Multi-role agent support** | No nativo: se simula con múltiples llamadas o servicios | Nativo: permite definir múltiples roles y relaciones entre agentes |
| **Auditabilidad / Trazabilidad** | Implícita: depende del sistema que consume el API | Explícita: cada mensaje MCP puede ser trazado, versionado y validado |
| **Token efficiency / cost** | Variable: depende del diseño del API y redundancia de llamadas | Optimizado: reduce redundancia al encapsular contexto y metas en una sola interacción |
| **Error handling / fallback** | Manual: requiere lógica de control en el cliente | Protocolar: puede incluir *fallback roles*, intenciones alternativas o validaciones internas |
| **Propuesta para agentes** | APIs son herramientas, no entidades inteligentes | MCP trata cada interacción como una unidad semántica entre agentes con roles definidos |

**Lectura crítica de esta tabla (no solo repetirla):** varias filas describen lo que MCP *permite* que un servidor haga (auditabilidad explícita, *fallback roles*, eficiencia de tokens), no algo que el protocolo garantice por sí solo — un `FastMCP` server mal diseñado puede seguir siendo tan opaco y frágil como una API mal documentada. Lo que MCP fija es el **contrato de transporte y descubrimiento** (JSON-RPC, `tools/list`, esquemas tipados); la calidad de la contextualización y el manejo de errores sigue dependiendo de quien implementa el servidor — el mismo punto que ya hizo Chip Huyen sobre el número de herramientas en la Sesión 15 (§7 de ese análisis): el protocolo no salva a un mal diseño de tools.

### 4.3 Function Calling clásico vs MCP — el mismo flujo, dos arquitecturas (diapositiva 21, *by DailyDoseofDS*)

El material trae un diagrama comparativo directo entre **Function Calling** (el patrón que ya se usa en LangChain con `@tool`, Sesiones 12-15) y **MCP**:

**Function Calling** (6 pasos):
```
Usuario → Query → LLM (con Function definitions ya cargadas)
LLM prepara la function call → Function call → invoca la tool/API directamente
API/Tool responde → Tool Output → se pasa como prompt al LLM → LLM genera la respuesta final
```

**MCP** (9 pasos — más participantes, no más pasos "de más"):
```
Usuario → Query → MCP Client (dentro del MCP Host, ej. Claude)
El LLM (dentro del Host) selecciona qué MCP tool usar → el MCP Client la propone
Usuario aprueba el uso de la tool ("MCP Tool approval")   ← paso que Function Calling NO tiene
MCP Client → Request tool call → MCP Server
MCP Server invoca la tool real (MCP Tool / API) → Tool Output
MCP Server devuelve el output → MCP Client lo entrega al LLM
LLM genera la respuesta final
```

**La diferencia que importa, más allá del diagrama:** en *Function Calling* clásico, las definiciones de las funciones viven **hardcodeadas** en el proceso del agente (el mismo patrón `@tool` de `agente.py` en `Tarea_Agente_Personal` / `AgentePersonal-Web`) — el LLM invoca directo, sin intermediarios ni aprobación explícita del usuario. En MCP hay un **servidor separado** de por medio, y el diagrama incluye un paso que Function Calling no tiene: **"MCP Tool approval"** — el usuario aprueba explícitamente antes de que la tool se ejecute. Esto no es un detalle menor: es la misma preocupación de seguridad que ya se documentó para `AgentePersonal-Web` — la decisión de que editar/eliminar un evento de Google Calendar **nunca** sea una tool que el LLM invoque libremente, sino una acción gatillada por un clic explícito del usuario con modal de confirmación (ver `CLAUDE.md` de ese proyecto) — es, en esencia, un "aprovechamiento" manual del mismo patrón de aprobación que MCP formaliza como parte del protocolo.

---

## 5. MCP Authentication

Las diapositivas 22-23 muestran un ejemplo real con **FastMCP** (el framework usado en todo el código de esta sesión — ver §6) integrando **Auth0** como proveedor de identidad vía **OIDC** (*OpenID Connect*, capa de autenticación construida sobre OAuth 2.0 que añade verificación de identidad):

**Servidor protegido (`server.py`, del material):**
```python
from fastmcp import FastMCP
from fastmcp.server.auth.providers.auth0 import Auth0Provider

auth_provider = Auth0Provider(
    config_url="https://.../.well-known/openid-configuration",
    client_id="...",
    client_secret="...",
    audience="https://...",
    base_url="http://localhost:8000",
)

mcp = FastMCP(name="Auth0 Secured App", auth=auth_provider)

@mcp.tool
async def get_token_info() -> dict:
    """Returns information about the Auth0 token."""
    from fastmcp.server.dependencies import get_access_token
    token = get_access_token()
    return {
        "issuer": token.claims.get("iss"),
        "audience": token.claims.get("aud"),
        "scope": token.claims.get("scope"),
    }
```

**Cliente (`test_client.py`, del material):**
```python
from fastmcp import Client
import asyncio

async def main():
    async with Client("http://localhost:8000/mcp", auth="oauth") as client:
        # La primera conexión abre el login de Auth0 en el navegador
        print("✓ Authenticated with Auth0!")
        result = await client.call_tool("get_token_info")
        print(f"Auth0 audience: {result['audience']}")

if __name__ == "__main__":
    asyncio.run(main())
```

**El punto clave:** con FastMCP, la autenticación no se implementa a mano tool por tool — se declara **una vez** al crear el servidor (`auth=auth_provider`), y el cliente simplemente pide `auth="oauth"` sin manejar el flujo OAuth manualmente (FastMCP lo abre en el navegador la primera vez). El material muestra el listado de proveedores ya soportados out-of-the-box por FastMCP (documentación oficial): **Auth0, AuthKit, AWS Cognito, Azure (Entra ID), Descope, GitHub, Scalekit, Google, WorkOS** (autenticación), y **Eunomia Auth, Permit.io** (autorización — separando "quién eres" de "qué puedes hacer"). Esto es exactamente el mismo problema de *token exchange* delegado que ya apareció en la Sesión 15 con el proyecto *Assistant0* (§3.1 de ese análisis) — aquí, en vez de reconstruirlo a mano con Auth0 directo, FastMCP lo da como una integración de una línea.

---

## 6. El código real de la sesión (`agents26_m6s16-main/`)

A diferencia de sesiones anteriores (solo diapositivas), esta trae una carpeta de ejemplos reales en **FastMCP** — la implementación open-source más usada para construir servidores MCP en Python sin escribir el protocolo JSON-RPC a mano — más un notebook que sí lo hace a mano, para contraste.

### 6.1 `sample.py` — el servidor MCP mínimo posible

```python
from fastmcp import FastMCP

mcp = FastMCP("Weather Service 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

Tres líneas de verdad: crear el servidor, decorar una función con `@mcp.tool`, correrlo. FastMCP infiere el **esquema JSON** de entrada/salida directamente de los *type hints* de Python (`a: int, b: int -> int`) — no hay que escribir el JSON Schema a mano, a diferencia del ejemplo de bajo nivel del notebook (§6.5).

### 6.2 `split/simpleserver.py` + `split/simpleclient.py` — transporte HTTP real, cliente y servidor separados

```python
# simpleserver.py
mcp = FastMCP("My MCP Server")

@mcp.tool()
def SaludoFeliz(name: str) -> str:
    """Responde de una forma amistosa con un saludo"""
    return f"hola!!! como estas {name}? :D"

@mcp.tool()
def SaludoMolesto(name: str) -> str: ...   # variante "molesta"

@mcp.tool()
def SaludoTriste(name: str) -> str: ...    # variante "triste/cansada"

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
```
```python
# simpleclient.py
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("SaludoFeliz", {"name": name})
        print(result.content)

asyncio.run(call_tool("Juan"))
```

Este par de archivos es el ejemplo pedagógicamente más importante de la carpeta: demuestra que servidor y cliente son **procesos completamente independientes** (uno corre en `:8000` vía HTTP, el otro se conecta como cualquier cliente HTTP) — a diferencia de `sample.py`, que corre por STDIO dentro del mismo proceso que lo invoca (ej. Claude Desktop lanzándolo como subproceso). Las tres variantes de saludo (feliz/molesta/triste) con el **mismo nombre de parámetro** (`name`) son un ejercicio de *tool discovery*: un cliente que liste las tools del servidor (`tools/list`) recibe 3 nombres distintos con la misma firma, y tiene que decidir cuál invocar por su **descripción** (el *docstring*), no por su forma — el mismo mecanismo de selección de tool que un agente LLM usa en producción.

### 6.3 `mcpdesktop.py` — conectar un servidor MCP a Claude Desktop, con Tools + Resource + Prompt combinados

```python
# Para agregar el MCP Server a Claude Desktop:
# uv run mcp install mcpdesktop.py   (y reiniciar Claude App)

mcp = FastMCP("NotasIA")

@mcp.tool()
def add_note(message: str) -> str:
    """Append a new note to the sticky note file."""
    ...
    return "Nota guardada!"

@mcp.tool()
def read_note() -> str:
    """Read and return all the notes from the sticky note file."""
    ...

@mcp.resource("notes://latest")
def get_latest_note() -> str:
    """Read the latest note from the sticky note file."""
    ...

@mcp.prompt()
def note_summary_prompt() -> str:
    """Generate a prompt asking the AI to summarize all the notes"""
    ...
```

Este archivo es el único de la carpeta que usa las **tres primitivas de servidor a la vez** (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt` — ver §3.3) sobre un caso de uso real y simple: notas persistidas en un `.txt` local. También trae el comando exacto para registrar un servidor MCP propio en **Claude Desktop** vía **uv** (gestor de paquetes y entornos Python de Astral, mucho más rápido que `pip`/`venv` — ver `docs.astral.sh/uv` en Referencias): `uv run mcp install mcpdesktop.py`.

> **Dos bugs reales encontrados al leer este archivo** (no están en el PDF, son del código de ejemplo):
> 1. `get_latest_note()` hace `lines = f.readlines` (le falta `()`) — así `lines` queda apuntando al **método** `readlines`, no a la lista de líneas; `lines[-1]` fallaría con `TypeError` porque un método no soporta indexado. Debería ser `f.readlines()`.
> 2. `note_summary_prompt()` hace `return f"Summarize current notes: "+{content}` — intenta sumar un `str` con un `set` literal (`{content}` son llaves de conjunto, no de f-string), lo que lanza `TypeError: can only concatenate str (not "set") to str`. La forma correcta sería `f"Summarize current notes: {content}"` (interpolación) o `"Summarize current notes: " + content` (concatenación simple, sin llaves).
>
> Ninguna de las dos rutas se prueba en el resto del material — son el tipo de error que solo aparece al **ejecutar** la tool/resource/prompt real, no al leerlo por encima. Vale la pena tenerlo presente para la Tarea (§8): si se construye un MCP server propio, probarlo de verdad con un cliente (como `simpleclient.py`) antes de darlo por bueno, exactamente la misma disciplina de "no aceptar código sin probarlo" que ya está documentada en las declaraciones de transparencia de IA de `Tarea_Agente_Personal`.

### 6.4 `allinone.py` — *structured output* con FastMCP, y cómo probar tools sin levantar un servidor real

Este archivo no enseña MCP básico — enseña algo más avanzado: cómo hacer que una tool devuelva **datos tipados y validados**, no solo texto suelto, usando distintas formas de tipar el retorno:

| Técnica de tipado | Ejemplo en el archivo |
|---|---|
| **Modelo Pydantic** | `WeatherData(BaseModel)` con `Field(description=...)` por campo — genera un JSON Schema rico, con descripciones por campo. |
| **`TypedDict`** | `WeatherSummary` — estructura más simple, sin validación en tiempo de ejecución. |
| **`dict[str, dict[str, float]]`** | `get_weather_metrics` — esquema flexible/anidado sin clase dedicada. |
| **`dataclass`** | `WeatherAlert`, devuelto como `list[WeatherAlert]` — útil cuando no se necesita la validación de Pydantic. |
| **Primitivo (`float`)** | `get_temperature` — el material aclara que, al devolver un primitivo como *structured output*, el resultado se envuelve automáticamente en `{"result": value}`. |
| **Modelos anidados** | `WeatherStats` contiene dos `DailyStats` (uno para temperatura, otro para humedad) — Pydantic anidado dentro de Pydantic. |

**El patrón más reutilizable del archivo** es este, en el bloque `if __name__ == "__main__"`:

```python
from mcp.shared.memory import create_connected_server_and_client_session as client_session

async with client_session(mcp._mcp_server) as client:
    result = await client.call_tool("get_weather", {"city": "London"})
    print(json.dumps(result.structuredContent, indent=2))
```

Esto crea un **cliente y servidor MCP conectados en memoria**, sin abrir ningún puerto ni proceso — permite probar las tools de un servidor FastMCP como si fueran funciones normales, en un test automatizado. También expone `mcp.list_tools()` para imprimir el `inputSchema`/`outputSchema` de cada tool tal como los vería un cliente real (`--schemas` como argumento de línea de comandos) — útil para depurar por qué un agente no está "viendo" bien una tool: el problema casi siempre está en un schema mal inferido, y este patrón lo hace visible sin necesidad de conectar un LLM real.

### 6.5 `Anthropic_Tutorial.ipynb` — el mismo problema, resuelto sin FastMCP (SDK de bajo nivel)

Este notebook (30 celdas) es el contraste deliberado frente a todo lo anterior: en vez de `fastmcp`, usa el **SDK oficial de MCP de bajo nivel** (`mcp.server.Server`, `mcp.types.Tool/Resource/Prompt`) — lo que FastMCP hace con un decorador, aquí se construye a mano. Estructura declarada en sus propias secciones:

| Parte | Contenido |
|---|---|
| 1 | Configuración e imports (verificación de versiones instaladas de `mcp`, `anthropic`, `langchain`) |
| 2 | Sistema de autenticación — `AuthenticationMethod` (`NONE`, `API_KEY`, `BEARER_TOKEN`, `HMAC_SHA256`, `OAUTH2`) y una clase `Authenticator` construida a mano |
| 3 | Tools — un `ToolRegistry` propio, con registro vía decorador, *sync*/*async*, y auth por tool |
| 4 | Resources — recursos estáticos y *templates* dinámicos con *URI template matching* |
| 5 | Prompts — plantillas reutilizables con argumentos |
| 6 | `MCPServerCore` — clase integradora que junta tools + resources + prompts + auth + estadísticas (`tools_called`, `auth_failures`, etc.) en un único servidor |
| 7 | Logging avanzado — formateador con colores ANSI, `RequestMetricsCollector` |
| 8 | Integración con LangChain + Anthropic — tools de LangChain (`@tool` de `langchain_core.tools`) enlazadas a `ChatAnthropic`, mismo patrón `@tool` de las Sesiones 12-15, mostrando que un MCP server y un agente LangChain pueden convivir |
| 9 | Resumen final + *checklist* de producción |

**Por qué vale la pena leer este notebook aunque el resto de la sesión use FastMCP:** muestra **qué hace FastMCP por debajo** — un registro de tools con *schemas*, gestión de auth con expiración de credenciales, *rate limiting*, notificaciones — todo lo que en `sample.py` o `mcpdesktop.py` desaparece detrás de un decorador. Es la misma relación que hay entre usar LangGraph (Sesión 15) y construir el bucle ReAct a mano: entender la versión manual ayuda a saber **qué se está delegando** al framework, y cuándo ese framework no alcanza (ej. si se necesita HMAC-SHA256 o *rate limiting* fino, FastMCP puede no cubrirlo out-of-the-box y hay que caer a este nivel).

El propio *checklist* de producción del notebook (celda final) es honesto sobre lo que falta incluso después de todo ese código: persistencia en base de datos, cifrado, HTTPS/TLS, *rate limiting* más sofisticado, *caching* distribuido (Redis), *circuit breakers*, *tracing* distribuido (Jaeger), logs centralizados, *healthchecks*, métricas (Prometheus), tests automatizados, CI/CD. Es un recordatorio de que "funciona en el notebook" y "listo para producción" son cosas muy distintas — el mismo tipo de honestidad que ya aparece en el `CLAUDE.md` de `AgentePersonal-Web` sobre lo que falta probar de verdad.

---

## 7. Lab y Tarea de la sesión

| Actividad | Instrucción |
|---|---|
| **Lab — Aterrizando a proyectos** (diapositiva 15) | Reflexión sobre el proyecto propio: ¿se puede usar un MCP Server de algún proveedor ya existente? ¿conviene implementar un servidor propio? *Check:* usar draw.io (u otra herramienta) para plasmarlo en un diagrama. |
| **Tarea PERSONAL — MCP** (diapositiva 25) | Probar con Claude un **MCP Server personal, de autoría propia**, que ayude en el día a día. Entregable: definición del MCP Server en Python + *screenshots* de Claude o de la terminal de Python + PDF. **Fecha límite: 15/08.** |

**Notas operativas del `link_clase.txt` de esta sesión** (no están en el PDF):
- El profesor recomienda explícitamente usar **MCP 2.0** para la tarea.
- Enlaces de referencia entregados: el anuncio oficial de Anthropic sobre MCP, el `github.com/modelcontextprotocol` (organización con las implementaciones de referencia), la documentación de **uv** (`docs.astral.sh/uv`), la documentación de arquitectura de `modelcontextprotocol.io` (versión `2026-07-28`), el repositorio `microsoft/mcp-gateway`, y la certificación *Claude Certified Architect Foundations* (Anthropic, vía Skilljar).

---

## 8. Aplicación al proyecto propio (`AgentePersonal-Web`)

Esta sección conecta la sesión con el proyecto que el estudiante mantiene activamente fuera del repo del curso (`D:\APRENDIZAJE\PROYECTOS\AgentePersonal-Web`), siguiendo la misma lógica que la Sesión 15 aplicó a `Tarea_Agente_Personal` (§3.1 y checklist de ese análisis).

`AgentePersonal-Web` ya tiene tools bien delimitadas — Calendar (Google Calendar API), RAG sobre materiales (Chroma), CRUD de actividades (MySQL) — corriendo **in-process** dentro del mismo backend FastAPI, invocadas por un agente LangChain (`create_agent`, patrón ReAct de las Sesiones 12-15). Dos caminos posibles, sin que ninguno sea obligatorio hoy:

1. **Consumir un MCP Server de un proveedor** en vez de mantener la integración propia con `googleapiclient` — por ejemplo, un servidor MCP de Calendar ya existente, con su propia gestión de auth (§5) y *discovery* de tools.
2. **Exponer las tools propias como un MCP Server** (con FastMCP, siguiendo el patrón de §6.1-6.3) para que otros clientes MCP (Claude Desktop, Claude Code) las reutilicen — no solo el chat React de la app.

**El trade-off, explicado en la sesión sin nombrarlo así:** hoy las tools corren sin la capa de protocolo adicional (sin *transporte* separado, sin *discovery* dinámico, sin aprobación explícita por tool — ver §4.3); pasar a MCP agrega justamente eso, a cambio de un proceso/servidor adicional que mantener. Para un solo cliente (el chat propio de la app) no es necesario — es una mejora de **reusabilidad e interoperabilidad**, exactamente las dos filas de la tabla de §4.2 donde MCP le gana claramente a una integración directa. Vale la pena, en cambio, como base concreta para la Tarea de esta sesión (§7): un MCP Server pequeño y personal (ej. envolver `consultar_calendario` o `buscar_en_documentos` de `agente.py` como tools de un `FastMCP`) es un ejercicio directo, acotado, y reutiliza lógica que ya existe y ya está probada.

---

## 9. Síntesis — lo que hay que llevarse de esta sesión

1. **MCP no reemplaza el *function calling*** que ya se usa en LangChain (`@tool`) — le agrega alrededor un protocolo estandarizado de transporte (JSON-RPC sobre STDIO/HTTP), *discovery* dinámico de tools, y un paso explícito de aprobación del usuario que el *function calling* directo no tiene (§4.3).
2. **La arquitectura tiene tres roles fijos** (Host, Client, Server) con una relación de conexión **uno-a-uno** por servidor — un host con *n* servidores mantiene *n* clientes, no uno solo (§3.1).
3. **Dos capas independientes**: datos (JSON-RPC, primitivas) y transporte (STDIO/HTTP, auth) — se pueden combinar (mismo servidor por dos transportes distintos) sin tocar la lógica de las tools (§3.2).
4. **Seis primitivas en total**, tres del servidor (Tools/Resources/Prompts) y tres+ del cliente (Sampling/Elicitation/Logging/Notificaciones) — cada una resuelve un problema distinto de contexto compartido (§3.3).
5. **MCP resuelve específicamente lo que una integración API ad-hoc no resuelve bien**: *discovery*, estandarización, adaptabilidad a cambios, contexto integrado — no es solo "una API con otro nombre" (§4.1-4.2), aunque la calidad real depende de cómo se implemente el servidor, no solo de usar el protocolo.
6. **FastMCP** es, en la práctica de esta sesión, la forma de facto de construir un servidor MCP en Python — decoradores simples (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt`) que generan JSON Schema automáticamente desde *type hints*, más *auth providers* ya integrados (Auth0, Google, GitHub, etc.) sin implementar OAuth a mano (§5, §6).
7. **El SDK de bajo nivel existe y se usa cuando FastMCP no alcanza** (auth custom tipo HMAC, *rate limiting* fino, registries propios) — entenderlo ayuda a saber qué está haciendo FastMCP por debajo (§6.5).
8. **Probar el código antes de confiar en él sigue siendo la regla**: dos bugs reales aparecieron en el material de ejemplo (`mcpdesktop.py`, §6.3) con solo leer el código con atención — ninguno se habría visto sin ejecutarlo o revisarlo línea por línea.

---

## 10. Checklist práctico — decidiendo si (y cómo) usar MCP

- [ ] ¿El agente necesita que **más de un cliente** (no solo tu propio chat) reutilice las mismas tools? Si es solo tu app, MCP es una mejora de arquitectura, no una necesidad.
- [ ] ¿Alguna de las tools puede tener consecuencias reales e irreversibles (borrar, modificar, enviar)? Si sí, replica el paso de **"tool approval"** de MCP (§4.3) aunque no uses MCP — aprobación explícita del usuario antes de ejecutar, nunca automática por el LLM.
- [ ] ¿Ya existe un MCP Server de un proveedor para el sistema externo que necesitas (Calendar, Slack, GitHub, Filesystem...)? Revisa antes de escribir el tuyo — reduce superficie de mantenimiento.
- [ ] Si construyes tu propio servidor: ¿usas **FastMCP** (rápido, decoradores, *auth providers* ya hechos) o necesitas el **SDK de bajo nivel** (control fino de auth/registro/logging)?
- [ ] ¿El servidor va a correr **local** (STDIO, ej. un servidor personal para Claude Desktop) o **remoto** (HTTP, con auth real de por medio)? Cambia si necesitas un `auth_provider` o no.
- [ ] ¿Los tipos de retorno de tus tools están bien tipados (Pydantic/`TypedDict`/`dataclass`, ver §6.4)? Un esquema de salida pobre es tan malo para un agente como una tool sin *docstring*.
- [ ] ¿Probaste las tools de verdad, con un cliente conectado (real o en memoria, ver `client_session` de §6.4) — no solo leyendo el código?

---

## 11. Referencias

**Del material original:**
- Diagramas propios del curso — participantes MCP, capas de datos/transporte, ecosistema USB-C, cuadrante *Functionality and Problem Solving*, iceberg de limitaciones de API, tabla comparativa API vs MCP, autenticación con FastMCP + Auth0.
- Diagrama *"Function Calling & MCP for AI Agents"* — atribuido a **DailyDoseofDS** (`join.DailyDoseofDS.com`) en el propio material.
- **FastMCP** — documentación oficial, sección de proveedores de autenticación (Auth0, AuthKit, AWS Cognito, Azure Entra ID, Descope, GitHub, Scalekit, Google, WorkOS) y autorización (Eunomia Auth, Permit.io).

**Del `link_clase.txt` de esta sesión:**
- Anthropic — anuncio oficial de Model Context Protocol: [anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol)
- Organización oficial con las implementaciones de referencia: [github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)
- **uv** (gestor de paquetes/entornos Python de Astral) — interfaz compatible con `pip`: [docs.astral.sh/uv/getting-started/features/#the-pip-interface](https://docs.astral.sh/uv/getting-started/features/#the-pip-interface)
- Documentación de arquitectura de MCP (versión `2026-07-28`): [modelcontextprotocol.io/docs/2026-07-28/learn/architecture](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)
- Microsoft — `mcp-gateway`: [github.com/microsoft/mcp-gateway](https://github.com/microsoft/mcp-gateway)
- Certificación *Claude Certified Architect Foundations* (Anthropic, vía Skilljar).

**Código revisado de `agents26_m6s16-main/`:** `sample.py`, `split/simpleserver.py`, `split/simpleclient.py`, `mcpdesktop.py`, `allinone.py`, `Anthropic_Tutorial.ipynb`, `requirements.txt` (`mcp`, `fastmcp`, `mcp[cli]`).

**Arco interno del curso:** Sesión 14 (Infraestructura de Agentes) y Sesión 15 (LangGraph MultiAgent) — el patrón *tool approval* de MCP (§4.3) formaliza la misma precaución de seguridad ya documentada como decisión de arquitectura en `AgentePersonal-Web/CLAUDE.md` para editar/eliminar eventos de Google Calendar.

---

*Documento generado a partir del PDF de la Sesión 16 (Módulo 5, UTEC Posgrado) — texto extraído + diapositivas gráficas interpretadas visualmente — más revisión directa, archivo por archivo, del código de ejemplo en `agents26_m6s16-main/`.*
