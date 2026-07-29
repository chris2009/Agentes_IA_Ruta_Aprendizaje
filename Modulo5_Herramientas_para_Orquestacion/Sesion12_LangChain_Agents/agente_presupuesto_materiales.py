"""
# Agente de cálculo presupuestal de materiales de oficina (Tool Calling Agent)
################################################################################

Lab de la Sesion12: un agente construido con `langchain.agents.create_agent`
(misma API que `agente_analista_reclamos.py` de la Sesion11) al que se le
describe, en lenguaje natural, qué materiales de oficina se necesitan y en
qué cantidad. El agente arma el presupuesto llamando a sus propias tools en
vez de calcular los montos "de memoria":

    1. consultar_precio_material  -> busca el precio unitario de un material
       en el catálogo interno (el LLM no conoce precios, solo la tool).
    2. calcular_subtotal_item     -> multiplica precio_unitario x cantidad.
       Existe como tool (y no como cuenta mental del LLM) porque un modelo de
       lenguaje puede desviarse en aritmética exacta; delegar la multiplicación
       a código Python la hace determinística.
    3. generar_presupuesto_final  -> con la lista completa de ítems ya
       cotizados, recalcula los subtotales (nunca confía en los números que
       "recuerda" el LLM), suma el subtotal general, aplica IGV (18%, Perú)
       si corresponde, y guarda un reporte en Markdown -- mismo patrón que
       generar_reporte_resolucion() en agente_analista_reclamos.py.

No hay memoria de conversación entre presupuestos (cada consulta es
independiente, como en agente_analista_reclamos.py): no hace falta un
checkpointer para este ejercicio.

Requisitos (venv compartido del módulo, ver ../requirements.txt):
    pip install -U langchain langchain-anthropic python-dotenv pydantic

    Backend: Anthropic (Claude). Requiere en Sesion12/.env:
        ANTHROPIC_API_KEY=sk-ant-...

Ejecutar el chat interactivo:
    python agente_presupuesto_materiales.py
"""

import os
import unicodedata
from datetime import datetime
from difflib import get_close_matches
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.tools import tool


# ------------------------------------------------------------
# 1. CONFIGURACIÓN
# ------------------------------------------------------------

load_dotenv()

# Carpeta donde se guarda un .md por cada presupuesto generado.
CARPETA_REPORTES = Path(__file__).parent / "presupuestos_generados"

# IGV vigente en Perú, usado por generar_presupuesto_final.
PORCENTAJE_IGV = 0.18


# ------------------------------------------------------------
# 2. CATÁLOGO DE MATERIALES DE OFICINA
# ------------------------------------------------------------
#
# Catálogo fijo de ejemplo (precios en soles, S/). En un caso real esto
# vendría de una base de datos o de un ERP; aquí se deja como diccionario
# en memoria para mantener el foco del ejercicio en el tool calling.

CATALOGO_MATERIALES: dict[str, dict] = {
    "papel bond a4": {"precio_unitario": 14.90, "unidad": "paquete x 500 hojas"},
    "lapicero": {"precio_unitario": 1.20, "unidad": "unidad"},
    "lapiz": {"precio_unitario": 0.80, "unidad": "unidad"},
    "folder manila": {"precio_unitario": 0.60, "unidad": "unidad"},
    "folder plastico": {"precio_unitario": 1.50, "unidad": "unidad"},
    "toner impresora": {"precio_unitario": 189.90, "unidad": "unidad"},
    "cartucho de tinta": {"precio_unitario": 45.00, "unidad": "unidad"},
    "grapadora": {"precio_unitario": 12.50, "unidad": "unidad"},
    "caja de grapas": {"precio_unitario": 3.20, "unidad": "caja x 1000"},
    "perforador": {"precio_unitario": 15.00, "unidad": "unidad"},
    "resaltador": {"precio_unitario": 2.50, "unidad": "unidad"},
    "corrector liquido": {"precio_unitario": 3.80, "unidad": "unidad"},
    "cinta adhesiva": {"precio_unitario": 2.00, "unidad": "unidad"},
    "post-it": {"precio_unitario": 4.50, "unidad": "paquete x 100 hojas"},
    "archivador de palanca": {"precio_unitario": 9.90, "unidad": "unidad"},
    "sobre manila": {"precio_unitario": 0.40, "unidad": "unidad"},
    "tijera": {"precio_unitario": 5.50, "unidad": "unidad"},
    "regla": {"precio_unitario": 2.20, "unidad": "unidad"},
    "calculadora": {"precio_unitario": 25.00, "unidad": "unidad"},
    "mouse": {"precio_unitario": 35.00, "unidad": "unidad"},
    "teclado": {"precio_unitario": 45.00, "unidad": "unidad"},
}


def _normalizar(texto: str) -> str:
    """
    Quita tildes y pasa a minúsculas, para poder comparar nombres de
    materiales sin importar cómo los escriba el usuario o el modelo
    ("Papel Bond A4" == "papel bond a4" == "papel bond a4 ").
    """

    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c)
    )
    return sin_tildes.strip()


def _buscar_material(nombre_material: str) -> tuple[str, dict] | None:
    """Devuelve (nombre_catalogo, datos) del material, o None si no existe."""

    clave = _normalizar(nombre_material)
    if clave in CATALOGO_MATERIALES:
        return clave, CATALOGO_MATERIALES[clave]
    return None


# ------------------------------------------------------------
# 3. HERRAMIENTAS DEL AGENTE
# ------------------------------------------------------------

@tool
def consultar_precio_material(nombre_material: str) -> str:
    """
    Busca un material de oficina en el catálogo interno y devuelve su
    precio unitario y su unidad de medida.

    Usa esta herramienta para CADA material que el usuario mencione,
    antes de calcular ningún subtotal: no inventes precios, siempre
    consúltalos aquí primero.
    """

    encontrado = _buscar_material(nombre_material)

    if encontrado is not None:
        clave, datos = encontrado
        return (
            f"Material: {clave} | Precio unitario: S/ {datos['precio_unitario']:.2f} "
            f"| Unidad: {datos['unidad']}"
        )

    sugerencias = get_close_matches(
        _normalizar(nombre_material), CATALOGO_MATERIALES.keys(), n=3, cutoff=0.5
    )

    if sugerencias:
        return (
            f"'{nombre_material}' no está en el catálogo. "
            f"¿Quisiste decir alguno de estos?: {', '.join(sugerencias)}"
        )

    catalogo_completo = ", ".join(sorted(CATALOGO_MATERIALES.keys()))
    return (
        f"'{nombre_material}' no está en el catálogo y no se encontraron "
        f"materiales similares. Materiales disponibles: {catalogo_completo}"
    )


@tool
def calcular_subtotal_item(precio_unitario: float, cantidad: float) -> str:
    """
    Calcula el subtotal de un ítem del presupuesto (precio_unitario x
    cantidad).

    Usa siempre esta herramienta para multiplicar, en vez de calcularlo
    tú mismo: así el resultado es exacto. Llama a esta herramienta una
    vez por cada material, después de haber consultado su precio con
    consultar_precio_material.
    """

    subtotal = precio_unitario * cantidad
    return (
        f"Subtotal: S/ {subtotal:.2f} "
        f"({cantidad} x S/ {precio_unitario:.2f})"
    )


class ItemPresupuesto(BaseModel):
    """Un ítem ya cotizado (precio consultado y subtotal calculado)."""

    material: str = Field(description="Nombre del material, tal como aparece en el catálogo.")
    cantidad: float = Field(description="Cantidad solicitada de ese material.")
    precio_unitario: float = Field(description="Precio unitario devuelto por consultar_precio_material.")
    subtotal: float = Field(description="precio_unitario x cantidad, devuelto por calcular_subtotal_item.")


@tool
def generar_presupuesto_final(items: list[ItemPresupuesto], incluir_igv: bool = True) -> str:
    """
    Registra el presupuesto final y genera su reporte en formato Markdown.

    Usa esta herramienta solo después de haber consultado el precio y
    calculado el subtotal de TODOS los materiales solicitados por el
    usuario, pasando la lista completa de ítems en un solo llamado.

    "incluir_igv" debe ser True salvo que el usuario pida explícitamente
    un presupuesto sin IGV.
    """

    if not items:
        return "No se generó el presupuesto: no se recibió ningún ítem."

    # No se confía en los subtotales que "recuerda" el modelo: se
    # recalculan aquí a partir de precio_unitario y cantidad, igual que
    # calcular_subtotal_item, para que el reporte final sea siempre exacto.
    filas = []
    subtotal_general = 0.0

    for item in items:
        subtotal_item = item.precio_unitario * item.cantidad
        subtotal_general += subtotal_item
        filas.append(
            f"| {item.material} | {item.cantidad:g} | S/ {item.precio_unitario:.2f} "
            f"| S/ {subtotal_item:.2f} |"
        )

    igv = subtotal_general * PORCENTAJE_IGV if incluir_igv else 0.0
    total = subtotal_general + igv

    fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    codigo_presupuesto = f"PRES-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    contenido_md = f"""# Presupuesto de materiales de oficina

**Código:** {codigo_presupuesto}
**Fecha de generación:** {fecha_generacion}

## Detalle

| Material | Cantidad | Precio unitario | Subtotal |
|---|---|---|---|
{chr(10).join(filas)}

## Resumen

| Concepto | Monto |
|---|---|
| Subtotal general | S/ {subtotal_general:.2f} |
| IGV (18%) | S/ {igv:.2f} |
| **Total** | **S/ {total:.2f}** |
"""

    try:
        CARPETA_REPORTES.mkdir(exist_ok=True)
        archivo_reporte = CARPETA_REPORTES / f"{codigo_presupuesto}.md"
        archivo_reporte.write_text(contenido_md, encoding="utf-8")

    except OSError as error:
        return f"No se pudo guardar el reporte: {error}"

    return (
        f"Presupuesto {codigo_presupuesto} generado con {len(items)} ítem(s). "
        f"Total: S/ {total:.2f} (IGV {'incluido' if incluir_igv else 'no incluido'}). "
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
Eres un agente que arma presupuestos de materiales de oficina para una
empresa. No conversas de forma abierta: recibes una lista de materiales
y cantidades que necesita la oficina, y debes calcular el presupuesto
usando tus herramientas.

Flujo obligatorio, por cada material que el usuario mencione:

1. Usa consultar_precio_material para obtener su precio unitario. Si el
   material no está en el catálogo, informa al usuario cuáles son las
   opciones más parecidas (o el catálogo completo) y NO inventes un
   precio para él.
2. Usa calcular_subtotal_item con el precio_unitario obtenido y la
   cantidad pedida. Nunca multipliques tú mismo: usa siempre esta
   herramienta.

Cuando ya tengas el precio y el subtotal de TODOS los materiales
solicitados:

3. Usa generar_presupuesto_final exactamente una vez, pasando la lista
   completa de ítems (material, cantidad, precio_unitario, subtotal) y
   el parámetro incluir_igv (True por defecto, salvo que el usuario pida
   explícitamente un presupuesto sin IGV).
4. Responde al usuario con un resumen breve: ítems cotizados, subtotal,
   IGV y total.

Reglas:
- Si el usuario no indica una cantidad para algún material, pídesela
  antes de cotizarlo; no asumas cantidad 1 por tu cuenta.
- Nunca inventes precios ni materiales que no estén en el catálogo.
- Sé breve y profesional en tus respuestas.
"""

# LLM_PROVIDER elige el backend del modelo (mismo patrón que main.py de la
# Sesion11): "anthropic" (por defecto, de pago, consume tokens de la API) u
# "ollama" (modelo corriendo en local, gratis, no requiere ANTHROPIC_API_KEY).
# `create_agent` resuelve el string "proveedor:modelo" automáticamente, sin
# necesidad de instanciar el chat model a mano.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()

if LLM_PROVIDER == "ollama":
    # Requiere tener Ollama corriendo en local (`ollama serve`) y el modelo
    # ya descargado (`ollama pull llama3.2`).
    MODEL_ID = f"ollama:{os.getenv('OLLAMA_MODEL', 'llama3.2')}"
else:
    MODEL_ID = f"anthropic:{os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-6')}"

agent = create_agent(
    model=MODEL_ID,
    system_prompt=PROMPT_SISTEMA,
    tools=[
        consultar_precio_material,
        calcular_subtotal_item,
        generar_presupuesto_final,
    ],
)


# ------------------------------------------------------------
# 6. FLUJO PRINCIPAL
# ------------------------------------------------------------

def iniciar_presupuesto() -> None:
    """
    Punto de entrada interactivo. Pide una lista de materiales y
    cantidades, y ejecuta el agente para calcular el presupuesto,
    uno a la vez.

    Cada presupuesto es independiente (no hay memoria entre consultas),
    igual que en agente_analista_reclamos.py de la Sesion11.
    """

    print("=" * 60)
    print("AGENTE DE PRESUPUESTO DE MATERIALES DE OFICINA")
    print("=" * 60)
    print("Describe los materiales y cantidades que necesitas.")
    print('Ejemplo: "5 lapiceros, 2 paquetes de papel bond A4 y 1 grapadora"')
    print("Escriba 'salir' para finalizar.")
    print()

    while True:
        try:
            solicitud = input("Solicitud: ").strip()

            if not solicitud:
                continue

            if solicitud.lower() in {"salir", "exit", "quit"}:
                print("Agente: Hasta luego.")
                break

            resultado = agent.invoke({
                "messages": [{"role": "user", "content": solicitud}]
            })

            contenido_respuesta = resultado["messages"][-1].content
            respuesta_agente = extraer_texto(contenido_respuesta)

            print(f"Agente: {respuesta_agente}\n")

        except KeyboardInterrupt:
            print("\nAgente: Presupuesto finalizado por el usuario.")
            break

        except Exception as error:
            print("Agente: Ocurrió un error al procesar la solicitud.")
            print(f"Detalle técnico: {error}")


# ------------------------------------------------------------
# 7. EJECUCIÓN
# ------------------------------------------------------------

if __name__ == "__main__":
    if LLM_PROVIDER != "ollama" and not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "No se encontró ANTHROPIC_API_KEY. Agrégala al archivo "
            "Sesion12/.env, o usa LLM_PROVIDER=ollama para no depender "
            "de la API de pago."
        )

    print(f"(Usando LLM_PROVIDER={LLM_PROVIDER}, modelo={MODEL_ID})\n")
    iniciar_presupuesto()
