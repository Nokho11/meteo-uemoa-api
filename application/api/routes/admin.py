from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_admin():
    return {"message": "Admin API — ici on mettra les fonctions admin"}
