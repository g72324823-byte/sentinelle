---
id: PROC-03
titre: "Traitement d'une alerte de rafale de paiements"
version: 1
date: 2026-04-14
habilitation: analyste
---

# PROC-03 — Traitement d'une alerte de rafale de paiements

## Objet

Une rafale est une série de paiements rapprochés chez des marchands différents, souvent signe d'un téléphone volé.

## Déroulement

1. Regarder le nombre de paiements sur 10 minutes et la liste des marchands.
2. Vérifier si l'appareil est le téléphone habituel du client. Attention : un téléphone volé reste l'appareil habituel.
3. Comparer avec les habitudes : un client qui règle ses factures et recharges d'affilée en fin de mois n'est pas suspect.
4. En cas de doute, bloquer en préventif (PROC-01) et appeler le client.

## Règles et seuils

- Seuil d'alerte par défaut : 8 paiements ou plus en 10 minutes.
- Les factures (FACTURE) et recharges (RECHARGE) groupées sont la première cause de faux positifs sur cette règle.
