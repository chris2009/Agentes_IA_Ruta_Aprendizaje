# ============================================================
# AGENTE CLEMENTE PARA RESERVAS Y CAPACIDAD DE RESTAURANTES
# Proyecto: Clemente para Restaurantes
# Framework: LangChain create_agent
# Memoria: corto plazo en JSONL + stores locales JSON
# ============================================================

import json
import os
import re

from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from uuid import uuid4

from langchain.agents import create_agent
from langchain.tools import tool

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*_args, **_kwargs) -> bool:
        """Fallback cuando python-dotenv no esta instalado."""
        return False


# ------------------------------------------------------------
# 1. CONFIGURACION
# ------------------------------------------------------------

load_dotenv()

BASE_DIR = Path(__file__).parent

ARCHIVO_HISTORIAL = BASE_DIR / "historial_clemente_reservas.jsonl"
ARCHIVO_RESERVAS = BASE_DIR / "reservas_clemente.json"
ARCHIVO_CLIENTES = BASE_DIR / "clientes_clemente.json"
ARCHIVO_ESCALAMIENTOS = BASE_DIR / "escalamientos_clemente.txt"

# Se recuperan los ultimos 12 mensajes al reiniciar el programa.
# Durante una conversacion activa se conserva toda la lista en memoria.
MAX_MENSAJES_MEMORIA = 12

MODELO = os.getenv("CLEMENTE_MODEL", "anthropic:claude-sonnet-4-6")

RESTAURANTE = {
    "restaurant_id": "clemente-demo",
    "nombre": "Clemente Demo Restaurant",
    "duracion_reserva_minutos": 120,
    "max_personas_autonomo": 8,
    "zonas": ["salon", "terraza", "barra", "privado"],
    "horarios": {
        # weekday(): lunes=0, domingo=6
        0: ("12:00", "22:00"),
        1: ("12:00", "22:00"),
        2: ("12:00", "22:00"),
        3: ("12:00", "22:00"),
        4: ("12:00", "23:30"),
        5: ("12:00", "23:30"),
        6: ("12:00", "21:00"),
    },
}

MESAS = [
    {"id": "S1", "zona": "salon", "capacidad": 2},
    {"id": "S2", "zona": "salon", "capacidad": 4},
    {"id": "S3", "zona": "salon", "capacidad": 4},
    {"id": "S4", "zona": "salon", "capacidad": 6},
    {"id": "T1", "zona": "terraza", "capacidad": 2},
    {"id": "T2", "zona": "terraza", "capacidad": 4},
    {"id": "T3", "zona": "terraza", "capacidad": 6},
    {"id": "B1", "zona": "barra", "capacidad": 2},
    {"id": "B2", "zona": "barra", "capacidad": 2},
    {"id": "P1", "zona": "privado", "capacidad": 8},
]

POLITICAS_OPERATIVAS = {
    "reservas": (
        "Para crear una reserva se requiere nombre, telefono, fecha, hora, "
        "cantidad de personas y confirmacion explicita del cliente."
    ),
    "disponibilidad": (
        "Nunca se debe prometer una mesa sin consultar disponibilidad en tiempo real. "
        "Si el horario solicitado no esta disponible, se deben ofrecer alternativas."
    ),
    "cancelaciones": (
        "Las cancelaciones y modificaciones requieren confirmacion explicita del cliente. "
        "El agente debe registrar motivo si el cliente lo indica."
    ),
    "grupos": (
        "Grupos de mas de 8 personas, eventos privados o solicitudes fuera de layout "
        "estandar deben escalarse al equipo del restaurante."
    ),
    "alergias": (
        "Las alergias o condiciones alimentarias se tratan como nota critica. "
        "El agente no debe prometer seguridad alimentaria absoluta; debe registrar la nota "
        "y escalar si hay duda."
    ),
    "datos": (
        "Solo se deben pedir datos necesarios para la reserva. No pedir DNI, tarjetas, CVV, "
        "contrasenas ni datos de pago en este flujo."
    ),
    "vision": (
        "La vision computacional, si existe, solo envia eventos operativos como mesa_liberada "
        "o ocupacion_prolongada. No identifica personas ni modifica el layout automaticamente."
    ),
}


# ------------------------------------------------------------
# 2. UTILIDADES DE ARCHIVOS Y MEMORIA
# ------------------------------------------------------------

def _leer_json(path: Path, valor_por_defecto):
    if not path.exists():
        return valor_por_defecto

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return valor_por_defecto


def _guardar_json(path: Path, data) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def guardar_mensaje(rol: str, contenido: str) -> None:
    """
    Guarda cada mensaje como una linea JSON.

    Esta memoria es de corto plazo persistida: permite recuperar el
    contexto reciente si el programa se cierra y vuelve a abrirse.
    """

    registro = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "role": rol,
        "content": contenido,
    }

    try:
        with ARCHIVO_HISTORIAL.open(mode="a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
    except OSError as error:
        print(f"No se pudo guardar el historial: {error}")


def cargar_memoria_corta() -> list[dict[str, str]]:
    """
    Recupera los ultimos mensajes utiles del historial.
    """

    if not ARCHIVO_HISTORIAL.exists():
        return []

    try:
        lineas = ARCHIVO_HISTORIAL.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        print(f"No se pudo leer el historial: {error}")
        return []

    mensajes = []

    for linea in lineas[-MAX_MENSAJES_MEMORIA:]:
        try:
            registro = json.loads(linea)
        except json.JSONDecodeError:
            continue

        rol = registro.get("role")
        contenido = registro.get("content")

        if rol in {"user", "assistant"} and contenido:
            mensajes.append({"role": rol, "content": contenido})

    return mensajes


def _normalizar_telefono(telefono: str) -> str:
    telefono = telefono.strip()
    telefono = re.sub(r"[^\d+]", "", telefono)
    return telefono


def _normalizar_fecha(fecha: str) -> str:
    fecha = fecha.strip()
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]

    for formato in formatos:
        try:
            return datetime.strptime(fecha, formato).strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError("La fecha debe estar en formato YYYY-MM-DD o DD/MM/YYYY.")


def _normalizar_hora(hora: str) -> str:
    hora = hora.strip().lower().replace(" ", "")

    if re.fullmatch(r"\d{1,2}", hora):
        hora = f"{int(hora):02d}:00"

    for formato in ["%H:%M", "%H.%M"]:
        try:
            return datetime.strptime(hora, formato).strftime("%H:%M")
        except ValueError:
            continue

    raise ValueError("La hora debe estar en formato HH:MM, por ejemplo 20:30.")


def _datetime_reserva(fecha: str, hora: str) -> datetime:
    return datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")


def _horario_del_dia(fecha: str) -> tuple[str, str]:
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    return RESTAURANTE["horarios"][fecha_dt.weekday()]


def _dentro_de_horario(fecha: str, hora: str) -> bool:
    apertura, cierre = _horario_del_dia(fecha)
    inicio = _datetime_reserva(fecha, hora)
    apertura_dt = _datetime_reserva(fecha, apertura)
    cierre_dt = _datetime_reserva(fecha, cierre)
    ultimo_inicio = cierre_dt - timedelta(
        minutes=RESTAURANTE["duracion_reserva_minutos"]
    )

    return apertura_dt <= inicio <= ultimo_inicio


def _intervalos_se_cruzan(
    inicio_a: datetime,
    fin_a: datetime,
    inicio_b: datetime,
    fin_b: datetime,
) -> bool:
    return inicio_a < fin_b and inicio_b < fin_a


def _reservas_activas() -> list[dict]:
    reservas = _leer_json(ARCHIVO_RESERVAS, [])
    return [
        reserva
        for reserva in reservas
        if reserva.get("estado") in {"confirmada", "pendiente_revision_staff"}
    ]


def _mesa_ocupada(
    mesa_id: str,
    fecha: str,
    hora: str,
    duracion_minutos: int,
    excluir_codigo: str | None = None,
) -> bool:
    inicio = _datetime_reserva(fecha, hora)
    fin = inicio + timedelta(minutes=duracion_minutos)

    for reserva in _reservas_activas():
        if excluir_codigo and reserva.get("codigo_reserva") == excluir_codigo:
            continue

        if reserva.get("fecha") != fecha:
            continue

        if mesa_id not in reserva.get("mesa_ids", []):
            continue

        try:
            inicio_reserva = _datetime_reserva(
                reserva["fecha"],
                reserva["hora"],
            )
        except (KeyError, ValueError):
            continue

        duracion_existente = int(
            reserva.get(
                "duracion_minutos",
                RESTAURANTE["duracion_reserva_minutos"],
            )
        )
        fin_reserva = inicio_reserva + timedelta(minutes=duracion_existente)

        if _intervalos_se_cruzan(inicio, fin, inicio_reserva, fin_reserva):
            return True

    return False


def _opciones_mesas(
    fecha: str,
    hora: str,
    cantidad_personas: int,
    zona_preferida: str = "",
    excluir_codigo: str | None = None,
) -> list[dict]:
    if not _dentro_de_horario(fecha, hora):
        return []

    zona_preferida = zona_preferida.strip().lower()
    duracion = RESTAURANTE["duracion_reserva_minutos"]

    candidatas = [
        mesa
        for mesa in MESAS
        if not zona_preferida or mesa["zona"] == zona_preferida
    ]

    libres = [
        mesa
        for mesa in candidatas
        if not _mesa_ocupada(
            mesa["id"],
            fecha,
            hora,
            duracion,
            excluir_codigo=excluir_codigo,
        )
    ]

    opciones = []

    for mesa in libres:
        if mesa["capacidad"] >= cantidad_personas:
            opciones.append({
                "fecha": fecha,
                "hora": hora,
                "mesa_ids": [mesa["id"]],
                "zona": mesa["zona"],
                "capacidad_total": mesa["capacidad"],
                "tipo": "mesa_individual",
            })

    # Combinaciones simples de dos mesas dentro de la misma zona.
    # Grupos mayores al limite autonomo se escalan, no se combinan aqui.
    if cantidad_personas <= RESTAURANTE["max_personas_autonomo"]:
        for mesa_a, mesa_b in combinations(libres, 2):
            if mesa_a["zona"] != mesa_b["zona"]:
                continue

            capacidad_total = mesa_a["capacidad"] + mesa_b["capacidad"]

            if capacidad_total >= cantidad_personas:
                opciones.append({
                    "fecha": fecha,
                    "hora": hora,
                    "mesa_ids": sorted([mesa_a["id"], mesa_b["id"]]),
                    "zona": mesa_a["zona"],
                    "capacidad_total": capacidad_total,
                    "tipo": "combinacion_mesas",
                })

    opciones.sort(
        key=lambda opcion: (
            opcion["capacidad_total"],
            len(opcion["mesa_ids"]),
            opcion["zona"],
        )
    )

    return opciones[:6]


def _horas_candidatas(fecha: str, hora: str) -> list[str]:
    objetivo = _datetime_reserva(fecha, hora)
    offsets = [0, -30, 30, -60, 60, -90, 90]
    horas = []

    for offset in offsets:
        candidata = objetivo + timedelta(minutes=offset)
        hora_candidata = candidata.strftime("%H:%M")

        if candidata.strftime("%Y-%m-%d") != fecha:
            continue

        if _dentro_de_horario(fecha, hora_candidata):
            horas.append(hora_candidata)

    return list(dict.fromkeys(horas))


def _cliente_por_telefono(telefono: str) -> dict:
    clientes = _leer_json(ARCHIVO_CLIENTES, {})
    telefono = _normalizar_telefono(telefono)
    return clientes.get(telefono, {})


def _score_opcion(
    opcion: dict,
    hora_preferida: str,
    cantidad_personas: int,
    zona_preferida: str = "",
    telefono_cliente: str = "",
) -> dict:
    zona_preferida = zona_preferida.strip().lower()
    cliente = _cliente_por_telefono(telefono_cliente)
    preferencias = cliente.get("preferencias", {})
    zona_cliente = str(preferencias.get("zona_preferida", "")).lower()

    if zona_preferida and opcion["zona"] == zona_preferida:
        preference_fit = 1.0
    elif not zona_preferida and zona_cliente and opcion["zona"] == zona_cliente:
        preference_fit = 0.95
    elif not zona_preferida:
        preference_fit = 0.75
    else:
        preference_fit = 0.55

    capacidad_total = max(opcion["capacidad_total"], 1)
    capacidad_fit = 1 - min(
        0.45,
        ((capacidad_total - cantidad_personas) / capacidad_total) * 0.45,
    )

    operational_efficiency = min(1.0, cantidad_personas / capacidad_total)

    minutos_espera = abs(
        int(
            (
                _datetime_reserva(opcion["fecha"], opcion["hora"])
                - _datetime_reserva(opcion["fecha"], hora_preferida)
            ).total_seconds()
            / 60
        )
    )
    waiting_time_score = max(0.0, 1 - minutos_espera / 120)

    customer_history_fit = 0.8
    if zona_cliente and opcion["zona"] == zona_cliente:
        customer_history_fit = 1.0

    no_show_count = int(cliente.get("no_show_count", 0))
    no_show_penalty = min(0.20, no_show_count * 0.05)

    utilidad = (
        0.30 * preference_fit
        + 0.25 * capacidad_fit
        + 0.20 * operational_efficiency
        + 0.15 * waiting_time_score
        + 0.10 * customer_history_fit
        - no_show_penalty
    )

    opcion_con_score = dict(opcion)
    opcion_con_score["score_utilidad"] = round(utilidad, 3)
    opcion_con_score["motivos_score"] = {
        "preference_fit": round(preference_fit, 2),
        "capacity_fit": round(capacidad_fit, 2),
        "operational_efficiency": round(operational_efficiency, 2),
        "waiting_time_score": round(waiting_time_score, 2),
        "customer_history_fit": round(customer_history_fit, 2),
        "no_show_penalty": round(no_show_penalty, 2),
    }

    return opcion_con_score


def _buscar_opciones_rankeadas(
    fecha: str,
    hora: str,
    cantidad_personas: int,
    zona_preferida: str = "",
    telefono_cliente: str = "",
    excluir_codigo: str | None = None,
) -> list[dict]:
    opciones = []

    for hora_candidata in _horas_candidatas(fecha, hora):
        opciones.extend(
            _opciones_mesas(
                fecha,
                hora_candidata,
                cantidad_personas,
                zona_preferida=zona_preferida,
                excluir_codigo=excluir_codigo,
            )
        )

    rankeadas = [
        _score_opcion(
            opcion,
            hora,
            cantidad_personas,
            zona_preferida=zona_preferida,
            telefono_cliente=telefono_cliente,
        )
        for opcion in opciones
    ]

    rankeadas.sort(
        key=lambda opcion: (
            -opcion["score_utilidad"],
            abs(
                (
                    _datetime_reserva(opcion["fecha"], opcion["hora"])
                    - _datetime_reserva(fecha, hora)
                ).total_seconds()
            ),
            opcion["capacidad_total"],
        )
    )

    return rankeadas[:5]


def _registrar_escalamiento_interno(
    motivo: str,
    resumen: str,
    urgencia: str = "media",
    codigo_reserva: str = "",
) -> str:
    codigo = f"ESC-{uuid4().hex[:8].upper()}"
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    bloque = (
        "\n"
        "============================================================\n"
        f"CODIGO_ESCALAMIENTO: {codigo}\n"
        f"FECHA: {fecha_registro}\n"
        f"URGENCIA: {urgencia}\n"
        f"CODIGO_RESERVA: {codigo_reserva or 'N/A'}\n"
        f"MOTIVO: {motivo}\n"
        f"RESUMEN: {resumen}\n"
        "ESTADO: pendiente_staff\n"
        "============================================================\n"
    )

    with ARCHIVO_ESCALAMIENTOS.open(mode="a", encoding="utf-8") as archivo:
        archivo.write(bloque)

    return codigo


# ------------------------------------------------------------
# 3. TOOLS DEL AGENTE
# ------------------------------------------------------------

@tool
def get_restaurant_policy(topico: str) -> str:
    """
    Recupera reglas operativas vigentes del restaurante.

    Usa esta herramienta antes de responder sobre disponibilidad,
    cancelaciones, grupos grandes, alergias, datos personales o uso de
    eventos de vision computacional.
    """

    consulta = topico.strip().lower()
    resultados = {}

    for clave, texto in POLITICAS_OPERATIVAS.items():
        if clave in consulta or any(palabra in texto.lower() for palabra in consulta.split()):
            resultados[clave] = texto

    if not resultados:
        resultados = POLITICAS_OPERATIVAS

    return json.dumps(resultados, ensure_ascii=False, indent=2)


@tool
def check_availability(
    fecha: str,
    hora: str,
    cantidad_personas: int,
    zona_preferida: str = "",
) -> str:
    """
    Consulta disponibilidad real para una fecha, hora y cantidad de personas.

    Usa esta herramienta antes de ofrecer o confirmar cualquier reserva.
    La fecha debe estar en YYYY-MM-DD o DD/MM/YYYY. La hora debe estar en HH:MM.
    """

    try:
        fecha_norm = _normalizar_fecha(fecha)
        hora_norm = _normalizar_hora(hora)
    except ValueError as error:
        return f"No se pudo consultar disponibilidad: {error}"

    if cantidad_personas <= 0:
        return "No se pudo consultar disponibilidad: la cantidad de personas debe ser mayor que cero."

    if cantidad_personas > RESTAURANTE["max_personas_autonomo"]:
        return (
            "El grupo supera el limite de gestion autonoma "
            f"({RESTAURANTE['max_personas_autonomo']} personas). "
            "Debe escalarse al equipo del restaurante."
        )

    opciones_exactas = _opciones_mesas(
        fecha_norm,
        hora_norm,
        cantidad_personas,
        zona_preferida=zona_preferida,
    )

    if opciones_exactas:
        respuesta = {
            "disponible": True,
            "fecha": fecha_norm,
            "hora": hora_norm,
            "opciones": opciones_exactas,
            "mensaje": "Hay disponibilidad en el horario solicitado.",
        }
    else:
        alternativas = _buscar_opciones_rankeadas(
            fecha_norm,
            hora_norm,
            cantidad_personas,
            zona_preferida=zona_preferida,
        )
        respuesta = {
            "disponible": False,
            "fecha": fecha_norm,
            "hora": hora_norm,
            "alternativas": alternativas,
            "mensaje": "No hay disponibilidad exacta; revisa alternativas cercanas.",
        }

    return json.dumps(respuesta, ensure_ascii=False, indent=2)


@tool
def rank_reservation_options(
    fecha: str,
    hora_preferida: str,
    cantidad_personas: int,
    zona_preferida: str = "",
    telefono_cliente: str = "",
) -> str:
    """
    Evalua y rankea alternativas de reserva usando una funcion de utilidad.

    La utilidad considera preferencia de zona, ajuste de capacidad,
    eficiencia operativa, cercania al horario pedido e historial del cliente.
    Usa esta herramienta cuando el horario exacto no este disponible o
    cuando quieras recomendar la mejor alternativa entre varias opciones.
    """

    try:
        fecha_norm = _normalizar_fecha(fecha)
        hora_norm = _normalizar_hora(hora_preferida)
    except ValueError as error:
        return f"No se pudieron rankear opciones: {error}"

    if cantidad_personas <= 0:
        return "No se pudieron rankear opciones: la cantidad de personas debe ser mayor que cero."

    opciones = _buscar_opciones_rankeadas(
        fecha_norm,
        hora_norm,
        cantidad_personas,
        zona_preferida=zona_preferida,
        telefono_cliente=telefono_cliente,
    )

    if not opciones:
        return (
            "No se encontraron alternativas automaticas. "
            "Escala el caso al equipo del restaurante."
        )

    return json.dumps({
        "fecha": fecha_norm,
        "hora_preferida": hora_norm,
        "opciones_rankeadas": opciones,
        "criterio": (
            "U = 0.30 preference_fit + 0.25 capacity_fit + "
            "0.20 operational_efficiency + 0.15 waiting_time_score + "
            "0.10 customer_history_fit - penalties"
        ),
    }, ensure_ascii=False, indent=2)


@tool
def create_reservation_request(
    nombre_cliente: str,
    telefono_cliente: str,
    fecha: str,
    hora: str,
    cantidad_personas: int,
    zona_preferida: str = "",
    ocasion: str = "",
    notas: str = "",
    alergias: str = "",
    confirmacion_cliente: bool = False,
) -> str:
    """
    Crea una reserva despues de validar disponibilidad.

    Usa esta herramienta solo si el cliente ya vio el resumen de la reserva
    y confirmo expresamente que desea crearla. Pasa confirmacion_cliente=True
    unicamente cuando esa confirmacion sea clara.
    """

    if not confirmacion_cliente:
        return (
            "No se registro la reserva. Antes debes mostrar un resumen y "
            "recibir confirmacion explicita del cliente."
        )

    telefono_norm = _normalizar_telefono(telefono_cliente)

    if len(telefono_norm) < 6:
        return "No se registro la reserva. El telefono del cliente es obligatorio."

    if cantidad_personas <= 0:
        return "No se registro la reserva. La cantidad de personas debe ser mayor que cero."

    if cantidad_personas > RESTAURANTE["max_personas_autonomo"]:
        codigo = _registrar_escalamiento_interno(
            motivo="grupo_mayor_a_limite_autonomo",
            resumen=(
                f"Cliente {nombre_cliente}, telefono {telefono_norm}, "
                f"solicita reserva para {cantidad_personas} personas."
            ),
            urgencia="alta",
        )
        return (
            "No se creo una reserva automatica porque el grupo supera el "
            "limite de gestion autonoma. Se escalo al equipo con codigo "
            f"{codigo}."
        )

    try:
        fecha_norm = _normalizar_fecha(fecha)
        hora_norm = _normalizar_hora(hora)
    except ValueError as error:
        return f"No se registro la reserva: {error}"

    opciones = _buscar_opciones_rankeadas(
        fecha_norm,
        hora_norm,
        cantidad_personas,
        zona_preferida=zona_preferida,
        telefono_cliente=telefono_norm,
    )
    opciones_exactas = [
        opcion
        for opcion in opciones
        if opcion["hora"] == hora_norm
    ]

    if not opciones_exactas:
        return json.dumps({
            "reserva_creada": False,
            "motivo": "No hay disponibilidad exacta para crear la reserva.",
            "alternativas": opciones,
        }, ensure_ascii=False, indent=2)

    mejor_opcion = opciones_exactas[0]
    codigo_reserva = f"RES-{uuid4().hex[:8].upper()}"
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    estado = "confirmada"
    requiere_revision = False

    if alergias.strip():
        estado = "pendiente_revision_staff"
        requiere_revision = True

    reserva = {
        "codigo_reserva": codigo_reserva,
        "fecha_registro": fecha_registro,
        "restaurant_id": RESTAURANTE["restaurant_id"],
        "nombre_cliente": nombre_cliente.strip(),
        "telefono_cliente": telefono_norm,
        "fecha": fecha_norm,
        "hora": hora_norm,
        "cantidad_personas": cantidad_personas,
        "zona": mejor_opcion["zona"],
        "mesa_ids": mejor_opcion["mesa_ids"],
        "capacidad_total": mejor_opcion["capacidad_total"],
        "duracion_minutos": RESTAURANTE["duracion_reserva_minutos"],
        "ocasion": ocasion.strip(),
        "notas": notas.strip(),
        "alergias": alergias.strip(),
        "estado": estado,
        "score_utilidad": mejor_opcion.get("score_utilidad"),
        "confirmacion_cliente": True,
    }

    reservas = _leer_json(ARCHIVO_RESERVAS, [])
    reservas.append(reserva)
    _guardar_json(ARCHIVO_RESERVAS, reservas)

    clientes = _leer_json(ARCHIVO_CLIENTES, {})
    cliente = clientes.setdefault(telefono_norm, {
        "nombre": nombre_cliente.strip(),
        "telefono": telefono_norm,
        "preferencias": {},
        "historial_reservas": [],
        "no_show_count": 0,
    })
    cliente["nombre"] = nombre_cliente.strip()
    cliente.setdefault("historial_reservas", []).append(codigo_reserva)

    if zona_preferida.strip():
        cliente.setdefault("preferencias", {})["zona_preferida"] = zona_preferida.strip().lower()

    if alergias.strip():
        cliente.setdefault("notas_criticas", []).append({
            "tipo": "alergia_o_condicion_alimentaria",
            "valor": alergias.strip(),
            "fuente": "reserva_confirmada",
            "fecha": fecha_registro,
        })

    clientes[telefono_norm] = cliente
    _guardar_json(ARCHIVO_CLIENTES, clientes)

    escalamiento = None
    if requiere_revision:
        escalamiento = _registrar_escalamiento_interno(
            motivo="alergia_o_condicion_alimentaria",
            resumen=(
                f"Reserva {codigo_reserva} contiene nota critica: "
                f"{alergias.strip()}"
            ),
            urgencia="alta",
            codigo_reserva=codigo_reserva,
        )

    respuesta = {
        "reserva_creada": True,
        "codigo_reserva": codigo_reserva,
        "estado": estado,
        "fecha": fecha_norm,
        "hora": hora_norm,
        "personas": cantidad_personas,
        "zona": mejor_opcion["zona"],
        "mesa_ids": mejor_opcion["mesa_ids"],
        "requiere_revision_staff": requiere_revision,
        "codigo_escalamiento": escalamiento,
    }

    return json.dumps(respuesta, ensure_ascii=False, indent=2)


@tool
def modify_reservation(
    codigo_reserva: str,
    nueva_fecha: str,
    nueva_hora: str,
    nueva_cantidad_personas: int,
    zona_preferida: str = "",
    confirmacion_cliente: bool = False,
) -> str:
    """
    Modifica una reserva existente tras validar disponibilidad.

    Usa esta herramienta solo despues de que el cliente confirme
    expresamente el cambio propuesto.
    """

    if not confirmacion_cliente:
        return (
            "No se modifico la reserva. Debes presentar el cambio y recibir "
            "confirmacion explicita del cliente."
        )

    reservas = _leer_json(ARCHIVO_RESERVAS, [])
    codigo = codigo_reserva.strip().upper()
    reserva = next(
        (item for item in reservas if item.get("codigo_reserva") == codigo),
        None,
    )

    if not reserva:
        return f"No se encontro ninguna reserva con el codigo {codigo}."

    if reserva.get("estado") == "cancelada":
        return f"La reserva {codigo} ya esta cancelada y no puede modificarse."

    if nueva_cantidad_personas > RESTAURANTE["max_personas_autonomo"]:
        return (
            "El nuevo grupo supera el limite de gestion autonoma. "
            "Escala el caso al equipo del restaurante."
        )

    try:
        fecha_norm = _normalizar_fecha(nueva_fecha)
        hora_norm = _normalizar_hora(nueva_hora)
    except ValueError as error:
        return f"No se modifico la reserva: {error}"

    telefono = reserva.get("telefono_cliente", "")
    opciones = _buscar_opciones_rankeadas(
        fecha_norm,
        hora_norm,
        nueva_cantidad_personas,
        zona_preferida=zona_preferida,
        telefono_cliente=telefono,
        excluir_codigo=codigo,
    )
    opciones_exactas = [
        opcion
        for opcion in opciones
        if opcion["hora"] == hora_norm
    ]

    if not opciones_exactas:
        return json.dumps({
            "reserva_modificada": False,
            "motivo": "No hay disponibilidad exacta para el cambio solicitado.",
            "alternativas": opciones,
        }, ensure_ascii=False, indent=2)

    mejor_opcion = opciones_exactas[0]
    reserva.update({
        "fecha": fecha_norm,
        "hora": hora_norm,
        "cantidad_personas": nueva_cantidad_personas,
        "zona": mejor_opcion["zona"],
        "mesa_ids": mejor_opcion["mesa_ids"],
        "capacidad_total": mejor_opcion["capacidad_total"],
        "fecha_ultima_modificacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score_utilidad": mejor_opcion.get("score_utilidad"),
    })

    _guardar_json(ARCHIVO_RESERVAS, reservas)

    return json.dumps({
        "reserva_modificada": True,
        "codigo_reserva": codigo,
        "fecha": fecha_norm,
        "hora": hora_norm,
        "personas": nueva_cantidad_personas,
        "zona": mejor_opcion["zona"],
        "mesa_ids": mejor_opcion["mesa_ids"],
    }, ensure_ascii=False, indent=2)


@tool
def cancel_reservation(
    codigo_reserva: str,
    motivo: str = "",
    confirmacion_cliente: bool = False,
) -> str:
    """
    Cancela una reserva existente.

    Usa esta herramienta solo si el cliente confirma expresamente que
    desea cancelar la reserva.
    """

    if not confirmacion_cliente:
        return (
            "No se cancelo la reserva. Debes recibir confirmacion explicita "
            "del cliente antes de cancelar."
        )

    reservas = _leer_json(ARCHIVO_RESERVAS, [])
    codigo = codigo_reserva.strip().upper()

    for reserva in reservas:
        if reserva.get("codigo_reserva") == codigo:
            if reserva.get("estado") == "cancelada":
                return f"La reserva {codigo} ya estaba cancelada."

            reserva["estado"] = "cancelada"
            reserva["motivo_cancelacion"] = motivo.strip()
            reserva["fecha_cancelacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _guardar_json(ARCHIVO_RESERVAS, reservas)

            return f"Reserva {codigo} cancelada correctamente."

    return f"No se encontro ninguna reserva con el codigo {codigo}."


@tool
def consultar_reserva(
    codigo_reserva: str = "",
    telefono_cliente: str = "",
) -> str:
    """
    Consulta reservas existentes por codigo de reserva o telefono del cliente.

    Usa codigo_reserva cuando el cliente lo tenga. Usa telefono_cliente
    cuando el cliente no recuerde el codigo.
    """

    reservas = _leer_json(ARCHIVO_RESERVAS, [])
    codigo = codigo_reserva.strip().upper()
    telefono = _normalizar_telefono(telefono_cliente)

    if codigo:
        for reserva in reservas:
            if reserva.get("codigo_reserva") == codigo:
                return json.dumps(reserva, ensure_ascii=False, indent=2)
        return f"No se encontro ninguna reserva con el codigo {codigo}."

    if telefono:
        coincidencias = [
            reserva
            for reserva in reservas
            if reserva.get("telefono_cliente") == telefono
        ]

        if not coincidencias:
            return f"No se encontraron reservas para el telefono {telefono}."

        return json.dumps(coincidencias[-5:], ensure_ascii=False, indent=2)

    return "Para consultar una reserva necesito el codigo de reserva o el telefono del cliente."


@tool
def save_customer_memory(
    nombre_cliente: str,
    telefono_cliente: str,
    preferencia: str,
    valor: str,
    consentimiento_explicito: bool = False,
) -> str:
    """
    Guarda una preferencia de cliente en memoria de largo plazo.

    Usa esta herramienta solo si la preferencia es relevante para futuras
    reservas y el cliente la dijo claramente o acepto que se recuerde.
    No guarda DNI, tarjetas, CVV, contrasenas ni datos de pago.
    """

    if not consentimiento_explicito:
        return (
            "No se guardo la memoria. Debes tener consentimiento explicito "
            "o evidencia clara de que el cliente quiere recordar esa preferencia."
        )

    clave = preferencia.strip().lower()
    valor = valor.strip()
    telefono = _normalizar_telefono(telefono_cliente)

    if len(telefono) < 6:
        return "No se guardo la memoria. El telefono del cliente es obligatorio."

    prohibidos = {
        "dni",
        "tarjeta",
        "cvv",
        "pin",
        "password",
        "contrasena",
        "contraseña",
        "pago",
    }

    if any(token in clave for token in prohibidos):
        return "No se guardo la memoria porque el dato no debe persistirse en este flujo."

    clientes = _leer_json(ARCHIVO_CLIENTES, {})
    cliente = clientes.setdefault(telefono, {
        "nombre": nombre_cliente.strip(),
        "telefono": telefono,
        "preferencias": {},
        "historial_reservas": [],
        "no_show_count": 0,
    })

    cliente["nombre"] = nombre_cliente.strip()
    cliente.setdefault("preferencias", {})[clave] = {
        "valor": valor,
        "fuente": "conversacion_confirmada",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    clientes[telefono] = cliente
    _guardar_json(ARCHIVO_CLIENTES, clientes)

    return f"Preferencia '{clave}' guardada para {nombre_cliente}."


@tool
def escalate_to_staff(
    motivo: str,
    resumen: str,
    urgencia: str = "media",
    codigo_reserva: str = "",
) -> str:
    """
    Escala un caso al equipo humano del restaurante.

    Usa esta herramienta para grupos grandes, alergias severas, conflicto
    de capacidad, cliente molesto, eventos especiales o despues de varios
    intentos fallidos de resolver el flujo.
    """

    try:
        codigo = _registrar_escalamiento_interno(
            motivo=motivo,
            resumen=resumen,
            urgencia=urgencia,
            codigo_reserva=codigo_reserva,
        )
    except OSError as error:
        return f"No se pudo registrar el escalamiento: {error}"

    return f"Caso escalado al equipo del restaurante con codigo {codigo}."


# ------------------------------------------------------------
# 4. EXTRACCION DE RESPUESTA DEL MODELO
# ------------------------------------------------------------

def extraer_texto(contenido) -> str:
    """
    Convierte la respuesta del modelo en texto plano.

    Algunos proveedores devuelven string; otros devuelven bloques.
    """

    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):
        textos = []

        for bloque in contenido:
            if isinstance(bloque, dict):
                texto = bloque.get("text")
            else:
                texto = getattr(bloque, "text", None)

            if texto:
                textos.append(texto)

        return "\n".join(textos)

    return str(contenido)


# ------------------------------------------------------------
# 5. PROMPT DEL AGENTE
# ------------------------------------------------------------

PROMPT_SISTEMA = """
Eres Clemente Reservations & Capacity Agent, un agente especializado en
reservas y capacidad para restaurantes.

Tu objetivo es convertir conversaciones en reservas validas, verificadas
y trazables, reduciendo carga operativa para el equipo del restaurante.

ARQUITECTURA DE DECISION SELECCIONADA

El proyecto NO usa todos los tipos de agentes de IBM. Para Clemente
Reservations se seleccionan solo tres patrones porque son los que el
Profile Card exige: memoria, meta y comparacion de opciones.

1. Model-Based Reflex Agent:
   - Mantienes un estado interno de la reserva en curso: intencion,
     fecha, hora, personas, zona, contacto, notas, slots ofrecidos y
     confirmacion pendiente.
   - No repitas preguntas ya respondidas.
   - No confundas preferencias de un cliente con otro.

2. Goal-Based Agent:
   - Tu meta es completar una reserva valida.
   - Plan tipico: capturar datos -> consultar disponibilidad -> ofrecer
     slot -> mostrar resumen -> pedir confirmacion -> crear reserva.
   - Si la meta no puede alcanzarse por via normal, escala al equipo.

3. Utility-Based Agent:
   - Si no hay disponibilidad exacta, usa rank_reservation_options para
     ofrecer las mejores alternativas.
   - Explica el trade-off de forma breve: cercania al horario, zona,
     capacidad o eficiencia operativa.

TIPOS DESCARTADOS EN ESTA FASE

- Simple Reflex Agent no se usa como arquitectura base porque el agente
  necesita memoria de corto y largo plazo. Sus reglas simples aparecen
  solo como guardrails internos, por ejemplo: si falta un dato obligatorio,
  pedirlo antes de consultar disponibilidad.
- Learning Agent se descarta por ahora porque el Profile Card no define un
  critico ni una senal de feedback. Guardar preferencias con
  save_customer_memory es Long-term Memory, no aprendizaje por refuerzo.

REGLAS OBLIGATORIAS

- Nunca confirmes disponibilidad sin usar check_availability.
- Nunca crees, modifiques o canceles una reserva sin confirmacion explicita.
- Antes de crear una reserva, presenta un resumen con nombre, telefono,
  fecha, hora, personas, zona/notas y pregunta si confirma.
- Usa create_reservation_request solo despues de confirmacion clara.
- Si una tool devuelve que no hay disponibilidad exacta, no inventes cupo:
  ofrece alternativas o escala.
- No pidas DNI, tarjeta, CVV, contrasenas, codigos SMS ni datos de pago.
- Las alergias o condiciones alimentarias son nota critica. No prometas
  seguridad alimentaria absoluta; registra y escala si corresponde.
- Para grupos de mas de 8 personas o eventos privados, escala al equipo.
- Si despues de tres intentos no logras completar el flujo, escala con un
  resumen de lo ocurrido.

TOOLS DISPONIBLES

- get_restaurant_policy: recupera reglas operativas vigentes.
- check_availability: consulta disponibilidad real.
- rank_reservation_options: rankea alternativas por utilidad.
- create_reservation_request: crea reserva tras confirmacion explicita.
- modify_reservation: modifica reserva tras confirmacion explicita.
- cancel_reservation: cancela reserva tras confirmacion explicita.
- consultar_reserva: busca reservas por codigo o telefono.
- save_customer_memory: guarda preferencias con consentimiento.
- escalate_to_staff: deriva casos especiales al equipo humano.

ESTILO DE RESPUESTA

- Conversa en espanol claro, amable y directo.
- Haz una pregunta por turno cuando falten datos.
- Cuando muestres alternativas, ofrece maximo tres.
- Cuando uses herramientas, resume el resultado para el cliente sin mostrar
  JSON crudo salvo que sea util para auditoria.
"""


agent = create_agent(
    model=MODELO,
    system_prompt=PROMPT_SISTEMA,
    tools=[
        get_restaurant_policy,
        check_availability,
        rank_reservation_options,
        create_reservation_request,
        modify_reservation,
        cancel_reservation,
        consultar_reserva,
        save_customer_memory,
        escalate_to_staff,
    ],
)


# ------------------------------------------------------------
# 6. CHAT PRINCIPAL
# ------------------------------------------------------------

def iniciar_chat() -> None:
    """
    Inicia el chat de consola y recupera memoria reciente.
    """

    mensajes = cargar_memoria_corta()

    print("=" * 70)
    print("CLEMENTE RESERVATIONS & CAPACITY AGENT")
    print("Agente semi-autonomo para reservas de restaurantes")
    print("=" * 70)
    print("Escriba 'salir' para finalizar.")
    print("Escriba 'nuevo' para iniciar una conversacion nueva.")
    print()

    if mensajes:
        print(
            "Se recupero el contexto reciente almacenado en "
            f"{ARCHIVO_HISTORIAL.name}.\n"
        )

    while True:
        try:
            entrada_usuario = input("Cliente: ").strip()

            if not entrada_usuario:
                continue

            if entrada_usuario.lower() in {"salir", "exit", "quit"}:
                print("Agente: Gracias por comunicarte con Clemente. Hasta luego.")
                break

            if entrada_usuario.lower() == "nuevo":
                mensajes = []
                print(
                    "Agente: Se inicio una conversacion nueva. "
                    "El historial anterior continua guardado."
                )
                continue

            guardar_mensaje("user", entrada_usuario)
            mensajes.append({"role": "user", "content": entrada_usuario})

            resultado = agent.invoke({"messages": mensajes})
            contenido_respuesta = resultado["messages"][-1].content
            respuesta_agente = extraer_texto(contenido_respuesta)

            print(f"Agente: {respuesta_agente}")

            guardar_mensaje("assistant", respuesta_agente)
            mensajes.append({"role": "assistant", "content": respuesta_agente})

        except KeyboardInterrupt:
            print("\nAgente: Conversacion finalizada por el usuario.")
            break

        except Exception as error:
            print("Agente: Ocurrio un error al procesar la solicitud.")
            print(f"Detalle tecnico: {error}")


# ------------------------------------------------------------
# 7. EJECUCION
# ------------------------------------------------------------

if __name__ == "__main__":
    if MODELO.startswith("anthropic:") and not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "No se encontro ANTHROPIC_API_KEY. Agregala al archivo .env "
            "o ejecuta con CLEMENTE_MODEL=ollama:llama3.2 si usaras Ollama."
        )

    iniciar_chat()
