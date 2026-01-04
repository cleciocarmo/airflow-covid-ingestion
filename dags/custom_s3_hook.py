import boto3
from airflow.hooks.base import BaseHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

class CustomS3Hook(BaseHook):
    def __init__(self, bucket: str, aws_conn_id: str = 'aws_default', **kwargs) -> None:
        super().__init__()
        self.bucket = bucket
        self.aws_conn_id = aws_conn_id # Agora usamos o ID da conexão, não variáveis
        self._client = None 

    def get_conn(self):
        """
        Usa o S3Hook oficial para ler as credenciais e o endpoint do Airflow Connection.
        """
        if not self._client:
            # A MÁGICA: O S3Hook vai lá no Admin -> Connections, pega o 'aws_default',
            # lê o login (minioadmin), a senha e o JSON do endpoint_url automaticamente.
            s3_hook = S3Hook(aws_conn_id=self.aws_conn_id)
            
            # Pega o cliente boto3 cru configurado
            self._client = s3_hook.get_conn()
            
        return self._client

    def put_object(self, key: str, buffer):
        client = self.get_conn()
        # O client retornado pelo S3Hook funciona igual ao boto3 padrão
        client.put_object(Body=buffer, Bucket=self.bucket, Key=key)

    def get_object(self, key: str):
        client = self.get_conn()
        response = client.get_object(Bucket=self.bucket, Key=key)
        return response.get("Body")