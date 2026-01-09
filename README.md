# 🚀 High-Performance Data Ingestion Pipeline: Airflow & MinIO

**A production-ready data engineering pipeline designed to ingest massive datasets with memory efficiency.**

This project demonstrates a robust ETL architecture that ingests COVID-19 data from **Our World in Data (OWID)** into a **MinIO Data Lake (S3 Compatible)**. It focuses on **resource optimization**, **clean architecture**, and **scalability**, using streaming techniques to handle large files without exhausting container resources (OOM).

---

## 🛠️ Tech Stack & Key Concepts

* **Orchestration:** Apache Airflow 2.x
* **Storage (Data Lake):** MinIO (S3 Compatible Object Storage)
* **Containerization:** Docker & Docker Compose
* **Language:** Python 3.9+ (Boto3, Requests)
* **Architecture:** Custom Operators, Hooks, and SOLID Principles

---

## ✨ Key Features (The "Why")

### 1. 📉 Memory Efficient Streaming (Zero-OOM)
Instead of loading 5GB+ datasets into RAM (standard `pandas.read_csv` approach), this pipeline implements **HTTP Streaming**.
* It processes data in **8KB chunks**.
* Writes to a `NamedTemporaryFile` on disk.
* Streams from disk directly to MinIO.
* **Result:** A container with 512MB RAM can process files of **any size**.

### 2. 🧩 Custom Operator Pattern
Business logic is encapsulated in a reusable `CovidDownloadOperator`, separating concerns from the DAG definition. This promotes **DRY (Don't Repeat Yourself)** principles and makes the code testable.

### 3. 🔌 Custom Hook Pattern (Lazy Loading)
Implements a `CustomS3Hook` that manages connections to MinIO/AWS efficiently, ensuring connections are only opened when strictly necessary (Lazy Initialization).

### 4. 🐳 Fully Reproducible Environment
Infrastructure as Code (IaC) using `docker-compose`. One command sets up Airflow (Webserver, Scheduler, Triggerer), Postgres (Metadata), and MinIO.

---

## 🏗️ Project Structure

```bash
airflow-covid-ingestion/
├── dags/
│   ├── dag_covid.py                # Main DAG definition (Orchestration logic)
│   ├── covid_download_operator.py  # Custom Operator (Business Logic & Streaming)
│   └── custom_s3_hook.py           # Custom Hook (MinIO/S3 Connection)
├── docker-compose.yaml             # Infrastructure definition
├── Dockerfile                      # Custom Airflow image build
├── requirements.txt                # Python dependencies
└── README.md                       # Documentation
````

🚀 Getting Started
Prerequisites
Docker & Docker Compose installed.

Git.

1. Clone & Start
git clone [https://github.com/cleciocarmo/airflow-covid-ingestion.git](https://github.com/cleciocarmo/airflow-covid-ingestion.git)
cd airflow-covid-ingestion

# Start Infrastructure (Airflow + MinIO + Postgres)
docker-compose up -d

Wait a few minutes for the Airflow Webserver to become healthy.

2. Configure Data Lake (MinIO)
Access MinIO Console at http://localhost:9001.

Login: minioadmin / minioadmin.

Create a Bucket named: covid-lake.

3. Configure Airflow Connections (Crucial)
Access Airflow UI at http://localhost:8080 (User/Pass: admin).

Go to Admin > Variables.

Add the following keys to connect Airflow to the internal Docker network:

| Key | Value | Description |
| :--- | :--- | :--- |
| `AWS_ENDPOINT` | `http://minio:9000` | Internal docker network address |
| `AWS_ACCESS_KEY_ID` | `minioadmin` | MinIO User |
| `AWS_SECRET_ACCESS_KEY` | `minioadmin` | MinIO Password |
| `AWS_REGION` | `us-east-1` | Default region |

4. Trigger the DAG
Enable the DAG ingestao_covid_19 in the UI.

Trigger it manually.

Check the covid-lake bucket in MinIO to see the raw .csv or .json file ingested.

🤝 Contributing
Feel free to submit issues or pull requests to improve the architecture.

📝 License
This project is licensed under the MIT License.

```mermaid
graph LR
    %% Definição de Estilos
    classDef orchestrator fill:#ff9f43,stroke:#333,stroke-width:2px,color:white;
    classDef source fill:#5f27cd,stroke:#333,stroke-width:2px,color:white;
    classDef storage fill:#2e86de,stroke:#333,stroke-width:2px,color:white;
    classDef process fill:#10ac84,stroke:#333,stroke-width:2px,color:white;
    classDef cloud fill:#feca57,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5;

    %% Camada de Orquestração
    subgraph Airflow_Controller [Orchestrator: Apache Airflow]
        direction TB
        Task_Ingest(Ingestion Operator)
        Task_Process(Spark/Python Operator)
        Task_Ingest --> Task_Process
    end

    %% Fonte de Dados
    Source[OWID Source API] -->|HTTP Stream| Task_Ingest

    %% Fluxo de Dados (Storage)
    subgraph Data_Lake [Data Lake Storage Layer]
        direction TB
        Raw_Bucket[(MinIO / S3 <br/> Bronze Zone <br/> .JSON)]
        Refined_Bucket[(MinIO / S3 <br/> Silver Zone <br/> .Parquet)]
    end

    %% Conexões de Processamento
    Task_Ingest -->|Raw Data Write| Raw_Bucket
    Raw_Bucket -->|Read Bytes| Task_Process
    Task_Process -->|Transform & Optimize| Refined_Bucket

    %% Nota de Infraestrutura
    subgraph Infra_Note [Infrastructure Replica]
        Cloud_AWS[AWS Cloud <br/> EC2 + S3 + Glue]
        Cloud_DB[Databricks <br/> Spark Cluster]
    end

    %% Link Visual (apenas para contexto)
    Refined_Bucket -.-> Cloud_DB

    %% Aplicação de Classes
    class Airflow_Controller orchestrator;
    class Source source;
    class Raw_Bucket,Refined_Bucket storage;
    class Task_Ingest,Task_Process process;
    class Infra_Note cloud;

