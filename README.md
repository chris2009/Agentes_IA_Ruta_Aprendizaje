# 🤖 Agentes IA — Ruta de Aprendizaje

Ruta de aprendizaje del **Programa de Diseño e Implementación de Agentes de IA (Inteligencia Artificial)** de UTEC (Universidad de Ingeniería y Tecnología). Incluye notebooks, scripts y apuntes desarrollados sesión a sesión: desde los fundamentos de **LLM** (Large Language Model, modelo de lenguaje grande) hasta la implementación de agentes cognitivos con **LangChain** y **LangGraph**.

## 📚 Contenido por módulo

| Módulo | Tema |
|---|---|
| 🧭 **Módulo 1** — Introducción y Motivación | Qué es un agente de IA |
| 🧠 **Módulo 2** — Fundamentos de LLMs | Bases de agentes con LLM, arquitectura funcional, evaluación de modelos |
| ✍️ **Módulo 3** — Ingeniería de Prompts | Evaluación de modelos, razonamiento mediante prompts (Chain-of-Thought y variantes), modularización de prompts en agentes |
| ⚙️ **Módulo 4** — Agentes Cognitivos | Arquitectura de agentes, memoria contextual, los 5 tipos de agentes según la taxonomía de IBM (reflejo simple, reflejo basado en modelo, basado en objetivos, basado en utilidad, con aprendizaje), agentes colaborativos |
| 🔗 **Módulo 5** — Herramientas de Orquestación | Agentes y tools con LangChain, agentes RAG (Retrieval-Augmented Generation, generación aumentada por recuperación), sistemas multiagente con LangGraph |
| 🦾 **Módulo 6** — Interacción con el Mundo Físico | APIs y MCP (Model Context Protocol), agentes multimodales (texto, audio, imagen), interfaces conversacionales por voz en tiempo real (WebSocket, WebRTC), Physical AI |
| 🔁 **Módulo 7** — Aprendizaje y Mejora | Feedback y auto-corrección en agentes LLM (interno, externo, multi-agente, humano), evaluación por resultado vs. por proceso, de corregir una salida a mejorar el propio agente |

## 🧪 Experimentando con distintos LLMs (no solo un modelo)

Uno de los ejes de esta ruta fue **no quedarme con el primer modelo que funcionara**: en `Modulo4_Agentes_Cognitivos/Sesion10_Agentes_Reflexivos` construí un mecanismo (`AGENT_MODEL`) para correr el mismo agente contra distintos backends de LLM sin tocar el código, y así comparar de forma empírica qué tan confiables son ejecutando *tool calling* (la capacidad del modelo de invocar funciones/herramientas reales, no solo describirlas en texto).

| Modelo | Nombre completo | Proveedor | Tool calls reales ejecutadas | Resultado |
|---|---|---|---|---|
| 🥇 `gemma-lmstudio` | Gemma 4 E4B (Google) | LM Studio (servidor local) | 3/3 | ✅ 100% confiable, todas las decisiones correctas |
| 🥈 `llama3.2` | Llama 3.2 (Meta) | Ollama (local) | 0/3 | ⚠️ Lee el sensor pero **alucina** la ejecución del actuador |
| 🥉 `phi4-mini` | Phi-4-mini (Microsoft) | Ollama (local) | 0/3 | ❌ No logra emitir ninguna tool call real |

Este experimento (detallado en [`TESTING_MODELOS_AGENTE_REFLEJO.md`](Modulo4_Agentes_Cognitivos/Sesion10_Agentes_Reflexivos/agents26_m4s10-main/TESTING_MODELOS_AGENTE_REFLEJO.md)) incluyó además resolver la integración de LM Studio como servidor OpenAI-compatible corriendo en Windows, consumido desde un entorno WSL (Windows Subsystem for Linux) — con su propio troubleshooting de red (firewall, binding de interfaces).

La misma pregunta reapareció en el Módulo 6 con visión: en `Modulo6_Interaccion_Fisica_Mundo_Real/Sesion17_Multimodal_Agents/agents26_m6s17-main/singlemodel.ipynb` comparé un modelo de visión local (**LLaVA** vía Ollama) contra uno en la nube (**GPT-4o-mini**) leyendo el mismo cheque bancario y estructurándolo en JSON: LLaVA alucinó el banco, el monto y el nombre del cliente con la misma confianza aparente que los datos correctos; GPT-4o-mini los leyó bien. Evidencia concreta de que, para documentos con consecuencias reales, "corre localmente" no es sinónimo de "es confiable" — detallado en [`Sesion17_Multimodalidad_ANALISIS_COMPLETO.md`](Modulo6_Interaccion_Fisica_Mundo_Real/Sesion17_Multimodal_Agents/Sesion17_Multimodalidad_ANALISIS_COMPLETO.md).

## 🛠️ Stack

`Python` · `LangChain` · `LangGraph` · `Ollama` · `LM Studio` · `LangSmith` (observabilidad/tracing) · `OpenAI API` (GPT-4o, Whisper, gpt-image-1, Sora-2) · `MCP` (Model Context Protocol) · `fastrtc` (voz en tiempo real) · Jupyter Notebooks

## 📝 Notas

- El material propio del docente/UTEC (diapositivas en PDF) no se incluye en este repositorio por derechos de autor — ver `.gitignore`.
- Cada carpeta de sesión con código Python incluye su propio `requirements.txt` y, cuando aplica, instrucciones de ejecución en su README o docstring.
- El proyecto final del programa se sube por separado cuando esté terminado.
