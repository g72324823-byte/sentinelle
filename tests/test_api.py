"""Tests de l'API de scoring (à enrichir au jalon J6)."""
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ml" / "api"))
import main  # noqa: E402

client = TestClient(main.app)
TX = {"tx_id": "T1", "compte_id": "CM000001", "type": "PAIEMENT", "montant": 5000, "device_id": "D1"}


def test_sante():
    assert client.get("/sante").json()["statut"] == "ok"


def test_montant_negatif_refuse():
    assert client.post("/score", json={**TX, "montant": -10}).status_code == 422


def test_decision_valide():
    r = client.post("/score", json=TX).json()
    assert r["decision"] in {"ACCEPTER", "VERIFIER", "BLOQUER"} and 0 <= r["score"] <= 1

# TODO J6 : test de latence (100 appels, p95 < 50 ms en local), test avec un modèle factice
