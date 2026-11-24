---
id: PROC-15
titre: "Anneaux de virements"
version: 1
date: 2026-07-01
habilitation: analyste
---

# PROC-15 — Anneaux de virements

## Objet

Un anneau est un circuit où l'argent passe d'un compte à l'autre et revient au point de départ, souvent pour brouiller son origine.

## Déroulement

1. Lancer la requête de recherche de cycles dans le graphe des virements (3 à 5 comptes, moins de 7 jours).
2. Observer les montants : dans un anneau, ils diminuent souvent de 1 à 5 % à chaque saut (commission des mules).
3. Rechercher les autres virements des membres de l'anneau pour trouver le compte d'entrée et le compte de sortie.
4. Préparer une note pour la déclaration de soupçon (PROC-14).

## Règles et seuils

- Un cycle de virements entre membres d'une même famille n'est pas suspect en soi ; c'est la répétition et la décroissance des montants qui alertent.
- Les requêtes sur le graphe se limitent à 5 sauts pour rester rapides.
