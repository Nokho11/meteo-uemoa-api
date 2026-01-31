import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta
import logging

# === Configuration de la base de données ===
DB_CONFIG = {
    'dbname': 'entrepot_uemoa',
    'user': 'postgres',
    'password': '    ',  # 🔐 À personnaliser
    'host': 'localhost',
    'port': '5432'
}

# === Fichier d'entrée ===
INPUT_CSV = "/Users/NOKHO/Desktop/Meteo/historique_meteo_uemoa_80villes_clean.csv"

# === Configuration du logging ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_float(value):
    """Convertit une valeur en float ou retourne None si invalide"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def initialiser_dim_date(conn):
    """Initialise la table dim_date pour l'année 2025"""
    try:
        logger.info("🔁 Vérification de la table dim_date...")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dim_date WHERE annee = 2025")
        if cursor.fetchone()[0] > 0:
            logger.info("✅ La table dim_date est déjà peuplée pour 2025")
            return

        logger.info("📅 Génération des dates de 2025...")
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append((
                current_date.date(),
                current_date.day,
                current_date.month,
                current_date.year,
                current_date.strftime('%A')
            ))
            current_date += timedelta(days=1)

        logger.info("💾 Insertion dans dim_date...")
        execute_batch(cursor, """
            INSERT INTO dim_date (date, jour, mois, annee, nom_jour)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (date) DO NOTHING
        """, dates)
        conn.commit()
        logger.info(f"✅ Table dim_date initialisée avec {len(dates)} lignes")

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erreur initialisation dim_date : {e}", exc_info=True)
        raise

def charger_donnees():
    """Charge les données nettoyées dans le schéma en étoile"""
    conn = None
    try:
        logger.info("🔗 Connexion à PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)

        # Initialiser dim_date
        initialiser_dim_date(conn)

        # Charger le CSV nettoyé
        logger.info(f"📂 Chargement du fichier {INPUT_CSV}...")
        df = pd.read_csv(INPUT_CSV)
        df['datetime'] = pd.to_datetime(df['datetime'])
        logger.info(f"✅ {len(df)} lignes chargées depuis le fichier")

        # Remplissage de dim_lieu avec gestion des doublons
        logger.info("🌍 Chargement des lieux dans dim_lieu...")
        with conn.cursor() as cursor:
            # Vérification des lieux existants
            cursor.execute("SELECT ville, pays FROM dim_lieu")
            lieux_existants = set((ville, pays) for (ville, pays) in cursor.fetchall())
            
            lieux_uniques = df[['Ville', 'Pays', 'latitude', 'longitude']].drop_duplicates()
            nouveaux_lieux = []
            
            for _, row in lieux_uniques.iterrows():
                ville = str(row['Ville'])
                pays = str(row['Pays'])
                
                if (ville, pays) not in lieux_existants:
                    nouveaux_lieux.append((
                        ville,
                        pays,
                        safe_float(row['latitude']),
                        safe_float(row['longitude'])
                    ))
            
            if nouveaux_lieux:
                execute_batch(cursor, """
                    INSERT INTO dim_lieu (ville, pays, latitude, longitude)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (ville, pays) DO UPDATE SET
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude
                """, nouveaux_lieux)
                logger.info(f"✅ {len(nouveaux_lieux)} nouveaux lieux insérés/mis à jour")
            else:
                logger.info("✅ Aucun nouveau lieu à insérer")
            conn.commit()

        # Remplissage de dim_conditions avec gestion des doublons
        logger.info("⛅ Chargement des conditions météo dans dim_conditions...")
        with conn.cursor() as cursor:
            # Vérification des conditions existantes
            cursor.execute("SELECT conditions FROM dim_conditions")
            conditions_existantes = set(condition for (condition,) in cursor.fetchall())
            
            conditions_uniques = df['conditions'].dropna().unique()
            nouvelles_conditions = []
            
            for condition in conditions_uniques:
                condition_str = str(condition)
                if condition_str not in conditions_existantes:
                    nouvelles_conditions.append((condition_str,))
            
            if nouvelles_conditions:
                execute_batch(cursor, """
                    INSERT INTO dim_conditions (conditions)
                    VALUES (%s)
                    ON CONFLICT (conditions) DO NOTHING
                """, nouvelles_conditions)
                logger.info(f"✅ {len(nouvelles_conditions)} nouvelles conditions insérées")
            else:
                logger.info("✅ Aucune nouvelle condition à insérer")
            conn.commit()

        # Remplissage de faits_meteo avec upsert
        logger.info("📈 Insertion des données dans faits_meteo...")
        with conn.cursor() as cursor:
            # Récupérer les mappings
            cursor.execute("SELECT id_dim_lieu, ville, pays FROM dim_lieu")
            lieux_map = {(ville, pays): id_lieu for (id_lieu, ville, pays) in cursor.fetchall()}

            cursor.execute("SELECT id_dim_condition, conditions FROM dim_conditions")
            conditions_map = {condition: id_cond for (id_cond, condition) in cursor.fetchall()}

            # Préparer les données
            data_faits = []
            for _, row in df.iterrows():
                id_lieu = lieux_map.get((str(row['Ville']), str(row['Pays'])))
                id_condition = conditions_map.get(str(row['conditions'])) if pd.notna(row['conditions']) else None

                if id_lieu and id_condition:
                    data_faits.append((
                        row['datetime'].date(),
                        id_lieu,
                        id_condition,
                        safe_float(row.get('temp')),
                        safe_float(row.get('tempmax')),
                        safe_float(row.get('tempmin')),
                        safe_float(row.get('feelslike')),
                        safe_float(row.get('feelslikemax')),
                        safe_float(row.get('feelslikemin')),
                        safe_float(row.get('dew')),
                        safe_float(row.get('precip')),
                        safe_float(row.get('precipcover')),
                        safe_float(row.get('windgust')),
                        safe_float(row.get('windspeed')),
                        safe_float(row.get('winddir')),
                        safe_float(row.get('cloudcover')),
                        safe_float(row.get('solarradiation')),
                        safe_float(row.get('solarenergy')),
                        safe_float(row.get('uvindex'))
                    ))

            if data_faits:
                execute_batch(cursor, """
                    INSERT INTO faits_meteo (
                        datecollect, id_dim_lieu, id_dim_condition, temp, tempmax, tempmin,
                        feelslike, feelslikemax, feelslikemin, dew, precip,
                        precipcover, windgust, windspeed, winddir, cloudcover,
                        solarradiation, solarenergy, uvindex
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (datecollect, id_dim_lieu) DO UPDATE SET
                        id_dim_condition = EXCLUDED.id_dim_condition,
                        temp = EXCLUDED.temp,
                        tempmax = EXCLUDED.tempmax,
                        tempmin = EXCLUDED.tempmin,
                        feelslike = EXCLUDED.feelslike,
                        feelslikemax = EXCLUDED.feelslikemax,
                        feelslikemin = EXCLUDED.feelslikemin,
                        dew = EXCLUDED.dew,
                        precip = EXCLUDED.precip,
                        precipcover = EXCLUDED.precipcover,
                        windgust = EXCLUDED.windgust,
                        windspeed = EXCLUDED.windspeed,
                        winddir = EXCLUDED.winddir,
                        cloudcover = EXCLUDED.cloudcover,
                        solarradiation = EXCLUDED.solarradiation,
                        solarenergy = EXCLUDED.solarenergy,
                        uvindex = EXCLUDED.uvindex
                """, data_faits, page_size=1000)
                logger.info(f"✅ {len(data_faits)} observations insérées/mises à jour dans faits_meteo")
            else:
                logger.info("✅ Aucune nouvelle observation à insérer")
            conn.commit()

        logger.info("🎉 Chargement des données terminé avec succès.")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Erreur lors du chargement : {e}", exc_info=True)
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    charger_donnees()
