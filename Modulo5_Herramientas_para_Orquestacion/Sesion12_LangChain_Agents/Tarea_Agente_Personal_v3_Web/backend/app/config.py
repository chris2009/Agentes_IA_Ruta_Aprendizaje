"""
Carga el modulo del agente v2 (agente_planificacion_actividades.py) como
libreria, sin duplicar su logica. v2 es la unica fuente de verdad: este
backend solo expone su logica ya existente via HTTP.

Orden critico: cargar el .env de v2 ANTES de importar su modulo, porque
agente_planificacion_actividades.py llama load_dotenv() a secas (depende
del cwd del proceso que lo importa). Con override=False (comportamiento
por defecto de python-dotenv), cargar aqui primero garantiza que las
variables correctas ya esten en os.environ cuando el load_dotenv() interno
de v2 se ejecute como no-op.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

V3_DIR = Path(__file__).resolve().parents[2]
V2_DIR = V3_DIR.parent / "Tarea_Agente_Personal_v2_ActividadesDiarias"

if not (V2_DIR / "agente_planificacion_actividades.py").exists():
    raise RuntimeError(
        f"No se encontro el agente v2 en {V2_DIR}. Este backend depende de "
        "Tarea_Agente_Personal_v2_ActividadesDiarias como hermana de "
        "Tarea_Agente_Personal_v3_Web; revisa que ambas carpetas existan."
    )

load_dotenv(V2_DIR / ".env")

sys.path.insert(0, str(V2_DIR))
import agente_planificacion_actividades as v2mod  # noqa: E402

FRONTEND_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
