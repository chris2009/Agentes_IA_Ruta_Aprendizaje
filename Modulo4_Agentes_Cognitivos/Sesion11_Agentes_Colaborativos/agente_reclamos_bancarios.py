# ============================================================
# AGENTE BANCARIO PARA RECEPCIÓN DE RECLAMOS
# Producto: Tarjeta de crédito
# Memoria: Corto plazo persistida en archivo plano
# ============================================================

import json
import os

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool


# ------------------------------------------------------------
# 1. CONFIGURACIÓN
# ------------------------------------------------------------

load_dotenv()

ARCHIVO_HISTORIAL = Path("historial_chat.txt")
ARCHIVO_RECLAMOS = Path("reclamos_registrados.txt")

# Cinco intercambios: 5 mensajes del usuario y 5 del agente.
# Solo limita cuánto historial se recupera de ARCHIVO_HISTORIAL al
# reiniciar el programa. No debe aplicarse dentro de una conversación
# en curso, o el agente "olvida" datos ya proporcionados a mitad de tarea.
MAX_MENSAJES_MEMORIA = 10


# ------------------------------------------------------------
# 2. FUNCIONES PARA LA MEMORIA DE CORTO PLAZO
# ------------------------------------------------------------

def guardar_mensaje(rol: str, contenido: str) -> None:
    """
    Guarda un mensaje en el archivo plano del historial.

    Cada línea del archivo contiene un objeto JSON.
    Aunque tenga extensión .txt, sigue siendo un archivo plano.
    """

    registro = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "role": rol,
        "content": contenido
    }

    try:
        with ARCHIVO_HISTORIAL.open(
            mode="a",
            encoding="utf-8"
        ) as archivo:
            archivo.write(
                json.dumps(registro, ensure_ascii=False) + "\n"
            )

    except OSError as error:
        print(f"No se pudo guardar el historial: {error}")


def cargar_memoria_corta() -> list[dict[str, str]]:
    """
    Recupera únicamente los últimos mensajes del historial.

    Esto permite que el agente recuerde el contexto reciente,
    incluso si el programa se cierra y vuelve a ejecutarse.
    """

    if not ARCHIVO_HISTORIAL.exists():
        return []

    try:
        lineas = ARCHIVO_HISTORIAL.read_text(
            encoding="utf-8"
        ).splitlines()

    except OSError as error:
        print(f"No se pudo leer el historial: {error}")
        return []

    mensajes = []

    for linea in lineas[-MAX_MENSAJES_MEMORIA:]:
        try:
            registro = json.loads(linea)

            rol = registro.get("role")
            contenido = registro.get("content")

            if rol in {"user", "assistant"} and contenido:
                mensajes.append({
                    "role": rol,
                    "content": contenido
                })

        except json.JSONDecodeError:
            # Ignora líneas dañadas o incompletas.
            continue

    return mensajes


# ------------------------------------------------------------
# 3. HERRAMIENTA DEL AGENTE
# ------------------------------------------------------------

@tool
def registrar_reclamo(
    nombre_cliente: str,
    dni_cliente: str,
    ultimos_cuatro_digitos: str,
    fecha_operacion: str,
    monto: float,
    comercio: str,
    descripcion: str,
    solucion_solicitada: str
) -> str:
    """
    Registra un reclamo confirmado relacionado con una tarjeta de crédito.

    Usa esta herramienta solamente cuando el cliente haya proporcionado
    los datos necesarios, se le haya mostrado un resumen y haya confirmado
    expresamente que desea registrar el reclamo.
    """

    dni_cliente = dni_cliente.strip()

    if len(dni_cliente) != 8 or not dni_cliente.isdigit():
        return (
            "No se registró el reclamo. El DNI debe contener "
            "exactamente ocho números."
        )

    ultimos_cuatro_digitos = ultimos_cuatro_digitos.strip()

    if (
        len(ultimos_cuatro_digitos) != 4
        or not ultimos_cuatro_digitos.isdigit()
    ):
        return (
            "No se registró el reclamo. Los últimos cuatro dígitos "
            "deben contener exactamente cuatro números."
        )

    if monto <= 0:
        return (
            "No se registró el reclamo. "
            "El monto debe ser mayor que cero."
        )

    codigo_reclamo = f"REC-{uuid4().hex[:8].upper()}"
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    reclamo = (
        "\n"
        "============================================================\n"
        f"CÓDIGO DEL RECLAMO: {codigo_reclamo}\n"
        f"FECHA DE REGISTRO: {fecha_registro}\n"
        "PRODUCTO: Tarjeta de crédito\n"
        f"CLIENTE: {nombre_cliente}\n"
        f"DNI: {dni_cliente}\n"
        f"TARJETA TERMINADA EN: {ultimos_cuatro_digitos}\n"
        f"FECHA DE LA OPERACIÓN: {fecha_operacion}\n"
        f"MONTO RECLAMADO: S/ {monto:.2f}\n"
        f"COMERCIO O DESCRIPCIÓN: {comercio}\n"
        f"DETALLE DEL RECLAMO: {descripcion}\n"
        f"SOLUCIÓN SOLICITADA: {solucion_solicitada}\n"
        "ESTADO: Registrado\n"
        "============================================================\n"
    )

    try:
        with ARCHIVO_RECLAMOS.open(
            mode="a",
            encoding="utf-8"
        ) as archivo:
            archivo.write(reclamo)

    except OSError as error:
        return (
            "Ocurrió un error al guardar el reclamo: "
            f"{error}"
        )

    return (
        f"Reclamo registrado correctamente. "
        f"El código de seguimiento es {codigo_reclamo}."
    )


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


@tool
def consultar_reclamo_por_codigo(codigo_reclamo: str) -> str:
    """
    Busca un reclamo ya registrado a partir de su código de seguimiento
    (formato REC-XXXXXXXX) y devuelve su detalle completo.

    Usa esta herramienta cuando el cliente pregunte por el estado de
    un reclamo existente y te proporcione el código de seguimiento.
    """

    codigo_reclamo = codigo_reclamo.strip().upper()

    for bloque in _extraer_bloques_reclamos():
        datos = _parsear_bloque_reclamo(bloque)

        if datos.get("codigo") == codigo_reclamo:
            return bloque

    return f"No se encontró ningún reclamo con el código {codigo_reclamo}."


@tool
def consultar_reclamos_por_dni(dni_cliente: str) -> str:
    """
    Busca todos los reclamos registrados a nombre de un cliente,
    a partir de su DNI, y devuelve su detalle completo.

    Usa esta herramienta como primera opción cuando el cliente
    pregunte por sus reclamos y te indique su DNI: es un identificador
    único, a diferencia del nombre, que puede repetirse entre clientes.
    """

    dni_cliente = dni_cliente.strip()

    coincidencias = [
        bloque
        for bloque in _extraer_bloques_reclamos()
        if _parsear_bloque_reclamo(bloque).get("dni") == dni_cliente
    ]

    if not coincidencias:
        return f"No se encontraron reclamos a nombre del DNI {dni_cliente}."

    return "\n\n".join(coincidencias)


@tool
def consultar_reclamos_por_nombre(nombre_cliente: str) -> str:
    """
    Busca todos los reclamos registrados a nombre de un cliente y
    devuelve su detalle completo.

    Usa esta herramienta solo como último recurso, cuando el cliente
    pregunte por sus reclamos y no recuerde ni el código de seguimiento
    ni su DNI. El nombre no es un identificador único (puede haber
    clientes homónimos), así que si el cliente puede darte su DNI,
    usa consultar_reclamos_por_dni en su lugar. La búsqueda por nombre
    no distingue mayúsculas ni minúsculas.
    """

    nombre_cliente = nombre_cliente.strip().lower()

    coincidencias = [
        bloque
        for bloque in _extraer_bloques_reclamos()
        if nombre_cliente in _parsear_bloque_reclamo(bloque).get(
            "cliente", ""
        ).lower()
    ]

    if not coincidencias:
        return f"No se encontraron reclamos a nombre de {nombre_cliente}."

    return "\n\n".join(coincidencias)


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

PROMPT_SISTEMA = """
Eres un agente virtual de atención al cliente de un banco.

Tu función es recibir reclamos relacionados exclusivamente con
TARJETAS DE CRÉDITO, especialmente por:

- Consumos no reconocidos.
- Cobros duplicados.
- Montos incorrectos.
- Pagos que no aparecen.
- Comisiones que el cliente considera incorrectas.

Debes conversar de manera amable, clara y profesional.

Para registrar un reclamo debes obtener:

1. Nombre del cliente.
2. DNI del cliente (ocho dígitos). Es obligatorio porque es el
   identificador único de la persona: el nombre por sí solo es
   ambiguo y puede repetirse entre distintos clientes.
3. Únicamente los últimos cuatro dígitos de la tarjeta.
4. Fecha de la operación reclamada.
5. Monto reclamado.
6. Nombre del comercio o descripción de la operación.
7. Explicación de lo sucedido.
8. Solución solicitada por el cliente.

Reglas obligatorias:

- Solicita los datos progresivamente, no todos en una sola pregunta.
- Nunca solicites el número completo de la tarjeta.
- Nunca solicites contraseña, PIN, CVV ni códigos enviados por SMS.
- No inventes información que el cliente no haya proporcionado.
- Antes de registrar, presenta un resumen del reclamo.
- Pregunta al cliente si confirma el registro.
- Solo después de recibir una confirmación expresa utiliza
  la herramienta registrar_reclamo.
- Al finalizar, comunica el código de seguimiento.
- Si se trata de un consumo no reconocido, recomienda al cliente
  comunicarse con los canales oficiales del banco para bloquear
  temporalmente la tarjeta.
- No afirmes que bloqueaste una tarjeta porque no tienes esa capacidad.

Además puedes consultar reclamos ya registrados:

- Si el cliente pregunta por el estado de un reclamo y te da un
  código de seguimiento (formato REC-XXXXXXXX), usa la herramienta
  consultar_reclamo_por_codigo.
- Si el cliente pregunta por sus reclamos pero no recuerda el código,
  y en cambio te da su DNI, usa la herramienta consultar_reclamos_por_dni.
  Prefiérela sobre la búsqueda por nombre, ya que el DNI identifica
  a la persona sin ambigüedad.
- Solo si el cliente no recuerda ni el código ni el DNI, y te da su
  nombre, usa la herramienta consultar_reclamos_por_nombre como
  último recurso.
- Si no se encuentra ningún reclamo, indícaselo con claridad al
  cliente en vez de inventar información.
"""

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt=PROMPT_SISTEMA,
    tools=[
        registrar_reclamo,
        consultar_reclamo_por_codigo,
        consultar_reclamos_por_dni,
        consultar_reclamos_por_nombre
    ]
)


# ------------------------------------------------------------
# 6. CHAT PRINCIPAL
# ------------------------------------------------------------

def iniciar_chat() -> None:
    """
    Inicia el chat y recupera la memoria reciente.
    """

    mensajes = cargar_memoria_corta()

    print("=" * 60)
    print("AGENTE DE RECLAMOS BANCARIOS")
    print("Producto: Tarjeta de crédito")
    print("=" * 60)
    print("Escriba 'salir' para finalizar.")
    print("Escriba 'nuevo' para iniciar una conversación nueva.")
    print()

    if mensajes:
        print(
            "Se recuperó el contexto reciente almacenado "
            "en historial_chat.txt.\n"
        )

    while True:
        try:
            entrada_usuario = input("Cliente: ").strip()

            if not entrada_usuario:
                continue

            if entrada_usuario.lower() in {
                "salir",
                "exit",
                "quit"
            }:
                print(
                    "Agente: Gracias por comunicarse con el banco. "
                    "Hasta luego."
                )
                break

            if entrada_usuario.lower() == "nuevo":
                mensajes = []
                print(
                    "Agente: Se inició una conversación nueva. "
                    "El historial anterior continúa guardado en el archivo."
                )
                continue

            # Se guarda inmediatamente el mensaje del cliente.
            guardar_mensaje("user", entrada_usuario)

            mensajes.append({
                "role": "user",
                "content": entrada_usuario
            })

            resultado = agent.invoke({
                "messages": mensajes
            })

            contenido_respuesta = resultado["messages"][-1].content
            respuesta_agente = extraer_texto(contenido_respuesta)

            print(f"Agente: {respuesta_agente}")

            # Se guarda la respuesta del agente.
            guardar_mensaje("assistant", respuesta_agente)

            mensajes.append({
                "role": "assistant",
                "content": respuesta_agente
            })

        except KeyboardInterrupt:
            print(
                "\nAgente: Conversación finalizada por el usuario."
            )
            break

        except Exception as error:
            print(
                "Agente: Ocurrió un error al procesar la solicitud."
            )
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

    iniciar_chat()