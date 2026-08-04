from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.deps import get_v2
from app.models.plans import PlanContenidoOut, PlanGenerateIn, PlanListItem

router = APIRouter(prefix="/plans", tags=["plans"])


def _validar_nombre_plan(nombre_archivo: str, v2) -> Path:
    """Evita path traversal: solo acepta nombres de archivo simples dentro de CARPETA_PLANES."""

    ruta = (v2.CARPETA_PLANES / nombre_archivo).resolve()

    if ruta.parent != v2.CARPETA_PLANES.resolve() or ruta.suffix != ".md":
        raise HTTPException(status_code=400, detail="Nombre de archivo de plan invalido.")

    if not ruta.exists():
        raise HTTPException(status_code=404, detail=f"No existe el plan '{nombre_archivo}'.")

    return ruta


@router.post("/generate")
def generar_plan(datos: PlanGenerateIn, v2=Depends(get_v2)):
    mensaje = v2.generar_plan.invoke(datos.model_dump())
    return {"mensaje": mensaje}


@router.get("", response_model=list[PlanListItem])
def listar_planes(v2=Depends(get_v2)):
    v2.CARPETA_PLANES.mkdir(exist_ok=True)
    archivos = sorted(v2.CARPETA_PLANES.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)

    return [
        {
            "nombre_archivo": archivo.name,
            "fecha_generacion": v2.datetime.fromtimestamp(archivo.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "url_descarga": f"/api/plans/{archivo.name}/download",
        }
        for archivo in archivos
    ]


@router.get("/{nombre_archivo}", response_model=PlanContenidoOut)
def obtener_plan(nombre_archivo: str, v2=Depends(get_v2)):
    ruta = _validar_nombre_plan(nombre_archivo, v2)
    return {"nombre_archivo": nombre_archivo, "contenido": ruta.read_text(encoding="utf-8")}


@router.get("/{nombre_archivo}/download")
def descargar_plan(nombre_archivo: str, v2=Depends(get_v2)):
    ruta = _validar_nombre_plan(nombre_archivo, v2)
    return FileResponse(ruta, media_type="text/markdown", filename=nombre_archivo)
