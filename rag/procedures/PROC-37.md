---
id: PROC-37
titre: "Mode dégradé en cas de panne du scoring"
version: 1
date: 2026-09-09
habilitation: superviseur
---

# PROC-37 — Mode dégradé en cas de panne du scoring

## Objet

Si l'API de scoring ou le flux temps réel tombe, les transactions ne doivent pas être bloquées en masse.

## Déroulement

1. Le système bascule automatiquement sur les règles simples (plafonds, liste noire des appareils, changement de SIM récent).
2. Le superviseur d'astreinte est prévenu automatiquement.
3. Au retour du service, les transactions de la période de panne sont rescorées et les alertes générées a posteriori.

## Règles et seuils

- Bascule automatique si l'API dépasse 500 ms pendant plus de 30 secondes.
- Le mode dégradé ne doit pas durer plus de 4 heures sans décision de la direction.
