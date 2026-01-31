# app/main.py
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from app.api.routes import meteo, stats, admin
from app.core.config import settings
from app.utils.logger import logger
from app.services.collect import run_collection

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API de gestion des données météo UEMOA",
    version="0.1.0",
)

# Inclusion des routers
app.include_router(meteo.router, prefix=settings.API_V1_STR + "/meteo", tags=["meteo"])
app.include_router(stats.router, prefix=settings.API_V1_STR + "/stats", tags=["stats"])
app.include_router(admin.router, prefix=settings.API_V1_STR + "/admin", tags=["admin"])


@app.get("/")
def read_root():
    return {"message": f"Bienvenue sur {settings.PROJECT_NAME}"}


@app.post("/trigger-collect", response_model=dict)
def trigger_collect():
    try:
        result = run_collection()
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.on_event("startup")
async def startup_event():
    logger.info("API démarrée")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API arrêtée")