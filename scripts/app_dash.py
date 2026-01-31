import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime as dt

# Configuration des données
DATA_CSV_PATH = "/Users/NOKHO/Desktop/Meteo/historique_meteo_uemoa_80villes_clean.csv"

# Vérification et chargement des données
if os.path.exists(DATA_CSV_PATH):
    df = pd.read_csv(DATA_CSV_PATH, parse_dates=['datetime'])
else:
    raise FileNotFoundError(f"Le fichier de données n'a pas été trouvé : {DATA_CSV_PATH}")

# Préparation des données - Utilisation des noms de colonnes exacts du CSV
df = df.rename(columns={
    'datetime': 'Date',
    'temp': 'Température (°C)',
    'precip': 'Précipitations (mm)',
    'windspeed': 'Vent (km/h)',
    'winddir': 'Direction Vent (°)',
    'cloudcover': 'Couverture Nuageuse',
    'conditions': 'Conditions'
})

# Colonnes à conserver (avec les noms exacts du CSV)
cols_utiles = [
    'Date', 'Pays', 'Ville', 'latitude', 'longitude',
    'Température (°C)', 'Précipitations (mm)', 'Vent (km/h)',
    'Direction Vent (°)', 'Couverture Nuageuse', 'Conditions'
]

# Vérification que les colonnes existent bien
cols_disponibles = [col for col in cols_utiles if col in df.columns]
df = df[cols_disponibles]

# Variables globales
date_debut = df['Date'].min().date()
date_fin = df['Date'].max().date()
pays_disponibles = sorted(df['Pays'].unique())

# Initialisation de l'app Dash
app = dash.Dash(__name__, 
               external_stylesheets=[dbc.themes.LUX],
               meta_tags=[{'name': 'viewport',
                          'content': 'width=device-width, initial-scale=1.0'}])
app.title = "🌦️ Dashboard Météo UEMOA"

# Layout de l'application
app.layout = dbc.Container([
    # En-tête
    dbc.NavbarSimple(
        brand="🌍 Dashboard Météo UEMOA",
        brand_href="#",
        color="primary",
        dark=True,
        fluid=True
    ),
    
    # Contrôles
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🔧 Filtres", className="fw-bold"),
                dbc.CardBody([
                    html.Label("🌍 Pays", className="form-label"),
                    dcc.Dropdown(
                        id='dropdown-pays',
                        options=[{"label": p, "value": p} for p in pays_disponibles],
                        value=pays_disponibles[0],
                        clearable=False,
                        className="mb-3"
                    ),
                    
                    html.Label("🏙️ Ville", className="form-label"),
                    dcc.Dropdown(
                        id='dropdown-ville',
                        clearable=False,
                        className="mb-3"
                    ),
                    
                    html.Label("📅 Période", className="form-label"),
                    dcc.DatePickerRange(
                        id='date-range',
                        min_date_allowed=date_debut,
                        max_date_allowed=date_fin,
                        start_date=date_debut,
                        end_date=date_fin,
                        display_format='DD/MM/YYYY',
                        className="mb-3"
                    ),
                    
                    dbc.Button("🔄 Actualiser", id="btn-refresh", color="info", className="w-100")
                ])
            ])
        ], md=3),
        
        # Contenu principal
        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardHeader("🌡️ Température Moyenne", className="fw-bold"),
                    dbc.CardBody(html.H4(id="temp-moyenne", className="text-center"))
                ], color="danger", inverse=True), md=4),
                
                dbc.Col(dbc.Card([
                    dbc.CardHeader("🌧️ Précipitations Totales", className="fw-bold"),
                    dbc.CardBody(html.H4(id="precip-total", className="text-center"))
                ], color="info", inverse=True), md=4),
                
                dbc.Col(dbc.Card([
                    dbc.CardHeader("💨 Vent Moyen", className="fw-bold"),
                    dbc.CardBody(html.H4(id="vent-moyen", className="text-center"))
                ], color="success", inverse=True), md=4),
            ], className="mb-4"),
            
            dbc.Tabs([
                dbc.Tab(label="Température", children=[
                    dcc.Graph(id='graph-temp')
                ]),
                
                dbc.Tab(label="Précipitations", children=[
                    dcc.Graph(id='graph-precip')
                ]),
                
                dbc.Tab(label="Vent", children=[
                    dcc.Graph(id='graph-vent')
                ]),
                
                dbc.Tab(label="Carte", children=[
                    dcc.Graph(id='carte-meteo')
                ]),
                
                dbc.Tab(label="Données Brutes", children=[
                    dash_table.DataTable(
                        id='table-donnees',
                        columns=[{"name": col, "id": col} for col in cols_disponibles],
                        page_size=10,
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '8px'
                        }
                    )
                ])
            ]),
            
            dbc.Row([
                dbc.Col(html.Div(id="alertes-meteo"), md=12)
            ], className="my-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button("📥 Exporter CSV", id="btn-export", color="success", className="me-2"),
                ], md=12, className="text-end")
            ]),
            
            dcc.Download(id="download-dataframe-csv")
        ], md=9)
    ], className="mt-3"),
    
    html.Footer(
        dbc.Container([
            html.Hr(),
            html.P("© 2025 Dashboard Météo UEMOA - by Nokho", className="text-center text-muted")
        ])
    )
], fluid=True)

# Callbacks
@app.callback(
    Output("dropdown-ville", "options"),
    Output("dropdown-ville", "value"),
    Input("dropdown-pays", "value")
)
def update_villes(pays):
    villes = df[df["Pays"] == pays]["Ville"].unique()
    options = [{"label": v, "value": v} for v in sorted(villes)]
    valeur = options[0]["value"] if options else None
    return options, valeur

@app.callback(
    Output("temp-moyenne", "children"),
    Output("precip-total", "children"),
    Output("vent-moyen", "children"),
    Output("graph-temp", "figure"),
    Output("graph-precip", "figure"),
    Output("graph-vent", "figure"),
    Output("carte-meteo", "figure"),
    Output("table-donnees", "data"),
    Output("alertes-meteo", "children"),
    Input("btn-refresh", "n_clicks"),
    State("dropdown-pays", "value"),
    State("dropdown-ville", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date")
)
def update_dashboard(n_clicks, pays, ville, start_date, end_date):
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    dff = df[
        (df["Pays"] == pays) &
        (df["Ville"] == ville) &
        (df["Date"] >= start) &
        (df["Date"] <= end)
    ]
    
    if dff.empty:
        temp_moy = precip_total = vent_moy = "N/A"
        
        # Création de figures vides avec un message
        fig_temp = go.Figure()
        fig_temp.add_annotation(text="Pas de données disponibles",
                              xref="paper", yref="paper",
                              x=0.5, y=0.5, showarrow=False)
        
        fig_precip = go.Figure()
        fig_precip.add_annotation(text="Pas de données disponibles",
                                 xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
        
        fig_vent = go.Figure()
        fig_vent.add_annotation(text="Pas de données disponibles",
                              xref="paper", yref="paper",
                              x=0.5, y=0.5, showarrow=False)
        
        fig_map = go.Figure()
        fig_map.add_annotation(text="Pas de données disponibles",
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False)
        fig_map.update_layout(mapbox_style="open-street-map")
        
        alertes = dbc.Alert("⚠️ Aucune donnée disponible pour cette sélection.", color="warning")
        return [temp_moy, precip_total, vent_moy, 
                fig_temp, fig_precip, fig_vent, 
                fig_map, [], alertes]
    
    # Calcul des indicateurs
    temp_moy_val = dff['Température (°C)'].mean()
    precip_total_val = dff['Précipitations (mm)'].sum()
    vent_moy_val = dff['Vent (km/h)'].mean()
    
    temp_moy = f"{temp_moy_val:.1f} °C"
    precip_total = f"{precip_total_val:.1f} mm"
    vent_moy = f"{vent_moy_val:.1f} km/h"
    
    # Création des graphiques
    fig_temp = px.line(dff, x="Date", y="Température (°C)", title=f'Température à {ville}')
    fig_precip = px.line(dff, x="Date", y="Précipitations (mm)", title=f'Précipitations à {ville}')
    fig_vent = px.line(dff, x="Date", y="Vent (km/h)", title=f'Vitesse du vent à {ville}')
    
    # Carte
    df_map = df[
        (df["Pays"] == pays) &
        (df["Date"] >= start) &
        (df["Date"] <= end)
    ].groupby(["Ville", "latitude", "longitude"]).agg({
        'Température (°C)': 'mean',
        'Précipitations (mm)': 'sum'
    }).reset_index()
    
    if not df_map.empty:
        fig_map = px.scatter_mapbox(
            df_map,
            lat="latitude",
            lon="longitude",
            color="Température (°C)",
            size="Précipitations (mm)",
            hover_name="Ville",
            hover_data=["Température (°C)", "Précipitations (mm)"],
            color_continuous_scale=px.colors.sequential.OrRd,
            zoom=5,
            height=500,
            title=f"Températures moyennes dans {pays}"
        )
        fig_map.update_layout(mapbox_style="open-street-map")
    else:
        fig_map = go.Figure()
        fig_map.add_annotation(text="Pas de données disponibles",
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False)
        fig_map.update_layout(mapbox_style="open-street-map")
    
    # Alertes
    alert_msgs = []
    if temp_moy_val > 35:
        alert_msgs.append("🔥 Température élevée (> 35°C)")
    if precip_total_val > 50:
        alert_msgs.append("🌧️ Précipitations importantes (> 50 mm)")
    if vent_moy_val > 30:
        alert_msgs.append("💨 Vent fort (> 30 km/h)")
    
    if alert_msgs:
        alertes = [dbc.Alert(msg, color="danger", className="mb-2") for msg in alert_msgs]
        alertes = html.Div(alertes)
    else:
        alertes = dbc.Alert("✅ Aucune alerte météo", color="success")
    
    # Préparation des données pour la table
    table_data = dff[cols_disponibles].to_dict('records')
    
    return [temp_moy, precip_total, vent_moy,
            fig_temp, fig_precip, fig_vent,
            fig_map, table_data, alertes]

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-export", "n_clicks"),
    State("dropdown-pays", "value"),
    State("dropdown-ville", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date"),
    prevent_initial_call=True
)
def export_csv(n_clicks, pays, ville, start_date, end_date):
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    dff = df[
        (df["Pays"] == pays) &
        (df["Ville"] == ville) &
        (df["Date"] >= start) &
        (df["Date"] <= end)
    ]
    
    if dff.empty:
        return dash.no_update
    
    return dcc.send_data_frame(
        dff.to_csv,
        filename=f"meteo_{ville}_{start.date()}_to_{end.date()}.csv",
        index=False
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
