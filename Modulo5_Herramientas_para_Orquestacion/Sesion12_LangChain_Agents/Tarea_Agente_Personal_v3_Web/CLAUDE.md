# CLAUDE.md — v3: Agente Personal de Planificación (web)

Contexto persistente para trabajar en esta carpeta en sesiones futuras.
Frontend React + Vite, backend FastAPI, que importa
`../Tarea_Agente_Personal_v2_ActividadesDiarias/agente_planificacion_actividades.py`
como única fuente de verdad (ver arquitectura completa en
[README.md](README.md)).

## Por qué existe este archivo

En la sesión que construyó la primera versión de este proyecto, el usuario
eligió explícitamente FastAPI + React en vez de Streamlit ("quería la
experiencia real de construir un agente web") y terminó con un frontend
que calificó de "pésimo, demasiado básico" — y con un bug real (el
explorador de archivos rechazaba cualquier subcarpeta) que pasó
desapercibido porque nunca se probó navegando de verdad. Este archivo
documenta ambas causas para no repetirlas.

## Regla 1 — Probar la UI de verdad, no solo el backend con curl

En esa sesión se reportó "probado end-to-end" habiendo solo hecho `curl`
contra los endpoints de FastAPI. Eso valida que el backend responde, pero
**no** que el flujo real en el navegador funcione — y de hecho no
funcionaba: `browseFiles` en el frontend construye `ruta_relativa` en
base a `CARPETA_AUTORIZADA`, pero el backend validaba esa misma ruta con
`v2._validar_ruta()`, que la resuelve relativa a la carpeta de v2 (un
ancla distinta). El resultado: cualquier clic en una subcarpeta desde la
página Materiales o el selector de "Nueva actividad" tiraba un 403. `curl`
al endpoint raíz nunca lo hubiera revelado porque solo se probó la carpeta
raíz, no la navegación real que hace un usuario.

**Antes de reportar una feature de UI como lista:**
- Si hay forma de abrir un navegador real (herramienta de screenshot, MCP
  de browser, o pedirle al usuario que confirme un flujo concreto),
  úsala.
- Si no la hay, dilo explícitamente ("no puedo probar el navegador desde
  aquí, verifiqué X e Y por API pero el flujo Z no está confirmado") en
  vez de dar a entender que todo quedó probado.
- Cuando dos partes del sistema comparten una convención de rutas
  (ejemplo real: "relativo a CARPETA_AUTORIZADA" vs. "relativo a la
  carpeta del módulo"), verificar que ambos lados usan la MISMA ancla —
  no asumir que una función auxiliar existente (`_validar_ruta` de v2)
  sirve tal cual para un caso de uso nuevo si su contrato no está escrito
  en ningún lado. Ver el fix real en
  `backend/app/routers/files.py::_resolver_dentro_de_carpeta_autorizada`.

## Regla 2 — El nivel de acabado del frontend debe ser real, no un MVP

El usuario dijo textualmente: "si elegí esta opción es porque pensé que lo
ibas a hacer mejor, sino me quedaba con la primera opción que me diste de
solo Python [Streamlit]". Elegir React sobre Streamlit es una señal
explícita de que quiere un producto con cara de producto, no una demo
funcional con HTML sin estilo.

**Estándar mínimo para cualquier página nueva o modificada en
`frontend/`:**
- Usar los tokens de diseño ya definidos en `src/styles/global.css`
  (`--color-*`, `--space-*`, `--radius-*`, `--shadow-card`) — no colores
  ni espaciados sueltos.
- Estados de carga con `<Spinner />`, mensajes de error/éxito con
  `<Banner type="error|success|info">`, listas vacías con `.empty-state`
  — nunca un `<p>` de texto plano rojo/verde ni un `if (!datos.length)
  return null`.
- Iconos vía `lucide-react` (ya instalado) en botones y navegación, no
  emojis sueltos ni botones sin ícono cuando el resto de la página sí los
  usa.
- El layout es un sidebar fijo (`NavBar.jsx` → clase `.sidebar`) + área de
  contenido con ancho máximo — mantener esa estructura, no volver a un
  navbar superior plano.

## Cómo levantar el proyecto para probar cambios

Ver [README.md](README.md) — resumen: backend con el venv compartido
(`Modulo4_Agentes_Cognitivos/.venv`) en el puerto 8000, frontend con
`npm run dev` en el puerto 5173. Los procesos en segundo plano de una
sesión anterior NO sobreviven a un reinicio de la sesión — hay que
volver a levantarlos.
