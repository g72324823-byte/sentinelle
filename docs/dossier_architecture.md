# Dossier d'architecture — équipe ……

> Modèle à compléter. Version 1 au jalon J2, version finale avec le rendu J6.
> 15 pages au plus hors annexes. Chaque choix est justifié par un argument ou une mesure.

## 1. Vue d'ensemble
- Schéma de l'architecture (sources → ingestion → stockage → traitements → restitution).
- Ce qui tourne en temps réel, ce qui tourne en lot, et pourquoi.

## 2. Données
- Modèle des couches bronze / argent / or : tables, partitionnement, format.
- Contrats de données : schéma Avro du flux, tests dbt, contrôles Great Expectations.

## 3. Choix de stockage
| Besoin | Technologie | Pourquoi pas une autre ? |
|---|---|---|
| Historique analytique | | |
| Features en ligne | | |
| Graphe des virements | | |
| Recherche dans les procédures | | |

## 4. Répartition et cohérence
- Où se situe chaque composant dans CAP / PACELC ? Que se passe-t-il si un nœud tombe ?
- Clé de partitionnement des topics Kafka et conséquence sur l'ordre des événements.

## 5. Temps réel
- Features calculées, fenêtres, watermark, garanties de livraison (au moins une fois, exactement une fois).
- Latence mesurée de bout en bout (méthode et résultats).

## 6. Modèle
- Features, découpage temporel, traitement des étiquettes retardées, métrique, seuils.
- Comparaison des versions dans MLflow, critère de promotion, suivi de dérive (PSI).

## 7. Assistant RAG
- Découpage, modèle d'embeddings, recherche hybride, rappel@5 mesuré, gestion des habilitations.

## 8. Limites connues et pistes
- Ce qui ne passerait pas à 10 fois la charge, et ce qu'il faudrait changer.
