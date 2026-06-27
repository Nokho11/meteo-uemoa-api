# Meteo UEMOA API

API de surveillance météorologique pour la zone UEMOA, développée avec FastAPI et Python.

## Objectif

Fournir un système de monitoring météorologique pour les pays de l'Union Economique et Monétaire Ouest-Africaine (UEMOA), avec des endpoints RESTful pour accéder aux données climatiques par région.

## Technologies

| Technologie | Usage |
|-------------|-------|
| Python 3.x  | Langage principal |
| FastAPI     | Framework API REST |
| Uvicorn     | Serveur ASGI |
| Pandas      | Traitement des données |

## Lancer le projet

git clone https://github.com/Nokho11/meteo-uemoa-api.git
cd meteo-uemoa-api
pip install -r requirements.txt
uvicorn main:app --reload

L'API sera disponible sur http://localhost:8000
Documentation interactive : http://localhost:8000/docs

## Auteure

**Ndeye Sokhna Nokho** — [Portfolio](https://portfolio-nsn.netlify.app) · [LinkedIn](https://www.linkedin.com/in/ndeye-sokhna-n-02327b373)

---
*Projet réalisé dans le cadre de ma certification en Data Engineering 
