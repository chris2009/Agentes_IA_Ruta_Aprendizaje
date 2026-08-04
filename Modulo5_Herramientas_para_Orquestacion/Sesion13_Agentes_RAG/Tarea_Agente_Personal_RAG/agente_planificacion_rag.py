"""
Agente personal de planificacion academica, construido con LangChain
(create_agent) siguiendo el patron ReAct: prioriza tareas pendientes segun
fecha limite y prioridad, arma un plan de tiempo, y responde preguntas sobre
los documentos asociados a cada tarea usando RAG real (Chroma + embeddings),
en vez de una busqueda de texto literal.

Version RAG (Sesion 13) de Tarea_Agente_Personal (Sesion 12): mismo agente
de planificacion, con buscar_en_documentos reemplazada por busqueda semantica
(ver rag.py), y una tool nueva de busqueda web (Tavily) como respaldo cuando
los materiales locales no alcanzan.

Backends soportados via AGENT_MODEL (.env):
    AGENT_MODEL=anthropic       -> Claude via API de Anthropic
    AGENT_MODEL=gemma-lmstudio  -> Gemma 4 E4B via LM Studio (local)

Antes de correr el chat, asegurate de tener las dependencias instaladas en
el venv (ver requirements.txt). Para correr el chat:
    python agente_planificacion_rag.py
    python agente_planificacion_rag.py --reindexar   # fuerza reconstruir el indice RAG
"""

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from pydantic import BaseModel, Field

import rag

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
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


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


@tool
def buscar_en_documentos(consulta: str, tarea_id: int | None = None) -> str:
    """
    Busca semanticamente (RAG con Chroma) dentro de los documentos de
    materiales/. Si se da tarea_id, filtra por la carpeta de materiales de
    esa tarea; si no, busca en todo el material indexado. A diferencia de
    una busqueda de texto literal, encuentra fragmentos relevantes aunque
    la pregunta no use las mismas palabras que el documento.

    Args:
        consulta: Pregunta o tema a buscar.
        tarea_id: Id de la tarea para limitar la busqueda a su carpeta de
            materiales (opcional; si se omite, busca en todos los materiales).
    """
    ruta_contexto = None
    if tarea_id is not None:
        tarea = _buscar_tarea(tarea_id)
        if tarea is None:
            return f"No existe una tarea con id {tarea_id}."
        if not tarea.get("ruta_contexto"):
            return f"La tarea {tarea_id} no tiene materiales asociados."
        ruta_contexto = tarea["ruta_contexto"]

    resultados = rag.buscar(consulta, k=4, ruta_contexto=ruta_contexto)
    if not resultados:
        return f"No se encontro informacion relevante para '{consulta}' en los materiales indexados."
    return "\n\n".join(f"[{doc.metadata['archivo']}] {doc.page_content}" for doc in resultados)


@tool
def buscar_en_la_web(consulta: str) -> str:
    """
    Busca informacion en la web con Tavily. Usala solo cuando
    buscar_en_documentos no encontro nada util en los materiales locales, o
    el usuario pregunta algo general que no depende de sus documentos (ej.
    conceptos, definiciones).
    """
    if not TAVILY_API_KEY:
        return "Busqueda web no disponible: falta configurar TAVILY_API_KEY en el archivo .env."

    from tavily import TavilyClient
    client = TavilyClient(TAVILY_API_KEY)
    respuesta = client.search(query=consulta, search_depth="advanced")

    resultados = respuesta.get("results", [])
    if not resultados:
        return f"No se encontraron resultados en la web para '{consulta}'."

    return "\n\n".join(
        f"{r.get('title', 'Sin titulo')}\n{r.get('content', '')}\nFuente: {r.get('url', '')}"
        for r in resultados
    )


class RespuestaAgente(BaseModel):
    resumen: str = Field(description="Resumen breve de la respuesta al usuario")
    acciones_recomendadas: str = Field(description="Proximos pasos concretos que el usuario deberia tomar")
    fuentes: list[str] = Field(default_factory=list, description="Archivos o resultados web usados como referencia")
    tools_usadas: list[str] = Field(default_factory=list, description="Nombres de las herramientas utilizadas para responder")


PROMPT_SISTEMA = """
Eres un agente personal de planificacion academica. Ayudas a priorizar
tareas pendientes y a responder preguntas sobre los materiales asociados a
cada una, usando siempre tus herramientas — nunca inventes fechas,
prioridades ni contenido de documentos que no hayas consultado.

Flujo recomendado:
1. Usa consultar_tareas para ver que hay pendiente.
2. Usa calcular_prioridad sobre las tareas relevantes para decidir cual
   atender primero (nunca decidas la urgencia "a ojo").
3. Si el usuario da un tiempo disponible, usa generar_plan para
   distribuir las tareas dentro de ese tiempo.
4. Si el usuario quiere empezar una tarea o pregunta algo sobre sus
   materiales, usa inspeccionar_carpeta para ver que documentos existen, y
   buscar_en_documentos (busqueda semantica con RAG, no busqueda literal)
   para responder preguntas de contenido — funciona aunque la pregunta no
   use las mismas palabras del documento.
5. Evalua con cuidado lo que devuelve buscar_en_documentos: que aparezcan
   fragmentos NO significa que respondan la pregunta. Si el usuario
   pregunta por un termino o concepto especifico (ej. "que es X") y ese
   termino NO esta explicitamente definido/explicado en los fragmentos
   devueltos — aunque mencionen temas relacionados o parecidos — eso
   cuenta como "no encontrado". En ese caso, o si la pregunta es general y
   no depende de los materiales del usuario (definiciones, conceptos,
   informacion actualizada), DEBES llamar tambien a buscar_en_la_web antes
   de responder. Nunca uses un fragmento tangencialmente relacionado como
   si fuera la respuesta a una pregunta distinta.
6. Usa actualizar_estado cuando el usuario indique que empezo o termino
   una tarea, y agregar_tarea cuando mencione una actividad nueva que no
   este registrada.
7. Si el usuario pide "guardar", "exportar" o "escribir en un archivo"
   un plan detallado que ya redactaste en la conversacion (distinto de
   la tabla de generar_plan), usa guardar_plan_detallado pasandole ese
   mismo contenido. Nunca digas que un plan quedo guardado sin haber
   llamado a una herramienta que efectivamente lo guarde.

Reglas:
- Solo puedes inspeccionar o buscar dentro de carpetas dentro de la
  carpeta autorizada; si el usuario pide otra ruta, rechazala.
- Se breve y concreto: prioridad, plan de tiempo y proximos pasos.
- Toda respuesta debe llenar los campos de RespuestaAgente: resumen,
  acciones_recomendadas, fuentes (archivos o resultados web citados) y
  tools_usadas (las herramientas que efectivamente llamaste).
- NUNCA generes la respuesta final (RespuestaAgente) sin haber llamado
  antes a las herramientas necesarias para responder la pregunta. Esta
  prohibido responder cosas como "dame un momento", "estoy consultando"
  o "espera mientras reviso" como respuesta final — eso no es una
  respuesta, es una excusa. Si la pregunta requiere informacion de
  tareas.json o de los materiales, llama la herramienta correspondiente
  en este mismo turno y recien entonces genera RespuestaAgente con el
  resultado real.
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


# Construye (o carga si ya existe) el indice RAG antes de crear el agente.
# `python agente_planificacion_rag.py --reindexar` fuerza reconstruirlo.
rag.construir_o_cargar_indice(forzar_reindexado="--reindexar" in sys.argv)

agent = create_agent(
    model=resolver_modelo(),
    system_prompt=PROMPT_SISTEMA,
    tools=[
        consultar_tareas, agregar_tarea, calcular_prioridad, generar_plan,
        actualizar_estado, guardar_plan_detallado, inspeccionar_carpeta,
        buscar_en_documentos, buscar_en_la_web,
    ],
    response_format=RespuestaAgente,
)


def iniciar_chat() -> None:
    print("=" * 60)
    print("AGENTE PERSONAL DE PLANIFICACION ACADEMICA (con RAG)")
    print("=" * 60)
    print(f"Modelo: {_nombre_modelo()}")
    print('Ejemplo: "¿Que tengo que entregar en la tarea del agente ReAct?"')
    print("Escribe 'salir' para finalizar.")
    print()

    historial: list = []
    while True:
        try:
            solicitud = input("Tu: ").strip()
            if not solicitud:
                continue
            if solicitud.lower() in {"salir", "exit", "quit"}:
                print("Agente: Hasta luego.")
                break

            historial.append({"role": "user", "content": solicitud})
            resultado = agent.invoke({"messages": historial}, config={"recursion_limit": 15})

            structured: RespuestaAgente = resultado["structured_response"]
            historial = resultado["messages"]

            print(f"Agente: {structured.resumen}")
            print(f"  Acciones recomendadas: {structured.acciones_recomendadas}")
            if structured.fuentes:
                print(f"  Fuentes: {', '.join(structured.fuentes)}")
            if structured.tools_usadas:
                print(f"  Herramientas usadas: {', '.join(structured.tools_usadas)}")
            print()
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
