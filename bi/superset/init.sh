#!/bin/bash
set -e
: "${SUPERSET_ADMIN_USER:?SUPERSET_ADMIN_USER must be set}"
: "${SUPERSET_ADMIN_PASSWORD:?SUPERSET_ADMIN_PASSWORD must be set}"
superset db upgrade
superset fab create-admin --username "$SUPERSET_ADMIN_USER" --firstname Admin --lastname Sentinelle \
  --email admin@dallapay.test --password "$SUPERSET_ADMIN_PASSWORD" || true
superset init
# Connexion DuckDB à déclarer dans l'interface (Paramètres > Connexions) :
#   duckdb:////app/superset_home/sentinelle.duckdb
# puis, dans SQL Lab :  INSTALL iceberg; LOAD iceberg; ... (voir README, section J6)
exec gunicorn -w 2 -b 0.0.0.0:8088 "superset.app:create_app()"
