# Cómo ver el grafo del Equipo Editorial en LangSmith Studio

Runbook para levantar el servidor local de **LangGraph** (la librería de grafos de LangChain) y conectarlo a **Studio** (el visualizador/depurador de grafos de LangSmith), cada vez que quieras ver o depurar visualmente el agente `editor_jefe`.

## 0) Setup — una sola vez por máquina

Instalar la **CLI** (*Command Line Interface*, interfaz de línea de comandos) de LangGraph, que trae el comando `langgraph dev`. Es un paquete distinto de la librería `langgraph` que ya usa el código (esa solo corre grafos, no levanta un servidor):

```bash
pip install "langgraph-cli[inmem]"
```

El archivo `langgraph.json` de esta carpeta ya está creado — le dice a `langgraph dev` qué grafo compilado exponer:

```json
{
  "dependencies": ["."],
  "graphs": { "editor_jefe": "./editor_jefe_agent.py:editor_jefe" },
  "env": ".env"
}
```

No hace falta tocarlo salvo que cambies el nombre del archivo/variable del agente.

## 1) Flujo de siempre — cada vez que quieras ver el grafo

**Paso 1 — Terminal en esta carpeta**, con el mismo entorno (venv) donde tienes instalado `langchain`, `langgraph` y ahora `langgraph-cli`:

```bash
cd Modulo5_Herramientas_para_Orquestacion/Sesion14_LangChain_Agents_Infraestructura/lab_equipo_editorial
```

**Paso 2 — Levantar el servidor:**

```bash
langgraph dev
```

Esto arranca un servidor local en `http://127.0.0.1:2024` y **abre el navegador solo**, ya apuntando a Studio con la conexión hecha — no deberías necesitar pegar ninguna URL a mano.

**Paso 3 — Si Studio no abrió solo, o pide la URL manualmente:**

Usar exactamente:

```
http://127.0.0.1:2024
```

`localhost` y `127.0.0.1` ya están permitidos por defecto en "Allowed Domains" de Studio — no hace falta configurar nada ahí.

**Paso 4 — Usar el grafo:**

En el panel de Studio vas a ver el grafo de `editor_jefe` (con sus tools `consultar_investigador` y `consultar_editor_estilo` como nodos), puedes mandarle un mensaje de prueba y ver la ejecución paso a paso, con el estado en cada nodo.

**Paso 5 — Terminar:**

`Ctrl+C` en la terminal donde corre `langgraph dev`. Esto apaga el servidor; Studio deja de poder conectarse hasta la próxima vez que lo levantes.

## Troubleshooting

| Problema | Causa | Solución |
|---|---|---|
| *"Connection failed. Ensure your server is running at this endpoint"* contra una URL `*.trycloudflare.com` | Ese túnel es efímero — se genera una URL nueva y aleatoria cada vez que se abre un túnel, y muere apenas se cierra el proceso que la creó. La URL vieja nunca vuelve a servir. | No uses la URL vieja. Corre `langgraph dev` de nuevo y usa `http://127.0.0.1:2024` (Paso 3), o la URL de túnel *nueva* que imprima esa corrida si de verdad necesitas acceder desde otra máquina. |
| `langgraph dev` tira error de que no encuentra `editor_jefe` | El path o el nombre de variable en `langgraph.json` no coincide con `editor_jefe_agent.py` | Revisar que `editor_jefe_agent.py` siga exportando una variable a nivel de módulo llamada `editor_jefe` (la que arma `create_agent(...)`). |
| Puerto 2024 ocupado | Ya hay otro `langgraph dev` corriendo (de otra sesión/terminal) | Cerrar esa otra terminal, o correr `langgraph dev --port 2025` y usar ese puerto en el Paso 3. |
| Studio conecta pero no encuentra `ANTHROPIC_API_KEY` / `LANGSMITH_API_KEY` | `langgraph.json` apunta a `.env`, pero el archivo no existe en esta carpeta o le faltan esas variables | Verificar que `.env` (en esta misma carpeta) tenga `ANTHROPIC_API_KEY`, `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`. |
