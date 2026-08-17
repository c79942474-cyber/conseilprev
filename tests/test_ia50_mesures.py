"""Transparence IA Act (art. 50) : la MESURE, à côté de l'attestation.

CE QUE CES TESTS PROTÈGENT, ET LA FAUTE QU'ILS EMPÊCHENT.

Le registre de l'article 50 déclarait la mention du Copilote Sentinel
« EN PLACE » alors que sentinel.html ne la portait pas : une déclaration ne se
périme pas toute seule quand le code change. Le module de vérification mesure
donc les artefacts RÉELLEMENT SERVIS — fichiers relus du disque à chaque
appel, document généré et relu à chaque appel — au lieu de faire confiance à
ce que le registre affirme.

Ces tests exécutent chaque mesure sur le dépôt réel, puis PROUVENT qu'elle
discrimine : la même mesure, servie d'un artefact amputé de sa mention, doit
répondre non-conforme. Une mesure qui dirait « conforme » aux deux ne
mesurerait rien — c'est le défaut exact que le registre avait.
"""
import io
import os
import sys
import zipfile

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')

import app as application  # noqa: E402


# ── Les artefacts réels du dépôt ───────────────────────────────────────────

def test_le_chat_public_porte_la_mention():
    r = application._ia50_mesure_mention_chat(
        application._ia50_page('index.html'), 'index.html')
    assert r['statut'] == 'conforme', r['preuve']
    assert '2024/1689' in r['preuve']


def test_le_chat_sentinel_porte_la_mention():
    """C'est LE défaut qui a motivé le module : le registre disait EN PLACE,
    la page ne portait rien. La mention y est désormais ; si ce test tombe,
    quelqu'un l'a retirée — et le registre recommencera à mentir."""
    r = application._ia50_mesure_mention_chat(
        application._ia50_page('sentinel.html'), 'sentinel.html')
    assert r['statut'] == 'conforme', r['preuve']


def test_l_explorateur_porte_le_bandeau():
    r = application._ia50_mesure_bandeau_explorateur(
        application._ia50_page('sentinel.html'))
    assert r['statut'] == 'conforme', r['preuve']


def test_le_document_genere_porte_le_marquage():
    """La mesure GÉNÈRE un document et LIT ses propriétés — elle ne fait pas
    confiance au code qui promet."""
    r = application._ia50_mesure_documents()
    assert r['statut'] == 'conforme', r['preuve']
    assert 'docProps/core.xml' in r['preuve']


def test_les_actualites_restent_une_attestation():
    """L'exception 50.4 (contrôle éditorial) n'est PAS mesurable par une
    machine : la mesure vérifie la PUBLICATION de la mention et rend
    « partiel » — jamais un vert entier. Un vert ici signifierait qu'une
    machine a attesté d'un examen humain."""
    r = application._ia50_mesure_actualites(
        application._ia50_page('actualites.html'))
    assert r['statut'] == 'partiel', r['preuve']
    assert 'attestation' in r['preuve']


# ── La discrimination : la mesure amputée doit tomber ─────────────────────

def test_la_mesure_de_mention_discrimine():
    page = application._ia50_page('sentinel.html')
    ampute = page.replace('interagissez avec une IA', 'interagissez avec un service')
    r = application._ia50_mesure_mention_chat(ampute, 'sentinel.html')
    assert r['statut'] == 'non-conforme', (
        'la mention retirée, la mesure dit encore conforme : elle ne mesure rien')
    assert '50.1' in r['preuve']


def test_la_mesure_de_bandeau_discrimine():
    page = application._ia50_page('sentinel.html')
    r = application._ia50_mesure_bandeau_explorateur(
        page.replace('AI GENERATED', 'SYNTHESE'))
    assert r['statut'] == 'non-conforme'


def test_un_fichier_absent_est_non_mesurable_pas_conforme():
    """Un artefact qu'on ne peut pas lire n'est ni vert ni rouge : il est
    non mesurable, et le dire est la seule réponse honnête."""
    r = application._ia50_mesure_mention_chat(None, 'disparu.html')
    assert r['statut'] == 'non-mesurable'


def test_un_document_sans_ia_ne_porte_pas_le_marquage():
    """Le versant symétrique du marquage : un document produit par calcul
    déterministe ne doit PAS être marqué IA — un marquage apposé partout ne
    signale plus rien (doctrine de livrables_export)."""
    import livrables_export
    blob = livrables_export.build_docx('# Controle\n\nSans IA.\n',
                                       {'ia': False, 'label': 'Controle'})
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        core = z.read('docProps/core.xml').decode('utf-8', 'replace')
    assert livrables_export.MARQUE_IA not in core
    assert 'deterministe' in core


# ── Le rattachement au registre ────────────────────────────────────────────

def test_chaque_mesure_trouve_sa_ligne_du_registre_par_defaut():
    """Les mesures se rattachent aux lignes par motif sur le nom du système.
    Si un motif ne matche plus aucune ligne d'IA50_USAGES_DEFAUT, la mesure
    flottera sans ligne — et la colonne « Mesuré » du tableau restera vide
    sans que rien ne le dise."""
    import re
    systemes = [u['systeme'] for u in application.IA50_USAGES_DEFAUT]
    for m in application._IA50_MESURES:
        touches = [s for s in systemes if re.search(m['motif'], s)]
        assert touches, ('la mesure %r ne matche aucune ligne du registre '
                         'par defaut' % m['cle'])
