# -*- coding: utf-8 -*-
"""La réindexation du corpus — les propriétés que la mesure a imposées.

CE QUI A ÉTÉ MESURÉ, ET POURQUOI CET OUTIL EXISTE. Sur la base vivante, le
5 septembre 2026 : onze documents sans AUCUN fragment — les onze plus gros,
soit toute la colonne vertébrale réglementaire du corpus (AI Act, RGPD,
NIST 800-82, ISO 42001) — et 763 fragments sans vecteur sur vingt et un
autres. Cause : la boucle de vectorisation est pilotée par le navigateur
(« le client rappelle cet endpoint en boucle », dit `rag_index_next_batch`),
et aucune route de reprise n'existe.

CES RÈGLES SONT STATIQUES — elles lisent le fichier. Le bout-en-bout demande
une base, un corpus et une clé d'API : il ne peut pas vivre dans la suite.
Ce que les règles tiennent, ce sont les garanties qu'on ne veut pas perdre :
le constat ne coûte rien, un échec ne se maquille pas en succès, et le statut
se mesure au lieu de se déclarer.
"""
import io
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

OUTIL = io.open(os.path.join(ICI, "outils", "rag_reindexer.py"),
                encoding="utf-8").read()


def _corps(nom):
    """Le corps d'une fonction, du `def` au `def` suivant."""
    i = OUTIL.index("def %s(" % nom)
    j = OUTIL.find("\ndef ", i + 1)
    return OUTIL[i:j if j > 0 else len(OUTIL)]


# ══════════════════════════════════════════════════════════════════════════
# 1. LE CONSTAT NE COÛTE RIEN — ni écriture, ni appel facturé
# ══════════════════════════════════════════════════════════════════════════

def test_le_constat_est_le_mode_par_defaut():
    """Un outil qui écrit par défaut est un accident qui attend son heure."""
    corps = _corps("main")
    assert 'executer = "--executer" in sys.argv' in corps, corps[:300]


def test_le_constat_ne_demande_aucun_embedding():
    """LA VECTORISATION EST FACTURÉE. Un essai à blanc qui appellerait l'API
    coûterait autant que l'exécution — et personne ne relancerait un constat.
    Le retour anticipé doit précéder tout appel à `rag_get_embeddings`."""
    corps = _corps("vectoriser")
    i = corps.index("if not executer:")
    j = corps.index("rag_get_embeddings")
    assert i < j, ("l'appel d'embeddings n'est pas protégé par le mode constat")
    # Et ce retour anticipé doit vraiment sortir de la fonction.
    assert "return attendus, []" in corps[i:j], corps[i:j]


def test_le_constat_ne_redecoupe_rien():
    """Le découpage écrit des fragments : lui aussi attend `--executer`."""
    corps = _corps("redecouper")
    i = corps.index("if not executer:")
    j = corps.index("INSERT INTO rag_chunks")
    assert i < j, "le découpage n'est pas protégé par le mode constat"


# ══════════════════════════════════════════════════════════════════════════
# 2. LE STATUT SE MESURE — la correction de fond
# ══════════════════════════════════════════════════════════════════════════

def test_le_statut_n_est_plus_defini_ici_mais_emprunte():
    """CETTE RÈGLE EN REMPLACE DEUX, ET LE CHANGEMENT EST DÉLIBÉRÉ.

    Jusqu'au 6 septembre 2026, deux règles vivaient ici :
    `test_le_statut_est_recalcule_depuis_les_donnees` et
    `test_termine_exige_zero_fragment_sans_vecteur_et_au_moins_un_fragment`.
    Elles tenaient une définition de « termine » PROPRE À CET OUTIL — un
    document sans fragment sans vecteur — pendant que la route de dépôt en
    portait une autre. Deux définitions, donc deux vérités, et rien pour
    signaler qu'elles divergeaient.

    La décision a été prise de n'en garder qu'UNE, dans `app.rag_statut_document`,
    et d'y changer le critère : l'index plein texte, pas le vecteur. Les deux
    propriétés que ces règles tenaient n'ont pas disparu — elles sont tenues
    là où la définition vit désormais, dans `tests/test_rag_statut_indexation.py` :
    `test_termine_se_mesure_sur_l_index_plein_texte_et_pas_sur_le_vecteur` et
    `test_termine_exige_au_moins_un_fragment`.

    Ce qui reste à tenir ICI, c'est que cet outil n'en refabrique pas une
    troisième : il délègue, et il ne lui reste aucun SQL propre.
    """
    corps = _corps("_statuer")
    code = corps[corps.index('"""', corps.index('"""') + 3) + 3:]
    assert "a.rag_ecrire_statut(cur, doc_id)" in code, code
    assert "SELECT" not in code.upper(), (
        "_statuer a repris une définition à lui : elle divergera de celle de "
        "la route, comme la dernière fois\n%s" % code)


def test_le_recalage_applique_la_definition_a_tout_le_corpus():
    """Changer une définition sans repasser sur les données laisserait 32
    documents affichés « en_cours » pour une raison qui n'a plus cours — un
    écart entre ce que le code dit et ce que la base montre."""
    corps = _corps("recaler_statuts")
    assert "FROM rag_documents" in corps, corps
    assert "a.rag_statut_document(cur, d['id'])" in corps, corps


# ══════════════════════════════════════════════════════════════════════════
# 3. UN ÉCHEC S'ARRÊTE ET SE DIT
# ══════════════════════════════════════════════════════════════════════════

def test_un_echec_d_embeddings_arrete_le_travail():
    """La route de l'application avance et marque « termine ». Ici on
    s'arrête : l'outil est relançable, donc s'arrêter ne perd rien, tandis
    que continuer perdrait la trace de ce qui a échoué."""
    corps = _corps("vectoriser")
    i = corps.index("if not ok:")
    fin = corps.index("for r, vecteur in zip")
    bloc = corps[i:fin]
    assert "soucis.append" in bloc, bloc
    assert "return faits, soucis" in bloc, bloc


def test_l_echec_est_retente_avant_d_abandonner():
    """Un 429 passager ne doit pas arrêter un travail de plusieurs milliers de
    fragments : on retente avec une attente qui double."""
    assert "TENTATIVES = 3" in OUTIL, OUTIL[:900]
    corps = _corps("vectoriser")
    assert "for essai in range(TENTATIVES)" in corps, corps
    assert "ATTENTE * (2 ** essai)" in corps, corps


def test_le_code_de_sortie_distingue_le_complet_de_l_incomplet():
    """Rendre 0 sur un corpus incomplet, c'est le faux succès qu'on corrige
    partout ailleurs."""
    corps = _corps("main")
    assert "return 1" in corps, corps[-1500:]
    assert corps.index("if soucis:") < corps.rindex("return 0"), corps[-1500:]
    assert "L'INDEXATION EST INCOMPLÈTE" in corps, corps[-1500:]


# ══════════════════════════════════════════════════════════════════════════
# 4. LES FRAGMENTS SONT CEUX DU DÉPÔT, PAS DES ÉQUIVALENTS
# ══════════════════════════════════════════════════════════════════════════

def test_le_decoupage_reutilise_le_generateur_de_l_application():
    """Réécrire un découpage « équivalent » produirait des fragments coupés
    autrement que ceux du dépôt — un corpus dont une moitié serait découpée
    d'une façon et l'autre d'une autre. On emprunte le générateur en flux de
    l'application, celui-là même qu'utilise le dépôt."""
    corps = _corps("redecouper")
    assert "rag_moteur.fragments_de_fichier" in corps, corps
    assert "RAG_CHUNK_SIZE" in corps and "RAG_CHUNK_OVERLAP" in corps, corps


def test_le_fragment_recoit_son_index_plein_texte_a_l_insertion():
    """Un fragment sans `search_vector` est invisible à la recherche par
    mots-clés — c'est le défaut qui a coûté 1 268 fragments à la reprise."""
    corps = _corps("redecouper")
    assert "to_tsvector('french', %s)" in corps, corps
    assert "search_vector" in corps, corps


def test_le_compte_de_fragments_est_recale_sur_le_reel():
    """`nb_chunks` annonçait un découpage qui n'a jamais abouti. Le garder
    ferait croire à des fragments qui n'existent pas."""
    corps = _corps("redecouper")
    assert "SET nb_chunks=%s" in corps, corps
    assert "(n, d['id'])" in corps, corps


# ══════════════════════════════════════════════════════════════════════════
# 5. CE QU'IL NE FAIT PAS
# ══════════════════════════════════════════════════════════════════════════

def test_il_ne_supprime_aucun_document():
    """Le dépôt, lui, retire la ligne d'un document dont le découpage échoue.
    Ici ce serait perdre l'original — la seule chose qui rende la réparation
    possible."""
    assert "DELETE FROM rag_documents" not in OUTIL
    assert "DROP " not in OUTIL.upper()


def test_il_ecarte_un_document_dont_l_original_manque():
    """Sans octets, il n'y a rien à redécouper : le dire plutôt que d'écrire
    zéro fragment et de passer au suivant."""
    corps = _corps("redecouper")
    assert "len(octets) < 1000" in corps, corps
    assert "original absent" in corps, corps


def test_la_vectorisation_echoue_ferme_sans_cle():
    """Sans clé, ne rien tenter et le dire — plutôt que d'enchaîner des échecs
    qui ressembleraient à un problème de réseau."""
    corps = _corps("vectoriser")
    assert "if not a.MISTRAL_API_KEY:" in corps, corps
    assert "MISTRAL_API_KEY absente" in corps, corps
