"""DCWATCH EST SOUS ODbL : ON PUBLIE DES CHIFFRES, ON NE REDISTRIBUE PAS LA BASE.

LA DÉCISION, ET CE QU'ELLE COÛTE SI ON LA TIENT MAL. DCWatch apporte ce que le
référentiel de centres de données n'a pas : une estimation de puissance par
site, sur 520 sites dont 427 en France. Elle est publiée sous Open Database
License 1.0, dont l'article 4.4 impose le PARTAGE À L'IDENTIQUE à toute base
DÉRIVÉE dont on fait un usage public — et servir une base à des abonnés par une
API en relève. Verser ces puissances dans `/api/datacentres` obligerait donc à
publier le référentiel fusionné sous ODbL, c'est-à-dire à ouvrir un actif
propriétaire.

L'ARTICLE 4.5 DIT OÙ S'ARRÊTE CETTE OBLIGATION, et c'est la ligne que ce module
tient :

    b. Using this Database [...] to create a Produced Work does not create a
       Derivative Database for purposes of Section 4.4;
    c. Use of a Derivative Database internally within an organisation is not to
       the public and therefore does not fall under the requirements of
       Section 4.4.

Un chiffre agrégé est un TRAVAIL PRODUIT au sens de l'article 4.3 : il porte la
mention de provenance, et rien de plus. La ligne passe entre PRODUIRE et
REDISTRIBUER LA BASE — pas entre gratuit et payant.

CE QUE CES RÈGLES GARDENT, ET POURQUOI CHACUNE.
  — qu'aucune fonction publique du module ne rende les enregistrements : c'est
    la seule chose qui sépare un travail produit d'une base dérivée ;
  — que le référentiel servi ne porte aucune valeur venue d'ici ;
  — que la mention de l'article 4.3 accompagne les chiffres, et pas une page de
    mentions légales rangée ailleurs ;
  — que la licence et l'attribution soient déposées AVEC la base (art. 4.2.b
    et 4.2.d) ;
  — et que le seuil de regroupement tienne, y compris sur le périmètre. Éprouvé
    sur « Monaco » : trois sites, et un total sur trois sites n'est plus un
    agrégat, c'est presque la donnée. Le regroupement des régions ne protégeait
    rien tant que la sélection elle-même pouvait descendre à trois lignes.
"""
import ast
import io
import json
import os
import re

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = io.open(os.path.join(ICI, 'dcwatch.py'), encoding='utf-8').read()
APP = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
DOSSIER = os.path.join(ICI, 'dcwatch')

import sys
sys.path.insert(0, ICI)
import dcwatch  # noqa: E402


# ── LA BASE EST DÉPOSÉE AVEC SA LICENCE ET SON ATTRIBUTION ───────────────

@pytest.mark.parametrize('fichier,pourquoi', [
    ('export_summary.csv', "la base elle-même, reprise sans modification"),
    ('DATA_LICENSE', "l'article 4.2.b exige la licence AVEC la base"),
    ('ATTRIBUTION.md', "l'article 4.2.d : les mentions vont là où on les cherche"),
])
def test_la_base_est_deposee_avec_sa_licence(fichier, pourquoi):
    chemin = os.path.join(DOSSIER, fichier)
    assert os.path.exists(chemin), (
        "%s manque dans dcwatch/ — %s" % (fichier, pourquoi))
    assert os.path.getsize(chemin) > 500, (
        "%s est vide ou tronqué" % fichier)


def test_la_licence_deposee_est_bien_l_ODbL():
    """Une licence déposée sans être lue ne garantit rien. Ce contrôle vérifie
    que le fichier porte le texte de l'ODbL, et pas autre chose."""
    texte = io.open(os.path.join(DOSSIER, 'DATA_LICENSE'), encoding='utf-8').read()
    assert 'ODC Open Database License' in texte, (
        "le fichier de licence déposé n'est pas l'ODbL")
    # LES INTITULÉS TELS QU'ILS SONT ÉCRITS DANS LE TEXTE DÉPOSÉ, relevés
    # dedans et non de mémoire : l'article 4.4 s'y intitule « Share alike »,
    # minuscule comprise. Une règle écrite d'après le souvenir qu'on a d'un
    # texte mesure le souvenir.
    for article in ('4.4 Share alike', '4.5 Limits of Share Alike',
                    '4.3 Notice for using output'):
        assert article in texte, (
            "l'article « %s » manque du texte déposé : c'est pourtant lui qui "
            "fonde la séparation tenue ici" % article)


def test_l_attribution_dit_la_version_et_l_empreinte():
    """Une base importée sans son millésime ne se compare à rien : on ne peut
    plus dire si un chiffre publié vient de celle-ci ou d'une autre."""
    texte = io.open(os.path.join(DOSSIER, 'ATTRIBUTION.md'), encoding='utf-8').read()
    assert re.search(r'2026\.04\.09', texte), "la version importée n'est plus dite"
    m = re.search(r'`([0-9a-f]{64})`', texte)
    assert m, "l'empreinte SHA-256 de la base n'est plus donnée"
    import hashlib
    reel = hashlib.sha256(
        open(os.path.join(DOSSIER, 'export_summary.csv'), 'rb').read()).hexdigest()
    assert m.group(1) == reel, (
        "l'empreinte déclarée ne correspond plus au fichier : la base a été "
        "modifiée, ou remplacée sans mettre l'attribution à jour")


# ── LE MODULE NE REND QUE DES AGRÉGATS ───────────────────────────────────

def test_aucune_fonction_publique_ne_rend_les_enregistrements():
    """LA RÈGLE PRINCIPALE. C'est la seule chose qui sépare un travail produit
    (art. 4.3) d'une base dérivée (art. 4.4). Vérifiée sur l'ARBRE : un
    commentaire qui parle des enregistrements ne doit ni la satisfaire ni la
    mettre en défaut."""
    arbre = ast.parse(SOURCE)
    publiques = [n.name for n in arbre.body
                 if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')]
    assert publiques, "le module n'expose plus rien : le contrôle doit être revu"

    # LA PREUVE PAR L'EXÉCUTION, PAS PAR LE TEXTE. Une première version lisait
    # le corps désassemblé et cherchait `_lire()` après un `return` : elle
    # accusait `disponible()`, qui rend `bool(_lire())` — un booléen, pas des
    # lignes. Une heuristique sur la forme du code se trompe de sujet ; ce qui
    # compte est ce qui SORT.
    for nom in publiques:
        f = getattr(dcwatch, nom)
        try:
            sortie = f()
        except TypeError:
            continue
        for cle, v in (sortie.items() if isinstance(sortie, dict) else []):
            assert not isinstance(v, (list, tuple)), (
                "%s rend une séquence sous « %s » : une base dérivée servie "
                "publiquement déclencherait le partage à l'identique" % (nom, cle))
        assert not isinstance(sortie, (list, tuple)), (
            "%s rend directement une séquence : ce sont probablement les "
            "enregistrements de la base" % nom)


def test_aucun_nom_de_site_ne_sort_du_module():
    """Le contrôle qui ne se contente pas des types : on cherche, dans ce qui
    sort, une valeur qui n'existe que dans une ligne de la base."""
    plat = json.dumps([dcwatch.agregats(), dcwatch.agregats('France'),
                       dcwatch.couverture()], ensure_ascii=False)
    with io.open(os.path.join(DOSSIER, 'export_summary.csv'),
                 encoding='utf-8', newline='') as f:
        import csv
        lignes = list(csv.DictReader(f))
    fuites = [l['name'] for l in lignes[:80]
              if l.get('name') and len(l['name']) > 6 and l['name'] in plat]
    assert not fuites, (
        "nom(s) de site retrouvé(s) dans les agrégats : %s" % ', '.join(fuites[:5]))


# ── LE SEUIL DE REGROUPEMENT ─────────────────────────────────────────────

def test_un_perimetre_trop_petit_est_refuse():
    """ÉPROUVÉ SUR MONACO. Trois sites, et le total de puissance devenait
    presque la donnée par site. Le regroupement des ventilations ne protégeait
    rien tant que la SÉLECTION pouvait descendre à trois lignes."""
    d = dcwatch.agregats('Monaco')
    assert d.get('trop_petit') is True, (
        "un périmètre de moins de %d sites rend tout de même ses totaux"
        % dcwatch.SEUIL_AGREGAT)
    assert d.get('puissance_totale_mw') is None, (
        "le total est rendu malgré le refus")
    assert d.get('pourquoi'), "le refus n'est pas expliqué"


def test_un_perimetre_suffisant_rend_ses_chiffres():
    """L'autre moitié : un seuil qui refuserait tout ne protégerait rien, il
    supprimerait l'usage."""
    d = dcwatch.agregats('France')
    assert d.get('sites') == 427, d.get('sites')
    assert d.get('puissance_totale_mw', 0) > 1000, (
        "la France ne rend plus de total de puissance")


def test_les_ventilations_regroupent_les_petites_categories():
    d = dcwatch.agregats('France')
    for champ in ('repartition_region', 'repartition_etat', 'repartition_pays'):
        for cle, n in d[champ].items():
            assert n >= dcwatch.SEUIL_AGREGAT or cle.startswith('autres'), (
                "%s laisse une catégorie « %s » à %d site(s), sous le seuil de "
                "%d : une ventilation assez fine republie la base"
                % (champ, cle, n, dcwatch.SEUIL_AGREGAT))


# ── LA MENTION SUIT LES CHIFFRES ─────────────────────────────────────────

def test_la_mention_accompagne_chaque_sortie():
    """ARTICLE 4.3. Une mention rangée dans une page « mentions légales » ne
    suit pas le chiffre qu'elle doit accompagner."""
    for nom, d in (('agregats', dcwatch.agregats('France')),
                   ('agregats refusés', dcwatch.agregats('Monaco')),
                   ('couverture', dcwatch.couverture())):
        assert 'DCWatch' in (d.get('mention') or ''), (
            "%s ne porte plus la mention de provenance" % nom)
        assert 'ODbL' in (d.get('mention') or ''), (
            "%s ne nomme plus la licence" % nom)
        assert 'opendatacommons.org' in (d.get('mention') or ''), (
            "%s ne donne plus l'adresse de la licence (art. 4.2.b)" % nom)


def test_la_reserve_de_methode_suit_les_chiffres():
    """Un ordre de grandeur publié sans sa méthode se lit comme une mesure. La
    puissance DCWatch est estimée sur imagerie satellite : c'est une mesure de
    BÂTIMENT, pas de charge informatique."""
    d = dcwatch.agregats('France')
    assert 'non exhaustive' in (d.get('reserve') or ''), (
        "la réserve d'exhaustivité ne suit plus les chiffres")
    # LE CONTRASTE, PAS LE MOT. Une première version cherchait « bâtiment » :
    # le mot figure aussi dans « dimensions du bâtiment », si bien qu'effacer
    # la phrase qui OPPOSE bâtiment et charge informatique laissait la règle
    # passer. C'est l'opposition qui porte l'avertissement, pas le vocabulaire.
    reserve = d.get('reserve') or ''
    for notion in ('bâtiment', 'charge informatique'):
        assert notion in reserve, (
            "la réserve ne dit plus « %s » : sans l'opposition entre la mesure "
            "du bâtiment et celle de la charge informatique, l'ordre de "
            "grandeur se lira comme une mesure de consommation" % notion)


# ── LE RÉFÉRENTIEL SERVI NE CONSOMME PAS LA BASE ─────────────────────────

def test_le_referentiel_de_centres_de_donnees_n_importe_rien_de_dcwatch():
    """LA RÈGLE QUI PROTÈGE L'ACTIF. Si `datacentres.py` se mettait à lire ce
    module, le référentiel servi par /api/datacentres consommerait la base à
    chaque appel — et deviendrait dérivé sans que personne ait rien décidé.

    CE CONTRÔLE NE DIT PLUS QUE LE RÉFÉRENTIEL EST « INDEMNE », et son titre a
    changé avec sa portée. Depuis 2026-09, cinq de ses lignes portent un point
    repris de cette base, par décision explicite. Un import n'est nécessaire à
    personne pour recopier cinq coordonnées à la main : cette règle resterait
    donc verte pendant que ce qu'elle prétendait garder serait entamé. Ce qui
    borne l'emprunt vit désormais dans `tests/test_cinq_communes.py`, qui
    compte les lignes empruntées au lieu de les interdire."""
    dc = io.open(os.path.join(ICI, 'datacentres.py'), encoding='utf-8').read()
    arbre = ast.parse(dc)
    importe = [n for n in ast.walk(arbre)
               if isinstance(n, (ast.Import, ast.ImportFrom))
               and 'dcwatch' in ast.unparse(n)]
    assert not importe, (
        "datacentres.py importe dcwatch : le référentiel servi devient une "
        "base dérivée au sens de l'article 4.4, et devra être publié sous ODbL")


def test_la_route_publiee_ne_rend_pas_la_base():
    """La route ne doit rendre que ce que le module rend — et le module ne rend
    que des agrégats. On vérifie qu'elle n'a pas gagné un raccourci."""
    d = APP.index("def api_dcwatch():")
    corps = APP[d:APP.index('\n@app.route', d)]
    assert '_lire' not in corps, (
        "la route contourne le module pour lire la base directement")
    assert 'dcwatch.agregats' in corps, "la route n'appelle plus les agrégats"
