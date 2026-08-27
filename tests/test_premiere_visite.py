"""CE QUE PAIE LE PREMIER VISITEUR APRÈS UN REDÉMARRAGE.

CE QUI A DÉCLENCHÉ CE FICHIER. Un service jugé « trop lent ». Mesuré sur un
processus neuf :

    /                 200 en     52 ms
    /api/news         200 en    482 ms
    /api/veille       200 en  5 085 ms

La page sort en cinquante-deux millisecondes. C'est `/api/veille`, que Sentinel
appelle au chargement, qui coûte cinq secondes — le temps d'agréger les flux
RSS publics.

PREMIER DÉFAUT : UN SEUL DES DEUX CACHES ÉTAIT PRÉCHAUFFÉ. Le fil de démarrage
remplissait `_news_cache`, celui de `/api/news`. `/api/veille` a SON PROPRE
cache, et personne ne le remplissait. Le premier visiteur payait donc la
collecte entière — et sur un service qui s'endort faute de trafic, chaque
visiteur est le premier.

SECOND DÉFAUT, PLUS GRAVE : QUAND AUCUN FLUX NE RÉPOND, CHAQUE REQUÊTE
REPAYAIT. Le cache était bien ÉCRIT sur une collecte vide, mais la condition de
lecture exigeait `items` non vide. Une collecte infructueuse n'était donc
jamais servie : cinq secondes par requête, tant que les flux restaient
injoignables. Avec huit fils par worker, quelques visiteurs simultanés
suffisent à saturer le service — au moment précis où il va déjà mal.

CE QUE CES CONTRÔLES NE PEUVENT PAS FAIRE. Mesurer le gain réel du
préchauffage : les flux RSS ne sont pas joignables depuis l'environnement de
compilation. Ils vérifient le MÉCANISME — que le fil appelle bien la route, et
que le cache est honoré — pas le temps gagné en production.
"""
import io
import os
import re
import sys
import time

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-premiere-visite')

import app as application  # noqa: E402

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()

_IP = [230]


def _get(chemin):
    _IP[0] += 1
    return application.app.test_client().get(
        chemin, headers={'X-Forwarded-For': '198.51.100.%d' % (_IP[0] % 250 + 1)})


@pytest.fixture
def sans_flux(monkeypatch):
    """Aucun flux à interroger : la collecte est vide ET instantanée, ce qui
    rend le contrôle déterministe au lieu de dépendre du réseau."""
    monkeypatch.setattr(application, 'VEILLE_FEEDS', [])
    application._VEILLE_CACHE.update({'ts': 0.0, 'items': [], 'errors': []})
    yield
    application._VEILLE_CACHE.update({'ts': 0.0, 'items': [], 'errors': []})


# ── LE PRÉCHAUFFAGE COUVRE LES DEUX CACHES ───────────────────────────────

def _corps_du_prechauffage():
    """Le corps de `_news_warmup()`, borné par la fin de son indentation.

    IL ÉTAIT BORNÉ PAR SON POINT DE DÉMARRAGE — la ligne
    `threading.Thread(target=_news_warmup…)` qui le suivait immédiatement. Cette
    ligne a dû bouger : sous `--preload`, un fil démarré à l'import démarre dans
    le maître, qui ne sert aucune requête, et aucun worker n'en hérite (voir
    test_fils_du_processus.py). Le déplacer a fait tomber ces trois contrôles
    d'un coup, non parce que le préchauffage avait changé, mais parce qu'ils
    s'ancraient sur son voisinage.

    Une borne prise sur l'INDENTATION ne dépend plus de ce qui suit."""
    i = SOURCE.index('def _news_warmup():')
    lignes = SOURCE[i:].split('\n')
    corps = [lignes[0]]
    for l in lignes[1:]:
        if l and not l[0].isspace():
            break
        corps.append(l)
    return '\n'.join(corps)


def test_le_prechauffage_remplit_aussi_le_cache_de_veille():
    """LE DÉFAUT. Un seul des deux caches était préchauffé, et c'était l'autre
    que la page appelle."""
    corps = _corps_du_prechauffage()
    assert '_news_cache' in corps, "le préchauffage des actualités a disparu"
    assert 'api_veille()' in corps, (
        "le fil de démarrage ne préchauffe pas /api/veille : le premier "
        "visiteur paiera la collecte entière")


def test_le_prechauffage_appelle_la_route_au_lieu_de_la_recopier():
    """La collecte tient une cinquantaine de lignes dans `api_veille`. Les
    dupliquer dans le fil créerait deux chemins qui divergeraient au premier
    ajout de flux, et le cache préchauffé cesserait de ressembler à ce qui est
    servi."""
    corps = _corps_du_prechauffage()
    assert 'test_request_context' in corps
    for signe in ('VEILLE_FEEDS', '_veille_relevant', '_veille_theme'):
        assert signe not in corps, (
            "la collecte de veille est recopiée dans le préchauffage (« %s ») "
            "au lieu d'être appelée" % signe)


def test_un_echec_de_prechauffage_ne_casse_rien():
    """Un préchauffage est un confort, jamais une condition de démarrage."""
    corps = _corps_du_prechauffage()
    i = corps.index('api_veille()')
    assert 'except' in corps[i:], "l'appel de préchauffage n'est pas protégé"


# ── LE CACHE EST HONORÉ, MÊME VIDE ───────────────────────────────────────

def test_une_collecte_vide_nest_pas_refaite_a_chaque_requete(sans_flux):
    """LE SECOND DÉFAUT, ET LE PLUS COÛTEUX. Cinq secondes par requête tant
    que les flux ne répondent pas."""
    r1 = _get('/api/veille').get_json()
    assert r1['count'] == 0 and r1['cached'] is False
    r2 = _get('/api/veille').get_json()
    assert r2['cached'] is True, (
        "une collecte vide est refaite à chaque requête : chaque visiteur "
        "repaie l'agrégation complète des flux")


def test_le_delai_dune_collecte_vide_est_court(sans_flux):
    """Deux minutes, et non trente : une panne de flux est souvent passagère,
    et garder un résultat vide une demi-heure ferait durer la panne bien après
    son rétablissement."""
    assert application.VEILLE_TTL_VIDE < application.VEILLE_TTL / 5
    assert 30 <= application.VEILLE_TTL_VIDE <= 600
    _get('/api/veille')
    # Passé le délai court, la collecte doit être retentée.
    application._VEILLE_CACHE['ts'] = time.time() - application.VEILLE_TTL_VIDE - 1
    assert _get('/api/veille').get_json()['cached'] is False


def test_une_collecte_pleine_garde_le_delai_long(sans_flux):
    """Le délai court ne doit pas s'appliquer à un résultat valide, sans quoi
    on rechargerait les flux toutes les deux minutes pour rien."""
    application._VEILLE_CACHE.update(
        {'ts': time.time() - application.VEILLE_TTL_VIDE - 10,
         'items': [{'title': 'x', 'link': 'y', 'source': 's', 'jur': 'j',
                    'theme': 't', 'date': None, 'summary': ''}],
         'errors': []})
    assert _get('/api/veille').get_json()['cached'] is True


def test_le_rafraichissement_force_reste_possible(sans_flux):
    """`?refresh=1` doit continuer d'ignorer le cache : c'est le seul moyen de
    sortir d'un cache vide avant l'expiration."""
    _get('/api/veille')
    assert _get('/api/veille?refresh=1').get_json()['cached'] is False


# ── CE QUE LA PAGE ELLE-MÊME NE DOIT PAS PAYER ───────────────────────────

def test_la_page_daccueil_ne_depend_daucune_collecte():
    """Le HTML sort en cinquante millisecondes et doit le rester : c'est ce
    que voit le visiteur avant tout le reste."""
    t = time.perf_counter()
    r = _get('/')
    d = (time.perf_counter() - t) * 1000
    assert r.status_code == 200
    assert d < 1500, "la page d'accueil met %.0f ms : elle attend quelque chose" % d


def test_la_sonde_de_vie_ninterroge_aucun_flux():
    """Render l'appelle toutes les quelques secondes. Si elle déclenchait une
    collecte, le service passerait sa vie à agréger des flux."""
    t = time.perf_counter()
    r = _get('/health')
    assert r.status_code == 200
    assert (time.perf_counter() - t) * 1000 < 200
