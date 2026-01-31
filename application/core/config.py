# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "Meteo UEMOA API"
    API_V1_STR: str = "/api/v1"
    
    # Dossiers
    DATA_DIR: str = str(BASE_DIR / "data")
    RESULTATS_DIR: str = str(BASE_DIR / "resultats")
    
    # Base de données PostgreSQL (adapte selon ton setup)
    DATABASE_URL: str = "postgresql+psycopg2://postgres:@localhost:5432/entrepot_uemoa"
    
    # Chemins des fichiers CSV (tu peux les changer plus tard)
    RAW_CSV_PATH: str = str(BASE_DIR / "data" / "historique_meteo_uemoa_80villes.csv")
    CLEAN_CSV_PATH: str = str(BASE_DIR / "data" / "historique_meteo_uemoa_80villes_clean.csv")
    
    model_config = SettingsConfigDict(
        env_file=".env",          # optionnel : tu pourras ajouter un .env plus tard
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()
