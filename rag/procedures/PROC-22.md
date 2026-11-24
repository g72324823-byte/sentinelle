---
id: PROC-22
titre: "Seuils de décision du score"
version: 1
date: 2026-08-19
habilitation: analyste
---

# PROC-22 — Seuils de décision du score

## Objet

Le modèle donne un score entre 0 et 1. Deux seuils transforment ce score en décision.

## Déroulement

1. Score inférieur à 0,50 : la transaction est acceptée.
2. Score entre 0,50 et 0,90 : la transaction passe, mais une alerte est créée pour vérification.
3. Score supérieur ou égal à 0,90 : la transaction est bloquée et le compte passe en blocage préventif.

## Règles et seuils

- L'API de scoring doit répondre en moins de 200 ms dans 95 % des cas.
- Si l'API ne répond pas à temps, on applique le mode dégradé (PROC-37).
