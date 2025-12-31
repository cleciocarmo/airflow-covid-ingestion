from airflow import DAG
from datetime import datetime
from convert_csv_to_parquet import ConvertCsvToParquetOperator

with DAG(
    dag_id="covid_convert_raw_to_processed",
    start_date=datetime(2023, 1, 1), 
    schedule_interval=None,    # # Minha sugestão é que essa DAG seja executada pela DAG ingestao_covid_19
    catchup=False
) as dag:
    
    task_convert_covid = ConvertCsvToParquetOperator(
        task_id="convert_covid_csv_to_parquet",
        bucket="covid-lake",
        
        # Usando {{ ds }} para pegar a data da execução
        # Ex: raw/2025-12-30/dados_covid_brutos.csv
        path_source="raw/{{ ds }}/dados_covid_brutos.csv",
        
        # Salvando na camada processed mantendo a partição de data
        # Ex: processed/2025-12-30/dados_covid.parquet
        path_target="processed/{{ ds }}/dados_covid.parquet"
    )

    task_convert_covid