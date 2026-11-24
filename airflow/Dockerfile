FROM apache/airflow:3.4.0
RUN pip install --no-cache-dir dbt-core~=1.12 dbt-duckdb great-expectations~=1.6 \
    apache-airflow-providers-openlineage pyiceberg[s3fs] duckdb
