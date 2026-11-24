---
id: PROC-01
titre: "Blocage préventif d'un compte suspect"
version: 1
date: 2026-03-02
habilitation: analyste
---

# PROC-01 — Blocage préventif d'un compte suspect

## Objet

Cette procédure dit quand et comment un analyste bloque un compte avant d'avoir la preuve d'une fraude.

## Déroulement

1. Vérifier que l'alerte concerne bien le compte (identifiant et numéro de téléphone).
2. Consulter les 30 derniers jours d'opérations du compte dans la console Sentinelle.
3. Si le score du modèle dépasse 0,90 ou si deux règles ont déclenché en moins d'une heure, poser un blocage préventif.
4. Choisir le motif dans la liste (rafale, prise de contrôle, mule, autre) et rédiger un commentaire d'au moins une phrase.
5. Envoyer au client le SMS modèle B1 (voir PROC-33).

## Règles et seuils

- Un blocage préventif dure au plus 48 heures. Passé ce délai, il est levé automatiquement sauf prolongation par un superviseur.
- Un analyste ne peut pas bloquer plus de 20 comptes par heure sans validation d'un superviseur.
- Un compte commerçant ne se bloque pas en préventif : on suspend seulement les retraits (voir PROC-12).
