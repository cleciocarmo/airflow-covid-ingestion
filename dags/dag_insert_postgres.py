from airflow import DAG
from datetime import datetime
from operator_insert_postgres import OperatorInsertPostgres

with DAG(
    dag_id="dag_insert_postgres",
    start_date=datetime(2023, 1, 1), 
    schedule_interval=None,    # # Minha sugestão é que essa DAG seja executada pela DAG ingestao_covid_19
    catchup=False
) as dag:
    
    task_insert = OperatorInsertPostgres(
        task_id="operator_insert_postgres",
        path_source="processed/{{ ds }}/dados_covid.parquet",
        table_name='dados_covid',        
        bucket="covid-lake",
        postgres_conn_id='pg_awari'
    )

    task_insert