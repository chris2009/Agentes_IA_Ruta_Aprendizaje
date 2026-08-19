# Agentes con Streaming usando LangChain y OpenAI

Este proyecto contiene dos ejemplos de agentes que utilizan streaming para comunicarse en tiempo real con OpenAI.

## 📋 Contenido

- **agent_streaming.py** - Agente básico con streaming simple
- **agent_streaming_avanzado.py** - Agente avanzado con callbacks personalizados
- **requirements.txt** - Dependencias del proyecto

## 🚀 Instalación

### 1. Crear un entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar API Key de OpenAI

```bash
export OPENAI_API_KEY="tu-clave-api-aqui"
```

O crear un archivo `.env`:

```
OPENAI_API_KEY=tu-clave-api-aqui
```

## 📖 Ejemplos

### Agente Básico

```bash
python agent_streaming.py
```

Este script demuestra:
- ✅ Configuración básica de un agente
- ✅ Streaming de tokens en tiempo real
- ✅ Tres herramientas simples (suma, multiplicación, información)
- ✅ Procesamiento de tareas en el orden correcto

### Agente Avanzado

```bash
python agent_streaming_avanzado.py
```

Este script demuestra:
- ✅ Callbacks personalizados detallados
- ✅ Captura de eventos de streaming
- ✅ Visualización paso a paso de acciones del agente
- ✅ Herramientas de cálculo geométrico

## 🔧 Características de Streaming

### Dos formas de hacer streaming en LangChain >= 1.0

1. **`agent.stream(..., stream_mode="messages")`** (síncrono, usado en `agent_streaming.py`)
   Entrega tuplas `(chunk, metadata)` con el mensaje parcial del LLM token a token. Es la forma más simple.

2. **`agent.astream_events(..., version="v2")`** (asíncrono, usado en `agent_streaming_avanzado.py`)
   Entrega eventos granulares con nombre y payload, entre ellos:
   - `on_chat_model_stream` - Nuevo token del LLM
   - `on_chat_model_start` / `on_chat_model_end` - Inicio/fin del modelo
   - `on_tool_start` / `on_tool_end` - Inicio/fin de una herramienta
   - `on_chain_start` / `on_chain_end` - Inicio/fin de nodos del grafo interno

> Nota: el contenido de un `AIMessageChunk` puede venir como un `str` plano
> o como una lista de bloques `[{"type": "text", "text": "..."}]` según el
> proveedor. Ambos scripts incluyen una función `extraer_texto()` que
> normaliza los dos formatos.

## 📝 Estructura de un Agente (API actual, LangChain >= 1.0)

> ⚠️ `initialize_agent` y `AgentType` quedaron **deprecados**. La API actual
> construye el agente sobre LangGraph con `create_agent`, y el streaming se
> hace iterando `agent.stream(..., stream_mode="messages")` o con
> `agent.astream_events(...)` para eventos más detallados (async).

```python
from langchain.agents import create_agent
from langchain_core.tools import tool

# 1. Definir herramientas con @tool (import desde langchain_core.tools)
@tool
def mi_herramienta(parametro: str) -> str:
    """Descripción de la herramienta"""
    return resultado

# 2. Crear el agente (acepta un string de modelo o una instancia ChatModel)
agente = create_agent(
    model="gpt-4o-mini",
    tools=[mi_herramienta],
    system_prompt="Eres un asistente útil.",
)

# 3. Ejecutar con streaming token a token
for chunk, metadata in agente.stream(
    {"messages": [{"role": "user", "content": "Tu pregunta aquí"}]},
    stream_mode="messages",
):
    if chunk.content:
        print(chunk.content, end="", flush=True)
```

## 🎯 Casos de Uso

- 📊 Análisis de datos en tiempo real
- 🤖 Chatbots inteligentes
- 🔍 Búsqueda de información
- 📐 Cálculos complejos
- 🎨 Generación de contenido

## ⚙️ Parámetros Importantes

| Parámetro | Descripción |
|-----------|------------|
| `streaming=True` | Habilita streaming de tokens |
| `temperature` | Creatividad (0-1, menor = más determinístico) |
| `model_name` | Modelo a usar (gpt-3.5-turbo, gpt-4, etc.) |
| `max_iterations` | Número máximo de pasos del agente |
| `verbose=True` | Muestra logs detallados |

## 🐛 Solución de Problemas

### Error: "Invalid API Key"
- Verifica que tu OPENAI_API_KEY sea correcta
- Asegúrate de que está configurada como variable de entorno

### Error: "ModuleNotFoundError"
- Instala las dependencias: `pip install -r requirements.txt`
- Verifica que estés en el entorno virtual correcto

### Streaming no funciona
- Asegúrate de que `streaming=True` en ChatOpenAI
- Verifica que hayas pasado los callbacks correctamente

## 📚 Recursos Adicionales

- [LangChain Docs](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)

## 📄 Licencia

Este proyecto es de código abierto y libre para usar.

## ✨ Ejemplos de Uso

### Ejemplo 1: Cálculos
```
Usuario: ¿Cuánto es 15 + 27?
Agente: Usaré la herramienta calcular_suma...
Resultado: 42
```

### Ejemplo 2: Información
```
Usuario: ¿Qué es Python?
Agente: Buscando información sobre Python...
Resultado: Python es un lenguaje de programación...
```

### Ejemplo 3: Tareas Múltiples
```
Usuario: Multiplica 8 por 6 y suma 10
Agente: Primero multiplicaré 8 × 6...
        Luego sumaré 10 al resultado...
Resultado: 58
```

---

¡Disfruta explorando agentes con streaming! 🚀
# agents26_m6s18
