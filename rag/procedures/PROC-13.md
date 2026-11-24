---
id: PROC-13
titre: "Retraits fractionnés chez un agent"
version: 1
date: 2026-06-08
habilitation: analyste
---

# PROC-13 — Retraits fractionnés chez un agent

## Objet

Le fractionnement consiste à découper un gros retrait en plusieurs retraits juste sous le seuil de contrôle.

## Déroulement

1. Repérer les agents qui enregistrent plusieurs retraits entre 300 000 et 499 999 XAF dans la même heure, pour des comptes différents.
2. Vérifier si ces comptes ont un lien entre eux (virements, même appareil, même ville d'ouverture).
3. Croiser avec le segment : certains commerçants retirent légitimement de gros montants plusieurs fois par semaine.
4. Si le doute persiste, ouvrir un dossier et proposer la suspension de l'agent (PROC-12).

## Règles et seuils

- Le seuil de contrôle renforcé chez un agent est de 500 000 XAF par opération.
- Au-delà de 5 retraits fractionnés par heure chez un même agent, le dossier passe en priorité haute.
