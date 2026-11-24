---
id: PROC-19
titre: "Astreinte de nuit"
version: 1
date: 2026-04-14
habilitation: analyste
---

# PROC-19 — Astreinte de nuit

## Objet

Entre 22 heures et 6 heures, une équipe réduite traite les alertes.

## Déroulement

1. Deux analystes et un superviseur joignable sont d'astreinte chaque nuit.
2. Seules les alertes de priorité haute sont traitées en temps réel ; les autres attendent 6 heures.
3. Les gros transferts de nuit depuis un nouvel appareil sont toujours en priorité haute.

## Règles et seuils

- La nuit, le seuil de blocage automatique du score passe de 0,90 à 0,85.
