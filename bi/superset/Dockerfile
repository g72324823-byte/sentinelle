# Superset interroge les tables Iceberg via DuckDB (moins de mémoire qu'un moteur Trino)
FROM apache/superset:6.1.0
USER root
RUN pip install --no-cache-dir duckdb duckdb-engine
USER superset
COPY --chown=superset init.sh /app/init.sh
CMD ["/app/init.sh"]
