from fastapi import APIRouter, Depends

from app.deps import get_v2

router = APIRouter(tags=["health"])


@router.get("/health")
def health(v2=Depends(get_v2)):
    return {
        "status": "ok",
        "agent_model": v2.AGENT_MODEL,
        "credenciales_calendar": v2.RUTA_CREDENCIALES.exists(),
        "token_calendar": v2.RUTA_TOKEN.exists(),
    }
