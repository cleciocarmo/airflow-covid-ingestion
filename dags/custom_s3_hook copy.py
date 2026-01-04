import boto3
from airflow.hooks.base import BaseHook
from airflow.models import Variable

class CustomS3Hook(BaseHook):
    def __init__(self, bucket: str, **kwargs) -> None:
        super().__init__()
        self.bucket = bucket
        # FIX: Não conectamos aqui. Apenas inicializamos a variável como None.
        # Isso protege seu Airflow de travar na inicialização.
        self._client = None 

    def get_conn(self):
        """
        Cria a conexão apenas quando for necessário (Lazy Loading).
        """
        if not self._client:
            self._client = boto3.client(
                's3', 
                endpoint_url=Variable.get("AWS_ENDPOINT"),
                aws_access_key_id=Variable.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=Variable.get("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=None,
                config=boto3.session.Config(signature_version='s3v4'),
                verify=False,
                region_name=Variable.get("AWS_REGION")
            )
        return self._client

    def put_object(self, key: str, buffer):
        # Chamamos get_conn() aqui. Se for a primeira vez, ele conecta.
        client = self.get_conn()
        client.put_object(Body=buffer, Bucket=self.bucket, Key=key)

    def get_object(self, key: str):
        client = self.get_conn()
        response = client.get_object(Bucket=self.bucket, Key=key)
        return response.get("Body")