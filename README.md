# 🦠 Airflow COVID-19 Data Ingestion Pipeline

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.x-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![MinIO](https://img.shields.io/badge/MinIO-Object%20Storage-c72c48.svg)

A robust and scalable data engineering pipeline designed to ingest large COVID-19 datasets from **Our World in Data (OWID)** into a **MinIO Data Lake** using **Apache Airflow**.

This project focuses on **memory efficiency** and **clean architecture**, utilizing streaming techniques to handle large files without exhausting container resources.

---

✨ Key Features
Memory Efficient Streaming: Implements Python's requests streaming and NamedTemporaryFile to process large datasets in small chunks (8KB), preventing OOM (Out of Memory) errors.

Custom Operator Pattern: Encapsulates business logic in a reusable CovidDownloadOperator.

Custom Hook Pattern: Implements a CustomS3Hook with lazy loading for efficient MinIO/S3 connections.

Dockerized Environment: Fully reproducible setup using Docker Compose (Airflow + MinIO + Postgres).

Idempotency: Operations rely on Airflow's logical execution dates to maintain data consistency.

🛠️ Project Structure

airflow-covid-ingestion/
├── dags/
│   ├── dag_covid.py               # Main DAG definition
│   ├── covid_download_operator.py # Custom Operator (Streaming Logic)
│   └── custom_s3_hook.py          # Custom Hook (MinIO Connection)
├── docker-compose.yaml            # Infrastructure definition
├── Dockerfile                     # Custom Airflow image build
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation


🚀 Getting Started
Prerequisites
Docker & Docker Compose installed.

Git.

1. Clone the Repository
git clone [https://github.com/cleciocarmo/airflow-covid-ingestion.git](https://github.com/cleciocarmo/airflow-covid-ingestion.git)
cd airflow-covid-ingestion

2. Start the Infrastructure
docker-compose up -d

Wait a few minutes for the Airflow Webserver to become healthy.

3. Configure MinIO (Data Lake)
Access the MinIO Console at http://localhost:9001.

Login with user/password: minioadmin / minioadmin.

Create a bucket named: covid-lake.

4. Configure Airflow Variables (Crucial Step)
Access Airflow UI at http://localhost:8080 (User: admin / Pass: admin).

Go to Admin > Variables.

Add the following variables (Key : Value) to connect Airflow to MinIO:

Key,Value,Description
AWS_ENDPOINT,http://minio:9000,Internal docker network address
AWS_ACCESS_KEY_ID,minioadmin,MinIO User
AWS_SECRET_ACCESS_KEY,minioadmin,MinIO Password
AWS_REGION,us-east-1,Default region

5. Trigger the DAG
Enable the DAG ingestao_covid_19 in the Airflow UI.

Trigger the DAG manually.

Check the covid-lake bucket in MinIO to see the ingested file.

🧠 Engineering Logic
Why Streaming?
Loading a 5GB+ CSV file entirely into RAM (e.g., pd.read_csv()) can crash standard Docker containers. This project solves this by:

Opening a stream to the source URL.

Writing data to a temporary file on disk in small chunks.

Streaming the file from disk directly to MinIO using boto3.

Automatically cleaning up temporary files after execution.

# Snippet of the streaming logic
with requests.get(self.url, stream=True) as r:
    for chunk in r.iter_content(chunk_size=8192):
        tmp_file.write(chunk)

🤝 Contributing
Feel free to submit issues or pull requests.

📝 License
This project is licensed under the MIT License.


## 🏗️ Architecture

```mermaid
graph LR
    A[OWID Source API] -->|HTTP Stream| B(Airflow Worker)
    B -->|Boto3 Stream| C[(MinIO Data Lake)]

    subgraph "Memory Safe Zone"
        B -- Writes 8KB Chunks --> D[Temporary File]
        D -- Reads Bytes --> C
    end

    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#2496ED,stroke:#333,stroke-width:2px,color:white
