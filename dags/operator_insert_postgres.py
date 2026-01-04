import pandas as pd
from io import BytesIO, StringIO
from airflow.models.baseoperator import BaseOperator
# Importar o Hook do Postgres (Ferramenta de conexão), não o Operador
from airflow.providers.postgres.hooks.postgres import PostgresHook
from custom_s3_hook import CustomS3Hook

class OperatorInsertPostgres(BaseOperator):
    
    template_fields = ('path_source', 'bucket')

    def __init__(
        self, path_source: 
        str, table_name: 
        str, bucket: 
        str, postgres_conn_id: str = 'pg_awari', # Definindo o padrão aqui
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.path_source = path_source
        self.table_name  = table_name
        self.bucket      = bucket
        self.postgres_conn_id = postgres_conn_id

    def execute(self, context):        
        custom_s3 = CustomS3Hook(bucket=self.bucket)

        # 1. Pega o stream (intocado)
        s3_stream = custom_s3.get_object(key=self.path_source)
        
        # 2. Lê os bytes na memória
        parquet_bytes = s3_stream.read()
        
        # 3. Processa no Pandas
        df = pd.read_parquet(BytesIO(parquet_bytes))

        # --- 2. Inserir no Postgres (Carga) ---
        self.log.info(f"Conectando ao Postgres: {self.postgres_conn_id}")
        
        # Instancia o Hook do Postgres
        pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        
        # Pega a engine do SQLAlchemy (necessária para o df.to_sql funcionar)
        engine = pg_hook.get_sqlalchemy_engine()

        self.log.info(f"Inserindo dados na tabela: {self.table_name}")
        
        # --- OTIMIZAÇÃO: COPY EXPERT ---

        # 1. Cria a estrutura da tabela vazia (Instantâneo)
        # Usamos head(0) para o Pandas criar os tipos de coluna no banco, mas sem inserir dados (lento)
        self.log.info(f"Recriando estrutura da tabela: {self.table_name}")
        df.head(0).to_sql(
            name=self.table_name,
            con=engine,
            if_exists='replace',
            index=False
        )

        # 2. Prepara os dados na memória (Buffer de Texto)
        # Convertemos o DF para um CSV separado por TAB (\t) na memória RAM
        output = StringIO()
        df.to_csv(output, sep='\t', header=False, index=False)
        output.seek(0) # Volta o ponteiro para o início do arquivo na memória

        # 3. Pega a conexão bruta (Raw Connection)
        # O SQLAlchemy é lento para insert, então pegamos o driver psycopg2 direto
        connection = pg_hook.get_conn()
        cursor = connection.cursor()

        self.log.info(f"Iniciando carga via COPY para: {self.table_name}...")
        
        # 4. O Comando Turbo
        # Copia do buffer da memória direto para o disco do banco
        cursor.copy_expert(
            f"COPY {self.table_name} FROM STDIN WITH CSV DELIMITER '\t'",
            output
        )

        connection.commit()
        cursor.close()
        connection.close()
        
        self.log.info("Carga COPY concluída com sucesso!")