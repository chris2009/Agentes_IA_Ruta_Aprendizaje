from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_v2
from app.models.chat import ChatMessage, ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(datos: ChatRequest, v2=Depends(get_v2)):
    historial = [{"role": "user" if m.role == "user" else "assistant", "content": m.content} for m in datos.history]
    historial.append({"role": "user", "content": datos.message})

    try:
        resultado = await v2.agent.ainvoke({"messages": historial})
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Error del agente: {error}")

    # El agente puede razonar en varios pasos (saludo -> tool call -> mas
    # texto -> otra tool call -> ...) antes de terminar el turno. Tomar solo
    # el ultimo mensaje pierde todo ese razonamiento intermedio y deja una
    # respuesta incoherente (un fragmento suelto sin el contexto de arriba).
    # Se concatenan todos los mensajes de tipo IA con texto no vacio
    # generados en ESTE turno (los que vienen despues del historial que se
    # mando de entrada), para mostrar el razonamiento completo.
    mensajes_nuevos = resultado["messages"][len(historial):]
    fragmentos = [
        texto for m in mensajes_nuevos
        if getattr(m, "type", None) == "ai" and (texto := v2.extraer_texto(m.content).strip())
    ]
    respuesta = "\n\n".join(fragmentos) if fragmentos else "(el agente no genero una respuesta)"
    nuevo_historial = datos.history + [
        ChatMessage(role="user", content=datos.message),
        ChatMessage(role="assistant", content=respuesta),
    ]

    return {"response": respuesta, "history": nuevo_historial}
