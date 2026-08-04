"""
Script de autenticacion unica para Google Calendar (leer eventos y crear
eventos nuevos; nunca edita ni borra uno existente).

Se corre UNA vez con el Python de Windows (no el de WSL) para evitar el
problema de reenvio de localhost entre WSL2 y Windows durante el flujo
OAuth. Genera token.json en esta misma carpeta; el agente principal
(agente_planificacion_actividades.py, corriendo en WSL) lo reutiliza
despues sin volver a pedir login.

Si ya tenias un token.json generado con el scope anterior (solo lectura),
borralo antes de correr este script: el scope cambio y Google exige un
nuevo consentimiento.

Uso:
    python autenticar_calendario.py
"""

from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

CARPETA = Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

flow = InstalledAppFlow.from_client_secrets_file(
    str(CARPETA / "credentials.json"), SCOPES
)
credenciales = flow.run_local_server(port=0)

(CARPETA / "token.json").write_text(credenciales.to_json(), encoding="utf-8")
print("Listo: token.json generado en", CARPETA / "token.json")
