# -*- coding: utf-8 -*-
"""Ce que « termine » veut dire, et pourquoi cela ne se déduit plus d'un compteur.

LA DÉCISION DU 6 SEPTEMBRE 2026. Un document est indexé quand il a des
fragments portant chacun leur index plein texte — c'est exactement ce qui le
rend cherchable. Le vecteur est un ENRICHISSEMENT, pas une condition : la
moitié sémantique est éteinte faute de clé d'embeddings, et 32 des 45 documents
n'en auront jamais. L'exiger laisserait 71 % du corpus en « en_cours » à
jamais : une alarme que personne ne pourrait éteindre, donc une alarme que tout
le monde apprendrait à ignorer.

LE DÉFAUT QU'ON CORRIGE ICI. `rag_index_next_batch` confondait TROIS choses —
le curseur de sa boucle, le compteur affiché et le statut du document — toutes
dérivées de `max(batch_indexes) + 1`, c'est-à-dire d'une POSITION DE BOUCLE.
Elle avançait donc à l'identique que l'appel d'embeddings ait réussi ou échoué,
et finissait par afficher « indexé avec succès » sur un document sans un seul
vecteur. Sans clé Mistral, cela se serait produit à CHAQUE dépôt.

ET DEUX DÉFINITIONS VALENT ZÉRO. L'outil de réindexation portait la sienne
(« aucun fragment sans vecteur »), la route portait l'autre (« la boucle est
au bout »). Ces règles tiennent qu'il n'y en ait plus qu'UNE, empruntée et non
recopiée — accorder deux copies aujourd'hui ne les empêcherait pas de diverger
demain.
"""
import io
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)


def _lire(nom):
    return io.open(os.path.join(ICI, nom), encoding="utf-8").read()


APP = _lire("app.py")
OUTIL = _lire("outils/rag_reindexer.py")
JS = _lire("sentinel.page.js")


def _fonction(source, nom):
    """Le corps d'une fonction, du `def` au `def` suivant de même indentation."""
    i = source.index("\ndef %s(" % nom)
    j = source.find("\ndef ", i + 1)
    return source[i:j if j > 0 else len(source)]


def _code(source, nom):
    """Le corps SANS sa docstring : une règle qui lirait la prose serait verte
    devant le code qui la contredit."""
    corps = _fonction(source, nom)
    if corps.count('"""') >= 2:
        return corps[corps.index('"""', corps.index('"""') + 3) + 3:]
    return corps


def _bloc_js(depart, fin):
    i = JS.index(depart)
    return JS[i:JS.index(fin, i)]


# ══════════════════════════════════════════════════════════════════════════
# 1. UNE SEULE DÉFINITION, EMPRUNTÉE ET NON RECOPIÉE
# ══════════════════════════════════════════════════════════════════════════

def test_l_outil_de_reindexation_emprunte_la_definition_au_lieu_de_la_copier():
    """DEUX DÉFINITIONS VALENT ZÉRO. L'outil en portait une, la route une
    autre ; elles ont divergé sans que rien ne le signale. La règle exige que
    `_statuer` DÉLÈGUE — et qu'il ne lui reste aucun SQL propre, sinon une
    copie pourrait revenir à côté de l'appel."""
    code = _code(OUTIL, "_statuer")
    assert "a.rag_ecrire_statut(cur, doc_id)" in code, code
    assert "SELECT" not in code.upper(), (
        "_statuer porte encore du SQL : la définition est de nouveau en deux "
        "exemplaires\n%s" % code)


def test_la_definition_vit_dans_app_et_nulle_part_ailleurs():
    """Le témoin de la règle précédente : déléguer ne vaut que si la fonction
    déléguée existe et calcule vraiment quelque chose."""
    code = _code(APP, "rag_statut_document")
    assert "FROM rag_chunks WHERE document_id" in code, code
    assert "return ('termine' if fini else 'en_cours')" in code, code


# ══════════════════════════════════════════════════════════════════════════
# 2. « TERMINE » SE LIT DANS L'INDEX PLEIN TEXTE
# ══════════════════════════════════════════════════════════════════════════

def test_termine_se_mesure_sur_l_index_plein_texte_et_pas_sur_le_vecteur():
    """LE CŒUR DE LA DÉCISION. Compter les fragments sans vecteur laisserait 32
    documents sur 45 — dont l'AI Act, le RGPD, NIST 800-82 et ISO 42001 — en
    « en_cours » à jamais, la vectorisation ne devant pas revenir."""
    code = _code(APP, "rag_statut_document")
    assert "count(*) FILTER (WHERE search_vector IS NULL)" in code, code
    assert "embedding" not in code, (
        "le statut dépend encore du vecteur : 71 %% du corpus resterait "
        "« en_cours » à jamais\n%s" % code)


def test_termine_exige_au_moins_un_fragment():
    """Zéro fragment sans index plein texte est vrai aussi quand il n'y a aucun
    fragment : un document vide passerait pour indexé."""
    code = _code(APP, "rag_statut_document")
    assert re.search(r"fini = \(total > 0 and sans_index == 0\)", code), code


def test_sqlite_dit_qu_il_ne_peut_pas_mesurer_au_lieu_de_rendre_un_faux_zero():
    """En SQLite `rag_chunks` n'a PAS de colonne `search_vector` (voir
    `rag_init_db`). Rendre 0 sans le dire ferait passer une impossibilité de
    mesure pour une mesure."""
    corps = _fonction(APP, "rag_statut_document")
    doc = corps[:corps.index("if REGISTRE_USE_PG:")]
    assert "SQLite" in doc and "n existe PAS" in doc, doc
    code = _code(APP, "rag_statut_document")
    assert "'SELECT count(*) AS total, 0 AS sans_index'" in code, code


# ══════════════════════════════════════════════════════════════════════════
# 3. LE CURSEUR DE LA BOUCLE SE LIT DANS LES DONNÉES
# ══════════════════════════════════════════════════════════════════════════

def test_le_lot_suivant_se_choisit_sur_les_fragments_sans_vecteur():
    """LE DÉFAUT DE FOND. Le curseur était `max(batch_indexes) + 1` — une
    position de boucle qui avançait que le lot ait réussi ou non, et sautait
    donc définitivement les fragments d'un lot échoué."""
    code = _code(APP, "rag_index_next_batch")
    lot = code[code.index("SELECT chunk_index, chunk_text"):]
    lot = lot[:lot.index(")")]
    assert "embedding IS NULL" in lot, lot
    assert "ORDER BY chunk_index LIMIT" in lot, lot


def test_aucune_position_de_boucle_ne_subsiste_dans_la_route():
    """Le témoin de la règle précédente : un curseur relu dans les données ne
    sert à rien si l'ancien compteur traîne encore quelque part."""
    code = _code(APP, "rag_index_next_batch")
    for vestige in ("max(batch_indexes)", "already_done", "batch_indexes"):
        assert vestige not in code, (
            "%s subsiste : la route retrouve une position de boucle\n%s"
            % (vestige, code))


def test_le_compte_de_vecteurs_ne_lit_pas_une_colonne_qui_peut_ne_pas_exister():
    """`embedding` N'EXISTE PAS quand pgvector est absent — ni en SQLite, ni
    même sur PostgreSQL : `rag_init_db` crée alors une `rag_chunks` sans elle.
    L'interroger ferait tomber en erreur un chemin dont tout le reste marche.
    La garde doit donc porter sur pgvector, pas seulement sur le moteur."""
    code = _code(APP, "rag_index_next_batch")
    i = code.index("def _vecteurs():")
    j = code.index("def _rendre(")
    garde = code[i:j]
    assert "if not (RAG_PGVECTOR_AVAILABLE and REGISTRE_USE_PG):" in garde, garde
    assert garde.index("RAG_PGVECTOR_AVAILABLE") < garde.index("embedding IS NOT NULL"), garde


# ══════════════════════════════════════════════════════════════════════════
# 4. UN ÉCHEC S'ARRÊTE ET SE DIT
# ══════════════════════════════════════════════════════════════════════════

def test_un_echec_d_embeddings_interrompt_au_lieu_d_avancer():
    """La route rendait le même compteur en cas d'échec qu'en cas de succès.
    Elle doit désormais RENDRE UN ÉTAT DISTINCT, et n'écrire aucun vecteur."""
    code = _code(APP, "rag_index_next_batch")
    i = code.index("if not embed_ok:")
    j = code.index("for r, embedding in zip")
    bloc = code[i:j]
    assert "_rendre('interrompue'" in bloc, bloc
    assert "UPDATE" not in bloc.upper(), bloc


def test_l_absence_de_cle_est_dite_avant_tout_travail():
    """Sans clé, faire tourner le client soixante fois pour soixante échecs
    identiques serait une perte de temps déguisée en tentative."""
    code = _code(APP, "rag_index_next_batch")
    i = code.index("if not MISTRAL_API_KEY:")
    j = code.index("SELECT chunk_index, chunk_text")
    assert i < j, "l'absence de clé est constatée après avoir cherché un lot"
    assert "_rendre('indisponible'" in code[i:j], code[i:j]


# ══════════════════════════════════════════════════════════════════════════
# 5. LE CLIENT S'ARRÊTE, ET NE PROMET PAS CE QUI N'A PAS EU LIEU
# ══════════════════════════════════════════════════════════════════════════

def test_le_client_ne_boucle_que_sur_en_cours():
    """« complete » n'a plus rien à faire, « indisponible » ne peut rien faire,
    « interrompue » a échoué : rappeler ne ferait que répéter l'échec soixante
    fois. Un seul état justifie un tour de plus."""
    bloc = _bloc_js("window.ragPollIndexation = function", "window.ragDeleteDoc")
    assert "if(d.vectorisation !== 'en_cours'){" in bloc, bloc
    assert "d.statut === 'termine'){" not in bloc, (
        "le client boucle encore sur le statut du document, qui vaut "
        "« termine » dès le découpage : il ne vectoriserait plus jamais rien")


def test_le_client_ne_promet_un_succes_semantique_que_s_il_y_a_des_vecteurs():
    """« ✅ indexé avec succès » sur un document sans un seul vecteur, c'est la
    même faute que la « transaction validée » d'un outil qui n'a rien écrit.
    Sans vecteur le document EST cherchable — par les mots — et le dire ainsi
    vaut mieux qu'une coche qui promet autre chose."""
    bloc = _bloc_js("window.ragPollIndexation = function", "window.ragDeleteDoc")
    assert "vect > 0" in bloc, bloc
    assert "recherche par mots-clés" in bloc, bloc


# ══════════════════════════════════════════════════════════════════════════
# 6. LE RECALAGE DU CORPUS EXISTANT
# ══════════════════════════════════════════════════════════════════════════

def test_le_recalage_des_statuts_n_ecrit_qu_en_execution():
    """Changer une définition sans repasser sur les données laisserait 32
    documents affichés « en_cours » pour une raison qui n'a plus cours. Mais le
    constat, lui, ne doit rien écrire."""
    code = _code(OUTIL, "recaler_statuts")
    i = code.index("if executer:")
    j = code.index("a.rag_ecrire_statut")
    assert i < j, "le recalage écrit sans attendre --executer"
    assert "conn.commit()" in code, code


def test_le_verdict_final_suit_la_definition_en_vigueur():
    """Exiger un vecteur par fragment ferait rendre 1 à un corpus complet au
    sens où le code l'entend : un échec permanent que personne ne pourrait
    faire disparaître."""
    code = _code(OUTIL, "main")
    fin = code[code.index("if apres['sans_fragment']:"):]
    assert "return 1" in fin, fin
    verdict = fin[fin.index("Le corpus est complet"):]
    assert "return 0" in verdict, verdict
    assert "sans_vecteur'] or" not in fin, (
        "le verdict exige encore un vecteur par fragment\n%s" % fin)
