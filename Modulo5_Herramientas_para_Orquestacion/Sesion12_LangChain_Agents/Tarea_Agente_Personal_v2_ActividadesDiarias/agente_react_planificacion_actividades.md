# v2 — Agente personal ReAct de planificación de actividades diarias (con Google Calendar)

## 1. Qué cambia respecto a v1

[v1](../Tarea_Agente_Personal/agente_react_planificacion_academica.md) es un
**Agente Personal de Planificación Académica**: solo tareas de curso, sin
Google Calendar, alcance exactamente el de la tarea calificada de la
Sesión 12. v2 es una evolución personal, más allá de esa tarea: deja de
ser "solo académico" y pasa a ser un **Agente Personal de Planificación de
Actividades Diarias**, que:

- gestiona actividades **académicas y personales** (`actividades.json`,
  generaliza `tareas.json`);
- **lee Google Calendar** (solo lectura) para conocer reuniones, cursos y
  citas ya agendados ese día;
- arma el plan del día como una **línea de tiempo real** (huecos libres
  entre eventos existentes), no una simple lista aditiva de duraciones
  como hacía v1.

v1 sigue existiendo tal cual, sin tocar — v2 es una carpeta hermana
independiente.

## 2. Necesidad personal

El plan de v1 asumía que todo el tiempo entre ahora y la fecha límite
estaba libre — pero en la práctica el día ya tiene reuniones, clases y
citas fijas. Un plan que ignora eso es poco realista: v2 resuelve esto
consultando el calendario real antes de proponer un horario.

## 3. Objetivo general

**Implementar un agente personal ReAct que combine actividades pendientes
(académicas y personales) con los eventos ya agendados en Google
Calendar, para proponer un plan de tiempo realista del día, usando
LangChain.**

## 4. Objetivos específicos

1. Generalizar la gestión de actividades de v1 para admitir tipos
   académicos y personales.
2. Leer Google Calendar en modo solo lectura para conocer los bloques ya
   ocupados de un día.
3. Calcular los huecos libres reales entre esos bloques y distribuir ahí
   las actividades pendientes, por urgencia.
4. Mantener sin cambios de lógica lo que v1 ya resolvía bien: búsqueda
   documental por palabra clave, seguridad de rutas, switch de modelo.

## 5. Ejemplo de uso

```
Tu: tengo de 14:00 a 20:00 libres hoy, arma mi plan considerando mi calendario

Acción: consultar_actividades       → 3 actividades pendientes
Acción: calcular_prioridad (c/u)    → "Implementar agente ReAct" es la más urgente
Acción: consultar_calendario        → "Reunión de equipo: 16:00-17:00"
Acción: generar_plan(hoy, 14:00, 20:00)
Observación: huecos libres 14:00-16:00 y 17:00-20:00; la reunión de
             16:00-17:00 queda intacta; las actividades se distribuyen
             en los huecos.

Respuesta final: línea de tiempo del día, reporte guardado en .md.
```

## 6. Modelo de datos — `actividades.json`

Mismo esquema que v1, con `curso` opcional y `tipo` nuevo:

```json
[
  {
    "id": 1,
    "nombre": "Implementar agente personal ReAct",
    "tipo": "academica",
    "curso": "Implementación de agentes con IA",
    "fecha_limite": "2026-08-02",
    "duracion_estimada_minutos": 240,
    "prioridad": "alta",
    "estado": "pendiente",
    "ruta_contexto": "materiales/TareaReAct",
    "entregable": "Google Doc con objetivo y código"
  },
  {
    "id": 3,
    "nombre": "Renovar DNI",
    "tipo": "personal",
    "curso": "",
    "fecha_limite": "2026-08-15",
    "duracion_estimada_minutos": 60,
    "prioridad": "media",
    "estado": "pendiente",
    "ruta_contexto": "",
    "entregable": ""
  }
]
```

`tipo` ∈ {`academica`, `personal`}. `ruta_contexto`/`curso` vacíos son
válidos (actividades sin materiales asociados, como un trámite personal).

## 7. Google Calendar — integración de solo lectura

Scope pedido: `https://www.googleapis.com/auth/calendar.readonly` —
técnicamente imposible que el agente cree, edite o borre un evento con
ese permiso. Configuración completa (proyecto de Google Cloud,
credenciales OAuth) en
[CONFIGURAR_GOOGLE_CALENDAR.md](CONFIGURAR_GOOGLE_CALENDAR.md).

```python
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
RUTA_CREDENCIALES = Path(__file__).parent / os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "credentials.json")
RUTA_TOKEN = Path(__file__).parent / os.getenv("GOOGLE_CALENDAR_TOKEN", "token.json")


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
        calendarId="primary", timeMin=inicio_dia.isoformat(), timeMax=fin_dia.isoformat(),
        singleEvents=True, orderBy="startTime",
    ).execute()

    eventos = []
    for item in resultado.get("items", []):
        inicio = item["start"].get("dateTime", item["start"].get("date"))
        fin = item["end"].get("dateTime", item["end"].get("date"))
        eventos.append({"resumen": item.get("summary", "(sin titulo)"), "inicio": inicio, "fin": fin})
    return eventos


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
```

**Nota sobre eventos de todo el día:** un evento sin `dateTime` (solo
`date`) no tiene hora puntual — se muestra en `consultar_calendario` pero
no se trata como bloque horario ocupado en `generar_plan` (Sección 8).

## 8. `generar_plan` v2 — huecos libres reales, no suma de duraciones

Diferencia clave con v1: recibe un rango horario real (`hora_inicio`,
`hora_fin`), resta los bloques ocupados del calendario, y solo asigna
actividades en lo que sobra:

```python
def _hhmm_a_minutos(hhmm: str) -> int:
    horas, minutos = hhmm.split(":")
    return int(horas) * 60 + int(minutos)


def _minutos_a_hhmm(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def _calcular_huecos_libres(hora_inicio: str, hora_fin: str, eventos: list[dict]) -> list[tuple[int, int]]:
    """
    Calcula los huecos libres (en minutos desde medianoche) entre
    hora_inicio y hora_fin, restando los bloques ocupados por eventos con
    hora puntual. Los eventos de todo el dia se ignoran aqui.
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
def generar_plan(fecha: str, hora_inicio: str, hora_fin: str) -> str:
    """
    Arma el plan del dia distribuyendo las actividades pendientes (por
    puntaje de urgencia) dentro de los huecos libres entre hora_inicio y
    hora_fin, respetando los eventos ya agendados en Google Calendar —
    nunca asigna una actividad sobre un bloque ya ocupado. Guarda el plan
    como reporte en Markdown.
    """
    eventos = _obtener_eventos_dia(fecha)
    huecos = _calcular_huecos_libres(hora_inicio, hora_fin, eventos)

    pendientes = sorted(
        (a for a in _cargar_actividades() if a["estado"] != "completada"),
        key=_puntaje_urgencia, reverse=True,
    )

    bloques = [
        (_hhmm_a_minutos(e["inicio"][11:16]), _hhmm_a_minutos(e["fin"][11:16]), f"Ocupado: {e['resumen']}")
        for e in eventos if "T" in e["inicio"]
    ]

    asignadas, idx = [], 0
    for inicio_hueco, fin_hueco in huecos:
        cursor = inicio_hueco
        while idx < len(pendientes):
            actividad = pendientes[idx]
            duracion = actividad["duracion_estimada_minutos"]
            if cursor + duracion > fin_hueco:
                break
            bloques.append((cursor, cursor + duracion, f"{actividad['nombre']} (prioridad {actividad['prioridad']})"))
            asignadas.append(actividad["nombre"])
            cursor += duracion
            if cursor + 10 <= fin_hueco:
                cursor += 10
            idx += 1
    # ... arma la línea de tiempo ordenada y la guarda en planes_generados/
```

(Código completo, incluyendo el guardado en Markdown, en
[agente_planificacion_actividades.py](agente_planificacion_actividades.py).)

**Por qué esto es un algoritmo real de scheduling y no una lista:** v1
solo sumaba duraciones sin saber la hora real de nada. v2 hace
*interval scheduling* básico — calcula huecos libres reales entre
bloques ocupados y asigna actividades solo ahí, así que nunca puede
proponer una actividad encima de una reunión ya agendada.

## 9. Resto de tools — sin cambios de lógica respecto a v1

`consultar_actividades`, `agregar_actividad`, `calcular_prioridad`,
`actualizar_estado`, `inspeccionar_carpeta(actividad_id)`,
`buscar_en_documentos(actividad_id, consulta)` son las mismas de v1
(mismo criterio: nunca RAG, siempre por `actividad_id` — nunca una ruta
que el modelo tenga que adivinar, lección aprendida en v1 cuando
`inspeccionar_carpeta` tomaba una ruta libre), solo renombradas de
"tarea" a "actividad" y con manejo explícito de actividades sin
materiales asociados (`ruta_contexto` vacío → "no tiene materiales
asociados", en vez de un falso "ruta no autorizada").

## 10. System prompt

```python
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
```

## 11. Modelo y creación del agente

Mismo switch `AGENT_MODEL` (`anthropic` / `gemma-lmstudio`) de v1, sin
cambios — ver `resolver_modelo()` en
[agente_planificacion_actividades.py](agente_planificacion_actividades.py).

```python
agent = create_agent(
    model=resolver_modelo(),
    system_prompt=PROMPT_SISTEMA,
    tools=[
        consultar_actividades, agregar_actividad, calcular_prioridad, actualizar_estado,
        consultar_calendario, generar_plan,
        inspeccionar_carpeta, buscar_en_documentos,
    ],
)
```

## 12. Consideraciones de seguridad

- Todo lo de v1 (carpeta autorizada, extensiones en lista blanca, ningún
  archivo se ejecuta) se mantiene igual.
- Google Calendar: scope de **solo lectura**; `credentials.json` y
  `token.json` nunca se suben al repo (`.gitignore` de la sesión) y
  ninguna tool los expone como texto — se usan solo internamente para
  autenticar.
- Si `credentials.json` no existe, las tools de calendario devuelven un
  mensaje de error claro señalando la guía de configuración, en vez de
  fallar con una traza críptica.

## 13. Por qué esto sigue siendo un agente, Goal-Based, y dónde está ReAct

Mismo análisis que v1 (ver su Sección 18), con la meta ampliada: ya no es
solo "cumplir la fecha límite de una tarea académica" sino "encajar todas
las actividades pendientes del día en el tiempo que de verdad queda libre
después de los compromisos ya agendados" — sigue siendo **Goal-Based**
(evalúa una meta explícita y elige acciones para acercarse a ella), no
Utility-Based (`_puntaje_urgencia` sigue siendo una heurística
determinista, no una función de utilidad con trade-offs ponderados).

El ciclo ReAct ocurre en el mismo lugar que en v1 (dentro de
`create_agent`), con un paso más en la cadena típica:

```
Thought:      "Necesito saber qué actividades hay antes de priorizar."
Action:       consultar_actividades()
Observation:  "3 actividades pendientes..."

Thought:      "Necesito saber qué ya está agendado hoy antes de proponer horario."
Action:       consultar_calendario()
Observation:  "Reunión de equipo: 16:00-17:00"

Thought:      "Con eso puedo armar el plan sin chocar con la reunión."
Action:       generar_plan(fecha="", hora_inicio="14:00", hora_fin="20:00")
Observation:  "Plan generado con 2 actividades asignadas y 1 evento respetado."
```

## 14. Alcance — v2 (esta versión) vs. v3 (futuro)

**v2 (esta versión):** lectura de Calendar, scheduling alrededor de
bloques ocupados, actividades académicas y personales unificadas.

**v3 (posible evolución futura):** escritura en Calendar (crear un evento
por cada bloque de actividad que el agente agenda) — descartado a
propósito en v2 por decisión explícita del usuario: mantener el
calendario real intacto y de solo lectura, sin riesgo de llenarlo de
eventos generados por el agente.

## 15. Declaración de transparencia de IA

Este documento y el código que describe fueron elaborados con asistencia
de un asistente de IA (Claude Code), a partir de la necesidad, el alcance
y las decisiones explícitas del estudiante (Calendar solo lectura, no
tocar los archivos de v1, guía de configuración desde cero). El asistente
ayudó a redactar el detalle técnico, el algoritmo de huecos libres y el
código de las herramientas.

## 16. Conclusión

v2 generaliza v1 de "agente académico" a "agente personal de
planificación de actividades diarias", agregando una integración real
(aunque acotada a solo lectura) con Google Calendar, y reemplazando la
suma ingenua de duraciones de v1 por un cálculo real de huecos libres
alrededor de los compromisos ya agendados — sin tocar ni un archivo de
v1, que sigue siendo la entrega válida de la tarea original de la Sesión 12.
