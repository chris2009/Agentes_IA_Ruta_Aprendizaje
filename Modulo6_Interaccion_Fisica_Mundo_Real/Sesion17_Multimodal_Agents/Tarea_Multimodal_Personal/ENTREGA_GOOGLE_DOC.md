# Bitácora de Voz

**Tarea Sesión 17 (Multimodalidad) — Programa Diseño e Implementación de Agentes IA, UTEC Posgrado.**
Tipo: PERSONAL. Fecha límite: 19/08.

## OBJETIVO

La consigna pedía probar con MLLMs (*Multimodal Large Language Models*, modelos de lenguaje multimodales) una implementación personal, por medio de un agente, que haga un cambio de modalidad en la información. En vez de armar una demo de una sola llamada, hice algo que uso de verdad mientras curso el programa: grabo un audio contando qué aprendí en una sesión, y el agente lo convierte en una nota de estudio y una imagen que resume los conceptos.

## DESCRIPCION DEL AGENTE

Le puse el nombre "Bitácora de Voz". Recibe el nombre de un archivo de audio y hace tres cosas en orden: lo transcribe, redacta con eso una nota de estudio en Markdown, y genera una infografía con los conceptos clave. Guarda los dos archivos y me devuelve un resumen de lo que hizo.

Elegí este caso entre varias opciones (una foto de recibo estructurada en JSON, o texto convertido directo a imagen) porque este sí encadena dos cambios de modalidad de verdad (audio→texto→imagen) y me queda algo que voy a seguir usando, no una prueba de una sola vez.

Solo le di tools donde hacía falta un modelo distinto al de texto:

| Tool | Qué hace | Modelo |
|---|---|---|
| `transcribir_audio` | pasa el audio a texto | Whisper |
| `generar_imagen_conceptual` | genera la infografía | gpt-image-1 |
| `guardar_nota` | guarda el .md en disco | — |

Redactar la nota no es una tool, eso lo hace el LLM (`gpt-4o-mini`) directamente razonando sobre la transcripción — igual que en el agente de siniestros del material de la clase (`agents26_m6s17-main/main.py`), que tampoco tiene una tool para "redactar".

## ARQUITECTURA

```
audio (.m4a) → transcribir_audio (Whisper) → el LLM redacta la nota
                                                    → generar_imagen_conceptual (gpt-image-1)
                                                    → guardar_nota
```

Lo corrí con LangSmith activado (`LANGSMITH_TRACING=true`) para poder ver si el orden que armé en el *system prompt* se respetaba de verdad. La traza (captura en `Tracing.png`, esta misma carpeta) muestra:

```
LangGraph — 69.00s total, 4.3K tokens, $0.0008

model  (4.10s)  → decide llamar a transcribir_audio
tools  (14.58s) → transcribir_audio
model  (7.86s)  → redacta la nota, sin tool
tools  (29.55s) → generar_imagen_conceptual + guardar_nota, en el mismo turno
model  (2.60s)  → respuesta final
```

Se respetó el orden y no gastó más de $0.001. Lo más lento es `generar_imagen_conceptual`, tiene sentido porque es la única llamada que devuelve contenido binario pesado.

Corrida real con mi voz — grabé un audio tocando workflow, tool calling, MCP y multiagentes, y corrí `python main.py mi_nota_de_voz.m4a`:

```
Procesando nota de voz: mi_nota_de_voz.m4a
============================================================
Audio transcrito (mi_nota_de_voz.m4a): Hoy quiero repasar varias cosas del curso que se conectan entre sí, aunque las m...
Nota guardada en: ./notas/sesion_mi_nota_de_voz.md
Imagen conceptual guardada en: ./imagenes/sesion_mi_nota_de_voz.png
============================================================
Respuesta del agente:

He transcrito la nota de voz y generado los artefactos permanentes solicitados. Aquí están los detalles:

1. Nota de estudio en Markdown: Se ha creado una nota que resume las diferencias entre un workflow y un agente en IA, así como conceptos relacionados como toolcalling y Model Context Protocol (MCP).
    - Ruta del archivo: `./notas/sesion_mi_nota_de_voz.md`

2. Imagen conceptual: Se ha generado una infografía que ilustra los conceptos clave discutidos en la nota.
    - Ruta del archivo: `./imagenes/sesion_mi_nota_de_voz.png`
```

La nota que quedó (`notas/sesion_mi_nota_de_voz.md`):

```markdown
# Diferencias entre Workflow y Agente en IA
- **Fecha:** no especificada
- **Resumen:** En esta sesión se revisan las diferencias entre un workflow y un agente, así como la importancia del toolcalling y el Model Context Protocol (MCP)...
- **Conceptos clave:** Workflow, Agente, Toolcalling, Model Context Protocol (MCP), Multiagentes
- **Conexión con otras sesiones del programa:** Se menciona la relación entre los conceptos de workflow y agente, así como la importancia del toolcalling y MCP en el contexto de la IA.

## Imagen conceptual
![Infografia](../imagenes/sesion_mi_nota_de_voz.png)
```

Dos cosas que noté revisándolo: el título quedó corto (solo "Workflow vs Agente" cuando toqué cinco temas) y la parte de "conexión con otras sesiones" salió genérica, no nombra sesiones concretas aunque sí las mencioné hablando. Y en la imagen (`imagenes/sesion_mi_nota_de_voz.png`) el texto del checklist no quedó del todo legible — es una limitación conocida de `gpt-image-1` con texto largo, no un bug del código, pero lo comprobé de primera mano.

## CODIGO

### `main.py`

```python
"""
Bitacora de Estudio Multimodal - Tarea personal Sesion 17 (Multimodalidad)
Programa en Diseno e Implementacion de Agentes IA - UTEC Posgrado

Agente que recibe una nota de voz sobre una sesion del programa y realiza
un cambio de modalidad en cadena: audio -> texto -> imagen.

  1) transcribir_audio        (audio  -> texto)   Whisper (OpenAI)
  2) [el LLM redacta la nota en Markdown a partir de la transcripcion]
  3) generar_imagen_conceptual (texto -> imagen)   gpt-image-1 (OpenAI)
  4) guardar_nota             (persiste la nota .md en disco)

Patron "Camino 1: LLM + Tools" (ver Sesion17_Multimodalidad_ANALISIS_COMPLETO.md,
Modulo6/Sesion17), igual que agents26_m6s17-main/main.py (agente de siniestros).
"""
import base64
import os
import sys
import uuid

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from openai import OpenAI

load_dotenv()

AUDIOS_DIR = "./audios/"
NOTAS_DIR = "./notas/"
IMAGENES_DIR = "./imagenes/"


class Toolbox:
    @tool
    def transcribir_audio(nombre_archivo: str) -> str:
        """
        Transcribe una nota de voz (audio) a texto usando Whisper.

        Args:
            nombre_archivo: nombre del archivo dentro de la carpeta "./audios/"
                (ej. "sesion17_multimodalidad.m4a").

        Returns:
            El texto transcrito de la nota de voz.

        Raises:
            FileNotFoundError: si el archivo no existe en "./audios/".
        """
        ruta = os.path.join(AUDIOS_DIR, nombre_archivo)
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontro el audio en: {ruta}")

        client = OpenAI()
        with open(ruta, "rb") as audio_file:
            transcripcion = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        print(f"Audio transcrito ({nombre_archivo}): {transcripcion.text[:80]}...")
        return transcripcion.text

    @tool
    def generar_imagen_conceptual(descripcion: str, nombre_archivo: str = "") -> str:
        """
        Genera una imagen conceptual/infografia a partir de una descripcion textual
        de los conceptos clave de una nota de estudio.

        Args:
            descripcion: descripcion clara de la escena/infografia a generar,
                incluyendo los conceptos clave y como se relacionan entre si.
            nombre_archivo: nombre opcional para el archivo (sin extension).
                Si no se indica, se genera un identificador unico.

        Returns:
            La ruta donde fue guardada la imagen generada.

        Raises:
            ValueError: si la descripcion esta vacia o es muy corta.
        """
        if not descripcion or len(descripcion.strip()) < 10:
            raise ValueError("La descripcion es muy corta para generar una imagen util.")

        os.makedirs(IMAGENES_DIR, exist_ok=True)
        client = OpenAI()

        prompt = (
            "Genera una infografia conceptual, estilo diagrama educativo limpio, "
            "que ilustre visualmente las siguientes ideas de una nota de estudio "
            "sobre Inteligencia Artificial y Agentes IA. Usa iconos simples, "
            "flechas y texto minimo (solo palabras clave), fondo claro:\n"
            + descripcion
        )

        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="high",
        )
        b64_data = response.data[0].b64_json
        image_bytes = base64.b64decode(b64_data)

        nombre = nombre_archivo.strip() or str(uuid.uuid4())
        ruta_imagen = os.path.join(IMAGENES_DIR, f"{nombre}.png")
        with open(ruta_imagen, "wb") as f:
            f.write(image_bytes)

        print(f"Imagen conceptual guardada en: {ruta_imagen}")
        return ruta_imagen

    @tool
    def guardar_nota(contenido: str, nombre_archivo: str) -> str:
        """
        Guarda la nota de estudio en formato Markdown en la carpeta de notas.
        La nota debe referenciar (con sintaxis Markdown de imagen) la imagen
        conceptual ya generada, por su ruta relativa dentro de "../imagenes/".

        Args:
            contenido: contenido completo de la nota, en Markdown.
            nombre_archivo: nombre del archivo (sin extension), ej. "sesion17_multimodalidad".

        Returns:
            La ruta donde fue guardada la nota.
        """
        os.makedirs(NOTAS_DIR, exist_ok=True)
        ruta_nota = os.path.join(NOTAS_DIR, f"{nombre_archivo}.md")
        with open(ruta_nota, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"Nota guardada en: {ruta_nota}")
        return ruta_nota


SYSTEM_PROMPT = """Eres un asistente que mantiene la bitacora personal de estudio de un
estudiante del Programa en Diseno e Implementacion de Agentes IA (UTEC Posgrado).

Cada vez que el estudiante te da el nombre de un archivo de audio, tu objetivo es
convertir esa nota de voz en dos artefactos permanentes:

1. Una nota de estudio en Markdown con esta estructura:
   - Titulo (tema de la sesion)
   - Fecha (si se menciona, si no, indica "no especificada")
   - Resumen (2-4 lineas)
   - Conceptos clave (lista)
   - Conexion con otras sesiones del programa (si el audio lo menciona)
   - Una seccion final "## Imagen conceptual" con el link Markdown a la imagen
     generada, ej: ![Infografia](../imagenes/NOMBRE.png)
2. Una imagen conceptual (infografia) que ilustre los conceptos clave de la nota.

Flujo obligatorio:
1. Transcribe el audio con la herramienta transcribir_audio.
2. Redacta la nota en Markdown a partir de la transcripcion (tu, como LLM, no una herramienta).
3. Genera la imagen conceptual con generar_imagen_conceptual, describiendo los
   conceptos clave de la nota (no la transcripcion completa).
4. Inserta la referencia a la imagen en la nota y guardala con guardar_nota.
5. Responde al final con un resumen breve de lo que hiciste y las rutas de los
   dos archivos generados.

Usa el mismo nombre base (sin extension) para la imagen y la nota, derivado del
tema principal (ej. "sesion17_multimodalidad").
"""


def construir_agente():
    modelo = os.environ.get("AGENT_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=modelo, temperature=0.2)
    toolbox = Toolbox()
    return create_agent(
        model=llm,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            toolbox.transcribir_audio,
            toolbox.generar_imagen_conceptual,
            toolbox.guardar_nota,
        ],
        debug=False,
    )


def main():
    nombre_audio = sys.argv[1] if len(sys.argv) > 1 else "nota_voz.m4a"
    ruta = os.path.join(AUDIOS_DIR, nombre_audio)
    if not os.path.exists(ruta):
        print(f"No se encontro '{ruta}'.")
        print(f"Coloca tu nota de voz ahi (o pasa el nombre como argumento: "
              f"python main.py mi_audio.m4a) y vuelve a ejecutar.")
        return

    agente = construir_agente()
    print(f"Procesando nota de voz: {nombre_audio}\n" + "=" * 60)
    respuesta = agente.invoke(
        {"messages": [{"role": "user", "content": f"Aqui esta mi nota de voz: {nombre_audio}"}]}
    )
    ultimo_mensaje = respuesta["messages"][-1]
    print("=" * 60)
    print("Respuesta del agente:\n")
    print(ultimo_mensaje.content)


if __name__ == "__main__":
    main()
```

## Declaración de transparencia de IA

Usé Claude Code para armar esto. Le pedí ideas de qué caso de uso hacer y me tiró varias; elegí la bitácora de voz yo, porque era la que más me servía de verdad. De ahí escribió el código y esta documentación, siguiendo el patrón que ya había investigado para la Sesión 17. Verificó que el código compilara y que el agente se armara bien antes de dármelo, pero la corrida real —grabar mi audio, correrlo con mi API key, revisar el resultado— la hice yo, y las dos observaciones sobre el título corto de la nota y el texto ilegible de la imagen salieron de esa revisión, no de una lista genérica.
