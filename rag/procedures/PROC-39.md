---
id: PROC-39
titre: "Indicateurs de pilotage de la fraude"
version: 1
date: 2026-10-01
habilitation: superviseur
---

# PROC-39 — Indicateurs de pilotage de la fraude

## Objet

La direction suit chaque semaine un tableau de bord de la fraude.

## Déroulement

1. Le tableau de bord est mis à jour chaque nuit par le pipeline.

## Règles et seuils

- Taux de fraude : montant fraudé divisé par le volume total, en points de base.
- Taux de détection : part des fraudes confirmées qui avaient déclenché une alerte.
- Taux de faux positifs : part des alertes marquées FAUX_POSITIF.
- Respect des délais : part des alertes traitées dans les délais de la PROC-34.
- Objectif 2026 : taux de fraude inférieur à 5 points de base.
