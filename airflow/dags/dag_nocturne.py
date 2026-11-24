"""J5 — Traitement nocturne (À COMPLÉTER).

Chaîne attendue :  fichier des agents du jour → contrôles Great Expectations
→ dbt build → couche or publiée comme asset → (second DAG) réentraînement si dérive.
"""
from __future__ import annotations

import pendulum
from airflow.sdk import Asset, dag, task

COUCHE_OR = Asset("s3://lakehouse/or/fct_kpi_journalier")


@dag(schedule="0 2 * * *", start_date=pendulum.datetime(2026, 11, 1, tz="Africa/Douala"),
     catchup=False, tags=["sentinelle", "J5"])
def sentinelle_nocturne():

    @task
    def recuperer_fichier_agents(ds=None) -> str:
        # Le générateur dépose data/agents/agents_AAAAMMJJ.csv (commande « agents »)
        chemin = f"/data/agents/agents_{ds.replace('-', '')}.csv"
        # TODO : vérifier que le fichier existe, sinon échouer avec un message clair
        return chemin

    @task
    def controler_qualite(chemin: str) -> str:
        # TODO : suite Great Expectations (unicité agent_id, ville non vide,
        #        type dans {AGENT, MARCHAND}, pays dans {CM, GA, TD}, date_agrement <= aujourd'hui).
        #        Décider : bloquer le DAG, ou mettre les lignes en quarantaine et continuer ?
        #        Justifier ce choix dans le dossier d'architecture.
        return chemin

    @task.bash(outlets=[COUCHE_OR])
    def dbt_build() -> str:
        return "cd /opt/sentinelle/dbt && dbt build --profiles-dir . --target dev"

    controler_qualite(recuperer_fichier_agents()) >> dbt_build()


sentinelle_nocturne()
