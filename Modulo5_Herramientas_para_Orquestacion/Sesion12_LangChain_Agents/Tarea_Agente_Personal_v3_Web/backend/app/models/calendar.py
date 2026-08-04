from pydantic import BaseModel


class EventoOut(BaseModel):
    resumen: str
    inicio: str
    fin: str


class EventoIn(BaseModel):
    fecha: str = ""
    hora_inicio: str
    hora_fin: str
    resumen: str
    descripcion: str = ""
