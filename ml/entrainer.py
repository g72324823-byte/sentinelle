"""J6 — Entraînement suivi dans MLflow (À COMPLÉTER).

Usage : MLFLOW_TRACKING_URI=http://localhost:5000 python ml/entrainer.py --data data
        --jours-validation 14 --jours-exclusion 14
"""
import argparse

import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score

FEATURES = ["montant"]          # TODO : ajouter les features calculées (mêmes définitions que Flink !)


def decouper_temporellement(
    df: pd.DataFrame, jours_validation: int, jours_exclusion: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fin_validation = df["ts"].max() - pd.Timedelta(days=jours_exclusion)
    debut_validation = fin_validation - pd.Timedelta(days=jours_validation)
    train = df[df["ts"] < debut_validation]
    valid = df[(df["ts"] >= debut_validation) & (df["ts"] < fin_validation)]
    return train, valid


def charger(data: str) -> pd.DataFrame:
    # TODO : lire plutôt la table d'entraînement de la couche or (Iceberg)
    return pd.read_parquet(f"{data}/historique")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data")
    p.add_argument("--jours-validation", type=int, default=14)
    p.add_argument("--jours-exclusion", type=int, default=14)
    a = p.parse_args()
    if a.jours_validation <= 0 or a.jours_exclusion <= 0:
        p.error("--jours-validation et --jours-exclusion doivent être positifs")

    df = charger(a.data).sort_values("ts")
    train, valid = decouper_temporellement(df, a.jours_validation, a.jours_exclusion)
    if train.empty or valid.empty:
        p.error("la période sélectionnée ne contient pas de données d'entraînement et de validation")

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
