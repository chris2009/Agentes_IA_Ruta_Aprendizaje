# Tarea Multimodal — Bitácora de Estudio (Sesión 17)

Agente personal que convierte una nota de voz sobre una sesión del programa en una
**nota de estudio en Markdown** + una **imagen conceptual (infografía)** — un cambio
de modalidad en cadena: **audio → texto → imagen**.

Implementa el patrón *"Camino 1: LLM + Tools"* documentado en
[`../Sesion17_Multimodalidad_ANALISIS_COMPLETO.md`](../Sesion17_Multimodalidad_ANALISIS_COMPLETO.md)
§4, con el mismo estilo que `agents26_m6s17-main/main.py` (agente de siniestros de
la clase): un LLM de texto (`gpt-4o-mini`) orquesta 3 *tools* vía *tool calling*,
sin entrenar nada.

## Instalación

Este proyecto reutiliza el entorno virtual ya creado en
`Modulo4_Agentes_Cognitivos/.venv` (WSL — Windows Subsystem for Linux), que ya
tiene `langchain`, `langchain_openai`, `openai` y `python-dotenv` instalados.
No hace falta instalar nada nuevo; solo hay que invocarlo **desde WSL**, no
desde PowerShell/Git Bash directo (el venv apunta a un intérprete de WSL).

```bash
cp .env.example .env
# completa OPENAI_API_KEY y, si quieres trazabilidad, LANGSMITH_API_KEY
```

(`requirements.txt` queda documentado por si en algún momento se crea un venv
propio para esta carpeta.)

`LANGSMITH_TRACING=true` en el `.env` es suficiente para que LangChain/LangGraph
manden la traza completa del agente (qué tool llamó, en qué orden, con qué
argumentos, tokens y latencia) a [smith.langchain.com](https://smith.langchain.com) —
no requiere cambios de código.

## Uso

1. Graba una nota de voz (1-2 min) contando qué aprendiste en una sesión del
   programa — tema, ideas clave, cómo se conecta con otras sesiones.
2. Colócala en `./audios/` (cualquier formato que acepte Whisper: `.m4a`, `.mp3`,
   `.wav`, ...).
3. Ejecuta (desde WSL, usando el venv de `Modulo4_Agentes_Cognitivos`):

```bash
wsl -e bash -lc "cd /mnt/d/APRENDIZAJE/PROGRAMA_IMPLEMENTACION_AGENTES_IA/Modulo6_Interaccion_Fisica_Mundo_Real/Sesion17_Multimodal_Agents/Tarea_Multimodal_Personal && /mnt/d/APRENDIZAJE/PROGRAMA_IMPLEMENTACION_AGENTES_IA/Modulo4_Agentes_Cognitivos/.venv/bin/python main.py mi_nota_de_voz.m4a"
```

O, ya dentro de una sesión de WSL:

```bash
cd /mnt/d/APRENDIZAJE/PROGRAMA_IMPLEMENTACION_AGENTES_IA/Modulo6_Interaccion_Fisica_Mundo_Real/Sesion17_Multimodal_Agents/Tarea_Multimodal_Personal
/mnt/d/APRENDIZAJE/PROGRAMA_IMPLEMENTACION_AGENTES_IA/Modulo4_Agentes_Cognitivos/.venv/bin/python main.py mi_nota_de_voz.m4a
```

(Si no pasas argumento, busca por defecto `./audios/nota_voz.m4a`.)

El agente:
1. Transcribe el audio (`transcribir_audio` → Whisper).
2. Redacta la nota de estudio en Markdown (razonamiento del propio LLM, sin tool).
3. Genera una infografía conceptual de los puntos clave (`generar_imagen_conceptual` → `gpt-image-1`).
4. Guarda la nota en `./notas/` con la imagen ya referenciada, y la imagen en `./imagenes/`.

## Herramientas (tools) del agente

| Tool | Modalidad | Motor |
|---|---|---|
| `transcribir_audio` | audio → texto | Whisper (`whisper-1`) |
| *(sin tool — el LLM redacta la nota)* | texto → texto estructurado | `gpt-4o-mini` |
| `generar_imagen_conceptual` | texto → imagen | `gpt-image-1` |
| `guardar_nota` | persistencia | filesystem |

## Evidencia para el entregable

Para el `ENTREGA_GOOGLE_DOC.md` de esta tarea, capturar:
- La nota `.md` generada y la imagen conceptual resultante.
- Una captura de la traza en LangSmith (URL del *run*: `smith.langchain.com/o/.../projects/p/tarea-multimodal-bitacora-estudio`) mostrando el orden real de las 3 tool calls.
- El texto de salida del terminal (`python main.py ...`).
