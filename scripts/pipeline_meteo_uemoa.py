from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'uemoa_user',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 30),
    'end_date': datetime(2025, 7, 14),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='pipeline_bon_meteo_uemoa',
    default_args=default_args,
    schedule_interval='0 0 * * *',
    catchup=True,
    tags=['meteo', 'uemoa'],
    description='Collecte, transformation et chargement météo UEMOA (14 jours)',
) as dag:

    collecter_donnees = BashOperator(
        task_id='collecte_meteo',
        bash_command='/Users/NOKHO/Desktop/Meteo/airflow_venv/bin/python3 /Users/NOKHO/Desktop/Meteo/openmeteo_uemoa.py'
    )

    transformer_donnees = BashOperator(
        task_id='transformation_meteo',
        bash_command='/Users/NOKHO/Desktop/Meteo/airflow_venv/bin/python3 /Users/NOKHO/Desktop/Meteo/transform_uemoa.py'
    )

    charger_donnees = BashOperator(
        task_id='chargement_entrepot',
        bash_command='/Users/NOKHO/Desktop/Meteo/airflow_venv/bin/python3 /Users/NOKHO/Desktop/Meteo/load_uemoa.py'
    )

    collecter_donnees >> transformer_donnees >> charger_donnees

