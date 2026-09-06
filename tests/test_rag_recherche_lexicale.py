# -*- coding: utf-8 -*-
"""La recherche du corpus quand la moitié sémantique est éteinte.

CE QUE LA MESURE A ÉTABLI, le 6 septembre 2026, sur la base vivante : 6 787
fragments, dont 6 787 avec index plein texte (100 %) et 363 avec vecteur
(5,3 %). Le service n'a pas de clé Mistral, et `ANTHROPIC_API_KEY` ne peut pas
y suppléer — Anthropic ne publie pas d'API d'embeddings. La décision a été
prise d'en rester là : la recherche par les mots couvre tout le corpus.

CE QUE CES RÈGLES PROTÈGENT. Cette décision n'est tenable que si deux choses
restent vraies, et aucune ne l'est par construction :

  · la recherche par les MOTS ne dépend d'aucun vecteur — sinon 95 % du corpus
    disparaîtrait de la réponse ;
  · RIEN ne filtre sur `statut_indexation` — 32 des 45 documents resteront
    `en_cours` à jamais faute de vecteurs, dont les ONZE TEXTES RÉGLEMENTAIRES
    (AI Act, RGPD, NIST 800-82, ISO 42001) recréés par la réindexation. Un
    filtre sur ce statut les ferait disparaître sans rien dire.

Ces règles LISENT LE SQL des fonctions concernées, pas la prose qui les
entoure : une règle qui se contenterait de trouver un mot quelque part dans le
fichier resterait verte devant la requête qui casse tout.
"""
import io
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

APP = io.open(os.path.join(ICI, "app.py"), encoding="utf-8").read()


def _corps(nom):
    """Le corps d'une fonction, du `def` au `def` suivant de même indentation."""
    i = APP.index("\ndef %s(" % nom)
    j = APP.find("\ndef ", i + 1)
    return APP[i:j if j > 0 else len(APP)]


def _sql(nom):
    """Les seules chaînes passées à `cur.execute` dans cette fonction.

    On isole le SQL de la docstring : c'est la différence entre une règle qui
    mesure et une règle qui constate.
    """
    corps = _corps(nom)
    debut = corps.index("cur.execute(")
    # Jusqu'à la fin du corps : on garde tout ce qui suit le premier execute,
    # docstring exclue.
    return corps[debut:]


# ══════════════════════════════════════════════════════════════════════════
# 1. LA RECHERCHE PAR LES MOTS NE DÉPEND D'AUCUN VECTEUR
# ══════════════════════════════════════════════════════════════════════════

def test_la_recherche_par_les_mots_n_exige_aucun_vecteur():
    """95 % DU CORPUS EN DÉPEND. Si la passe lexicale joignait `embedding`, ou
    exigeait qu'il soit non nul, elle se réduirait aux 363 fragments vectorisés
    — et les onze textes réglementaires, qui n'en ont aucun, sortiraient de
    toute réponse sans qu'aucune erreur ne soit levée."""
    sql = _sql("_rag_lexical")
    assert "embedding" not in sql, (
        "la recherche par les mots s'appuie sur un vecteur :\n%s" % sql[:600])


def test_la_recherche_par_les_mots_s_appuie_sur_l_index_plein_texte():
    """Le témoin positif de la règle précédente : l'absence d'`embedding` ne
    vaut que si la passe interroge bien `search_vector`. Sans cela, une passe
    vide passerait les deux règles."""
    sql = _sql("_rag_lexical")
    assert "c.search_vector @@" in sql, sql[:600]
    assert "ts_rank(c.search_vector" in sql, sql[:600]


# ══════════════════════════════════════════════════════════════════════════
# 2. RIEN NE FILTRE SUR LE STATUT D'INDEXATION
# ══════════════════════════════════════════════════════════════════════════

def test_aucune_recherche_ne_filtre_sur_le_statut_d_indexation():
    """32 DOCUMENTS SUR 45 RESTERONT « en_cours » À JAMAIS — la vectorisation
    ne reviendra pas. Filtrer là-dessus retirerait de la recherche l'AI Act, le
    RGPD, NIST 800-82 et ISO 42001, en silence et sans erreur.

    La règle énumère les trois fonctions du chemin de lecture plutôt que d'en
    nommer une : ajouter un moteur sans l'inscrire ici serait le trou par
    lequel le filtre reviendrait.
    """
    for nom in ("_rag_vectoriel", "_rag_lexical", "rag_recherche"):
        corps = _corps(nom)
        code = corps[corps.index('"""', corps.index('"""') + 3) + 3:] \
            if corps.count('"""') >= 2 else corps
        assert "statut_indexation" not in code, (
            "%s filtre sur le statut d'indexation : les 32 documents "
            "définitivement « en_cours » disparaîtraient de la recherche" % nom)


def test_le_seul_filtre_de_la_recherche_porte_sur_les_pages_liees():
    """Le témoin de la règle précédente : elle ne vaut que si l'on sait ce que
    le filtre contient VRAIMENT. Un `filtre_sql` devenu libre passerait
    l'absence de « statut_indexation » tout en filtrant sur autre chose."""
    corps = _corps("rag_recherche")
    filtres = re.findall(r"filtre_sql = '([^']+)'", corps)
    assert filtres == ["AND d.pages_liees LIKE %s"], filtres


# ══════════════════════════════════════════════════════════════════════════
# 3. LA MOITIÉ ÉTEINTE S'ÉTEINT PROPREMENT
# ══════════════════════════════════════════════════════════════════════════

def test_l_absence_d_embeddings_rend_une_liste_vide_et_pas_une_exception():
    """Sans clé, `rag_get_embeddings` rend (False, 'no_mistral_key') à CHAQUE
    appel. Si ce refus remontait en exception, la recherche entière tomberait
    au lieu de rendre sa moitié lexicale — l'assistant serait muet sur un
    corpus parfaitement cherchable."""
    corps = _corps("_rag_vectoriel")
    i = corps.index("ok, embs = rag_get_embeddings")
    j = corps.index("cur.execute(")
    assert re.search(r"if not ok:\s*\n\s*return \[\]", corps[i:j]), corps[i:j]
    # Et l'échec tardif — une requête refusée, un pgvector absent — aussi.
    queue = corps[corps.rindex("except Exception"):]
    assert "return []" in queue, queue


def test_le_mode_annonce_ce_qui_a_reellement_repondu():
    """LE FAUX SUCCÈS QU'ON NE VEUT PAS ICI. La réponse porte un `mode` que le
    frontend affiche. Sans vecteurs il doit dire « mots », jamais « hybride » :
    annoncer une recherche par le sens qui n'a rien cherché serait la même
    faute que la « transaction validée » d'un outil qui n'a rien écrit."""
    corps = _corps("rag_recherche")
    m = re.search(r"if v and l:\s*\n\s*mode = '([a-z+]+)'"
                  r"\s*\n\s*elif v:\s*\n\s*mode = '([a-z+]+)'"
                  r"\s*\n\s*elif l:\s*\n\s*mode = '([a-z+]+)'"
                  r"\s*\n\s*else:\s*\n\s*mode = '([a-z+]+)'", corps)
    assert m, corps[-900:]
    assert m.groups() == ('hybride', 'sens', 'mots', 'aucun'), m.groups()


def test_les_deux_moteurs_sont_interroges_avant_la_fusion():
    """Le témoin des règles ci-dessus : elles ne veulent rien dire si un seul
    moteur est appelé. La fusion doit recevoir les deux listes — c'est ce qui
    rend la moitié éteinte inoffensive plutôt que fatale."""
    corps = _corps("rag_recherche")
    assert "v = _rag_vectoriel(cur, query, large, filtre_sql, filtre_params)" in corps, corps
    assert "l = _rag_lexical(cur, query, large, filtre_sql, filtre_params)" in corps, corps
    assert "fusionner([v, l]" in corps, corps


# ══════════════════════════════════════════════════════════════════════════
# 4. LA DÉCISION EST ÉCRITE LÀ OÙ ON LA LIRA
# ══════════════════════════════════════════════════════════════════════════

def test_le_code_dit_que_la_moitie_semantique_est_eteinte_volontairement():
    """Une moitié silencieusement inactive se lit comme une panne, et quelqu'un
    finira par « réparer » en croyant bien faire. Le code doit porter la
    décision ET son motif : Anthropic ne fait pas d'embeddings, donc la clé
    Claude ne peut pas suppléer Mistral."""
    doc = _corps("_rag_vectoriel")
    doc = doc[:doc.index("cur.execute(")]
    assert "INACTIVE" in doc and "DELIBERE" in doc, doc
    assert "ANTHROPIC_API_KEY" in doc, doc
    assert "mistral-embed" in doc, doc
    assert "statut_indexation" in doc, doc
