# Ideas para la Tarea — Multimodal (personal, due 19/08)

> **Enunciado (diapositiva 48 de `SES17_M6_Multimodalidad.pdf`):** *"Pruebe con MLLMs una implementación personal por medio de un agente que realice un cambio de modalidad en la información."* Tipo: personal.

La jugada más eficiente es reusar el patrón ya verificado y funcionando en el material del curso — el **"Camino 1: LLM + Tools"** (orquestar modelos ya entrenados, sin *fine-tuning*), documentado en [`Sesion17_Multimodalidad_ANALISIS_COMPLETO.md`](Sesion17_Multimodalidad_ANALISIS_COMPLETO.md) §4 — en vez de inventar algo desde cero.

---

## 1. Foto de un recibo/boleta → gasto estructurado en JSON (imagen → texto estructurado)

**La más rápida.** Literalmente el mismo patrón que ya funcionó en `agents26_m6s17-main/singlemodel.ipynb` (cheque.jpg + GPT-4o-mini leyendo correctamente el monto, banco, fecha). Le tomas foto a un recibo real, el agente lo estructura como JSON de gasto (monto, categoría, fecha, comercio).

- **Por qué es aterrizable:** el código base ya está probado (base64 + `chat.completions` con `image_url`) — solo cambia el prompt de "cheque" a "recibo/gasto" y, opcionalmente, se guarda el JSON en un CSV/archivo.
- **Esfuerzo estimado:** ~30-45 min.
- **Utilidad real:** sirve para llevar un registro de gastos personal.

## 2. Nota de voz → resumen/tarea estructurada (audio → texto)

Grabas una nota de voz (igual que `entrevista.m4a` en el lab de la Sesión 17), el agente la transcribe con Whisper y la convierte en una lista de tareas o un resumen estructurado en Markdown. Mismo patrón que la tool `obtener_entrevista` en `agents26_m6s17-main/main.py`.

- **Esfuerzo estimado:** ~30-45 min, si ya está configurada `OPENAI_API_KEY`.

## 3. Texto (una idea/plan) → imagen ilustrativa (texto → imagen)

Igual que la tool `generar_croquis_accidente`, pero aplicado a algo propio: un plan de viaje, una receta, el layout de un mueble por armar. Se describe la escena y `gpt-image-1` genera la imagen.

- **Esfuerzo estimado:** ~20-30 min — la más simple de las tres, pero la menos "útil" en términos de vida diaria (más demo que herramienta).

## 4. Combinar dos pasos: nota de voz → resumen → imagen (audio → texto → imagen)

Esto es lo que realmente demuestra un **agente** (no solo una llamada a un modelo): usar `create_agent` de LangChain con 2 tools (`transcribir_audio`, `generar_imagen`), como hace `agents26_m6s17-main/main.py` pero recortado al caso propio. El LLM decide el orden y cuándo usar cada tool.

- **Esfuerzo estimado:** ~1h.
- **Por qué vale la pena:** el enunciado pide explícitamente *"por medio de un agente"*, no un script de una sola llamada.

---

## Recomendación

**Opción 4** (o, si el tiempo aprieta, opción 1 ó 2 solas como plan B) — porque el enunciado exige un *agente* que decida, no solo una transformación de modalidad de un solo paso, y el 90% del código ya existe como plantilla directa en `agents26_m6s17-main/main.py` (solo cambian las tools y el caso de uso).
