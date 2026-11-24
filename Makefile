# Projet Sentinelle — raccourcis. « make aide » liste les cibles.
PY ?= python3
COMPOSE = docker compose

aide:
	@grep -E '^[a-z0-9-]+:.*## ' Makefile | sed 's/:.*## /\t/'

donnees: ## génère comptes, agents et 60 jours d'historique dans ./data (≈ 30 s, 90 Mo)
	$(PY) generateur/sentinelle_gen.py init --sortie data

agents-du-jour: ## fichier nocturne des agents (JOUR=AAAA-MM-JJ)
	$(PY) generateur/sentinelle_gen.py agents --jour $(JOUR) --sortie data/agents

procedures: ## (re)construit les 40 procédures du RAG
	$(PY) rag/construire_procedures.py

j1: ## socle + lakehouse
	$(COMPOSE) --profile lakehouse up -d
j2: ## bases spécialisées
	$(COMPOSE) --profile stores up -d
j3: ## RAG
	$(COMPOSE) --profile rag up -d
j4: ## streaming (Kafka, Connect, Schema Registry, Flink, générateur)
	$(COMPOSE) --profile streaming up -d
	@echo "Enregistrer le connecteur CDC :  make cdc"
j5: ## orchestration
	$(COMPOSE) --profile orchestration up -d
j6: ## ML + restitution
	$(COMPOSE) --profile ml --profile bi up -d

cdc: ## enregistre le connecteur Debezium des comptes
	set -a; . ./.env; set +a; envsubst < connect/debezium-comptes.json | curl -fsS -X POST -H "Content-Type: application/json" --data @- http://localhost:8083/connectors

topics: ## crée les topics avec 6 partitions
	for t in transactions.brutes alertes features.comptes; do \
	  $(COMPOSE) exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 \
	    --create --if-not-exists --topic $$t --partitions 6 --replication-factor 1; done

scenario: ## injecte un scénario de fraude (NOM=rafale|nuit|anneau|agent|sim_swap)
	set -a; . ./.env; set +a; $(PY) generateur/sentinelle_gen.py scenario $(NOM) --vers kafka --pg "postgresql://postgres:$$PG_PASSWORD@localhost:5432/dallapay"

tests: ## lance les tests
	$(PY) -m pytest -q tests

arret: ## arrête tout (les volumes sont conservés)
	$(COMPOSE) --profile lakehouse --profile stores --profile rag --profile streaming --profile orchestration --profile ml --profile bi --profile lineage down

.PHONY: aide donnees agents-du-jour procedures j1 j2 j3 j4 j5 j6 cdc topics scenario tests arret
