# Prompt-plantilla · e4 — Convertir tareas vagas en contratos

> No le pides al modelo que HAGA las tareas: le pides que las REESCRIBA como contratos.
> Pega esta plantilla en ChatGPT/Claude/Gemini tal cual.

```
Eres un instructor de ingeniería de prompts. Para CADA tarea vaga entre <tareas></tareas>,
reescríbela como un CONTRATO de exactamente 3 partes:

  - Objetivo: qué se quiere lograr, empezando con un VERBO DE ACCIÓN, sin ambigüedad.
  - Restricciones e input: qué datos entran, qué está prohibido, y la POLÍTICA ANTE DATOS
    FALTANTES (qué hacer si algo no está).
  - Formato de salida verificable: una estructura (JSON, tabla o lista con campos fijos)
    cuyo cumplimiento se pueda chequear sin opinar.

Devuelve el resultado como una lista numerada (una entrada por tarea), y dentro de cada una
las tres partes etiquetadas. No resuelvas las tareas; solo escribe los contratos.

<tareas>
1. "Resume estas reseñas de clientes."
2. "Hazme unos correos para reactivar usuarios que dejaron de comprar."
3. "Sácame los datos importantes de este contrato laboral."
</tareas>
```
