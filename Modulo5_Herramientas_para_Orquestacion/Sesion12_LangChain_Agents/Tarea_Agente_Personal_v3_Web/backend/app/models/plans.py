from pydantic import BaseModel


class PlanGenerateIn(BaseModel):
    fecha: str = ""
    hora_inicio: str
    hora_fin: str


class PlanListItem(BaseModel):
    nombre_archivo: str
    fecha_generacion: str
    url_descarga: str


class PlanContenidoOut(BaseModel):
    nombre_archivo: str
    contenido: str
