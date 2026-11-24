#!/usr/bin/env python3
"""Simule la vie de la base des comptes pour alimenter le CDC (Debezium).

Chaque seconde, quelques comptes changent : passage au niveau KYC supérieur,
nouveau plafond, suspension, changement de téléphone ou d'appareil.
Ces UPDATE apparaissent dans le topic Kafka `dallapay.public.comptes`.

Usage : python maj_comptes.py --pg "postgresql://postgres:sentinelle@localhost:5432/dallapay" --par-seconde 2
"""
import argparse
import random
import sys
import time

import psycopg

PLAFOND = {1: 200_000, 2: 1_000_000, 3: 5_000_000}

REQUETES = {
    # poids, requête
    "kyc": (40, """UPDATE comptes SET kyc_niveau = kyc_niveau + 1,
                   plafond_journalier = CASE kyc_niveau + 1 WHEN 2 THEN 1000000 ELSE 5000000 END,
                   maj_le = now()
                   WHERE compte_id = %s AND kyc_niveau < 3"""),
    "appareil": (35, """UPDATE comptes SET device_principal = 'D' || substr(md5(random()::text), 1, 12),
                        maj_le = now() WHERE compte_id = %s"""),
    "telephone": (10, """UPDATE comptes SET telephone = left(telephone, 5) || (60000000 + floor(random() * 39999999))::bigint,
                         maj_le = now() WHERE compte_id = %s"""),
    "suspension": (10, "UPDATE comptes SET statut = 'SUSPENDU', maj_le = now() WHERE compte_id = %s AND statut = 'ACTIF'"),
    "reactivation": (5, "UPDATE comptes SET statut = 'ACTIF', maj_le = now() WHERE compte_id = %s AND statut = 'SUSPENDU'"),
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pg", default="postgresql://postgres:sentinelle@localhost:5432/dallapay")
    p.add_argument("--par-seconde", type=float, default=2)
    p.add_argument("--duree", type=float, default=None)
    p.add_argument("--graine", type=int, default=None)
    a = p.parse_args()
    rnd = random.Random(a.graine)
    noms = list(REQUETES)
    poids = [REQUETES[n][0] for n in noms]
    with psycopg.connect(a.pg, autocommit=True) as cx:
        ids = [r[0] for r in cx.execute("SELECT compte_id FROM comptes")]
        suspendus = [r[0] for r in cx.execute("SELECT compte_id FROM comptes WHERE statut = 'SUSPENDU'")]
        fin = time.time() + a.duree if a.duree else None
        n = 0
        while fin is None or time.time() < fin:
            nom = rnd.choices(noms, poids)[0]
            cible = rnd.choice(suspendus) if nom == "reactivation" and suspendus else rnd.choice(ids)
            cur = cx.execute(REQUETES[nom][1], (cible,))
            if cur.rowcount:
                n += 1
                if nom == "suspension":
                    suspendus.append(cible)
                print(f"{nom:<12} {cible}", flush=True)
            time.sleep(1 / a.par_seconde)
    print(f"{n} mises à jour", file=sys.stderr)


if __name__ == "__main__":
    main()
