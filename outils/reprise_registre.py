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
avant de se lancer — et il PRÉDIT l'exécution, ce qui n'allait pas de soi.

CE QUE LA PREMIÈRE VERSION PERDAIT, MESURÉ SUR DEUX BASES RÉELLES.
Éprouvée le 5 septembre 2026 contre une réplique fidèle des deux bases
(1 696 lignes d'un côté, 21 de l'autre), elle a annoncé « 1 573 lignes
reprises, transaction validée » et rendu 0. La mesure disait autre chose :

  · 112 LIGNES RESTÉES AU SOL, sans que rien ne le signale — six tables que
    la destination n'a pas (le registre RGPD, le registre IA Act art. 50, les
    événements Stripe, les sessions et l'inscription de formation), deux
    autres refusées faute de clé d'identité, et soixante fragments orphelins.
  · LE CONSTAT ANNONÇAIT 0 FRAGMENT et l'exécution en a copié 1 410 : un
    essai à blanc qui ne prédit pas l'exécution est pire qu'aucun essai.
  · LES 1 410 FRAGMENTS REPRIS N'AVAIENT AUCUN `search_vector`. La recherche
    plein texte y trouvait ZÉRO résultat. L'outil rendait à l'assistant un
    corpus invisible, et se déclarait satisfait.

Les trois défauts partagent une racine : l'outil DÉCRIVAIT son travail au
lieu de le MESURER. Il compte désormais ce qui reste au sol, et il refuse de
rendre 0 tant que quelque chose y reste.
"""
import os
import sys

# ══════════════════════════════════════════════════════════════════════════
# Le plan de reprise — une ligne par table
# ══════════════════════════════════════════════════════════════════════════
# `cle` : les EXPRESSIONS SQL qui font l'identité d'une ligne — un nom de
# colonne le plus souvent, mais pas toujours : l'identité d'un fichier est son
# contenu, pas son nom. Une ligne de la source dont la clé existe déjà dans la
# destination est IGNORÉE — jamais écrasée.
#
# AUCUNE TABLE N'A DE CLÉ VIDE. La première version en avait sept, et la règle
# « reprise seulement si la destination est vide » a fait rester au sol les
# huit preuves de consentement et sept lignes d'empreinte, sans autre signal
# qu'une remarque en fin de ligne. Une table sans identité naturelle en reçoit
# une composite : l'horodatage plus ce qui distingue deux lignes du même
# instant.
#
# `ignorer` : les colonnes qui ne se recopient pas — les identifiants
# auto-incrémentés, que la destination réattribue.
PLAN = [
    # (table, clé d'identité, colonnes à ne pas recopier)
    ("clients",             ("email",),                     ("id",)),
    # L'IDENTITÉ D'UN DOCUMENT EST SON CONTENU. Sur `nom_fichier`, trois
    # dépôts successifs du même PDF sous le même nom entraient trois fois, et
    # deux d'entre eux repartaient sans un seul fragment.
    ("rag_documents",       ("md5(contenu_fichier)",),      ("id",)),
    # rag_chunks est traité à part : ses lignes pointent vers rag_documents et
    # doivent suivre la renumérotation des documents.
    ("email_log",           ("date_envoi", "destinataire", "sujet"), ("id",)),
    ("raas_contracts",      ("reference",),                 ("id",)),
    # La contrainte UNIQUE que porte la destination, et non une absence de clé.
    ("raas_milestones",     ("client_id", "milestone_id"),  ("id",)),
    ("client_notes",        ("created_at", "client_id"),    ("id",)),
    ("consent_records",     ("horodatage", "ip_hash"),      ("id",)),
    ("stripe_events",       ("event_id",),                  ()),
    ("systemes_ia",         ("nom",),                       ("id",)),
    ("ia50_usages",         ("systeme", "role"),            ("id",)),
    ("rgpd_registre_site",  ("nom",),                       ("id",)),
    ("rgpd_retention",      ("cible",),                     ("id",)),
    ("rgpd_traitements",    ("nom",),                       ("id",)),
    ("form_sessions",       ("formation_id", "date_session"), ("id",)),
    ("form_inscriptions",   ("created_at", "email"),        ("id",)),
    ("empreinte_web",       ("jour",),                      ()),
    ("empreinte_llm",       ("horodatage", "module", "modele"), ("id",)),
]

# `search_vector` N'EST PAS CALCULÉE. Elle en avait l'air — le nom, le type
# tsvector — et la première version l'écartait comme telle. Vérification faite
# sur la base vivante : aucune colonne générée, aucun déclencheur. Rien ne la
# remplit. Les 1 410 fragments repris sans elle rendaient ZÉRO résultat à la
# recherche plein texte. Elle se recopie donc comme les autres.
CALCULEES = set()


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


def _ddl_source(cs, table):
    """Le CREATE TABLE de la source, reconstruit depuis son catalogue.

    POURQUOI L'OUTIL CRÉE DES TABLES. Six tables du registre — dont celui du
    RGPD et celui de l'article 50 — ne sont créées par l'application qu'au
    premier usage de leur propre fonctionnalité, jamais au démarrage. La base
    vivante, née le 27 août, ne les avait donc jamais vues, et la reprise
    passait devant en imprimant « absente de la destination ».

    La forme est celle de la SOURCE, qui a été créée par cette même
    application : c'est la plus proche de ce que l'application attend.
    """
    cs.execute("""
        SELECT string_agg(format('%%I %%s%%s%%s', a.attname,
                 format_type(a.atttypid, a.atttypmod),
                 CASE WHEN a.attnotnull THEN ' NOT NULL' ELSE '' END,
                 CASE WHEN d.adbin IS NOT NULL AND pg_get_expr(d.adbin,d.adrelid)
                           NOT LIKE 'nextval(%%'
                      THEN ' DEFAULT ' || pg_get_expr(d.adbin, d.adrelid)
                      ELSE '' END),
               ', ' ORDER BY a.attnum)
        FROM pg_attribute a
        LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
        WHERE a.attrelid = %s::regclass AND a.attnum > 0 AND NOT a.attisdropped
    """, ("public." + table,))
    colonnes = cs.fetchone()[0]
    cs.execute("SELECT a.attname FROM pg_index i JOIN pg_attribute a "
               "ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) "
               "WHERE i.indrelid = %s::regclass AND i.indisprimary",
               ("public." + table,))
    pk = [r[0] for r in cs.fetchall()]
    ddl = "CREATE TABLE IF NOT EXISTS public.%s (%s%s)" % (
        table, colonnes,
        (", PRIMARY KEY (%s)" % ", ".join(pk)) if pk else "")
    # Les identifiants auto-incrémentés : une identité, plutôt qu'une séquence
    # que la destination ne connaît pas.
    return ddl.replace("id integer NOT NULL,",
                       "id integer GENERATED BY DEFAULT AS IDENTITY,", 1)


def _creer_manquantes(src, dst):
    """Crée dans la destination les tables du PLAN qu'elle n'a pas.

    ELLES SONT CRÉÉES DANS LES DEUX MODES, y compris à blanc — le DDL est
    transactionnel sous PostgreSQL, et le constat annule sa transaction. Sans
    cela, le constat ne pouvait pas compter les lignes des tables qu'il
    n'avait pas créées, et sous-estimait la reprise de quarante-deux lignes :
    un essai à blanc qui n'annonce pas le même total que l'exécution ne sert
    à rien.
    """
    creees = []
    with src.cursor() as cs, dst.cursor() as cd:
        for table, _, _ in PLAN:
            if not _existe(cs, table) or _existe(cd, table):
                continue
            creees.append(table)
            cd.execute(_ddl_source(cs, table))
    return creees


def _cles_presentes(cur, table, cle):
    cur.execute("SELECT %s FROM %s" % (", ".join(cle), table))
    return {tuple(r) for r in cur.fetchall()}


def _reprendre_table(src, dst, table, cle, ignorer, ecrire):
    """Rend ((lues, reprises, deja, doublons), souci) pour une table."""
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

        # La clé est demandée EN PLUS des colonnes : elle peut être une
        # expression (`md5(contenu_fichier)`) et non un simple nom.
        cs.execute("SELECT %s, %s FROM %s"
                   % (", ".join(communes), ", ".join(cle), table))
        lignes = cs.fetchall()
        n = len(communes)

        a_reprendre, vues, doublons = [], set(), 0
        for ligne in lignes:
            k = tuple(ligne[n:])
            if k in deja:
                continue
            # LE LOT SE DÉDOUBLONNE LUI AUSSI. Ne comparer qu'à la destination
            # laissait entrer trois fois le même document : la garde ne
            # protégeait que de l'existant, pas du lot en cours.
            if k in vues:
                doublons += 1
                continue
            vues.add(k)
            a_reprendre.append(ligne[:n])

        if ecrire and a_reprendre:
            gabarit = "INSERT INTO %s (%s) VALUES (%s)" % (
                table, ", ".join(communes), ", ".join(["%s"] * n))
            cd.executemany(gabarit, a_reprendre)
        return (len(lignes), len(a_reprendre),
                len(lignes) - len(a_reprendre) - doublons, doublons), None


def _reprendre_corpus(src, dst, ecrire):
    """rag_chunks — les fragments suivent la renumérotation des documents.

    LE CONSTAT PRÉDIT L'EXÉCUTION, ce qui n'était pas le cas. La première
    version lisait les documents DÉJÀ présents en destination pour savoir où
    rattacher les fragments ; à blanc, rien n'ayant été écrit, elle n'en
    trouvait aucun et annonçait « 0 fragment ». L'exécution en copiait 1 410.
    Ici, les documents que la reprise VA créer sont comptés comme tels.
    """
    with src.cursor() as cs, dst.cursor() as cd:
        for table in ("rag_documents", "rag_chunks"):
            if not (_existe(cs, table) and _existe(cd, table)):
                return None, "%s absente d'un des deux côtés" % table

        cd.execute("SELECT md5(contenu_fichier), id FROM rag_documents")
        deja = dict(cd.fetchall())

        colonnes = [c for c in _colonnes(cs, "rag_chunks")
                    if c in set(_colonnes(cd, "rag_chunks"))
                    and c not in ("id", "document_id") and c not in CALCULEES]

        cs.execute("SELECT id, md5(contenu_fichier) FROM rag_documents ORDER BY id")
        documents = cs.fetchall()

        fragments, documents_vus, vus = 0, 0, set()
        for ancien_id, empreinte in documents:
            if empreinte in vus:
                continue          # même contenu : ses fragments sont déjà comptés
            vus.add(empreinte)
            cible = deja.get(empreinte)
            if cible is not None:
                cd.execute("SELECT count(*) FROM rag_chunks WHERE document_id=%s",
                           (cible,))
                if cd.fetchone()[0]:
                    continue      # déjà pourvu : on ne double pas
            cs.execute("SELECT count(*) FROM rag_chunks WHERE document_id=%s",
                       (ancien_id,))
            combien = cs.fetchone()[0]
            if not combien:
                continue
            documents_vus += 1
            fragments += combien
            if not ecrire:
                continue          # à blanc : compté, pas copié
            if cible is None:
                # Le document vient d'être repris par le PLAN, dans cette même
                # transaction : on relit l'identifiant qu'il y a reçu.
                cd.execute("SELECT id FROM rag_documents WHERE md5(contenu_fichier)"
                           " = %s ORDER BY id LIMIT 1", (empreinte,))
                trouve = cd.fetchone()
                if not trouve:
                    continue
                cible = trouve[0]
            cs.execute("SELECT %s FROM rag_chunks WHERE document_id=%%s"
                       % ", ".join(colonnes), (ancien_id,))
            cd.executemany(
                "INSERT INTO rag_chunks (document_id, %s) VALUES (%s)"
                % (", ".join(colonnes), ", ".join(["%s"] * (len(colonnes) + 1))),
                [(cible,) + tuple(l) for l in cs.fetchall()])
        return (documents_vus, fragments), None


def main():
    ecrire = "--reprendre" in sys.argv
    src, dst = _connexions()
    print("REPRISE DU REGISTRE — %s\n" %
          ("EXÉCUTION (les écritures sont réelles)" if ecrire
           else "CONSTAT (aucune écriture)"))

    au_sol = []          # ce qui NE SERA PAS repris, et pourquoi
    total = 0
    try:
        creees = _creer_manquantes(src, dst)
        if creees:
            print("Tables absentes de la destination, %s : %s\n"
                  % ("créées" if ecrire else "créées puis annulées (constat)",
                     ", ".join(creees)))

        print("%-22s %8s %8s %8s %9s" %
              ("table", "source", "reprises", "déjà là", "doublons"))
        print("-" * 62)
        for table, cle, ignorer in PLAN:
            compte, souci = _reprendre_table(src, dst, table, cle, ignorer, ecrire)
            if compte is None:
                au_sol.append((table, souci))
                print("%-22s %8s %8s %8s %9s   %s"
                      % (table, "—", "—", "—", "—", souci))
                continue
            lues, reprises, deja, doublons = compte
            total += reprises
            print("%-22s %8d %8d %8d %9d" % (table, lues, reprises, deja, doublons))

        corpus, souci = _reprendre_corpus(src, dst, ecrire)
        if corpus is None:
            au_sol.append(("rag_chunks", souci))
            print("%-22s %8s %8s %8s %9s   %s"
                  % ("rag_chunks", "—", "—", "—", "—", souci))
        else:
            docs, frags = corpus
            total += frags
            print("%-22s %8s %8d %8s %9s   %d document(s) pourvu(s)"
                  % ("rag_chunks", "—", frags, "—", "—", docs))

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

    # ── LE VERDICT REFUSE DE RENDRE 0 SI QUELQUE CHOSE RESTE AU SOL ────────
    # La première version imprimait « absente de la destination » dans une
    # colonne de remarques, poursuivait, et rendait 0 en annonçant une
    # transaction validée. 112 lignes étaient restées derrière.
    if au_sol:
        print("\nRESTÉ AU SOL — %d table(s) non reprises :" % len(au_sol))
        for table, souci in au_sol:
            print("  · %-22s %s" % (table, souci))
        print("\nLA REPRISE EST INCOMPLÈTE. Ne supprimez pas la source.")
        return 1
    print("\nRien n'est resté au sol.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
