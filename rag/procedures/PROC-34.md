---
id: PROC-34
titre: "Délais de traitement des alertes"
version: 1
date: 2026-04-14
habilitation: analyste
---

# PROC-34 — Délais de traitement des alertes

## Objet

Les alertes sont traitées selon leur priorité.

## Déroulement

1. La priorité est calculée à partir du score, du montant et du scénario détecté.
2. La console trie la file d'alertes par priorité puis par ancienneté.

## Règles et seuils

- Priorité haute : prise en charge sous 15 minutes.
- Priorité moyenne : sous 2 heures.
- Priorité basse : sous 24 heures.
- Le taux d'alertes traitées dans les délais est un indicateur suivi par la direction (PROC-39).
