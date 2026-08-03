# Configurar Google Calendar (solo lectura) para el agente v2

Guía paso a paso para que
[agente_planificacion_actividades.py](agente_planificacion_actividades.py)
pueda leer tu **Google Calendar** real (reuniones, cursos, citas) y
planificar alrededor de esos bloques ocupados. El agente **nunca** crea,
modifica ni borra eventos: solo pide permiso de lectura
(`calendar.readonly`).

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
2. En el selector de proyectos (arriba, junto al logo), crea un proyecto
   nuevo — por ejemplo `agente-planificacion-personal`. No necesita
   facturación habilitada; el uso personal de la Calendar API es gratis
   dentro de sus cuotas normales.

## Paso 2 — Habilitar la Google Calendar API

1. Menú **APIs & Services → Library**.
2. Busca "Google Calendar API" y ábrela.
3. Click en **Enable**.

## Paso 3 — Configurar la pantalla de consentimiento OAuth

1. Menú **APIs & Services → OAuth consent screen**.
2. Tipo de usuario: **External** (uso personal, no es una cuenta de Google
   Workspace de una organización).
3. Completa nombre de la app (p. ej. "Agente Planificación Personal"),
   correo de soporte y correo de contacto del desarrollador — puedes usar
   tu propio correo en ambos.
4. En **Scopes**, no hace falta agregar nada manualmente aquí (el código
   ya pide exactamente `calendar.readonly` en tiempo de ejecución).
5. En **Test users**, agrega tu propia cuenta de Gmail. Esto es
   obligatorio: mientras la app esté en modo *Testing* (no publicada ni
   verificada por Google), solo las cuentas listadas como *test users*
   pueden autorizarla — que es exactamente tu caso de uso personal.

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

- **Solo lectura, siempre.** El scope pedido es
  `https://www.googleapis.com/auth/calendar.readonly`; con ese permiso es
  técnicamente imposible que el agente cree, edite o borre un evento,
  aunque el modelo lo intentara.
- **App en modo *Testing*:** el token de acceso puede expirar cada 7 días
  mientras la app no esté verificada por Google (no hace falta verificarla
  para uso personal). Si el agente deja de poder leer el calendario,
  borra `token.json` y vuelve a correr el script para autenticarte de nuevo.
- **Eventos de todo el día:** un evento sin hora puntual (p. ej. un
  cumpleaños o un recordatorio de "todo el día") aparece listado en
  `consultar_calendario`, pero `generar_plan` no lo trata como un bloque
  horario ocupado — solo bloquea horarios los eventos con hora de inicio y
  fin específicas.
