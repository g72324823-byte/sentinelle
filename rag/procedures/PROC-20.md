---
id: PROC-20
titre: "Retour des décisions vers le modèle"
version: 1
date: 2026-08-19
habilitation: analyste
---

# PROC-20 — Retour des décisions vers le modèle

## Objet

Chaque décision d'analyste devient une étiquette pour le prochain entraînement du modèle.

## Déroulement

1. Marquer chaque alerte traitée : FRAUDE_CONFIRMEE, FAUX_POSITIF ou A_REVOIR.
2. Les décisions sont écrites dans la table decisions de la base opérationnelle.
3. Le pipeline nocturne les copie dans la couche or du lakehouse.

## Règles et seuils

- Une fraude est confirmée en moyenne 10 jours après les faits : les étiquettes des deux dernières semaines sont donc incomplètes.
- Les alertes A_REVOIR de plus de 30 jours sont exclues de l'entraînement.
