-- J4 — Features par fenêtres et règles d'alerte (À COMPLÉTER)

-- Exemple fourni : nombre de transactions par compte sur une fenêtre glissante
-- de 10 minutes, recalculée toutes les minutes.
CREATE VIEW nb_tx_10min AS
SELECT window_start, window_end, compte_id, COUNT(*) AS nb, SUM(montant) AS somme
FROM TABLE(HOP(TABLE transactions, DESCRIPTOR(ts), INTERVAL '1' MINUTE, INTERVAL '10' MINUTE))
GROUP BY window_start, window_end, compte_id;

-- TODO 1 : règle « rafale » : plus de N paiements en 10 minutes → INSERT INTO alertes.
--          Choisissez N à partir de l'historique (requête Spark ou DuckDB) et justifiez-le.
-- TODO 2 : règle « agent » : retraits d'un même agent proches de 500 000 XAF sur 1 heure.
-- TODO 3 : jointure temporelle avec la table comptes (FOR SYSTEM_TIME AS OF) pour
--          détecter un appareil différent de device_principal.
-- TODO 4 : écrire les features par compte dans Valkey (ou dans un topic lu par l'API)
--          pour que l'API de scoring les retrouve en moins de 5 ms.
-- Bonus  : features par fenêtre de session (SESSION), gestion des retardataires.
