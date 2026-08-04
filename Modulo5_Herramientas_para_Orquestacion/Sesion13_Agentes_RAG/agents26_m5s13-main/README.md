# agents26_m5s13 — Guía práctica de RAG

Proyecto de ejemplo que implementa un sistema **RAG (Retrieval-Augmented Generation)** aplicado a reseñas de comida peruana hechas por youtubers. Combina una base de datos vectorial (Chroma) con un **agente de LangChain 1.x** (`create_agent`) capaz de decidir cuándo buscar en la base de reseñas y cuándo complementar con búsqueda web (Tavily).

Este repo está pensado como material de estudio: cada archivo cubre una etapa distinta del pipeline de RAG, desde la carga y vectorización de datos hasta el agente conversacional con salida estructurada.

## ¿Qué es RAG?

**RAG (Retrieval-Augmented Generation)** es una técnica que combina la recuperación de información con la generación de texto mediante modelos de lenguaje. En lugar de depender únicamente del conocimiento que un modelo aprendió durante su entrenamiento, un sistema RAG primero busca (recupera) fragmentos relevantes de una fuente externa de datos y luego usa esa información como contexto para generar una respuesta más precisa y fundamentada, reduciendo el riesgo de respuestas inventadas ("alucinaciones").

## Estructura del proyecto

```
agents26_m5s13/
├── data/              # Dataset con las reseñas de comida peruana (CSV)
├── init.ipynb         # Notebook exploratorio: carga, chunking y pruebas de RAG
├── vector.py           # Carga el CSV, genera embeddings y crea el vector store (Chroma)
├── toolbox.py          # Tools del agente: búsqueda en el vector store y búsqueda web (Tavily)
├── prompt.py            # System prompt del agente
├── main.py              # Punto de entrada: agente conversacional en consola
└── requirements.txt      # Dependencias del proyecto
```

## Componentes

### `vector.py` — Vector store con Chroma

Carga las reseñas desde `data/data.csv`, genera un `Document` de LangChain por cada fila (nombre del restaurante, autor, calificación, plato estrella, distrito, tipo de comida) y las indexa en una colección de **Chroma** persistente en disco. Soporta dos proveedores de embeddings intercambiables:

- **OpenAI** (`OpenAIEmbeddings`)
- **Ollama** local (`OllamaEmbeddings`, modelo `mxbai-embed-large`)

Expone una variable global `retriever` que el resto del proyecto usa para hacer búsquedas semánticas (`search_kwargs={"k": 5}`).

### `toolbox.py` — Tools del agente

Define dos herramientas (`@tool`) que el agente puede invocar según la consulta del usuario:

- **`buscar_reviews_comida_peruana`**: busca en el vector store de Chroma reseñas relevantes de youtubers.
- **`buscar_con_tavily`**: complementa con búsqueda web en tiempo real (historia de platos, restaurantes nuevos, datos que no están en el dataset local), devolviendo título, contenido y fuente de cada resultado encontrado.

El agente decide de forma autónoma cuál tool usar (o ambas) según la consulta, y reporta en la salida estructurada (`tools_usadas`) cuáles empleó para responder.

### `prompt.py` — Instrucciones del agente

Contiene el `system_prompt` que define el rol, tono y reglas de comportamiento del agente (cuándo usar cada tool, cómo citar fuentes, etc.).

### `main.py` — Agente conversacional

Construye el agente con `create_agent` de `langchain.agents`, define una salida estructurada (`ResearcherResponse`, un modelo de Pydantic con `descripcion_plato`, `recomendaciones`, `referencias` y `tools_usadas`) y corre un loop de consola donde el usuario puede chatear con el agente hasta escribir `salir`.

## Requisitos

- Python 3.11+
- Cuenta y API key de [OpenAI](https://platform.openai.com)
- (Opcional) [Ollama](https://ollama.com) instalado localmente si prefieres embeddings locales en vez de OpenAI
- Cuenta y API key de [Tavily](https://tavily.com) para la tool de búsqueda web

## Instalación

```bash
git clone https://github.com/alzamoralabs/agents26_m5s13.git
cd agents26_m5s13
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

pip install -r requirements.txt
```

<details>
<summary>Ver dependencias principales (<code>requirements.txt</code>)</summary>

```pip-requirements
langchain==1.3.14
langchain-openai==0.0.19
langchain-community==0.4.2
langchain-chroma==1.1.0
langchain-ollama>=0.3.0
langchain-text-splitters>=1.0.0
python-dotenv==1.2.2
pypdf==6.14.2
chromadb==1.5.9
beautifulsoup4==4.15.0
tavily-python==0.7.26
pandas>=2.2.0
pydantic==2.12.4
pydantic-settings>=2.12.0
```

</details>

## Configuración

Crea un archivo `.env` en la raíz del proyecto con tus llaves:

```
OPENAI_API_KEY=tu_api_key_de_openai
TAVILY_API_KEY=tu_api_key_de_tavily
```

## Uso

### 1. Generar el vector store

Antes de correr el agente, asegúrate de que la base de datos vectorial exista. Ejecuta:

```bash
python vector.py
```

Esto crea (si no existe aún) una carpeta `./chroma_openai_rest_reviews` o `./chroma_ollama_rest_reviews` con los embeddings de `data/data.csv`.

### 2. Correr el agente

```bash
python main.py
```

El programa te pedirá una consulta en consola. Por ejemplo:

```
Ingrese su consulta (o 'salir' para terminar): cuál es el mejor ceviche de Lima según los youtubers
```

El agente responderá con una salida estructurada:

```
Descripción del plato: ...
Recomendaciones: ...
Referencias: [...]
Herramientas usadas: [...]
```

Escribe `salir` para terminar la sesión.

### 3. Explorar el notebook

`init.ipynb` contiene ejemplos paso a paso de carga de documentos, *chunking* con `RecursiveCharacterTextSplitter` y pruebas del pipeline de RAG, útil para entender cada etapa antes de verla integrada en el agente.

## Stack técnico

| Componente | Librería |
|---|---|
| Orquestación de agentes | `langchain` 1.3.14 (`create_agent`) |
| Vector store | `langchain-chroma` + `chromadb` |
| Embeddings | `langchain-openai` / `langchain-ollama` |
| Carga y manejo de datos | `pandas` |
| Búsqueda web | `tavily-python` |
| Validación de datos / salida estructurada | `pydantic` + `pydantic-settings` |
| Carga de PDFs (notebook) | `pypdf` |
| Web scraping (notebook) | `beautifulsoup4` |
| Variables de entorno | `python-dotenv` |

## Notas y problemas conocidos

- El agente usa `recursion_limit` configurado explícitamente en `main.py` como salvaguarda ante bucles de tool-calling, aunque ya no es el mecanismo principal de control (ver siguiente punto).
- `buscar_con_tavily` (en `toolbox.py`) ahora formatea y devuelve los resultados reales de Tavily (título, contenido y fuente de cada resultado), en vez de un mensaje genérico. Esto fue clave para evitar que el agente reintentara la búsqueda indefinidamente al no recibir información útil.
- `langchain-chroma`/`chromadb` requieren `pydantic-settings` instalado cuando se usa `pydantic >= 2.12`, para evitar errores de importación (`BaseSettings` se movió a ese paquete separado).

## Licencia

Este proyecto es material educativo. Ajusta esta sección según la licencia que quieras aplicar (MIT, Apache 2.0, etc.).