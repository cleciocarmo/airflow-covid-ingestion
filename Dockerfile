FROM apache/airflow:2.5.1-python3.8

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt