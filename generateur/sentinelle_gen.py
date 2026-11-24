#!/usr/bin/env python3
"""Générateur de données du projet Sentinelle (opérateur fictif Dalla Pay).

Sous-commandes :
  init      crée les comptes, les agents et l'historique de transactions étiqueté
  flux      émet des transactions en continu (Kafka, fichier JSONL ou stdout)
  scenario  injecte un scénario de fraude précis dans le flux (démonstration)
  agents    produit le fichier nocturne des agents d'un jour (avec défauts de qualité)

Tout est déterministe avec --graine : deux équipes qui lancent la même commande
obtiennent exactement les mêmes données.

Exemples :
  python sentinelle_gen.py init --sortie ../data
  python sentinelle_gen.py flux --vers kafka --debit 300
  python sentinelle_gen.py flux --vers stdout --debit 5 --duree 10
  python sentinelle_gen.py scenario anneau --vers kafka
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Référentiels
# ---------------------------------------------------------------------------
PAYS = {
    "CM": {"poids": 0.60, "villes": ["Douala", "Yaoundé", "Bafoussam", "Garoua", "Bamenda", "Kribi"],
           "poids_villes": [0.34, 0.30, 0.10, 0.10, 0.10, 0.06], "indicatif": "+237"},
    "GA": {"poids": 0.20, "villes": ["Libreville", "Port-Gentil", "Franceville", "Oyem"],
           "poids_villes": [0.60, 0.22, 0.10, 0.08], "indicatif": "+241"},
    "TD": {"poids": 0.20, "villes": ["N'Djamena", "Moundou", "Abéché", "Sarh"],
           "poids_villes": [0.62, 0.15, 0.12, 0.11], "indicatif": "+235"},
}
SEGMENTS = ["particulier", "commercant", "etudiant"]
POIDS_SEGMENTS = [0.72, 0.10, 0.18]
CATEGORIES = ["alimentation", "carburant", "telecom", "pharmacie", "transport",
              "habillement", "restauration", "electronique", "education", "sante"]
TYPES = ["PAIEMENT", "TRANSFERT", "RETRAIT", "DEPOT", "FACTURE", "RECHARGE"]
# probabilité de chaque type selon le segment
MIX_TYPES = {
    "particulier": [0.30, 0.25, 0.15, 0.12, 0.10, 0.08],
    "commercant":  [0.10, 0.30, 0.20, 0.30, 0.07, 0.03],
    "etudiant":    [0.35, 0.25, 0.10, 0.10, 0.05, 0.15],
}
# montant médian (XAF) par type
MEDIANE_TYPE = {"PAIEMENT": 6_000, "TRANSFERT": 15_000, "RETRAIT": 25_000,
                "DEPOT": 30_000, "FACTURE": 12_000, "RECHARGE": 1_500}
PLAFOND_KYC = {1: 200_000, 2: 1_000_000, 3: 5_000_000}
SEUIL_DECLARATION = 500_000   # au-delà, contrôle renforcé chez l'agent

COLONNES = ["tx_id", "ts", "compte_id", "type", "montant", "devise", "compte_dest",
            "agent_id", "pays", "ville", "canal", "device_id", "est_fraude", "scenario"]


@dataclass
class Referentiel:
    comptes: pd.DataFrame
    agents: pd.DataFrame


# ---------------------------------------------------------------------------
# Comptes et agents
# ---------------------------------------------------------------------------
def creer_comptes(rng: np.random.Generator, n: int, debut: datetime) -> pd.DataFrame:
    codes = list(PAYS)
    pays = rng.choice(codes, size=n, p=[PAYS[c]["poids"] for c in codes])
    villes = np.empty(n, dtype=object)
    for c in codes:
        m = pays == c
        villes[m] = rng.choice(PAYS[c]["villes"], size=m.sum(), p=PAYS[c]["poids_villes"])
    segment = rng.choice(SEGMENTS, size=n, p=POIDS_SEGMENTS)
    kyc = rng.choice([1, 2, 3], size=n, p=[0.45, 0.45, 0.10])
    kyc[segment == "commercant"] = np.maximum(kyc[segment == "commercant"], 2)
    anciennete = rng.integers(10, 3_000, size=n)
    ouverture = [(debut - timedelta(days=int(a))).date().isoformat() for a in anciennete]
    tel = [f"{PAYS[p]['indicatif']}6{rng.integers(10_000_000, 99_999_999)}" for p in pays]
    # habitudes, cachées dans le référentiel mais utiles au générateur
    heure_hab = np.clip(rng.normal(13, 3.5, size=n), 6, 22)
    mu_montant = rng.normal(0, 0.45, size=n)
    activite = rng.gamma(1.6, 0.22, size=n)          # transactions par jour
    activite[segment == "commercant"] *= 4
    ids = np.array([f"{p}{i:06d}" for p, i in zip(pays, range(1, n + 1))])
    df = pd.DataFrame({
        "compte_id": ids, "telephone": tel, "pays": pays, "ville": villes,
        "segment": segment, "kyc_niveau": kyc,
        "plafond_journalier": [PLAFOND_KYC[k] for k in kyc],
        "date_ouverture": ouverture, "statut": "ACTIF",
        "device_principal": [f"D{uuid.UUID(int=int(rng.integers(0, 2**63))).hex[:12]}" for _ in range(n)],
    })
    df.attrs["habitudes"] = {"heure": heure_hab, "mu": mu_montant, "activite": activite}
    return df


def creer_agents(rng: np.random.Generator, n: int, debut: datetime) -> pd.DataFrame:
    codes = list(PAYS)
    pays = rng.choice(codes, size=n, p=[PAYS[c]["poids"] for c in codes])
    villes = np.empty(n, dtype=object)
    for c in codes:
        m = pays == c
        villes[m] = rng.choice(PAYS[c]["villes"], size=m.sum(), p=PAYS[c]["poids_villes"])
    typ = rng.choice(["AGENT", "MARCHAND"], size=n, p=[0.35, 0.65])
    cat = np.where(typ == "AGENT", "cash", rng.choice(CATEGORIES, size=n))
    agrement = [(debut - timedelta(days=int(d))).date().isoformat() for d in rng.integers(30, 2_500, n)]
    return pd.DataFrame({
        "agent_id": [f"AG{i:05d}" for i in range(1, n + 1)], "type": typ, "categorie": cat,
        "pays": pays, "ville": villes, "date_agrement": agrement, "statut": "ACTIF",
    })


# ---------------------------------------------------------------------------
# Transactions normales (vectorisé)
# ---------------------------------------------------------------------------
_CACHE_VILLES: dict = {}


def _agents_par_ville(agents: pd.DataFrame) -> dict:
    if id(agents) in _CACHE_VILLES:
        return _CACHE_VILLES[id(agents)]
    out = _CACHE_VILLES.setdefault(id(agents), {})
    for (ville, typ), g in agents.groupby(["ville", "type"]):
        out[(ville, typ)] = g["agent_id"].to_numpy()
    return out


def transactions_normales(rng, ref: Referentiel, jour: datetime, facteur: float = 1.0) -> pd.DataFrame:
    c = ref.comptes
    hab = c.attrs["habitudes"]
    n_cpt = len(c)
    nb = rng.poisson(hab["activite"] * facteur)
    idx = np.repeat(np.arange(n_cpt), nb)
    m = len(idx)
    if m == 0:
        return pd.DataFrame(columns=COLONNES)
    seg = c["segment"].to_numpy()[idx]
    # type selon le segment
    u = rng.random(m)
    typ = np.empty(m, dtype=object)
    for s, probs in MIX_TYPES.items():
        sel = seg == s
        cum = np.cumsum(probs)
        typ[sel] = np.array(TYPES)[np.searchsorted(cum, u[sel] * cum[-1])]
    # heure : habitude du compte + bruit ; quelques travailleurs de nuit légitimes
    heure = rng.normal(hab["heure"][idx], 3.0)
    nuit_legit = rng.random(m) < 0.015
    heure[nuit_legit] = rng.uniform(0, 5, nuit_legit.sum())
    heure = np.mod(heure, 24)
    ts = np.array([jour + timedelta(hours=float(h)) for h in heure])
    # montant log-normal autour de la médiane du type, ajusté au compte
    med = np.array([MEDIANE_TYPE[t] for t in typ])
    montant = med * np.exp(hab["mu"][idx] + rng.normal(0, 0.7, m))
    jour_paie = jour.day in (25, 26, 27, 28)            # fin de mois : gros montants légitimes
    if jour_paie:
        montant *= np.where(rng.random(m) < 0.25, rng.uniform(1.5, 4, m), 1)
    montant = np.round(np.clip(montant, 100, None), -1)
    # destinataire pour les transferts : un petit cercle de contacts
    dest = np.full(m, None, dtype=object)
    tr = typ == "TRANSFERT"
    off = rng.choice([1, 7, 31, 101, 977, 5003], size=tr.sum())
    alea = rng.random(tr.sum()) < 0.2
    cible = np.where(alea, rng.integers(0, n_cpt, tr.sum()), (idx[tr] + off) % n_cpt)
    dest[tr] = c["compte_id"].to_numpy()[cible]
    # agent / marchand dans la ville du compte
    villes = c["ville"].to_numpy()[idx]
    agent = np.full(m, None, dtype=object)
    par_ville = _agents_par_ville(ref.agents)
    besoin_agent = np.isin(typ, ["RETRAIT", "DEPOT"])
    besoin_marchand = typ == "PAIEMENT"
    for v in np.unique(villes):
        sv = villes == v
        for masque, t in ((besoin_agent, "AGENT"), (besoin_marchand, "MARCHAND")):
            sel = sv & masque
            pool = par_ville.get((v, t))
            if pool is not None and sel.any():
                agent[sel] = rng.choice(pool, size=sel.sum())
    canal = np.where(rng.random(m) < 0.55, "APP", "USSD")
    device = c["device_principal"].to_numpy()[idx].copy()
    autre = rng.random(m) < 0.06                         # téléphone prêté, changé ou réinstallé
    device[autre] = [f"D{rng.integers(0, 2**48):012x}" for _ in range(autre.sum())]
    # commerçants : gros retraits légitimes, parfois juste sous le seuil (habitude de fractionner)
    com = (seg == "commercant") & (typ == "RETRAIT") & (rng.random(m) < 0.12)
    montant[com] = np.round(rng.uniform(380_000, 499_900, com.sum()), -1)
    df = pd.DataFrame({
        "ts": ts, "compte_id": c["compte_id"].to_numpy()[idx], "type": typ,
        "montant": montant, "devise": "XAF", "compte_dest": dest, "agent_id": agent,
        "pays": c["pays"].to_numpy()[idx], "ville": villes, "canal": canal,
        "device_id": device, "est_fraude": 0, "scenario": "normal",
    })
    return pd.concat([df, rafales_legitimes(rng, ref, jour)], ignore_index=True)


def rafales_legitimes(rng, ref, jour):
    """Faux positifs typiques : un client règle plusieurs factures et recharges d'affilée,
    ou un commerçant encaisse une série de paiements le jour du marché."""
    c = ref.comptes
    n = rng.poisson(len(c) * 0.0012)
    lignes = []
    for i in rng.integers(0, len(c), n):
        cp = c.iloc[int(i)]
        t = jour + timedelta(hours=float(np.clip(rng.normal(c.attrs["habitudes"]["heure"][i], 3), 0, 23.9)))
        dev = cp["device_principal"] if rng.random() < 0.8 else f"D{rng.integers(0, 2**48):012x}"
        pool = _marchands(ref, cp["ville"])
        for _ in range(int(rng.integers(5, 14))):
            t = t + timedelta(seconds=float(rng.uniform(10, 90)))
            typ = rng.choice(["FACTURE", "RECHARGE", "PAIEMENT"], p=[0.35, 0.25, 0.40])
            lignes.append({"ts": t, "compte_id": cp["compte_id"], "type": typ,
                           "montant": float(round(rng.uniform(1_000, 40_000), -1)), "devise": "XAF",
                           "compte_dest": None, "agent_id": rng.choice(pool) if typ == "PAIEMENT" else None,
                           "pays": cp["pays"], "ville": cp["ville"], "canal": "APP", "device_id": dev,
                           "est_fraude": 0, "scenario": "normal"})
    return pd.DataFrame(lignes, columns=COLONNES[1:])


# ---------------------------------------------------------------------------
# Scénarios de fraude
# ---------------------------------------------------------------------------
def _ligne(ts, compte, typ, montant, pays, ville, device, scenario, dest=None, agent=None, canal="APP"):
    return {"ts": ts, "compte_id": compte, "type": typ, "montant": float(round(montant, -1)),
            "devise": "XAF", "compte_dest": dest, "agent_id": agent, "pays": pays, "ville": ville,
            "canal": canal, "device_id": device, "est_fraude": 1, "scenario": scenario}


def _compte(rng, ref):
    i = int(rng.integers(0, len(ref.comptes)))
    return ref.comptes.iloc[i]


def _marchands(ref, ville):
    a = ref.agents
    pool = a[(a["ville"] == ville) & (a["type"] == "MARCHAND")]["agent_id"].to_numpy()
    return pool if len(pool) else a["agent_id"].to_numpy()


def fraude_rafale(rng, ref, t0):
    """Carte compromise : 8 à 20 paiements en quelques minutes chez des marchands différents."""
    c = _compte(rng, ref)
    # téléphone volé : la moitié du temps, c'est le vrai appareil du client
    dev = c["device_principal"] if rng.random() < 0.5 else f"D{rng.integers(0, 2**48):012x}"
    pool = _marchands(ref, c["ville"])
    n = int(rng.integers(8, 21))
    t = t0
    lignes = []
    for _ in range(n):
        t = t + timedelta(seconds=float(rng.uniform(5, 40)))
        lignes.append(_ligne(t, c["compte_id"], "PAIEMENT", rng.uniform(8_000, 45_000),
                             c["pays"], c["ville"], dev, "rafale", agent=rng.choice(pool)))
    return lignes


def fraude_nuit(rng, ref, t0):
    """Gros transferts entre 1 h et 4 h depuis un nouveau téléphone, vers un compte inconnu."""
    c = _compte(rng, ref)
    dev = c["device_principal"] if rng.random() < 0.3 else f"D{rng.integers(0, 2**48):012x}"
    t = t0.replace(hour=int(rng.integers(0, 6)) if rng.random() < 0.7 else int(rng.integers(19, 24)), minute=int(rng.integers(0, 60)))
    dest = ref.comptes.iloc[int(rng.integers(0, len(ref.comptes)))]["compte_id"]
    plafond = c["plafond_journalier"]
    lignes = []
    for k in range(int(rng.integers(1, 4))):
        lignes.append(_ligne(t + timedelta(minutes=7 * k), c["compte_id"], "TRANSFERT",
                             rng.uniform(0.1, 0.9) * plafond / 2, c["pays"], c["ville"], dev,
                             "nuit", dest=dest))
    return lignes


def fraude_anneau(rng, ref, t0):
    """Blanchiment : l'argent tourne entre 3 à 5 comptes, une commission est prélevée à chaque saut."""
    k = int(rng.integers(3, 6))
    membres = [_compte(rng, ref) for _ in range(k)]
    montant = rng.uniform(150_000, 600_000)
    t = t0
    lignes = []
    for tour in range(int(rng.integers(2, 4))):
        for i in range(k):
            a, b = membres[i], membres[(i + 1) % k]
            t = t + timedelta(hours=float(rng.uniform(1, 20)))
            lignes.append(_ligne(t, a["compte_id"], "TRANSFERT", montant, a["pays"], a["ville"],
                                 a["device_principal"], "anneau", dest=b["compte_id"]))
            montant *= rng.uniform(0.95, 0.99)
    return lignes


def fraude_agent(rng, ref, t0):
    """Agent complice : retraits fractionnés juste sous le seuil, pour des comptes différents."""
    a = ref.agents[ref.agents["type"] == "AGENT"]
    ag = a.iloc[int(rng.integers(0, len(a)))]
    locaux = ref.comptes[ref.comptes["ville"] == ag["ville"]]
    t = t0.replace(hour=int(rng.integers(9, 17)))
    lignes = []
    for _ in range(int(rng.integers(6, 15))):
        c = locaux.iloc[int(rng.integers(0, len(locaux)))]
        t = t + timedelta(minutes=float(rng.uniform(2, 25)))
        lignes.append(_ligne(t, c["compte_id"], "RETRAIT", rng.uniform(300_000, 499_900),
                             c["pays"], c["ville"], c["device_principal"], "agent",
                             agent=ag["agent_id"], canal="USSD"))
    return lignes


def fraude_sim_swap(rng, ref, t0):
    """Prise de contrôle après échange de carte SIM : le compte est vidé depuis un nouveau téléphone.
    Le changement de numéro arrive dans PostgreSQL (donc par le CDC) quelques minutes avant."""
    c = _compte(rng, ref)
    dev = f"D{rng.integers(0, 2**48):012x}"
    t = t0 + timedelta(minutes=float(rng.uniform(3, 30)))
    dest = ref.comptes.iloc[int(rng.integers(0, len(ref.comptes)))]["compte_id"]
    lignes = [_ligne(t, c["compte_id"], "TRANSFERT", c["plafond_journalier"] * rng.uniform(0.3, 0.5),
                     c["pays"], c["ville"], dev, "sim_swap", dest=dest)]
    ag = ref.agents[(ref.agents["ville"] == c["ville"]) & (ref.agents["type"] == "AGENT")]["agent_id"].to_numpy()
    lignes.append(_ligne(t + timedelta(minutes=2), c["compte_id"], "RETRAIT",
                         c["plafond_journalier"] * rng.uniform(0.2, 0.4), c["pays"], c["ville"], dev,
                         "sim_swap", agent=rng.choice(ag) if len(ag) else None, canal="USSD"))
    return lignes, {"compte_id": c["compte_id"], "ts_changement": t0,
                    "nouveau_telephone": f"{PAYS[c['pays']]['indicatif']}6{rng.integers(10**7, 10**8 - 1)}"}


SCENARIOS = {"rafale": fraude_rafale, "nuit": fraude_nuit, "anneau": fraude_anneau,
             "agent": fraude_agent, "sim_swap": fraude_sim_swap}
# nombre moyen d'épisodes de chaque scénario par jour
FREQ_JOUR = {"rafale": 6, "nuit": 9, "anneau": 1.2, "agent": 1.0, "sim_swap": 5}


def fraudes_du_jour(rng, ref, jour):
    lignes, changements = [], []
    for nom, f in SCENARIOS.items():
        for _ in range(rng.poisson(FREQ_JOUR[nom])):
            t0 = jour + timedelta(hours=float(rng.uniform(0, 23)))
            r = f(rng, ref, t0)
            if nom == "sim_swap":
                r, ch = r
                changements.append(ch)
            lignes.extend(r)
    return pd.DataFrame(lignes, columns=COLONNES[1:]), changements


# ---------------------------------------------------------------------------
# Sous-commande init
# ---------------------------------------------------------------------------
def charger_referentiel(graine: int, n_comptes: int, n_agents: int, debut: datetime) -> Referentiel:
    rng = np.random.default_rng(graine)
    return Referentiel(creer_comptes(rng, n_comptes, debut), creer_agents(rng, n_agents, debut))


def cmd_init(a):
    out = Path(a.sortie)
    debut = datetime.fromisoformat(a.debut).replace(tzinfo=timezone.utc)
    ref = charger_referentiel(a.graine, a.comptes, a.agents, debut)
    rng = np.random.default_rng(a.graine + 1)
    (out / "historique").mkdir(parents=True, exist_ok=True)
    (out / "agents").mkdir(parents=True, exist_ok=True)
    ref.comptes.to_csv(out / "comptes.csv", index=False)
    ref.agents.to_csv(out / "agents" / f"agents_{debut:%Y%m%d}.csv", index=False)

    # Le jeu de test suit l'historique, mais il est tiré avec une graine secrète connue
    # de l'enseignant seul : sans elle, impossible de régénérer les étiquettes cachées.
    jours_test = a.jours_test if a.graine_test is not None else 0
    rng_test = np.random.default_rng(a.graine_test) if jours_test else None
    test_dir = Path(a.test_sortie) if a.test_sortie else out / "_enseignant"
    cpt = 0
    tests, changements = [], []
    for d in range(a.jours + jours_test):
        jour = debut + timedelta(days=d)
        if d >= a.jours:
            rng = rng_test
        df = transactions_normales(rng, ref, jour)
        fr, ch = fraudes_du_jour(rng, ref, jour)
        changements.extend(ch)
        df = pd.concat([df, fr], ignore_index=True).sort_values("ts", kind="stable")
        prefixe = "T" if d < a.jours else "X"
        df["tx_id"] = [f"{prefixe}{cpt + i:09d}" for i in range(len(df))]
        cpt += len(df)
        df["ts"] = pd.to_datetime(df["ts"], utc=True)
        df = df[COLONNES]
        if d < a.jours:
            # les étudiants voient l'étiquette, mais pas le nom du scénario
            # étiquettes retardées : une fraude est confirmée en moyenne 10 jours après les faits,
            # donc une partie des fraudes récentes est encore marquée 0
            reste = a.jours - d
            if reste <= 14:
                pas_encore = (df["est_fraude"] == 1) & (rng.random(len(df)) < (15 - reste) / 20)
                df.loc[pas_encore, "est_fraude"] = 0
            df.drop(columns=["scenario"]).to_parquet(out / "historique" / f"tx_{jour:%Y%m%d}.parquet", index=False)
        else:
            tests.append(df)
        print(f"  {jour:%Y-%m-%d} : {len(df):>7} transactions, {int(df['est_fraude'].sum()):>4} frauduleuses",
              file=sys.stderr)
    if tests:
        test = pd.concat(tests, ignore_index=True)
        # jeu de test : sans étiquette pour les étudiants, avec étiquette pour l'enseignant
        test_dir.mkdir(parents=True, exist_ok=True)
        test.drop(columns=["est_fraude", "scenario"]).to_parquet(test_dir / "test_sans_etiquette.parquet", index=False)
        test[["tx_id", "est_fraude", "scenario"]].to_parquet(test_dir / "verite_test.parquet", index=False)
        print(f"Jeu de test : {len(test)} transactions → {test_dir}", file=sys.stderr)
    print(f"Terminé : {cpt} transactions, {len(ref.comptes)} comptes, {len(ref.agents)} agents → {out}",
          file=sys.stderr)


# ---------------------------------------------------------------------------
# Sous-commandes flux et scenario
# ---------------------------------------------------------------------------
SCHEMA_AVRO = Path(__file__).resolve().parent.parent / "schemas" / "transaction.avsc"


def vers_avro(ev: dict, ctx=None) -> dict:
    """Adapte un événement JSON au schéma Avro (horodatage en millisecondes)."""
    d = dict(ev)
    d["ts"] = int(datetime.fromisoformat(ev["ts"]).timestamp() * 1000)
    return d


class Sortie:
    def __init__(self, vers, topic, bootstrap, fichier, format_="json", registry=None):
        self.vers, self.topic, self.format = vers, topic, format_
        if vers == "kafka":
            from confluent_kafka import Producer   # pip install confluent-kafka
            self.p = Producer({"bootstrap.servers": bootstrap, "enable.idempotence": True,
                               "linger.ms": 20, "compression.type": "lz4"})
            if format_ == "avro":
                # le schéma est enregistré dans le Schema Registry au premier envoi
                from confluent_kafka.schema_registry import SchemaRegistryClient
                from confluent_kafka.schema_registry.avro import AvroSerializer
                from confluent_kafka.serialization import MessageField, SerializationContext
                schema = (Path(os.environ.get("SCHEMA_AVRO", SCHEMA_AVRO))).read_text()
                self.ser = AvroSerializer(SchemaRegistryClient({"url": registry}), schema, vers_avro)
                self.ctx = SerializationContext(topic, MessageField.VALUE)
        elif vers == "fichier":
            self.f = open(fichier, "a", encoding="utf-8")

    def envoyer(self, ev: dict):
        ligne = json.dumps(ev, ensure_ascii=False)
        if self.vers == "kafka":
            # la clé = compte : tous les événements d'un compte vont dans la même partition
            valeur = self.ser(ev, self.ctx) if self.format == "avro" else ligne.encode()
            self.p.produce(self.topic, key=ev["compte_id"], value=valeur)
            self.p.poll(0)
        elif self.vers == "fichier":
            self.f.write(ligne + "\n")
        else:
            print(ligne, flush=True)

    def fermer(self):
        if self.vers == "kafka":
            self.p.flush(10)
        elif self.vers == "fichier":
            self.f.close()


def _evenement(row, maintenant):
    ev = {k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in row.items()}
    ev["ts"] = maintenant.isoformat(timespec="milliseconds")
    ev["tx_id"] = f"L{uuid.uuid4().hex[:16]}"
    ev.pop("est_fraude", None)
    ev.pop("scenario", None)      # la vérité ne voyage pas dans le flux
    return ev


def _maj_postgres(dsn, ch):
    import psycopg   # pip install "psycopg[binary]"
    with psycopg.connect(dsn, autocommit=True) as cx:
        cx.execute("UPDATE comptes SET telephone = %s, maj_le = now() WHERE compte_id = %s",
                   (ch["nouveau_telephone"], ch["compte_id"]))


def cmd_flux(a):
    debut = datetime.fromisoformat(a.debut).replace(tzinfo=timezone.utc)
    ref = charger_referentiel(a.graine, a.comptes, a.agents, debut)
    rng = np.random.default_rng(int(time.time()) if a.graine_flux is None else a.graine_flux)
    sortie = Sortie(a.vers, a.topic, a.bootstrap, a.fichier, a.format, a.registry)
    journal = open(a.journal, "a", encoding="utf-8") if a.journal else None
    periode = 1.0 / a.debit
    fin = time.time() + a.duree if a.duree else None
    file = []
    envoyes = 0
    t_debut = time.time()
    try:
        while fin is None or time.time() < fin:
            if not file:
                jour = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                lot = transactions_normales(rng, ref, jour, facteur=0.02).sample(frac=1, random_state=int(rng.integers(1e9)))
                file = lot.to_dict("records")
                # une fraude toutes les ~ (1 / taux) transactions
                # nombre d'épisodes de fraude dans ce lot (un épisode ≈ 6 transactions)
                for _ in range(rng.poisson(a.taux_fraude * len(file) / 6)):
                    nom = rng.choice(list(SCENARIOS), p=np.array(list(FREQ_JOUR.values())) / sum(FREQ_JOUR.values()))
                    file = _inserer_scenario(rng, ref, nom, file, a, journal, pos=int(rng.integers(0, len(file))))
            row = file.pop()
            maintenant = datetime.now(timezone.utc)
            ev = _evenement(row, maintenant)
            sortie.envoyer(ev)
            if journal and row.get("est_fraude"):
                journal.write(json.dumps({"tx_id": ev["tx_id"], "scenario": row["scenario"], "ts": ev["ts"]}) + "\n")
                journal.flush()
            envoyes += 1
            # cadence fixe : on vise l'instant théorique du prochain envoi
            retard = t_debut + envoyes * periode - time.time()
            if retard > 0:
                time.sleep(retard)
    except KeyboardInterrupt:
        pass
    finally:
        sortie.fermer()
        print(f"{envoyes} événements émis", file=sys.stderr)


def _inserer_scenario(rng, ref, nom, file, a, journal, pos):
    r = SCENARIOS[nom](rng, ref, datetime.now(timezone.utc))
    if nom == "sim_swap":
        r, ch = r
        if a.pg:
            _maj_postgres(a.pg, ch)
    # les lignes d'un épisode sont jouées d'affilée (pop() lit la file par la fin)
    return file[:pos] + [dict(x) for x in reversed(r)] + file[pos:]


def cmd_scenario(a):
    debut = datetime.fromisoformat(a.debut).replace(tzinfo=timezone.utc)
    ref = charger_referentiel(a.graine, a.comptes, a.agents, debut)
    rng = np.random.default_rng(a.graine_flux or int(time.time()))
    sortie = Sortie(a.vers, a.topic, a.bootstrap, a.fichier, a.format, a.registry)
    r = SCENARIOS[a.nom](rng, ref, datetime.now(timezone.utc))
    if a.nom == "sim_swap":
        r, ch = r
        if a.pg:
            _maj_postgres(a.pg, ch)
            print(f"téléphone modifié dans PostgreSQL pour {ch['compte_id']}", file=sys.stderr)
    for row in r:
        ev = _evenement(row, datetime.now(timezone.utc))
        sortie.envoyer(ev)
        print(f"  {a.nom} → {ev['tx_id']} {ev['compte_id']} {ev['type']} {ev['montant']:.0f} XAF", file=sys.stderr)
        time.sleep(a.pause)
    sortie.fermer()


def cmd_agents(a):
    """Fichier nocturne des agents du jour J : quelques créations, suspensions,
    et des défauts de qualité volontaires (à attraper avec Great Expectations)."""
    debut = datetime.fromisoformat(a.debut).replace(tzinfo=timezone.utc)
    ref = charger_referentiel(a.graine, a.comptes, a.agents, debut)
    jour = datetime.fromisoformat(a.jour)
    rng = np.random.default_rng(a.graine + int(jour.strftime("%Y%m%d")))
    df = ref.agents.copy()
    # agents suspendus depuis le début (évolution progressive, reproductible)
    n_jours = max((jour.date() - debut.date()).days, 0)
    susp = rng.random(len(df)) < min(0.0004 * n_jours, 0.05)
    df.loc[susp, "statut"] = "SUSPENDU"
    nouveaux = creer_agents(rng, 5 + n_jours // 2, jour)
    nouveaux["agent_id"] = [f"AG{len(df) + i + 1:05d}" for i in range(len(nouveaux))]
    df = pd.concat([df, nouveaux], ignore_index=True)
    defauts = []
    if not a.propre:
        k = int(rng.integers(3, 12))
        lignes = rng.choice(len(df), k, replace=False)
        for j, i in enumerate(lignes):
            sorte = ["doublon", "ville_vide", "type_inconnu", "date_future", "pays_inconnu"][j % 5]
            if sorte == "doublon":
                df = pd.concat([df, df.iloc[[i]]], ignore_index=True)
            elif sorte == "ville_vide":
                df.loc[i, "ville"] = None
            elif sorte == "type_inconnu":
                df.loc[i, "type"] = "Agent "          # casse et espace parasites
            elif sorte == "date_future":
                df.loc[i, "date_agrement"] = "2031-01-01"
            else:
                df.loc[i, "pays"] = "XX"
            defauts.append({"agent_id": df.loc[i, "agent_id"], "defaut": sorte})
    sortie = Path(a.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    f = sortie / f"agents_{jour:%Y%m%d}.csv"
    df.to_csv(f, index=False)
    print(f"{f} : {len(df)} lignes, {int(susp.sum())} suspendus, {len(nouveaux)} nouveaux, "
          f"{len(defauts)} défauts injectés", file=sys.stderr)
    if a.journal_defauts:
        pd.DataFrame(defauts).to_csv(a.journal_defauts, index=False)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--graine", type=int, default=2026)
    p.add_argument("--comptes", type=int, default=100_000)
    p.add_argument("--agents", type=int, default=5_000)
    p.add_argument("--debut", default="2026-09-01")
    sp = p.add_subparsers(dest="cmd", required=True)

    i = sp.add_parser("init", help="crée le référentiel et l'historique")
    i.add_argument("--sortie", default="data")
    i.add_argument("--jours", type=int, default=60, help="jours d'historique étiqueté")
    i.add_argument("--jours-test", type=int, default=14, help="jours du jeu de test caché")
    i.add_argument("--graine-test", type=int, default=None,
                   help="graine secrète du jeu de test (enseignant uniquement)")
    i.add_argument("--test-sortie", default=None, help="dossier de la vérité terrain (enseignant)")
    i.set_defaults(f=cmd_init)

    g = sp.add_parser("agents", help="fichier nocturne des agents d'un jour donné")
    g.add_argument("--jour", required=True, help="AAAA-MM-JJ")
    g.add_argument("--sortie", default="data/agents")
    g.add_argument("--propre", action="store_true", help="sans défauts de qualité")
    g.add_argument("--journal-defauts", default=None, help="CSV des défauts injectés (enseignant)")
    g.set_defaults(f=cmd_agents)

    for nom, aide in (("flux", "émet un flux continu"), ("scenario", "injecte un scénario de fraude")):
        s = sp.add_parser(nom, help=aide)
        if nom == "scenario":
            s.add_argument("nom", choices=list(SCENARIOS))
            s.add_argument("--pause", type=float, default=0.5)
        s.add_argument("--vers", choices=["kafka", "fichier", "stdout"], default="stdout")
        s.add_argument("--topic", default="transactions.brutes")
        s.add_argument("--bootstrap", default="localhost:9092")
        s.add_argument("--fichier", default="flux.jsonl")
        s.add_argument("--format", choices=["json", "avro"], default="json",
                       help="avro : sérialisation via le Schema Registry (bonus J4)")
        s.add_argument("--registry", default="http://localhost:8081")
        s.add_argument("--debit", type=float, default=200, help="transactions par seconde")
        s.add_argument("--duree", type=float, default=None, help="secondes (vide = sans fin)")
        s.add_argument("--taux-fraude", type=float, default=0.004)
        s.add_argument("--graine-flux", type=int, default=None)
        s.add_argument("--pg", default=None, help="DSN PostgreSQL pour le scénario sim_swap")
        s.add_argument("--journal", default=None, help="fichier où noter les fraudes émises (enseignant)")
        s.set_defaults(f=cmd_flux if nom == "flux" else cmd_scenario)

    a = p.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
