"""
# Agente personal ReAct de planificacion de actividades diarias (v2)
################################################################################

Version 2 de agente_planificacion_academica.py (Sesion 12, carpeta hermana
Tarea_Agente_Personal/). Deja de ser solo "academico": combina actividades
pendientes (academicas y personales, en actividades.json) con los eventos
ya agendados en Google Calendar (reuniones, cursos, citas) para armar el
plan del dia respetando el tiempo real ya comprometido.

Google Calendar en modo SOLO LECTURA (scope calendar.readonly): el agente
nunca crea, modifica ni borra eventos. Requiere credentials.json (ver
CONFIGURAR_GOOGLE_CALENDAR.md, en esta misma carpeta) y, en la primera
ejecucion, un login interactivo en el navegador que genera token.json.

Especificacion completa en agente_react_planificacion_actividades.md, en
esta misma carpeta.

Backends soportados via AGENT_MODEL (.env):
    AGENT_MODEL=anthropic       -> Claude via API de Anthropic (de pago)
    AGENT_MODEL=gemma-lmstudio  -> Gemma 4 E4B via LM Studio (local, gratis)

Ejecutar el chat interactivo:
    python agente_planificacion_actividades.py
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

RUTA_ACTIVIDADES = Path(__file__).parent / "actividades.json"

# Carpeta donde se guarda un .md por cada plan generado.
CARPETA_PLANES = Path(__file__).parent / "planes_generados"

# Carpeta raiz fuera de la cual el agente no puede leer nada.
CARPETA_AUTORIZADA = Path(
    os.getenv("CARPETA_AUTORIZADA", str(Path(__file__).parent / "materiales"))
).resolve()

EXTENSIONES_ADMITIDAS = {".pdf", ".docx", ".txt", ".md", ".py"}

PESO_PRIORIDAD = {"alta": 3, "media": 2, "baja": 1}

# Google Calendar: solo lectura, nunca se pide permiso de escritura.
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
RUTA_CREDENCIALES = Path(__file__).parent / os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "credentials.json")
RUTA_TOKEN = Path(__file__).parent / os.getenv("GOOGLE_CALENDAR_TOKEN", "token.json")


# ------------------------------------------------------------
# 2. HELPERS COMPARTIDOS
# ------------------------------------------------------------

def _normalizar(texto: str) -> str:
    """Quita tildes y pasa a minusculas, para comparar sin importar como se escriba."""

    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c)
    )
    return sin_tildes.strip()


def _cargar_actividades() -> list[dict]:
    if not RUTA_ACTIVIDADES.exists():
        return []
    return json.loads(RUTA_ACTIVIDADES.read_text(encoding="utf-8"))


def _guardar_actividades(actividades: list[dict]) -> None:
    RUTA_ACTIVIDADES.write_text(json.dumps(actividades, ensure_ascii=False, indent=2), encoding="utf-8")


def _buscar_actividad(actividad_id: int) -> dict | None:
    return next((a for a in _cargar_actividades() if a["id"] == actividad_id), None)


def _validar_ruta(ruta: str) -> Path | None:
    """Devuelve la ruta resuelta solo si esta dentro de CARPETA_AUTORIZADA."""

    ruta_resuelta = (Path(__file__).parent / ruta).resolve() if not Path(ruta).is_absolute() else Path(ruta).resolve()
    if ruta_resuelta == CARPETA_AUTORIZADA or CARPETA_AUTORIZADA in ruta_resuelta.parents:
        return ruta_resuelta
    return None


def _puntaje_urgencia(actividad: dict) -> float:
    """
    puntaje = peso_prioridad * 100 / (dias_restantes + 1)

    Heuristica simple y determinista para ordenar actividades: mas
    prioridad declarada y menos tiempo restante equivale a mayor
    urgencia. No es una funcion de utilidad, solo un criterio
    reproducible para decidir el orden.
    """

    dias_restantes = max((date.fromisoformat(actividad["fecha_limite"]) - date.today()).days, 0)
    peso = PESO_PRIORIDAD.get(actividad["prioridad"], 1)
    return peso * 100 / (dias_restantes + 1)


def _hhmm_a_minutos(hhmm: str) -> int:
    horas, minutos = hhmm.split(":")
    return int(horas) * 60 + int(minutos)


def _minutos_a_hhmm(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


# ------------------------------------------------------------
# 3. GOOGLE CALENDAR (solo lectura)
# ------------------------------------------------------------

def _obtener_servicio_calendario():
    """Autentica contra Google Calendar (OAuth2) y devuelve el cliente de la API."""

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None

    if RUTA_TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(RUTA_TOKEN), GOOGLE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not RUTA_CREDENCIALES.exists():
                raise FileNotFoundError(
                    f"No se encontro {RUTA_CREDENCIALES}. Sigue los pasos de "
                    "CONFIGURAR_GOOGLE_CALENDAR.md para descargar tus credenciales OAuth."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(RUTA_CREDENCIALES), GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)

        RUTA_TOKEN.write_text(creds.to_json(), encoding="utf-8")

    return build("calendar", "v3", credentials=creds)


def _obtener_eventos_dia(fecha: str) -> list[dict]:
    """Devuelve los eventos del dia [{resumen, inicio, fin}], ordenados por hora de inicio."""

    fecha_obj = date.fromisoformat(fecha) if fecha else date.today()
    zona = datetime.now().astimezone().tzinfo
    inicio_dia = datetime.combine(fecha_obj, datetime.min.time(), tzinfo=zona)
    fin_dia = datetime.combine(fecha_obj, datetime.max.time(), tzinfo=zona)

    servicio = _obtener_servicio_calendario()
    resultado = servicio.events().list(
        calendarId="primary",
        timeMin=inicio_dia.isoformat(),
        timeMax=fin_dia.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    eventos = []

    for item in resultado.get("items", []):
        inicio = item["start"].get("dateTime", item["start"].get("date"))
        fin = item["end"].get("dateTime", item["end"].get("date"))
        eventos.append({"resumen": item.get("summary", "(sin titulo)"), "inicio": inicio, "fin": fin})

    return eventos


def _calcular_huecos_libres(hora_inicio: str, hora_fin: str, eventos: list[dict]) -> list[tuple[int, int]]:
    """
    Calcula los huecos libres (en minutos desde medianoche) entre
    hora_inicio y hora_fin, restando los bloques ocupados por eventos con
    hora puntual. Los eventos de todo el dia (sin "dateTime") no bloquean
    un rango horario especifico y se ignoran aqui.
    """

    inicio_min = _hhmm_a_minutos(hora_inicio)
    fin_min = _hhmm_a_minutos(hora_fin)

    ocupados = sorted(
        (_hhmm_a_minutos(e["inicio"][11:16]), _hhmm_a_minutos(e["fin"][11:16]))
        for e in eventos if "T" in e["inicio"]
    )

    huecos: list[tuple[int, int]] = []
    cursor = inicio_min

    for ini_ocupado, fin_ocupado in ocupados:
        if ini_ocupado > cursor:
            huecos.append((cursor, min(ini_ocupado, fin_min)))
        cursor = max(cursor, fin_ocupado)
        if cursor >= fin_min:
            break

    if cursor < fin_min:
        huecos.append((cursor, fin_min))

    return [(a, b) for a, b in huecos if b > a]


@tool
def consultar_calendario(fecha: str = "") -> str:
    """
    Lista los eventos (reuniones, cursos, citas) del calendario de Google
    para una fecha (YYYY-MM-DD; vacio = hoy). Solo lectura: nunca crea,
    modifica ni borra eventos. Usa esto para saber que bloques del dia ya
    estan ocupados antes de proponer cualquier horario.
    """

    try:
        eventos = _obtener_eventos_dia(fecha)
    except FileNotFoundError as error:
        return str(error)
    except Exception as error:
        return f"No se pudo consultar Google Calendar: {error}"

    if not eventos:
        return f"No hay eventos en el calendario para {fecha or 'hoy'}."

    lineas = []

    for evento in eventos:
        if "T" in evento["inicio"]:
            lineas.append(f"- {evento['resumen']}: {evento['inicio'][11:16]}-{evento['fin'][11:16]}")
        else:
            lineas.append(f"- {evento['resumen']}: todo el dia")

    return f"Eventos para {fecha or 'hoy'}:\n" + "\n".join(lineas)


# ------------------------------------------------------------
# 4. TOOLS - GESTION DE ACTIVIDADES
# ------------------------------------------------------------

@tool
def consultar_actividades() -> str:
    """Devuelve todas las actividades registradas (academicas y personales), con su estado actual."""

    actividades = _cargar_actividades()

    if not actividades:
        return "No hay actividades registradas."

    lineas = []

    for a in actividades:
        detalle_curso = f" — curso: {a['curso']}" if a.get("curso") else ""
        lineas.append(
            f"[{a['id']}] {a['nombre']} ({a['tipo']}){detalle_curso} — vence: {a['fecha_limite']} "
            f"— prioridad: {a['prioridad']} — estado: {a['estado']}"
        )

    return "\n".join(lineas)


@tool
def agregar_actividad(
    nombre: str, tipo: str, fecha_limite: str, duracion_minutos: int,
    prioridad: str, curso: str = "", ruta_contexto: str = "", entregable: str = "",
) -> str:
    """
    Registra una nueva actividad pendiente, academica o personal.

    tipo debe ser 'academica' o 'personal'. fecha_limite en formato
    YYYY-MM-DD. prioridad debe ser 'alta', 'media' o 'baja'. No inventes
    estos datos: pideselos al usuario si no los menciono.
    """

    actividades = _cargar_actividades()
    nuevo_id = max((a["id"] for a in actividades), default=0) + 1
    actividades.append({
        "id": nuevo_id, "nombre": nombre, "tipo": tipo, "curso": curso,
        "fecha_limite": fecha_limite, "duracion_estimada_minutos": duracion_minutos,
        "prioridad": prioridad, "estado": "pendiente",
        "ruta_contexto": ruta_contexto, "entregable": entregable,
    })
    _guardar_actividades(actividades)

    return f"Actividad '{nombre}' registrada con id {nuevo_id}."


@tool
def calcular_prioridad(actividad_id: int) -> str:
    """
    Calcula el puntaje de urgencia de una actividad (fecha limite +
    prioridad declarada). Nunca decidas la urgencia "a ojo": usa siempre
    esta herramienta antes de recomendar cual atender primero.
    """

    actividad = _buscar_actividad(actividad_id)

    if actividad is None:
        return f"No existe una actividad con id {actividad_id}."

    dias_restantes = max((date.fromisoformat(actividad["fecha_limite"]) - date.today()).days, 0)

    return (
        f"Actividad {actividad_id} ({actividad['nombre']}): puntaje de urgencia "
        f"{_puntaje_urgencia(actividad):.1f} (prioridad={actividad['prioridad']}, vence en {dias_restantes} dia(s))."
    )


@tool
def actualizar_estado(actividad_id: int, nuevo_estado: str) -> str:
    """Cambia el estado de una actividad a 'pendiente', 'iniciada' o 'completada'."""

    if nuevo_estado not in {"pendiente", "iniciada", "completada"}:
        return f"Estado '{nuevo_estado}' invalido. Usa: pendiente, iniciada o completada."

    actividades = _cargar_actividades()

    for a in actividades:
        if a["id"] == actividad_id:
            a["estado"] = nuevo_estado
            _guardar_actividades(actividades)
            return f"Actividad {actividad_id} actualizada a estado '{nuevo_estado}'."

    return f"No existe una actividad con id {actividad_id}."


# ------------------------------------------------------------
# 5. GENERAR PLAN (respeta Google Calendar)
# ------------------------------------------------------------

@tool
def generar_plan(fecha: str, hora_inicio: str, hora_fin: str) -> str:
    """
    Arma el plan del dia distribuyendo las actividades pendientes (por
    puntaje de urgencia) dentro de los huecos libres entre hora_inicio y
    hora_fin, respetando los eventos ya agendados en Google Calendar —
    nunca asigna una actividad sobre un bloque ya ocupado. Guarda el plan
    como reporte en Markdown. fecha en formato YYYY-MM-DD (vacio = hoy),
    horas en formato HH:MM. Usala despues de consultar_calendario y
    calcular_prioridad; no armes el plan a mano.
    """

    try:
        eventos = _obtener_eventos_dia(fecha)
    except FileNotFoundError as error:
        return str(error)
    except Exception as error:
        return f"No se pudo consultar Google Calendar: {error}"

    huecos = _calcular_huecos_libres(hora_inicio, hora_fin, eventos)

    pendientes = sorted(
        (a for a in _cargar_actividades() if a["estado"] != "completada"),
        key=_puntaje_urgencia, reverse=True,
    )

    bloques: list[tuple[int, int, str]] = [
        (_hhmm_a_minutos(e["inicio"][11:16]), _hhmm_a_minutos(e["fin"][11:16]), f"Ocupado: {e['resumen']}")
        for e in eventos if "T" in e["inicio"]
    ]

    asignadas: list[str] = []
    idx_pendiente = 0

    for inicio_hueco, fin_hueco in huecos:
        cursor = inicio_hueco

        while idx_pendiente < len(pendientes):
            actividad = pendientes[idx_pendiente]
            duracion = actividad["duracion_estimada_minutos"]

            if cursor + duracion > fin_hueco:
                break

            bloques.append((cursor, cursor + duracion, f"{actividad['nombre']} (prioridad {actividad['prioridad']})"))
            asignadas.append(actividad["nombre"])
            cursor += duracion

            if cursor + 10 <= fin_hueco:
                cursor += 10

            idx_pendiente += 1

    if not asignadas and not eventos:
        return "No hay eventos en el calendario ni actividades pendientes que quepan en ese rango."

    bloques.sort()
    fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    codigo_plan = f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    filas_md = "\n".join(
        f"| {_minutos_a_hhmm(ini)}-{_minutos_a_hhmm(fin)} | {etiqueta} |" for ini, fin, etiqueta in bloques
    )

    contenido_md = f"""# Plan de actividades diarias

**Código:** {codigo_plan}
**Fecha de generación:** {fecha_generacion}
**Día planificado:** {fecha or 'hoy'}
**Rango:** {hora_inicio}-{hora_fin}

## Línea de tiempo

| Horario | Bloque |
|---|---|
{filas_md}
"""

    CARPETA_PLANES.mkdir(exist_ok=True)
    archivo_plan = CARPETA_PLANES / f"{codigo_plan}.md"
    archivo_plan.write_text(contenido_md, encoding="utf-8")

    return (
        f"Plan {codigo_plan} generado con {len(asignadas)} actividad(es) asignada(s) "
        f"y {len(eventos)} evento(s) de calendario respetados. Reporte guardado en {archivo_plan}."
    )


# ------------------------------------------------------------
# 6. TOOLS - CONSULTA DOCUMENTAL (sin RAG, por palabra clave)
# ------------------------------------------------------------

@tool
def inspeccionar_carpeta(actividad_id: int) -> str:
    """
    Lista los documentos compatibles (PDF, DOCX, TXT, Markdown, Python) en
    la carpeta de materiales de una actividad. Recibe el id de la
    actividad, no una ruta escrita a mano: la ruta real se resuelve
    internamente.
    """

    actividad = _buscar_actividad(actividad_id)

    if actividad is None:
        return f"No existe una actividad con id {actividad_id}."

    if not actividad.get("ruta_contexto"):
        return f"La actividad {actividad_id} no tiene materiales asociados."

    carpeta = _validar_ruta(actividad["ruta_contexto"])

    if carpeta is None:
        return f"La carpeta de materiales de la actividad {actividad_id} esta fuera de la carpeta autorizada."

    if not carpeta.is_dir():
        return f"La carpeta '{actividad['ruta_contexto']}' de la actividad {actividad_id} no existe."

    archivos = sorted(f.name for f in carpeta.iterdir() if f.suffix.lower() in EXTENSIONES_ADMITIDAS)

    if not archivos:
        return f"No se encontraron documentos compatibles en la carpeta de la actividad {actividad_id}."

    return f"Documentos encontrados para la actividad {actividad_id}: " + ", ".join(archivos)


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
def buscar_en_documentos(actividad_id: int, consulta: str) -> str:
    """
    Busca lineas que contengan la consulta (coincidencia de palabra clave,
    SIN embeddings ni vector store) dentro de los documentos de la carpeta
    asociada a una actividad. Usala para saber que dicen los materiales;
    no asumas ni inventes su contenido.
    """

    actividad = _buscar_actividad(actividad_id)

    if actividad is None:
        return f"No existe una actividad con id {actividad_id}."

    if not actividad.get("ruta_contexto"):
        return f"La actividad {actividad_id} no tiene materiales asociados."

    carpeta = _validar_ruta(actividad["ruta_contexto"])

    if carpeta is None or not carpeta.is_dir():
        return f"La carpeta de materiales de la actividad {actividad_id} no es valida."

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
        return f"No se encontro '{consulta}' en los documentos de la actividad {actividad_id}."

    return "\n".join(coincidencias[:10])


# ------------------------------------------------------------
# 7. FUNCION PARA EXTRAER LA RESPUESTA DEL MODELO
# ------------------------------------------------------------

def extraer_texto(contenido) -> str:
    """Convierte la respuesta del modelo (string o lista de bloques) en texto plano."""

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
# 8. CREACION DEL AGENTE
# ------------------------------------------------------------

PROMPT_SISTEMA = """
Eres un agente personal de planificacion de actividades diarias. Ayudas
a organizar el dia del usuario combinando sus actividades pendientes
(academicas y personales) con los compromisos ya agendados en Google
Calendar (reuniones, cursos, citas) — nunca inventes horarios, fechas,
prioridades ni contenido de documentos que no hayas consultado.

Flujo recomendado:
1. Usa consultar_actividades para ver que hay pendiente.
2. Usa calcular_prioridad sobre las actividades relevantes para decidir
   cual atender primero.
3. Usa consultar_calendario para ver que reuniones o cursos ya estan
   agendados ese dia, ANTES de proponer cualquier horario.
4. Si el usuario da un rango horario disponible, usa generar_plan para
   distribuir las actividades pendientes en los huecos libres — nunca
   sobre un bloque ya ocupado del calendario.
5. Si el usuario quiere empezar una actividad con materiales asociados,
   usa inspeccionar_carpeta y buscar_en_documentos.
6. Usa actualizar_estado cuando el usuario indique que empezo o termino
   una actividad, y agregar_actividad cuando mencione una nueva.

Reglas:
- Solo puedes inspeccionar o buscar dentro de carpetas dentro de la
  carpeta autorizada; si el usuario pide otra ruta, rechazala.
- El calendario es de SOLO LECTURA: nunca ofrezcas crear, modificar ni
  borrar eventos.
- Se breve y concreto: prioridad, plan de tiempo y proximos pasos.
"""

# AGENT_MODEL elige el backend del modelo (mismo patron que v1 y que el
# lab de equipo editorial de la Sesion 14).
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


agent = create_agent(
    model=resolver_modelo(),
    system_prompt=PROMPT_SISTEMA,
    tools=[
        consultar_actividades, agregar_actividad, calcular_prioridad, actualizar_estado,
        consultar_calendario, generar_plan,
        inspeccionar_carpeta, buscar_en_documentos,
    ],
)


# ------------------------------------------------------------
# 9. FLUJO PRINCIPAL
# ------------------------------------------------------------

def iniciar_chat() -> None:
    """Punto de entrada interactivo. Cada mensaje se procesa con memoria de la sesion actual."""

    print("=" * 60)
    print("AGENTE PERSONAL DE PLANIFICACION DE ACTIVIDADES DIARIAS")
    print("=" * 60)
    print('Ejemplo: "Tengo de 14:00 a 20:00 libres hoy, arma mi plan considerando mi calendario"')
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
# 10. EJECUCION
# ------------------------------------------------------------

if __name__ == "__main__":
    if AGENT_MODEL == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "No se encontro ANTHROPIC_API_KEY. Agregala al archivo .env, o usa "
            "AGENT_MODEL=gemma-lmstudio para no depender de la API de pago."
        )

    print(f"(Usando AGENT_MODEL={AGENT_MODEL})\n")
    iniciar_chat()
