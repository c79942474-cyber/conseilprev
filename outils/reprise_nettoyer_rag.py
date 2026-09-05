# -*- coding: utf-8 -*-
"""Vider la partie RAG de la base VIVANTE, pour repartir d'une reprise propre.

POURQUOI CE SCRIPT EXISTE. La reprise du 5 septembre 2026 a tourné avec une
version buggée de `reprise_registre.py` (déployée sur `main`, avant la
correction). Elle a copié le corpus de l'assistant SANS son index plein texte
— 1 268 fragments, aucun `search_vector`, zéro résultat à la recherche — et
avec des documents en double. Or l'outil de reprise n'écrase JAMAIS une ligne
existante : relancer la version corrigée par-dessus ne réparerait pas ces
fragments-là. Il faut donc vider la partie RAG, puis relancer la reprise.

CE QUE CE SCRIPT TOUCHE, ET RIEN D'AUTRE. Uniquement `rag_documents` et
`rag_chunks` — le corpus. Aucune autre table. Sur la base vivante, ces deux
tables étaient VIDES avant la reprise (0 document, 0 fragment le 27 août) :
tout ce qu'elles contiennent aujourd'hui vient de la copie ratée. Les vider ne
perd donc aucune donnée écrite par le site.

TROIS GARDES, PARCE QU'UN TRUNCATE NE SE REJOUE PAS.
  1. À SEC PAR DÉFAUT. Sans `--vider`, il compte et n'écrit rien.
  2. IL REFUSE DE VIDER LA SOURCE. Si la base pointée porte le nom de
     l'ancienne base (`conseilprev_registre_db`), il s'arrête : on ne vide pas
     le corpus qu'on s'apprête à recopier.
  3. IL DIT À QUOI IL EST CONNECTÉ. Le nom de la base est imprimé avant tout,
     pour qu'une erreur d'adresse se voie plutôt que se subisse.

    DATABASE_URL   la base VIVANTE (destination de la reprise)

    python3 outils/reprise_nettoyer_rag.py            # compte, n'écrit rien
    python3 outils/reprise_nettoyer_rag.py --vider    # vide rag_documents + rag_chunks
"""
import os
import sys

# La base à NE JAMAIS vider : la source de la reprise. La vider effacerait le
# corpus qu'on veut justement recopier.
SOURCE_INTERDITE = "conseilprev_registre_db"

# Les seules tables que ce script touche.
TABLES_RAG = ("rag_chunks", "rag_documents")


def _connexion():
    import psycopg
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        sys.exit("DATABASE_URL n'est pas définie : la base vivante est requise.")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg.connect(url)


def _compter(cur):
    n = {}
    for t in TABLES_RAG:
        cur.execute("SELECT to_regclass(%s)", ("public." + t,))
        if cur.fetchone()[0] is None:
            n[t] = None
            continue
        cur.execute("SELECT count(*) FROM %s" % t)
        n[t] = cur.fetchone()[0]
    return n


def main():
    vider = "--vider" in sys.argv
    conn = _connexion()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database()")
            base = cur.fetchone()[0]
            print("Base connectée : %s\n" % base)

            # GARDE 2 : ne jamais vider la source.
            if base == SOURCE_INTERDITE:
                sys.exit("REFUS : cette base est la SOURCE de la reprise (%s). "
                         "On ne vide pas le corpus qu'on va recopier." % base)

            avant = _compter(cur)
            for t in TABLES_RAG:
                v = avant[t]
                print("  %-16s %s" % (t, "absente" if v is None else "%d lignes" % v))

            total = sum(v for v in avant.values() if v)
            if not total:
                print("\nRien à vider — la partie RAG est déjà vide.")
                return 0

            if not vider:
                print("\n%d ligne(s) SERAIENT supprimées (rag_documents + rag_chunks). "
                      "Relancer avec --vider pour exécuter." % total)
                return 0

            # rag_chunks référence rag_documents (ON DELETE CASCADE) : vider les
            # documents suffit, mais on nomme les deux pour que l'intention soit
            # lisible et l'ordre sans ambiguïté.
            cur.execute("TRUNCATE rag_chunks, rag_documents RESTART IDENTITY")
            conn.commit()
            apres = _compter(cur)
            print("\nVidé. État après :")
            for t in TABLES_RAG:
                print("  %-16s %d lignes" % (t, apres[t] or 0))
            print("\nLa partie RAG est vide. Relancez maintenant :")
            print("  python3 outils/reprise_registre.py            # constat")
            print("  python3 outils/reprise_registre.py --reprendre # exécution")
            return 0
    except Exception:
        conn.rollback()
        print("\nÉCHEC — rien n'a été supprimé (transaction annulée).")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
