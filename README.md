# Projet Sentinelle — kit de démarrage

Plateforme de données de Dalla Pay, opérateur fictif de mobile money (Cameroun, Gabon, Tchad).
L'énoncé complet est dans `Enonce_Projet_Sentinelle.docx`.

## Démarrer

```bash
cp .env.exemple .env
pip install -r generateur/requirements.txt duckdb scikit-learn pytest
make donnees          # comptes, agents, 60 jours d'historique étiqueté dans ./data
make tests            # les tests fournis doivent passer
make j1               # socle + lakehouse, puis http://localhost:8888 (Jupyter + Spark)
```

Le jeu de test sans étiquette (`test_sans_etiquette.parquet`, 14 jours) est distribué à part
par l'enseignant. Vos prédictions sur ce fichier sont évaluées en PR-AUC.

## Contenu

| Dossier | Contenu | Jalon |
|---|---|---|
| `generateur/` | générateur de transactions, de fraudes et du fichier des agents ; mises à jour des comptes pour le CDC | tous |
| `postgres/` | base opérationnelle des comptes (chargée au premier démarrage) | J2, J4 |
| `spark/` | image Spark 4 + Iceberg, script bronze → argent à compléter | J1 |
| `neo4j/` | chargement du graphe des virements | J2 |
| `rag/` | 40 procédures internes, 20 questions de référence, indexeur à compléter | J3 |
| `schemas/`, `connect/`, `flink/` | schéma Avro, connecteur Debezium, tables et features Flink SQL | J4 |
| `dbt/`, `airflow/` | projet dbt (DuckDB) et DAG nocturnes | J5 |
| `ml/` | entraînement MLflow, API de scoring | J6 |
| `bi/` | Superset (direction) et Streamlit (analystes) | J6 |
| `docs/` | modèle du dossier d'architecture | J2, J6 |
| `tests/` | tests pytest | tous |

## Profils Docker Compose et mémoire

Ne lancez que le profil du jalon en cours (`make arret` entre deux jalons).

| Profil | Services | Mémoire indicative |
|---|---|---|
| (socle) | MinIO, PostgreSQL | 0,6 Go |
| `lakehouse` | + catalogue Iceberg REST, Spark + Jupyter | 4,5 Go |
| `stores` | + Valkey, Neo4j | 2 Go |
| `rag` | + Qdrant (le modèle d'embeddings tourne sur votre machine) | 1,5 Go |
| `streaming` | + Kafka, Schema Registry, Kafka Connect / Debezium, Flink (2 conteneurs), Valkey, générateur | 6 Go |
| `orchestration` | + Airflow (standalone), catalogue Iceberg | 2,5 Go |
| `ml` + `bi` | + MLflow, API, Kafka, Valkey, générateur, Superset, Streamlit | 6 Go |

### Démonstration complète

`make demo` lance les profils `streaming`, `ml`, `bi` et `rag` (environ 9 à 10 Go de mémoire).
Avant de la lancer, arrêtez Spark et Neo4j pour libérer de la mémoire :
`docker compose stop spark neo4j`.

## Commandes utiles du générateur

```bash
python generateur/sentinelle_gen.py flux --vers stdout --debit 5 --duree 10      # voir le flux
python generateur/sentinelle_gen.py flux --vers kafka --debit 300                 # alimenter Kafka
python generateur/sentinelle_gen.py flux --vers kafka --format avro               # bonus : Avro + Schema Registry
make scenario NOM=sim_swap
python generateur/sentinelle_gen.py agents --jour 2026-11-23 --sortie data/agents # fichier nocturne (avec défauts)
python generateur/maj_comptes.py --par-seconde 2                                  # trafic CDC
```

## Ce qui a été vérifié avant distribution

- Générateur : historique, flux (500 événements/s tenus), scénarios, fichier des agents, conformité Avro du flux.
- `postgres/init.sql`, `maj_comptes.py` et le scénario `sim_swap` sur PostgreSQL.
- Projet dbt (`dbt build` : 9 sur 9), DAG Airflow 3.4 (import sans erreur), API FastAPI, application Streamlit, `entrainer.py` avec MLflow 3.18, tests pytest.
- Le seuil de PR-AUC du sujet est atteignable : un modèle de référence avec des features de fenêtres l'atteint ; le même modèle sans ces features reste en dessous.

Non vérifié ici, faute de démon Docker : le démarrage des images. Les versions des connecteurs
Flink et Iceberg téléchargés dans les Dockerfile sont des arguments (`ARG`) à ajuster si la
construction échoue. Signalez tout problème à l'enseignant dès la première séance.
