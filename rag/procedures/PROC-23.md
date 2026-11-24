---
id: PROC-23
titre: "Liste noire des appareils"
version: 1
date: 2026-05-20
habilitation: analyste
---

# PROC-23 — Liste noire des appareils

## Objet

Un appareil utilisé pour une fraude confirmée est mis en liste noire.

## Déroulement

1. Ajouter l'identifiant de l'appareil depuis la fiche de l'alerte.
2. Toute opération future depuis cet appareil est refusée, quel que soit le compte.

## Règles et seuils

- Un appareil reste en liste noire 12 mois.
- Un retrait de liste noire demande l'accord d'un superviseur.
