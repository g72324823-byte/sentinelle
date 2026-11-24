-- Base opérationnelle des comptes Dalla Pay.
-- Exécuté automatiquement au premier démarrage du conteneur postgres
-- (dossier /docker-entrypoint-initdb.d). Le CSV est monté dans /data.

CREATE TABLE comptes (
    compte_id          TEXT PRIMARY KEY,
    telephone          TEXT NOT NULL,
    pays               CHAR(2) NOT NULL,
    ville              TEXT NOT NULL,
    segment            TEXT NOT NULL CHECK (segment IN ('particulier', 'commercant', 'etudiant')),
    kyc_niveau         SMALLINT NOT NULL CHECK (kyc_niveau BETWEEN 1 AND 3),
    plafond_journalier BIGINT NOT NULL,
    date_ouverture     DATE NOT NULL,
    statut             TEXT NOT NULL DEFAULT 'ACTIF'
                       CHECK (statut IN ('ACTIF', 'SUSPENDU', 'BLOQUE', 'CLOTURE')),
    device_principal   TEXT NOT NULL,
    maj_le             TIMESTAMPTZ NOT NULL DEFAULT now()
);

\copy comptes (compte_id, telephone, pays, ville, segment, kyc_niveau, plafond_journalier, date_ouverture, statut, device_principal) FROM '/data/comptes.csv' WITH (FORMAT csv, HEADER true)

CREATE INDEX ON comptes (pays, ville);

-- Debezium lit le journal WAL : il faut une publication et l'image complète des lignes
-- pour recevoir l'ancienne valeur lors d'un UPDATE (utile pour voir l'ancien téléphone).
ALTER TABLE comptes REPLICA IDENTITY FULL;
CREATE PUBLICATION dbz_comptes FOR TABLE comptes;

-- Décisions prises par les analystes (alimentée par l'application Streamlit)
CREATE TABLE decisions (
    tx_id       TEXT PRIMARY KEY,
    compte_id   TEXT NOT NULL REFERENCES comptes,
    decision    TEXT NOT NULL CHECK (decision IN ('FRAUDE_CONFIRMEE', 'FAUX_POSITIF', 'A_REVOIR')),
    analyste    TEXT NOT NULL,
    commentaire TEXT,
    decide_le   TIMESTAMPTZ NOT NULL DEFAULT now()
);
