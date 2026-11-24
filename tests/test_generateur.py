"""Tests du générateur : ils passent dès le départ. Ajoutez les vôtres dans ce dossier."""
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "generateur"))
import sentinelle_gen as g  # noqa: E402

DEBUT = datetime(2026, 9, 1, tzinfo=timezone.utc)


def test_referentiel_deterministe():
    a = g.charger_referentiel(1, 500, 50, DEBUT)
    b = g.charger_referentiel(1, 500, 50, DEBUT)
    assert a.comptes["compte_id"].tolist() == b.comptes["compte_id"].tolist()
    assert a.comptes["kyc_niveau"].between(1, 3).all()


def test_plafond_coherent_avec_kyc():
    ref = g.charger_referentiel(1, 500, 50, DEBUT)
    attendu = ref.comptes["kyc_niveau"].map(g.PLAFOND_KYC)
    assert (ref.comptes["plafond_journalier"] == attendu).all()


def test_scenarios_marques_comme_fraude():
    ref = g.charger_referentiel(1, 2000, 200, DEBUT)
    rng = np.random.default_rng(0)
    for nom, f in g.SCENARIOS.items():
        r = f(rng, ref, DEBUT)
        lignes = r[0] if nom == "sim_swap" else r
        assert lignes and all(x["est_fraude"] == 1 and x["scenario"] == nom for x in lignes)


def test_flux_sans_verite():
    """La vérité terrain ne doit jamais voyager dans le flux."""
    ref = g.charger_referentiel(1, 500, 50, DEBUT)
    row = g.fraude_rafale(np.random.default_rng(0), ref, DEBUT)[0]
    ev = g._evenement(row, DEBUT)
    assert "est_fraude" not in ev and "scenario" not in ev
