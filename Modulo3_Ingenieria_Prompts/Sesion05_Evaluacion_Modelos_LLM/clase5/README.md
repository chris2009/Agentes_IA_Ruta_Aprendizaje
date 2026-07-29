# Clase 5 · Ejercicios — Ingeniería de prompts funcionales (v2)

Estos ejercicios bajan a la práctica los **dos principios de Ng & Fulford** y la metáfora del
**prompt como contrato verificable** de la Clase 5. Cada uno es **ejecutable tal cual** en
ChatGPT, Claude o Gemini: pegas el contenido de `prompt-plantilla.md` (sustituyendo el bloque de
input por el archivo indicado) y comparas la salida contra el `criterio.md`.

> El número `eN` sigue el **orden de dictado en el deck** (no una jerarquía conceptual).

| # | Carpeta | Principio / táctica | Qué entrena |
|---|---------|---------------------|-------------|
| e1 | `e1-delimitadores-json/` | P1 · delimitadores + salida estructurada | Construir UN prompt en 2 pasos: parte 1 demarcar (salida libre) → parte 2 agregar el contrato JSON |
| e2 | `e2-verificar-condiciones/` | P1 · verificar condiciones (anti-alucinación) | Detectar el caso vacío sin inventar |
| e3 | `e3-few-shot/` | P1 · few-shot | Clasificar con exactamente 2 ejemplos / 2 clases |
| e4 | `e4-contrato/` | Contrato I/O (síntesis del P1 · CRTO+ITE) | Reescribir 3 tareas vagas como contrato de 3 partes |
| e5 | `e5-pensar-paso-a-paso/` | P2 · resolver antes de concluir (CoT) | Juzgar una solución resolviendo primero |
| e6 | `e6-integrador-extraccion-legal/` | Todo · integrador | Contrato laboral → JSON exacto con rúbrica |

## Cómo trabajarlos
1. Abre la carpeta del ejercicio.
2. Lee el/los archivo(s) de **input** (`.md` / `.json`).
3. Copia `prompt-plantilla.md` (o `prompt-maestro.md` en e6) y pega dentro el input donde dice
   `{...}` o entre los delimitadores `<...></...>`.
   - **e1 va en 2 pasos:** primero `prompt-plantilla-1-delimitadores.md` (salida libre), y cuando
     funcione, el MISMO prompt + contrato JSON en `prompt-plantilla-2-json.md`.
4. Ejecútalo en el modelo de tu elección.
5. Evalúa la salida con `criterio.md` (o `rubrica.md`): **todo criterio es binario** — cumple o no.

## Regla de oro de la clase
> Si no puedes verificar tu salida, no tienes un contrato; tienes una apuesta.
