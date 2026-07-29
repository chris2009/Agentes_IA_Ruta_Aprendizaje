# Instrucciones · e7 ESTRELLA — Evaluar modelos con rúbrica (flujo no-code)

> **Objetivo:** tomar **un mismo problema** (`problema.md`), generar las salidas **directa**
> (`prompt-directo.md`) vs **CoT** (`prompt-cot.md`) en **2–3 modelos**, y compararlas con la
> **rúbrica de 4 ejes** (`rubrica-comparacion.md`) para declarar un ganador **por tarea**. Todo
> **sin programar**. Al final hay un Colab opcional para quien quiera automatizarlo.

Elige **una** de las tres herramientas (puedes usar dos para contrastar). Todas son gratuitas con
una cuenta. El uso de API en Anthropic Console puede requerir crédito.

---

## Opción 1 — Google AI Studio · Compare Mode  ·  https://aistudio.google.com

El mismo prompt a distintos modelos/parámetros, lado a lado.

1. Entra a **aistudio.google.com** e inicia sesión con tu cuenta de Google.
2. Abre un prompt nuevo y, arriba a la derecha, pulsa el botón **"Compare"**.
3. Se abren dos paneles. En el selector de cada panel elige **el modelo Gemini disponible** (puedes
   poner distintas versiones/variantes para compararlas).
4. En el panel de parámetros ajusta la **temperatura** (déjala baja, ~0.2, para que el resultado sea
   estable mientras evalúas; súbela solo si quieres ver variabilidad).
5. **Pasada 1 — condición directa:** pega el prompt de `prompt-directo.md` con el problema dentro.
   Ejecuta y mira las dos salidas lado a lado.
6. **Pasada 2 — condición CoT:** borra y pega el prompt de `prompt-cot.md`. Ejecuta.
7. Para cada salida, anota en `plantilla-resultados.md` el total y los 4 ejes de la rúbrica.

---

## Opción 2 — LMArena  ·  https://lmarena.ai

Ideal para la **dinámica de clase** (votación a ciegas) y para comparación dirigida.

- **Battle Mode (a ciegas — para la dinámica):** escribes el prompt y respondes **dos modelos
  anónimos**; **votas** cuál respondió mejor y **recién entonces se revelan** sus nombres. Úsalo en
  clase con el prompt CoT del carrito: que la sala vote y luego descubra qué modelo ganó (quita el
  sesgo de marca).
- **Side-by-Side Mode (dirigido):** **tú eliges** los dos modelos a comparar. Úsalo para correr el
  mismo problema en directo vs CoT con modelos concretos y llenar la tabla de la rúbrica.

Flujo: corre el problema con `prompt-directo.md`, luego con `prompt-cot.md`; anota total + 4 ejes
por salida en `plantilla-resultados.md`.

---

## Opción 3 — Anthropic Console · Workbench + pestaña "Evaluate"  ·  https://console.anthropic.com

La más cercana a una evaluación formal con casos de prueba y calificación.

1. Entra a **console.anthropic.com** e inicia sesión (gratis con cuenta; usar la API puede requerir
   crédito).
2. Abre el **Workbench** (editor de prompts) y escribe el prompt usando una **variable** con la
   sintaxis `{{problema}}` donde iría el enunciado. Ejemplo de prompt:
   `Resuelve el problema. Pensemos paso a paso... {{problema}}` (versión CoT) y otro con la versión
   directa.
3. Ve a la pestaña **"Evaluate"**. Ahí puedes **generar casos de prueba** y **agregar** el valor de
   la variable `{{problema}}` (pega el enunciado de `problema.md`).
4. Usa **"comparar salidas lado a lado"** para enfrentar la versión directa contra la CoT (y/o
   distintos ajustes), y **califica cada salida en la escala de 5 puntos** que ofrece la pestaña.
5. Mapea esa calificación de 5 puntos a la rúbrica de 4 ejes y vacíala en `plantilla-resultados.md`.

> Nota: Console/Workbench compara variantes de prompt y parámetros sobre los modelos de Anthropic.
> Para comparar **entre proveedores distintos** (p. ej. Gemini vs otro), usa AI Studio o LMArena, o
> el Colab opcional.

---

## Alternativas rápidas (mención)
- **OpenAI Playground** (`platform.openai.com/playground`): editor con varios modelos y control de
  parámetros.
- **Poe** (`poe.com`) y **OpenRouter** (`openrouter.ai`): varios modelos de distintos proveedores en
  una sola interfaz, útiles para tener 2–3 modelos a mano sin abrir varias cuentas.

---

## Colab opcional (para automatizar)
`comparar_modelos.ipynb` (en esta misma carpeta) llama por API a 2–3 modelos (uno por proveedor) en
las dos condiciones y arma la tabla automáticamente. **No es necesario** para aprobar el ejercicio:
el camino principal es no-code. Ábrelo en **Google Colab** y sigue las celdas de arriba hacia abajo.

## Cierre del ejercicio
Con la tabla llena, completa la sección **Veredicto** de `plantilla-resultados.md`: qué celdas
acertaron, si CoT mejoró la corrección, y el ganador **por esta tarea** justificado por
**corrección + coste** (no por tamaño del modelo).
