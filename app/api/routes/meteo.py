from fastapi import APIRouter
from app.services.collect import collect_data

router = APIRouter()

# Endpoint pour toutes les données
@router.get("/")
def get_all_meteo():
    return collect_data()

# Endpoint pour une ville spécifique
@router.get("/ville/{Dakar}")
def get_meteo_ville(Dakar: str):
    data = collect_data()
    # Filtrer la ville demandée
    ville_data = [d for d in data if d["ville"].lower() == Dakar.lower()]
    return ville_data
