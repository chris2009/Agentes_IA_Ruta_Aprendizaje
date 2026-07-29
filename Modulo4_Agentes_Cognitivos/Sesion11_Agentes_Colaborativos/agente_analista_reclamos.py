# ============================================================
# AGENTE ANALISTA DE RECLAMOS
# Producto: Tarjeta de crédito
#
# Este es el SEGUNDO agente del flujo. El primero
# (agente_reclamos_bancarios.py) recibe al cliente y registra el
# reclamo en ARCHIVO_RECLAMOS. Este agente toma esos reclamos ya
# registrados, los analiza contra reglas de negocio y determina una
# resolución final, entregando un reporte en Markdown.
#
# No conversa con el cliente: se opera dando el código de un reclamo
# ya existente (formato REC-XXXXXXXX).
# ============================================================

import os

from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool


# ------------------------------------------------------------
# 1. CONFIGURACIÓN
# ------------------------------------------------------------

load_dotenv()

# Mismo archivo que escribe agente_reclamos_bancarios.py.
ARCHIVO_RECLAMOS = Path("reclamos_registrados.txt")

# Carpeta donde se guarda un .md por cada reclamo analizado.
CARPETA_REPORTES = Path("reportes_reclamos")

# Reclamos por montos iguales o mayores a este umbral no se aprueban
# de forma automática: se escalan a investigación de fraude, salvo
# que se trate de un cobro duplicado con evidencia clara en el
# detalle del reclamo. Es un valor de ejemplo para este ejercicio,
# ajustable según la política real del banco.
UMBRAL_ESCALAMIENTO_FRAUDE = 3000.00


# ------------------------------------------------------------
# 2. LECTURA DE RECLAMOS YA REGISTRADOS
# ------------------------------------------------------------
#
# El formato de bloques (separador, campos "CLAVE: valor") es el
# mismo que escribe registrar_reclamo() en agente_reclamos_bancarios.py.
# Se reimplementa aquí en vez de importar ese módulo para que este
# archivo funcione como un agente independiente.

SEPARADOR_RECLAMO = "=" * 60

CAMPOS_RECLAMO = {
    "codigo": "CÓDIGO DEL RECLAMO:",
    "fecha_registro": "FECHA DE REGISTRO:",
    "producto": "PRODUCTO:",
    "cliente": "CLIENTE:",
    "dni": "DNI:",
    "tarjeta": "TARJETA TERMINADA EN:",
    "fecha_operacion": "FECHA DE LA OPERACIÓN:",
    "monto": "MONTO RECLAMADO:",
    "comercio": "COMERCIO O DESCRIPCIÓN:",
    "detalle": "DETALLE DEL RECLAMO:",
    "solucion": "SOLUCIÓN SOLICITADA:",
    "estado": "ESTADO:",
}


def _extraer_bloques_reclamos() -> list[str]:
    """
    Divide el archivo de reclamos registrados en bloques individuales,
    delimitados por la línea separadora.
    """

    if not ARCHIVO_RECLAMOS.exists():
        return []

    try:
        contenido = ARCHIVO_RECLAMOS.read_text(encoding="utf-8")

    except OSError as error:
        print(f"No se pudo leer los reclamos registrados: {error}")
        return []

    return [
        parte.strip()
        for parte in contenido.split(SEPARADOR_RECLAMO)
        if "CÓDIGO DEL RECLAMO" in parte
    ]


def _parsear_bloque_reclamo(bloque: str) -> dict[str, str]:
    """
    Extrae los campos (código, cliente, monto, etc.) de un bloque
    de texto correspondiente a un reclamo registrado.
    """

    datos: dict[str, str] = {}

    for linea in bloque.splitlines():
        linea = linea.strip()

        for clave, prefijo in CAMPOS_RECLAMO.items():
            if linea.startswith(prefijo):
                datos[clave] = linea[len(prefijo):].strip()

    return datos


def _buscar_bloque_por_codigo(codigo_reclamo: str) -> str | None:
    """
    Devuelve el bloque de texto del reclamo con ese código,
    o None si no existe ningún reclamo registrado con ese código.
    """

    codigo_reclamo = codigo_reclamo.strip().upper()

    for bloque in _extraer_bloques_reclamos():
        if _parsear_bloque_reclamo(bloque).get("codigo") == codigo_reclamo:
            return bloque

    return None


def _actualizar_estado_reclamo(codigo_reclamo: str, nuevo_estado: str) -> bool:
    """
    Reemplaza la línea "ESTADO: ..." del bloque correspondiente a un
    reclamo, directamente en ARCHIVO_RECLAMOS, sin tocar el resto
    del archivo.

    Devuelve True si encontró y actualizó el reclamo, False si no.
    """

    if not ARCHIVO_RECLAMOS.exists():
        return False

    codigo_reclamo = codigo_reclamo.strip().upper()
    contenido = ARCHIVO_RECLAMOS.read_text(encoding="utf-8")
    partes = contenido.split(SEPARADOR_RECLAMO)

    actualizado = False

    for indice, parte in enumerate(partes):
        if f"CÓDIGO DEL RECLAMO: {codigo_reclamo}" not in parte:
            continue

        lineas = parte.splitlines()
        nuevas_lineas = [
            f"ESTADO: {nuevo_estado}"
            if linea.strip().startswith("ESTADO:")
            else linea
            for linea in lineas
        ]

        partes[indice] = "\n".join(nuevas_lineas) + "\n"
        actualizado = True
        break

    if actualizado:
        try:
            ARCHIVO_RECLAMOS.write_text(
                SEPARADOR_RECLAMO.join(partes), encoding="utf-8"
            )

        except OSError as error:
            print(f"No se pudo actualizar el estado del reclamo: {error}")
            return False

    return actualizado


# ------------------------------------------------------------
# 3. HERRAMIENTAS DEL AGENTE
# ------------------------------------------------------------

@tool
def buscar_reclamo_por_codigo(codigo_reclamo: str) -> str:
    """
    Busca un reclamo ya registrado a partir de su código de
    seguimiento (formato REC-XXXXXXXX) y devuelve todos sus datos.

    Usa esta herramienta primero, para obtener la información del
    reclamo antes de analizarlo y decidir una resolución.
    """

    bloque = _buscar_bloque_por_codigo(codigo_reclamo)

    if bloque is None:
        return f"No se encontró ningún reclamo con el código {codigo_reclamo}."

    return bloque


@tool
def generar_reporte_resolucion(
    codigo_reclamo: str,
    resolucion: str,
    monto_a_reembolsar: float,
    justificacion: str,
    siguientes_pasos: str
) -> str:
    """
    Registra la resolución final de un reclamo y genera su reporte
    en formato Markdown.

    Usa esta herramienta solo después de haber consultado el reclamo
    con buscar_reclamo_por_codigo y de haber determinado una
    resolución clara conforme a las reglas de negocio.

    El parámetro "resolucion" debe ser exactamente uno de:
    "Aprobado - Reembolso total", "Aprobado - Reembolso parcial",
    "Rechazado", "Escalado a investigación de fraude" o
    "Pendiente de información adicional".

    "monto_a_reembolsar" debe ser 0 si la resolución no implica
    ningún reembolso (rechazado, escalado o pendiente).
    """

    codigo_reclamo = codigo_reclamo.strip().upper()
    bloque = _buscar_bloque_por_codigo(codigo_reclamo)

    if bloque is None:
        return f"No se encontró ningún reclamo con el código {codigo_reclamo}."

    datos = _parsear_bloque_reclamo(bloque)
    fecha_analisis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    contenido_md = f"""# Reporte de resolución de reclamo

**Código de reclamo:** {codigo_reclamo}
**Fecha de análisis:** {fecha_analisis}

## Datos del reclamo

| Campo | Valor |
|---|---|
| Cliente | {datos.get('cliente', '—')} |
| DNI | {datos.get('dni', '—')} |
| Tarjeta terminada en | {datos.get('tarjeta', '—')} |
| Fecha de la operación | {datos.get('fecha_operacion', '—')} |
| Monto reclamado | {datos.get('monto', '—')} |
| Comercio | {datos.get('comercio', '—')} |
| Detalle del reclamo | {datos.get('detalle', '—')} |
| Solución solicitada | {datos.get('solucion', '—')} |

## Resolución

- **Decisión:** {resolucion}
- **Monto a reembolsar:** S/ {monto_a_reembolsar:.2f}

### Justificación

{justificacion}

### Siguientes pasos

{siguientes_pasos}
"""

    try:
        CARPETA_REPORTES.mkdir(exist_ok=True)
        archivo_reporte = CARPETA_REPORTES / f"{codigo_reclamo}.md"
        archivo_reporte.write_text(contenido_md, encoding="utf-8")

    except OSError as error:
        return f"No se pudo guardar el reporte: {error}"

    _actualizar_estado_reclamo(codigo_reclamo, f"Resuelto - {resolucion}")

    return (
        f"Resolución registrada para {codigo_reclamo}: {resolucion}. "
        f"Reporte guardado en {archivo_reporte}."
    )


# ------------------------------------------------------------
# 4. FUNCIÓN PARA EXTRAER LA RESPUESTA DEL MODELO
# ------------------------------------------------------------

def extraer_texto(contenido) -> str:
    """
    Convierte la respuesta del modelo en texto.

    Algunos modelos retornan un string y otros retornan
    una lista de bloques de contenido.
    """

    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):
        textos = []

        for bloque in contenido:
            if isinstance(bloque, dict):
                texto = bloque.get("text")

                if texto:
                    textos.append(texto)

            else:
                texto = getattr(bloque, "text", None)

                if texto:
                    textos.append(texto)

        return "\n".join(textos)

    return str(contenido)


# ------------------------------------------------------------
# 5. CREACIÓN DEL AGENTE
# ------------------------------------------------------------

PROMPT_SISTEMA = f"""
Eres un agente analista de reclamos de un banco, especializado en
TARJETAS DE CRÉDITO. No conversas con el cliente: recibes el código
de un reclamo ya registrado por otro agente y debes analizarlo para
determinar una resolución final.

Flujo obligatorio:

1. Usa buscar_reclamo_por_codigo para obtener los datos del reclamo.
2. Analiza el caso aplicando las reglas de negocio de abajo.
3. Usa generar_reporte_resolucion exactamente una vez, con tu
   decisión final, para dejar registrada la resolución y generar
   el reporte en Markdown.
4. Responde al usuario con un resumen breve de la decisión tomada.

Reglas de negocio para decidir la resolución:

- Consumo no reconocido: si el monto reclamado es menor a
  S/ {UMBRAL_ESCALAMIENTO_FRAUDE:.2f}, aprueba el reembolso total.
  Si el monto es igual o mayor a ese umbral, la resolución debe ser
  "Escalado a investigación de fraude" en vez de una aprobación
  directa.
- Cobro duplicado: si el detalle del reclamo describe claramente un
  cobro repetido, aprueba el reembolso total del monto duplicado,
  sin importar el monto.
- Monto incorrecto: si el cliente indicó en el detalle cuál era el
  monto correcto, aprueba el reembolso parcial por la diferencia.
  Si no indicó el monto correcto, la resolución debe ser
  "Pendiente de información adicional".
- Comisión que el cliente considera incorrecta o pago que no
  aparece reflejado: si el detalle no da información suficiente
  para verificar el caso, usa "Pendiente de información adicional"
  en vez de aprobar o rechazar.
- Nunca inventes datos que no estén en el reclamo ni asumas hechos
  no descritos en el detalle.
- Sé conciso y profesional en la justificación: explica en qué
  regla de negocio te basaste para la decisión.
"""

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt=PROMPT_SISTEMA,
    tools=[
        buscar_reclamo_por_codigo,
        generar_reporte_resolucion
    ]
)


# ------------------------------------------------------------
# 6. FLUJO PRINCIPAL
# ------------------------------------------------------------

def iniciar_analisis() -> None:
    """
    Punto de entrada interactivo. Pide el código de un reclamo ya
    registrado y ejecuta el agente analista sobre él, uno a la vez.

    A diferencia del agente de recepción, este agente no necesita
    memoria de conversación: cada análisis es independiente y se
    resuelve en un solo intercambio de mensajes con el modelo.
    """

    print("=" * 60)
    print("AGENTE ANALISTA DE RECLAMOS")
    print("Producto: Tarjeta de crédito")
    print("=" * 60)
    print("Ingrese el código de un reclamo ya registrado (REC-XXXXXXXX).")
    print("Escriba 'salir' para finalizar.")
    print()

    while True:
        try:
            codigo_reclamo = input("Código de reclamo: ").strip()

            if not codigo_reclamo:
                continue

            if codigo_reclamo.lower() in {"salir", "exit", "quit"}:
                print("Analista: Hasta luego.")
                break

            instruccion = (
                "Analiza el reclamo con código "
                f"{codigo_reclamo.upper()} y determina su resolución "
                "final siguiendo el flujo y las reglas de negocio "
                "indicadas."
            )

            resultado = agent.invoke({
                "messages": [{"role": "user", "content": instruccion}]
            })

            contenido_respuesta = resultado["messages"][-1].content
            respuesta_agente = extraer_texto(contenido_respuesta)

            print(f"Analista: {respuesta_agente}\n")

        except KeyboardInterrupt:
            print("\nAnalista: Análisis finalizado por el usuario.")
            break

        except Exception as error:
            print("Analista: Ocurrió un error al procesar la solicitud.")
            print(f"Detalle técnico: {error}")


# ------------------------------------------------------------
# 7. EJECUCIÓN
# ------------------------------------------------------------

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "No se encontró ANTHROPIC_API_KEY. "
            "Agrégala al archivo .env."
        )

    iniciar_analisis()
