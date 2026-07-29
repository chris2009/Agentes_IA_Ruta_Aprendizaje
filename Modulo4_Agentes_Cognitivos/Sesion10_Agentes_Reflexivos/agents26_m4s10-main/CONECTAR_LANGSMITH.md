# Conectar LangSmith a los agentes de esta carpeta

Guía paso a paso para activar el *tracing* (registro detallado de cada
ejecución) de los agentes en `agents26_m4s10-main/` en **LangSmith**, la
plataforma web de LangChain (el framework que arma tus agentes con
`create_agent`) para observabilidad de agentes: permite ver, para cada
ejecución, la secuencia completa de llamadas al LLM (*Large Language
Model*, el modelo de lenguaje que genera texto y decide qué herramienta
invocar) y a las *tools* (funciones Python que el agente puede ejecutar,
como `sensor_temperatura` o `consultar_estado_estante`), junto con
tokens consumidos, costo estimado en USD (*United States Dollar*, dólar
estadounidense) y latencia de cada paso.

Esta guía reemplaza al PDF `CONECTAR_LANGSMITH.pdf` de la carpeta
superior, que fue escrito para otro agente (`agente_presupuesto_materiales.py`,
en una carpeta `Sesion12/`) y no coincide con los archivos reales de esta
sesión. Aquí está adaptada a los 6 scripts que sí existen:

| Script | Modelo que usa |
|---|---|
| `00_basic_agent.py` | Anthropic (`claude-opus-4-8`) — **cuesta dinero real** por token |
| `01_simple_reflex_agent.py` | Ollama local (`llama3.2`) — gratis |
| `02_model_based_reflex_agent.py` | Ollama local (`llama3.2`) — gratis |
| `03_goal_based_agent.py` | Ollama local (`llama3.2`) — gratis |
| `04_utility_based_agent.py` | Ollama local (`llama3.2`) — gratis |
| `05_learning_agent.py` | Ollama local (`llama3.2`) — gratis |

No requiere modificar la lógica de ningún agente: LangSmith se activa
enteramente por variables de entorno. Lo único que sí importa (ver Paso 3)
es que el script lea el archivo `.env` — y hoy en día **solo
`00_basic_agent.py` lo hace**.

## Prerrequisitos

- Los agentes ya funcionando (Ollama corriendo localmente con `llama3.2`
  descargado, y `ANTHROPIC_API_KEY` configurada en `.env` para el agente
  Anthropic).
- El paquete `langsmith` disponible en el entorno virtual. Es una
  dependencia habitual de `langchain`, pero como no aparece listado
  explícitamente en `requirements.txt` de esta carpeta, confírmalo con:
  ```powershell
  pip install -U langsmith
  ```

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

## Paso 2 — Agregar las variables al `.env` de esta carpeta

Abre `agents26_m4s10-main/.env` (el mismo archivo que ya tiene tu
`ANTHROPIC_API_KEY`) y agrega:

```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_tu_key_aqui
LANGSMITH_PROJECT=agentes-reflexivos-m4s10
```

Qué hace cada variable:

| Variable | Para qué sirve |
|---|---|
| `LANGSMITH_TRACING` | En `true`, activa el envío automático de trazas a LangSmith en cada ejecución del agente. |
| `LANGSMITH_API_KEY` | Autentica las trazas contra tu cuenta de LangSmith. |
| `LANGSMITH_PROJECT` | Nombre del proyecto donde se agrupan las trazas en la web (si no existe, LangSmith lo crea automáticamente la primera vez que llega una traza). |

## Paso 3 — Asegurar que cada script cargue el `.env`

Aquí es donde esta guía difiere del PDF original. `00_basic_agent.py` ya
llama a `load_dotenv()` al inicio, así que con el Paso 2 termina su
configuración: no hace falta tocarlo.

Los scripts `01_simple_reflex_agent.py` a `05_learning_agent.py` **no**
importan `dotenv` ni llaman a `load_dotenv()` — hoy dependen únicamente
de Ollama local, que no necesita API key. Para que también manden trazas
a LangSmith, elige una de estas dos opciones:

**Opción A — Agregar `load_dotenv()` al script (recomendado, 2 líneas)**

Al inicio del archivo, junto a los demás imports:

```python
from dotenv import load_dotenv
load_dotenv()
```

Con esto el script queda igual de autocontenido que antes (sigue sin
depender de otros archivos del repo), solo que ahora también lee
variables de entorno desde `.env` — igual que ya hace `00_basic_agent.py`.

**Opción B — Exportar las variables en la sesión de PowerShell (sin tocar código)**

```powershell
$env:LANGSMITH_TRACING="true"
$env:LANGSMITH_API_KEY="lsv2_pt_tu_key_aqui"
$env:LANGSMITH_PROJECT="agentes-reflexivos-m4s10"
python 01_simple_reflex_agent.py
```

Esto solo dura mientras esa ventana de PowerShell esté abierta — tendrías
que repetirlo cada vez que abras una terminal nueva.

## Paso 4 — Ejecutar el agente normalmente

```powershell
python 00_basic_agent.py
```

o, para cualquiera de los agentes reflexivos (tras aplicar el Paso 3):

```powershell
python 01_simple_reflex_agent.py
```

Cada `agent.invoke(...)` queda registrado como una traza en LangSmith,
sin que el script tenga que hacer nada explícito para reportarla.

## Paso 5 — Ver la traza en LangSmith

1. Vuelve a [smith.langchain.com](https://smith.langchain.com).
2. Entra al proyecto `agentes-reflexivos-m4s10` (panel lateral
   **Projects**).
3. Verás una fila por cada `agent.invoke(...)` ejecutado. Al abrir una
   fila puedes revisar:
   - **Árbol de la ejecución**: mensaje del usuario → llamada al modelo
     → qué tool decidió invocar → resultado de esa tool → siguiente
     llamada al modelo, y así hasta la respuesta final.
   - **Tokens**: de entrada (*input*) y de salida (*output*), por cada
     llamada individual al modelo y acumulados para todo el run.
   - **Costo estimado**: LangSmith calcula el costo en USD según el
     modelo usado y la cantidad de tokens.
   - **Latencia**: tiempo que tomó cada paso, útil para identificar si
     el cuello de botella es el modelo o alguna tool.

## Paso 6 (opcional) — Nombrar proyectos por agente o por tanda de pruebas

Si quieres distinguir las trazas de cada tipo de agente (o separar
pruebas de ejecuciones "reales"), cambia `LANGSMITH_PROJECT` antes de
correr el script — sin tocar el código:

```powershell
$env:LANGSMITH_PROJECT="m4s10-agente-reflejo-simple"
python 01_simple_reflex_agent.py
```

Así cada tanda queda agrupada en su propio proyecto dentro de LangSmith,
y puedes comparar tokens/costo entre proyectos desde el panel
**Projects**.

## Notas

- El costo mostrado en LangSmith es una **estimación** basada en las
  tarifas públicas del proveedor y el conteo de tokens: es una
  referencia, no una factura.
- El `.env` con la API key de LangSmith **no debe subirse al
  repositorio**: ya está cubierto por la línea `.env` en el
  `.gitignore` de esta carpeta.
- Los scripts `01` a `05` usan Ollama (modelo local): LangSmith registra
  la traza igual, pero el costo estimado aparecerá en `$0.00` porque
  Ollama no cobra por token — es una forma gratuita de ver tokens y
  latencia sin gastar en la API de Anthropic.
