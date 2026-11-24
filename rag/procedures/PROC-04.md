---
id: PROC-04
titre: "Échange de carte SIM suspect (SIM swap)"
version: 1
date: 2026-05-20
habilitation: analyste
---

# PROC-04 — Échange de carte SIM suspect (SIM swap)

## Objet

Un fraudeur obtient un duplicata de la carte SIM du client, change le numéro rattaché au compte, puis vide le compte.

## Déroulement

1. Toute modification du numéro de téléphone est visible en temps réel par le flux CDC des comptes.
2. Si un transfert ou un retrait important suit un changement de numéro de moins de 60 minutes, bloquer immédiatement le compte.
3. Prévenir l'opérateur télécom par le canal dédié pour vérifier la date du duplicata.
4. Appeler le client sur son ancien numéro et, à défaut, sur le numéro de secours déclaré à l'ouverture.

## Règles et seuils

- Après un changement de numéro, le plafond est réduit à 50 000 XAF pendant 24 heures.
- Cette règle s'applique même si le nouveau numéro vient du même opérateur.
