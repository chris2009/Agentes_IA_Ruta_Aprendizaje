import uvicorn
import os
from pydantic import BaseModel
from langchain.messages import HumanMessage, AIMessage
from fastapi import FastAPI, HTTPException
from kratos_agent import kratos
from contextlib import asynccontextmanager
global kratos_agent_executor

kratos_agent_executor = kratos

@asynccontextmanager
async def lifespan(app: FastAPI):
    global kratos_agent_executor
    required = ["OPENAI_API_KEY"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        print(f"WARNING: Variables de entorno faltantes: {', '.join(missing)}")
    kratos_agent_executor = kratos
    yield

app = FastAPI(
    title="Kratos Motivational Agent",
    description="Consejos motivacionales desde la perspectiva de Kratos, el Dios de la Guerra",
    version="1.0.0"
)


class AdviceRequest(BaseModel):
    message: str
    chat_history: list[dict] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Me siento sin motivación para seguir entrenando, ¿qué hago?",
                "chat_history": []
            }
        }
    }

class AdviceResponse(BaseModel):
    response: str
    agent: str = "Kratos, Dios de la Guerra"


@app.get("/")
async def root():
    return {
        "message": "El Dios de la Guerra te aguarda. Usa /advice para recibir su sabiduría.",
        "docs": "/docs"
    }


@app.post("/advice", response_model=AdviceResponse)
async def get_advice(request: AdviceRequest):
    if not kratos_agent_executor:
        raise HTTPException(status_code=503, detail="El agente no está inicializado")

    # Convert chat history to LangChain messages
    history = []
    for msg in request.chat_history:
        if msg.get("role") == "human":
            history.append(HumanMessage(content=msg["content"]))
        elif msg.get("role") == "assistant":
            history.append(AIMessage(content=msg["content"]))
    
    history.append(HumanMessage(content=request.message))

    try:
        result = await kratos_agent_executor.ainvoke({"messages": history})
        # la respuesta está en el último mensaje del grafo
        return AdviceResponse(response=result["messages"][-1].content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del agente: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "alive", "agent": "Kratos"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)