import os
import requests
from airflow.models.baseoperator import BaseOperator
from tempfile import NamedTemporaryFile 

# Importamos o SEU hook que já está pronto
from custom_s3_hook import CustomS3Hook

class CovidDownloadOperator(BaseOperator):
    
    template_fields = ('url', 'bucket_name')

    def __init__(self, url: str, bucket_name: str = "covid-data", filename: str = "covid_full.csv", **kwargs) -> None:
        super().__init__(**kwargs)
        self.url = url
        self.bucket_name = bucket_name
        self.filename = filename

    def execute(self, context):
        execution_date = context['ds']
        
        # 1. Instancia o Hook (Lazy Loading)
        custom_s3 = CustomS3Hook(bucket=self.bucket_name)
        
        # Define o caminho onde vai salvar no MinIO
        # Ex: raw/2025-12-28/covid_full.csv
        s3_key = f"raw/{execution_date}/{self.filename}"

        print(f"--- Iniciando Download direto de: {self.url} ---")

        # 2. Cria arquivo temporário
        # Usamos suffix='.csv' só pra identificar, mas o conteúdo é texto
        with NamedTemporaryFile(suffix=".csv") as tmp_file:
            
            # --- FASE 1: BAIXAR O ARQUIVO (STREAMING) ---
            with requests.get(self.url, stream=True) as r:
                r.raise_for_status()
                # Baixa em pedacinhos de 8KB e escreve no disco
                for chunk in r.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
            
            tmp_file.flush() # Garante que tudo foi escrito no disco
            
            print(f"Download concluído. Tamanho: {os.path.getsize(tmp_file.name)} bytes")
            print(f"Enviando para o MinIO em: {s3_key}...")
            
            # --- FASE 2: UPLOAD PARA MINIO ---
            # Voltamos o ponteiro para o início do arquivo
            tmp_file.seek(0)
            
            # Mandamos o arquivo aberto para o seu Hook
            # O Hook espera um 'buffer', então passamos o arquivo direto
            custom_s3.put_object(key=s3_key, buffer=tmp_file)

        print("Processo finalizado com sucesso.")
        return s3_key