from fastapi import APIRouter

# Créer le router pour ce fichier
router = APIRouter()

# Endpoint simple pour tester
@router.get("/")
def get_stats():
    return {"message": "Stats API — ici on mettra les statistiques météo"}

