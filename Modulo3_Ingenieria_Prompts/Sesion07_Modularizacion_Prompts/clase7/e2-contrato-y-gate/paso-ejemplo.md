# Input · el paso a contratar (el verificador bilingüe)

Trabajamos sobre el **paso de verificación** del pipeline de la clase
(`resumen → traducción → verificación`). Es el paso crítico: compara el **resumen original** con su
**traducción** y decide si la traducción es fiel. Su salida alimenta el **gate** que decide si el
pipeline continúa, se rehace, o escala a un humano.

Pega esta descripción donde lo indique `prompt-plantilla.md`.

---

> **Paso a contratar — Verificación bilingüe**
>
> - **Recibe (entrada):** dos textos — el RESUMEN ORIGINAL (en el idioma de partida) y su TRADUCCIÓN
>   (en el idioma objetivo).
> - **Hace:** compara ambos y determina si la traducción **conserva el significado y la información**
>   del original (sin omitir datos, sin cambiar el sentido).
> - **Debe entregar:** un veredicto **verificable y parseable** (no un párrafo de opinión) que un
>   programa —o el docente copiando y pegando— pueda evaluar con una regla binaria para decidir el
>   siguiente movimiento del pipeline.
>
> Restricciones del dominio:
> - Si la traducción **omite información** del resumen, debe listarse qué se omitió.
> - Si la traducción **cambia el sentido** de algo, debe listarse qué cambió.
> - El pipeline permite **hasta 2 reintentos** automáticos (`max_retries: 2`) antes de escalar a un
>   humano.

---

## Tu tarea
Escribe el **contrato de I/O** de la salida de este paso (el **JSON** con sus claves y tipos) y la
**regla del gate** que se evalúa sobre ese JSON: cuándo `approve`, cuándo `revise`, cuándo
`escalate`. Apóyate en `esquema.json` como punto de partida.
