# Configurar Google Calendar para el agente v2

Guía paso a paso para que
[agente_planificacion_actividades.py](agente_planificacion_actividades.py)
pueda leer tu **Google Calendar** real (reuniones, cursos, citas),
planificar alrededor de esos bloques ocupados, y **agendar actividades
nuevas** cuando se lo pidas. El agente pide el scope `calendar.events`
(leer y crear eventos): puede agregar un evento nuevo, pero **nunca**
edita ni borra uno que ya existía.

No requiere modificar el código: una vez que tengas `credentials.json` en
esta carpeta, el script se conecta solo.

## Prerrequisitos

- Una cuenta de Google (Gmail) — la misma cuyo calendario quieres que el
  agente consulte.
- Las librerías ya instaladas en el venv compartido del programa:
  `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

## Paso 1 — Crear un proyecto en Google Cloud Console

1. Entra a [console.cloud.google.com](https://console.cloud.google.com)
   con tu cuenta de Google.
2. En el selector de proyectos (arriba, junto al logo) → **Proyecto
   nuevo** → nómbralo, por ejemplo `agente-planificacion-personal`. No
   necesita facturación habilitada; el uso personal de la Calendar API es
   gratis dentro de sus cuotas normales.
3. **Si tu cuenta pertenece a una organización de Google Workspace** (p.
   ej. un correo `@utec.edu.pe`), el formulario pide un **Recurso
   superior** (dónde cuelga el proyecto en la jerarquía: la organización o
   una carpeta dentro de ella). Click en **Explorar** y selecciona la
   organización (p. ej. `utec.edu.pe`). Si la organización restringe a los
   estudiantes crear proyectos propios y da error de permisos, la
   alternativa más simple es repetir este paso con una cuenta de **Gmail
   personal** — ahí no hay organización de por medio y el campo "Recurso
   superior" ni siquiera aparece.

## Paso 2 — Habilitar la Google Calendar API

1. Menú **APIs & Services → Library**.
2. Busca "Google Calendar API" y ábrela.
3. Click en **Enable**.

## Paso 3 — Configurar la pantalla de consentimiento OAuth (Google Auth Platform)

Google renombró esta sección: ya no es un menú "OAuth consent screen" con
campos sueltos, sino un asistente llamado **Google Auth Platform**.

1. Menú **APIs & Services → Google Auth Platform → Descripción general**.
2. Click en **Comenzar**. El asistente pide, en orden:
   - **Información de la app**: nombre (p. ej. "Agente Planificación
     Personal") y correo de soporte.
   - **Público (Audience)**: aquí se elige el equivalente al antiguo
     "External" → selecciona **Externo**. Si tu cuenta es de una
     organización Workspace (p. ej. `utec.edu.pe`), es posible que solo
     ofrezca **Interno** — en ese caso no hace falta agregar test users:
     cualquier cuenta de la organización puede autorizar la app
     directamente, así que puedes saltar el punto 4 de abajo.
   - **Información de contacto**: tu correo de desarrollador.
   - Acepta las políticas y **Finalizar**.
3. En **Scopes**, no hace falta agregar nada manualmente (el código ya
   pide exactamente `calendar.events` en tiempo de ejecución).
4. Si tu app quedó como **Externo**, ve a la sección **Público** en el
   menú lateral de Google Auth Platform y agrega tu propia cuenta de
   Gmail en **Test users**. Esto es obligatorio: mientras la app esté en
   modo *Testing* (no publicada ni verificada por Google), solo las
   cuentas listadas como *test users* pueden autorizarla — que es
   exactamente tu caso de uso personal.

## Paso 4 — Crear las credenciales OAuth

1. Menú **APIs & Services → Credentials**.
2. **Create Credentials → OAuth client ID**.
3. Tipo de aplicación: **Desktop app**.
4. Nombre: lo que quieras (p. ej. "Agente Planificación - Desktop").
5. Click **Create** y luego **Download JSON**.

## Paso 5 — Colocar el archivo de credenciales

Renombra el archivo descargado a `credentials.json` y colócalo directo en
esta carpeta:

```
Tarea_Agente_Personal_v2_ActividadesDiarias/
  credentials.json   <- aquí
  agente_planificacion_actividades.py
  ...
```

`credentials.json` y `token.json` ya están excluidos en
[`.gitignore`](../.gitignore) de esta sesión — nunca se suben al repositorio.

## Paso 6 — Primera ejecución (requiere tu login en el navegador)

```bash
python agente_planificacion_actividades.py
```

Pídele al agente algo que dispare `consultar_calendario`, por ejemplo:

```
Tu: revisa mi calendario de hoy
```

La **primera vez**, esto abre una pestaña del navegador pidiéndote iniciar
sesión con la cuenta de Google que agregaste como *test user* y aceptar el
permiso de solo lectura. Al aceptar, se genera automáticamente
`token.json` en esta carpeta — las siguientes ejecuciones ya no piden
login de nuevo.

## Notas

- **Solo puede crear, nunca editar ni borrar.** El scope pedido es
  `https://www.googleapis.com/auth/calendar.events` (leer y crear/editar/
  borrar eventos, sin acceso a la lista de calendarios ni su
  configuración). El agente solo usa `agendar_actividad` para *crear* un
  evento nuevo — el system prompt le prohíbe explícitamente ofrecer editar
  o borrar uno existente, aunque el permiso técnico de la API lo
  permitiría.
- **Si ya tenías `token.json` generado antes (con el scope de solo
  lectura), bórralo y vuelve a correr `autenticar_calendario.py`** (o la
  primera ejecución del agente): el scope cambió, así que Google exige un
  nuevo consentimiento del usuario.
- **App en modo *Testing*:** el token de acceso puede expirar cada 7 días
  mientras la app no esté verificada por Google (no hace falta verificarla
  para uso personal). Si el agente deja de poder leer o agendar en el
  calendario, borra `token.json` y vuelve a correr el script para
  autenticarte de nuevo.
- **Eventos de todo el día:** un evento sin hora puntual (p. ej. un
  cumpleaños o un recordatorio de "todo el día") aparece listado en
  `consultar_calendario`, pero `generar_plan` no lo trata como un bloque
  horario ocupado — solo bloquea horarios los eventos con hora de inicio y
  fin específicas.
