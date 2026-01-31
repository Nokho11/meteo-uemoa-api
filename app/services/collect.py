# app/api/routes/meteo.py
from fastapi import APIRouter
from app.services.collect import run_collection  # <- on importe la bonne fonction
from app.utils.logger import logger

router = APIRouter(
    prefix="/meteo",
    tags=["Météo"]
)

@router.get("/collect")
async def collect_meteo():
    """
    Endpoint pour lancer la collecte des données météo.
    """
    try:
        logger.info("Endpoint /meteo/collect appelé")
        result = run_collection()  # <- on utilise la fonction correcte
        return result
    except Exception as e:
        logger.error(f"Erreur endpoint /meteo/collect : {e}")
        return {"status": "error", "message": str(e)}
