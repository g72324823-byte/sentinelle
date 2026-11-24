---
id: PROC-21
titre: "Réentraînement et mise en production du modèle"
version: 1
date: 2026-08-19
habilitation: superviseur
---

# PROC-21 — Réentraînement et mise en production du modèle

## Objet

Le modèle de score est réentraîné quand ses données changent trop ou quand sa performance baisse.

## Déroulement

1. Le suivi quotidien calcule l'indice de stabilité de population (PSI) des principales variables.
2. Un PSI supérieur à 0,25 sur une variable déclenche un réentraînement.
3. Le nouveau modèle est comparé au modèle en production sur la même période de validation.
4. Il n'est promu (alias champion dans le registre) que si sa PR-AUC est meilleure et validée par le comité modèle.

## Règles et seuils

- PSI inférieur à 0,10 : stable. Entre 0,10 et 0,25 : à surveiller. Au-delà de 0,25 : dérive.
- Le comité modèle se réunit chaque premier mardi du mois, ou en urgence sur demande.
