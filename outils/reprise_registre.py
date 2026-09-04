# -*- coding: utf-8 -*-
"""Reprendre dans la base vivante ce qui est resté sur l'ancienne.

CE QUI S'EST PASSÉ. Le 27 août 2026 à 9 h 07, une seconde base de registre a
été créée (`conseilprevia-registre-db`) et le service a basculé dessus : la
précédente (`conseilprev-registre-db`) a cessé d'être écrite six minutes plus
tôt. Depuis, le site tourne sur une base neuve — et la BASE DE CONNAISSANCE de
l'assistant, 49 documents et leurs fragments indexés, est restée sur l'autre.
L'assistant répond donc sans aucun ancrage documentaire.

CE QUE CET OUTIL FAIT, ET CE QU'IL NE FAIT PAS.
  · Il COPIE de l'ancienne vers la vivante ce qui manque à la vivante.
  · Il n'écrase JAMAIS une ligne existante : en cas de rencontre sur la clé
    d'identité, c'est la ligne VIVANTE qui gagne. Huit jours d'exploitation
    valent mieux qu'une reprise qui les efface.
  · Il ne supprime rien, nulle part.
  · Il est IDEMPOTENT : le relancer ne duplique pas ce qu'il a déjà repris.

POURQUOI IL S'EXÉCUTE DEPUIS RENDER ET PAS D'AILLEURS. Les deux bases
n'acceptent les connexions que depuis l'extérieur autorisé ; l'atelier de
développement n'a pas d'issue vers le port 5432. Le service, lui, joint les
deux. Cet outil est donc écrit pour tourner LÀ, avec deux adresses en
variables d'environnement.

    DATABASE_URL           la base VIVANTE — destination
    REGISTRE_ANCIEN_URL    la base de juin — source, lue seulement

    python3 outils/reprise_registre.py              # constate, n'écrit rien
    python3 outils/reprise_registre.py --reprendre  # exécute la reprise

SANS `--reprendre`, RIEN N'EST ÉCRIT. Le constat imprime, table par table, ce
qui serait copié. C'est le mode par défaut parce qu'une reprise se regarde
avant de se lancer.
"""
import os
import sys

# ══════════════════════════════════════════════════════════════════════════
# Le plan de reprise — une ligne par table
# ══════════════════════════════════════════════════════════════════════════
# `cle` : les colonnes qui font l'identité d'une ligne. Une ligne de la source
# dont la clé existe déjà dans la destination est IGNORÉE — jamais écrasée.
# `cle` vide signifie « pas d'identité naturelle » : la table est alors reprise
# seulement si la destination est VIDE, faute de quoi on dupliquerait.
#
# `ignorer` : les colonnes qui ne se recopient pas — les identifiants
# auto-incrémentés, que la destination réattribue, et les colonnes calculées.
PLAN = [
    # (table, clé d'identité, colonnes à ne pas recopier)
    ("clients",             ("email",),          ("id",)),
    ("rag_documents",       ("nom_fichier",),    ("id",)),
    # rag_chunks est traité à part : ses lignes pointent vers rag_documents et
    # doivent suivre la renumérotation des documents.
    ("email_log",           (),                  ("id",)),
    ("raas_contracts",      ("reference",),      ("id",)),
    ("raas_milestones",     (),                  ("id",)),
    ("client_notes",        (),                  ("id",)),
    ("consent_records",     (),                  ("id",)),
    ("stripe_events",       ("event_id",),       ()),
    ("systemes_ia",         ("nom",),            ("id",)),
    ("ia50_usages",         ("systeme", "role"), ("id",)),
    ("rgpd_registre_site",  ("nom",),            ("id",)),
    ("rgpd_retention",      ("cible",),          ("id",)),
    ("rgpd_traitements",    ("nom",),            ("id",)),
    ("form_sessions",       (),                  ("id",)),
    ("form_inscriptions",   (),                  ("id",)),
    ("empreinte_web",       ("jour",),           ()),
    ("empreinte_llm",       (),                  ("id",)),
]

# Les colonnes que Postgres calcule lui-même : les recopier échouerait.
CALCULEES = {"search_vector"}


def _connexions():
    import psycopg
    source = os.environ.get("REGISTRE_ANCIEN_URL", "").strip()
    dest = os.environ.get("DATABASE_URL", "").strip()
    if not source:
        sys.exit("REGISTRE_ANCIEN_URL n'est pas définie : l'adresse de "
                 "l'ancienne base (conseilprev-registre-db) est requise.")
    if not dest:
        sys.exit("DATABASE_URL n'est pas définie : la base vivante est requise.")
    if source == dest:
        sys.exit("Les deux adresses sont identiques : il n'y a rien à reprendre, "
                 "et une reprise sur elle-même dupliquerait tout.")
    for nom, url in (("source", source), ("destination", dest)):
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if nom == "source":
            source = url
        else:
            dest = url
    return psycopg.connect(source), psycopg.connect(dest)


def _colonnes(cur, table):
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position",
        (table,))
    return [r[0] for r in cur.fetchall()]


def _existe(cur, table):
    cur.execute("SELECT to_regclass(%s)", ("public." + table,))
    return cur.fetchone()[0] is not None


def _cles_presentes(cur, table, cle):
    """Les clés déjà présentes dans la destination."""
    if not cle:
        return set()
    cur.execute("SELECT %s FROM %s" % (", ".join(cle), table))
    return {tuple(r) for r in cur.fetchall()}


def _reprendre_table(src, dst, table, cle, ignorer, ecrire):
    """Rend (lues, reprises, ignorées) pour une table."""
    with src.cursor() as cs, dst.cursor() as cd:
        if not _existe(cs, table):
            return None, "absente de la source"
        if not _existe(cd, table):
            return None, "absente de la destination"

        communes = [c for c in _colonnes(cs, table)
                    if c in set(_colonnes(cd, table))
                    and c not in set(ignorer) and c not in CALCULEES]
        if not communes:
            return None, "aucune colonne commune"

        deja = _cles_presentes(cd, table, cle)
        if not cle:
            cd.execute("SELECT count(*) FROM %s" % table)
            if cd.fetchone()[0]:
                return (0, 0, 0), ("destination non vide et pas de clé "
                                   "d'identité — reprise refusée pour ne pas "
                                   "dupliquer")

        cs.execute("SELECT %s FROM %s" % (", ".join(communes), table))
        lignes = cs.fetchall()
        index_cle = [communes.index(c) for c in cle] if cle else []

        a_reprendre = []
        for ligne in lignes:
            if cle and tuple(ligne[i] for i in index_cle) in deja:
                continue
            a_reprendre.append(ligne)

        if ecrire and a_reprendre:
            gabarit = "INSERT INTO %s (%s) VALUES (%s)" % (
                table, ", ".join(communes), ", ".join(["%s"] * len(communes)))
            cd.executemany(gabarit, a_reprendre)
        return (len(lignes), len(a_reprendre), len(lignes) - len(a_reprendre)), None


def _reprendre_corpus(src, dst, ecrire):
    """rag_chunks — les fragments suivent la renumérotation des documents.

    Un fragment ne vaut rien sans son document : la copie se fait document par
    document, en relisant l'identifiant que la destination vient d'attribuer.
    """
    with src.cursor() as cs, dst.cursor() as cd:
        for table in ("rag_documents", "rag_chunks"):
            if not (_existe(cs, table) and _existe(cd, table)):
                return None, "%s absente d'un des deux côtés" % table

        cd.execute("SELECT nom_fichier, id FROM rag_documents")
        deja = dict(cd.fetchall())

        colonnes = [c for c in _colonnes(cs, "rag_chunks")
                    if c in set(_colonnes(cd, "rag_chunks"))
                    and c not in ("id", "document_id") and c not in CALCULEES]

        cs.execute("SELECT id, nom_fichier FROM rag_documents ORDER BY id")
        documents = cs.fetchall()

        fragments_repris = 0
        documents_vus = 0
        for ancien_id, nom in documents:
            cible = deja.get(nom)
            if cible is None:
                continue          # le document lui-même est repris par le PLAN
            cd.execute("SELECT count(*) FROM rag_chunks WHERE document_id=%s",
                       (cible,))
            if cd.fetchone()[0]:
                continue          # déjà pourvu : on ne double pas
            cs.execute("SELECT %s FROM rag_chunks WHERE document_id=%%s"
                       % ", ".join(colonnes), (ancien_id,))
            lignes = cs.fetchall()
            if not lignes:
                continue
            documents_vus += 1
            fragments_repris += len(lignes)
            if ecrire:
                gabarit = "INSERT INTO rag_chunks (document_id, %s) VALUES (%s)" % (
                    ", ".join(colonnes), ", ".join(["%s"] * (len(colonnes) + 1)))
                cd.executemany(gabarit, [(cible,) + tuple(l) for l in lignes])
        return (documents_vus, fragments_repris), None


def main():
    ecrire = "--reprendre" in sys.argv
    src, dst = _connexions()
    print("REPRISE DU REGISTRE — %s\n" %
          ("EXÉCUTION (les écritures sont réelles)" if ecrire
           else "CONSTAT (aucune écriture)"))
    print("%-22s %8s %8s %8s   %s" % ("table", "source", "à copier", "déjà là", ""))
    print("-" * 72)

    total = 0
    try:
        for table, cle, ignorer in PLAN:
            compte, souci = _reprendre_table(src, dst, table, cle, ignorer, ecrire)
            if compte is None:
                print("%-22s %8s %8s %8s   %s" % (table, "—", "—", "—", souci))
                continue
            lues, reprises, ignorees = compte
            total += reprises
            print("%-22s %8d %8d %8d   %s" % (table, lues, reprises, ignorees,
                                              souci or ""))

        corpus, souci = _reprendre_corpus(src, dst, ecrire)
        if corpus is None:
            print("%-22s %8s %8s %8s   %s" % ("rag_chunks", "—", "—", "—", souci))
        else:
            docs, frags = corpus
            total += frags
            print("%-22s %8s %8d %8s   %d document(s) pourvu(s)"
                  % ("rag_chunks", "—", frags, "—", docs))

        if ecrire:
            dst.commit()
            print("\n%d ligne(s) reprise(s), transaction validée." % total)
        else:
            dst.rollback()
            print("\n%d ligne(s) SERAIENT reprises. Relancer avec --reprendre "
                  "pour exécuter." % total)
    except Exception:
        dst.rollback()
        print("\nÉCHEC — rien n'a été écrit (transaction annulée).")
        raise
    finally:
        src.close()
        dst.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
