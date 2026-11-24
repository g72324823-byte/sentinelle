---
id: PROC-02
titre: "Déblocage d'un compte après vérification"
version: 1
date: 2026-03-02
habilitation: analyste
---

# PROC-02 — Déblocage d'un compte après vérification

## Objet

Cette procédure décrit la levée d'un blocage quand la fraude n'est pas confirmée.

## Déroulement

1. Joindre le client par l'appel de vérification (PROC-05).
2. Si le client reconnaît toutes les opérations, lever le blocage depuis la console.
3. Marquer l'alerte FAUX_POSITIF pour qu'elle alimente le réentraînement (PROC-20).
4. Envoyer le SMS modèle B2 de levée de blocage.

## Règles et seuils

- Le déblocage doit intervenir dans les 4 heures ouvrées après l'appel réussi.
- Si le client ne répond pas après 3 tentatives sur 24 heures, le compte reste bloqué et le dossier passe au superviseur.
