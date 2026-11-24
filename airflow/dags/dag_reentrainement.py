"""J5/J6 — Déclenché quand la couche or est mise à jour (À COMPLÉTER)."""
from __future__ import annotations

import pendulum
from airflow.sdk import Asset, dag, task

COUCHE_OR = Asset("s3://lakehouse/or/fct_kpi_journalier")


@dag(schedule=[COUCHE_OR], start_date=pendulum.datetime(2026, 11, 1, tz="Africa/Douala"),
     catchup=False, tags=["sentinelle", "J6"])
def sentinelle_reentrainement():

    @task.short_circuit
    def derive_detectee() -> bool:
        # TODO : calculer le PSI des features principales entre la semaine d'entraînement
        #        et les dernières 24 h ; retourner True si un PSI dépasse 0,25
        return False

    @task
    def reentrainer():
        # TODO : relancer ml/entrainer.py, comparer au @champion, promouvoir si meilleur
        ...

    derive_detectee() >> reentrainer()


sentinelle_reentrainement()
