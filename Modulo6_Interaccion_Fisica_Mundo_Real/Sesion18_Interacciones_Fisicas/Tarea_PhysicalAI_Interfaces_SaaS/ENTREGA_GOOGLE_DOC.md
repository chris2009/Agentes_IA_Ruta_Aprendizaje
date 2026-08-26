# Agente de Clima por Voz

**Tarea Sesión 18 (Interfaces Físicas) — Programa Diseño e Implementación de Agentes IA, UTEC Posgrado.**
Tipo: grupal. Fecha límite: 12/11.

## OBJETIVO

La consigna pedía probar *Physical Agent Interfaces* con cualquier SaaS que estuviera considerando para el proyecto del equipo, y contar qué encontré. No tengo cámara Tapo ni parlante aparte para montar nada físico, así que en vez de forzar algo que no puedo armar, usé lo que sí tengo a mano: el micrófono y el parlante de mi laptop. Al final esa ya es una interfaz física de verdad, solo que no es la que estamos usando en el proyecto de los gatos.

Elegí ElevenLabs porque es el SaaS que nombra el material de la sesión, junto con Twilio, y porque quería ver qué tan lejos se puede llegar sin escribir una línea de código de backend.

## DESCRIPCION DEL AGENTE

Al entrar a ElevenLabs te hace elegir entre dos plataformas: ElevenCreative (TTS, doblaje, efectos sueltos) y ElevenAgents (agentes conversacionales completos). Fui por ElevenAgents porque arma solo el pipeline de voz→LLM→voz de punta a punta, que es justo el patrón de "Speech Agent" del que habla la sesión.

Armé el agente en blanco, sin plantilla, para escribir yo mismo el system prompt en vez de heredar el de "Asistente personal" o "Agente de negocios". Le puse esto:

```
Eres un asistente de voz breve y directo. Respondes en español,
en oraciones cortas (una o dos frases), sin emojis ni markdown,
porque tu respuesta se convierte a audio. Si el usuario pregunta
por el clima de una ciudad, usa la herramienta get_clima.
```

Lo de "sin emojis ni markdown" no fue capricho: si el LLM devuelve texto con formato, el TTS lo lee literal, y quería evitar que la voz dijera "asterisco asterisco" o algo así. Además le agregué una tool, `get_clima`, que recibe una ciudad y devuelve el clima — simulada, sin conectarla a ningún servicio real de clima.

| Campo | Valor |
|---|---|
| Nombre | `Agente-Prueba-Sesion18` |
| Idioma | Español |
| Voz | Gaby — Natura & Casual (femenina, español latinoamericano) |
| LLM | Gemini 2.5 Flash (quedó en el valor por defecto) |
| Tool | `get_clima`, parámetro `ciudad` |

Por defecto el agente venía en inglés, con una voz llamada Eric — hay que cambiar el idioma y la voz a mano, no vienen en español de entrada.

![Agente configurado: prompt en español + voz Gaby](screenshots/07_agente_configurado.png)
*Figura 1. Panel de configuración del agente en ElevenLabs, con el system prompt en español y la voz Gaby ya seleccionada.*

## PROCESO

Crear la tool fue sencillo, aunque me trabé un momento con un campo de "Descripción" que el formulario marcaba como obligatorio — pensé que era la descripción de la tool en general, pero era la del parámetro `ciudad`, para que el modelo sepa cómo reconocer una ciudad dentro de lo que diga el usuario.

La primera llamada de prueba falló. Le pregunté por el clima de Lima y el agente respondió "No pude obtener el clima de Lima", sin más. Fui a revisar el panel de "Herramientas de prueba" y encontré el motivo: tenía activado "Simular todas las herramientas" pero sin ninguna respuesta simulada cargada para `get_clima`, y la estrategia de respaldo estaba puesta en "Finalizar con error" — cualquier tool sin un mock definido termina ahí, sin más aviso.

![La estrategia de respaldo "Finalizar con error" causó el primer fallo](screenshots/12_estrategia_respaldo.png)
*Figura 2. Estrategia de respaldo en "Finalizar con error" — la causa del primer intento fallido con la tool `get_clima`, sin ninguna respuesta simulada configurada todavía.*

Pensé que para arreglar esto iba a necesitar un webhook real corriendo en algún lado, pero no — hay un botón "Configurar" al lado de esa opción que te deja elegir la tool y escribirle una respuesta simulada directo ahí, en JSON:

```json
{"temperatura": "18°C", "condicion": "nublado"}
```

Con eso puesto, volví a llamar al agente, esta vez por voz de verdad, con el micrófono del navegador:

> Yo: "Hola, ¿cómo estás? ¿Cuál es el clima en Lima?"
> Agente: "El clima en Lima es nublado con una temperatura de dieciocho grados Celsius."
> Yo: "Muchas gracias. Hasta luego."
> Agente: "De nada. ¡Hasta luego!"

![Prueba exitosa: llamada de voz con el tool call resuelto](screenshots/13_prueba_exitosa_llamada.png)
*Figura 3. Transcripción de la llamada de voz real, ya con la respuesta simulada de `get_clima` funcionando y verbalizada por el agente.*

Funcionó bien: reconoció la ciudad dentro de la pregunta, llamó a la tool, y convirtió el JSON en una respuesta hablada natural, no leyó el JSON en voz alta ni nada raro. La conversación se sintió fluida, sin esas pausas incómodas que uno espera de un demo. La voz de Gaby no sonó robótica en ningún momento de la transcripción.

Lo que más me quedó de esta prueba es que no hacía falta tener nada de infraestructura propia corriendo para probar tool calling completo — todo el mock se hace desde el mismo dashboard. Eso contrasta bastante con el laboratorio de la sesión, que arma el mismo tipo de pipeline (STT→LLM→TTS) a mano con `fastrtc`, `moonshine` y `kokoro`, todo local. Ahí ganas en control y en costo (una vez armado, corre gratis), pero te toca resolver tú mismo cosas que en ElevenLabs vienen resueltas, como el streaming de audio o la detección de cuándo el usuario dejó de hablar. Para una prueba rápida como esta, el SaaS gana por lejos; si en algún momento esto se volviera algo que el equipo corre en producción y con volumen, ahí empezaría a pesar más el costo por uso.

No llegué a conectar nada de esto con el proyecto real de los gatos — sin cámara no tenía cómo, y tampoco era el punto de esta prueba. Si en algún momento el equipo quisiera agregar una interfaz de voz (para preguntar el estado de algo hablando, por ejemplo), esto ya deja demostrado que se puede armar y probar un flujo completo, con tool calling incluido, en una sola sesión de trabajo y sin backend propio.

## Declaración de transparencia de IA

Usé Claude Code como guía durante todo el proceso: me explicó las arquitecturas de voz que menciona el material de la sesión, me fue diciendo qué botón tocar en cada pantalla a medida que le mandaba capturas, y me ayudó a entender por qué falló el primer intento con la tool. La cuenta, la configuración del agente, la llamada de voz real y el arreglo del error los hice yo, pantalla por pantalla. Este documento lo redactó Claude Code a partir de esa sesión de trabajo real, no de una lista de pasos genérica.
