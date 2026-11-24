-- J4 — Tables Flink SQL de départ. Lancer avec :
--   docker compose exec flink-jobmanager ./bin/sql-client.sh -f /opt/sentinelle/sql/01_sources.sql

-- Flux brut des transactions (JSON). L'horodatage métier sert de temps d'événement.
CREATE TABLE transactions (
  tx_id        STRING,
  ts           TIMESTAMP_LTZ(3),
  compte_id    STRING,
  `type`       STRING,
  montant      DOUBLE,
  devise       STRING,
  compte_dest  STRING,
  agent_id     STRING,
  pays         STRING,
  ville        STRING,
  canal        STRING,
  device_id    STRING,
  -- on tolère 5 secondes de désordre entre événements
  WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'transactions.brutes',
  'properties.bootstrap.servers' = 'kafka:29092',
  'properties.group.id' = 'flink-features',
  'scan.startup.mode' = 'latest-offset',
  'format' = 'json',
  'json.timestamp-format.standard' = 'ISO-8601'
);

-- Comptes reçus par le CDC Debezium (dernier état de chaque compte)
CREATE TABLE comptes (
  compte_id          STRING,
  telephone          STRING,
  kyc_niveau         INT,
  plafond_journalier BIGINT,
  statut             STRING,
  device_principal   STRING,
  PRIMARY KEY (compte_id) NOT ENFORCED
) WITH (
  'connector' = 'upsert-kafka',
  'topic' = 'dallapay.public.comptes',
  'properties.bootstrap.servers' = 'kafka:29092',
  'key.format' = 'json',
  'value.format' = 'json',
  'value.fields-include' = 'ALL'
);

-- Topic de sortie des alertes
CREATE TABLE alertes (
  tx_id STRING, compte_id STRING, ts_tx TIMESTAMP_LTZ(3), regle STRING, valeur DOUBLE
) WITH (
  'connector' = 'kafka',
  'topic' = 'alertes',
  'properties.bootstrap.servers' = 'kafka:29092',
  'format' = 'json'
);
