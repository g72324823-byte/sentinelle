// J2 — Graphe des virements (À COMPLÉTER)
// Exporter d'abord les TRANSFERT de la couche argent en CSV dans ./data/virements.csv
// (colonnes : tx_id, ts, compte_id, compte_dest, montant), puis :

CREATE CONSTRAINT compte_id IF NOT EXISTS FOR (c:Compte) REQUIRE c.id IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///virements.csv' AS l
CALL (l) {
  MERGE (a:Compte {id: l.compte_id})
  MERGE (b:Compte {id: l.compte_dest})
  CREATE (a)-[:VIREMENT {tx_id: l.tx_id, ts: datetime(l.ts), montant: toFloat(l.montant)}]->(b)
} IN TRANSACTIONS OF 10000 ROWS;

// TODO : requête de détection des anneaux (cycles de 3 à 5 comptes en moins de 7 jours,
//        montants qui décroissent de 1 à 5 % à chaque saut). Voir la séance 3 :
//        motifs quantifiés  -[:VIREMENT]->{3,5}
