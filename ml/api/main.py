"""J6 — API de scoring (À COMPLÉTER). Objectif : p95 < 200 ms à 500 transactions/s.

Lancer en local :  uvicorn main:app --reload
"""
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

ETAT = {"modele": None, "version": None}


class Transaction(BaseModel):
    tx_id: str
    compte_id: str
    type: str
    montant: float = Field(gt=0)
    device_id: str
    canal: str = "APP"
    agent_id: str | None = None
    compte_dest: str | None = None


class Decision(BaseModel):
    tx_id: str
    score: float
    decision: str            # ACCEPTER, VERIFIER ou BLOQUER
    version_modele: str | None
    latence_ms: float


@asynccontextmanager
async def demarrage(app: FastAPI):
    uri = os.environ.get("MODELE_URI")
    if uri:
        import mlflow
        ETAT["modele"] = mlflow.sklearn.load_model(uri)   # chargé une seule fois
        ETAT["version"] = uri
    yield


app = FastAPI(title="Sentinelle — scoring", lifespan=demarrage)


@app.get("/sante")
def sante():
    return {"statut": "ok", "modele_charge": ETAT["modele"] is not None, "version": ETAT["version"]}


@app.post("/score", response_model=Decision)
def score(tx: Transaction):
    t0 = time.perf_counter()
    # TODO 1 : lire les features en ligne du compte dans Valkey (calculées par Flink)
    # TODO 2 : construire le vecteur dans le MÊME ordre qu'à l'entraînement
    # TODO 3 : appliquer le modèle ; seuils VERIFIER / BLOQUER choisis sur la validation
    s = 0.0 if ETAT["modele"] is None else float(
        ETAT["modele"].predict_proba([[tx.montant]])[0, 1])
    decision = "BLOQUER" if s >= 0.9 else "VERIFIER" if s >= 0.5 else "ACCEPTER"
    return Decision(tx_id=tx.tx_id, score=s, decision=decision, version_modele=ETAT["version"],
                    latence_ms=(time.perf_counter() - t0) * 1000)
