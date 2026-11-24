---
id: PROC-17
titre: "Conservation des données et des dossiers"
version: 1
date: 2025-10-01
habilitation: public
---

# PROC-17 — Conservation des données et des dossiers

## Objet

Cette procédure fixe les durées de conservation des données chez Dalla Pay.

## Déroulement

1. Les données de transaction sont conservées dans le lakehouse, partitionnées par jour.
2. Les dossiers de fraude et de déclaration sont archivés à leur clôture.
3. Les données à caractère personnel sont pseudonymisées dans les environnements d'analyse.

## Règles et seuils

- Transactions : 10 ans.
- Dossiers de fraude et déclarations : 10 ans après clôture.
- Journaux techniques : 1 an.
- Enregistrements d'appels : 6 mois.
