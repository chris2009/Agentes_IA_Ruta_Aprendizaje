# Conectar LangSmith al agente de presupuesto de materiales

Guía paso a paso para activar el *tracing* (registro detallado de cada
ejecución) de [agente_presupuesto_materiales.py](agente_presupuesto_materiales.py)
en **LangSmith**, la plataforma web de LangChain para observabilidad de
agentes: permite ver, para cada ejecución, la secuencia completa de
llamadas al LLM (*Large Language Model*, el modelo de lenguaje que
genera texto y decide qué herramienta invocar) y a las *tools*
(funciones Python que el agente puede ejecutar, como
`consultar_precio_material`), junto con tokens consumidos, costo
estimado en USD (*United States Dollar*, dólar estadounidense) y
latencia de cada paso.

No requiere modificar el código del agente: LangSmith se activa
enteramente por variables de entorno.

## Prerrequisitos

- El agente ya funcionando con el proveedor Anthropic (`LLM_PROVIDER=anthropic`,
  el valor por defecto en [`.env`](.env)).
- El paquete `langsmith` ya está disponible: es una dependencia de
  `langchain`, que ya está instalado en el entorno virtual compartido del
  módulo (ver [`requirements.txt`](../requirements.txt)). No hace falta
  instalar nada adicional.

## Paso 1 — Crear cuenta y API key en LangSmith

1. Entra a [smith.langchain.com](https://smith.langchain.com) y crea una
   cuenta (puedes usar el mismo correo con el que te registraste en otros
   servicios).
2. Dentro del proyecto/organización que te asigna por defecto, ve a
   **Settings → API Keys**.
3. Genera una nueva API key (*Application Programming Interface key*,
   credencial que identifica tus peticiones ante el servicio). Tendrá un
   formato similar a `lsv2_pt_...` o `lsv2_sk_...`.
4. Copia esa key: LangSmith solo la muestra una vez.

## Paso 2 — Agregar las variables al `.env` de esta sesión

Abre [`Sesion12/.env`](.env) y descomenta/completa el bloque de LangSmith
que ya está preparado ahí:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_tu_key_aqui
LANGSMITH_PROJECT=sesion12-presupuesto-materiales
```

Qué hace cada variable:

| Variable | Para qué sirve |
|---|---|
| `LANGSMITH_TRACING` | En `true`, activa el envío automático de trazas a LangSmith en cada ejecución del agente. |
| `LANGSMITH_API_KEY` | Autentica las trazas contra tu cuenta de LangSmith. |
| `LANGSMITH_PROJECT` | Nombre del proyecto donde se agrupan las trazas en la web (si no existe, LangSmith lo crea automáticamente la primera vez que llega una traza). |

No hace falta tocar `agente_presupuesto_materiales.py`: el script ya
llama a `load_dotenv()` al inicio, que carga estas variables del `.env`
igual que carga `ANTHROPIC_API_KEY`.

## Paso 3 — Ejecutar el agente normalmente

```bash
python agente_presupuesto_materiales.py
```

Prueba con una solicitud real, por ejemplo:

```
Solicitud: 5 lapiceros, 2 paquetes de papel bond A4 y 1 grapadora
```

Cada `agent.invoke(...)` que hace `iniciar_presupuesto()` queda
registrado como una traza en LangSmith, sin que el script tenga que
hacer nada explícito para reportarla.

## Paso 4 — Ver la traza en LangSmith

1. Vuelve a [smith.langchain.com](https://smith.langchain.com).
2. Entra al proyecto `sesion12-presupuesto-materiales` (panel lateral
   **Projects**).
3. Verás una fila por cada `agent.invoke(...)` ejecutado. Al abrir una
   fila puedes revisar:
   - **Árbol de la ejecución**: mensaje del usuario → llamada al modelo
     → qué tool decidió invocar (`consultar_precio_material`,
     `calcular_subtotal_item`, `generar_presupuesto_final`) → resultado
     de esa tool → siguiente llamada al modelo, y así hasta la respuesta
     final.
   - **Tokens**: de entrada (*input*) y de salida (*output*), por cada
     llamada individual al modelo y acumulados para todo el run.
   - **Costo estimado**: LangSmith calcula el costo en USD según el
     modelo usado (`claude-sonnet-4-6` en este agente) y la cantidad de
     tokens.
   - **Latencia**: tiempo que tomó cada paso, útil para identificar si
     el cuello de botella es el modelo o alguna tool.

## Paso 5 (opcional) — Nombrar runs y comparar

Si quieres distinguir ejecuciones de prueba de ejecuciones "reales" (por
ejemplo, para la tarea de comparar costos entre proveedores), puedes
correr el script con un proyecto distinto sin tocar el código, solo
cambiando la variable de entorno antes de ejecutar:

```bash
LANGSMITH_PROJECT=sesion12-pruebas python agente_presupuesto_materiales.py
```

Así cada tanda de pruebas queda agrupada en su propio proyecto dentro de
LangSmith, y puedes comparar tokens/costo entre proyectos desde el panel
**Projects**.

## Notas

- El costo mostrado en LangSmith es una **estimación** basada en las
  tarifas públicas del proveedor (Anthropic) y el conteo de tokens: es
  una referencia, no una factura.
- El `.env` con la API key de LangSmith **no debe subirse al repositorio**:
  ya está cubierto por la línea `.env` en [`.gitignore`](.gitignore) de
  esta carpeta.
- Si más adelante corres el agente con `LLM_PROVIDER=ollama` (modelo
  local), LangSmith sigue registrando la traza igual, pero el costo
  estimado aparecerá en `$0.00` porque Ollama no cobra por token.
