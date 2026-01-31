import pandas as pd
import logging
from datetime import datetime

# === Configuration du logging ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === Configuration des fichiers ===
input_csv = "/Users/NOKHO/Desktop/Meteo/historique_meteo_uemoa_80villes.csv"
output_csv = "/Users/NOKHO/Desktop/Meteo/historique_meteo_uemoa_80villes_clean.csv"

# === Nettoyage des données ===
def nettoyer_donnees(df):
    """
    Nettoie et transforme les données météorologiques
    """
    logging.info("⏳ Conversion des dates...")
    df['datetime'] = pd.to_datetime(df['datetime'])

    weather_codes = {
        0: 'Ensoleillé', 1: 'Principalement clair', 2: 'Partiellement nuageux', 3: 'Couvert',
        45: 'Brouillard', 48: 'Brouillard givrant', 51: 'Bruine légère', 53: 'Bruine modérée',
        55: 'Bruine dense', 56: 'Bruine verglaçante légère', 57: 'Bruine verglaçante dense',
        61: 'Pluie légère', 63: 'Pluie modérée', 65: 'Pluie forte', 66: 'Pluie verglaçante légère',
        67: 'Pluie verglaçante forte', 71: 'Chute de neige légère', 73: 'Chute de neige modérée',
        75: 'Chute de neige forte', 77: 'Grains de neige', 80: 'Averses de pluie légères',
        81: 'Averses de pluie modérées', 82: 'Averses de pluie violentes', 85: 'Averses de neige légères',
        86: 'Averses de neige fortes', 95: 'Orage léger ou modéré', 96: 'Orage avec grêle légère',
        99: 'Orage avec grêle forte'
    }

    logging.info("🧠 Normalisation des conditions météo (codes ou texte)...")

    def normaliser_condition(val):
        try:
            code = int(float(val))
            return weather_codes.get(code, 'Inconnu')
        except:
            return str(val).strip().capitalize() if pd.notnull(val) else 'Inconnu'

    df['conditions'] = df['conditions'].apply(normaliser_condition)

    logging.info("💨 Conversion des vitesses du vent en km/h...")
    df['windspeed'] = df['windspeed'] * 3.6
    df['windgust'] = df['windgust'] * 3.6

    logging.info("☁️ Estimation de la couverture nuageuse...")
    def cloud_cover_from_weathercode(x):
        if x in ['Ensoleillé', 'Principalement clair']: return 0.2
        elif x == 'Partiellement nuageux': return 0.5
        elif x == 'Couvert': return 0.8
        elif x in ['Brouillard', 'Brouillard givrant']: return 1.0
        else: return 0.6
    df['cloudcover'] = df['conditions'].apply(cloud_cover_from_weathercode)

    logging.info("📏 Arrondi des colonnes numériques...")
    numeric_cols = ['tempmax', 'tempmin', 'temp', 'feelslikemax', 'feelslikemin',
                    'feelslike', 'dew', 'precip', 'windgust', 'windspeed',
                    'solarradiation', 'solarenergy', 'uvindex']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].round(2)

    cols_order = ['datetime', 'Pays', 'Ville', 'latitude', 'longitude', 'temp', 'tempmax', 'tempmin',
                  'feelslike', 'feelslikemax', 'feelslikemin', 'dew', 'humidity', 'precip',
                  'precipcover', 'windgust', 'windspeed', 'winddir', 'cloudcover',
                  'solarradiation', 'solarenergy', 'uvindex', 'conditions']
    cols_order = [col for col in cols_order if col in df.columns]

    return df[cols_order]

# === Script principal ===
if __name__ == "__main__":
    logging.info("🚀 Début du processus de nettoyage")

    try:
        logging.info(f"📂 Chargement du fichier : {input_csv}")
        df = pd.read_csv(input_csv)
        logging.info(f"✅ Fichier chargé avec {len(df)} lignes")
    except Exception as e:
        logging.error(f"❌ Erreur lors du chargement du fichier CSV : {e}")
        exit(1)

    try:
        logging.info("🧹 Nettoyage en cours...")
        df_clean = nettoyer_donnees(df)
        df_clean.to_csv(output_csv, index=False)
        logging.info(f"✅ Données nettoyées et sauvegardées dans {output_csv}")
    except Exception as e:
        logging.error(f"❌ Erreur lors du nettoyage : {e}")
        exit(1)

    logging.info("🎉 Nettoyage terminé avec succès.")
