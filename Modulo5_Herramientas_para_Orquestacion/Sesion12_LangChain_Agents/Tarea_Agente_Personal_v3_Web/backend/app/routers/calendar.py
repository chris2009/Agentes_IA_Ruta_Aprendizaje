from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_v2
from app.models.calendar import EventoIn, EventoOut

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/events", response_model=list[EventoOut])
def listar_eventos(fecha: str = "", v2=Depends(get_v2)):
    try:
        return v2._obtener_eventos_dia(fecha)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"No se pudo consultar Google Calendar: {error}")


@router.post("/events")
def crear_evento(datos: EventoIn, v2=Depends(get_v2)):
    mensaje = v2.agendar_actividad.invoke(datos.model_dump())
    return {"mensaje": mensaje}
