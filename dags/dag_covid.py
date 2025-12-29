from airflow import DAG
from datetime import datetime
from covid_download_operator import CovidDownloadOperator

# Link direto do CSV
URL_COVID = 'https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv'

with DAG(dag_id="ingestao_covid_19", 
         start_date=datetime(2023, 1, 1), 
         schedule_interval=None, 
         catchup=False
        ) as dag:
    
    # Task única: Baixa e salva no MinIO
    download_task = CovidDownloadOperator(
        task_id='download_covid_data',
        url=URL_COVID,
        bucket_name='covid-lake', #criar bucket antes se não existir
        filename='dados_covid_brutos.csv'
    )
