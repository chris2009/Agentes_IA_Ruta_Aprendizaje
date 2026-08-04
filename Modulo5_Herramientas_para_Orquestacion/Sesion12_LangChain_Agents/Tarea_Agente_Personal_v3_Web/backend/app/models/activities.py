from typing import Literal

from pydantic import BaseModel


class ActividadIn(BaseModel):
    nombre: str
    tipo: Literal["academica", "personal"]
    fecha_limite: str
    duracion_minutos: int
    prioridad: Literal["alta", "media", "baja"]
    curso: str = ""
    ruta_contexto: str = ""
    entregable: str = ""


class ActividadOut(BaseModel):
    id: int
    nombre: str
    tipo: str
    curso: str = ""
    fecha_limite: str
    duracion_estimada_minutos: int
    prioridad: str
    estado: str
    ruta_contexto: str = ""
    entregable: str = ""
    puntaje_urgencia: float
    dias_restantes: int


class EstadoUpdateIn(BaseModel):
    nuevo_estado: Literal["pendiente", "iniciada", "completada"]


class MensajeOut(BaseModel):
    mensaje: str
