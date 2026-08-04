# Explicación completa del código — Las 5 versiones del Agente Personal

Documento de estudio que explica, por bloques y funciones (no línea por línea literal), cómo
funciona el código de cada una de las 5 versiones del agente personal de planificación
académica construidas a lo largo del programa. Cada sección tiene su propio diagrama de
arquitectura en `diagramas/` (formato draw.io — ábrelos en [app.diagrams.net](https://app.diagrams.net)
o con la app de escritorio de draw.io).

## Índice

1. [Versión 1 — Tarea_Agente_Personal](#versión-1--tarea_agente_personal-sesión-12) (Sesión 12) — agente ReAct base, gestión de tareas en JSON, búsqueda literal en documentos.
2. [Versión 2 — Tarea_Agente_Personal_v2_ActividadesDiarias](#versión-2--tarea_agente_personal_v2_actividadesdiarias-sesión-12) (Sesión 12) — v1 + integración real de Google Calendar.
3. [Versión 3 — Tarea_Agente_Personal_v3_Web](#versión-3--tarea_agente_personal_v3_web-sesión-12) (Sesión 12) — v2 envuelta en una app web (FastAPI + React), sin login.
4. [Versión 4 — AgentePersonal-Web](#versión-4--agentepersonal-web-proyecto-standalone-con-login--mysql) (proyecto standalone) — login real, MySQL multi-usuario, avatar de perfil.
5. [Versión 5 — Tarea_Agente_Personal_RAG](#versión-5--tarea_agente_personal_rag-sesión-13-rag-real-con-chroma) (Sesión 13) — RAG real con Chroma, búsqueda web de respaldo, salida estructurada.

## Diagramas de arquitectura

| Versión | Archivo |
|---|---|
| v1 | `diagramas/v1_tarea_agente_personal.drawio.xml` |
| v2 | `diagramas/v2_actividades_diarias.drawio.xml` |
| v3 | `diagramas/v3_web.drawio.xml` |
| v4 (AgentePersonal-Web) | `diagramas/v4_agentepersonalweb.drawio.xml` |
| v5 (RAG) | `diagramas/v5_rag.drawio.xml` |

---

## Versión 1 — Tarea_Agente_Personal (Sesión 12)

Archivo: `agente_planificacion_academica.py`

### Resumen

Es un agente ReAct (patrón *Reasoning + Acting*, donde el modelo alterna entre "pensar" y llamar herramientas) construido con `create_agent` de LangChain. Gestiona tareas académicas persistidas en un archivo `tareas.json` (sin base de datos), calcula un puntaje de urgencia combinando fecha límite y prioridad declarada, arma planes de tiempo en Markdown, y permite buscar contenido dentro de los documentos (PDF, DOCX, TXT, MD, PY) asociados a cada tarea mediante coincidencia de texto literal — sin *embeddings* (representaciones vectoriales de significado) ni *vector store* (base de datos de esos vectores), es decir, sin RAG (*Retrieval-Augmented Generation*, generación aumentada por recuperación). Lo distingue de versiones posteriores el hecho de ser un único archivo CLI (interfaz de línea de comandos) autocontenido, con backend de modelo intercambiable entre la API de pago de Anthropic y un modelo local servido por LM Studio.

### Estructura de datos

`tareas.json` es una lista de objetos (uno por tarea) con este esquema, inferido de `agregar_tarea` y `consultar_tareas`:

```json
{
  "id": 1,
  "nombre": "...",
  "curso": "...",
  "fecha_limite": "YYYY-MM-DD",
  "duracion_estimada_minutos": 60,
  "prioridad": "alta | media | baja",
  "estado": "pendiente | iniciada | completada",
  "ruta_contexto": "materiales/subcarpeta (opcional)",
  "entregable": "descripción opcional del entregable"
}
```

No hay base de datos: el archivo completo se lee y se reescribe cada vez que cambia algo (patrón *read-modify-write* sobre JSON plano). El `id` se autoasigna como `max(ids existentes) + 1`, arrancando en 1 si la lista está vacía.

### Funciones auxiliares

- **`_normalizar(texto)`**: quita tildes (usando descomposición Unicode NFKD y filtrando caracteres combinantes) y pasa a minúsculas. Se usa tanto para comparar términos de búsqueda como líneas de documentos, de modo que "Válido" y "valido" coincidan.
- **`_cargar_tareas()` / `_guardar_tareas(tareas)`**: leen y escriben `tareas.json` completo como texto JSON (`ensure_ascii=False` para conservar acentos legibles, `indent=2` para que el archivo sea revisable a mano). Si el archivo no existe, `_cargar_tareas` devuelve `[]` en vez de fallar.
- **`_buscar_tarea(tarea_id)`**: recorre la lista cargada y devuelve la primera tarea cuyo `id` coincide, o `None`. Es el punto único que usan todas las tools que operan sobre una tarea existente.
- **`_validar_ruta(ruta)`**: resuelve una ruta relativa o absoluta a una ruta absoluta y comprueba que quede **dentro** de `CARPETA_AUTORIZADA` (igual a ella o que ésta aparezca entre sus carpetas padre). Si la ruta se sale del directorio permitido devuelve `None`. Es el mecanismo de sandboxing (aislamiento de acceso a archivos): el agente nunca puede leer nada fuera de la carpeta de materiales configurada, aunque el usuario o el propio modelo intenten inducirlo con una ruta como `../../secretos`.
- **`_puntaje_urgencia(tarea)`**: heurística determinista, `peso_prioridad * 100 / (dias_restantes + 1)`, donde `peso_prioridad` viene del diccionario `PESO_PRIORIDAD = {"alta": 3, "media": 2, "baja": 1}` y `dias_restantes` nunca baja de 0 (tareas vencidas se tratan como "vencen hoy"). El `+1` en el denominador evita división por cero. A mayor prioridad y menos tiempo restante, mayor el puntaje; es el criterio que ordena todo lo demás.
- **`_extraer_texto_archivo(ruta)`**: dado un `Path`, decide cómo extraer texto según la extensión — lectura directa para `.txt/.md/.py`, `python-docx` para `.docx`, `pypdf` para `.pdf` (concatenando el texto de cada página). Devuelve cadena vacía para extensiones no reconocidas. Las librerías de terceros (`docx`, `pypdf`) se importan de forma perezosa (*lazy import*, dentro de la función) para no exigir esas dependencias si nunca se usan.
- **`extraer_texto(contenido)`**: normaliza la respuesta del modelo a texto plano. LangChain a veces devuelve un string simple y a veces una lista de "bloques" de contenido (por ejemplo cuando Claude usa *extended thinking*/razonamiento explícito); esta función concatena solo los bloques que tienen campo `text`, ignorando el resto.

### Tools del agente

Las 8 herramientas están decoradas con `@tool` de `langchain.tools`, que expone la *docstring* de cada función como la descripción que el modelo lee para decidir cuándo invocarla — por eso las docstrings están escritas como instrucciones de uso, no solo como documentación.

1. **`consultar_tareas()`** — sin parámetros. Devuelve un listado de todas las tareas con id, nombre, curso, fecha límite, prioridad y estado, una por línea. Es el punto de partida típico de cualquier conversación.
2. **`agregar_tarea(nombre, curso, fecha_limite, duracion_minutos, prioridad, ruta_contexto="", entregable="")`** — registra una tarea nueva con `estado="pendiente"` fijo y un `id` autogenerado. La docstring instruye al modelo a pedir el dato al usuario en vez de inventarlo si falta algo.
3. **`calcular_prioridad(tarea_id)`** — calcula y devuelve el puntaje de urgencia de una tarea puntual (vía `_puntaje_urgencia`), junto con los días restantes. El prompt del sistema exige llamarla antes de decidir qué tarea atacar primero, para que la priorización no dependa del criterio libre del modelo.
4. **`generar_plan(minutos_disponibles)`** — toma las tareas no completadas, las ordena de mayor a menor urgencia, y va "llenando" el tiempo disponible: agrega una tarea si cabe entera, deja 10 minutos de descanso entre tareas consecutivas (mientras quede tiempo), y se detiene cuando no cabe ninguna más. Escribe el resultado como tabla Markdown en `planes_generados/PLAN-<timestamp>.md` y devuelve un resumen de cuántas tareas entraron y cuánto tiempo se usó.
5. **`actualizar_estado(tarea_id, nuevo_estado)`** — valida que `nuevo_estado` sea uno de `{"pendiente", "iniciada", "completada"}` y, si la tarea existe, actualiza y persiste el cambio.
6. **`guardar_plan_detallado(tarea_id, titulo, contenido_markdown)`** — a diferencia de `generar_plan` (que arma su propia tabla desde `tareas.json`), esta tool guarda tal cual un contenido que el propio modelo ya redactó en el chat (por ejemplo un desglose por fases explicado en lenguaje natural). Antepone un encabezado con código de plan, fecha y nombre de la tarea, y lo guarda en `planes_generados/PLAN-DETALLADO-<timestamp>.md`. Existe para que el agente nunca "mienta" diciendo que guardó algo sin haber llamado a una tool que efectivamente escriba a disco.
7. **`inspeccionar_carpeta(tarea_id)`** — busca la tarea, valida que su `ruta_contexto` esté dentro de `CARPETA_AUTORIZADA` (vía `_validar_ruta`), y lista los archivos con extensión admitida que encuentra ahí. Es el paso previo obligatorio antes de poder buscar contenido.
8. **`buscar_en_documentos(tarea_id, consulta)`** — recorre todos los archivos admitidos de la carpeta de la tarea, extrae su texto con `_extraer_texto_archivo`, y compara línea por línea (tras `_normalizar`) si contienen el término buscado. Cada coincidencia se reporta como `[nombre_archivo] línea`, limitando la salida a las primeras 10 coincidencias. Es búsqueda léxica literal, no semántica: no encuentra sinónimos ni relaciona conceptos, solo substrings normalizados.

### Prompt del sistema y creación del agente

`PROMPT_SISTEMA` define el rol del agente ("agente personal de planificación académica") y, sobre todo, impone un **flujo recomendado** de 6 pasos que enlaza las tools en el orden esperado (consultar → calcular prioridad → generar plan si hay tiempo disponible → inspeccionar/buscar si se va a empezar una tarea → actualizar estado / agregar tarea → guardar plan detallado solo si el usuario lo pide explícitamente). También fija dos reglas duras: nunca inventar datos que debieran salir de una tool, y respetar el sandboxing de carpetas.

`resolver_modelo()` lee la variable de entorno `AGENT_MODEL` (por defecto `"anthropic"`) y devuelve:
- si es `"gemma-lmstudio"`: una instancia de `ChatOpenAI` (de `langchain_openai`) apuntando a un servidor local compatible con la API de OpenAI expuesto por LM Studio (`base_url` configurable, típicamente la IP del host Windows vista desde WSL), con `api_key="lm-studio"` (valor dummy que LM Studio ignora) y `temperature=0.3`;
- si es `"anthropic"`: **no** instancia un objeto de modelo directamente, sino que devuelve el string `"anthropic:<nombre-modelo>"` — `create_agent` de LangChain acepta esta sintaxis de "identificador de proveedor" y resuelve el modelo internamente;
- cualquier otro valor lanza `ValueError`.

`create_agent(model=resolver_modelo(), system_prompt=PROMPT_SISTEMA, tools=[...8 tools...])` construye el agente ReAct completo: LangChain se encarga internamente del bucle de razonar → decidir si llamar una tool → ejecutar la tool → incorporar su resultado → repetir hasta producir una respuesta final. El objeto `agent` queda instanciado a nivel de módulo (se crea una sola vez al importar/ejecutar el archivo).

### Loop de chat (`iniciar_chat`)

Bucle infinito de consola: imprime una cabecera con el nombre del modelo activo, lee una línea de `input()`, y si el usuario escribe `salir`/`exit`/`quit` termina. Cada turno de usuario se agrega a una lista `historial` (formato `{"role": ..., "content": ...}`, el mismo formato que consumen los modelos de chat) y se invoca `agent.invoke({"messages": historial})`, pasando **todo el historial acumulado** en cada llamada — así el agente tiene memoria de la conversación completa dentro de esa ejecución del programa (no persiste entre ejecuciones). La respuesta final se extrae del último mensaje con `extraer_texto` y también se añade al historial antes de imprimirse. `KeyboardInterrupt` (Ctrl+C) termina limpiamente, y cualquier otra excepción se atrapa para que un error de una tool o del modelo no tumbe la sesión completa, mostrando el detalle técnico pero sin perder el historial acumulado. Al final del archivo, el bloque `if __name__ == "__main__"` valida que exista `ANTHROPIC_API_KEY` cuando el backend es Anthropic, antes de arrancar el chat.

---

## Versión 2 — Tarea_Agente_Personal_v2_ActividadesDiarias (Sesión 12)

Archivos: `agente_planificacion_actividades.py` y `autenticar_calendario.py`

### Qué cambia respecto a v1

- **Alcance**: deja de ser solo "académico". El archivo de datos pasa de `tareas.json` a `actividades.json`, y cada actividad gana un campo `tipo` (`"academica"` o `"personal"`) — `curso` ahora es opcional (`curso=""` por defecto) porque una actividad personal no tiene curso asociado.
- **Renombrado consistente**: `tarea`→`actividad` en todo el código (`_cargar_tareas`→`_cargar_actividades`, `_buscar_tarea`→`_buscar_actividad`, `consultar_tareas`→`consultar_actividades`, `agregar_tarea`→`agregar_actividad`, etc.), reflejando el cambio de dominio.
- **Nueva integración externa**: Google Calendar vía OAuth2, con scope mínimo `calendar.events` (solo eventos, ni siquiera acceso a la lista de calendarios) — de solo lectura para eventos existentes, y con permiso de escritura limitado a **crear** eventos nuevos, nunca editar ni borrar los que ya existían.
- **`generar_plan` cambia de firma y de lógica**: en v1 recibía `minutos_disponibles` (un número) y llenaba un bloque continuo de tiempo ignorando cualquier compromiso externo. En v2 recibe `(fecha, hora_inicio, hora_fin)`, consulta primero los eventos reales de Google Calendar de ese día, calcula los huecos libres entre ellos, y solo asigna actividades pendientes dentro de esos huecos — nunca sobre un bloque ya ocupado. El reporte Markdown generado también cambia: ya no es una tabla simple de "tarea/duración/prioridad" sino una línea de tiempo (`Horario | Bloque`) que intercala bloques `Ocupado: <evento>` con las actividades asignadas.
- **Dos tools nuevas**: `agendar_actividad` (crea un evento en Calendar) y `consultar_calendario` (lista los eventos del día). Con esto v2 pasa de 8 a 9 tools.
- **`guardar_plan_detallado` desaparece**: v2 no la incluye en la lista de tools ni en el archivo (a diferencia de v1, que sí la tiene).
- **Prompt del sistema**: se reescribe el flujo recomendado para intercalar la consulta de calendario antes de proponer horarios, y se añade una regla explícita de que la única escritura permitida sobre el calendario es crear eventos nuevos, nunca editar/borrar.
- **Estilo de código**: v2 organiza el archivo en secciones numeradas con comentarios de bloque (`# 1. CONFIGURACION`, `# 2. HELPERS COMPARTIDOS`, ... hasta `# 10. EJECUCION`) y usa más líneas en blanco entre sentencias dentro de cada función; v1 es más compacto. Funcionalmente ambos archivos comparten casi textualmente `_normalizar`, `_validar_ruta`, `_puntaje_urgencia`, `_extraer_texto_archivo` y `extraer_texto`.

### Integración con Google Calendar

- **`_obtener_servicio_calendario()`**: implementa el flujo estándar de OAuth2 de Google para aplicaciones instaladas. Si existe `token.json`, carga las credenciales desde ahí; si están vencidas pero tienen `refresh_token`, las renueva automáticamente sin intervención del usuario; si no hay token válido ni forma de renovarlo, arranca un flujo interactivo (`InstalledAppFlow.from_client_secrets_file` + `flow.run_local_server(port=0)`, que abre el navegador y levanta un servidor local temporal para recibir el código de autorización) usando `credentials.json` como secreto de cliente. Al terminar, siempre persiste las credenciales vigentes en `token.json` y construye el cliente de la API (`googleapiclient.discovery.build("calendar", "v3", ...)`). Si `credentials.json` no existe, lanza `FileNotFoundError` con instrucciones hacia `CONFIGURAR_GOOGLE_CALENDAR.md`.
- **`_obtener_eventos_dia(fecha)`**: dada una fecha (o el día de hoy si viene vacía), arma los límites de inicio y fin del día en la zona horaria local (`datetime.now().astimezone().tzinfo`) y llama a `servicio.events().list(...)` con `singleEvents=True` (expande eventos recurrentes en instancias individuales) y `orderBy="startTime"`. Devuelve una lista simplificada de diccionarios `{resumen, inicio, fin}`, tomando `dateTime` cuando el evento tiene hora puntual o `date` cuando es de todo el día.
- **`_calcular_huecos_libres(hora_inicio, hora_fin, eventos)`**: convierte horas `HH:MM` a minutos desde medianoche (con `_hhmm_a_minutos`), descarta los eventos de todo el día (no tienen una hora puntual que bloquee un rango), ordena los eventos con hora por su inicio, y recorre esa lista con un "cursor" de tiempo: cada vez que hay un espacio entre el cursor y el siguiente evento ocupado, ese espacio es un hueco libre; al final, si queda tiempo entre el cursor y `hora_fin`, también se agrega como hueco. Es el mismo patrón algorítmico usado para calcular huecos en calendarios de reuniones (barrido de intervalos ordenados).
- **`_crear_evento(fecha, hora_inicio, hora_fin, resumen, descripcion)`**: arma los `datetime` de inicio/fin combinando fecha y hora en la zona horaria local, y llama a `servicio.events().insert(calendarId="primary", body={...})`. Es la única función del archivo que escribe en el calendario del usuario, y solo inserta (nunca actualiza ni borra un evento existente).
- **`agendar_actividad(fecha, hora_inicio, hora_fin, resumen, descripcion="")`** (tool): capa fina sobre `_crear_evento` que atrapa errores (credenciales faltantes, fallas de red o de la API) y los convierte en mensajes legibles para el modelo, en vez de dejar que la excepción se propague. Su docstring es explícita en que es "la ÚNICA acción de escritura permitida" y que el modelo debe confirmar fecha/hora/resumen con el usuario y revisar disponibilidad con `consultar_calendario` antes de invocarla.
- **`consultar_calendario(fecha="")`** (tool): capa fina sobre `_obtener_eventos_dia` que formatea los eventos como lista de texto (`HH:MM-HH:MM` para eventos con hora, `"todo el dia"` para los de día completo). Es de solo lectura y el prompt del sistema instruye a llamarla antes de proponer cualquier horario nuevo.

### `autenticar_calendario.py`

Es un script de un solo uso, separado del agente principal, cuyo único propósito es completar el login interactivo de OAuth2 y generar `token.json` una primera vez. Existe como archivo aparte por una razón muy concreta documentada en su docstring: el agente principal corre normalmente en WSL (Subsistema de Windows para Linux), pero el flujo `flow.run_local_server(port=0)` de Google necesita abrir un navegador y recibir la respuesta OAuth en `localhost` — y hay un bug conocido de reenvío (*forwarding*) de `localhost` entre WSL2 y Windows que hace fallar ese flujo si se ejecuta dentro de WSL. Por eso este script debe ejecutarse una vez con el intérprete de Python de **Windows** (no el de WSL): genera `token.json` en la misma carpeta, y una vez creado, el agente principal (corriendo en WSL con normalidad) puede reutilizarlo — y renovarlo automáticamente vía `refresh_token` — sin volver a pasar por el navegador. El script también advierte que si existía un `token.json` de un scope anterior (de solo lectura), hay que borrarlo antes de correrlo, porque Google exige un nuevo consentimiento cuando cambia el alcance de permisos solicitado.

---

## Versión 3 — Tarea_Agente_Personal_v3_Web (Sesión 12)

### Resumen

Es la primera versión web del agente: envuelve al agente CLI de v2 (`agente_planificacion_actividades.py`, con Google Calendar) en una aplicación full-stack sin autenticación (un solo usuario implícito). El backend está construido con FastAPI y el frontend con React + Vite. La decisión de diseño clave está documentada en el propio código (`backend/app/config.py`): v2 es "la única fuente de verdad" y **no se duplica su lógica** — el backend importa el módulo `agente_planificacion_actividades.py` de v2 directamente vía `sys.path`, y cada endpoint HTTP simplemente llama a las funciones y *tools* de LangChain ya existentes en v2 (`.invoke()`, `.ainvoke()`) o lee sus estructuras de datos (`actividades.json`, `CARPETA_PLANES`, `CARPETA_AUTORIZADA`). Todas las *tools* del agente, incluida `buscar_en_documentos` (búsqueda literal por palabras clave sobre el texto extraído de los archivos, sin *embeddings* ni RAG), se heredan sin cambios desde v2. El frontend consume esa API mediante `fetch` y organiza la interfaz en 7 páginas con una barra lateral de navegación y tema claro/oscuro.

### Backend — estructura FastAPI

#### config.py y deps.py

`config.py` es el punto de arranque de todo el backend: calcula `V2_DIR` como la carpeta hermana `Tarea_Agente_Personal_v2_ActividadesDiarias` (dos niveles arriba de `config.py`, es decir la raíz de v3, y su padre), verifica que exista `agente_planificacion_actividades.py` ahí (si no, lanza `RuntimeError` explicando la dependencia), y hace `load_dotenv(V2_DIR / ".env")` **antes** de importar el módulo de v2. El comentario del archivo explica por qué el orden es crítico: v2 llama `load_dotenv()` a secas dentro de su propio código, lo cual depende del directorio de trabajo del proceso que lo importa; al cargar aquí primero el `.env` correcto, cuando el `load_dotenv()` interno de v2 se ejecute como no-op (por `override=False`, comportamiento por defecto de `python-dotenv`), las variables de entorno ya están en `os.environ`. Luego hace `sys.path.insert(0, str(V2_DIR))` e importa el módulo como `v2mod`. También define `FRONTEND_ORIGINS` (los orígenes de Vite en `localhost:5173`).

`deps.py` es un envoltorio trivial de una sola función, `get_v2()`, que retorna el `v2mod` ya cargado por `config.py`. Se usa como dependencia de FastAPI (`Depends(get_v2)`) en todos los routers, de modo que cada endpoint recibe el módulo de v2 como parámetro `v2` sin tener que importarlo directamente.

#### main.py

Crea la instancia `FastAPI` con un `lifespan` (contexto de arranque/apagado) que solo hace una comprobación no bloqueante: si `v2mod.RUTA_CREDENCIALES` no existe, imprime un aviso en consola (las *tools* de Calendar fallarán hasta que se configure `credentials.json`), pero no impide que la app arranque. Se añade `CORSMiddleware` permitiendo los orígenes definidos en `FRONTEND_ORIGINS` con todos los métodos y cabeceras. Finalmente incluye los 6 routers (`health`, `activities`, `calendar`, `plans`, `files`, `chat`) todos bajo el prefijo `/api`. El bloque `if __name__ == "__main__"` permite levantar el servidor con `uvicorn` directamente (`host=127.0.0.1`, `port=8000`, `reload=True`).

#### Modelos Pydantic (models/)

- **activities.py**: `ActividadIn` (payload para crear actividad: nombre, tipo, fecha límite, duración, prioridad, curso, ruta de contexto, entregable), `ActividadOut` (misma info más campos calculados: `puntaje_urgencia`, `dias_restantes`, `estado`, `id`), `EstadoUpdateIn` (un único campo `nuevo_estado` restringido a `pendiente`/`iniciada`/`completada`) y `MensajeOut` (respuesta genérica de un solo campo `mensaje`, usada por varios endpoints de escritura).
- **calendar.py**: `EventoOut` (resumen, inicio, fin — lo que devuelve Google Calendar) y `EventoIn` (payload para crear evento: fecha, hora inicio/fin, resumen, descripción).
- **chat.py**: `ChatMessage` (role `user`/`assistant` + contenido), `ChatRequest` (mensaje nuevo + historial), `ChatResponse` (respuesta del agente + historial actualizado).
- **files.py**: `FileEntry` (nombre, si es carpeta, ruta relativa, si la extensión está admitida) y `FileBrowseOut` (ruta actual + lista de entradas) — soportan el explorador de materiales.
- **plans.py**: `PlanGenerateIn` (fecha, hora inicio/fin para generar un plan), `PlanListItem` (nombre de archivo, fecha de generación, URL de descarga) y `PlanContenidoOut` (nombre de archivo + contenido Markdown).

#### Routers (routers/)

Cada router recibe `v2=Depends(get_v2)` y se apoya en las funciones internas o *tools* `@tool` de v2. La distinción central que pide documentar el enunciado es: **lecturas** que acceden directo a las estructuras de datos de v2 (funciones privadas `_algo`, atributos como `CARPETA_PLANES`) vs. **escrituras** que invocan las mismas *tools* de LangChain que usa el agente conversacional, vía `.invoke(dict_con_los_argumentos)`.

- **health.py** — `GET /api/health`: no toca ninguna *tool*; devuelve un diccionario de diagnóstico (`agent_model`, si existen `credenciales_calendar` y `token_calendar`) leyendo atributos de `v2mod` directamente.

- **activities.py** (prefix `/activities`):
  - `GET ""` (`listar_actividades`): **lectura directa** — llama `v2._cargar_actividades()` (lee `actividades.json`), y para cada actividad calcula `dias_restantes` con `v2.date` y añade `puntaje_urgencia` llamando a `v2._puntaje_urgencia(a)`; ordena la lista por urgencia descendente antes de devolverla. No usa ninguna *tool* del agente.
  - `POST ""` (`crear_actividad`): **escritura vía tool** — llama `v2.agregar_actividad.invoke(datos.model_dump())`, la misma *tool* `@tool` que usaría el agente conversacional si el usuario le pidiera "agrega esta actividad".
  - `PATCH "/{actividad_id}/estado"` (`actualizar_estado`): **escritura vía tool** — `v2.actualizar_estado.invoke({...})`; si el mensaje de retorno empieza con "No existe" (actividad inexistente), lo traduce a `HTTPException 404`.

- **calendar.py** (prefix `/calendar`):
  - `GET "/events"` (`listar_eventos`): **lectura directa** contra la API real de Google Calendar vía `v2._obtener_eventos_dia(fecha)`; mapea `FileNotFoundError` (sin credenciales) a 503 y cualquier otro error a 502.
  - `POST "/events"` (`crear_evento`): **escritura vía tool** — `v2.agendar_actividad.invoke(datos.model_dump())`, crea un evento real en Google Calendar (distinto de registrar una actividad pendiente, como aclara la UI).

- **chat.py** (prefix `/chat`): `POST ""` (`chat`, async) es el único endpoint que invoca el **agente completo** (no una tool suelta): arma la lista de mensajes (`historial` + mensaje nuevo) y llama `await v2.agent.ainvoke({"messages": historial})`. El agente de LangChain puede razonar en varios pasos (texto → *tool call* → más texto → otra *tool call* → ...) antes de terminar el turno; el código toma **todos** los mensajes nuevos generados en ese turno (`resultado["messages"][len(historial):]`), filtra los de tipo `"ai"` con texto no vacío usando `v2.extraer_texto(m.content)`, y los concatena con `\n\n` para no perder el razonamiento intermedio (si solo tomara el último mensaje, perdería contexto). Devuelve la respuesta concatenada más el historial actualizado.

- **files.py** (prefix `/files`): expone `GET "/browse"` (`explorar`) para navegar `v2.CARPETA_AUTORIZADA`. Define una función auxiliar propia, `_resolver_dentro_de_carpeta_autorizada`, que **no reutiliza** `v2._validar_ruta` porque esa función de v2 resuelve rutas relativas al archivo de v2 (pensada para el campo `ruta_contexto` de actividades, con prefijo `"materiales/"`), mientras que este endpoint ancla las rutas a `CARPETA_AUTORIZADA` directamente (la convención que usa el resto del router). Valida que la ruta resuelta quede dentro de la carpeta autorizada (o sea igual a ella) antes de listar, devolviendo 403 si no. Lista cada entrada con nombre, si es carpeta, ruta relativa y si la extensión está en `v2.EXTENSIONES_ADMITIDAS`.

- **plans.py** (prefix `/plans`): tiene una función auxiliar `_validar_nombre_plan` que evita *path traversal* (solo acepta nombres de archivo simples dentro de `v2.CARPETA_PLANES` con extensión `.md`).
  - `POST "/generate"` (`generar_plan`): **escritura vía tool** — `v2.generar_plan.invoke(datos.model_dump())`.
  - `GET ""` (`listar_planes`): **lectura directa** — recorre `v2.CARPETA_PLANES.glob("*.md")` ordenados por fecha de modificación descendente, construyendo también la URL de descarga.
  - `GET "/{nombre_archivo}"` (`obtener_plan`): **lectura directa** del contenido Markdown de un plan.
  - `GET "/{nombre_archivo}/download"` (`descargar_plan`): devuelve el archivo como `FileResponse` para descarga directa.

### Frontend — estructura React

#### api/client.js

Un módulo único con una función interna `solicitar(ruta, opciones)` que hace `fetch` contra `${BASE_URL}/api${ruta}` (donde `BASE_URL` sale de `VITE_API_BASE_URL` o por defecto `http://127.0.0.1:8000`), fija `Content-Type: application/json`, parsea la respuesta como JSON (con `.catch(() => ({}))` para no romper si el cuerpo está vacío) y lanza un `Error` con el campo `detail` de FastAPI si `response.ok` es falso. Sobre esa base exporta una función por endpoint: `getHealth`, `getActivities`, `createActivity`, `updateEstado`, `getEvents`, `createEvent`, `generatePlan`, `listPlans`, `getPlan`, `downloadPlanUrl` (construye la URL, no hace `fetch`), `browseFiles`, `sendChat`. Es la única capa que conoce las rutas HTTP; todas las páginas importan de aquí.

#### App.jsx, main.jsx

`main.jsx` monta la app en modo `StrictMode`, envuelve todo en `BrowserRouter` (React Router) e importa `global.css` antes de renderizar `<App />`. `App.jsx` define el layout general (`app-shell` con `NavBar` a la izquierda + `main.app-content` a la derecha, y `Footer` fijo fuera del shell) y las 7 rutas de la aplicación con `react-router-dom`: `/` (Dashboard), `/actividades`, `/actividades/nueva`, `/calendario`, `/planes`, `/materiales`, `/chat`.

#### Componentes reutilizables

- **ActivityTable.jsx**: tabla de actividades (nombre, tipo, curso, fecha límite + días restantes, prioridad, puntaje de urgencia, estado, botón de acción). Si `onCambiarEstado` está presente, muestra un botón "Marcar `<siguiente estado>`" que rota `pendiente → iniciada → completada → pendiente` según el mapa `SIGUIENTE_ESTADO`. Muestra un estado vacío si no hay actividades.
- **Banner.jsx**: mensaje de estado (error/success/info) con ícono de `lucide-react`; no renderiza nada si `children` está vacío.
- **ChatBubble.jsx**: burbuja de mensaje de chat, con avatar y alineación distinta según `role` (usuario a la derecha, agente a la izquierda).
- **FileBrowser.jsx**: explorador de `CARPETA_AUTORIZADA` vía `browseFiles`. Tiene *breadcrumbs* de navegación y, si recibe la prop `onSelect`, agrega un botón "Elegir esta carpeta" (usado como selector embebido en `NewActivityPage`); si no, es solo navegación de lectura (usado en `MaterialsPage`).
- **Footer.jsx**: pie de página fijo con la firma "Elaborado por @Sherlock".
- **NavBar.jsx**: barra lateral colapsable (persistida en `localStorage` bajo `sidebar-colapsado`) con los 7 enlaces de navegación (`ENLACES`, cada uno con ícono de `lucide-react`) y un botón de cambio de tema que usa el hook `useTheme`.
- **PlanCard.jsx**: tarjeta de un plan generado, con botón de mostrar/ocultar *preview* (Markdown renderizado con `react-markdown`) y enlace de descarga (`downloadPlanUrl`).
- **Spinner.jsx**: indicador de carga simple con etiqueta opcional.
- **UrgencyBadge.jsx**: exporta `BadgePrioridad` y `BadgeEstado`, dos *badges* de color según diccionarios (`COLOR_PRIORIDAD`, `COLOR_ESTADO`).

#### Páginas

- **DashboardPage.jsx**: carga actividades (`getActivities`), filtra las que **no** están `completada` y las muestra en `ActivityTable` ordenadas por urgencia (el orden ya viene calculado del backend); permite cambiar estado inline.
- **ActivitiesPage.jsx**: igual que el Dashboard pero sin filtrar por estado (muestra todas las actividades) y con un botón "Nueva actividad" que enlaza a `/actividades/nueva`.
- **NewActivityPage.jsx**: formulario controlado para crear una actividad (`createActivity`). Incluye un selector de carpeta de materiales que despliega `FileBrowser` en modo selector (`onSelect` rellena `ruta_contexto`). Al éxito, muestra el mensaje devuelto por la *tool* y navega a `/actividades` tras 800 ms.
- **CalendarPage.jsx**: dos secciones. Arriba, lista de eventos de Google Calendar del día seleccionado (`getEvents`, recarga al cambiar `fecha`). Abajo, un formulario para agendar un evento real (`createEvent`) — aclara explícitamente que esto es distinto de registrar una actividad pendiente.
- **PlansPage.jsx**: formulario para generar un plan (fecha + hora inicio/fin) que llama `generatePlan` y recarga el historial de planes (`listPlans`); el historial se renderiza con `PlanCard`, con *previews* individuales cacheadas en el estado `previews` (se piden con `getPlan` solo la primera vez que se abren).
- **MaterialsPage.jsx**: página mínima que solo monta `FileBrowser` en modo navegación pura (sin `onSelect`).
- **ChatPage.jsx**: interfaz de chat con historial en estado local; al enviar, agrega el mensaje del usuario de inmediato, llama `sendChat(mensaje, historial)` y reemplaza el historial completo con el que devuelve el backend (que ya incluye la respuesta del agente). Muestra una burbuja "Pensando…" mientras `cargando` es verdadero.

#### Estilos (global.css)

Un único archivo CSS global basado en *design tokens* (variables CSS en `:root`): colores de fondo/superficie/texto/borde, color primario, colores de estado (danger/success), radios de borde, espaciados (`--space-1`…`--space-6`), ancho de la barra lateral (expandida/colapsada) y alto del footer. El tema oscuro se activa sobrescribiendo esas mismas variables bajo el selector `:root[data-theme="dark"]` (el atributo `data-theme` lo controla `useTheme.js` escribiéndolo en `document.documentElement.dataset.theme`). El resto del archivo son reglas por sección: layout general (`app-shell`, `sidebar`, `app-content`), *banners*, tarjetas/tabla/*badges*, botones, formularios, explorador de archivos, lista de eventos, tarjetas de plan, footer fijo y la ventana de chat con sus burbujas — todo reutilizando las mismas variables de espaciado y color para mantener consistencia visual entre páginas.

### Flujo de datos end-to-end (ejemplo)

Tomando el ejemplo de "generar un plan": en `PlansPage.jsx` el usuario completa el formulario (fecha, hora inicio, hora fin) y hace clic en "Generar plan". El *handler* `generar` llama a `generatePlan(form)` de `api/client.js`, que hace `POST /api/plans/generate` con el JSON `{fecha, hora_inicio, hora_fin}`. FastAPI enruta la petición al router `plans.py`, la valida contra el modelo `PlanGenerateIn`, y el endpoint `generar_plan` ejecuta `v2.generar_plan.invoke(datos.model_dump())` — la *tool* `@tool generar_plan` definida en `agente_planificacion_actividades.py` de v2, la misma que usaría el agente conversacional. Esa *tool* (código de v2, no reescrito en v3) lee `actividades.json`, calcula huecos libres contra los eventos reales de Google Calendar del día pedido, arma el plan y lo escribe como un archivo Markdown en `CARPETA_PLANES`, devolviendo un mensaje de confirmación en texto. El router envuelve ese mensaje en `{"mensaje": ...}` (modelo `MensajeOut` implícito) y FastAPI lo serializa como respuesta JSON. De vuelta en el frontend, `PlansPage` recibe `res.mensaje`, lo muestra en un `Banner` de éxito y vuelve a llamar `cargarPlanes()` (`GET /api/plans`), que lee de nuevo `CARPETA_PLANES` (ahora con el archivo nuevo) y repinta la lista con `PlanCard`; si el usuario pulsa "Ver preview" en la tarjeta nueva, se dispara `GET /api/plans/{nombre_archivo}` para traer el contenido Markdown y renderizarlo con `react-markdown`.

---

## Versión 4 — AgentePersonal-Web (proyecto standalone con login + MySQL)

### Resumen

`AgentePersonal-Web` es la evolución de v3, pero reescrita como proyecto **100% autocontenido**: no importa nada de las carpetas `Sesion12`/`Sesion13` del curso, sino que trae su propia copia adaptada del agente (`backend/app/agente.py`) y su propia configuración (`backend/app/config.py`), de modo que la carpeta completa se puede mover a otro repositorio o máquina sin arrastrar dependencias externas. Sobre v3 agrega tres cosas nuevas: **login real** (registro/inicio de sesión con contraseña hasheada en bcrypt y sesión mantenida con un JWT en una cookie `httpOnly`), **cuentas de usuario en MySQL** (tabla `usuarios`, algo que ninguna versión anterior tenía) y, como consecuencia directa, **multi-usuario real**: las actividades dejan de vivir en un JSON compartido de un solo usuario y pasan a una tabla `actividades` en MySQL donde cada fila lleva un `usuario_id`, de forma que cada cuenta ve y modifica únicamente sus propias actividades. Google Calendar sigue siendo compartido/global (todavía no hay un Calendar por usuario) y la búsqueda documental sigue siendo la de v1/v2 por palabra clave, sin RAG ni embeddings.

### Modelo de datos (db_models.py)

`backend/app/db_models.py` define dos modelos SQLAlchemy sobre la `Base` declarativa de `db.py`:

- **`Usuario`** (tabla `usuarios`): `id`, `username` y `email` únicos e indexados, `password_hash` (nunca la contraseña en claro), `nombre_completo`, `avatar_path` (ruta pública del avatar subido) y `google_refresh_token` (columna `Text`, nullable, comentada como *placeholder* para el día en que cada usuario conecte su propio Google Calendar vía OAuth "Web application" — hoy no se usa, Calendar sigue siendo global). Tiene timestamps `creado_en`/`actualizado_en` con `server_default=func.now()`.
- **`Actividad`** (tabla `actividades`): los mismos campos que en v3 (`nombre`, `tipo` enum `academica`/`personal`, `curso`, `fecha_limite`, `duracion_estimada_minutos`, `prioridad` enum `alta`/`media`/`baja`, `estado` enum `pendiente`/`iniciada`/`completada`, `ruta_contexto`, `entregable`) más una columna nueva y central: **`usuario_id`**, `ForeignKey("usuarios.id", ondelete="CASCADE")`, indexada y `nullable=False`.

La relación `Usuario.actividades` usa `cascade="all, delete-orphan"`: si se borra un usuario, sus actividades se borran con él a nivel de ORM (y `ondelete="CASCADE"` lo refuerza también a nivel de base de datos). El motivo de que `usuario_id` exista en cada actividad es el aislamiento multi-usuario: sin esa columna, todas las cuentas verían las actividades de todas las demás. Por eso, como se ve más abajo, cada consulta a `Actividad` en el agente y en los routers filtra siempre por `usuario_id` además del `id` de la fila.

### Autenticación (auth.py, routers/auth.py)

`backend/app/auth.py` concentra las primitivas de seguridad:

- `hash_password` / `verify_password`: usan `bcrypt.hashpw`/`bcrypt.checkpw` sobre la contraseña codificada en UTF-8; nunca se guarda ni compara la contraseña en claro.
- `create_access_token(usuario_id)`: genera un JWT con `jwt.encode`, payload `{"sub": str(usuario_id), "exp": ...}`, firmado con `JWT_SECRET_KEY`/`JWT_ALGORITHM` (HS256 por defecto) y expiración `JWT_EXPIRE_MINUTES` (7 días por defecto, `10080` minutos).
- `decode_access_token(token)`: decodifica y valida el JWT; si falla (firma inválida, expirado, payload corrupto) devuelve `None` en vez de propagar la excepción, para que el llamador solo tenga que comprobar `None`.
- `get_current_user(request, db)`: es la **dependency** de FastAPI que protege casi todos los endpoints. Lee la cookie `COOKIE_NAME` (`access_token`) de la request, la decodifica a un `usuario_id`, busca el `Usuario` en la base y lanza `HTTPException(401)` si falta la cookie, el token es inválido/expirado o el usuario ya no existe. Se usa como `Depends(get_current_user)` en el resto de routers.

`backend/app/routers/auth.py` expone el flujo completo:

- `POST /auth/register`: valida que `username` y `email` no estén ya en uso (409 si lo están), crea el `Usuario` con `hash_password`, hace commit, y **setea la cookie de sesión inmediatamente** (`_setear_cookie`) — o sea, registrarse deja al usuario ya autenticado, sin login aparte.
- `POST /auth/login`: busca el usuario por `username` **o** `email` (operador `|` de SQLAlchemy sobre el filtro), verifica la contraseña con `verify_password` y devuelve 401 genérico ("Usuario o contraseña inválidos") si falla, sin distinguir si el problema fue el usuario o la contraseña (evita filtrar qué cuentas existen).
- `POST /auth/logout`: borra la cookie con `response.delete_cookie`.
- `GET /auth/me`: devuelve el usuario actual resuelto por `get_current_user`; el frontend lo usa para restaurar sesión al recargar la página.
- `POST /auth/avatar`: sube un archivo (`UploadFile`), valida el `content_type` contra `EXTENSIONES_AVATAR` (solo PNG/JPEG/WEBP), borra cualquier avatar previo del mismo usuario (`AVATARS_DIR.glob(f"{usuario.id}.*")`) y guarda el nuevo como `{usuario.id}.{extension}`, actualizando `avatar_path` en la base. La carpeta se sirve como archivos estáticos montados en `/uploads` desde `main.py`.

La cookie se crea con `httponly=True` (no accesible desde JavaScript, mitiga robo de token por XSS), `samesite="lax"` y `secure=False` (con un comentario explícito de que debe pasar a `True` si el proyecto se despliega alguna vez con HTTPS), y `max_age` de 7 días.

### El agente adaptado (agente.py)

`backend/app/agente.py` es una copia adaptada de `agente_planificacion_actividades.py` (v2), documentada así en su propio docstring: la diferencia clave es que las actividades ya no viven en un JSON de un solo usuario, sino en la tabla `actividades` de MySQL, con cada fila asociada a un `usuario_id`.

**El problema que resuelve el `ContextVar`:** las tools de LangChain se definen con `@tool` y su firma solo puede incluir los parámetros que el modelo va a rellenar (los que ve en el schema); no hay forma nativa de pasarles un argumento oculto como "para qué usuario está corriendo este turno". La solución ingenua sería una variable global (`usuario_actual_id = None`) que el router setea antes de invocar al agente — pero eso rompe bajo concurrencia: si dos usuarios distintos mandan un mensaje de chat casi al mismo tiempo, sus dos requests async pueden entrelazarse en el mismo proceso y una pisaría el valor de la otra, filtrando las actividades de un usuario a otro. Por eso se usa un `contextvars.ContextVar`:

```python
_usuario_id_ctx: ContextVar[int | None] = ContextVar("usuario_id_ctx", default=None)

def set_usuario_actual(usuario_id: int) -> None:
    _usuario_id_ctx.set(usuario_id)

def _usuario_actual() -> int:
    usuario_id = _usuario_id_ctx.get()
    if usuario_id is None:
        raise RuntimeError("set_usuario_actual() no fue llamado antes de invocar al agente.")
    return usuario_id
```

Un `ContextVar` aísla su valor por cada tarea asíncrona/contexto de ejecución (cada request de FastAPI corre en su propio contexto), así que dos requests concurrentes de usuarios distintos no se pisan entre sí, cosa que una variable global compartida sí haría. El router llama a `agente.set_usuario_actual(usuario.id)` (con el `usuario.id` que vino de `get_current_user`, es decir, del JWT verificado) justo antes de invocar cualquier tool o al agente completo, y las tools internamente llaman a `_usuario_actual()` para obtener ese id.

**El fix de IDOR en cada tool:** las siete tools que tocan la tabla `Actividad` (`consultar_actividades`, `agregar_actividad`, `calcular_prioridad`, `actualizar_estado`, `editar_actividad`, `eliminar_actividad`, y las tres de documentos que resuelven una actividad por id: `inspeccionar_carpeta`, `buscar_en_documentos`, `leer_documento`) nunca hacen `filter(Actividad.id == actividad_id)` solo — siempre combinan `Actividad.id == actividad_id` **con** `Actividad.usuario_id == _usuario_actual()` en el mismo `.filter(...)`, por ejemplo:

```python
actividad = db.query(Actividad).filter(
    Actividad.id == actividad_id, Actividad.usuario_id == _usuario_actual(),
).first()
```

Esto es exactamente lo que evita un IDOR (*Insecure Direct Object Reference*): si un usuario A conoce o adivina el `id` numérico de una actividad del usuario B (los ids son autoincrementales y por lo tanto predecibles), un filtro que solo comprobara `Actividad.id == actividad_id` le permitiría leer, editar o borrar esa actividad ajena con solo pasar el id correcto. Al exigir también `usuario_id == _usuario_actual()`, la consulta simplemente no encuentra la fila (`actividad is None` → "No existe una actividad con id {id}") si no es del usuario que hace la petición, sin filtrar siquiera si esa actividad existe para otra cuenta.

**Las 13 tools del agente**, agrupadas como en v2 pero con la capa de persistencia distinta:

- *Google Calendar (compartido/global, sin cambios de fondo respecto a v2)*: `agendar_actividad` (única acción de escritura permitida: crea un evento nuevo, nunca edita/borra uno existente), `consultar_calendario` (lista eventos de un día, solo lectura). Se apoyan en helpers privados `_obtener_servicio_calendario` (OAuth2 con `RUTA_CREDENCIALES`/`RUTA_TOKEN`), `_obtener_eventos_dia`, `_calcular_huecos_libres` y `_crear_evento`.
- *Gestión de actividades (MySQL, por `usuario_id`)*: `consultar_actividades`, `agregar_actividad`, `calcular_prioridad` (usa el helper `_puntaje_urgencia`, la misma fórmula determinista `peso_prioridad * 100 / (dias_restantes + 1)` de v1/v2), `actualizar_estado`, `editar_actividad` (edición parcial: solo cambia los campos no `None`), `eliminar_actividad`.
- *Generar plan*: `generar_plan` combina huecos libres del calendario (vía `_calcular_huecos_libres`) con las actividades pendientes del usuario ordenadas por urgencia, y escribe un reporte Markdown en `CARPETA_PLANES`.
- *Consulta documental sin RAG (compartida/global)*: `inspeccionar_carpeta`, `buscar_en_documentos` (coincidencia literal de texto tras normalizar tildes/mayúsculas con `_normalizar`, sin embeddings ni vector store — el mismo enfoque de v1/v2, no el de la Sesión 13 de RAG) y `leer_documento` (lee el archivo completo, truncado a 6000 caracteres). Todas resuelven primero la actividad por `id` + `usuario_id` para obtener su `ruta_contexto`, y luego validan esa ruta contra `CARPETA_AUTORIZADA` con `_validar_ruta` para evitar path traversal.
- *Guardar plan*: `guardar_plan` persiste como Markdown un texto que el propio modelo ya redactó en la conversación (por ejemplo el plan de una sola actividad), distinto de `generar_plan` que arma el plan completo del día respetando el calendario real.

El agente se construye con `create_agent` de `langchain.agents`, con un `PROMPT_SISTEMA` que le da el flujo recomendado paso a paso (consultar actividades → calcular prioridad → consultar calendario antes de proponer horario → generar plan → actualizar/editar/eliminar actividades → agendar solo si se confirma → guardar plan solo si el usuario lo pide explícitamente) y reglas explícitas (no inventar horarios/prioridades/contenido de documentos, no salirse de `CARPETA_AUTORIZADA`, la única escritura en Calendar es crear eventos nuevos, nunca decir que se hizo algo sin haber llamado a la tool correspondiente). El modelo se resuelve en `resolver_modelo()` según `AGENT_MODEL`: `"anthropic"` usa el string `"anthropic:{modelo}"` que `create_agent` sabe interpretar, o `"gemma-lmstudio"` que arma un `ChatOpenAI` apuntando a un servidor LM Studio local vía `base_url`.

Por último, `extraer_texto(contenido)` normaliza la respuesta del modelo (string plano o lista de bloques de contenido) a texto simple, usado por el router de chat.

### Routers y endpoints

Todos los routers viven bajo el prefijo `/api` (montado en `main.py`) y, salvo `health`, requieren autenticación vía `Depends(get_current_user)`:

- **`health`** (`GET /api/health`, sin auth): devuelve `status`, el `AGENT_MODEL` configurado y si existen `credentials.json`/`token.json` de Google Calendar — útil para diagnosticar despliegue sin necesidad de loguearse.
- **`auth`** (`/api/auth`, ver sección anterior): `register`, `login`, `logout` (sin auth previa los dos primeros; `logout` tampoco la exige), `me` y `avatar` (estos dos sí requieren sesión).
- **`activities`** (`/api/activities`, todo con auth): `GET ""` lista las actividades del usuario ordenadas por `puntaje_urgencia` descendente (recalculado en el router llamando a `agente._puntaje_urgencia`, no a la tool); `POST ""` crea una actividad invocando directamente `agente.agregar_actividad.invoke(...)` (los routers reutilizan las tools del agente como funciones normales, no solo el LLM las llama); `PATCH "/{id}/estado"`, `PUT "/{id}"` y `DELETE "/{id}"` reusan igual `actualizar_estado`, `editar_actividad`, `eliminar_actividad`, devolviendo 404 si la tool responde con un mensaje que empieza en "No existe" (esto cubre tanto "no existe" como "no es de este usuario", porque la tool ya filtra por `usuario_id`).
- **`calendar`** (`/api/calendar`, con auth): `GET /events` lista eventos de un día llamando a `agente._obtener_eventos_dia`; `POST /events` crea un evento invocando `agente.agendar_actividad.invoke(...)`. Sigue siendo el calendario global de la cuenta OAuth configurada en el backend, no uno por usuario.
- **`chat`** (`POST /api/chat`, con auth): setea `agente.set_usuario_actual(usuario.id)`, arma el historial de mensajes, invoca `await agente.agent.ainvoke({"messages": historial})` y concatena **todos** los mensajes de tipo IA con texto generados en ese turno (no solo el último), porque el agente puede razonar en varios pasos intercalando llamadas a tools con texto.
- **`plans`** (`/api/plans`, con auth): `POST /generate` invoca `agente.generar_plan`; `GET ""` lista los `.md` en `CARPETA_PLANES` ordenados por fecha de modificación; `GET "/{nombre}"` devuelve el contenido para preview; `GET "/{nombre}/download"` lo sirve como descarga. `_validar_nombre_plan` evita path traversal comprobando que el archivo resuelto quede dentro de `CARPETA_PLANES` y tenga extensión `.md`.
- **`files`** (`GET /api/files/browse`, con auth): navega `CARPETA_AUTORIZADA` reutilizando `agente._validar_ruta` para no salirse de ella; devuelve carpetas y archivos, marcando cuáles tienen una extensión admitida.

### Script de migración (migrate_actividades_json.py)

`backend/scripts/migrate_actividades_json.py` es un script de **uso manual, una sola vez**: migra las actividades de ejemplo que traía v2 en `backend/actividades.json` a la tabla `actividades` de MySQL, asignándolas todas al **primer usuario registrado** (`db.query(Usuario).order_by(Usuario.id).first()`). Se ejecuta después de crear la primera cuenta desde `/login`, con `python -m scripts.migrate_actividades_json` desde `backend/`. Es idempotente en el sentido de que si ese usuario ya tiene actividades, el script no hace nada (evita duplicar); y si no hay ningún usuario registrado todavía, avisa y termina sin migrar. `_limpiar_ruta_contexto` adapta las rutas del JSON viejo (que tenían el prefijo `materiales/`) al formato nuevo donde `ruta_contexto` ya es relativa a la carpeta de materiales.

### Frontend — autenticación y estado

- **`context/AuthContext.jsx`**: al montar, llama `api.getMe()` para restaurar sesión desde la cookie (si el navegador ya la tiene, el usuario sigue logueado tras recargar); expone `user`, `loading`, y las funciones `login`, `register`, `logout` que llaman al `client.js` y actualizan `user` con la respuesta. `loading` es clave para no redirigir a `/login` mientras todavía no se sabe si hay sesión.
- **`components/ProtectedRoute.jsx`**: componente de ruta de React Router que muestra un `Spinner` mientras `loading` es `true`, redirige a `/login` con `<Navigate replace>` si no hay `user`, y si no renderiza el `<Outlet />` (las rutas hijas protegidas). Se monta como wrapper de todas las rutas de la app excepto `/login` en `App.jsx`.
- **`pages/LoginPage.jsx`**: pantalla partida en dos: un panel de "pitch" del producto (lista de características) y una tarjeta con pestañas Iniciar sesión / Crear cuenta. El login manda `identificador` (username o email) + `password`; el registro manda `username`, `email`, `password`, `nombre_completo`. Ambos formularios, al tener éxito, navegan a `/` con `replace: true` (para que el botón "atrás" del navegador no vuelva al login).
- **`api/client.js`**: todas las llamadas usan `credentials: "include"` en el `fetch`, indispensable para que el navegador mande la cookie `httpOnly` de sesión en cada request al backend (que está en otro origen/puerto). Para `uploadAvatar` no fuerza `Content-Type: application/json` porque con `FormData` el navegador necesita poner su propio `Content-Type` con boundary.

**Flujo de login/registro end to end**: `LoginPage` llama `login()`/`register()` del contexto → `client.js` hace `POST /auth/login` o `/auth/register` con `credentials: "include"` → el backend valida y responde `Set-Cookie` con el JWT en `httpOnly` → `AuthContext` guarda el `Usuario` devuelto en `user` → `ProtectedRoute` dejar de redirigir y renderiza el resto de la app.

### Frontend — resto de componentes y páginas

**Layout y navegación:**
- `App.jsx` define las rutas con React Router: `/login` fuera de protección, y el resto (`/`, `/actividades`, `/actividades/nueva`, `/calendario`, `/planes`, `/materiales`, `/chat`) dentro de `ProtectedRoute` + `AppShell` (que monta `NavBar`, `Footer` y el `ChatProvider`).
- `main.jsx` envuelve todo en `BrowserRouter` y `AuthProvider`.
- `NavBar.jsx`: sidebar colapsable (persiste el estado colapsado/expandido en `localStorage`), enlaces a las 7 páginas, botón de tema claro/oscuro (`useTheme`), y el bloque de perfil: muestra el avatar (o un ícono placeholder si no hay), un input de archivo oculto que se dispara al hacer clic en el avatar y llama `uploadAvatar`, nombre/username del usuario, y botón de cerrar sesión.
- `Footer.jsx`: pie de página fijo con crédito del autor.

**Componentes reutilizables:**
- `Banner.jsx`: mensaje de estado (error/success/info) con ícono, no renderiza nada si `children` está vacío.
- `Spinner.jsx`: indicador de carga simple con etiqueta opcional.
- `Modal.jsx`: modal genérico con overlay, cierre por click afuera, por botón X o por tecla Escape; soporta un tono "danger" para el header.
- `UrgencyBadge.jsx`: exporta `BadgePrioridad` y `BadgeEstado`, badges de color según prioridad (alta/media/baja) o estado (pendiente/iniciada/completada).
- `ActivityTable.jsx`: tabla de actividades con columnas nombre/tipo/curso/vence/prioridad/urgencia/estado y acciones opcionales (cambiar estado al siguiente de la secuencia pendiente→iniciada→completada→pendiente, editar, eliminar), condicionadas a si el padre le pasa esos callbacks.
- `EditActivityModal.jsx` / `DeleteActivityModal.jsx`: modales de edición (formulario completo con selector de carpeta embebido) y confirmación de borrado.
- `FileBrowser.jsx`: navegador de `CARPETA_AUTORIZADA` con breadcrumbs; en modo standalone (página Materiales) es solo lectura, y cuando recibe `onSelect` (usado dentro de los formularios de actividad) agrega un botón "Elegir esta carpeta" para seleccionar la ruta de materiales sin escribirla a mano.
- `ChatBubble.jsx`: burbuja de mensaje con ícono distinto para usuario/agente y alineación a izquierda/derecha.
- `PlanCard.jsx`: tarjeta de un plan generado, con botón de mostrar/ocultar preview (renderizado en Markdown con `react-markdown` + `remark-gfm`) y enlace de descarga directa.

**Páginas:**
- `DashboardPage.jsx`: actividades no completadas, ordenadas por urgencia (que ya viene ordenado desde el backend), con acción rápida de cambiar estado.
- `ActivitiesPage.jsx`: listado completo con editar/eliminar, monta `EditActivityModal`/`DeleteActivityModal` según el estado local `editando`/`eliminando`.
- `NewActivityPage.jsx`: formulario de alta de actividad (no crea nada en Calendar, distingue explícitamente esa acción en el texto de ayuda).
- `CalendarPage.jsx`: selector de fecha + lista de eventos reales de Google Calendar del día, y un formulario para agendar un evento nuevo (acción de escritura real en Calendar).
- `PlansPage.jsx`: formulario para generar el plan del día (fecha + rango horario) e historial de planes ya generados con preview/descarga.
- `MaterialsPage.jsx`: envoltorio delgado sobre `FileBrowser` en modo solo lectura.
- `ChatPage.jsx`: interfaz de chat que usa el `ChatContext` (historial compartido para que no se pierda al navegar entre pestañas mientras la sesión de React sigue viva) y llama `sendChat`.

**Estado y utilidades:**
- `context/ChatContext.jsx`: guarda el `historial` de mensajes del chat en memoria (no persiste a través de recargas de página).
- `hooks/useTheme.js`: persiste el tema claro/oscuro en `localStorage` y lo aplica como `data-theme` en `<html>`.
- `styles/global.css`: define tokens de diseño (`--color-*`, `--radius-*`, `--space-*`) con variante para `[data-theme="dark"]`; estructura visual en sidebar fijo + contenido centrado + footer fijo; estilos de login en dos paneles (pitch + card con tabs); estilos de perfil/avatar en el pie del sidebar (imagen circular con badge de cámara superpuesto para indicar que es editable).

### Flujo de datos end-to-end (ejemplo)

1. El usuario abre la app; `AuthContext` llama `GET /api/auth/me`. Como no hay cookie válida todavía, el backend responde 401 y `user` queda en `null` → `ProtectedRoute` redirige a `/login`.
2. El usuario llena el formulario de login (`identificador` + `password`) en `LoginPage` y lo envía; `AuthContext.login()` llama `POST /api/auth/login` con `credentials: "include"`.
3. En `routers/auth.py`, `iniciar_sesion` busca el `Usuario` por username o email, valida la contraseña con `verify_password` (bcrypt) y, si es correcta, llama `_setear_cookie`, que genera un JWT con `create_access_token(usuario.id)` y lo manda como cookie `httpOnly` en la respuesta.
4. El navegador guarda esa cookie automáticamente; `AuthContext` recibe el `Usuario` en la respuesta y actualiza `user`; `ProtectedRoute` deja de redirigir y navega a `/` (Dashboard).
5. `DashboardPage` llama `GET /api/activities`. La request incluye la cookie automáticamente (`credentials: "include"`); en el backend, la dependency `get_current_user` decodifica el JWT de la cookie, recupera el `Usuario` de MySQL y lo inyecta en el endpoint.
6. `listar_actividades` en `routers/activities.py` hace `db.query(Actividad).filter(Actividad.usuario_id == usuario.id).all()` — solo las actividades de ESE usuario, nunca las de otra cuenta — calcula `puntaje_urgencia`/`dias_restantes` por fila con `agente._puntaje_urgencia`, ordena por urgencia descendente y devuelve el JSON.
7. El frontend recibe el arreglo y `ActivityTable` lo pinta con columnas y badges de color; si el usuario marca una actividad como "iniciada" desde la tabla, `updateEstado` hace `PATCH /api/activities/{id}/estado`, que internamente llama a la tool `agente.actualizar_estado.invoke(...)` — la cual, antes de tocar la fila, vuelve a filtrar por `Actividad.id == actividad_id` **y** `Actividad.usuario_id == _usuario_actual()`, así que ni siquiera con un id ajeno adivinado se podría modificar una actividad de otro usuario.
8. Si en cambio el usuario escribe en el Chat "qué tengo pendiente", `ChatPage` llama `POST /api/chat`; el router setea `agente.set_usuario_actual(usuario.id)` en el `ContextVar` de ese request y luego invoca `agente.agent.ainvoke(...)`; cuando el modelo decide llamar a la tool `consultar_actividades`, esta lee el `usuario_id` correcto desde el `ContextVar` (aislado de cualquier otro request concurrente) y filtra la tabla `actividades` exactamente igual que el endpoint REST.

---

## Versión 5 — Tarea_Agente_Personal_RAG (Sesión 13, RAG real con Chroma)

### Resumen

Es v1 (Sesión 12) con un cambio central: `buscar_en_documentos` deja de ser una búsqueda de
texto literal y pasa a ser **búsqueda semántica real** sobre una base de datos vectorial
(Chroma), con embeddings generados localmente vía Ollama. Se agregan además una tool de
búsqueda web (Tavily) como respaldo, y salida estructurada (Pydantic) en vez de texto libre.
A diferencia de v3/v4, no es una app web — sigue siendo un agente de consola de un solo
archivo (más un módulo `rag.py` separado para el índice), porque el entregable de esta tarea
es un script + un Google Doc, no una aplicación.

Dos archivos: `rag.py` (índice vectorial, sin dependencia de LangChain `create_agent`) y
`agente_planificacion_rag.py` (el agente en sí, que importa `rag.py`).

### `rag.py` — índice vectorial

#### Constantes y estado de módulo
`CARPETA_MATERIALES`, `CARPETA_INDICE` (`./chroma_index`, persistente en disco) y
`NOMBRE_COLECCION` fijan dónde vive todo. `MODELO_EMBEDDINGS`/`OLLAMA_BASE_URL` se leen de
variables de entorno con defaults (`nomic-embed-text` en `localhost:11434`), para no acoplar
el código a una sola máquina. `_embeddings`/`_vector_store` son variables globales de módulo
que cachean el cliente de embeddings y el vector store ya construidos, para no recrearlos en
cada llamada a `buscar()`.

#### `_obtener_embeddings()`
Lazy-init de `OllamaEmbeddings`: solo se instancia la primera vez que se necesita (evita abrir
una conexión al servidor de Ollama si el índice ya existe en disco y no hace falta reindexar).

#### `_extraer_texto_archivo(ruta)`
Extrae texto plano según la extensión: `.txt/.md/.py` se leen directo, `.docx` usa
`python-docx` (concatena el texto de cada párrafo), `.pdf` usa `pypdf` (concatena el texto
extraído de cada página — importante: si el PDF no tiene capa de texto en una página, esa
página simplemente no aporta nada, no falla).

#### `_cargar_documentos()`
Recorre `materiales/` recursivamente (`rglob("*")`), filtra por extensión admitida, extrae el
texto de cada archivo, y lo divide en fragmentos con `RecursiveCharacterTextSplitter`
(`chunk_size=800`, `chunk_overlap=120` — el solape evita perder contexto que quedaría cortado
justo en el borde de dos fragmentos). Por cada fragmento crea un `Document` de LangChain con
metadata `{"archivo": ..., "ruta_contexto": ...}` — `ruta_contexto` se calcula relativo a la
carpeta *padre* de `materiales/` (no a `materiales/` misma), para que su valor coincida
exactamente con el campo `ruta_contexto` de `tareas.json` (ej. `"materiales/TareaReAct"`) y así
poder filtrar la búsqueda por tarea más adelante. Cada fragmento recibe un id único
determinístico (`archivo::índice_de_chunk`).

#### `construir_o_cargar_indice(forzar_reindexado=False)`
Si `forzar_reindexado=True` borra `chroma_index/` primero (reindexado completo desde cero). Si
la carpeta del índice no existe todavía, indexa (`_cargar_documentos()` + `add_documents`); si
ya existe y no se fuerza, simplemente abre el índice existente sin volver a leer/embeber los
documentos (evita recalcular embeddings en cada arranque — son costosos). Se puede invocar
manualmente por CLI: `python rag.py --reindexar`.

#### `buscar(consulta, k=4, ruta_contexto=None)`
La función que usa el resto del proyecto. Llama a `similarity_search` de Chroma, que compara el
embedding de la consulta contra los embeddings indexados y devuelve los `k` más cercanos. Si se
pasa `ruta_contexto`, se agrega como filtro exacto de metadata (`filter={"ruta_contexto": ...}`)
para limitar la búsqueda a una carpeta/tarea específica.

### `agente_planificacion_rag.py` — el agente

#### Qué se reutiliza de v1 sin cambios
`_cargar_tareas`, `_guardar_tareas`, `_buscar_tarea`, `_validar_ruta`, `_puntaje_urgencia`, y las
tools `consultar_tareas`, `agregar_tarea`, `calcular_prioridad`, `generar_plan`,
`actualizar_estado`, `guardar_plan_detallado`, `inspeccionar_carpeta` — mismo código, mismo
comportamiento. La gestión de tareas (`tareas.json`) no cambia con RAG; solo cambia cómo se
consultan los *documentos*.

#### `buscar_en_documentos(consulta, tarea_id=None)` — la tool nueva
Reemplaza a la de v1 (que hacía `for linea in texto.splitlines(): if termino in linea`). Ahora:
si se da `tarea_id`, resuelve la tarea y usa su `ruta_contexto` como filtro; llama a
`rag.buscar(consulta, k=4, ruta_contexto=...)`; devuelve los fragmentos encontrados citando el
archivo de origen (`[archivo] contenido`). La diferencia clave frente a v1: encuentra contenido
relevante aunque la pregunta no use las palabras exactas del documento (verificado en pruebas
reales — ver `ENTREGA_GOOGLE_DOC.md`).

#### `buscar_en_la_web(consulta)` — tool de respaldo
Usa `tavily-python` para buscar en la web cuando los materiales locales no alcanzan. Si no hay
`TAVILY_API_KEY` configurada, devuelve un mensaje explícito de "no disponible" en vez de fallar
con una excepción — el agente puede reportar esa limitación al usuario en vez de romperse o
inventar una respuesta.

#### `RespuestaAgente` (Pydantic) — salida estructurada
En vez de que el agente devuelva texto libre, `create_agent(..., response_format=RespuestaAgente)`
lo obliga a llenar 4 campos: `resumen`, `acciones_recomendadas`, `fuentes` (qué documentos o
resultados web citó) y `tools_usadas` (qué herramientas llamó realmente). Esto hace la respuesta
trazable: se puede verificar que el agente sí usó una tool antes de responder, en vez de confiar
ciegamente en el texto.

#### `PROMPT_SISTEMA`
Mismo flujo que v1 (consultar → priorizar → planificar → buscar en materiales → actualizar
estado), con dos agregados: cuándo usar `buscar_en_la_web` como respaldo (solo si
`buscar_en_documentos` no encontró nada útil), y una regla explícita agregada **después de un
bug real encontrado en pruebas**: el modelo, en una primera prueba, respondió "dame un momento
mientras consulto tus materiales" como respuesta *final* sin haber llamado ninguna tool
(`fuentes`/`tools_usadas` vacíos). La salida estructurada por sí sola no obliga a usar las tools
antes de responder — se corrigió agregando al prompt una prohibición explícita de responder con
mensajes de "espera" como respuesta final.

#### Arranque e inicialización
Al importar el módulo se llama `rag.construir_o_cargar_indice(forzar_reindexado="--reindexar" in
sys.argv)` — así el índice está listo antes de crear el agente, y `python
agente_planificacion_rag.py --reindexar` fuerza reconstruirlo sin tener que llamar `rag.py` por
separado.

#### `iniciar_chat()`
Mismo loop de consola que v1, con dos cambios: en vez de imprimir `resultado["messages"][-1]`
como texto libre, lee `resultado["structured_response"]` (una instancia de `RespuestaAgente`) e
imprime sus 4 campos por separado; y en vez de reconstruir el historial a mano, usa
`resultado["messages"]` completo como el `historial` del siguiente turno (conserva el registro
completo de llamadas a tools entre turnos, no solo el texto final).

### Qué cambia respecto a v1 (resumen)

| | v1 | RAG (v5) |
|---|---|---|
| Búsqueda en documentos | Texto literal (`in`), sin tildes | Semántica (Chroma + embeddings Ollama) |
| Filtrado por tarea | Implícito (busca en la carpeta de la tarea) | Explícito por metadata (`ruta_contexto`) |
| Fuente adicional | Ninguna | Búsqueda web (Tavily) como respaldo |
| Formato de respuesta | Texto libre | Estructurado (Pydantic: resumen/acciones/fuentes/tools) |
| Tools totales | 8 | 9 (+ `buscar_en_la_web`, `buscar_en_documentos` reescrita) |
