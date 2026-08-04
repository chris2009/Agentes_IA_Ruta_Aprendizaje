import json
import os
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv

from _utils import resolver_modelo

load_dotenv()

_FUENTES_PATH = os.path.join(os.path.dirname(__file__), "fuentes_investigacion.json")
with open(_FUENTES_PATH, "r", encoding="utf-8") as file:
    _FUENTES = json.load(file)


@tool
def buscar_fuentes(palabra_clave: str) -> str:
    """
    Busca en la base de datos interna de investigacion notas sobre el impacto de la IA en la fuerza laboral.

    Args:
        palabra_clave: categoria o termino a buscar, por ejemplo "automatizacion", "creacion_empleo",
            "habilidades", "sectores_afectados", "politicas_publicas" o "datos_estudios".

    Returns:
        Los datos encontrados que coinciden con la palabra clave (en la categoria o en el texto del dato).
    """
    termino = palabra_clave.strip().lower()
    coincidencias = [
        f"[{f['categoria']}] {f['dato']}"
        for f in _FUENTES
        if termino in f["categoria"].lower() or termino in f["dato"].lower()
    ]
    if not coincidencias:
        return f"No se encontraron datos para '{palabra_clave}'. Categorias disponibles: {', '.join(sorted(set(f['categoria'] for f in _FUENTES)))}"
    return "\n".join(coincidencias)


MODELO = resolver_modelo(temperature=0.2)

with open(os.path.join(os.path.dirname(__file__), "investigador.prompt"), "r", encoding="utf-8") as file:
    investigador_prompt = file.read()

investigador = create_agent(
    model=MODELO,
    system_prompt=investigador_prompt,
    tools=[buscar_fuentes],
)
