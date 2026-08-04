# v3: Agente Personal de Planificación — versión web

Interfaz web ([FastAPI](https://fastapi.tiangolo.com/) — framework de Python para construir
APIs, del inglés *Application Programming Interface*, "interfaz de programación de
aplicaciones" — como backend, y [React](https://react.dev/) con [Vite](https://vite.dev/) como
frontend) sobre el agente v2
(`../Tarea_Agente_Personal_v2_ActividadesDiarias/agente_planificacion_actividades.py`), que se
importa tal cual: v2 sigue siendo la única fuente de verdad, esta carpeta solo la expone por
[API REST](https://es.wikipedia.org/wiki/Transferencia_de_Estado_Representacional) (*Application
Programming Interface* que sigue el estilo arquitectónico REST, *Representational State
Transfer* — "transferencia de estado representacional") y le agrega un frontend.

## Cómo levantar el proyecto (2 terminales)

Se necesitan **dos servidores corriendo a la vez**: el backend (FastAPI, puerto 8000) y el
frontend (Vite, puerto 5173). Van en dos terminales separadas.

### Terminal 1 — Backend

El backend importa el módulo de v2 directamente, así que necesita el **mismo entorno Python**
donde ya corre `agente_planificacion_actividades.py` (con `langchain`, `langchain-anthropic`,
`python-dotenv`, `google-api-python-client`, etc. ya instalados), más `fastapi` y `uvicorn`
(servidor [ASGI](https://asgi.readthedocs.io/) — *Asynchronous Server Gateway Interface*,
"interfaz de puerta de enlace de servidor asíncrono" — que ejecuta la app de FastAPI).

```bash
# Desde Tarea_Agente_Personal_v3_Web/backend, usando el venv compartido del programa
# (ajusta la ruta si tu venv esta en otro lugar):
../../../../Modulo4_Agentes_Cognitivos/.venv/bin/python -m pip install -r requirements.txt

../../../../Modulo4_Agentes_Cognitivos/.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Debe imprimir `Uvicorn running on http://127.0.0.1:8000`. Verifica con:

```bash
curl http://127.0.0.1:8000/api/health
```

- API: http://127.0.0.1:8000
- Documentación interactiva ([Swagger](https://swagger.io/), interfaz autogenerada para probar
  cada endpoint desde el navegador): http://127.0.0.1:8000/docs

### Terminal 2 — Frontend

```bash
cd Tarea_Agente_Personal_v3_Web/frontend
npm install     # solo la primera vez
npm run dev
```

- App: **http://127.0.0.1:5173** ← abre esta URL en el navegador

### Orden y apagado

El frontend puede arrancar antes o después del backend (recién falla al hacer la primera
llamada si el backend no está arriba). Para apagar, `Ctrl+C` en cada terminal.

## Requisito previo: re-autenticar Google Calendar

El scope de Calendar cambió esta sesión de `calendar.readonly` a `calendar.events` (para poder
agendar eventos). El `token.json` que ya tenías fue generado con el scope viejo, así que **hay
que regenerarlo** antes de que las secciones de Calendario/Planes funcionen:

```bash
# Borra el token viejo
rm Tarea_Agente_Personal_v2_ActividadesDiarias/token.json

# Genera uno nuevo con el Python de Windows (evita el bug de reenvío de
# localhost entre WSL2 y Windows durante el login OAuth — Open Authorization,
# el protocolo con el que Google Calendar autoriza el acceso sin pedir tu contraseña)
cd Tarea_Agente_Personal_v2_ActividadesDiarias
python autenticar_calendario.py
```

Sin esto, el dashboard de actividades y el chat funcionan igual; solo fallan (con un mensaje
claro, no un error 500) las llamadas que tocan Calendar.

## Variables de entorno — dónde viven

Todas las claves y configuración del agente (`ANTHROPIC_API_KEY`, `AGENT_MODEL`,
`LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL`, `LANGSMITH_*`, rutas de credenciales de Calendar) siguen
viviendo en un solo lugar: **`../Tarea_Agente_Personal_v2_ActividadesDiarias/.env`**. El backend
de v3 no tiene su propio `.env` con esos valores — en `backend/app/config.py` carga
explícitamente el `.env` de v2 antes de importar su módulo, para no duplicar configuración.

El único `.env` propio de v3 es `frontend/.env`, y solo trae una variable no-secreta:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

(Cualquier variable dentro de un `.env` de Vite queda embebida en el JavaScript que se manda al
navegador, así que ahí nunca deben ir claves — solo la URL del backend.)

## Páginas

- **Dashboard** (`/`): pendientes ordenados por puntaje de urgencia.
- **Actividades** (`/actividades`): listado completo, cambiar estado.
- **Nueva actividad** (`/actividades/nueva`): registrar una actividad/tarea pendiente (con
  selector de carpeta de materiales).
- **Calendario** (`/calendario`): eventos reales del día + formulario para **agendar un evento
  nuevo** (acción distinta de "nueva actividad": esta sí crea algo en Google Calendar).
- **Planes** (`/planes`): generar un plan para un rango horario, ver el historial con preview en
  Markdown y descargar el `.md`.
- **Materiales** (`/materiales`): explorador de la carpeta autorizada de documentos.
- **Chat** (`/chat`): conversación en lenguaje natural con el mismo agente ReAct (*Reasoning +
  Acting*, "razonamiento + actuación": el patrón de agente que razona y llama tools en pasos
  intercalados) del CLI (*Command Line Interface*, "interfaz de línea de comandos" — el
  `agente_planificacion_actividades.py` original que se usa desde la terminal).

## Notas de diseño

- Las páginas de lectura (dashboard, calendario, planes, archivos) llaman directo a la lógica de
  v2 — sin pasar por el LLM (*Large Language Model*, "modelo de lenguaje de gran tamaño"),
  instantáneo.
- Las acciones de escritura (nueva actividad, cambiar estado, agendar evento, generar plan)
  llaman a las mismas tools que usa el CLI (`.invoke(...)`) — mismo código, sin LLM de por medio.
- Solo el chat pasa por el loop ReAct completo (`agent.ainvoke(...)`).

## Solución de problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| El frontend muestra errores de red en todas las páginas | El backend no está corriendo | Revisa la Terminal 1, confirma `curl http://127.0.0.1:8000/api/health` |
| Errores de [CORS](https://developer.mozilla.org/es/docs/Web/HTTP/CORS) (*Cross-Origin Resource Sharing*, "compartición de recursos de origen cruzado": la política del navegador que bloquea llamadas entre puertos distintos si el servidor no las autoriza explícitamente) en la consola del navegador | El frontend no corre en el puerto 5173 esperado | Usa `npm run dev` sin cambiar el puerto, o ajusta `FRONTEND_ORIGINS` en `backend/app/config.py` |
| Calendario/Planes devuelven `invalid_scope` | `token.json` viejo (scope `calendar.readonly`) | Sigue la sección "Requisito previo: re-autenticar Google Calendar" arriba |
| El backend falla al arrancar con `ModuleNotFoundError` | Estás usando un Python distinto al venv de v2 | Usa el mismo intérprete que corre `agente_planificacion_actividades.py` (ver Terminal 1) |
| El chat tarda mucho o no responde | `AGENT_MODEL=gemma-lmstudio` en el `.env` de v2 pero LM Studio no está abierto | Abre LM Studio con el servidor local activo, o cambia `AGENT_MODEL=anthropic` en el `.env` de v2 |
