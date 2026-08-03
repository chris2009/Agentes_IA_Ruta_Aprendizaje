"""
# Agente personal ReAct de planificacion academica (Tool Calling Agent)
################################################################################

Tarea - Agente ReAct Personal (Sesion 12). Agente que prioriza tareas
academicas pendientes segun fecha limite y prioridad declarada, distribuye
el tiempo disponible entre ellas, e inspecciona/busca por palabra clave en
los documentos asociados a cada una. Especificacion completa y
justificacion teorica (tipo de agente, patron ReAct) en
agente_react_planificacion_academica.md, en esta misma carpeta.

Sin RAG ni vector store (ver Seccion 15 del .md): la busqueda documental es
por coincidencia de texto, no por embeddings.

Backends soportados via AGENT_MODEL (.env):
    AGENT_MODEL=anthropic       -> Claude via API de Anthropic (de pago)
    AGENT_MODEL=gemma-lmstudio  -> Gemma 4 E4B via LM Studio (local, gratis)

Ejecutar el chat interactivo:
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


# ------------------------------------------------------------
# 1. CONFIGURACION
# ------------------------------------------------------------

RUTA_TAREAS = Path(__file__).parent / "tareas.json"

# Carpeta donde se guarda un .md por cada plan generado (mismo patron que
# presupuestos_generados/ en agente_presupuesto_materiales.py).
CARPETA_PLANES = Path(__file__).parent / "planes_generados"

# Carpeta raiz fuera de la cual el agente no puede leer nada. Por defecto
# apunta a materiales/ dentro de esta misma carpeta (portable, sirve para
# probar el agente); puede sobreescribirse con la variable de entorno.
CARPETA_AUTORIZADA = Path(
    os.getenv("CARPETA_AUTORIZADA", str(Path(__file__).parent / "materiales"))
).resolve()

EXTENSIONES_ADMITIDAS = {".pdf", ".docx", ".txt", ".md", ".py"}

PESO_PRIORIDAD = {"alta": 3, "media": 2, "baja": 1}


# ------------------------------------------------------------
# 2. HELPERS COMPARTIDOS
# ------------------------------------------------------------

def _normalizar(texto: str) -> str:
    """Quita tildes y pasa a minusculas, para comparar sin importar como se escriba."""

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
    """Devuelve la ruta resuelta solo si esta dentro de CARPETA_AUTORIZADA."""

    ruta_resuelta = (Path(__file__).parent / ruta).resolve() if not Path(ruta).is_absolute() else Path(ruta).resolve()
    if ruta_resuelta == CARPETA_AUTORIZADA or CARPETA_AUTORIZADA in ruta_resuelta.parents:
        return ruta_resuelta
    return None


def _puntaje_urgencia(tarea: dict) -> float:
    """
    puntaje = peso_prioridad * 100 / (dias_restantes + 1)

    Heuristica simple y determinista para ordenar tareas: mas prioridad
    declarada y menos tiempo restante equivale a mayor urgencia. No es una
    funcion de utilidad (no pondera trade-offs entre objetivos en
    conflicto), solo un criterio reproducible para decidir el orden.
    """

    dias_restantes = max((date.fromisoformat(tarea["fecha_limite"]) - date.today()).days, 0)
    peso = PESO_PRIORIDAD.get(tarea["prioridad"], 1)
    return peso * 100 / (dias_restantes + 1)


# ------------------------------------------------------------
# 3. TOOLS - GESTION DE TAREAS
# ------------------------------------------------------------

@tool
def consultar_tareas() -> str:
    """Devuelve todas las tareas academicas registradas, con su estado actual."""

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
    Registra una nueva actividad academica pendiente.

    fecha_limite en formato YYYY-MM-DD. prioridad debe ser 'alta', 'media'
    o 'baja'. No inventes estos datos: pideselos al usuario si no los
    menciono.
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
    """
    Calcula el puntaje de urgencia de una tarea (fecha limite + prioridad
    declarada). Nunca decidas la urgencia "a ojo": usa siempre esta
    herramienta antes de recomendar que tarea atender primero.
    """

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
    Distribuye las tareas pendientes (no completadas) dentro del tiempo
    disponible, de mayor a menor puntaje de urgencia, con 10 minutos de
    descanso entre tareas, y guarda el plan como reporte en Markdown.
    Usala despues de revisar prioridades con calcular_prioridad; no armes
    el plan a mano.
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
    Guarda como archivo Markdown en planes_generados/ un plan detallado
    que ya redactaste para el usuario (por ejemplo, el desglose por fases
    para completar una tarea) — no recalcula nada, guarda exactamente el
    contenido que le pasas.

    Usa esta herramienta cuando el usuario pida "guardar", "exportar" o
    "escribir en un archivo" un plan que ya generaste en la conversación.
    No es lo mismo que generar_plan (que arma la tabla de prioridades
    desde tareas.json): esta guarda el texto libre que tú ya escribiste.
    Nunca digas que un plan quedó guardado sin haber llamado a esta
    herramienta primero.
    """

    tarea = _buscar_tarea(tarea_id)

    if tarea is None:
        return f"No existe una tarea con id {tarea_id}."

    fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    codigo_plan = f"PLAN-DETALLADO-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    contenido_final = (
        f"# {titulo}\n\n"
        f"**Código:** {codigo_plan}\n"
        f"**Fecha de generación:** {fecha_generacion}\n"
        f"**Tarea:** {tarea['nombre']}\n\n"
        "---\n\n"
        f"{contenido_markdown}"
    )

    try:
        CARPETA_PLANES.mkdir(exist_ok=True)
        archivo_plan = CARPETA_PLANES / f"{codigo_plan}.md"
        archivo_plan.write_text(contenido_final, encoding="utf-8")
    except OSError as error:
        return f"No se pudo guardar el plan: {error}"

    return f"Plan detallado guardado en {archivo_plan}."


# ------------------------------------------------------------
# 4. TOOLS - CONSULTA DOCUMENTAL (sin RAG, por palabra clave)
# ------------------------------------------------------------

@tool
def inspeccionar_carpeta(tarea_id: int) -> str:
    """
    Lista los documentos compatibles (PDF, DOCX, TXT, Markdown, Python) en
    la carpeta de materiales de una tarea. Recibe el id de la tarea, no
    una ruta escrita a mano: la ruta real (ruta_contexto) se resuelve
    internamente, para no depender de que la adivines.
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
    """Extrae texto plano segun la extension. Sin embeddings: solo lectura."""

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
    Busca lineas que contengan la consulta (coincidencia de palabra clave,
    SIN embeddings ni vector store) dentro de los documentos de la carpeta
    asociada a una tarea. Usala para saber que dicen los materiales; no
    asumas ni inventes su contenido.
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


# ------------------------------------------------------------
# 5. FUNCION PARA EXTRAER LA RESPUESTA DEL MODELO
# ------------------------------------------------------------

def extraer_texto(contenido) -> str:
    """
    Convierte la respuesta del modelo en texto.

    Algunos modelos retornan un string y otros retornan una lista de
    bloques de contenido (p. ej. Claude con thinking activado).
    """

    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):
        textos = []

        for bloque in contenido:
            if isinstance(bloque, dict):
                texto = bloque.get("text")
            else:
                texto = getattr(bloque, "text", None)

            if texto:
                textos.append(texto)

        return "\n".join(textos)

    return str(contenido)


# ------------------------------------------------------------
# 6. CREACION DEL AGENTE
# ------------------------------------------------------------

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

# AGENT_MODEL elige el backend del modelo: "anthropic" (por defecto, de pago,
# consume tokens de la API) o "gemma-lmstudio" (Gemma 4 E4B corriendo en
# LM Studio, local y gratis, requiere el servidor de LM Studio activo).
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
    """Nombre legible del modelo real que se va a usar, para mostrarlo al arrancar."""

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


# ------------------------------------------------------------
# 7. FLUJO PRINCIPAL
# ------------------------------------------------------------

def iniciar_chat() -> None:
    """Punto de entrada interactivo. Cada mensaje se procesa con memoria de la sesion actual."""

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


# ------------------------------------------------------------
# 8. EJECUCION
# ------------------------------------------------------------

if __name__ == "__main__":
    if AGENT_MODEL == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "No se encontro ANTHROPIC_API_KEY. Agregala al archivo .env, o usa "
            "AGENT_MODEL=gemma-lmstudio para no depender de la API de pago."
        )

    iniciar_chat()
