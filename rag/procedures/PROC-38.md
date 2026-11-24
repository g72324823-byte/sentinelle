---
id: PROC-38
titre: "Incidents de qualité des données"
version: 1
date: 2026-09-09
habilitation: analyste
---

# PROC-38 — Incidents de qualité des données

## Objet

Un fichier ou un flux arrive incomplet ou faux (doublons, champs vides, valeurs inconnues).

## Déroulement

1. Le pipeline nocturne contrôle le fichier des agents avant tout chargement.
2. Les lignes en erreur sont mises en quarantaine ; les lignes valides sont chargées.
3. Si plus de 1 % des lignes sont en erreur, le chargement est arrêté et l'équipe données est prévenue.

## Règles et seuils

- Le fournisseur du fichier dispose de 24 heures pour corriger.
- Chaque incident est noté dans le registre des incidents avec sa cause.
