# Agente Personal ReAct de Planificación Académica

## Objetivo

Implementar un agente personal basado en el patrón **ReAct** (*Reasoning
and Acting*) que priorice actividades académicas pendientes y consulte
los documentos asociados a cada una para apoyar su desarrollo, usando
LangChain.

## Necesidad personal

Durante el desarrollo de cursos, trabajos y proyectos se acumulan
actividades con distintas fechas límite y niveles de importancia.
Decidir a mano cuál atender primero, y encontrar dentro de qué documento
está un requisito puntual, consume tiempo que preferiría dedicar a
resolver la tarea en sí. El agente ayuda a decidir qué actividad hacer
primero, cómo distribuir el tiempo disponible entre las tareas
pendientes, y qué dicen los materiales de una tarea sin tener que abrir
cada archivo manualmente.

## Cómo funciona — dónde vive cada cosa

El agente se construye con `create_agent` de LangChain y ocho
herramientas. Antes de leer el código completo, esto orienta qué hace
cada pieza y dónde queda guardada:

| Qué | Dónde | Cómo se genera/actualiza |
|---|---|---|
| **Tareas registradas** | `tareas.json`, junto al script | Se cargan al inicio de cada operación y se reescriben con `agregar_tarea` (nueva tarea) o `actualizar_estado` (cambio de estado). No hay base de datos: es un archivo de texto plano, legible directamente. |
| **Materiales de consulta** | `materiales/<carpeta de la tarea>/` | Carpeta fija por tarea (campo `ruta_contexto` en `tareas.json`). El agente solo puede leer dentro de esta raíz — cualquier otra ruta se rechaza. |
| **Reportes de plan** | `planes_generados/` | Se generan de **dos formas distintas**, según lo que pida el usuario (ver abajo). |

**Los dos caminos para generar un reporte en `planes_generados/`:**

1. **`generar_plan(minutos_disponibles)`** — calcula desde cero, a partir
   de `tareas.json`, qué tareas caben en el tiempo disponible (ordenadas
   por un puntaje de urgencia: prioridad declarada + cercanía de la
   fecha límite) y guarda esa tabla como `PLAN-<fecha>.md`. Es un cálculo
   determinista, no una redacción libre del modelo.
2. **`guardar_plan_detallado(tarea_id, titulo, contenido)`** — guarda tal
   cual un texto que el agente ya redactó en la conversación (por
   ejemplo, un desglose paso a paso para completar una tarea puntual),
   como `PLAN-DETALLADO-<fecha>.md`. Existe como herramienta aparte
   porque `generar_plan` no puede persistir texto libre: solo sabe
   recalcular su propia tabla.

Ninguna de las dos se usa "porque sí": el *system prompt* del agente
(ver sección de código) indica explícitamente cuándo usar cada una, para
que el modelo no termine afirmando que guardó algo sin haber llamado a
ninguna herramienta real.

## Arquitectura — herramientas del agente

| Herramienta | Función |
|---|---|
| `consultar_tareas` | Lista las tareas registradas y su estado. |
| `agregar_tarea` | Registra una tarea nueva. |
| `calcular_prioridad` | Calcula el puntaje de urgencia de una tarea. |
| `generar_plan` | Arma y guarda el plan calculado desde `tareas.json`. |
| `actualizar_estado` | Cambia el estado de una tarea (pendiente/iniciada/completada). |
| `guardar_plan_detallado` | Guarda un plan de texto libre ya redactado en el chat. |
| `inspeccionar_carpeta` | Lista los documentos disponibles de una tarea. |
| `buscar_en_documentos` | Busca una consulta por palabra clave dentro de esos documentos (sin RAG ni embeddings). |

El modelo (Claude vía Anthropic, o Gemma 4 E4B vía LM Studio local,
intercambiable con una variable de entorno) decide en cada turno cuál de
estas herramientas invocar y en qué orden — ese ciclo de decisión →
acción → observación → siguiente decisión es el patrón ReAct aplicado.

## Ejemplo de uso

```
Tú: Tengo cuatro horas disponibles. Revisa mis tareas pendientes,
    dime cuál es más urgente y busca en sus materiales cuáles son
    los requisitos de entrega.

Acción: consultar_tareas          → 5 tareas pendientes
Acción: calcular_prioridad (c/u)  → "Implementar agente ReAct" es la más urgente
Acción: generar_plan(240)         → tabla guardada en planes_generados/
Acción: inspeccionar_carpeta      → 1 archivo encontrado (instrucciones.txt)
Acción: buscar_en_documentos      → línea con el entregable encontrada

Respuesta final: tarea priorizada, plan de tiempo y requisitos de entrega.
```

## Código completo

```python
"""
Agente personal de planificacion academica, construido con LangChain
(create_agent) siguiendo el patron ReAct: prioriza tareas pendientes
segun fecha limite y prioridad, arma un plan de tiempo y busca
contenido dentro de los documentos asociados a cada tarea.

Backends soportados via AGENT_MODEL (.env):
    AGENT_MODEL=anthropic       -> Claude via API de Anthropic
    AGENT_MODEL=gemma-lmstudio  -> Gemma 4 E4B via LM Studio (local)

Para correr el chat:
    python agente_planificacion_academica.py
"""

import json
import os
import unicodedata
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

RUTA_TAREAS = Path(__file__).parent / "tareas.json"
CARPETA_PLANES = Path(__file__).parent / "planes_generados"

# Nada se lee fuera de esta carpeta. Se puede apuntar a otra ubicacion
# con la variable de entorno CARPETA_AUTORIZADA.
CARPETA_AUTORIZADA = Path(
    os.getenv("CARPETA_AUTORIZADA", str(Path(__file__).parent / "materiales"))
).resolve()

EXTENSIONES_ADMITIDAS = {".pdf", ".docx", ".txt", ".md", ".py"}
PESO_PRIORIDAD = {"alta": 3, "media": 2, "baja": 1}


def _normalizar(texto: str) -> str:
    """Quita tildes y pasa a minusculas, para que la busqueda no dependa de como se escriba."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c)
    )
    return sin_tildes.strip()


def _cargar_tareas() -> list[dict]:
    if not RUTA_TAREAS.exists():
        return []
    return json.loads(RUTA_TAREAS.read_text(encoding="utf-8"))


def _guardar_tareas(tareas: list[dict]) -> None:
    RUTA_TAREAS.write_text(json.dumps(tareas, ensure_ascii=False, indent=2), encoding="utf-8")


def _buscar_tarea(tarea_id: int) -> dict | None:
    return next((t for t in _cargar_tareas() if t["id"] == tarea_id), None)


def _validar_ruta(ruta: str) -> Path | None:
    ruta_resuelta = (Path(__file__).parent / ruta).resolve() if not Path(ruta).is_absolute() else Path(ruta).resolve()
    if ruta_resuelta == CARPETA_AUTORIZADA or CARPETA_AUTORIZADA in ruta_resuelta.parents:
        return ruta_resuelta
    return None


def _puntaje_urgencia(tarea: dict) -> float:
    # peso * 100 / (dias restantes + 1): a mayor prioridad y menos tiempo
    # restante, mayor el puntaje.
    dias_restantes = max((date.fromisoformat(tarea["fecha_limite"]) - date.today()).days, 0)
    peso = PESO_PRIORIDAD.get(tarea["prioridad"], 1)
    return peso * 100 / (dias_restantes + 1)


@tool
def consultar_tareas() -> str:
    """Devuelve todas las tareas registradas, con su estado actual."""
    tareas = _cargar_tareas()
    if not tareas:
        return "No hay tareas registradas."
    return "\n".join(
        f"[{t['id']}] {t['nombre']} — curso: {t['curso']} — vence: {t['fecha_limite']} "
        f"— prioridad: {t['prioridad']} — estado: {t['estado']}"
        for t in tareas
    )


@tool
def agregar_tarea(
    nombre: str, curso: str, fecha_limite: str, duracion_minutos: int,
    prioridad: str, ruta_contexto: str = "", entregable: str = "",
) -> str:
    """
    Registra una tarea nueva. fecha_limite en formato YYYY-MM-DD,
    prioridad 'alta', 'media' o 'baja'. Si falta algun dato pideselo al
    usuario en vez de inventarlo.
    """
    tareas = _cargar_tareas()
    nuevo_id = max((t["id"] for t in tareas), default=0) + 1
    tareas.append({
        "id": nuevo_id, "nombre": nombre, "curso": curso, "fecha_limite": fecha_limite,
        "duracion_estimada_minutos": duracion_minutos, "prioridad": prioridad,
        "estado": "pendiente", "ruta_contexto": ruta_contexto, "entregable": entregable,
    })
    _guardar_tareas(tareas)
    return f"Tarea '{nombre}' registrada con id {nuevo_id}."


@tool
def calcular_prioridad(tarea_id: int) -> str:
    """Calcula el puntaje de urgencia de una tarea. Usala antes de decidir cual atender primero."""
    tarea = _buscar_tarea(tarea_id)
    if tarea is None:
        return f"No existe una tarea con id {tarea_id}."
    dias_restantes = max((date.fromisoformat(tarea["fecha_limite"]) - date.today()).days, 0)
    return (
        f"Tarea {tarea_id} ({tarea['nombre']}): puntaje de urgencia "
        f"{_puntaje_urgencia(tarea):.1f} (prioridad={tarea['prioridad']}, vence en {dias_restantes} dia(s))."
    )


@tool
def generar_plan(minutos_disponibles: int) -> str:
    """
    Arma un plan con las tareas pendientes, de mayor a menor urgencia,
    con 10 minutos de descanso entre cada una, y lo guarda como .md en
    planes_generados/. Usala despues de calcular_prioridad.
    """
    pendientes = sorted(
        (t for t in _cargar_tareas() if t["estado"] != "completada"),
        key=_puntaje_urgencia, reverse=True,
    )

    filas: list[str] = []
    minutos_usados = 0
    for tarea in pendientes:
        duracion = tarea["duracion_estimada_minutos"]
        if minutos_usados + duracion > minutos_disponibles:
            continue
        filas.append(f"| {tarea['nombre']} | {duracion} min | {tarea['prioridad']} |")
        minutos_usados += duracion
        if minutos_usados < minutos_disponibles:
            minutos_usados += 10

    if not filas:
        return "No hay tiempo suficiente para ninguna tarea pendiente con el tiempo disponible."

    fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    codigo_plan = f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    contenido_md = f"""# Plan academico

**Código:** {codigo_plan}
**Fecha de generación:** {fecha_generacion}
**Tiempo disponible:** {minutos_disponibles} min (usados: {minutos_usados} min, incluye descansos de 10 min entre tareas)

## Bloques

| Tarea | Duración | Prioridad |
|---|---|---|
{chr(10).join(filas)}
"""

    try:
        CARPETA_PLANES.mkdir(exist_ok=True)
        archivo_plan = CARPETA_PLANES / f"{codigo_plan}.md"
        archivo_plan.write_text(contenido_md, encoding="utf-8")
    except OSError as error:
        return f"No se pudo guardar el plan: {error}"

    return (
        f"Plan {codigo_plan} generado con {len(filas)} tarea(s), "
        f"{minutos_usados} de {minutos_disponibles} minutos usados. "
        f"Reporte guardado en {archivo_plan}."
    )


@tool
def actualizar_estado(tarea_id: int, nuevo_estado: str) -> str:
    """Cambia el estado de una tarea a 'pendiente', 'iniciada' o 'completada'."""
    if nuevo_estado not in {"pendiente", "iniciada", "completada"}:
        return f"Estado '{nuevo_estado}' invalido. Usa: pendiente, iniciada o completada."
    tareas = _cargar_tareas()
    for t in tareas:
        if t["id"] == tarea_id:
            t["estado"] = nuevo_estado
            _guardar_tareas(tareas)
            return f"Tarea {tarea_id} actualizada a estado '{nuevo_estado}'."
    return f"No existe una tarea con id {tarea_id}."


@tool
def guardar_plan_detallado(tarea_id: int, titulo: str, contenido_markdown: str) -> str:
    """
    Guarda en planes_generados/ un plan que ya escribiste en el chat
    (por ejemplo un desglose por fases), tal cual, sin recalcular nada.
    Usala cuando el usuario pida guardar o exportar algo que ya
    redactaste — generar_plan no sirve para esto porque arma su propia
    tabla desde tareas.json.
    """
    tarea = _buscar_tarea(tarea_id)
    if tarea is None:
        return f"No existe una tarea con id {tarea_id}."

    fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    codigo_plan = f"PLAN-DETALLADO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    contenido_final = (
        f"# {titulo}\n\n**Código:** {codigo_plan}\n"
        f"**Fecha de generación:** {fecha_generacion}\n**Tarea:** {tarea['nombre']}\n\n"
        f"---\n\n{contenido_markdown}"
    )

    try:
        CARPETA_PLANES.mkdir(exist_ok=True)
        archivo_plan = CARPETA_PLANES / f"{codigo_plan}.md"
        archivo_plan.write_text(contenido_final, encoding="utf-8")
    except OSError as error:
        return f"No se pudo guardar el plan: {error}"

    return f"Plan detallado guardado en {archivo_plan}."


@tool
def inspeccionar_carpeta(tarea_id: int) -> str:
    """
    Lista los archivos compatibles (PDF, DOCX, TXT, Markdown, Python) en
    la carpeta de materiales de una tarea, a partir de su id.
    """
    tarea = _buscar_tarea(tarea_id)
    if tarea is None:
        return f"No existe una tarea con id {tarea_id}."
    if not tarea.get("ruta_contexto"):
        return f"La tarea {tarea_id} no tiene materiales asociados."

    carpeta = _validar_ruta(tarea["ruta_contexto"])
    if carpeta is None:
        return f"La carpeta de materiales de la tarea {tarea_id} esta fuera de la carpeta autorizada."
    if not carpeta.is_dir():
        return f"La carpeta '{tarea['ruta_contexto']}' de la tarea {tarea_id} no existe."

    archivos = sorted(f.name for f in carpeta.iterdir() if f.suffix.lower() in EXTENSIONES_ADMITIDAS)
    if not archivos:
        return f"No se encontraron documentos compatibles en la carpeta de la tarea {tarea_id}."
    return f"Documentos encontrados para la tarea {tarea_id}: " + ", ".join(archivos)


def _extraer_texto_archivo(ruta: Path) -> str:
    sufijo = ruta.suffix.lower()
    if sufijo in {".txt", ".md", ".py"}:
        return ruta.read_text(encoding="utf-8", errors="ignore")
    if sufijo == ".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(ruta).paragraphs)
    if sufijo == ".pdf":
        from pypdf import PdfReader
        return "\n".join(pagina.extract_text() or "" for pagina in PdfReader(ruta).pages)
    return ""


@tool
def buscar_en_documentos(tarea_id: int, consulta: str) -> str:
    """
    Busca la consulta como texto dentro de los documentos de una tarea
    (coincidencia literal, sin embeddings ni vector store).
    """
    tarea = _buscar_tarea(tarea_id)
    if tarea is None:
        return f"No existe una tarea con id {tarea_id}."
    if not tarea.get("ruta_contexto"):
        return f"La tarea {tarea_id} no tiene materiales asociados."

    carpeta = _validar_ruta(tarea["ruta_contexto"])
    if carpeta is None or not carpeta.is_dir():
        return f"La carpeta de materiales de la tarea {tarea_id} no es valida."

    termino = _normalizar(consulta)
    coincidencias: list[str] = []
    for archivo in carpeta.iterdir():
        if archivo.suffix.lower() not in EXTENSIONES_ADMITIDAS:
            continue
        try:
            texto = _extraer_texto_archivo(archivo)
        except Exception:
            continue
        for linea in texto.splitlines():
            if termino in _normalizar(linea):
                coincidencias.append(f"[{archivo.name}] {linea.strip()}")

    if not coincidencias:
        return f"No se encontro '{consulta}' en los documentos de la tarea {tarea_id}."
    return "\n".join(coincidencias[:10])


def extraer_texto(contenido) -> str:
    # A veces el contenido de la respuesta es un string y a veces una
    # lista de bloques (por ejemplo con Claude y thinking activado).
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        textos = []
        for bloque in contenido:
            texto = bloque.get("text") if isinstance(bloque, dict) else getattr(bloque, "text", None)
            if texto:
                textos.append(texto)
        return "\n".join(textos)
    return str(contenido)


PROMPT_SISTEMA = """
Eres un agente personal de planificacion academica. Ayudas a priorizar
tareas pendientes y a consultar los materiales asociados a cada una,
usando siempre tus herramientas — nunca inventes fechas, prioridades ni
contenido de documentos que no hayas consultado.

Flujo recomendado:
1. Usa consultar_tareas para ver que hay pendiente.
2. Usa calcular_prioridad sobre las tareas relevantes para decidir cual
   atender primero (nunca decidas la urgencia "a ojo").
3. Si el usuario da un tiempo disponible, usa generar_plan para
   distribuir las tareas dentro de ese tiempo.
4. Si el usuario quiere empezar una tarea, usa inspeccionar_carpeta para
   ver que materiales existen, y buscar_en_documentos para consultar
   instrucciones, requisitos o conceptos.
5. Usa actualizar_estado cuando el usuario indique que empezo o termino
   una tarea, y agregar_tarea cuando mencione una actividad nueva que no
   este registrada.
6. Si el usuario pide "guardar", "exportar" o "escribir en un archivo"
   un plan detallado que ya redactaste en la conversacion (distinto de
   la tabla de generar_plan), usa guardar_plan_detallado pasandole ese
   mismo contenido. Nunca digas que un plan quedo guardado sin haber
   llamado a una herramienta que efectivamente lo guarde.

Reglas:
- Solo puedes inspeccionar o buscar dentro de carpetas dentro de la
  carpeta autorizada; si el usuario pide otra ruta, rechazala.
- Se breve y concreto: prioridad, plan de tiempo y proximos pasos.
"""

AGENT_MODEL = os.getenv("AGENT_MODEL", "anthropic").lower()


def resolver_modelo():
    if AGENT_MODEL == "gemma-lmstudio":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("LMSTUDIO_MODEL", "google/gemma-4-e4b"),
            base_url=os.getenv("LMSTUDIO_BASE_URL", "http://172.30.32.1:8666/v1"),
            api_key="lm-studio",
            temperature=0.3,
        )
    if AGENT_MODEL == "anthropic":
        return f"anthropic:{os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-6')}"
    raise ValueError(f"AGENT_MODEL desconocido: {AGENT_MODEL!r}. Opciones: anthropic, gemma-lmstudio")


def _nombre_modelo() -> str:
    if AGENT_MODEL == "gemma-lmstudio":
        return f"{os.getenv('LMSTUDIO_MODEL', 'google/gemma-4-e4b')} (LM Studio, local)"
    return f"{os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-6')} (Anthropic, de pago)"


agent = create_agent(
    model=resolver_modelo(),
    system_prompt=PROMPT_SISTEMA,
    tools=[
        consultar_tareas, agregar_tarea, calcular_prioridad, generar_plan,
        actualizar_estado, guardar_plan_detallado, inspeccionar_carpeta, buscar_en_documentos,
    ],
)


def iniciar_chat() -> None:
    print("=" * 60)
    print("AGENTE PERSONAL DE PLANIFICACION ACADEMICA")
    print("=" * 60)
    print(f"Modelo: {_nombre_modelo()}")
    print('Ejemplo: "Tengo 4 horas libres, dime que tarea es mas urgente y ayudame a empezarla"')
    print("Escribe 'salir' para finalizar.")
    print()

    historial: list[dict] = []
    while True:
        try:
            solicitud = input("Tu: ").strip()
            if not solicitud:
                continue
            if solicitud.lower() in {"salir", "exit", "quit"}:
                print("Agente: Hasta luego.")
                break

            historial.append({"role": "user", "content": solicitud})
            resultado = agent.invoke({"messages": historial})

            mensaje_final = resultado["messages"][-1]
            respuesta = extraer_texto(mensaje_final.content)
            historial.append({"role": "assistant", "content": respuesta})

            print(f"Agente: {respuesta}\n")
        except KeyboardInterrupt:
            print("\nAgente: Sesion finalizada por el usuario.")
            break
        except Exception as error:
            print("Agente: Ocurrio un error al procesar la solicitud.")
            print(f"Detalle tecnico: {error}")


if __name__ == "__main__":
    if AGENT_MODEL == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "No se encontro ANTHROPIC_API_KEY. Agregala al archivo .env, o usa "
            "AGENT_MODEL=gemma-lmstudio para no depender de la API de pago."
        )
    iniciar_chat()
```

## Declaración de transparencia de IA

Este documento y el código que describe fueron elaborados con asistencia de un asistente de IA (Claude Code, Anthropic), bajo dirección explícita del estudiante en cada decisión:

- **Definición del alcance:** la necesidad personal, los objetivos y las decisiones de qué incluir (sin RAG, sin integraciones externas) fueron decisiones del estudiante, no sugerencias del asistente.
- **Generación de código:** el asistente redactó el código de las herramientas, el *system prompt* y esta documentación, a partir de esos requisitos.
- **Verificación y corrección por el estudiante:** el código no se aceptó sin probarlo. Durante las pruebas, el estudiante detectó fallas reales que el asistente tuvo que corregir — por ejemplo, `inspeccionar_carpeta` obligaba al modelo a adivinar una ruta de carpeta (fallaba en la práctica) hasta que se rediseñó para resolverla internamente por id de tarea; y no existía ninguna herramienta capaz de guardar en disco un plan detallado ya redactado en el chat, lo que llevó al modelo a afirmar falsamente que había guardado un archivo — corregido agregando `guardar_plan_detallado`.
- **Pruebas reales:** el agente se ejecutó con un backend real (Claude Sonnet vía API de Anthropic, y también con Gemma 4 E4B vía LM Studio local) contra tareas y materiales de ejemplo, no solo revisado como texto.
