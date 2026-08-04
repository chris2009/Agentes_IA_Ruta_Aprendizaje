from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_v2
from app.models.activities import ActividadIn, ActividadOut, EstadoUpdateIn, MensajeOut

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=list[ActividadOut])
def listar_actividades(v2=Depends(get_v2)):
    actividades = v2._cargar_actividades()
    salida = []

    for a in actividades:
        dias_restantes = max((v2.date.fromisoformat(a["fecha_limite"]) - v2.date.today()).days, 0)
        salida.append({
            **a,
            "puntaje_urgencia": v2._puntaje_urgencia(a),
            "dias_restantes": dias_restantes,
        })

    salida.sort(key=lambda a: a["puntaje_urgencia"], reverse=True)
    return salida


@router.post("", response_model=MensajeOut)
def crear_actividad(datos: ActividadIn, v2=Depends(get_v2)):
    mensaje = v2.agregar_actividad.invoke(datos.model_dump())
    return {"mensaje": mensaje}


@router.patch("/{actividad_id}/estado", response_model=MensajeOut)
def actualizar_estado(actividad_id: int, datos: EstadoUpdateIn, v2=Depends(get_v2)):
    mensaje = v2.actualizar_estado.invoke({"actividad_id": actividad_id, "nuevo_estado": datos.nuevo_estado})

    if mensaje.startswith("No existe"):
        raise HTTPException(status_code=404, detail=mensaje)

    return {"mensaje": mensaje}
