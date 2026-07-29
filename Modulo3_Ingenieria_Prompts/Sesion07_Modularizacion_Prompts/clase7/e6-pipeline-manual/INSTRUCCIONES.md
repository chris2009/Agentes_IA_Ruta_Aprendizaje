# Instrucciones · e6 ESTRELLA — Pipeline manual: resumen → traducción → verificación con gate

> **Objetivo:** construir el pipeline de la clase **encadenándolo a mano** en cualquier chat
> (ChatGPT / Claude / Gemini), **sin escribir una línea de código**. Correr el paso 1, **copiar su
> salida y pegarla como entrada del paso 2**, y así, es **ya** prompt chaining (Anthropic 2024). El
> "camino de código predefinido" eres tú copiando y pegando en orden. Al final hay un **Colab opcional**
> (`pipeline_langchain.ipynb`) que automatiza lo mismo, pero **no es necesario para aprobar**.

## Lo que necesitas
- Un chat de IA (ChatGPT, Claude o Gemini). Idealmente, **chats/ventanas separadas** por paso para que
  no se contaminen entre sí.
- Los 4 archivos de esta carpeta: `texto-fuente.md`, `paso1-resumen.md`, `paso2-traduccion.md`,
  `paso3-verificacion.md`.
- Una hoja para registrar el resultado del gate de cada corrida (ver Paso E).

---

## El flujo, paso a paso

### Paso A — Resumen (Paso 1)
1. Abre `paso1-resumen.md` y copia el prompt.
2. Pega **dentro** de los delimitadores `<<<...>>>` el contenido de `texto-fuente.md`.
3. Ejecútalo. **Copia la salida (el resumen)** y guárdala. *Esta salida es la entrada del Paso 2.*

### Paso B — Traducción (Paso 2)
1. Abre `paso2-traduccion.md` y copia el prompt.
2. Pega **dentro** de `<<<...>>>` la **salida del Paso 1** (el resumen) — **no** el texto original.
3. Ejecútalo. **Copia la traducción** y guárdala junto con el resumen.

### Paso C — Verificación / gate (Paso 3)
1. Abre `paso3-verificacion.md` y copia el prompt.
2. Pega el **resumen del Paso 1** en el primer `<<<...>>>` y la **traducción del Paso 2** en el segundo.
3. Ejecútalo. La salida debe ser un **JSON parseable** con `faithful`, `missing_info`,
   `changes_of_meaning`, `action`.

### Paso D — Aplica la regla del gate
Lee el campo `action` del JSON y actúa:

```
if action == "approve":
    -> El pipeline TERMINA OK. La traducción está aprobada.

if action == "revise"  and  retries < max_retries (= 2):
    -> Vuelve al Paso B (traducción) y REHAZLO, agregando al prompt una instrucción que corrija lo
       que el verificador señaló. Por ejemplo:
       "Rehaz la traducción corrigiendo esto: <pega aquí missing_info y changes_of_meaning>."
    -> Suma 1 a retries y vuelve al Paso C (verificar de nuevo).

if action == "revise"  and  retries >= max_retries (= 2):
    -> ESCALATE: marca el caso para un revisor humano. El pipeline NO se aprueba solo.
```

> **Nota sobre `retries`:** al hacerlo a mano, **tú** llevas la cuenta (0, 1, 2). El paso 3 devuelve
> `action: approve|revise`; la decisión de `escalate` la tomas tú según cuántas veces ya reintentaste.

### Paso E — Registra el resultado (observabilidad)
Anota, para cada corrida, qué disparó el gate. Con ≥ 3 textos distintos, calcula el **revise rate del
paso de traducción** = (corridas que necesitaron al menos un `revise`) / (total de corridas).

| # | Texto | ¿faithful? | action | reintentos | resultado final |
|---|-------|-----------|--------|-----------|-----------------|
| 1 | (este) | | | | approve / escalate |
| 2 | | | | | |
| 3 | | | | | |

> **Revise rate del paso de traducción = ___ / ___.** Nombra el paso más débil (normalmente la
> traducción es el cuello de botella, no el resumen).

---

## Cómo forzar un `revise` en clase (para verlo funcionar)
Si todas las corridas salen `approve`, el gate "no se ve". Para provocar un `revise` controlado:
- En el Paso B, pídele a propósito una traducción que **omita un dato** (p. ej.: "traduce pero NO
  menciones las cuatro ventajas"). El verificador del Paso 3 debería marcar `faithful: false` y listar
  la omisión en `missing_info` → `action: "revise"`. Luego rehaces el Paso B bien y vuelves a verificar.

Es la forma más clara de mostrar las cuatro ventajas del chaining en vivo: **formato estable entre
pasos**, **error detenido por el gate**, **depuración localizada** (sabes que falló la traducción, no
el resumen) y **el punto exacto del HITL** (cuando se agotan los reintentos).

---

## Vía "pro" (opcional, fuera de clase) — Colab con LangChain
`pipeline_langchain.ipynb` (en esta misma carpeta) reproduce **el mismo pipeline** en código: cada
paso es una *chain* de LangChain y el gate es una función de Python que parsea el JSON y reintenta. Es
para quien quiera **automatizar y medir** las métricas a escala. **No es necesario** para aprobar el
ejercicio: el camino principal es el encadenamiento manual de arriba. Ábrelo en **Google Colab** y
sigue las celdas de arriba hacia abajo.

## Cierre del ejercicio
Reporta: el resumen, la traducción final aprobada, el JSON del verificador, y la tabla del Paso E con
el revise rate del paso de traducción. Evalúa con `rubrica.md`.
