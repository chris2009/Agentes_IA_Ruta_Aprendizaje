from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGINS, v2mod
from app.routers import activities, calendar, chat, files, health, plans


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not v2mod.RUTA_CREDENCIALES.exists():
        print(f"AVISO: no se encontro {v2mod.RUTA_CREDENCIALES}. Las tools de Calendar fallaran hasta configurarlo.")

    yield


app = FastAPI(
    title="Agente Personal de Planificacion — API",
    description="Backend web (v3) sobre el agente v2 (agente_planificacion_actividades.py).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(activities.router, prefix="/api")
app.include_router(calendar.router, prefix="/api")
app.include_router(plans.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
