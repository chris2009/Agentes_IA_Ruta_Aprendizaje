# Prompt-plantilla · e5 — Human-in-the-loop (trigger + checkpoint + métrica)

> El objetivo es diseñar el escape humano de un paso crítico: **automatizar lo común, escalar lo
> raro/riesgoso.** Eliges un punto del escenario y defines **1 trigger** (umbral de fallo o alto
> riesgo), **dónde** va el checkpoint y **qué métrica** te diría si está bien calibrado. Pega
> `escenario.md` donde dice `<<<...>>>`. Puedes resolverlo a mano o con esta plantilla en un chat.

---

```
Eres un diseñador de sistemas con LLMs que aplica la guía de OpenAI "Plan for human intervention".
Te doy un escenario con dos puntos posibles. Elige UNO y diseña su Human-in-the-Loop.

Recuerda: hay solo DOS tipos de trigger (umbral de fallo / acción de alto riesgo); el checkpoint va
en pre-check (entrada), gate intermedio (tras un paso), o post-check (antes de ejecutar/publicar); y
la calibración se mide con una de estas métricas: format pass rate, revise rate, escalate rate, MTTR.

Escenario:
<<<
{pega aquí el contenido de escenario.md}
>>>

Devuelve EXACTAMENTE este formato, sin texto extra:

PUNTO ELEGIDO: <Verificación de política | Autorizar reembolso>

1. TRIGGER
   - Tipo: <umbral de fallo | acción de alto riesgo>
   - Condición concreta: <p. ej. "retries >= max_retries (2)" o "monto del reembolso > S/ 200">

2. CHECKPOINT
   - Ubicación: <pre-check | gate intermedio | post-check>
   - Por qué ahí: <1 línea>

3. MÉTRICA DE CALIBRACIÓN
   - Métrica: <format pass rate | revise rate | escalate rate | MTTR>
   - Qué me diría: <1 línea — p. ej. "escalate rate muy alto = gate mal calibrado o dominio difícil">
```

---

**Entregable del alumno:** el trigger (de uno de los dos tipos), la ubicación del checkpoint con su
razón, y la métrica de calibración con su lectura. El humano es **feature, no falla**: es la tercera
acción del gate (`escalate`).
