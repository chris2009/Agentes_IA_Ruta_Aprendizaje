# Aprendizaje Colaborativo Multi-Agente — Análisis completo de la Sesión 21 (Módulo 7)

> **Fuente base:** *"Aprendizaje colaborativo — Multi-agentes"* (`collective_learning.pdf`, 30 diapositivas) — Módulo 7 (Aprendizaje y Mejora), Programa en Diseño e Implementación de Agentes IA, UTEC Posgrado. Dictada por **Dr. Vicente Machaca Arceda**, el mismo docente de las Sesiones 19 y 20.
> **Nota técnica 1:** el PDF está protegido con contraseña de propietario (igual que el de la Sesión 20) — se extrajo el texto completo con `pdftotext`, ya que la restricción es de permisos de edición, no de apertura.
> **Nota técnica 2:** a diferencia de las Sesiones 19 y 20, esta carpeta **no tiene notebook de laboratorio adjunto** — es una sesión puramente conceptual, sin práctica de código. Tampoco tiene una diapositiva de "Referencias" formal con citas académicas explícitas (autor, año, arXiv): el material nombra decenas de sistemas y métodos (LLM-Blender, AutoAct, AgentCF, AgentVerse, DyLAN, CAMEL, MapCoder, MACRec, SPP...) sin atribuirlos. La investigación complementaria de este documento (§9) identificó y verificó el origen de cada uno.
> **Hallazgo clave de esta sesión:** el "Marco Extensible de Cinco Dimensiones" que organiza toda la diapositiva 1, y la propia figura de "Aplicaciones en Diversos Dominios" de la diapositiva 26 (5G/6G, Industria 5.0, robótica, generación de código, simulación social...), reproducen **casi palabra por palabra** la taxonomía y hasta los dominios de aplicación de un único *paper* ancla: Tran, Dao, Nguyen, Pham, O'Sullivan & Nguyen, *"Multi-Agent Collaboration Mechanisms: A Survey of LLMs"* ([arXiv:2501.06322](https://arxiv.org/abs/2501.06322), enero 2025). Es el mismo patrón que las Sesiones 19 y 20: una sesión entera construida como traducción didáctica de un solo *survey*, sin decirlo explícitamente en las diapositivas.
> **El puente con la clase anterior:** la Sesión 20 (`Sesion20_LearningFromLogs_ANALISIS_COMPLETO.md`) cerraba con una pregunta abierta: *"hoy un agente mejoró su prompt leyendo su propia historia, en solitario. ¿Y si hubiera muchos agentes, compitiendo y compartiendo lo aprendido?"* — esta sesión es literalmente esa respuesta: pasa de un agente que aprende solo (Sesiones 19-20) a **varios agentes que colaboran, compiten o hacen ambas cosas a la vez** (Sesión 21).

---

## 1. El marco de cinco dimensiones

### 1.1 Visión general

La diapositiva de apertura organiza el resto de la sesión alrededor de un **sistema multiagente** (*Multi-Agent System*, MAS) descrito con cinco dimensiones. Reconstruyendo el diagrama (actores en el centro-arriba, y cuatro cuadrantes alrededor de un núcleo "Marco MAS"):

```
                         Actores
                          │
   Coordinación ──────────┼────────── Tipos
   (Protocolos)           │        (Cooperación / Competencia)
                    ┌─────┴─────┐
                    │ Marco MAS │
                    └─────┬─────┘
   Estrategias ───────────┼────────── Estructuras
(Basadas en reglas/roles) │      (Centralizada / Distribuida)
```

El conjunto de actores se define formalmente como $A = \{a_i\}_{i=1}^n$. Las cinco dimensiones — **Actores**, **Tipos** de colaboración, **Estrategias** de colaboración, **Estructuras** de comunicación y **Arquitecturas de Coordinación** — son exactamente las cinco secciones en que se organiza el resto del material (§2 a §5 de este documento), y coinciden con la estructura del *survey* ancla identificado en el Hallazgo clave.

### 1.2 Un eje adicional: en qué etapa del *pipeline* se colabora

Antes de entrar a las cinco dimensiones, el material introduce un eje transversal: **en qué punto del ciclo de *machine learning* ocurre la colaboración**, no solo *cómo*.

| Etapa inicial | Etapa intermedia | Etapa tardía |
|---|---|---|
| Compartir contexto | Compartir modelo | Compartir salida |
| Intercambio de datos | Compartir pesos | Compartir objetivo |
| *Embedding* de entrada | Intercambio de inteligencia | Compartir tarea |

La idea central es que la colaboración no es un único punto de integración fijo: dos agentes pueden colaborar compartiendo solo el contexto de entrada (barato, poco acoplado) hasta compartir pesos del modelo o el objetivo final de la tarea (caro, muy acoplado). Esta flexibilidad es lo que permite que los sistemas multiagente se adapten a distintos escenarios sin un único diseño rígido.

---

## 2. Tipos de colaboración: cooperación, competencia y coopetición

### 2.1 Cooperación

Los agentes alinean sus objetivos individuales $o_i$ con una meta colectiva compartida $O_{collab}$, trabajando juntos hacia un propósito común.

```
          Objetivo Compartido
                    │
      ┌─────────────┼─────────────┐
  Agente 1       Agente 2       Agente 3
(objetivo 1)   (objetivo 2)   (objetivo 3)
```

| Ventajas | Desventajas |
|---|---|
| Asigna subtareas según las fortalezas de cada agente; simple de diseñar con objetivos claros | Objetivos desalineados causan ineficiencias; el fallo de un agente puede amplificarse en todo el sistema |

**Escenarios de ejemplo:** generación de código, responder preguntas, sistemas de toma de decisiones. **Caso de uso destacado:** escritura académica, donde agentes Editor, Traductor, Investigador y Verificador cooperan hacia una producción académica de calidad.

### 2.2 Competencia

Los agentes priorizan sus propios objetivos $o_i$, que pueden entrar en conflicto u oponerse a los de otros agentes.

```
Agente 1 (Fiscal)  ──── compiten ────  Agente 2 (Acusado)
  objetivo: condena                     objetivo: absolución
                    │
                Resultado
               (Decisión)
```

| Ventajas | Desventajas |
|---|---|
| Impulsa a los agentes a desempeñarse mejor; promueve estrategias adaptativas e innovación | Necesita mecanismos para resolver conflictos; debe asegurar que la competencia siga siendo beneficiosa, no destructiva |

**Escenarios de ejemplo:** sistemas de debate, entornos de juego, juego estratégico. **Caso de uso destacado:** simulación de tribunal, donde Fiscal y Acusado debaten y compiten por resultados opuestos.

### 2.3 Coopetición

Un enfoque híbrido: los agentes colaboran en tareas compartidas mientras compiten en otros aspectos, equilibrando cooperación y competencia dentro del mismo sistema.

```
        Tarea Compartida (cooperan)
                    │
              ┌─────┴─────┐
          Agente 1 ── compiten ── Agente 2
          (Tarea A)              (Tarea B)
```

| Ventajas | Desventajas |
|---|---|
| Equilibra intercambios para alcanzar acuerdos mutuos; combina beneficios de ambos paradigmas | Pocos estudios exploran la coopetición en profundidad; complejo de implementar bien |

**Escenarios de ejemplo:** sistemas de negociación, arquitecturas de **Mezcla de Expertos** (*Mixture of Experts*, MoE) — donde varios expertos "compiten" por ser el más relevante para una entrada, mientras el sistema conjunto "coopera" para producir una salida única. **Caso de uso destacado:** creación de políticas públicas, donde los agentes compiten en aspectos específicos mientras cooperan en objetivos de gobernanza compartidos.

---

## 3. Estrategias de colaboración: reglas, roles y modelo

### 3.1 Basada en reglas

Las interacciones están estrictamente controladas por reglas predefinidas, asegurando que los agentes se coordinen según restricciones fijas del sistema.

| Ventajas | Desventajas |
|---|---|
| Eficiente, con alta predictibilidad; asegura consistencia y equidad | Baja adaptabilidad a la incertidumbre; difícil de escalar para tareas complejas |

**Escenarios de ejemplo:** sistemas de búsqueda de consenso, respuesta de preguntas con mecanismos de votación. **Ejemplo ilustrado — votación por mayoría:**

```
                Consulta del Usuario
       A1(Sí)   A2(Sí)   A3(No)   A4(Sí)
                     │
             Mayoría: Sí (3/4)
```

### 3.2 Basada en roles

Aprovecha roles predefinidos y distintos, o división del trabajo, con cada agente operando sobre un objetivo segmentado $o_i \subseteq O_{collab}$.

| Ventajas | Desventajas |
|---|---|
| Modularidad y reutilización; aprovecha la experiencia especializada de cada agente | Difícil de escalar para tareas complejas; el rendimiento depende de qué tan bien conectado está cada agente al resto |

**Escenarios de ejemplo:** desarrollo de software, robótica, procesos de revisión por pares. **Ejemplo ilustrado — desarrollo de software:**

```
              Objetivo del Proyecto de Software
Gerente de     Arquitecto de    Desarrollador     Control de
Producto   →     Solución    →  Implementación →   Calidad
(Requisitos)      (Diseño)                        (Pruebas)
```

### 3.3 Basada en modelo

Con incertidumbre en la percepción, el entorno o los objetivos compartidos, los agentes realizan toma de decisiones probabilística en vez de seguir reglas o roles fijos.

| Ventajas | Desventajas |
|---|---|
| Adaptabilidad a entornos dinámicos; robusta ante incertidumbre y ruido | Compleja de diseñar e implementar; operaciones computacionalmente costosas |

**Escenarios de ejemplo:** entornos de juego con incertidumbre, robótica en entornos dinámicos. **Ejemplo ilustrado:** dos agentes que observan un entorno dinámico, se comunican, y deciden con base en $P(\text{acción} \mid \text{estado})$ — probabilidad de una acción dado el estado observado — en vez de una regla fija.

**Nota de síntesis sobre las tres estrategias (diapositiva 16):** las estrategias basadas en reglas o roles imitan dinámicas de colaboración humana (debate, regla de mayoría); la basada en modelo va un paso más allá e infiere los objetivos y la racionalidad de los demás agentes mediante **Modelado Gráfico Probabilístico** (*Probabilistic Graphical Model*, PGM) o **Teoría de la Mente** (*Theory of Mind*, ToM) — la capacidad de un agente de representar internamente lo que otro agente "cree" o "quiere" — permitiendo adaptar creencias y acciones propias en consecuencia.

---

## 4. Estructuras de comunicación: centralizada, descentralizada y jerárquica

### 4.1 Centralizada

La decisión de colaboración se concentra en un agente central (*hub*) que gestiona, controla y coordina todas las interacciones.

```
        A2
A1 ──  Hub  ── A3
        │
       A4, A5, A6
```

| Ventajas | Desventajas |
|---|---|
| Simple de diseñar e implementar; asignación eficiente de recursos | Punto único de fallo; sistema menos resiliente a interrupciones |

**Implementaciones citadas:** Aprendizaje Federado (*Federated Learning*, FL), **LLM-Blender** ([Jiang, Ren & Lin, ACL 2023](https://arxiv.org/abs/2306.02561) — ensambla las salidas de varios LLMs mediante *ranking* por pares y fusión generativa), **AutoAct** (*Automatic Agent Learning from Scratch*, aprendizaje automático de agentes desde cero mediante auto-planificación).

### 4.2 Descentralizada

El control y la toma de decisiones se distribuyen entre los agentes, que se comunican directamente punto a punto, sin un coordinador central.

```
          Agente 1
   Agente 6      Agente 2
   Agente 5      Agente 3
          Agente 4
(cada agente puede hablar directo con cualquier otro)
```

| Ventajas | Desventajas |
|---|---|
| El sistema sigue funcionando si algunos agentes fallan | Asignación de recursos ineficiente; altos costos de comunicación (cada par debe coordinarse) |

**Implementaciones citadas:** sistemas de debate multiagente, **AgentCF** ([Zhang et al., 2023, arXiv:2310.09233](https://arxiv.org/abs/2310.09233) — simula interacciones usuario-ítem con agentes-usuario y agentes-ítem para sistemas de recomendación), **AgentVerse** ([Chen et al., 2023, arXiv:2308.10848](https://arxiv.org/abs/2308.10848)).

### 4.3 Jerárquica

Los agentes se organizan en un sistema en capas, con roles distintos y niveles de autoridad, permitiendo comunicación estructurada.

```
                    Agente Gerente
         ┌────────────┼────────────┐
   Coordinador 1  Coordinador 2  Coordinador 3
      │    │         │    │        │    │
     T1   T2        T3   T4       T5   T6
```

| Ventajas | Desventajas |
|---|---|
| Bajo cuello de botella (la comunicación está distribuida por niveles); asignación eficiente de recursos | Alta complejidad y latencia en sistemas de muchos niveles |

**Implementaciones citadas:** AgentVerse, **Red Dinámica de Agentes-LLM** (*Dynamic LLM-Agent Network*, **DyLAN** — [Liu, Zhang, Li, Liu & Yang, 2023, arXiv:2310.02170](https://arxiv.org/abs/2310.02170); modela la colaboración como una red *feed-forward* temporal y desactiva dinámicamente agentes de bajo rendimiento), **CAMEL** ([Li et al., NeurIPS 2023, arXiv:2303.17760](https://arxiv.org/abs/2303.17760) — agentes que se asignan roles mediante *role-playing* guiado por *inception prompting*, con mínima intervención humana).

---

## 5. Arquitecturas de coordinación: estática y dinámica

### 5.1 Estática

Se basa en reglas predefinidas y conocimiento del dominio para establecer canales de colaboración que **permanecen fijos durante toda la ejecución**.

| Ventajas | Desventajas |
|---|---|
| Ejecución consistente; aprovecha bien el conocimiento del dominio | Depende de un diseño inicial preciso; los canales fijos pueden tener problemas de escalabilidad |

**Mecanismos y ejemplos:** encadenamiento secuencial, **MapCoder** ([Islam, Ali & Parvez, 2024, arXiv:2405.11403](https://arxiv.org/abs/2405.11403) — generación de código multiagente para resolución de problemas competitivos), **MACRec** (*Multi-Agent Collaboration framework for Recommendation* — [Wang et al., SIGIR 2024, arXiv:2402.15235](https://arxiv.org/abs/2402.15235)).

### 5.2 Dinámica

Diseñada para adaptarse en tiempo real a entornos cambiantes o en evolución, y a requisitos de tarea que no se conocen de antemano.

| Ventajas | Desventajas |
|---|---|
| Roles y canales adaptables según la necesidad de la tarea; maneja bien tareas complejas y cambiantes | Mayor uso de recursos por los ajustes en tiempo real; riesgo de fallos durante esos cambios dinámicos |

**Mecanismos y ejemplos:** agente de gestión, orquestación basada en **DAG** (*Directed Acyclic Graph*, grafo acíclico dirigido — permite expresar dependencias entre subtareas sin ciclos), orquestación basada en **Persona** con **Solo Performance Prompting** (**SPP** — [Wang et al., NAACL 2024, arXiv:2307.05300](https://arxiv.org/abs/2307.05300); un único LLM simula múltiples personas especializadas en una auto-colaboración de varios turnos, sin necesitar agentes separados de verdad), orquestación de grafos en general.

---

## 6. Aplicaciones y problemas abiertos

### 6.1 Dominios de aplicación (diapositiva 26)

El material presenta un mosaico de dominios donde ya se aplican sistemas multiagente basados en LLM:

| Bloque | Dominios |
|---|---|
| Redes e industria | 5G/6G, IoT (*Internet of Things*, internet de las cosas), Industria 5.0, robótica, sistemas autónomos |
| Lenguaje | Respuesta de preguntas (QA), generación de lenguaje natural (NLG), aplicaciones MAS basadas en LLM |
| Sociedad y desarrollo | Simulación social y cultural, desarrollo de software, generación de código |

Esta lista coincide, casi frase por frase, con los dominios de aplicación que enumera el *survey* ancla de Tran et al. (§Hallazgo clave) — otra señal de que la diapositiva es una síntesis directa del *paper*, no una lista construida de forma independiente por el curso.

### 6.2 Problemas abiertos y desafíos (diapositiva 28)

| Bloque | Desafíos |
|---|---|
| Gobernanza | Inteligencia colectiva artificial, toma de decisiones, escalabilidad |
| Evaluación | Métricas unificadas, *benchmarks* dinámicos, reproducibilidad |
| Riesgo ético | Seguridad, alucinaciones, ataques adversarios, sobre-dependencia |

**Necesidad crítica, en palabras del material:** abordar estos desafíos es esencial para el despliegue seguro y efectivo de sistemas multiagente basados en LLM — un cierre deliberadamente honesto sobre los límites del campo, coherente con el tono de "seminario académico" del resto de las sesiones de este docente (ver también §5 "Los límites" de la Sesión 20).

---

## 7. Síntesis — cómo se conectan las cinco dimensiones entre sí

Ninguna de las cinco dimensiones es independiente de las demás — son ejes que se combinan, no una lista de opciones mutuamente excluyentes:

- El **Tipo** de colaboración (cooperación/competencia/coopetición) determina si conviene una **Estructura** centralizada (más natural para cooperación pura, con un *hub* que reparte trabajo) o descentralizada (más natural para competencia, sin un árbitro único).
- La **Estrategia** (reglas/roles/modelo) determina cuánta incertidumbre puede tolerar el sistema — basada en reglas para entornos predecibles, basada en modelo cuando ni los propios agentes conocen del todo los objetivos o el entorno de los demás.
- La **Arquitectura de Coordinación** (estática/dinámica) es ortogonal a las anteriores: incluso un sistema cooperativo con estructura jerárquica puede coordinarse de forma estática (canales fijos, como en MapCoder) o dinámica (canales que cambian con la tarea, como en la orquestación por DAG).

El ejemplo de simulación de tribunal (§2.2) ilustra bien la combinación: **Tipo** = competencia, **Estructura** = probablemente descentralizada (Fiscal y Acusado se comunican directo, sin *hub*), **Estrategia** = basada en roles (cada uno tiene un objetivo fijo y un papel claro), **Arquitectura** = estática (el protocolo de un juicio no cambia a mitad de proceso).

**Frase de cierre del material:** *"Los mejores agentes son aquellos que nunca dejan de aprender."* — un cierre que, leído junto con el puente señalado al inicio de este documento, resume el arco completo del Módulo 7: de un agente que corrige su salida (Sesión 19), a uno que reescribe su propio *prompt* con lo que aprendió (Sesión 20), a un sistema de varios agentes que colaboran, compiten o negocian para resolver juntos lo que ninguno resolvería solo (Sesión 21).

---

## 8. Checklist práctico — diseñando un sistema multiagente colaborativo

- [ ] ¿Los objetivos de los agentes están alineados (cooperación), en conflicto (competencia), o ambas cosas en distintos aspectos (coopetición)? Esa respuesta condiciona casi todo el resto del diseño.
- [ ] ¿En qué etapa del *pipeline* conviene compartir información entre agentes: contexto de entrada, pesos/modelo, o solo la salida final? (§1.2)
- [ ] ¿El entorno y los objetivos de los demás agentes son ciertos y conocidos, o hay incertidumbre real? Si hay incertidumbre, una estrategia basada en reglas o roles fijos probablemente no alcance — considerar una basada en modelo (PGM/ToM).
- [ ] ¿Un punto único de fallo (estructura centralizada) es aceptable para este sistema, o se necesita que siga funcionando si un agente cae (descentralizada)?
- [ ] Si hay muchos agentes y tareas heterogéneas: ¿conviene una jerarquía con coordinadores intermedios, en vez de un solo *hub* o una malla completa punto a punto?
- [ ] ¿Los canales de colaboración pueden fijarse de antemano (arquitectura estática, más simple y predecible), o la tarea exige adaptarlos en tiempo real (dinámica, más costosa mecánicamente pero más flexible)?
- [ ] ¿Cómo se evaluará el sistema multiagente en su conjunto, no solo cada agente por separado? (§6.2 — métricas unificadas y reproducibilidad son, según el propio material, un problema abierto, no algo resuelto)
- [ ] ¿Qué mecanismo existe para resolver conflictos si el sistema tiene algún componente competitivo, y para evitar que la competencia deje de ser beneficiosa?

---

## 9. Referencias

**Paper ancla identificado (no citado explícitamente en las diapositivas, pero es la fuente evidente del marco y de los ejemplos):**
- Tran, K-T., Dao, D., Nguyen, M-D., Pham, Q-V., O'Sullivan, B., Nguyen, H.D. (2025). *"Multi-Agent Collaboration Mechanisms: A Survey of LLMs."* [arXiv:2501.06322](https://arxiv.org/abs/2501.06322).

**Sistemas y métodos nombrados en las diapositivas, identificados y verificados en esta investigación:**
- Jiang, D., Ren, X., Lin, B.Y. (2023). *"LLM-Blender: Ensembling Large Language Models with Pairwise Ranking and Generative Fusion."* ACL 2023. [arXiv:2306.02561](https://arxiv.org/abs/2306.02561).
- Zhang, J., et al. (2023). *"AgentCF: Collaborative Learning with Autonomous Language Agents for Recommender Systems."* [arXiv:2310.09233](https://arxiv.org/abs/2310.09233).
- Chen, W., et al. (2023). *"AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors."* [arXiv:2308.10848](https://arxiv.org/abs/2308.10848).
- Liu, Z., Zhang, Y., Li, P., Liu, Y., Yang, D. (2023). *"Dynamic LLM-Agent Network (DyLAN): An LLM-agent Collaboration Framework with Agent Team Optimization."* [arXiv:2310.02170](https://arxiv.org/abs/2310.02170).
- Li, G., et al. (2023). *"CAMEL: Communicative Agents for 'Mind' Exploration of Large Language Model Society."* NeurIPS 2023. [arXiv:2303.17760](https://arxiv.org/abs/2303.17760).
- Islam, M.A., Ali, M.A., Parvez, M.R. (2024). *"MapCoder: Multi-Agent Code Generation for Competitive Problem Solving."* [arXiv:2405.11403](https://arxiv.org/abs/2405.11403).
- Wang, Z., et al. (2024). *"MACRec: A Multi-Agent Collaboration Framework for Recommendation."* SIGIR 2024. [arXiv:2402.15235](https://arxiv.org/abs/2402.15235).
- Wang, Z., Mao, S., Wu, W., Ge, T., Wei, F., Ji, H. (2023/2024). *"Unleashing Cognitive Synergy in Large Language Models: A Task-Solving Agent through Multi-Persona Self-Collaboration"* (Solo Performance Prompting, SPP). NAACL 2024. [arXiv:2307.05300](https://arxiv.org/abs/2307.05300).

**Arco interno del curso:**
- `Sesion20_LearningFromLogs_ANALISIS_COMPLETO.md` (Módulo 7) — esta sesión es la respuesta directa a la pregunta de cierre de la Sesión 20 sobre agentes que compiten y comparten lo aprendido.
- `Sesion19_FeedbackYCorreccion_ANALISIS_COMPLETO.md` (Módulo 7) — primer eslabón del arco del módulo: un agente que corrige su propia salida, antes de aprender a reescribir su *prompt* (Sesión 20) y a colaborar con otros agentes (esta sesión).

---

*Documento generado a partir del PDF de la Sesión 21 (Módulo 7, UTEC Posgrado) — 30 páginas extraídas con `pdftotext` tras encontrar el archivo protegido contra edición — más investigación propia para identificar y verificar el origen de los sistemas y el marco teórico citados sin bibliografía explícita en el material original.*
