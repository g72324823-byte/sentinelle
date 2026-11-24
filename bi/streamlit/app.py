"""J6 — Console des analystes de la fraude (À COMPLÉTER).

Écrans attendus : file des alertes en direct, fiche d'un compte (historique, graphe des
virements), bouton de décision qui écrit dans la table PostgreSQL `decisions`,
assistant RAG (question → réponse avec les procédures citées).
"""
import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sentinelle — analystes", layout="wide")
st.title("Sentinelle · console des analystes")

onglet_alertes, onglet_compte, onglet_assistant = st.tabs(["Alertes", "Compte", "Assistant procédures"])

with onglet_alertes:
    st.caption("Alertes reçues du topic Kafka `alertes`")
    # TODO : consommer le topic (confluent_kafka) dans un fragment rafraîchi toutes les 2 s
    st.dataframe(pd.DataFrame(columns=["ts", "tx_id", "compte_id", "regle", "score", "decision"]))

with onglet_compte:
    compte = st.text_input("Identifiant du compte", placeholder="CM012345")
    if compte:
        # TODO : historique depuis la couche argent, statut depuis PostgreSQL
        st.info(f"Fiche du compte {compte} à construire")
        decision = st.radio("Décision", ["FRAUDE_CONFIRMEE", "FAUX_POSITIF", "A_REVOIR"], horizontal=True)
        if st.button("Enregistrer la décision"):
            # TODO : INSERT INTO decisions (...) avec os.environ["PG_DSN"]
            st.success("Décision enregistrée (à implémenter)")

with onglet_assistant:
    q = st.text_input("Question sur une procédure", placeholder="Que faire après un échange de carte SIM ?")
    if q:
        # TODO : recherche hybride dans Qdrant + génération avec citations [PROC-xx]
        st.write("Réponse à construire. Chaque réponse doit citer ses sources.")
