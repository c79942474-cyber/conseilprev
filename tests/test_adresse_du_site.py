"""L'ADRESSE DU SITE — une promesse que le module ne tenait pas.

CE QUE `seo.py` ANNONCE EN TÊTE DE FICHIER :

    « `SITE_BASE_URL` est lue dans l'environnement. Le jour où le site quitte
    `conseilprev.onrender.com` pour un nom de domaine propre, aucune ligne de
    code ne change — et rien ne reste en arrière avec l'ancienne adresse en
    dur, ce qui serait le pire des deux mondes : des canoniques qui pointent
    vers un site qu'on a quitté. »

CE QU'IL FAISAIT. `balises()` ne comble que les trous — « on n'écrase jamais
ce qui est déjà là ». Or seize pages portent leur canonique écrite à la main.
`SITE_BASE_URL` n'avait donc aucun effet sur elles : mesuré, vingt-six
occurrences de l'ancien hôte survivaient dans les pages servies, dont neuf sur
la seule page d'accueil. Le module décrivait, mot pour mot, le défaut qu'il
causait.

POURQUOI CELA COMPTE MAINTENANT. Un second service a été créé sur Render
(`conseilprevia`). Basculer dessus sans corriger cela reviendrait à servir des
pages qui déclarent aux moteurs que leur version canonique est ailleurs — sur
un service qu'on s'apprête à éteindre.

LA DISTINCTION QUI RESTE JUSTE. Un titre ou une description écrits à la main
sont un travail éditorial : `balises()` a raison de ne pas y toucher. Une
adresse absolue n'est pas de l'écriture, c'est une coordonnée — elle doit
suivre le site. Ces contrôles gardent les deux moitiés de cette distinction.
"""
import glob
import importlib
import io
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

AUTRE = 'https://exemple-nouveau-domaine.test'


def _seo(base=None):
    """Le module rechargé avec l'adresse voulue — `BASE` est lue à l'import."""
    if base:
        os.environ['SITE_BASE_URL'] = base
    else:
        os.environ.pop('SITE_BASE_URL', None)
    import seo
    return importlib.reload(seo)


@pytest.fixture(autouse=True)
def _restaurer():
    yield
    os.environ.pop('SITE_BASE_URL', None)
    import seo
    importlib.reload(seo)


def _pages():
    for p in sorted(glob.glob(os.path.join(ICI, '*.html'))):
        n = os.path.basename(p)
        yield n, ('/' if n == 'index.html' else '/' + n[:-5]), \
            io.open(p, encoding='utf-8').read()


COORDONNEES = (
    (re.compile(r'<link[^>]*rel="canonical"[^>]*href="([^"]*)"', re.I), 'canonical'),
    (re.compile(r'<meta[^>]*property="og:url"[^>]*content="([^"]*)"', re.I), 'og:url'),
    (re.compile(r'<meta[^>]*property="og:image"[^>]*content="([^"]*)"', re.I), 'og:image'),
    (re.compile(r'<meta[^>]*name="twitter:image"[^>]*content="([^"]*)"', re.I), 'twitter:image'),
)


def _coordonnees_hors_base(seo, route, html):
    """Les adresses absolues servies qui ne sont PAS sur la base courante."""
    sorti = seo.enrichir(route, html)
    fautes = []
    for motif, nom in COORDONNEES:
        for val in motif.findall(sorti):
            if val.startswith('http') and not val.startswith(seo.BASE):
                fautes.append('%s → %s' % (nom, val))
    return fautes


# ── LA PROMESSE, TENUE ────────────────────────────────────────────────────

def test_toutes_les_coordonnees_suivent_ladresse_declaree():
    """LE CONTRÔLE QUI AURAIT VU LE DÉFAUT. Il ne connaît pas les seize pages
    fautives : il relit toutes les pages du dépôt, avec une adresse de base
    volontairement différente de celle écrite en dur."""
    seo = _seo(AUTRE)
    # LA VÉRIFICATION QUI MANQUAIT, ET QUI RENDAIT TOUT LE RESTE CIRCULAIRE.
    # Les contrôles suivants comparent les coordonnées servies à `seo.BASE`.
    # Si `BASE` cessait d'être lue dans l'environnement, elle resterait sur
    # l'ancienne adresse — et les coordonnées, calculées depuis elle, seraient
    # « cohérentes » avec une base fausse. La mutation qui figeait `BASE` a
    # effectivement survécu au premier passage.
    assert seo.BASE == AUTRE, (
        'SITE_BASE_URL n\'est pas lue : BASE vaut %s' % seo.BASE)
    accueil = seo.enrichir('/', io.open(
        os.path.join(ICI, 'index.html'), encoding='utf-8').read())
    assert 'href="%s/"' % AUTRE in accueil, (
        'la canonique de la page d\'accueil ne porte pas la nouvelle adresse')

    fautes = []
    for nom, route, html in _pages():
        for f in _coordonnees_hors_base(seo, route, html):
            fautes.append('%s : %s' % (nom, f))
    assert not fautes, (
        "des coordonnées restent sur une autre adresse que SITE_BASE_URL — "
        "ce sont des canoniques qui pointent vers un site qu'on a quitté :\n   "
        + "\n   ".join(fautes[:12]))


def test_le_controle_sait_reperer_une_canonique_egaree():
    """DISCRIMINATION. Une règle qui déclare « rien à signaler » sans savoir
    reconnaître le défaut ne protège de rien. Le cas éprouvé est le vrai :
    une page qui déclare encore l'ANCIENNE adresse du site."""
    seo = _seo(AUTRE)
    page = ('<html><head><title>Essai</title>'
            '<link rel="canonical" href="%s/x">'
            '</head><body>t</body></html>' % seo.BASE_PAR_DEFAUT)
    brut = [v for m, _ in COORDONNEES for v in m.findall(page)]
    assert brut == [seo.BASE_PAR_DEFAUT + '/x']
    assert not _coordonnees_hors_base(seo, '/x', page)


def test_une_canonique_vers_UN_AUTRE_SITE_nest_pas_touchee():
    """LA LIMITE DE LA RÈGLE, ET ELLE EST VOULUE. Une canonique qui désigne un
    autre site est un choix éditorial — du contenu syndiqué, par exemple. Ce
    module ne défait pas le travail fait à la main : c'est son principe depuis
    le début, et une première version de ce recalage le violait. La recette
    `recette_seo_cta.py` l'a signalé.

    C'est aussi ce qui distingue « notre ancienne adresse », qu'il FAUT
    corriger, de « l'adresse de quelqu'un d'autre », qu'il faut respecter."""
    seo = _seo(AUTRE)
    ailleurs = 'https://un-autre-site.test/article'
    page = ('<html><head><title>T</title>'
            '<link rel="canonical" href="%s">'
            '</head><body>t</body></html>' % ailleurs)
    sorti = seo.enrichir('/x', page)
    # ON ASSERTE CE QU'ON VEUT DIRE, PAS PLUS. Une première version exigeait
    # une page IDENTIQUE — trop fort : cette page n'a pas de balises de
    # partage, et `balises()` a raison de les ajouter. Ce qui doit rester
    # intact, c'est la canonique étrangère.
    assert 'href="%s"' % ailleurs in sorti, 'la canonique étrangère a été réécrite'
    assert sorti.count('rel="canonical"') == 1, 'une seconde canonique a été posée'


def test_sans_variable_denvironnement_rien_ne_bouge():
    """Le comportement par défaut ne change pas : c'est ce qui rend la
    correction sûre à déployer avant même la bascule."""
    seo = _seo(None)
    html = io.open(os.path.join(ICI, 'index.html'), encoding='utf-8').read()
    sorti = seo.enrichir('/', html)
    m = COORDONNEES[0][0].search(sorti)
    assert m and m.group(1) == seo.BASE + '/'
    assert 'conseilprev.onrender.com' in seo.BASE


# ── CE QU'IL NE FAUT SURTOUT PAS ÉCRASER ─────────────────────────────────

def test_le_travail_editorial_nest_pas_touche():
    """Un titre et une description écrits à la main sont un travail
    éditorial. `balises()` a raison de ne combler que les trous : le recalage
    ne porte QUE sur les adresses absolues."""
    seo = _seo(AUTRE)
    page = ('<html><head><title>Un titre soigné, écrit à la main</title>'
            '<meta name="description" content="Une description choisie.">'
            '<link rel="canonical" href="https://ancien-site.test/x">'
            '</head><body>t</body></html>')
    sorti = seo.enrichir('/x', page)
    assert '<title>Un titre soigné, écrit à la main</title>' in sorti
    assert 'Une description choisie.' in sorti
    assert sorti.count('<title>') == 1, 'un second titre a été inséré'


def test_une_page_sans_tete_reste_intacte():
    """Sans `</head>`, coller des balises casserait le rendu — et le recalage
    ne doit pas non plus s'y risquer."""
    seo = _seo(AUTRE)
    fragment = '<div>pas une page</div>'
    assert seo.enrichir('/x', fragment) == fragment


def test_une_page_vide_ne_leve_pas():
    seo = _seo(AUTRE)
    assert seo.enrichir('/x', '') == ''
    assert seo.enrichir('/x', None) is None
