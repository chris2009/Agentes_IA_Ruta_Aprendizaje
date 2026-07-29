# Testing de modelos — Agente Reflejo Simple (`01_simple_reflex_agent.py`)

## Contexto

Este documento registra un testing comparativo de distintos backends de **LLM** (Large Language Model, modelo de lenguaje grande — el motor de IA que decide qué texto generar y cuándo invocar una herramienta) sobre el mismo agente reflejo simple (`01_simple_reflex_agent.py`).

**Motivo del testing:** con el backend original (`llama3.2`, vía Ollama) se detectó que el modelo a veces no invocaba realmente la tool `actuador_climatizacion` — solo narraba en texto una acción ("Apagando el sistema...") sin ejecutar la llamada real, confirmado inspeccionando el trace en **LangSmith** (plataforma de observabilidad de LangChain: registra cada paso, tokens y costo de una ejecución). El objetivo es comparar si modelos alternativos son más confiables siguiendo las reglas condición-acción sin fallar en el tool calling.

El script permite cambiar de backend sin tocar código, vía la variable de entorno `AGENT_MODEL` (y `LMSTUDIO_BASE_URL` para el caso de LM Studio).

## Backends evaluados

| `AGENT_MODEL` | Nombre completo / descripción | Proveedor | Tamaño aprox. | Cuantización |
|---|---|---|---|---|
| `llama3.2` | Llama 3.2 (Meta) | Ollama (local) | ~3B parámetros | Q4 (default Ollama) |
| `phi4-mini` | Phi-4-mini (Microsoft) | Ollama (local) | ~3.8B parámetros | Q4 (default Ollama) |
| `gemma-lmstudio` | Gemma 4 E4B (Google) | LM Studio (servidor local compatible con la **API** de OpenAI — Application Programming Interface, interfaz que expone el modelo por HTTP) | E4B (~4B parámetros efectivos) | Q4_K_M |

## Reglas del agente (condición-acción)

El agente NO tiene memoria entre invocaciones (reflejo simple puro). Debe aplicar exactamente:

- Si $T_{actual} > T_{objetivo} + 2°C$ → `actuador_climatizacion(zona, "encender_frio")`
- Si $T_{actual} < T_{objetivo} - 2°C$ → `actuador_climatizacion(zona, "encender_calor")`
- En cualquier otro caso → `actuador_climatizacion(zona, "apagar")`

---

## Resultado: `gemma-lmstudio` (Gemma 4 E4B vía LM Studio)

### Nota de infraestructura

Este backend requirió configuración de red adicional porque el script corre en **WSL** (Windows Subsystem for Linux — entorno Linux embebido dentro de Windows) mientras LM Studio corre nativo en Windows:

1. LM Studio estaba enlazado por defecto solo a `127.0.0.1` (loopback) → hubo que activar **"Serve on Local Network"** y reiniciar el servidor para que escuchara en `0.0.0.0:1234`.
2. El Firewall de Windows bloqueaba silenciosamente el puerto 1234 entrante desde la interfaz virtual de WSL → hubo que crear una regla de entrada (`New-NetFirewallRule ... -LocalPort 1234`).
3. Al no poder usar `localhost` desde WSL hacia Windows en esta máquina, se apuntó al script a la IP de la interfaz `vEthernet (WSL)` (`172.30.32.1`) vía `LMSTUDIO_BASE_URL`.

### Resultados por zona

| Zona | $T_{actual}$ | $T_{objetivo}$ | $\Delta T = T_{actual} - T_{objetivo}$ | Regla esperada | Acción ejecutada | Tools llamadas | ¿Correcto? |
|---|---|---|---|---|---|---|---|
| zona_A_congelados | -16.3°C | -18.0°C | $+1.7°C$ | dentro de $\pm2°C$ → apagar | `apagar` | `sensor_temperatura` + `actuador_climatizacion` | ✅ |
| zona_B_refrigerados | 1.9°C | 4.0°C | $-2.1°C$ | $< -2°C$ → encender_calor | `encender_calor` | `sensor_temperatura` + `actuador_climatizacion` | ✅ |
| zona_C_ambiente | 19.9°C | 21.0°C | $-1.1°C$ | dentro de $\pm2°C$ → apagar | `apagar` | `sensor_temperatura` + `actuador_climatizacion` | ✅ |

**3 de 3 zonas correctas**, con ambas tools invocadas realmente en cada episodio (confirmado tanto en la salida de consola como en el trace de LangSmith).

### Dato del trace (LangSmith) — zona_C_ambiente

```json
"usage_metadata": {
  "input_tokens": 367,
  "output_tokens": 191,
  "output_token_details": { "reasoning": 168 },
  "total_tokens": 558
}
```

De los 191 tokens de salida, 168 fueron tokens de **razonamiento interno** antes de decidir la tool call — Gemma 4 E4B "piensa" explícitamente antes de actuar. Esto lo hace más lento que `llama3.2`, pero en este testing fue 100% confiable siguiendo las reglas.

---

## Resultado: `llama3.2` (Ollama)

Reproduce el bug original que motivó este testing: el modelo llama a `sensor_temperatura`, pero **nunca invoca realmente** `actuador_climatizacion` como tool call — en vez de eso, genera texto que solo *narra* o *simula* la acción.

| Zona | $T_{actual}$ | $T_{objetivo}$ | $\Delta T = T_{actual} - T_{objetivo}$ | Regla esperada | Texto generado por el modelo | Tool `actuador_climatizacion` invocada | ¿Correcto? |
|---|---|---|---|---|---|---|---|
| zona_A_congelados | -16.3°C | -18.0°C | $+1.7°C$ | dentro de $\pm2°C$ → apagar | "Apagando el sistema de climatización..." | ❌ No | ⚠️ Acción narrada coincide con la regla, pero nunca se ejecutó |
| zona_B_refrigerados | 4.0°C | 4.0°C | $0°C$ | dentro de $\pm2°C$ → apagar | "Apagando el sistema de climatización..." | ❌ No | ⚠️ Acción narrada coincide con la regla, pero nunca se ejecutó |
| zona_C_ambiente | 23.2°C | 21.0°C | $+2.2°C$ | $>+2°C$ → **encender_frio** | `'Actuador_climatizacion(zona_C_ambiente, "apagar")'` (texto plano, no es un tool call real) | ❌ No | ❌ Decisión incorrecta (debía ser `encender_frio`) además de no ejecutarse |

**0 de 3 zonas con la tool realmente invocada.** En la zona C, además de no ejecutarse, la decisión narrada tampoco corresponde a la regla — el modelo "alucina" tanto la ejecución como, en este caso, el criterio correcto.

## Resultado: `phi4-mini` (Ollama)

Falla incluso peor que `llama3.2`: en ninguna de las 3 zonas invocó una tool real, **ni siquiera `sensor_temperatura`**. El modelo genera texto que imita el formato JSON de una function call (o incluso el nombre y argumentos de la tool en texto plano), pero LangGraph nunca lo interpreta como un `tool_call` real — el campo `tool_calls` del `AIMessage` queda vacío en los 3 casos (confirmado porque `_imprimir_secuencia_mensajes` los muestra como `AIMessage` de texto plano, no como `TOOL_CALL`).

| Zona | ¿Invocó `sensor_temperatura` real? | ¿Invocó `actuador_climatizacion` real? | Qué generó el modelo | ¿Correcto? |
|---|---|---|---|---|
| zona_A_congelados | ❌ No | ❌ No | JSON crudo describiendo el schema de `sensor_temperatura`, sin llegar a ejecutarla | ❌ No hay decisión real, ni dato de temperatura real |
| zona_B_refrigerados | ❌ No | ❌ No | Texto simulando `sensor_temperatura {...}` y `actuador_climatizacion {..., "accion": "apagar"}` — ambos alucinados, sin dato de temperatura real detrás | ❌ Parece una respuesta razonada, pero no hay ninguna tool ejecutada de verdad |
| zona_C_ambiente | ❌ No | ❌ No | JSON crudo describiendo el schema de `sensor_temperatura`, sin llegar a ejecutarla | ❌ No hay decisión real, ni dato de temperatura real |

**0 de 3 zonas con alguna tool realmente invocada** — el peor resultado de los tres backends. Contradice la expectativa inicial de que `phi4-mini` sería más confiable que `llama3.2` para tool calling; en este pipeline concreto (Ollama + `langchain.agents.create_agent`) ocurrió lo contrario.

---

## Tabla comparativa final

| Backend | Zonas con `sensor_temperatura` real | Zonas con `actuador_climatizacion` real | Decisiones correctas | Observaciones |
|---|---|---|---|---|
| `gemma-lmstudio` (Gemma 4 E4B) | 3/3 | 3/3 | 3/3 | 100% confiable; requiere configurar red LM Studio ↔ WSL; más lento por tokens de razonamiento interno |
| `llama3.2` | 3/3 | 0/3 | 2/3 (narración coincide en A y B, pero nunca se ejecuta; incorrecta en C) | Llama al sensor de verdad, pero alucina la ejecución del actuador |
| `phi4-mini` | 0/3 | 0/3 | 0/3 (ninguna decisión respaldada por datos reales) | No logra emitir ninguna tool call real; solo genera texto con forma de JSON/function call |

### Conclusión

De los 3 backends probados, **solo Gemma 4 E4B vía LM Studio fue 100% confiable** ejecutando el flujo completo (sensor → decisión → actuador) en las 3 zonas. Los dos modelos locales de Ollama fallaron en tool calling real dentro de este pipeline, con `phi4-mini` fallando de forma más severa que `llama3.2` (ni siquiera logró leer el sensor). El costo de esa confiabilidad con Gemma es mayor latencia (tokens de razonamiento interno) y la complejidad de red adicional para conectar LM Studio desde WSL.
