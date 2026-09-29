# -*- coding: utf-8 -*-
"""LE GARDIEN DURABLE DE LA TRADUCTION DE SENTINEL — sans navigateur.

CE QUI EXISTAIT, ET CE QUI MANQUAIT. La recette recette_sentinel_langue.js
mesure, dans un vrai navigateur, ce qui reste en français quand EN est
choisi. Elle se joue à la main, contre un serveur : la suite de tests ne
l'exécute pas. Il fallait une règle STATIQUE, jouable à chaque passage de la
suite, qui tombe le jour où quelqu'un ajoute une page en français sans la
traduire.

CE QUE CES RÈGLES MESURENT. Le catalogue (i18n/sentinel/CATALOGUE.json,
produit par l'outil d'inventaire) porte toutes les clés françaises du corps
de Sentinel ; les dictionnaires (i18n/sentinel/*.json) portent les
traductions. La COUVERTURE EN MOTS — part des mots du catalogue dont la clé
est traduite — doit atteindre le PLANCHER écrit dans
i18n/sentinel/SEUIL_COUVERTURE. Il valait 0 tant que le lot de traduction
n'avait pas commencé ; il monte ensuite, et ne redescend pas.

DEUX SEUILS, ET ILS NE DISENT PAS LA MÊME CHOSE. Celui-ci est un PLANCHER de
couverture, lu ici. i18n/sentinel/SEUIL est un PLAFOND : la part française
encore visible À L'ÉCRAN que le dépôt promet de ne pas dépasser, gardée par
tests/test_sentinel_donnees_saisies.py sur i18n/sentinel/MESURE_APRES.json.
Un seul fichier pour les deux désarmerait l'un en silence — un plancher à
5 % est tenu par n'importe quoi.

TANT QUE LE CATALOGUE N'EXISTE PAS, la règle de couverture SAUTE en le
disant : elle ne peut rien garder, et un « passe » silencieux serait un
mensonge. Le calcul, lui, est éprouvé sur des catalogues et dictionnaires
d'essai (outils/sentinel_langue_couverture.py), pour que le jour où le
catalogue arrive, le gardien mesure juste du premier coup.
"""
import importlib.util
import io
import json
import os

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER = os.path.join(_RACINE, 'i18n', 'sentinel')
CATALOGUE = os.path.join(DOSSIER, 'CATALOGUE.json')
SEUIL = os.path.join(DOSSIER, 'SEUIL_COUVERTURE')


def _charger():
    spec = importlib.util.spec_from_file_location(
        'sentinel_langue_couverture',
        os.path.join(_RACINE, 'outils', 'sentinel_langue_couverture.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


C = _charger()


def _ecrire(dossier, nom, contenu):
    p = os.path.join(dossier, nom)
    with io.open(p, 'w', encoding='utf-8') as f:
        f.write(contenu if isinstance(contenu, u''.__class__) else json.dumps(contenu, ensure_ascii=False))
    return p


# ══════════════════════════════════════════════════════════════════════════
#  1. LE GARDIEN LUI-MÊME — sur le dépôt réel
# ══════════════════════════════════════════════════════════════════════════

def test_le_fichier_SEUIL_existe_et_porte_une_part_entre_0_et_1():
    """Le seuil est un FICHIER, pas une constante de test : le lot de
    traduction le monte sans toucher aux règles, et sa valeur se lit dans
    l'historique. Les DEUX seuils du dossier se lisent de la même manière."""
    assert os.path.isfile(os.path.join(DOSSIER, 'SEUIL')), 'i18n/sentinel/SEUIL manque'
    assert 0.0 <= C.lire_seuil(os.path.join(DOSSIER, 'SEUIL')) <= 1.0
    assert os.path.isfile(SEUIL), 'i18n/sentinel/SEUIL_COUVERTURE manque'
    s = C.lire_seuil(SEUIL)
    assert 0.0 <= s <= 1.0, s


def test_la_couverture_en_mots_du_catalogue_atteint_le_SEUIL():
    """LA RÈGLE QUI TOMBERA le jour où une page française est ajoutée sans
    traduction : le catalogue grossit, la couverture baisse sous le seuil.
    Le message nomme les clés manquantes les plus longues — ce qu'il faut
    traduire d'abord."""
    if not os.path.isfile(CATALOGUE):
        pytest.skip('i18n/sentinel/CATALOGUE.json n\'existe pas encore : '
                    'l\'outil d\'inventaire ne l\'a pas produit — rien à garder')
    seuil = C.lire_seuil(SEUIL)
    cat = C.lire_json(CATALOGUE)
    dico = C.dictionnaires_du_dossier(DOSSIER)
    cv = C.couverture(cat, dico)
    exemples = u'\n  '.join(u'[%s] (%d mots) %s' % (r, n, k[:90]) for r, k, n in cv['manquantes'][:10])
    assert cv['part'] >= seuil, (
        u'couverture %.1f %% (%d / %d mots, %d / %d clés) sous le seuil %.1f %% — '
        u'les clés manquantes les plus longues :\n  %s'
        % (cv['part'] * 100, cv['mots_couverts'], cv['mots_total'],
           cv['cles_couvertes'], cv['cles_total'], seuil * 100, exemples))


def test_le_dossier_reel_ne_prend_ni_le_catalogue_ni_une_mesure_pour_un_dictionnaire():
    """Le catalogue porte du FRANÇAIS, une mesure porte des CHIFFRES : ni
    l'un ni l'autre n'est une traduction, et les compter ferait monter la
    couverture sans qu'un mot soit traduit."""
    assert not C.est_dictionnaire(os.path.join(DOSSIER, 'CATALOGUE.json'))
    assert not C.est_dictionnaire(os.path.join(DOSSIER, 'MESURE_AVANT.json'))
    assert C.est_dictionnaire(os.path.join(DOSSIER, '_exemple.json'))
    assert not C.est_dictionnaire(os.path.join(DOSSIER, 'SEUIL'))
    assert not C.est_dictionnaire(os.path.join(DOSSIER, 'SEUIL_COUVERTURE'))


# ══════════════════════════════════════════════════════════════════════════
#  2. LE CALCUL, ÉPROUVÉ SUR DES DOSSIERS D'ESSAI
# ══════════════════════════════════════════════════════════════════════════

CATALOGUE_ESSAI = {
    'texte': {
        u'Voir': u'Voir',
        u'Programme détaillé': u'Programme détaillé',
        u'Un expert vous accompagne à chaque étape.': u'Un expert vous accompagne à chaque étape.',
    },
    'bloc': {
        u'Le cadre ISO # structure l\'ensemble.': {'fr': u'Le cadre ISO 42001 structure l\'ensemble.',
                                                   'html': u'Le <b>cadre</b> ISO 42001 structure l\'ensemble.',
                                                   'pages': ['cadre-normatif']},
    },
    'attr': {
        u'Ouvrir le guide': u'Ouvrir le guide',
    },
}


def test_les_mots_se_comptent_en_lettres_et_le_diese_ne_compte_pas():
    assert C.mots(u'Toutes (#) — l’audit de maturité') == 4
    assert C.mots(u'#') == 0
    assert C.mots(u'') == 0
    assert C.mots(None) == 0


def test_la_couverture_est_en_MOTS_et_pas_en_cles():
    """Deux clés sur cinq traduites, mais les deux plus longues : 12 mots sur
    18 (« l'ensemble » est un mot). Compter les clés dirait 40 % ; en mots,
    c'est 67 %, et c'est ce qui se rapproche de ce qu'un lecteur voit."""
    dico = {'texte': {u'Un expert vous accompagne à chaque étape.': u'An expert supports you at every step.'},
            'bloc': {u'Le cadre ISO # structure l\'ensemble.': u'The ISO # <b>framework</b> structures the whole.'}}
    cv = C.couverture(CATALOGUE_ESSAI, dico)
    assert (cv['mots_total'], cv['mots_couverts']) == (18, 12), cv
    assert (cv['cles_total'], cv['cles_couvertes']) == (5, 2), cv
    assert abs(cv['part'] - 12.0 / 18) < 1e-9, cv['part']


def test_un_attribut_se_cherche_dans_le_dictionnaire_TEXTE():
    """Le navigateur traduit title, aria-label et placeholder par le
    dictionnaire « texte » (sentinel.i18n.js, sentAttrsAppliquer) : la
    couverture doit chercher au même endroit, sinon un attribut traduit
    compterait pour manquant."""
    dico = {'texte': {u'Ouvrir le guide': u'Open the guide'}, 'bloc': {}}
    cv = C.couverture(CATALOGUE_ESSAI, dico)
    assert cv['cles_couvertes'] == 1 and cv['mots_couverts'] == 3, cv
    assert ('attr', u'Ouvrir le guide', 3) not in cv['manquantes']


def test_les_manquantes_sont_nommees_des_plus_longues_aux_plus_courtes():
    cv = C.couverture(CATALOGUE_ESSAI, {'texte': {}, 'bloc': {}})
    assert [m[2] for m in cv['manquantes']] == sorted([m[2] for m in cv['manquantes']], reverse=True)
    assert cv['manquantes'][0][1] == u'Un expert vous accompagne à chaque étape.'
    assert cv['part'] == 0.0


def test_un_catalogue_vide_est_couvert_a_100_pour_cent():
    assert C.couverture({'texte': {}}, {'texte': {}, 'bloc': {}})['part'] == 1.0


@pytest.mark.parametrize('cat', [[], u'x', {}, {'texte': [1, 2]}],
                         ids=['liste', 'chaine', 'sans-regime', 'regime-liste'])
def test_un_catalogue_de_forme_inconnue_est_une_ERREUR_nommee_et_pas_un_catalogue_vide(cat):
    """Un catalogue mal lu qui passerait pour vide rendrait 100 % de
    couverture : le gardien ne garderait plus rien, en vert."""
    with pytest.raises(ValueError):
        C.couverture(cat, {'texte': {}, 'bloc': {}})


def test_les_dictionnaires_du_dossier_se_fusionnent_sans_le_catalogue_ni_les_mesures(tmp_path):
    d = str(tmp_path)
    _ecrire(d, 'a.json', {'_lot': 'a', 'texte': {u'Voir': u'View'}, 'bloc': {u'X <b>y</b>': u'X <b>y</b>'}})
    _ecrire(d, 'b.json', {'_lot': 'b', 'texte': {u'Fermer': u'Close', u'Vide': u'  ', u'Nombre': 3}})
    _ecrire(d, 'CATALOGUE.json', {'texte': {u'Voir': u'Voir', u'Ouvrir': u'Ouvrir'}})
    _ecrire(d, 'MESURE_AVANT.json', {'texte': {u'Ouvrir': u'Ouvrir'}, 'global': {}})
    dico = C.dictionnaires_du_dossier(d)
    assert dico['texte'] == {u'Voir': u'View', u'Fermer': u'Close'}, dico
    assert dico['bloc'] == {u'X <b>y</b>': u'X <b>y</b>'}, dico


def test_le_gardien_tombe_quand_une_cle_francaise_arrive_sans_traduction(tmp_path):
    """LE SCÉNARIO QUE LE GARDIEN EXISTE POUR ATTRAPER, joué en petit : tout
    est traduit, le seuil est monté à 1, puis une page ajoute une phrase
    française au catalogue — la couverture passe sous le seuil."""
    d = str(tmp_path)
    _ecrire(d, 'a.json', {'texte': {u'Voir': u'View'}})
    cat = {'texte': {u'Voir': u'Voir'}}
    assert C.couverture(cat, C.dictionnaires_du_dossier(d))['part'] >= 1.0
    cat['texte'][u'Une phrase que personne n\'a traduite'] = u'Une phrase que personne n\'a traduite'
    assert C.couverture(cat, C.dictionnaires_du_dossier(d))['part'] < 1.0


# ══════════════════════════════════════════════════════════════════════════
#  3. LE FICHIER SEUIL
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize('contenu,attendu', [
    (u'0\n', 0.0),
    (u'# commentaire\n\n0.85\n', 0.85),
    (u'0,5\n', 0.5),
    (u'1', 1.0),
], ids=['zero', 'commente', 'virgule', 'un'])
def test_le_SEUIL_se_lit_avec_ses_commentaires(tmp_path, contenu, attendu):
    p = _ecrire(str(tmp_path), 'SEUIL', contenu)
    assert C.lire_seuil(p) == attendu


@pytest.mark.parametrize('contenu', [u'', u'# rien\n', u'0\n1\n', u'abc\n', u'1.5\n', u'-0.1\n'],
                         ids=['vide', 'que-commentaire', 'deux-valeurs', 'lettres', 'trop-grand', 'negatif'])
def test_un_SEUIL_mal_ecrit_est_une_ERREUR_nommee(tmp_path, contenu):
    """Un seuil illisible qui vaudrait 0 par défaut désarmerait le gardien
    en silence."""
    p = _ecrire(str(tmp_path), 'SEUIL', contenu)
    with pytest.raises(ValueError):
        C.lire_seuil(p)
