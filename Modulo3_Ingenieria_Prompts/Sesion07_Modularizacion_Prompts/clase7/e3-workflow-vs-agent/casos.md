# Input · 4 casos para clasificar (Workflow vs Agent)

La diferencia esencial **no es la tecnología**, es **quién dirige el control de flujo** (Anthropic
2024): en un **workflow** la secuencia la fija un **camino de código predefinido** (el desarrollador);
en un **agent** el **LLM dirige dinámicamente** qué hacer a continuación, qué herramienta usar y
cuándo terminar. La pregunta de clasificación es una sola: **¿hay una secuencia fija de pasos (código)
o el LLM decide el orden en tiempo de ejecución?**

Clasifica cada uno de estos 4 casos como **Workflow** o **Agent** y justifica en ≤ 2 líneas. Pega
estos casos donde lo indique `prompt-plantilla.md`.

---

**Caso A — Soporte (pipeline de respuesta).**
"Recibe el correo del cliente y procésalo SIEMPRE en este orden: clasificar → traducir si no está en
español → redactar respuesta → verificar política. Cada salida se audita antes de pasar a la
siguiente."

**Caso B — Ventas (cotización estándar).**
"Toma los datos del formulario (producto, cantidad, país) y genera la cotización: aplica la tabla de
precios, calcula impuestos según el país, suma el envío y arma el PDF. Mismos pasos, mismo orden,
cada vez."

**Caso C — Operaciones (incidente raro).**
"Llega una alerta de un sistema que falló de forma inusual. El asistente debe **investigar**: leer
logs, consultar la base de configuración, buscar incidentes similares en el histórico y, según lo que
vaya encontrando, decidir qué revisar después, hasta proponer una causa raíz. No se sabe de antemano
cuántos pasos ni en qué orden."

**Caso D — Investigación de proveedores (due diligence abierta).**
"Investiga a este proveedor: búscalo en la web, en la base interna y en documentos cargados, y dame
un veredicto de riesgo. Puede que baste con la web, o que haga falta cruzar tres fuentes; depende de
lo que aparezca. El asistente decide qué fuente consultar y cuándo dar por cerrada la investigación."

---

## Tu tarea
Para cada caso: marca **Workflow** o **Agent** y justifica en ≤ 2 líneas, apoyándote en **"¿secuencia
fija de código o el LLM decide el orden?"** — no en preferencia ni en qué suena más moderno.
