# 🦠 Airflow COVID-19 Data Ingestion Pipeline

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.x-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![MinIO](https://img.shields.io/badge/MinIO-Object%20Storage-c72c48.svg)

A robust and scalable data engineering pipeline designed to ingest large COVID-19 datasets from **Our World in Data (OWID)** into a **MinIO Data Lake** using **Apache Airflow**.

This project focuses on **memory efficiency** and **clean architecture**, utilizing streaming techniques to handle large files without exhausting container resources.

---

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
