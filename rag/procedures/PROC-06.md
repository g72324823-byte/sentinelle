---
id: PROC-06
titre: "Plafonds par niveau de vérification d'identité (KYC)"
version: 1
date: 2026-01-10
habilitation: public
---

# PROC-06 — Plafonds par niveau de vérification d'identité (KYC)

## Objet

Les plafonds d'opérations dépendent du niveau de vérification d'identité du client.

## Déroulement

1. Le niveau KYC est affiché sur la fiche du compte.
2. Une opération qui dépasse le plafond journalier est refusée par le système, sans intervention humaine.
3. Le client qui veut un plafond plus élevé doit passer au niveau supérieur (PROC-07 et PROC-08).

## Règles et seuils

- Niveau 1 : 200 000 XAF par jour.
- Niveau 2 : 1 000 000 XAF par jour.
- Niveau 3 : 5 000 000 XAF par jour.
- Un commerçant est au moins au niveau 2.
