# Versión 1 — Tarea_Agente_Personal (Sesión 12)

Archivo documentado: `Modulo5_Herramientas_para_Orquestacion/Sesion12_LangChain_Agents/Tarea_Agente_Personal/agente_planificacion_academica.py`

## Resumen

Es un agente ReAct (Reasoning + Acting, patrón en el que el modelo alterna entre "pensar" y "llamar herramientas" hasta responder) construido con `create_agent` de LangChain, cuyo propósito es priorizar tareas académicas pendientes, generar planes de tiempo y buscar contenido dentro de los documentos asociados a cada tarea. No usa base de datos: toda la persistencia es un archivo `tareas.json` leído y reescrito completo en cada operación. Lo que distingue a esta versión es que la búsqueda documental es **búsqueda literal de texto** (sin *embeddings* ni *vector store*, es decir, sin representación numérica del significado ni motor de recuperación semántica) y que el modelo detrás del agente es intercambiable entre Anthropic (Claude, de pago) y un modelo local vía LM Studio, mediante la variable de entorno `AGENT_MODEL`.

## Estructura de datos

`tareas.json` es una lista de objetos JSON (JavaScript Object Notation) ubicada en `RUTA_TAREAS` (junto al script). Cada tarea tiene el siguiente esquema, según el archivo real:

```json
{
  "id": 1,
  "nombre": "Implementar agente personal ReAct",
  "curso": "Implementación de agentes con IA",
  "fecha_limite": "2026-08-02",
  "duracion_estimada_minutos": 240,
  "prioridad": "alta",
  "estado": "iniciada",
  "ruta_contexto": "materiales/TareaReAct",
  "entregable": "Google Doc con objetivo y código"
}
```

- `id`: entero autoincremental (se calcula como `max(ids existentes) + 1`).
- `fecha_limite`: cadena en formato `YYYY-MM-DD`, parseable con `date.fromisoformat`.
- `prioridad`: uno de `"alta"`, `"media"`, `"baja"`, usado como clave en `PESO_PRIORIDAD = {"alta": 3, "media": 2, "baja": 1}`.
- `estado`: uno de `"pendiente"`, `"iniciada"`, `"completada"`.
- `ruta_contexto`: ruta relativa (a la carpeta autorizada) donde viven los materiales de la tarea; puede estar vacía si la tarea no tiene documentos asociados.
- `entregable`: texto libre, informativo.

No hay motor de base de datos ni ORM (Object-Relational Mapper): cada lectura/escritura serializa/deserializa el archivo completo con `json.loads`/`json.dumps`.

## Funciones auxiliares

### `_cargar_tareas()` y `_guardar_tareas(tareas)`
Son el único punto de entrada/salida a `tareas.json`. `_cargar_tareas` devuelve `[]` si el archivo no existe (evita `FileNotFoundError` en el primer uso); `_guardar_tareas` serializa la lista completa con `ensure_ascii=False` (para conservar tildes y símbolos en español) e indentación de 2 espacios. Todas las tools que modifican datos siguen el mismo patrón: cargar todo → mutar en memoria → guardar todo. No hay bloqueo de concurrencia ni transacciones; para un agente de un solo usuario en CLI (interfaz de línea de comandos) es suficiente.

### `_buscar_tarea(tarea_id)`
Busca una tarea por `id` recorriendo el resultado de `_cargar_tareas()` con `next(...)`, devolviendo `None` si no existe. La usan casi todas las tools que reciben un `tarea_id`, para poder devolver un mensaje de error uniforme ("No existe una tarea con id X") en vez de lanzar una excepción.

### `_validar_ruta(ruta)`
Es el mecanismo de seguridad de acceso a archivos. Resuelve la ruta recibida (relativa al directorio del script, o absoluta si ya lo es) y solo la acepta si es exactamente `CARPETA_AUTORIZADA` o si `CARPETA_AUTORIZADA` aparece entre sus rutas padre (`ruta_resuelta.parents`). Si la ruta cae fuera de esa carpeta, devuelve `None`. `CARPETA_AUTORIZADA` por defecto es `materiales/` junto al script, pero puede redirigirse con la variable de entorno `CARPETA_AUTORIZADA`. Esto impide que el agente lea archivos arbitrarios del sistema aunque el usuario o el modelo intenten inducirlo a hacerlo (protección contra *path traversal*, es decir, rutas tipo `../../` que escapen del directorio permitido).

### `_puntaje_urgencia(tarea)`
Implementa la heurística de priorización: `peso_prioridad * 100 / (días_restantes + 1)`. A mayor prioridad declarada y menor tiempo restante, mayor el puntaje; el `+1` evita división por cero cuando la tarea vence hoy. Es una fórmula simple y determinista (no un modelo de utilidad ni una llamada al LLM — Large Language Model, modelo de lenguaje de gran escala): el mismo input siempre da el mismo resultado, lo cual es importante porque el prompt del sistema le exige al agente "nunca decidir la urgencia a ojo".

### `_normalizar(texto)`
Prepara texto para comparación insensible a mayúsculas/tildes: pasa a minúsculas y luego usa `unicodedata.normalize("NFKD", ...)` para descomponer caracteres acentuados en base + diacrítico, descartando los diacríticos (`unicodedata.combining(c)`). Así, buscar "practica" encuentra "práctica". La usan tanto `buscar_en_documentos` (para comparar la consulta con cada línea) como, indirectamente, cualquier comparación de texto libre.

### `_extraer_texto_archivo(ruta)` y `extraer_texto(contenido)`
Son dos funciones distintas con propósitos distintos, aunque el nombre es parecido:
- `_extraer_texto_archivo` (privada, con guion bajo) extrae el texto plano de un **archivo de materiales** según su extensión: lectura directa para `.txt`/`.md`/`.py`, `python-docx` para `.docx` (concatenando párrafos), y `pypdf` para `.pdf` (concatenando el texto de cada página, tolerando páginas sin texto extraíble con `or ""`). Devuelve cadena vacía para extensiones no reconocidas.
- `extraer_texto` (pública, sin guion bajo) convierte la **respuesta del modelo** en texto plano: si `content` ya es un string lo devuelve tal cual; si es una lista de bloques (como ocurre con Claude cuando el modo *thinking* — razonamiento extendido — está activo, que devuelve una lista de bloques tipados en vez de un string simple) extrae el campo `text` de cada bloque, sea dict o objeto, y los une con saltos de línea. Se usa en el loop de chat para imprimir la respuesta final del agente sin importar el formato interno que use el proveedor del modelo.

## Tools del agente

Cada tool está decorada con `@tool` de `langchain.tools`, lo que expone su *docstring* como la descripción que el modelo ve para decidir cuándo usarla — por eso los docstrings del código están escritos como instrucciones de uso, no solo como documentación.

### `consultar_tareas()`
Sin parámetros. Devuelve un listado de todas las tareas con id, nombre, curso, fecha límite, prioridad y estado, una por línea. Es el punto de partida del flujo recomendado: el agente la usa primero para saber qué hay pendiente antes de razonar sobre prioridades.

### `agregar_tarea(nombre, curso, fecha_limite, duracion_minutos, prioridad, ruta_contexto="", entregable="")`
Registra una tarea nueva calculando el siguiente `id` disponible, la inserta con `estado="pendiente"` fijo, y persiste con `_guardar_tareas`. El docstring instruye explícitamente al modelo a pedir el dato al usuario en vez de inventarlo si falta algo — la validación de completitud queda delegada al criterio del LLM, no hay validación de esquema en código.

### `calcular_prioridad(tarea_id)`
Busca la tarea, calcula días restantes y devuelve el puntaje de `_puntaje_urgencia` formateado a un decimal, junto con la prioridad declarada y los días restantes. El prompt del sistema exige llamarla antes de decidir qué tarea atender primero.

### `generar_plan(minutos_disponibles)`
Ordena las tareas no completadas por `_puntaje_urgencia` descendente y va llenando un bloque de tiempo: por cada tarea que entra en el presupuesto de minutos, agrega una fila a una tabla Markdown y suma su duración más 10 minutos de descanso (salvo que ya se haya agotado el tiempo). Genera un identificador único `PLAN-{timestamp}`, arma un documento Markdown con encabezado (código, fecha de generación, tiempo disponible/usado) y una tabla de bloques, y lo escribe en `planes_generados/{codigo_plan}.md`, creando la carpeta si no existe. Devuelve un resumen de cuántas tareas entraron y dónde quedó guardado el archivo. Si ninguna tarea cabe en el tiempo disponible, devuelve un mensaje explicativo en vez de un plan vacío.

### `actualizar_estado(tarea_id, nuevo_estado)`
Valida que `nuevo_estado` sea uno de los tres estados permitidos (si no, rechaza con mensaje de error), busca la tarea por id iterando la lista completa, la muta in-place y guarda. Devuelve confirmación o error de id inexistente.

### `guardar_plan_detallado(tarea_id, titulo, contenido_markdown)`
Existe para un caso distinto al de `generar_plan`: cuando el usuario ya recibió del agente, dentro de la conversación, un plan redactado en texto libre (por ejemplo un desglose por fases) y pide "guardarlo" o "exportarlo" tal cual. A diferencia de `generar_plan`, esta tool no recalcula nada desde `tareas.json` — simplemente envuelve el `contenido_markdown` que el propio modelo generó en un encabezado estándar (código `PLAN-DETALLADO-{timestamp}`, fecha, nombre de la tarea) y lo escribe a disco. El docstring es explícito en aclarar esta diferencia porque, sin esa instrucción, el modelo podría confundir ambas tools.

### `inspeccionar_carpeta(tarea_id)`
Recibe un `tarea_id` (nunca una ruta escrita a mano) y resuelve la carpeta de materiales de esa tarea vía `_validar_ruta(tarea["ruta_contexto"])`. Si la ruta cae fuera de `CARPETA_AUTORIZADA`, o la carpeta no existe, o la tarea no tiene `ruta_contexto`, devuelve el mensaje de error correspondiente. Si es válida, lista los nombres de archivo cuya extensión esté en `EXTENSIONES_ADMITIDAS` (`.pdf`, `.docx`, `.txt`, `.md`, `.py`).

### `buscar_en_documentos(tarea_id, consulta)`
La tool de "recuperación de información" de esta versión. Resuelve y valida la carpeta igual que `inspeccionar_carpeta`, normaliza la consulta con `_normalizar`, y para cada archivo compatible extrae su texto con `_extraer_texto_archivo`, recorre línea por línea, y compara si el término normalizado está contenido en la línea normalizada (`in`, es decir, coincidencia de subcadena literal, no búsqueda difusa ni semántica). Acumula coincidencias como `[nombre_archivo] línea` y devuelve como máximo las primeras 10. Cualquier error al leer un archivo individual (`except Exception: continue`) se ignora silenciosamente para no abortar la búsqueda completa por un archivo corrupto. Es explícitamente **no-RAG** (RAG = Retrieval-Augmented Generation, generación aumentada por recuperación con vectores semánticos): no hay *embeddings*, no hay *chunking* semántico, no hay *vector store* — solo coincidencia de texto.

## Prompt del sistema y creación del agente

### `PROMPT_SISTEMA`
Es un bloque de texto que define el rol del agente ("agente personal de planificación académica"), impone la regla general de no inventar fechas/prioridades/contenido sin haber consultado las tools, y describe un **flujo recomendado en 6 pasos** que espeja casi 1:1 el orden natural de las tools: `consultar_tareas` → `calcular_prioridad` → `generar_plan` (si hay tiempo disponible) → `inspeccionar_carpeta` + `buscar_en_documentos` (si el usuario quiere empezar una tarea) → `actualizar_estado` / `agregar_tarea` según corresponda → `guardar_plan_detallado` solo cuando se pide exportar algo ya redactado. También fija dos reglas duras: restringir el acceso a la carpeta autorizada, y ser breve/concreto en las respuestas. Este prompt es la única guía de "razonamiento" del agente — no hay lógica de orquestación en código que fuerce ese orden, todo depende de que el modelo siga las instrucciones.

### `resolver_modelo()` y `AGENT_MODEL`
`AGENT_MODEL` se lee de la variable de entorno (por defecto `"anthropic"`) y decide qué backend de modelo se instancia:
- `"anthropic"`: devuelve el string `"anthropic:{modelo}"` (por defecto `claude-sonnet-4-6`, configurable con `ANTHROPIC_MODEL`), que es la sintaxis abreviada que `create_agent` de LangChain reconoce para resolver automáticamente el proveedor y crear el cliente de Anthropic.
- `"gemma-lmstudio"`: construye explícitamente un objeto `ChatOpenAI` de `langchain_openai` apuntando a un servidor LM Studio local (compatible con la API de OpenAI) vía `base_url`, con una API key dummy (`"lm-studio"`) porque el servidor local no la valida, y `temperature=0.3`.
- Cualquier otro valor lanza `ValueError`.

Esto permite correr el mismo agente sin costo (modelo local) o con un modelo de mayor calidad (Claude, de pago), sin tocar el resto del código — solo cambiando una variable de entorno.

### `create_agent(...)`
Se llama una sola vez a nivel de módulo (al importar el script), pasando el modelo resuelto, `PROMPT_SISTEMA` y la lista de las 8 tools (`consultar_tareas, agregar_tarea, calcular_prioridad, generar_plan, actualizar_estado, guardar_plan_detallado, inspeccionar_carpeta, buscar_en_documentos`). `create_agent` es la función de LangChain que arma internamente el grafo ReAct: en cada turno, el modelo decide si responder directamente o invocar una o más tools, LangChain ejecuta las tools elegidas y le devuelve el resultado al modelo, y el ciclo se repite hasta que el modelo emite una respuesta final sin más llamadas a herramientas.

## Loop de chat (`iniciar_chat`)

Es el punto de entrada interactivo, ejecutado solo si el script corre como programa principal (`if __name__ == "__main__"`), y antes de arrancar valida que exista `ANTHROPIC_API_KEY` si el backend es `"anthropic"` (para fallar rápido con un mensaje claro en vez de un error críptico de la librería).

El ciclo es un `while True` que:
1. Imprime un encabezado con el nombre del modelo activo (vía `_nombre_modelo()`, que arma una etiqueta legible tipo "claude-sonnet-4-6 (Anthropic, de pago)" o "google/gemma-4-e4b (LM Studio, local)").
2. Lee una línea de `input("Tu: ")`; ignora líneas vacías; corta el loop si el usuario escribe `"salir"`, `"exit"` o `"quit"`.
3. Mantiene un `historial: list[dict]` en memoria (no persistido) con mensajes `{"role": "user"/"assistant", "content": ...}`, que se le pasa completo a `agent.invoke({"messages": historial})` en cada turno — así el agente conserva contexto de toda la conversación de esa sesión, pero pierde todo al cerrar el programa.
4. Extrae el último mensaje del resultado (`resultado["messages"][-1]`) y lo convierte a texto con `extraer_texto`, lo agrega al historial como turno del asistente, y lo imprime.
5. Envuelve cada iteración en `try/except`: `KeyboardInterrupt` (Ctrl+C) termina limpiamente, y cualquier otra excepción se captura, se imprime un mensaje genérico más el detalle técnico, y el loop continúa sin caerse — así un error en una tool (por ejemplo, un PDF corrupto) no tumba toda la sesión de chat.

Diagrama de arquitectura: `v1_tarea_agente_personal.drawio.xml` (ya existe en otra carpeta, solo se referencia el nombre).
