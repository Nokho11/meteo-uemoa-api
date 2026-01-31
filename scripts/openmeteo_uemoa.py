import requests
import pandas as pd
from datetime import datetime, timedelta
import time


# === Configuration générale ===
start_date = "2025-01-01"
end_date = datetime.now().strftime("%Y-%m-%d")



# === Liste des pays à inclure (laisser vide pour tout)
pays_selectionnes = []  

# === Villes UEMOA (80 villes, 10 par pays)
villes_uemoa = {
    "Sénégal": [
        {"ville": "Dakar", "lat": 14.7167, "lon": -17.4677},
        {"ville": "Saint-Louis", "lat": 16.0333, "lon": -16.5000},
        {"ville": "Thiès", "lat": 14.7833, "lon": -16.9333},
        {"ville": "Kaolack", "lat": 14.1500, "lon": -16.1000},
        {"ville": "Ziguinchor", "lat": 12.5833, "lon": -16.2667},
        {"ville": "Tambacounda", "lat": 13.7667, "lon": -13.6667},
        {"ville": "Kolda", "lat": 12.8833, "lon": -14.9500},
        {"ville": "Louga", "lat": 15.6167, "lon": -16.2167},
        {"ville": "Mbour", "lat": 14.4200, "lon": -16.9600},
        {"ville": "Fatick", "lat": 14.3333, "lon": -16.4167}
    ],
    "Bénin": [
        {"ville": "Cotonou", "lat": 6.3667, "lon": 2.4333},
        {"ville": "Porto-Novo", "lat": 6.4969, "lon": 2.6283},
        {"ville": "Parakou", "lat": 9.3372, "lon": 2.6300},
        {"ville": "Djougou", "lat": 9.7085, "lon": 1.6654},
        {"ville": "Abomey", "lat": 7.1825, "lon": 1.9911},
        {"ville": "Bohicon", "lat": 7.1783, "lon": 2.0667},
        {"ville": "Natitingou", "lat": 10.3042, "lon": 1.3796},
        {"ville": "Kandi", "lat": 11.1287, "lon": 2.9388},
        {"ville": "Lokossa", "lat": 6.6380, "lon": 1.7167},
        {"ville": "Savé", "lat": 8.0333, "lon": 2.4833}
    ],
    "Burkina Faso": [
        {"ville": "Ouagadougou", "lat": 12.3600, "lon": -1.5300},
        {"ville": "Bobo-Dioulasso", "lat": 11.1833, "lon": -4.2833},
        {"ville": "Koudougou", "lat": 12.2500, "lon": -2.3667},
        {"ville": "Banfora", "lat": 10.6333, "lon": -4.7667},
        {"ville": "Ouahigouya", "lat": 13.5667, "lon": -2.4167},
        {"ville": "Dédougou", "lat": 12.4667, "lon": -3.4667},
        {"ville": "Tenkodogo", "lat": 11.7833, "lon": -0.3667},
        {"ville": "Houndé", "lat": 11.5000, "lon": -3.5167},
        {"ville": "Kaya", "lat": 13.0833, "lon": -1.0833},
        {"ville": "Fada N'gourma", "lat": 12.0500, "lon": 0.3667}
    ],
    "Côte d’Ivoire": [
        {"ville": "Abidjan", "lat": 5.3364, "lon": -4.0267},
        {"ville": "Yamoussoukro", "lat": 6.8161, "lon": -5.2742},
        {"ville": "Bouaké", "lat": 7.6833, "lon": -5.0333},
        {"ville": "Daloa", "lat": 6.8833, "lon": -6.4500},
        {"ville": "Korhogo", "lat": 9.4500, "lon": -5.6333},
        {"ville": "Man", "lat": 7.4125, "lon": -7.5536},
        {"ville": "San Pedro", "lat": 4.7485, "lon": -6.6363},
        {"ville": "Divo", "lat": 5.8333, "lon": -5.3667},
        {"ville": "Gagnoa", "lat": 6.1333, "lon": -5.9500},
        {"ville": "Abengourou", "lat": 6.7304, "lon": -3.4964}
    ],
    "Mali": [
        {"ville": "Bamako", "lat": 12.6392, "lon": -8.0029},
        {"ville": "Sikasso", "lat": 11.3167, "lon": -5.6667},
        {"ville": "Kayes", "lat": 14.4500, "lon": -11.4167},
        {"ville": "Ségou", "lat": 13.4333, "lon": -6.2667},
        {"ville": "Mopti", "lat": 14.4833, "lon": -4.1833},
        {"ville": "Koutiala", "lat": 12.3833, "lon": -5.4667},
        {"ville": "Gao", "lat": 16.2667, "lon": -0.0500},
        {"ville": "Tombouctou", "lat": 16.7735, "lon": -3.0074},
        {"ville": "Kidal", "lat": 18.4411, "lon": 1.4078},
        {"ville": "San", "lat": 13.3000, "lon": -4.9000}
    ],
    "Niger": [
        {"ville": "Niamey", "lat": 13.5128, "lon": 2.1128},
        {"ville": "Zinder", "lat": 13.8000, "lon": 8.9833},
        {"ville": "Maradi", "lat": 13.5000, "lon": 7.1000},
        {"ville": "Agadez", "lat": 16.9733, "lon": 7.9911},
        {"ville": "Tahoua", "lat": 14.8888, "lon": 5.2654},
        {"ville": "Dosso", "lat": 13.0500, "lon": 3.2000},
        {"ville": "Diffa", "lat": 13.3154, "lon": 12.6114},
        {"ville": "Tillabéri", "lat": 14.2137, "lon": 1.4572},
        {"ville": "Tessaoua", "lat": 13.7550, "lon": 7.9867},
        {"ville": "Birni N’Konni", "lat": 13.7904, "lon": 5.2599}
    ],
    "Guinée-Bissau": [
        {"ville": "Bissau", "lat": 11.8600, "lon": -15.5984},
        {"ville": "Bafata", "lat": 12.1658, "lon": -14.6617},
        {"ville": "Gabu", "lat": 12.2833, "lon": -14.2167},
        {"ville": "Bissora", "lat": 12.0000, "lon": -15.3167},
        {"ville": "Buba", "lat": 11.5833, "lon": -15.0000},
        {"ville": "Cacheu", "lat": 12.2667, "lon": -16.1667},
        {"ville": "Catió", "lat": 11.2833, "lon": -15.1667},
        {"ville": "Quinhámel", "lat": 11.8833, "lon": -15.8667},
        {"ville": "Mansôa", "lat": 12.0481, "lon": -15.3186},
        {"ville": "Bolama", "lat": 11.5808, "lon": -15.4761}
    ],
    "Togo": [
        {"ville": "Lomé", "lat": 6.1319, "lon": 1.2228},
        {"ville": "Sokodé", "lat": 8.9833, "lon": 1.1333},
        {"ville": "Kara", "lat": 9.5511, "lon": 1.1861},
        {"ville": "Atakpamé", "lat": 7.5333, "lon": 1.1333},
        {"ville": "Dapaong", "lat": 10.8667, "lon": 0.2500},
        {"ville": "Tchamba", "lat": 9.0333, "lon": 1.4167},
        {"ville": "Aného", "lat": 6.2333, "lon": 1.6000},
        {"ville": "Tsévié", "lat": 6.4261, "lon": 1.2133},
        {"ville": "Kpalimé", "lat": 6.9000, "lon": 0.6333},
        {"ville": "Notsé", "lat": 6.9500, "lon": 1.1667}
    ]
}

# === Requête
base_url = "https://archive-api.open-meteo.com/v1/archive"
params_template = {
    "start_date": start_date,
    "end_date": end_date,
    "daily": [
        "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
        "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean",
        "dew_point_2m_mean", "precipitation_sum", "precipitation_hours",
        "wind_gusts_10m_max", "wind_speed_10m_max", "wind_direction_10m_dominant",
        "sunshine_duration", "shortwave_radiation_sum", "et0_fao_evapotranspiration",
        "weathercode"
    ],
    "timezone": "Africa/Abidjan"
}

column_mapping = {
    "temperature_2m_max": "tempmax",
    "temperature_2m_min": "tempmin",
    "temperature_2m_mean": "temp",
    "apparent_temperature_max": "feelslikemax",
    "apparent_temperature_min": "feelslikemin",
    "apparent_temperature_mean": "feelslike",
    "dew_point_2m_mean": "dew",
    "precipitation_sum": "precip",
    "precipitation_hours": "precipcover",
    "wind_gusts_10m_max": "windgust",
    "wind_speed_10m_max": "windspeed",
    "wind_direction_10m_dominant": "winddir",
    "sunshine_duration": "solarradiation",
    "shortwave_radiation_sum": "solarenergy",
    "et0_fao_evapotranspiration": "uvindex",
    "weathercode": "conditions"
}

toutes_donnees = []

for pays, villes in villes_uemoa.items():
    if pays_selectionnes and pays not in pays_selectionnes:
        continue
    for ville_info in villes:
        ville = ville_info["ville"]
        lat = ville_info["lat"]
        lon = ville_info["lon"]
        print(f"🔄 Téléchargement : {ville}, {pays}")
        try:
            params = params_template.copy()
            params["latitude"] = lat
            params["longitude"] = lon
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
             df = pd.DataFrame(response.json()["daily"])
             df = df.rename(columns=column_mapping)
             df["datetime"] = df["time"]
             df["Ville"] = ville
             df["Pays"] = pays
             df["latitude"] = lat
             df["longitude"] = lon
             toutes_donnees.append(df)

            elif response.status_code == 429:
                print(f"🚫 Trop de requêtes pour {ville} (429).")
            else:
                print(f"❌ Échec {ville} ({response.status_code})")
        except Exception as e:
            print(f"⚠️ Erreur {ville} : {e}")
        time.sleep(1.5)

if not toutes_donnees:
    print("🚫 Aucune donnée collectée.")
    sys.exit(1)

df_final = pd.concat(toutes_donnees, ignore_index=True)
df_final.to_csv("historique_meteo_uemoa_80villes.csv", index=False)
print("✅ CSV enregistré avec données")

