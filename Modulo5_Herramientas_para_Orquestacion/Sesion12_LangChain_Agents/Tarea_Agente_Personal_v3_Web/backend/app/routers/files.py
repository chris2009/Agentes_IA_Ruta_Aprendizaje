from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_v2
from app.models.files import FileBrowseOut

router = APIRouter(prefix="/files", tags=["files"])


def _resolver_dentro_de_carpeta_autorizada(path: str, v2) -> Path | None:
    """
    Resuelve `path` como una ruta relativa a CARPETA_AUTORIZADA (que es la
    convencion que usa este router: `ruta_relativa` en las entradas del
    listado ya viene relativa a CARPETA_AUTORIZADA, no a la carpeta de v2).

    No reutiliza v2._validar_ruta porque esa funcion resuelve rutas
    relativas al archivo de v2 (pensada para el campo `ruta_contexto` de
    actividades.json, que incluye el prefijo "materiales/"), un ancla
    distinta a la que usa este endpoint.
    """

    base = v2.CARPETA_AUTORIZADA.resolve()
    ruta_resuelta = (base / path).resolve()

    if ruta_resuelta == base or base in ruta_resuelta.parents:
        return ruta_resuelta

    return None


@router.get("/browse", response_model=FileBrowseOut)
def explorar(path: str = "", v2=Depends(get_v2)):
    if not path:
        carpeta = v2.CARPETA_AUTORIZADA
        ruta_relativa_actual = ""
    else:
        carpeta = _resolver_dentro_de_carpeta_autorizada(path, v2)

        if carpeta is None:
            raise HTTPException(status_code=403, detail="La ruta esta fuera de la carpeta autorizada.")

        ruta_relativa_actual = path

    if not carpeta.is_dir():
        raise HTTPException(status_code=404, detail=f"'{path}' no es una carpeta.")

    entradas = []

    for item in sorted(carpeta.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        ruta_rel = str(item.relative_to(v2.CARPETA_AUTORIZADA)).replace("\\", "/")
        entradas.append({
            "nombre": item.name,
            "es_carpeta": item.is_dir(),
            "ruta_relativa": ruta_rel,
            "extension_admitida": item.is_file() and item.suffix.lower() in v2.EXTENSIONES_ADMITIDAS,
        })

    return {"ruta_actual": ruta_relativa_actual, "entradas": entradas}
