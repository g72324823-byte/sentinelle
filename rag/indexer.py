"""J3 — Indexation des procédures dans Qdrant (À COMPLÉTER).

Usage : python indexer.py --qdrant http://localhost:6333
"""
import argparse
from pathlib import Path


def lire_procedure(chemin: Path) -> dict:
    """Sépare l'en-tête YAML du corps Markdown."""
    texte = chemin.read_text(encoding="utf-8")
    _, entete, corps = texte.split("---", 2)
    meta = dict(l.split(": ", 1) for l in entete.strip().splitlines())
    return {"id": meta["id"], "titre": meta["titre"].strip('"'), "habilitation": meta["habilitation"],
            "texte": corps.strip()}


def decouper(doc: dict) -> list[dict]:
    # TODO : découper par section (## …) ou par fenêtre glissante ; justifier la taille choisie
    return [{"doc_id": doc["id"], "habilitation": doc["habilitation"], "texte": doc["texte"]}]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--qdrant", default="http://localhost:6333")
    a = p.parse_args()
    docs = [lire_procedure(f) for f in sorted((Path(__file__).parent / "procedures").glob("PROC-*.md"))]
    morceaux = [m for d in docs for m in decouper(d)]
    print(f"{len(docs)} procédures, {len(morceaux)} morceaux")
    # TODO 1 : embeddings denses (sentence-transformers, modèle multilingue) + vecteurs creux (BM25)
    # TODO 2 : collection Qdrant avec les deux types de vecteurs, payload = doc_id, habilitation
    # TODO 3 : fonction rechercher(question, habilitation, k=5) en hybride (prefetch + RRF)
    # TODO 4 : écrire resultats_rag.jsonl : {"id": "Q01", "resultats": ["PROC-01", ...]} pour
    #          les 20 questions de questions_reference.jsonl → évalué avec le rappel@5


if __name__ == "__main__":
    main()
