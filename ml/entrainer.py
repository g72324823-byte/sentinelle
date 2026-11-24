"""J6 — Entraînement suivi dans MLflow (À COMPLÉTER).

Usage : MLFLOW_TRACKING_URI=http://localhost:5000 python ml/entrainer.py --data data
"""
import argparse

import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score

FEATURES = ["montant"]          # TODO : ajouter les features calculées (mêmes définitions que Flink !)


def charger(data: str) -> pd.DataFrame:
    # TODO : lire plutôt la table d'entraînement de la couche or (Iceberg)
    return pd.read_parquet(f"{data}/historique")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data")
    a = p.parse_args()
    df = charger(a.data).sort_values("ts")
    # Découpage temporel, jamais aléatoire : on entraîne sur le passé, on valide sur la suite.
    coupure = df["ts"].quantile(0.8)
    # Attention : les étiquettes des 14 derniers jours sont incomplètes (voir énoncé, § données)
    train, valid = df[df.ts < coupure], df[df.ts >= coupure]
    mlflow.set_experiment("sentinelle-fraude")
    with mlflow.start_run():
        m = RandomForestClassifier(n_estimators=200, max_depth=12, n_jobs=-1, random_state=0,
                                   class_weight="balanced_subsample")
        m.fit(train[FEATURES], train["est_fraude"])
        pr_auc = average_precision_score(valid["est_fraude"], m.predict_proba(valid[FEATURES])[:, 1])
        mlflow.log_params({"modele": "random_forest", "features": ",".join(FEATURES)})
        mlflow.log_metric("pr_auc_valid", pr_auc)
        mlflow.sklearn.log_model(m, name="modele", input_example=valid[FEATURES].head(3),
                                 registered_model_name="sentinelle-fraude",
                                 serialization_format="skops",
                                 skops_trusted_types=["sklearn.tree._tree.Tree"])
        print(f"PR-AUC validation : {pr_auc:.3f}")
        # TODO : promouvoir avec l'alias @champion si meilleur que le champion actuel


if __name__ == "__main__":
    main()
