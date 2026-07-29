# Ideas de Proyecto Final — Agent Profile Cards

> Basado en el framework del lab: Agent Profile Card → System Prompt.
> Cada idea cubre las dimensiones: Context Definition, Environment Definition, Autonomy Dimension y Criticality Dimension.

---

## Idea 1 — Agente de Triaje de Soporte al Cliente

### Communication Layer
**No Conversacional** — procesa tickets entrantes de forma automática en batch o en tiempo real.

---

### Context Definition

#### Domain Definition

| Campo | Descripción |
|---|---|
| **Domain** | Soporte técnico de primer nivel para una empresa de software o SaaS |
| **Alcance** | Tickets recibidos vía sistema de ticketing desde la recepción hasta la resolución o escalamiento al agente humano |
| **Restricción** | No puede acceder a sistemas de producción del cliente. No puede emitir reembolsos ni modificar contratos. No resuelve incidentes de nivel 2 o superior |

#### Objectives Definition

1. Recibir y leer tickets entrantes del sistema de soporte.
2. Clasificar cada ticket por tipo (bug, consulta, facturación, acceso) y nivel de urgencia (crítico, medio, bajo).
3. Resolver automáticamente los tickets de baja complejidad con respuesta desde la base de conocimiento.
4. Escalar los tickets complejos al agente humano correspondiente con un resumen ejecutivo y contexto del cliente.
5. Actualizar el estado del ticket en el sistema y notificar al cliente del avance.

---

### Environment Definition

#### Knowledge

- **MOF:** Catálogo de productos y versiones activas como documento principal de criterio de resolución.
- **Vectorial DB / Docs:**
  - Base de conocimiento interna: FAQs, guías de resolución paso a paso, errores conocidos.
  - Historial de tickets resueltos con sus soluciones para aprender patrones.
  - Políticas de SLA (tiempos máximos de respuesta por nivel de urgencia).
  - Perfiles de clientes: plan contratado, historial de incidencias previas.

#### Tools

- Conexión con sistema de ticketing (Zendesk, Jira Service Desk o similar) para leer, actualizar y cerrar tickets.
- Búsqueda semántica sobre la base de conocimiento para encontrar soluciones relevantes.
- Envío de respuesta al cliente por email o dentro del portal de soporte.
- Creación de ticket escalado con resumen automático para el agente humano.
- Consulta del perfil del cliente en el CRM para personalizar la respuesta.

#### Short Term Memory

Los datos del ticket activo que se está procesando en la sesión actual: descripción del problema, adjuntos, historial reciente del cliente en esta sesión.

#### Long Term Memory

- Patrones de tickets recurrentes por tipo de producto o versión.
- Preferencias de escalamiento del equipo de soporte (qué agente atiende qué tipo de incidente).
- Feedback del equipo sobre la calidad de las resoluciones automáticas para reentrenamiento.
- Soluciones que han funcionado para clientes con perfil similar.

---

### Autonomy Dimension Definition

**Semi-Autónomo / Constreñido**

El agente resuelve de forma completamente autónoma los tickets de baja complejidad (consultas de uso, reseteo de contraseñas, problemas conocidos con solución documentada). Para tickets de media o alta complejidad, su función es clasificar, resumir y derivar — no tomar la decisión de resolución. No puede improvisar soluciones fuera de la base de conocimiento aprobada.

---

### Criticality Dimension Definition

**Nivel de Criticidad: Medio**

Las respuestas incorrectas generan insatisfacción del cliente pero no tienen consecuencias financieras ni técnicas críticas directas. El escalamiento al humano actúa como red de seguridad para los casos complejos.

---
---

## Idea 2 — Agente de Análisis y Mejora de Propuestas Comerciales

### Communication Layer
**No Conversacional** — recibe documentos y devuelve análisis y versión mejorada.

---

### Context Definition

#### Domain Definition

| Campo | Descripción |
|---|---|
| **Domain** | Área comercial — análisis y mejora de propuestas B2B antes de su envío al cliente |
| **Alcance** | Propuestas en estado borrador entregadas por el equipo comercial dentro de la plataforma interna |
| **Restricción** | No puede enviar propuestas al cliente. No puede modificar precios ni condiciones comerciales sin aprobación humana. No puede acceder a información financiera confidencial fuera del documento recibido |

#### Objectives Definition

1. Leer y estructurar el contenido de la propuesta recibida (PDF o DOCX).
2. Comparar la propuesta contra los requisitos del cliente (RFP) y detectar gaps.
3. Evaluar la propuesta contra plantillas y propuestas ganadoras anteriores.
4. Identificar debilidades de redacción, argumentación o presentación.
5. Generar un reporte de análisis con hallazgos y recomendaciones específicas.
6. Producir una versión mejorada del documento con los cambios aplicados.

---

### Environment Definition

#### Knowledge

- **MOF:** El RFP (Request for Proposal) del cliente como documento principal que define los criterios de éxito.
- **Vectorial DB / Docs:**
  - Repositorio de propuestas ganadoras y perdidas con sus resultados registrados.
  - Guía de estilo corporativo y lineamientos de presentación.
  - Catálogo de servicios y productos con sus descripciones oficiales.
  - Perfiles de clientes anteriores con preferencias detectadas.

#### Tools

- Lectura y parseo de documentos PDF y DOCX.
- Búsqueda semántica sobre repositorio de propuestas anteriores para encontrar secciones similares exitosas.
- Búsqueda web para obtener contexto público del cliente (noticias recientes, tamaño, industria).
- Generación de documento Word con track changes o versión limpia mejorada.
- Envío del reporte de análisis y documento mejorado al equipo comercial por email o plataforma interna.

#### Short Term Memory

La propuesta activa y el RFP del cliente que se están procesando en la sesión actual.

#### Long Term Memory

- Historial de propuestas: qué argumentos funcionaron con qué tipo de cliente.
- Patrones de debilidades frecuentes detectadas en propuestas del equipo.
- Preferencias documentadas por industria o tamaño de cliente.
- Feedback del equipo comercial sobre la utilidad de las mejoras sugeridas.

---

### Autonomy Dimension Definition

**Semi-Autónomo / Constreñido**

El agente analiza y mejora de forma autónoma, pero la decisión de envío al cliente siempre requiere aprobación humana. No puede alterar cifras, fechas de entrega ni condiciones contractuales — solo puede mejorar redacción, estructura y argumentación dentro de los parámetros ya definidos por el equipo comercial.

---

### Criticality Dimension Definition

**Nivel de Criticidad: Alto**

Una propuesta mal mejorada puede resultar en la pérdida de un negocio o en compromisos incorrectos con el cliente. El agente siempre entrega una versión para revisión humana final antes de cualquier envío externo.

---
---

## Idea 3 — Agente de Monitoreo de Competencia y Precios

### Communication Layer
**No Conversacional** — corre en batch programado (diario o semanal), sin interacción directa con usuarios.

---

### Context Definition

#### Domain Definition

| Campo | Descripción |
|---|---|
| **Domain** | Inteligencia comercial — monitoreo de precios y actividad pública de competidores |
| **Alcance** | Competidores predefinidos en una lista de configuración; solo información públicamente disponible en sus sitios web y medios |
| **Restricción** | No puede modificar precios propios ni publicar información externamente. No puede acceder a sistemas internos de los competidores. No puede inferir datos confidenciales ni realizar ingeniería inversa de estrategias privadas |

#### Objectives Definition

1. Monitorear diariamente los precios publicados de los competidores en sus sitios oficiales.
2. Detectar cambios de precio superiores al umbral configurado y generar alertas inmediatas.
3. Recopilar noticias y comunicados públicos relevantes de los competidores (lanzamientos, alianzas, cambios).
4. Consolidar la información en un reporte ejecutivo con tendencias y variaciones históricas.
5. Distribuir el reporte al equipo comercial y de producto por email cada mañana.

---

### Environment Definition

#### Knowledge

- **MOF:** Lista maestra de competidores con sus URLs, productos a monitorear y umbrales de variación de precio que activan alerta.
- **Vectorial DB / Docs:**
  - Historial de precios por competidor y producto para análisis de tendencias.
  - Repositorio de noticias y comunicados recopilados en ejecuciones anteriores.
  - Posicionamiento propio de la empresa para contextualizar los hallazgos.

#### Tools

- Web scraping de páginas de precios de competidores (con rate limiting para no ser bloqueado).
- Búsqueda de noticias recientes por nombre de competidor (Google News API o similar).
- Comparación automática contra precios del día anterior para detectar cambios.
- Generación de reporte en formato PDF o HTML con gráficos de tendencias.
- Envío del reporte por email al equipo configurado.
- Alerta inmediata vía email o Slack cuando se detecta un cambio superior al umbral.

#### Short Term Memory

Resultados del scraping y búsqueda de noticias de la ejecución actual antes de consolidarlos.

#### Long Term Memory

- Serie histórica de precios por competidor y producto (para graficar tendencias).
- Registro de alertas enviadas anteriormente para evitar duplicados.
- Noticias ya procesadas en ejecuciones pasadas para no reportar lo mismo dos veces.

---

### Autonomy Dimension Definition

**Autónomo / Constreñido**

Opera completamente sin intervención humana en cada ejecución: accede, recopila, analiza y distribuye. Su autonomía está constreñida a la lista de competidores y criterios configurados previamente. No puede decidir monitorear nuevas fuentes por iniciativa propia ni puede actuar sobre los precios propios de la empresa.

---

### Criticality Dimension Definition

**Nivel de Criticidad: Medio**

El agente informa pero no actúa sobre precios. Un error en el reporte genera desinformación interna pero no tiene impacto externo directo. La información se presenta siempre como referencial para decisión humana.

---
---

## Idea 4 — Agente de Revisión de Cumplimiento Regulatorio

### Communication Layer
**No Conversacional** — audita documentos entregados a la plataforma y devuelve reporte estructurado.

---

### Context Definition

#### Domain Definition

| Campo | Descripción |
|---|---|
| **Domain** | Legal / compliance en industrias reguladas (financiera, salud, manufactura o alimentaria) |
| **Alcance** | Documentos enviados explícitamente a la plataforma de auditoría: contratos, políticas internas, manuales de proceso |
| **Restricción** | No puede emitir opiniones legales vinculantes. No puede aprobar ni rechazar contratos. No puede modificar documentos originales. No sustituye al área legal — su función es asistir y señalar, no dictaminar |

#### Objectives Definition

1. Leer y estructurar el documento enviado para auditoría.
2. Identificar las normativas aplicables según el tipo de documento y la industria configurada.
3. Verificar artículo por artículo el cumplimiento del documento contra la normativa vigente.
4. Generar un reporte de gaps con referencia exacta al artículo normativo incumplido y al fragmento del documento que lo viola.
5. Priorizar los hallazgos por nivel de riesgo (crítico, moderado, informativo).
6. Entregar el reporte al equipo legal para revisión y acción.

---

### Environment Definition

#### Knowledge

- **MOF:** El cuerpo normativo aplicable (ley, reglamento o estándar) como documento maestro de criterios de evaluación.
- **Vectorial DB / Docs:**
  - Base de datos vectorial de normativas regulatorias con sus artículos indexados.
  - Historial de auditorías anteriores con sus hallazgos para detectar patrones recurrentes.
  - Glosario legal y definiciones oficiales de términos regulatorios.
  - Plantillas de contratos aprobados previamente como referencia de cumplimiento.

#### Tools

- Lectura y parseo de documentos PDF, DOCX y contratos estructurados.
- Búsqueda semántica sobre base de normativas para encontrar artículos relevantes a cada cláusula.
- Clasificación de hallazgos por nivel de riesgo (crítico, moderado, informativo).
- Generación de reporte PDF con tabla de hallazgos, referencias normativas y fragmentos del documento auditado.
- Envío del reporte al equipo legal con resumen ejecutivo.

#### Short Term Memory

El documento siendo auditado en la sesión actual y los artículos normativos recuperados durante el análisis.

#### Long Term Memory

- Historial de auditorías por tipo de documento y sus hallazgos recurrentes.
- Actualizaciones normativas registradas para mantener la base de conocimiento vigente.
- Patrones de incumplimiento frecuentes por área o tipo de contrato.
- Feedback del equipo legal sobre la precisión de los hallazgos para mejorar la búsqueda semántica.

---

### Autonomy Dimension Definition

**Semi-Autónomo / Fuertemente Constreñido**

El agente analiza y reporta de forma completamente autónoma, pero su función termina en la entrega del reporte. Nunca modifica documentos, nunca emite un veredicto de aprobación o rechazo, y nunca actúa sobre los hallazgos. Toda decisión posterior es responsabilidad del equipo legal humano.

---

### Criticality Dimension Definition

**Nivel de Criticidad: Alto-Crítico (Controlado)**

Un hallazgo falso negativo (no detectar un incumplimiento real) puede tener consecuencias legales y regulatorias graves. Por eso el agente siempre prioriza reportar más antes que menos, y sus hallazgos siempre pasan por revisión humana antes de cualquier acción. El reporte es un insumo, no una decisión.

---
---

## Idea 5 — Agente de Onboarding de Nuevos Empleados

### Communication Layer
**Conversacional** — interactúa directamente con el nuevo empleado durante sus primeras semanas.

---

### Context Definition

#### Domain Definition

| Campo | Descripción |
|---|---|
| **Domain** | Recursos Humanos — gestión del conocimiento organizacional y acompañamiento de nuevos ingresos |
| **Alcance** | Empleados nuevos durante sus primeras 4 a 8 semanas desde la fecha de ingreso |
| **Restricción** | No puede modificar datos de nómina ni beneficios. No puede aprobar permisos, vacaciones ni gastos. No puede tomar decisiones sobre continuidad o desempeño del empleado. No comparte información de otros empleados |

#### Objectives Definition

1. Dar la bienvenida al nuevo empleado y presentarle el proceso de onboarding de forma personalizada según su rol y área.
2. Responder consultas sobre procesos internos, políticas, herramientas y cultura organizacional.
3. Asignar y hacer seguimiento a las tareas del checklist de onboarding (lecturas, cursos, reuniones obligatorias).
4. Agendar automáticamente las reuniones de inducción con los equipos correspondientes.
5. Monitorear el progreso del empleado y alertar a RRHH si alguna tarea crítica no se completa en el plazo.
6. Recopilar feedback del empleado sobre la experiencia de onboarding al final del proceso.

---

### Environment Definition

#### Knowledge

- **MOF:** El manual del empleado y la descripción del puesto como documentos principales que definen qué debe conocer y hacer el nuevo ingreso.
- **Vectorial DB / Docs:**
  - Manual del empleado y políticas internas (vacaciones, beneficios, código de conducta).
  - Organigrama y directorio de contactos por área.
  - FAQs frecuentes de empleados nuevos por rol y área.
  - Catálogo de cursos y recursos de inducción disponibles.
  - Checklist de onboarding personalizado por posición.

#### Tools

- Conexión con sistema RRHH para leer datos del nuevo empleado (rol, área, fecha de ingreso, líder asignado).
- Asignación de cursos y recursos en plataforma de e-learning interna.
- Integración con calendario (Google Calendar u Outlook) para agendar reuniones de inducción.
- Envío de recordatorios y notificaciones al empleado por email o plataforma interna.
- Registro del progreso del checklist de onboarding en el sistema RRHH.
- Alerta al área de RRHH cuando una tarea crítica no se completa en el plazo establecido.

#### Short Term Memory

La conversación activa con el empleado en la sesión actual: preguntas realizadas, contexto de lo que ya se explicó, tareas revisadas en esta sesión.

#### Long Term Memory

- Progreso acumulado del empleado: tareas completadas, pendientes y fechas.
- Historial de conversaciones para no repetir explicaciones ya dadas.
- Dudas frecuentes registradas por área para mejorar el material de onboarding.
- Feedback recopilado al final del proceso de empleados anteriores.

---

### Autonomy Dimension Definition

**Semi-Autónomo / Constreñido**

El agente responde consultas, asigna recursos y agenda reuniones de forma completamente autónoma. Para solicitudes fuera de su alcance (aprobación de gastos, cambios de rol, permisos especiales), deriva al contacto de RRHH correspondiente sin intentar resolver. No puede improvisar respuestas sobre temas no documentados — en ese caso, lo reconoce y escala.

---

### Criticality Dimension Definition

**Nivel de Criticidad: Medio**

Un error en la información entregada al empleado genera confusión y mala experiencia, pero no tiene consecuencias operativas o legales directas. Las decisiones sensibles (nómina, desempeño, continuidad) siempre quedan fuera del alcance del agente y en manos humanas.

---

## Resumen comparativo de las 5 ideas

| | Soporte al Cliente | Propuestas Comerciales | Monitoreo Competencia | Compliance | Onboarding |
|---|---|---|---|---|---|
| **Communication Layer** | No conversacional | No conversacional | No conversacional | No conversacional | Conversacional |
| **Autonomía** | Semi-autónomo | Semi-autónomo | Autónomo | Semi-autónomo | Semi-autónomo |
| **Criticidad** | Medio | Alto | Medio | Alto-Crítico | Medio |
| **Complejidad técnica** | Media | Media | Media-Baja | Alta | Media |
| **Impacto de negocio** | Alto | Alto | Medio | Muy alto | Medio |

> Ver también:
> - [`taxonomia_conversational_automation.md`](taxonomia_conversational_automation.md)
> - [`../Modulo1_Introduccion_Motivacion/Sesion01_Introduccion_Agentes/que_es_un_agente_ia.md`](../Modulo1_Introduccion_Motivacion/Sesion01_Introduccion_Agentes/que_es_un_agente_ia.md)
