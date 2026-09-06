# -*- coding: utf-8 -*-
"""Terminer l'indexation du corpus : re-découper ce qui n'a aucun fragment,
vectoriser ce qui n'a aucun vecteur.

POURQUOI CET OUTIL EXISTE. L'indexation de Sentinel se fait en deux temps : le
découpage au dépôt, puis la vectorisation par lots de dix — et cette seconde
boucle est PILOTÉE PAR LE NAVIGATEUR. `rag_index_next_batch` le dit :
« Le client (frontend) rappelle cet endpoint en boucle jusqu'à indexation
complète. » Ferme l'onglet, et le corpus s'arrête là où il en était. Aucune
route ne permet de le reprendre : `reindex`, `reprocess`, `retraiter` —
aucune n'existe.

CE QUE LA MESURE A TROUVÉ sur la base vivante, le 5 septembre 2026 :

  · ONZE DOCUMENTS N'AVAIENT AUCUN FRAGMENT — et ce sont les onze plus gros :
    EU_IA_ACT, Reglement_RGPD, NIST.SP.800-82r2, ISO_IEC_42001, CYBER_ACT,
    Code_of_Practice… toute la colonne vertébrale réglementaire du corpus. Le
    découpage n'avait jamais abouti au dépôt. Leurs 20,8 Mo d'origine sont
    intacts en base : tout est réparable sans redéposer un seul fichier.
  · 763 FRAGMENTS N'AVAIENT AUCUN VECTEUR, sur 21 documents dont la boucle de
    vectorisation n'a simplement jamais tourné.

POURQUOI IL TOURNE DANS LE SHELL ET NON DERRIÈRE UNE ROUTE. C'est le délai
HTTP qui a tué le découpage des gros fichiers. Ici, aucun délai ne borne le
travail — et le découpage réutilise `rag_moteur.fragments_de_fichier`, le
générateur en flux du dépôt, qui ne tient jamais le document entier en
mémoire. Les fragments produits sont donc IDENTIQUES à ceux d'un dépôt normal.

LE STATUT EST MESURÉ, PAS AFFIRMÉ. `rag_index_next_batch` avance son compteur
même quand l'appel d'embeddings ÉCHOUE, et peut donc marquer « termine » un
document dont aucun fragment n'a de vecteur — une indexation ratée qui se
déclare finie. Ici, `statut_indexation` est recalculé depuis les données :
« termine » seulement s'il ne reste aucun fragment sans vecteur. Et un échec
d'embeddings ARRÊTE le travail avec un rapport, au lieu de le maquiller.

    DATABASE_URL      la base à réparer
    MISTRAL_API_KEY   requis pour la phase 2 (vectorisation)

    python3 outils/rag_reindexer.py                  # constat, AUCUN appel d'API
    python3 outils/rag_reindexer.py --executer       # répare
    python3 outils/rag_reindexer.py --executer --limite 500   # borne la phase 2

SANS `--executer`, RIEN N'EST ÉCRIT ET AUCUN EMBEDDING N'EST DEMANDÉ : le
constat ne coûte rien. L'outil est relançable — il reprend ce qui manque.
"""
import io
import os
import sys
import time

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOT = 10                 # même taille de lot que la route de l'application
TENTATIVES = 3           # avant d'abandonner un lot d'embeddings
ATTENTE = 5              # secondes, doublées à chaque nouvelle tentative


def _app():
    """L'application elle-même : on lui emprunte SES fonctions de découpage et
    de vectorisation. Réécrire un découpage « équivalent » produirait des
    fragments légèrement différents de ceux du dépôt — et un corpus dont une
    moitié serait coupée autrement que l'autre."""
    if RACINE not in sys.path:
        sys.path.insert(0, RACINE)
    import app
    return app


# ══════════════════════════════════════════════════════════════════════════
# Ce que la base dit d'elle-même
# ══════════════════════════════════════════════════════════════════════════

def _sans_fragment(a, cur):
    cur.execute("""SELECT id, nom_fichier, nb_chunks FROM rag_documents r
                   WHERE NOT EXISTS (SELECT 1 FROM rag_chunks c
                                     WHERE c.document_id = r.id)
                   ORDER BY id""")
    return [dict(r) if not isinstance(r, dict) else r for r in cur.fetchall()]


def _sans_vecteur(a, cur):
    cur.execute("""SELECT r.id, r.nom_fichier,
                          count(*) FILTER (WHERE c.embedding IS NULL) AS manquants,
                          count(*) AS total
                   FROM rag_documents r JOIN rag_chunks c ON c.document_id = r.id
                   GROUP BY r.id, r.nom_fichier
                   HAVING count(*) FILTER (WHERE c.embedding IS NULL) > 0
                   ORDER BY r.id""")
    return [dict(r) if not isinstance(r, dict) else r for r in cur.fetchall()]


# ══════════════════════════════════════════════════════════════════════════
# Phase 1 — re-découper ce qui n'a aucun fragment
# ══════════════════════════════════════════════════════════════════════════

def redecouper(a, executer):
    conn = a.registre_get_db()
    cur = conn.cursor()
    docs = _sans_fragment(a, cur)
    if not docs:
        print("  aucun document sans fragment.")
        conn.close()
        return 0, []

    total, soucis = 0, []
    for d in docs:
        cur.execute(a.registre_sql(
            'SELECT contenu_fichier FROM rag_documents WHERE id=%s',
            'SELECT contenu_fichier FROM rag_documents WHERE id=?'), (d['id'],))
        row = cur.fetchone()
        octets = bytes((dict(row) if not isinstance(row, dict) else row)['contenu_fichier'] or b'')
        if len(octets) < 1000:
            soucis.append((d['nom_fichier'], "fichier d'origine absent ou tronqué"))
            print("  %-44s ÉCARTÉ — original absent" % d['nom_fichier'][:44])
            continue

        if not executer:
            print("  %-44s %6d fragments annoncés, %d Ko à redécouper"
                  % (d['nom_fichier'][:44], d['nb_chunks'] or 0, len(octets) // 1024))
            total += d['nb_chunks'] or 0
            continue

        n = 0
        try:
            for frag in a.rag_moteur.fragments_de_fichier(
                    d['nom_fichier'], io.BytesIO(octets),
                    a.RAG_CHUNK_SIZE, a.RAG_CHUNK_OVERLAP):
                cur.execute("""INSERT INTO rag_chunks
                               (document_id, chunk_text, chunk_index, search_vector)
                               VALUES (%s,%s,%s, to_tsvector('french', %s))""",
                            (d['id'], frag, n, frag))
                n += 1
        except Exception as e:                                    # noqa: BLE001
            conn.rollback()
            soucis.append((d['nom_fichier'], str(e)[:120]))
            print("  %-44s ÉCHEC — %s" % (d['nom_fichier'][:44], str(e)[:60]))
            continue

        # `nb_chunks` est recalé sur le compte RÉEL. La valeur annoncée au
        # dépôt décrivait un découpage qui n'a jamais abouti ; la garder
        # ferait croire à des fragments qui n'existent pas.
        cur.execute(a.registre_sql(
            "UPDATE rag_documents SET nb_chunks=%s, chunks_indexes=0,"
            " statut_indexation='en_cours' WHERE id=%s",
            "UPDATE rag_documents SET nb_chunks=?, chunks_indexes=0,"
            " statut_indexation='en_cours' WHERE id=?"), (n, d['id']))
        conn.commit()
        total += n
        print("  %-44s %6d fragments recréés" % (d['nom_fichier'][:44], n))

    conn.close()
    return total, soucis


# ══════════════════════════════════════════════════════════════════════════
# Phase 2 — vectoriser ce qui n'a aucun vecteur
# ══════════════════════════════════════════════════════════════════════════

def vectoriser(a, executer, limite):
    conn = a.registre_get_db()
    cur = conn.cursor()
    docs = _sans_vecteur(a, cur)
    if not docs:
        print("  aucun fragment sans vecteur.")
        conn.close()
        return 0, []

    attendus = sum(d['manquants'] for d in docs)
    if not executer:
        for d in docs:
            print("  %-44s %5d fragment(s) à vectoriser sur %d"
                  % (d['nom_fichier'][:44], d['manquants'], d['total']))
        print("\n  %d fragment(s) SERAIENT vectorisés — AUCUN appel d'API n'a été fait."
              % attendus)
        conn.close()
        return attendus, []

    if not a.MISTRAL_API_KEY:
        conn.close()
        return 0, [("(global)", "MISTRAL_API_KEY absente : la vectorisation est "
                                "impossible. Rien n'a été tenté.")]

    faits, soucis = 0, []
    for d in docs:
        if limite and faits >= limite:
            break
        while True:
            if limite and faits >= limite:
                break
            cur.execute(a.registre_sql(
                'SELECT chunk_index, chunk_text FROM rag_chunks WHERE document_id=%s'
                ' AND embedding IS NULL ORDER BY chunk_index LIMIT %s',
                'SELECT chunk_index, chunk_text FROM rag_chunks WHERE document_id=?'
                ' AND embedding IS NULL ORDER BY chunk_index LIMIT ?'), (d['id'], LOT))
            rows = [dict(r) if not isinstance(r, dict) else r for r in cur.fetchall()]
            if not rows:
                break

            ok, res = False, None
            for essai in range(TENTATIVES):
                ok, res = a.rag_get_embeddings([r['chunk_text'] for r in rows])
                if ok:
                    break
                if essai < TENTATIVES - 1:
                    time.sleep(ATTENTE * (2 ** essai))

            # UN ÉCHEC ARRÊTE LE TRAVAIL. La route de l'application, elle,
            # avance son compteur et peut marquer « termine » : c'est ainsi
            # qu'une indexation ratée se déclare finie. Ici, on s'arrête et on
            # le dit — l'outil est relançable, rien n'est perdu.
            if not ok:
                soucis.append((d['nom_fichier'], "embeddings refusés : %s" % res))
                _statuer(a, cur, d['id'])
                conn.commit()
                conn.close()
                print("  %-44s ARRÊT — %s" % (d['nom_fichier'][:44], res))
                return faits, soucis

            for r, vecteur in zip(rows, res):
                cur.execute(a.registre_sql(
                    'UPDATE rag_chunks SET embedding=%s WHERE document_id=%s'
                    ' AND chunk_index=%s',
                    'UPDATE rag_chunks SET embedding=? WHERE document_id=?'
                    ' AND chunk_index=?'), (vecteur, d['id'], r['chunk_index']))
            faits += len(rows)
            conn.commit()

        _statuer(a, cur, d['id'])
        conn.commit()
        print("  %-44s vectorisé (%d au total ce passage)"
              % (d['nom_fichier'][:44], faits))

    conn.close()
    return faits, soucis


def _statuer(a, cur, doc_id):
    """LE STATUT EST RECALCULÉ DEPUIS LES DONNÉES, jamais depuis un compteur —
    et par LA MÊME fonction que la route de dépôt, jamais par une copie.

    Cet outil portait sa propre définition de « termine » : un document sans
    fragment sans vecteur. La route en portait une autre : une boucle arrivée
    au bout. Deux définitions, donc deux vérités — et la seule façon d'en
    sortir n'est pas de les accorder aujourd'hui, c'est qu'il n'y en ait plus
    qu'une. `app.rag_ecrire_statut` est cette définition ; on l'emprunte.

    Ce qu'elle dit depuis le 6 septembre 2026 : un document est indexé quand il
    a des fragments portant chacun leur index plein texte. Le vecteur est un
    enrichissement — la moitié sémantique est éteinte, et l'exiger laisserait
    71 % du corpus en « en_cours » à jamais.
    """
    a.rag_ecrire_statut(cur, doc_id)

# ══════════════════════════════════════════════════════════════════════════
# PHASE 3 — LES STATUTS SE RECALENT SUR LA DÉFINITION EN VIGUEUR
# ══════════════════════════════════════════════════════════════════════════

def recaler_statuts(a, executer):
    """Réapplique à TOUT le corpus la définition de `rag_statut_document`.

    POURQUOI CETTE PHASE EXISTE. La définition de « termine » a changé le
    6 septembre 2026 : elle exigeait un vecteur par fragment, elle exige
    désormais un index plein texte. Changer la règle sans repasser sur les
    données laisserait 32 documents affichés « en_cours » pour une raison qui
    n'a plus cours — un écart entre ce que le code dit et ce que la base
    montre, c'est-à-dire précisément ce qu'on corrige partout ailleurs.

    Elle est aussi RELANÇABLE SANS DOMMAGE : appliquer une définition à des
    données qui la respectent déjà ne change rien. C'est ce qui la rend sûre à
    laisser dans le passage normal de l'outil.

    Rend (nombre de statuts changés, soucis).
    """
    conn = a.registre_get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, nom_fichier, statut_indexation, chunks_indexes'
                ' FROM rag_documents ORDER BY nom_fichier')
    docs = [dict(d) if not isinstance(d, dict) else d for d in cur.fetchall()]

    changes = 0
    for d in docs:
        statut, indexes, total = a.rag_statut_document(cur, d['id'])
        if statut == d['statut_indexation'] and indexes == (d['chunks_indexes'] or 0):
            continue
        changes += 1
        print("  %-44s %-9s → %-9s  %d/%d fragment(s) indexé(s)"
              % (d['nom_fichier'][:44], d['statut_indexation'], statut, indexes, total))
        if executer:
            a.rag_ecrire_statut(cur, d['id'])

    if not changes:
        print("  aucun statut à recaler.")
    elif executer:
        conn.commit()
        print("\n  %d statut(s) recalé(s)." % changes)
    else:
        print("\n  %d statut(s) SERAIENT recalés — aucune écriture n'a été faite."
              % changes)
    conn.close()
    return changes, []


# ══════════════════════════════════════════════════════════════════════════

def _etat(a):
    conn = a.registre_get_db()
    cur = conn.cursor()
    cur.execute("""SELECT (SELECT count(*) FROM rag_documents) AS documents,
                          (SELECT count(*) FROM rag_chunks) AS fragments,
                          (SELECT count(*) FROM rag_chunks WHERE embedding IS NULL) AS sans_vecteur,
                          (SELECT count(*) FROM rag_documents r WHERE NOT EXISTS
                             (SELECT 1 FROM rag_chunks c WHERE c.document_id=r.id)) AS sans_fragment""")
    r = cur.fetchone()
    conn.close()
    return dict(r) if not isinstance(r, dict) else r


def main():
    executer = "--executer" in sys.argv
    limite = 0
    if "--limite" in sys.argv:
        try:
            limite = int(sys.argv[sys.argv.index("--limite") + 1])
        except (IndexError, ValueError):
            sys.exit("--limite attend un nombre.")

    a = _app()
    avant = _etat(a)
    print("RÉINDEXATION DU CORPUS — %s\n"
          % ("EXÉCUTION" if executer else "CONSTAT (aucune écriture, aucun appel d'API)"))
    print("État : %d documents, %d fragments, %d sans vecteur, %d document(s) sans fragment\n"
          % (avant['documents'], avant['fragments'], avant['sans_vecteur'],
             avant['sans_fragment']))

    print("PHASE 1 — re-découpage des documents sans fragment")
    n1, s1 = redecouper(a, executer)
    print("\nPHASE 2 — vectorisation des fragments sans vecteur")
    n2, s2 = vectoriser(a, executer, limite)
    print("\nPHASE 3 — recalage des statuts sur la définition en vigueur")
    n3, s3 = recaler_statuts(a, executer)

    soucis = s1 + s2 + s3
    apres = _etat(a)
    print("\n" + "-" * 66)
    print("%-28s %10s %10s" % ("", "avant", "après"))
    for cle, lib in (("documents", "documents"), ("fragments", "fragments"),
                     ("sans_vecteur", "sans vecteur"),
                     ("sans_fragment", "documents sans fragment")):
        print("%-28s %10d %10d" % (lib, avant[cle], apres[cle]))
    print("-" * 66)

    if not executer:
        print("\n%d fragment(s) à recréer, %d à vectoriser, %d statut(s) à recaler. "
              "Relancer avec --executer." % (n1, n2, n3))
        return 0

    print("\n%d fragment(s) recréés, %d vectorisés, %d statut(s) recalés."
          % (n1, n2, n3))
    if soucis:
        print("\nCE QUI N'A PAS ABOUTI :")
        for nom, motif in soucis:
            print("  · %-42s %s" % (nom[:42], motif))
        print("\nL'INDEXATION EST INCOMPLÈTE. Relancez : l'outil reprend où il s'arrête.")
        return 1
    if apres['sans_fragment']:
        print("\nIl reste %d document(s) sans fragment. Relancez pour continuer."
              % apres['sans_fragment'])
        return 1
    # LE VERDICT SUIT LA DÉFINITION EN VIGUEUR, pas l'ancienne. Exiger un
    # vecteur par fragment ferait rendre 1 à un corpus complet au sens où le
    # code l'entend depuis le 6 septembre 2026 — un échec permanent que
    # personne ne pourrait faire disparaître, donc un échec que tout le monde
    # apprendrait à ignorer.
    print("\nLe corpus est complet au sens de la définition en vigueur : chaque "
          "document a ses fragments, chacun portant son index plein texte.")
    if apres['sans_vecteur']:
        print("%d fragment(s) n'ont pas de vecteur — la recherche par le sens "
              "reste éteinte, celle par les mots les couvre tous."
              % apres['sans_vecteur'])
    return 0


if __name__ == "__main__":
    sys.exit(main())
