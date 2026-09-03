"""
Equipo publicitario multiagente para Cafe.AI -- Tarea bonus de la Sesion 15
(Modulo 5: LangGraph y sistemas multiagente).

Construye con LangGraph un equipo de cuatro roles para la primera campana de
redes sociales de Cafe.AI:

    ENRUTADOR  -- clasifica el pedido y decide la ruta del grafo
    CREATIVO   -- director creativo: define el concepto de campana
    REDACTOR   -- copywriter: escribe los posts de cada red social
    DISENADOR  -- director de arte: define el arte y el prompt de imagen

El patron es el mismo de `sol/maslc.py` y del ejemplo de *Routing* de
`intro.ipynb`: clasificacion con `with_structured_output` + despacho con
`add_conditional_edges`. La diferencia es que aqui una de las rutas no termina
en un solo agente, sino que encadena a los tres roles en pipeline.

Uso:
    python campana_cafeai.py                      # corre el pedido de ejemplo
    python campana_cafeai.py "solo dame el copy"  # corre un pedido propio
    python campana_cafeai.py --grafo              # exporta el diagrama del grafo
    AGENT_MODEL=claude python campana_cafeai.py   # cambia de backend de LLM
"""

import os
import sys
from datetime import datetime
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from _utils import AGENT_MODEL, extraer_texto, resolver_modelo
from brief_cafeai import BRIEF_CAFEAI

# El enrutador clasifica: temperatura baja para que la decision sea estable.
# Los roles creativos generan: temperatura alta para que las ideas varien.
llm_enrutador = resolver_modelo(temperature=0.1)
llm_creativo = resolver_modelo(temperature=0.8)


# ############################ ESTADO DEL GRAFO ############################

class EstadoCampana(TypedDict):
    """
    Cuaderno compartido que viaja por el grafo. Cada rol escribe su casillero y
    lee los de los roles anteriores: asi el redactor trabaja sobre el concepto
    del creativo, y el disenador sobre ambos.
    """

    pedido: str          # lo que pide el usuario (el "cliente")
    ruta: str            # decision del enrutador
    motivo_ruta: str     # por que el enrutador decidio esa ruta
    concepto: str        # entregable del creativo
    copys: str           # entregable del redactor
    diseno: str          # entregable del disenador
    entregable: str      # documento final consolidado


# ########################## SALIDA ESTRUCTURADA ###########################

class RutaCampana(BaseModel):
    """Decision del enrutador, forzada a una de las cuatro rutas validas."""

    ruta: Literal["campana_completa", "creativo", "redactor", "disenador"] = Field(
        ...,
        description=(
            "A donde enviar el pedido: "
            "'campana_completa' si piden una campana o no queda claro que rol basta; "
            "'creativo' si solo piden ideas, concepto, angulo o eslogan; "
            "'redactor' si solo piden textos, copys, captions o pies de foto; "
            "'disenador' si solo piden arte, diseno, visual, paleta o formato de imagen"
        ),
    )
    motivo: str = Field(..., description="Una frase corta explicando la decision")


PROMPT_ENRUTADOR = f"""Eres el enrutador (trafico) de una agencia de publicidad que
atiende a la marca Cafe.AI. Clasificas el pedido del cliente y decides que rol lo
atiende. NO resuelves el pedido, solo lo clasificas.

Rutas disponibles:
- campana_completa: el cliente quiere una campana, un lanzamiento, o un paquete de
  piezas para redes. Tambien es la ruta por defecto cuando el pedido es amplio o
  ambiguo.
- creativo: solo quiere ideas, concepto, gran idea, angulo, eslogan o hashtag.
- redactor: solo quiere textos ya escritos: copys, captions, pies de foto, titulares.
- disenador: solo quiere lo visual: arte, diseno, paleta, tipografia, formato o
  prompt de imagen.

Contexto de la marca:
{BRIEF_CAFEAI}"""


# ############################ NODOS DEL GRAFO #############################

def enrutador(state: EstadoCampana) -> dict:
    """Clasifica el pedido del cliente y fija la ruta del grafo."""
    decisor = llm_enrutador.with_structured_output(RutaCampana)
    try:
        decision = decisor.invoke(
            [SystemMessage(content=PROMPT_ENRUTADOR), HumanMessage(content=state["pedido"])]
        )
        ruta, motivo = decision.ruta, decision.motivo
    except Exception as error:
        # Mismo criterio de `maslc.py`: si la clasificacion falla, hay una ruta
        # por defecto en vez de romper la corrida. Aqui la mas segura es hacer la
        # campana completa: entrega de mas, no de menos.
        ruta, motivo = "campana_completa", f"fallback por error de clasificacion: {error}"

    print(f"[ENRUTADOR] ruta -> {ruta} ({motivo})")
    return {"ruta": ruta, "motivo_ruta": motivo}


def creativo(state: EstadoCampana) -> dict:
    """Director creativo: define el concepto que gobierna toda la campana."""
    print("[CREATIVO] pensando el concepto de campana...")
    sistema = f"""Eres el director creativo de la agencia. Defines el concepto de la
primera campana de lanzamiento de Cafe.AI en redes sociales.

{BRIEF_CAFEAI}

Entrega EXACTAMENTE esta estructura, en espanol, sin preambulos:

## Insight
(una frase: que le pasa de verdad al publico objetivo)

## Gran idea
(una frase que resuma el concepto de la campana)

## Eslogan
(maximo 6 palabras)

## Hashtag
(uno solo, empezando con #)

## Tono
(dos o tres adjetivos)

## Ejes de contenido
1. (eje 1: que se cuenta y por que)
2. (eje 2)
3. (eje 3)

Reglas: no inventes precios, premios ni cifras. No expliques tu razonamiento."""
    respuesta = llm_creativo.invoke(
        [
            SystemMessage(content=sistema),
            HumanMessage(content=f"Pedido del cliente: {state['pedido']}"),
        ]
    )
    return {"concepto": extraer_texto(respuesta)}


def redactor(state: EstadoCampana) -> dict:
    """Copywriter: convierte el concepto en los textos publicables."""
    print("[REDACTOR] escribiendo los copys...")
    concepto = state.get("concepto", "")
    contexto_concepto = (
        f"Concepto aprobado por el director creativo, respetalo:\n{concepto}"
        if concepto
        else "Todavia no hay concepto del creativo: propon tu mismo el angulo a partir del brief."
    )
    sistema = f"""Eres el redactor publicitario (copywriter) de la agencia. Escribes los
textos de la primera campana de Cafe.AI en redes sociales.

{BRIEF_CAFEAI}

Entrega EXACTAMENTE esta estructura, en espanol, sin preambulos:

## Instagram
Gancho: (una linea, maximo 60 caracteres)
Texto: (maximo 3 lineas)
CTA: (llamado a la accion, una linea)
Hashtags: (4 hashtags)

## LinkedIn
Gancho: (una linea)
Texto: (maximo 4 lineas, tono profesional pero humano)
CTA: (una linea)
Hashtags: (3 hashtags)

## TikTok
Gancho hablado: (primeros 3 segundos del video, una linea)
Guion: (3 lineas, una por escena)
CTA: (una linea)
Hashtags: (3 hashtags)

Reglas: no inventes precios, promociones ni horarios. No expliques tu razonamiento."""
    respuesta = llm_creativo.invoke(
        [
            SystemMessage(content=sistema),
            HumanMessage(
                content=f"Pedido del cliente: {state['pedido']}\n\n{contexto_concepto}"
            ),
        ]
    )
    return {"copys": extraer_texto(respuesta)}


def disenador(state: EstadoCampana) -> dict:
    """
    Director de arte: define la pieza visual.

    Un LLM de texto no genera imagenes, asi que este rol entrega lo que si es
    accionable: la especificacion de arte y un prompt listo para pegar en un
    generador de imagenes.
    """
    print("[DISENADOR] definiendo direccion de arte...")
    partes = []
    if state.get("concepto"):
        partes.append(f"Concepto del creativo:\n{state['concepto']}")
    if state.get("copys"):
        partes.append(
            f"Copys del redactor (el arte debe convivir con estos textos):\n{state['copys']}"
        )
    contexto = "\n\n".join(partes) or "Trabaja directamente desde el brief de marca."

    sistema = f"""Eres el director de arte de la agencia. Defines como se ve la primera
campana de Cafe.AI en redes sociales.

{BRIEF_CAFEAI}

Entrega EXACTAMENTE esta estructura, en espanol, sin preambulos:

## Concepto visual
(dos lineas: que se ve en la pieza y que sensacion deja)

## Paleta
(3 o 4 colores con su codigo hexadecimal y para que se usa cada uno)

## Tipografia
(una familia para titulo y una para texto, y por que)

## Composicion
(donde va el logo, el titular y el CTA en la pieza)

## Formatos
- Instagram: (proporcion y que se ajusta)
- LinkedIn: (proporcion y que se ajusta)
- TikTok: (proporcion y que se ajusta)

## Prompt de imagen
(un parrafo en ingles, listo para pegar en un generador de imagenes, describiendo
la escena, el estilo, la iluminacion y el encuadre; sin texto dentro de la imagen)

Reglas: no inventes premios ni datos de la marca. No expliques tu razonamiento."""
    respuesta = llm_creativo.invoke(
        [
            SystemMessage(content=sistema),
            HumanMessage(content=f"Pedido del cliente: {state['pedido']}\n\n{contexto}"),
        ]
    )
    return {"diseno": extraer_texto(respuesta)}


def consolidador(state: EstadoCampana) -> dict:
    """
    Arma el entregable final con lo que haya producido la ruta recorrida.

    No llama al LLM a proposito: es el mismo criterio del `synthesizer` del
    ejemplo orquestador-workers de `intro.ipynb`. Pegar texto ya generado es
    trabajo deterministico, y pasarlo otra vez por el modelo solo agrega
    latencia y riesgo de que reescriba o pierda contenido.
    """
    print("[CONSOLIDADOR] armando el entregable...")
    bloques = [
        "# Campana de lanzamiento -- Cafe.AI",
        f"**Pedido del cliente:** {state['pedido']}",
        f"**Ruta del equipo:** `{state['ruta']}` -- {state.get('motivo_ruta', '')}",
        f"**Modelo usado:** `{AGENT_MODEL}`",
        f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    for titulo, clave in (
        ("Concepto (director creativo)", "concepto"),
        ("Copys (redactor)", "copys"),
        ("Direccion de arte (disenador)", "diseno"),
    ):
        if state.get(clave):
            bloques.append(f"---\n\n## {titulo}\n\n{state[clave]}")
    return {"entregable": "\n\n".join(bloques)}


# ####################### ARISTAS CONDICIONALES ############################

def despachar(state: EstadoCampana) -> str:
    """Primera bifurcacion: a que nodo manda el enrutador."""
    return state["ruta"]


def seguir_a_redactor(state: EstadoCampana) -> str:
    """Tras el creativo: sigue el pipeline solo si es la campana completa."""
    return "seguir" if state["ruta"] == "campana_completa" else "cerrar"


def seguir_a_disenador(state: EstadoCampana) -> str:
    """Tras el redactor: sigue el pipeline solo si es la campana completa."""
    return "seguir" if state["ruta"] == "campana_completa" else "cerrar"


# ########################### GRAFO DEL EQUIPO #############################

constructor = StateGraph(EstadoCampana)

constructor.add_node("enrutador", enrutador)
constructor.add_node("creativo", creativo)
constructor.add_node("redactor", redactor)
constructor.add_node("disenador", disenador)
constructor.add_node("consolidador", consolidador)

constructor.add_edge(START, "enrutador")

# Ruta 1 (campana completa) entra por el creativo; las rutas puntuales entran
# directo al rol pedido.
constructor.add_conditional_edges(
    "enrutador",
    despachar,
    {
        "campana_completa": "creativo",
        "creativo": "creativo",
        "redactor": "redactor",
        "disenador": "disenador",
    },
)

constructor.add_conditional_edges(
    "creativo", seguir_a_redactor, {"seguir": "redactor", "cerrar": "consolidador"}
)
constructor.add_conditional_edges(
    "redactor", seguir_a_disenador, {"seguir": "disenador", "cerrar": "consolidador"}
)
constructor.add_edge("disenador", "consolidador")
constructor.add_edge("consolidador", END)

equipo_publicitario = constructor.compile()


# ############################## EJECUCION #################################

PEDIDO_EJEMPLO = (
    "Necesitamos la primera campana de lanzamiento de Cafe.AI para redes sociales, "
    "con concepto, textos y arte."
)

CARPETA_SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campanas_generadas")


def exportar_grafo(destino: str = "grafo_equipo_publicitario") -> str:
    """
    Guarda el diagrama del grafo. Intenta el PNG (Portable Network Graphics) via
    `draw_mermaid_png()`, que necesita internet porque renderiza en el servicio
    mermaid.ink; si no hay red, deja el codigo Mermaid en un archivo .mmd.
    """
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), destino)
    try:
        with open(f"{base}.png", "wb") as archivo:
            archivo.write(equipo_publicitario.get_graph().draw_mermaid_png())
        return f"{base}.png"
    except Exception as error:
        print(f"[GRAFO] no se pudo renderizar el PNG ({error}); guardo el Mermaid")
        with open(f"{base}.mmd", "w", encoding="utf-8") as archivo:
            archivo.write(equipo_publicitario.get_graph().draw_mermaid())
        return f"{base}.mmd"


def correr(pedido: str) -> dict:
    """Ejecuta el grafo completo y guarda el entregable en disco."""
    print(f"\n=== Cafe.AI | modelo: {AGENT_MODEL} ===")
    print(f"Pedido: {pedido}\n")
    estado = equipo_publicitario.invoke({"pedido": pedido})

    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    nombre = f"campana_{AGENT_MODEL.replace(':', '-')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    ruta_archivo = os.path.join(CARPETA_SALIDA, nombre)
    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(estado["entregable"])

    print("\n" + estado["entregable"])
    print(f"\n[OK] Entregable guardado en: {ruta_archivo}")
    return estado


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    if argumentos and argumentos[0] == "--grafo":
        print(f"[OK] Diagrama guardado en: {exportar_grafo()}")
    else:
        correr(" ".join(argumentos) if argumentos else PEDIDO_EJEMPLO)
