# Input · escenario para definir el Human-in-the-Loop

HITL es el mecanismo por el cual el sistema **transfiere el control a un humano** cuando no debe (o no
puede) decidir solo. Idea clave: **automatizar lo común, escalar lo raro/riesgoso.** El humano es una
**feature de diseño, no una falla** — es la tercera acción del gate (`escalate`). La guía OpenAI
("Plan for human intervention") define **dos triggers primarios**:

- **Umbral de fallo** (exceeding failure thresholds): si el sistema no resuelve tras N reintentos →
  escala. Conecta con `max_retries` del gate.
- **Acción de alto riesgo** (high-risk actions): acciones sensibles, irreversibles o de alto impacto
  (autorizar reembolsos grandes, cancelar pedidos, hacer pagos) → supervisión humana.

Y **métricas de calibración**: *format pass rate*, *revise rate*, *escalate rate*, *MTTR*.

Pega este escenario donde lo indique `prompt-plantilla.md`.

---

> **Escenario — el pipeline de soporte en producción (primera semana)**
>
> El pipeline `clasificar → traducir → redactar → verificar política` ya corre. Dos pasos preocupan al
> equipo:
>
> 1. **Verificación de política (gate).** A veces la respuesta no pasa el verificador y se rehace
>    (`revise`). Si tras 2 reintentos sigue sin pasar, alguien debería mirarlo en vez de seguir
>    reintentando para siempre.
>
> 2. **Autorizar un reembolso.** Algunas respuestas implican **autorizar un reembolso al cliente**.
>    Un reembolso de S/ 50 es rutina; uno de S/ 5,000 es dinero real, irreversible, que nadie quiere
>    que un modelo apruebe solo en la primera semana de producción.

---

## Tu tarea
Elige **uno** de los dos puntos. Define: **(1)** el trigger de HITL (¿umbral de fallo o acción de alto
riesgo?), **(2)** dónde se inserta el checkpoint (pre-check a la entrada / gate intermedio /
post-check antes de ejecutar-publicar), y **(3)** una métrica que diría si el HITL está bien calibrado
(format pass rate / revise rate / escalate rate / MTTR).
