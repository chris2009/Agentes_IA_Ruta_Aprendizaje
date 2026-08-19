# Multimodalidad y Agentes Multimodales — Análisis completo de la Sesión 17

> **Fuente base:** *Agentes IA — Multimodality* (`SES17_M6_Multimodalidad.pdf`, 49 diapositivas) — Módulo 6 (Interacción con el Mundo Físico), Programa en Diseño e Implementación de Agentes IA, UTEC Posgrado. Dictada por MEng. Boris Alzamora.
> **Nota técnica:** el PDF, exportado desde PowerPoint/Google Slides, tiene muy poca capa de texto extraíble — la mayoría de las diapositivas son capturas de pantalla, imágenes de stock y diagramas embebidos como gráficos. Este documento se generó **renderizando cada una de las 49 páginas como imagen e interpretándolas visualmente**, complementado con el texto sí extraíble y con el código del laboratorio del repositorio adjunto (`agents26_m6s17-main/`).
> **Hallazgo clave de esta sesión:** el material cita **explícitamente** dos fuentes externas identificables — (1) la serie de Shaw (Shawhin) Talebi, *"Multimodal Models — LLMs That Can See and Hear"* (Towards Data Science / su repo `YouTube-Blog/multimodal-ai` en GitHub), como base de los "3 caminos" para construir sistemas multimodales (§3), y (2) una charla de **MongoDB en AI Engineer World's Fair 2025** sobre agentes y RAG multimodal (§5), cuyo patrón coincide con el laboratorio público `mongodb-developer/multimodal-agents-lab` (MongoDB + Voyage AI + Gemini/LangGraph). Ambas fuentes se identifican y contrastan con investigación propia en las secciones correspondientes.

---

## 1. Objetivos y Agenda

**Objetivos declarados:**
1. Entender multimodalidad desde los LLMs (*Large Language Models*, modelos de lenguaje de gran escala).
2. Agentes con multimodalidad en el mundo real.

**Agenda completa (dos partes, según las diapositivas 5 y 32):**

| # | Tema |
|---|---|
| 1 | ¿Qué es multimodalidad? |
| 2 | Conceptos fundamentales |
| 3 | Vista al mercado global |
| 4 | Mecanismos de implementación |
| 5 | *MultiModal Agents* |
| 6 | Revisión de implementación multimodal en VSCode |
| 7 | Lab: aterrizando a proyectos — multimodalidad en mi implementación |
| 8 | Multimodal RAG (*Retrieval-Augmented Generation*, generación aumentada por recuperación) |
| 9 | Multimodal Vector Embeddings |
| 10 | Multimodal RAG — repositorio de referencia |
| 11 | Extensibilidad del mundo — Physical AI |

Esta sesión es, dentro del programa, el puente explícito entre los **agentes puramente conversacionales/textuales** (Módulos 4-5) y el tema del **Módulo 6 — "Interacción con el Mundo Físico"**: multimodalidad es el requisito técnico para que un agente pueda "ver, oír y actuar" sobre el mundo real, antes de llegar a robótica y *Physical AI* (§7).

---

## 2. ¿Qué es Multimodalidad? — Definiciones del material

**Definición base (diapositiva 6):**
> *"Habilidad de los modelos de Machine Learning para procesar, comprender, y a veces generar diferentes tipos de data como texto, imágenes, audio, video, etc."*
>
> *"Multimodal large language models (MLLMs) are deep learning algorithms that can understand and generate various forms of content ranging across text, images, video, audio, and more."*

**Data Modality (diapositiva 7):**
> *"La modalidad de datos es un tipo o formato específico de datos que un sistema puede percibir, procesar y del que puede aprender."*

El material traza una analogía directa: así como los humanos usamos distintos **sentidos** para comprender el mundo (vista, oído, tacto), un sistema de IA multimodal usa distintas **modalidades de datos** — y cada modalidad requiere sus propias técnicas de procesamiento (texto → tokenización; imagen → *patches*/convoluciones; audio → espectrogramas; etc.).

**La definición de Jensen Huang / NVIDIA (diapositiva 8), citada textualmente:**
> *"Jensen Huang and Nvidia define multimodality as an advancement in AI that allows systems to process, understand, and generate content from multiple data types simultaneously. Unlike traditional AI that handles only one type of data (like text or images), multimodal AI is trained on diverse data and can interpret the complex relationships between different modalities."*

El matiz que aporta esta segunda definición frente a la primera: no basta con que un sistema *acepte* varios tipos de entrada — la característica distintiva es que interpreta las **relaciones complejas entre modalidades** (p. ej., que la palabra "rojo" en un texto corresponda al color de un objeto específico en una imagen adjunta). Esta idea de relación cruzada entre modalidades es exactamente lo que CLIP (§4) formaliza matemáticamente.

---

## 3. Vista al mercado global — casos de uso de frontera

El material dedica varias diapositivas (9, 12-14) a mostrar el estado del arte comercial, sin mayor comentario textual — se interpretan visualmente:

- **Diapositiva 9 — "Una escuela para Early Adopters":** un mosaico de logos de startups líderes en generación multimodal, agrupadas por modalidad de salida: **Suno** (música), **NotebookLM** (audio/podcast a partir de documentos, Google), **ElevenLabs** (voz), **Higgsfield**, **Pika**, **Runway** (video), **HeyGen** (avatares/video con voz clonada), **Meshy.ai** (modelos 3D). El mensaje implícito: la generación multimodal ya no es "texto → imagen" únicamente — cubre prácticamente cualquier par (modalidad de entrada, modalidad de salida).
- **Diapositiva 10 — Chord diagram de salud digital:** un diagrama circular (*chord diagram*) que conecta 8 **modalidades de datos** de salud (ómica, metabolitos/biomarcadores, microbioma, historia clínica/imágenes, biosensores wearables, sensores ambientales) con 8 **oportunidades** (salud de precisión, ensayos clínicos digitales, hospitalización domiciliaria, vigilancia de pandemias, gemelos digitales, *virtual health coach*). Ilustra que multimodalidad no es solo texto+imagen — en dominios como salud, involucra decenas de señales estructuradas y de sensores.
- **Diapositivas 13-14 — Meta Ray-Ban y Waymo:** el anuncio de **Meta | Ray-Ban** (gafas inteligentes con IA multimodal embebida, captura de foto/video por comando de voz, *"Stay still, taking a look"* reconociendo objetos en una mesa) y una línea de tiempo de **vehículos autónomos** (Waymo, lanzado en 2009 — el pionero, aún operando; GM Cruise, 2013 — servicio de taxi pausado; Amazon Zoox, 2014; Apple, 2014 — proyecto cancelado en 2024; Uber, 2014 — terminado en 2020). Este segundo diagrama es notable porque documenta **cuántos de los grandes intentos de conducción autónoma fracasaron o se cancelaron** (solo Waymo y Zoox siguen activos de los cinco) — un recordatorio de que la promesa de la IA multimodal aplicada al mundo físico tiene una tasa de fracaso alta incluso entre actores con capital prácticamente ilimitado (Apple, Uber).

**Investigación complementaria:** el timeline de la diapositiva 14 es consistente con el registro público — Waymo (originalmente el "Google Self-Driving Car Project") es en efecto el proyecto activo más antiguo del sector, y tanto el proyecto de Apple ("Titan", cancelado formalmente en 2024) como la división de *self-driving* de Uber (vendida a Aurora en 2020 tras un accidente fatal en 2018) son los casos de fracaso más citados en la industria.

---

## 4. Los 3 caminos para construir un sistema multimodal (diapositivas 16-19)

Esta es la sección más estructurada del material teórico, y corresponde **directamente** al framework de **Shaw (Shawhin) Talebi** en su artículo *"Multimodal Models — LLMs That Can See and Hear"* (Towards Data Science / Medium), cuyo repositorio de código se referencia explícitamente en la diapositiva 39 (`github.com/ShawhinT/YouTube-Blog/tree/main/multimodal-ai`).

| Camino | Mecanismo | Pros (según el material) | Contras (según el material) | Ejemplos citados |
|---|---|---|---|---|
| **1. LLM + Tools** | Módulos externos hacen *X-to-text* o *text-to-X* alrededor de un LLM de solo texto (p. ej. `Whisper → LLM → FLUX`) | Simple de implementar; no requiere datos de entrenamiento | Capacidades limitadas; difícil de personalizar | *(implícito: cualquier *tool-calling* agent)* |
| **2. LLM + Adapters** | Se añaden codificadores/decodificadores (p. ej. CLIP, Stable Diffusion) alineados al LLM mediante *fine-tuning* de adaptadores — con partes congeladas (❄) y partes entrenables (🔥) | Mejor personalización; eficiencia de datos | Requiere datos de entrenamiento; técnicamente sofisticado | LLaVA, LLaMA 3.2 Vision, MiniGPT4, Janus, Mini-Omni2, IDEFICS |
| **3. Unified Models** | Se mezclan las modalidades desde el *pre-entrenamiento* (entrenar desde cero con texto+imagen+audio simultáneamente) | Integración de modalidades sin fisuras; inferencia más rápida | Retos técnicos avanzados; requiere datos y cómputo masivos | GPT-4o, Gemini, Emu3, BLIP, Chameleon |

**Por qué esta clasificación importa más allá de la taxonomía:** los tres caminos representan un **espectro de costo de ingeniería vs. calidad** exactamente análogo al framework Workflows-vs-Agents de Anthropic ya documentado en la Sesión 15 (`JUSTIFICACION_AGENTE_VS_WORKFLOW.md`, `Sesion15_LangGraph_MultiAgent_ANALISIS_COMPLETO.md` §4) — Camino 1 es la opción "barata y rápida" (análoga a un *workflow*), Camino 3 es la opción "cara pero nativa" (análoga a construir un modelo propio). **El laboratorio de esta sesión (§6) es, sin ambigüedad, una implementación del Camino 1**: el agente de siniestros no entrena nada — orquesta llamadas a Whisper (audio→texto) y a `gpt-image-1` (texto→imagen) alrededor de un LLM de texto (`gpt-5.1`) vía *tool calling*.

---

## 5. MLLM internamente — CLIP y el embedding compartido (diapositivas 18, 20)

El material muestra el diagrama clásico de **CLIP** (*Contrastive Language-Image Pre-training*, OpenAI, 2021):

```
Texto ("Pepper the aussie pup") ──▶ Text Encoder ──▶ [T1, T2, T3, ..., TN]
Imágenes (N fotos)              ──▶ Image Encoder ─▶ [I1, I2, I3, ..., IN]

Matriz N×N de productos punto Ii·Tj
La diagonal (Ii·Ti) se maximiza durante el entrenamiento (par correcto imagen-texto)
El resto de la matriz se minimiza (pares incorrectos)
```

Esto es el **aprendizaje contrastivo**: el modelo no aprende a "describir" una imagen palabra por palabra — aprende a colocar la imagen y su descripción textual **en el mismo punto** de un espacio vectorial compartido. Es el mecanismo que hace posible que **texto e imagen sean comparables numéricamente** (mismo espacio de *embeddings*), y es la pieza que reaparece en las diapositivas 20 y 37-38 bajo el nombre "CLIP-based Embedding Models" y "Multimodal Embeddings".

**Por qué esto es la base técnica de casi todo lo que sigue en la sesión:** tanto el *Multimodal RAG* (§7) como los *Multimodal Agents* del talk de MongoDB (§6) dependen de poder **buscar por similitud entre una imagen y un texto** — y eso solo es posible si ambos viven en el mismo espacio vectorial, que es exactamente lo que CLIP (o su sucesor comercial, `voyage-multimodal-3`) provee.

---

## 6. Multimodal Agents — el patrón del talk de MongoDB (diapositivas 21-29)

Estas diapositivas (con el logo de MongoDB) reconstruyen, paso a paso, cómo construir un **agente con RAG multimodal**. Es la sección con más contenido técnico reutilizable de toda la sesión.

### 6.1 La ecuación del agente multimodal (diapositiva 23)

```
Multimodal data + Multimodal embedding models + Multimodal LLMs (con tools y memoria) = 🚀 Agente multimodal
```

### 6.2 Dos estrategias para preparar documentos mixtos para recuperación (diapositivas 24-25)

El material presenta **el mismo diagrama dos veces**, con una sola diferencia — el modelo de embeddings final:

| Estrategia | Extracción | Embeddings con | Prompt final al LLM |
|---|---|---|---|
| **A — Texto solamente** | Texto, figuras (con *caption*) y tablas se extraen y **resumen a texto** | **Text Embedding Model** | *Text-only Prompt* |
| **B — Multimodal real** | Igual extracción | **Multimodal Embedding Model** | *Multimodal Prompt* (incluye la imagen original, no solo su descripción) |

La diferencia no es cosmética: en la estrategia A, si el resumen automático de una figura pierde un detalle (ej. un color en un semáforo, un número en una tabla), ese detalle **desaparece permanentemente** antes de llegar al LLM. En la estrategia B, la imagen original llega intacta al modelo — el *embedding* solo se usa para decidir **qué recuperar**, no reemplaza a la imagen en el prompt final.

### 6.3 "Screenshots are all you need" (diapositivas 27-28)

Un patrón deliberadamente simplificador: en lugar de parsear cada documento en texto+figuras+tablas por separado (con todo el riesgo de pérdida de información que eso implica), se toma un **screenshot de cada página completa** del documento y se embebe *la página entera como imagen* con un modelo de embeddings multimodal:

```
Documentos → Screenshots (páginas) → voyage-multimodal-3 → Embeddings → MongoDB
                    │
                    └──▶ Blob storage (las imágenes originales)
```

Esto evita por completo el problema de "¿cómo extraigo bien esta tabla/gráfico?" — la respuesta es: no lo extraigas, trata la página como una imagen y deja que el modelo de embeddings multimodal (entrenado sobre pares imagen-texto tipo CLIP) capture su contenido visual y textual a la vez.

### 6.4 El bucle completo del agente (diapositiva 29)

```
User ──Question──▶ Agent ──{"query": "..."}──▶ Vector search ──▶ MongoDB
 ▲                   │  ▲                            │
 └──────Answer────────┘  └────────Image IDs───────────┘
                     │
                     ├──Question + Images──▶ Multimodal LLM ──Answer──▶ (vuelve al Agent)
                     │
                     └──Image IDs / Images──▶ Blob storage
```

El **Agent** es el orquestador: recibe la pregunta del usuario, la convierte en una consulta de *vector search*, recupera los IDs de las imágenes relevantes desde MongoDB, obtiene las imágenes reales desde el *blob storage*, arma un prompt con pregunta+imágenes y se lo pasa al LLM multimodal, y devuelve la respuesta.

### 6.5 Investigación complementaria — la fuente exacta

Este patrón corresponde a la charla de **MongoDB en AI Engineer World's Fair 2025** (San Francisco), y coincide en cada pieza con el laboratorio público que MongoDB mantiene en GitHub: **`mongodb-developer/multimodal-agents-lab`** — un laboratorio *self-contained* que construye exactamente este agente usando **MongoDB** (como *vector store* y almacén de metadatos), **Voyage AI** (`voyage-multimodal-3`, el modelo de *embeddings* multimodal mencionado literalmente en la diapositiva 28) y **Gemini** (como LLM multimodal) orquestado con **LangGraph**. El blog técnico *"Building Multimodal AI Applications With MongoDB, Voyage AI, and Gemini"* (dev.to/mongodb) documenta el mismo flujo: *screenshot → embedding multimodal → vector search → LLM multimodal con la imagen original*.

---

## 7. Caso práctico del curso — agente de siniestros de tránsito (`agents26_m6s17-main/`)

El repositorio adjunto a la sesión implementa, en Python puro (LangChain `create_agent` + OpenAI), un **agente multimodal end-to-end siguiendo exactamente el Camino 1 (LLM + Tools) de §4** — la opción "simple de implementar, sin entrenamiento" del framework de Shaw Talebi.

### 7.1 El dominio: reportes de siniestros para una aseguradora ficticia ("Calma S.A.")

**System prompt del agente** (`main.py`): *"Eres un especialista en la toma de información de los accidentes de tránsito... tu objetivo principal es redactar el reporte de accidentes... apóyate de tus herramientas para obtener un caso y la información asociada..."*

### 7.2 Las 4 herramientas — cada una resuelve una modalidad distinta

| Herramienta | Modalidad de entrada | Modalidad de salida | Mecanismo |
|---|---|---|---|
| `obtener_caso` | Texto (archivo `.txt` en `./casos/`) | Texto | Lectura de archivo plano — el "caso base" (parte policial) |
| `obtener_entrevista` | **Audio** (`.m4a`, podcast de noticiero) | Texto | **Whisper** (`whisper-1` de OpenAI) — *speech-to-text* |
| `generar_croquis_accidente` | Texto (descripción del accidente) | **Imagen** | **`gpt-image-1`** — *text-to-image*, genera un collage con el croquis de posiciones de vehículos |
| `guardar_reporte` | Texto (Markdown con referencia a la imagen) | Archivo `.md` | Persiste el reporte final referenciando la imagen ya generada |

Esto es, literalmente, el diagrama *"Path 1: LLM + Tools"* de la diapositiva 16 (`Whisper → LLM → FLUX`) pero con herramientas reales de producción: Whisper para audio→texto y `gpt-image-1` (en vez de FLUX) para texto→imagen, todo orquestado por un único LLM de texto (`gpt-5.1`) que decide **cuándo** llamar a cada una.

### 7.3 Traza real de un caso (caso `00012025`)

El repositorio incluye datos completos para un caso simulado, que permiten ver el flujo multimodal de principio a fin:

1. **`casos/caso001.txt`** — el parte policial base: choque entre un Toyota Corolla (conductora Ana María Rojas) y una Honda CR-V (conductor Juan Carlos Pérez) en Miraflores, Lima — con testigos, versiones contrapuestas (quién cruzó en rojo) y datos de seguros (Pacífico vs. Rímac).
2. **`transcripts/transcript_llamada_accidente.md`** — la transcripción (vía Whisper, simulando `obtener_entrevista`) de la llamada telefónica de la aseguradora con la clienta, con una tabla resumen y notas internas del agente humano de atención — un detalle adicional que **no estaba en el parte policial** (p. ej. que el vehículo quedó operativo y fue conducido hasta el domicilio).
3. **`images/...imagen.png`** — el croquis generado por `gpt-image-1` a partir de la descripción textual del accidente.
4. **`reportes/...report.md`** — el reporte final en Markdown, que **combina las tres fuentes** (parte policial + transcripción + croquis generado) en un documento estructurado de 11 secciones, incluyendo un "Análisis Preliminar de Responsabilidad" que cruza las versiones de ambos conductores con las declaraciones de los dos testigos independientes.

**Por qué este caso es un buen ejemplo pedagógico:** no es un demo de juguete de "generar una imagen bonita" — muestra el patrón real de un **agente de *back-office*** que tiene que **fusionar evidencia de múltiples modalidades y múltiples fuentes potencialmente contradictorias** (el conductor de la camioneta dice que cruzó en ámbar; el testigo dice que fue en rojo) para producir un documento auditable. Es el mismo tipo de problema — reconciliar fuentes heterogéneas bajo incertidumbre — que aparece en cualquier dominio regulado (salud, seguros, cumplimiento normativo).

### 7.4 `singlemodel.ipynb` — comparación directa: visión local vs. visión en la nube

El notebook complementario es, en efecto, un **benchmark informal** entre dos formas de resolver "leer una imagen y estructurarla como JSON", usando la misma imagen de prueba (`cheque.jpg`, un cheque bancario real fotografiado):

| Modelo | Tipo | Resultado sobre el mismo cheque |
|---|---|---|
| **LLaVA** (vía `ollama.generate`, local) | Modelo de visión open-source, corre en la máquina del alumno | **Alucina datos**: identifica "Banca Continental" (el banco real es BBVA Continental), un monto de "1230 pesos" (el monto real en el cheque es S/ 4,758.00) y un nombre de cliente inventado |
| **GPT-4o-mini** (vía API de OpenAI, *chat.completions* con imagen en Base64) | Modelo de visión propietario en la nube | Lee correctamente el banco (BBVA Continental), el monto exacto (S/ 4,758.00), el beneficiario y la fecha, y los estructura en un JSON limpio |

**Esto no es un detalle menor del notebook — es el hallazgo más concreto y verificable de toda la sesión**: para una tarea de OCR/lectura estructurada de un documento financiero real, el modelo local gratuito (`llava`, corriendo en Ollama) produjo **datos incorrectos con la misma confianza aparente** que el modelo correcto. Es la ilustración práctica y con evidencia directa de por qué, en el checklist Workflows-vs-Agents de Anthropic (Sesión 15, §4.2), el criterio *"costo del error"* es central: si este agente usara LLaVA para procesar cheques reales sin verificación humana, produciría reportes financieros con montos incorrectos, sin que el sistema lo señale como incierto.

El notebook continúa con dos casos adicionales de visión estructurada (`supermercado.jpg` — análisis de riesgos de seguridad; `condensadores.jpg` — inventario de riesgos en un *data center*) y cierra con generación de contenido: una imagen editorial de moda (`gpt-image-1`) y **dos videos generados con Sora-2** (`client.videos.create`, modelo `sora-2`, incluyendo *polling* del estado de renderizado y descarga del binario vía `videos.download_content`) — uno de un paisaje de montaña, y uno, con humor autoreferencial, de un *"YouTuber"* generado por IA diciendo *"¿me acaba de generar una IA para enseñarte sobre IA? Qué meta..."*.

---

## 8. Multimodal RAG — los 3 niveles (diapositivas 34-38)

Retomando el mismo repositorio de Shaw Talebi (`YouTube-Blog/multimodal-ai`, referenciado en la diapositiva 39 junto a un artículo de Medium y uno de IBM sobre Multimodal RAG), el material presenta 3 niveles progresivos de sofisticación para hacer RAG sobre documentos con contenido mixto (texto + figuras + tablas):

| Nivel | Nombre | Recuperación | Prompt al LLM | Pérdida de información |
|---|---|---|---|---|
| **1** | *Translate everything to text* | Texto plano — todo (texto, *captions* de figuras, *captions* generados de imágenes) se convierte a texto antes de indexar | *Text-only Prompt* | **Alta** — la imagen original nunca llega al LLM, solo su descripción textual |
| **2** | *Text-only retrieval + MLLM* | Igual indexación en texto | **Multimodal Prompt** — se recupera el texto, pero se adjunta la **modalidad original** (imagen, tabla) al prompt final | Media — la búsqueda puede fallar si la consulta depende de algo visual que el texto no captura bien |
| **3** | *Multimodal retrieval + MLLM* | *Vector search* con **embeddings multimodales** — el texto y las imágenes/tablas se embeben en el mismo espacio vectorial | Multimodal Prompt | **Mínima** — tanto la búsqueda como la respuesta usan la información original |

Esta progresión es idéntica en estructura a la de §6.2 (estrategias A/B del talk de MongoDB) — confirma que ambas fuentes del material (Shaw Talebi y MongoDB) convergen en la misma conclusión práctica: **el punto donde más se pierde información en un sistema multimodal no es la generación final, es la etapa de recuperación** — si el motor de búsqueda solo entiende texto, nunca vas a recuperar la imagen correcta aunque el LLM final sea perfectamente multimodal.

**El problema de fondo — espacios de embeddings no alineados (diapositivas 36-38):** el material ilustra con un ejemplo simple por qué el Nivel 3 requiere un modelo *entrenado específicamente* para esto (como CLIP o `voyage-multimodal-3`) y no basta con tener "un embedding de texto" y "un embedding de imagen" por separado: si se embeben con modelos independientes, el texto *"a cute puppy"* y una foto de un cachorro caen en **posiciones completamente distintas** de dos espacios vectoriales distintos — no son comparables entre sí (`Note: Text and image embedding dimensions are not aligned`). Solo un modelo multimodal entrenado contrastivamente (§5) logra que texto e imagen relacionados caigan cerca **en el mismo espacio**.

---

## 9. Extensibilidad del mundo — Physical AI (diapositivas 40-47)

La última sección conecta multimodalidad con el tema central del **Módulo 6**: llevar los agentes del mundo digital al mundo físico. El material se apoya fuertemente en material público de **NVIDIA** (keynotes de Jensen Huang, incluyendo un fragmento explícitamente marcado como del **NVIDIA GTC Keynote de marzo de 2026**).

### 9.1 La curva de evolución de la IA, según Jensen Huang (diapositiva 41)

```
2012 AlexNet
   │
   ▼
Perception AI  →  Generative AI  →  Agentic AI  →  Physical AI
(speech recog.,   (digital           (coding          (autonomous
 deep recsys,      marketing,         assistant,        vehicles,
 medical imaging)  content            customer          general
                    creation)          service,          robotics)
                                       patient care)
```

Titular citado: *"NVIDIA's Jensen Huang says the next wave of AI is Physical AI."* La lectura que propone el material: cada "ola" de IA no reemplaza a la anterior, se **construye sobre** ella — un robot físico (*Physical AI*) necesita percepción (visión, audio — Perception AI), necesita poder generar/planificar contenido y acciones (Generative AI), y necesita poder decidir su propia trayectoria de acciones (Agentic AI, el mismo concepto ya cubierto en la Sesión 15) — *antes* de poder actuar de forma autónoma en el mundo físico.

### 9.2 Herramientas concretas mostradas

- **NVIDIA Omniverse + Cosmos** — descrito como *"Physical AI Digital Twin Operating System"*: se entrena/simula a un robot en un **gemelo digital estilizado** (Omniverse) y ese comportamiento se transfiere a un modelo foto-realista (Cosmos) que sirve de puente hacia el control del robot físico real.
- **CUDA-X libraries** — el material muestra el catálogo de más de una decena de librerías aceleradas por GPU (cuLitho, cuOpt, Warp, cuDF/cuML, Megatron/NIXL para *deep learning*, cuEquivariance para química cuántica, Earth-2 para clima, MONAI para imágenes médicas, Parabricks para genómica, Aerial/Sionna para 5G/6G) — el mensaje es que *Physical AI* no es un producto aislado sino que se apoya en toda la pila de cómputo acelerado de NVIDIA.
- **Robots humanoides** — dos ejemplos visuales: un robot doméstico haciendo tareas de cocina (estilo *1X Neo*) y un robot industrial con casco de NVIDIA en un entorno de fábrica (colaboración NVIDIA + Fourier Intelligence, sobre estación NVIDIA DGX).

### 9.3 Síntesis del material — 5 pilares de la "extensibilidad del mundo" (diapositiva 46)

Sobre una imagen de la exhibición de robots de NVIDIA (excavadoras, brazos robóticos industriales, humanoides y autos autónomos compartiendo un mismo escenario), el material identifica 5 capacidades que definen hacia dónde se extiende un agente multimodal:

1. **Prompt to Anything** — de un *prompt* de texto a cualquier modalidad de salida (imagen, video, audio, acción física).
2. **Multi Agent Systems of Multimodal Inputs** — sistemas multiagente (Sesión 15) donde cada entrada que reciben puede ser de una modalidad distinta.
3. **Autonomy of Modality** — el agente elige *qué modalidad* usar según la tarea, sin que un humano se lo indique explícitamente.
4. **Digital Twins of the planet** — simulación a escala de entornos reales (Omniverse/Cosmos, Earth-2).
5. **Physical AI Robotics** — el punto de llegada: acción física real en el mundo, no solo generación de contenido.

Esta lista funciona como **el cierre conceptual de todo el Módulo 6**: la Sesión 17 (multimodalidad) es el prerequisito técnico de las sesiones posteriores del módulo dedicadas a robótica y agentes físicos — sin percepción y generación multimodal, un agente no tiene forma de "ver" el mundo físico ni de expresar una acción sobre él.

---

## 10. Laboratorios y tarea de la sesión

| Actividad | Instrucción |
|---|---|
| **Lab — Explorando Multimodalidad** | Hacer un *mock* con modelos multimodales disponibles (Ollama/LLaVA, ChatGPT, u otro) — el ejercicio que se ve desarrollado en `singlemodel.ipynb`. |
| **Lab — Aterrizando a proyectos** | Reflexionar sobre el proyecto personal del alumno: ¿qué capacidades multimodales tiene o necesita? ¿Cómo se implementarían? |
| **Tarea PERSONAL — Multimodal** | Con MLLMs, implementar un agente personal que realice un **cambio de modalidad** en la información (p. ej. audio→texto→imagen, como el agente de siniestros de este material). **Fecha límite: 19/08.** |

---

## 11. Síntesis — lo que hay que llevarse de esta sesión

1. **Multimodalidad no es "aceptar varios tipos de archivo"** — según la propia definición de NVIDIA citada en el material, la característica distintiva es interpretar **relaciones entre modalidades**, lo cual solo es posible cuando texto e imagen comparten un mismo espacio vectorial (CLIP, §5).
2. **Existen 3 caminos de ingeniería, no uno solo, para hacer un sistema multimodal** (Shaw Talebi, §4): LLM+Tools (barato, sin entrenamiento — el que usa el laboratorio del curso), LLM+Adapters (requiere *fine-tuning*, mejor personalización) y Unified Models (requiere entrenar desde cero, mejor integración). La elección es la misma disyuntiva costo-vs-calidad que Workflows-vs-Agents en la Sesión 15.
3. **Un agente multimodal en producción (patrón MongoDB, §6) necesita 3 piezas**: datos multimodales, un modelo de *embeddings* multimodal para poder **buscar**, y un LLM multimodal con herramientas y memoria para poder **razonar y actuar** sobre lo recuperado.
4. **El punto donde más se pierde información en un pipeline multimodal es la etapa de recuperación, no la de generación** (§8) — si el buscador solo indexa texto, ninguna imagen relevante llegará jamás al LLM final, sin importar qué tan bueno sea ese LLM.
5. **El costo de un modelo de visión equivocado es silencioso y real**: la comparación LLaVA vs. GPT-4o-mini sobre el mismo cheque (§7.4) no es solo un ejercicio de clase — mostró datos financieros alucinados con la misma confianza aparente que los datos correctos, evidencia directa de por qué la elección de modelo importa más en dominios de alto costo de error (Sesión 15, checklist de Anthropic).
6. **Esta sesión es el puente formal del programa hacia Physical AI** (§9): la curva Perception → Generative → Agentic → Physical AI de Jensen Huang encapsula por qué el Módulo 6 empieza con multimodalidad antes de llegar a robótica — sin percepción multimodal, no hay agente físico posible.

---

## 12. Checklist práctico — diseñando un sistema multimodal

- [ ] ¿Qué modalidades necesita procesar mi agente en la entrada (texto, audio, imagen, video)? ¿Y en la salida?
- [ ] Dado el presupuesto de ingeniería disponible, ¿me conviene el Camino 1 (LLM+Tools, orquestar modelos ya entrenados), el 2 (adaptadores con *fine-tuning*) o el 3 (modelo unificado)? Por defecto, empezar por el Camino 1.
- [ ] Si el sistema necesita **recuperar** contenido multimodal (RAG), ¿estoy en el Nivel 1 (todo a texto — pierdo información), Nivel 2 (recupero por texto pero paso la modalidad original al LLM) o Nivel 3 (embeddings multimodales de punta a punta)?
- [ ] ¿El modelo de *embeddings* que uso para texto e imagen está entrenado para un **espacio compartido** (tipo CLIP / `voyage-multimodal-3`), o son dos modelos independientes cuyos vectores no son comparables entre sí?
- [ ] Para tareas de visión con consecuencias reales (documentos financieros, reportes legales, diagnósticos): ¿validé la precisión del modelo elegido (local vs. cloud) con casos de prueba conocidos, o estoy asumiendo que "ve bien" sin verificarlo?
- [ ] ¿El caso de uso requiere solo **entender** contenido multimodal (percepción) o también **generar** contenido en otra modalidad (imagen, video, audio)? Cada dirección tiene herramientas y costos distintos.
- [ ] Si el agente eventualmente debe actuar sobre el mundo físico: ¿qué capa de percepción multimodal (visión, audio) es prerequisito antes de considerar actuadores/robótica?

---

## 13. Referencias

**Del material original:**
- Diagramas y capturas propias del curso — definiciones de multimodalidad, casos de mercado (Suno, NotebookLM, ElevenLabs, HeyGen, Meta Ray-Ban, Waymo), los 3 caminos (LLM+Tools/Adapters/Unified), CLIP internamente, patrón de agente multimodal, niveles de Multimodal RAG, curva Perception→Physical AI de NVIDIA.
- Shaw (Shawhin) Talebi — *"Multimodal Models — LLMs That Can See and Hear"* (Towards Data Science / Medium) y repositorio [`github.com/ShawhinT/YouTube-Blog/tree/main/multimodal-ai`](https://github.com/ShawhinT/YouTube-Blog/tree/main/multimodal-ai) — fuente de los "3 caminos" (§4) y de los "3 niveles de Multimodal RAG" (§8).
- MongoDB — charla en **AI Engineer World's Fair 2025** sobre *Multimodal Agents* y *Multimodal RAG* (§6).
- Medium — *"Multimodal RAG: Process Any File Type with AI"*; IBM — *"What is Multimodal RAG?"* ([ibm.com/think/topics/multimodal-rag](https://www.ibm.com/think/topics/multimodal-rag)).
- NVIDIA — keynotes públicos de Jensen Huang (incluyendo fragmento del NVIDIA GTC Keynote, marzo 2026) sobre Physical AI, Omniverse, Cosmos y CUDA-X.

**Investigación complementaria (añadida en este documento):**
- Verificación del framework de Shaw Talebi y sus 3 caminos (LLM+Tools/Adapters/Unified Models) contra su publicación original en Towards Data Science.
- Verificación del patrón del talk de MongoDB contra el laboratorio público [`mongodb-developer/multimodal-agents-lab`](https://github.com/mongodb-developer/multimodal-agents-lab) (MongoDB + Voyage AI `voyage-multimodal-3` + Gemini/LangGraph) y el artículo técnico *"Building Multimodal AI Applications With MongoDB, Voyage AI, and Gemini"* (dev.to/mongodb).
- Contexto histórico del timeline de vehículos autónomos (§3): confirmación de que Waymo es el proyecto activo más antiguo del sector, y que los proyectos de Apple ("Titan") y Uber (vendido a Aurora tras el accidente fatal de 2018) son los casos de fracaso/cancelación más documentados de la industria.
- Análisis propio del caso práctico del laboratorio (`agents26_m6s17-main/`, §7): trazabilidad completa del caso de siniestro `00012025` a través de sus 4 fuentes (parte policial, transcripción de llamada, croquis generado, reporte final), y lectura del *benchmark* informal LLaVA-vs-GPT-4o-mini sobre el cheque bancario como evidencia concreta del riesgo de alucinación en modelos de visión locales para documentos financieros reales.
- Arco interno del curso: `Sesion15_LangGraph_MultiAgent_ANALISIS_COMPLETO.md` (Módulo 5) — el framework Workflows-vs-Agents de Anthropic ahí documentado es la misma lógica costo-vs-calidad que estructura los "3 caminos" de esta sesión (§4) y el criterio de "costo del error" que explica por qué la elección LLaVA-vs-GPT-4o (§7.4) importa en la práctica.

---

*Documento generado a partir del PDF de la Sesión 17 (Módulo 6, UTEC Posgrado) — 49 diapositivas renderizadas e interpretadas visualmente + código y datos del laboratorio adjunto (`agents26_m6s17-main/`) — más investigación propia sobre las fuentes citadas (Shaw Talebi, MongoDB/AI Engineer World's Fair 2025, NVIDIA).*
