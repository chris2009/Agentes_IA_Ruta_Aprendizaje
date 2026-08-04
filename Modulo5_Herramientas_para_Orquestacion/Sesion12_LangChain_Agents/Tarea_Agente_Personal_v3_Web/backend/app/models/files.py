from pydantic import BaseModel


class FileEntry(BaseModel):
    nombre: str
    es_carpeta: bool
    ruta_relativa: str
    extension_admitida: bool


class FileBrowseOut(BaseModel):
    ruta_actual: str
    entradas: list[FileEntry]
