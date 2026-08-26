"""LA POLITIQUE DE CACHE DES PAGES — ce que « no-store » coûtait vraiment.

LA FAUTE, ET SON ÉTENDUE. Vingt-quatre routes sont servies par
`_serve_page_fast`, qui garde les pages en mémoire, pré-compressées, avec une
étiquette ETag forte. Trois seulement — celles embarquées en iframe dans
Sentinel — recevaient une politique de cache. Les vingt et une autres n'en
avaient AUCUNE et retombaient sur le défaut posé par `add_security_headers` :
« no-store ».

CE QUE « NO-STORE » INTERDIT. Pas seulement de servir depuis le cache : de
GARDER la réponse. Le navigateur ne peut donc même pas présenter d'étiquette
au retour, et retélécharge la page ENTIÈRE à chaque visite. Vingt-quatre
pages, 1,8 Mo en clair, 429 Ko compressés, repayés à chaque clic dans le menu.
L'ETag était calculé, servi… et inutilisable.

POURQUOI LA CORRECTION EST SANS RISQUE, et le code le disait déjà : ces pages
sortent d'un cache mémoire PARTAGÉ, les mêmes octets pour tout le monde. Elles
ne peuvent pas contenir de donnée personnelle — la personnalisation passe par
les API. Une page qui varierait selon le visiteur serait déjà cassée par ce
cache, indépendamment de cette politique.

CE QUE LA POLITIQUE GARDE. « no-cache, must-revalidate » n'autorise jamais à
servir sans demander : le navigateur revalide à chaque visite, donc une mise
en ligne est prise en compte immédiatement. Ce qu'on économise n'est pas
l'aller-retour, c'est le CORPS. Et « private » interdit à un cache
intermédiaire de garder une page d'abonné pour le visiteur suivant.
"""
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-cache')

import app as application  # noqa: E402

SOURCE = open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()

# Chaque page est sondée depuis une adresse distincte : le limiteur de débit
# compte 60 requêtes par minute et par IP sur ces routes, et un 429 se lirait
# comme une politique de cache absente.
_IP = [150]


def _get(chemin, **entetes):
    _IP[0] += 1
    h = {'X-Forwarded-For': '198.51.100.%d' % (_IP[0] % 250 + 1),
         'Accept-Encoding': 'gzip',
         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    h.update(entetes)
    return application.app.test_client().get(chemin, headers=h)


def _routes_rapides():
    """Les routes réellement servies par le cache rapide — relues de `PAGES`,
    jamais recopiées ici. Une liste tenue à part dériverait du dépôt."""
    return sorted(application.PAGES.keys())


# ── LE DÉFAUT LUI-MÊME ────────────────────────────────────────────────────

def test_aucune_page_du_cache_rapide_nest_en_no_store():
    """LE CONTRÔLE QUI AURAIT VU LE DÉFAUT. « no-store » rend l'ETag
    inutilisable : la page repart en entier à chaque visite."""
    fautes = []
    for r in _routes_rapides():
        rep = _get(r)
        if rep.status_code != 200:
            continue
        cc = (rep.headers.get('Cache-Control') or '').lower()
        if 'no-store' in cc:
            fautes.append('%s → %s' % (r, cc))
    assert not fautes, (
        'pages servies en no-store, donc retéléchargées en entier à chaque '
        'visite :\n   ' + '\n   '.join(fautes))


def test_chaque_page_porte_une_etiquette_forte():
    """Sans ETag, aucune revalidation n'est possible : le navigateur ne peut
    rien proposer au retour."""
    sans = []
    for r in _routes_rapides():
        rep = _get(r)
        if rep.status_code == 200 and not rep.headers.get('ETag'):
            sans.append(r)
    assert not sans, 'pages sans ETag : %s' % sans


def test_la_revisite_ne_repaie_pas_le_corps():
    """La mesure qui compte : une seconde visite doit coûter un 304 sans un
    seul octet de corps."""
    testees = 0
    for r in _routes_rapides():
        rep = _get(r)
        etag = rep.headers.get('ETag')
        if rep.status_code != 200 or not etag:
            continue
        rev = _get(r, **{'If-None-Match': etag})
        assert rev.status_code == 304, '%s revalide en %s' % (r, rev.status_code)
        assert rev.data == b'', '%s renvoie un corps en 304' % r
        testees += 1
    assert testees >= 10, (
        'seules %d pages ont pu être éprouvées : le contrôle ne mesure '
        'presque rien' % testees)


def test_les_pages_restent_privees():
    """« private » n'est pas décoratif : un cache intermédiaire qui garderait
    une page d'abonné la rendrait lisible au visiteur suivant."""
    fautes = []
    for r in _routes_rapides():
        rep = _get(r)
        if rep.status_code != 200:
            continue
        cc = (rep.headers.get('Cache-Control') or '').lower()
        if 'private' not in cc:
            fautes.append('%s → %s' % (r, cc))
    assert not fautes, 'pages sans « private » : %s' % fautes


def test_la_revalidation_reste_obligatoire():
    """On économise le corps, PAS l'aller-retour. Une politique qui
    autoriserait à servir sans demander (« max-age » sans « no-cache »)
    laisserait une mise en ligne invisible pendant la durée du cache."""
    for r in _routes_rapides()[:6]:
        rep = _get(r)
        if rep.status_code != 200:
            continue
        cc = (rep.headers.get('Cache-Control') or '').lower()
        assert 'no-cache' in cc or 'max-age=0' in cc, '%s → %s' % (r, cc)


# ── LA POLITIQUE EST DÉCLARÉE UNE SEULE FOIS ──────────────────────────────

def test_la_politique_nest_ecrite_quune_fois():
    """Elle l'était à trois endroits, dont deux qui n'en donnaient à personne.
    Trois copies, trois occasions de diverger."""
    assert "_CACHE_PAGES = 'private, no-cache, must-revalidate'" in SOURCE
    copies = re.findall(r"cache_control\s*=\s*'[^']+'", SOURCE)
    assert not copies, (
        'politique de cache écrite à la main au lieu de la constante : %s'
        % copies)


def test_le_marqueur_de_politique_dediee_est_bien_retire():
    """`_serve_page_fast` pose `X-Perf-Cache` pour dire à
    `add_security_headers` de ne pas écraser sa politique. Ce marqueur est
    interne : le laisser fuiter vers le visiteur exposerait un détail
    d'implémentation, et surtout signalerait que la page vient d'un cache."""
    for r in _routes_rapides()[:6]:
        rep = _get(r)
        assert not rep.headers.get('X-Perf-Cache'), r
