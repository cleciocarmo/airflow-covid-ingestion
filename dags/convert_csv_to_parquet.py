import pandas as pd
from io import BytesIO
from airflow.models.baseoperator import BaseOperator
from custom_s3_hook import CustomS3Hook

class ConvertCsvToParquetOperator(BaseOperator):
    
    template_fields = ('path_source', 'path_target', 'bucket')

    def __init__(self, path_source: str, path_target: str, bucket: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.path_source = path_source
        self.path_target = path_target
        self.bucket      = bucket

    def execute(self, context):        
        custom_s3 = CustomS3Hook(bucket=self.bucket)

        # 1. Pega o stream (intocado)
        s3_stream = custom_s3.get_object(key=self.path_source)
        
        # 2. Lê os bytes na memória
        csv_bytes = s3_stream.read()
        
        # 3. Processa no Pandas
        df = pd.read_csv(BytesIO(csv_bytes))

        # 4. Converte
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        
        # 5. Salva
        custom_s3.put_object(key=self.path_target, buffer=parquet_buffer)
        
        # Log pra gente ver o que aconteceu
        self.log.info(f"Convertido: {self.path_source} -> {self.path_target}")