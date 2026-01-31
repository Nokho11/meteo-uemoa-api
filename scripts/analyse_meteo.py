import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import logging
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats

# ====================
# CONFIGURATION INITIALE
# ====================

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('analyse_meteo.log')
    ]
)
logger = logging.getLogger(__name__)

# Création du dossier de résultats
OUTPUT_DIR = f"resultats_meteo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(OUTPUT_DIR, exist_ok=True)
logger.info(f"Dossier de résultats créé : {OUTPUT_DIR}")

# Configuration des graphiques
def configurer_graphiques():
    """Configure les paramètres par défaut des graphiques"""
    plt.style.use('ggplot')
    sns.set(style="whitegrid", palette="husl")
    plt.rcParams.update({
        'figure.figsize': (12, 7),
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'figure.dpi': 100
    })

configurer_graphiques()

# ====================
# CHARGEMENT DES DONNÉES
# ====================

def charger_donnees(chemin):
    """Charge et nettoie les données météo"""
    try:
        logger.info(f"Chargement des données depuis {chemin}")
        df = pd.read_csv(chemin, parse_dates=['datetime'])
        
        # Renommage des colonnes
        df = df.rename(columns={
            'datetime': 'Date',
            'temp': 'Température',
            'tempmax': 'Température_max',
            'tempmin': 'Température_min',
            'precip': 'Précipitations',
            'latitude': 'Lat',
            'longitude': 'Lon'
        })
        
        # Nettoyage des données
        df_clean = df.dropna(subset=['Température', 'Précipitations']).copy()
        logger.info(f"Données chargées avec succès. {len(df_clean)} lignes après nettoyage.")
        
        return df_clean
    
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données : {e}")
        raise

# ====================
# FONCTIONS UTILITAIRES
# ====================

def afficher_et_sauvegarder(fig, nom_fichier):
    """
    Affiche et sauvegarde un graphique
    Args:
        fig: Figure matplotlib
        nom_fichier: Nom du fichier de sortie (sans extension)
    """
    try:
        chemin_complet = os.path.join(OUTPUT_DIR, f"{nom_fichier}.png")
        fig.tight_layout()
        fig.savefig(chemin_complet, dpi=300, bbox_inches='tight')
        logger.info(f"Graphique sauvegardé : {chemin_complet}")
        plt.show()
        plt.close(fig)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du graphique {nom_fichier} : {e}")

# ====================
# ANALYSE EXPLORATOIRE
# ====================

def analyser_donnees(df):
    """Effectue l'analyse exploratoire des données"""
    
    logger.info("Début de l'analyse exploratoire")
    
    # 1. Aperçu des données
    logger.info("\nAperçu des données :")
    logger.info(df.head().to_string())
    
    logger.info("\nStatistiques descriptives :")
    logger.info(df[['Température', 'Précipitations']].describe().to_string())
    
    # 2. Distribution des températures
    fig1, ax1 = plt.subplots()
    sns.histplot(df['Température'], bins=30, kde=True, color='royalblue', ax=ax1)
    ax1.set_title("Distribution des Températures dans l'UEMOA")
    ax1.set_xlabel("Température (°C)")
    ax1.set_ylabel("Fréquence")
    afficher_et_sauvegarder(fig1, "distribution_temperatures")
    
    # 3. Températures par pays
    temp_pays = df.groupby('Pays')['Température'].mean().sort_values()
    
    fig2, ax2 = plt.subplots()
    temp_pays.plot(kind='bar', color=sns.color_palette("coolwarm", len(temp_pays)), ax=ax2)
    ax2.set_title("Température Moyenne par Pays")
    ax2.set_ylabel("Température moyenne (°C)")
    ax2.tick_params(axis='x', rotation=45)
    afficher_et_sauvegarder(fig2, "temperature_par_pays")
    
    # 4. Corrélations
    corr_matrix = df[['Température', 'Température_max', 'Température_min', 'Précipitations']].corr()
    
    fig3, ax3 = plt.subplots()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                annot_kws={"size": 12}, fmt=".2f", linewidths=.5, ax=ax3)
    ax3.set_title("Matrice de Corrélation des Variables Météo")
    afficher_et_sauvegarder(fig3, "matrice_correlation")
    
    # 5. Analyse temporelle
    df['Mois'] = df['Date'].dt.month
    temp_mois = df.groupby('Mois')['Température'].mean()
    
    fig4, ax4 = plt.subplots()
    temp_mois.plot(kind='line', marker='o', ax=ax4)
    ax4.set_title("Variation Mensuelle des Températures")
    ax4.set_xlabel("Mois")
    ax4.set_ylabel("Température Moyenne (°C)")
    ax4.set_xticks(range(1,13))
    ax4.set_xticklabels(['Jan','Fév','Mar','Avr','Mai','Jun',
                         'Jul','Aoû','Sep','Oct','Nov','Déc'])
    afficher_et_sauvegarder(fig4, "variation_mensuelle_temp")

# ====================
# ANALYSE STATISTIQUE
# ====================

def analyser_correlations(df):
    """Effectue les analyses statistiques"""
    logger.info("\nAnalyse des corrélations")
    
    # Test de Pearson
    corr, pval = stats.pearsonr(df['Température'], df['Précipitations'])
    logger.info(f"Corrélation Pearson Température/Précipitations:")
    logger.info(f"- Coefficient: {corr:.3f}")
    logger.info(f"- P-value: {pval:.4f}")
    logger.info("- Interprétation: " + ("Corrélation significative" if pval < 0.05 else "Pas de corrélation significative"))

# ====================
# MACHINE LEARNING
# ====================

def appliquer_ml(df):
    """Applique les algorithmes de machine learning"""
    logger.info("\nApplication des algorithmes de Machine Learning")
    
    # 1. Clustering K-Means
    logger.info("\nClustering K-Means")
    X_cluster = df[['Température', 'Précipitations']].values
    
    # Méthode du coude
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
        kmeans.fit(X_cluster)
        wcss.append(kmeans.inertia_)
    
    fig5, ax5 = plt.subplots()
    ax5.plot(range(1, 11), wcss, marker='o', linestyle='--')
    ax5.set_title('Méthode du Coude pour Déterminer k Optimal')
    ax5.set_xlabel('Nombre de clusters')
    ax5.set_ylabel('WCSS')
    afficher_et_sauvegarder(fig5, "methode_coude")
    
    # Clustering avec k=3
    kmeans = KMeans(n_clusters=3, init='k-means++', random_state=42)
    clusters = kmeans.fit_predict(X_cluster)
    df['Cluster'] = clusters
    
    fig6, ax6 = plt.subplots()
    sns.scatterplot(data=df, x='Température', y='Précipitations', 
                    hue='Cluster', palette='viridis', s=100, alpha=0.7, ax=ax6)
    ax6.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], 
                s=300, c='red', marker='X', label='Centroïdes')
    ax6.set_title("Clustering des Conditions Météorologiques (K=3)")
    ax6.set_xlabel("Température (°C)")
    ax6.set_ylabel("Précipitations (mm)")
    ax6.legend(title='Cluster')
    afficher_et_sauvegarder(fig6, "clustering_kmeans")
    
    # 2. Régression Linéaire
    logger.info("\nRégression Linéaire")
    X_reg = df[['Précipitations']].values
    y_reg = df['Température_max'].values
    
    # Séparation train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )
    
    # Entraînement
    reg = LinearRegression()
    reg.fit(X_train, y_train)
    
    # Prédiction et évaluation
    y_pred = reg.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    logger.info("Performance du modèle (sur le jeu de test):")
    logger.info(f"- RMSE: {rmse:.2f}")
    logger.info(f"- R²: {r2:.2f}")
    logger.info(f"- Equation: Température_max = {reg.intercept_:.2f} + {reg.coef_[0]:.2f} * Précipitations")
    
    # Visualisation
    fig7, ax7 = plt.subplots()
    ax7.scatter(X_test, y_test, color='royalblue', alpha=0.5, label='Données réelles')
    ax7.plot(X_test, y_pred, color='red', linewidth=2, label='Prédictions')
    ax7.set_title("Régression: Température Max vs Précipitations")
    ax7.set_xlabel("Précipitations (mm)")
    ax7.set_ylabel("Température Max (°C)")
    ax7.legend()
    afficher_et_sauvegarder(fig7, "regression_lineaire")

# ====================
# PROGRAMME PRINCIPAL
# ====================

def main():
    try:
        # Chargement des données
        df = charger_donnees("/Users/NOKHO/Desktop/Meteo/historique_meteo_uemoa_80villes_clean.csv")
        
        # Analyses
        analyser_donnees(df)
        analyser_correlations(df)
        appliquer_ml(df)
        
        logger.info("\n✅ Analyse terminée avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    main()
