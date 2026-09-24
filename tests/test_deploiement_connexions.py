# -*- coding: utf-8 -*-
"""CE QUI BRANCHE LE SITE : déclaré au déploiement, et des tâches planifiées
qui aboutissent.

TROIS DÉFAUTS MESURÉS SUR LE CODE DE BASE (29e13da), le 24 septembre 2026 :

  1. `/api/cron/essai-relances` et `/api/cron/rgpd-purge` répondaient 500 avec
     le BON secret : `hmac.compare_digest` là où le module n'est importé que
     sous le nom `_hmac` (NameError). Un mauvais secret était refusé (403),
     donc rien ne se voyait du dehors ; seule la tâche légitime échouait. La
     purge RGPD automatique ne tournait jamais, les relances d'essai ne
     partaient qu'au fil des visites. Le secret était aussi accepté dans
     l'adresse (`?secret=`), donc dans les journaux d'accès.

  2. `render.yaml` ne déclarait AUCUNE des variables qui branchent Stripe,
     Brevo et le courrier. Un service recréé depuis ce fichier démarrait sans
     caisse, sans courrier, et personne n'était prévenu.

  3. `robots.txt` et `llms.txt` désignaient `conseilprev.onrender.com` en dur,
     alors que la canonique et le plan du site suivent déjà `SITE_BASE_URL`
     (mesuré : `Sitemap: https://conseilprev.onrender.com/sitemap.xml` servi
     par le service conseilprevia).

Ces règles mesurent les trois : elles sont rouges sur 29e13da.
"""
import importlib
import io
import os
import sys

import pytest
import yaml

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import app as A          # noqa: E402
import seo               # noqa: E402

NAVIGATEUR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0',
              'Accept': 'text/plain,*/*'}
SECRET = 'secret-de-recette-0123456789abcdef'
CRON = ('/api/cron/essai-relances', '/api/cron/rgpd-purge')
AUTRE = 'https://exemple-nouveau-domaine.test'

# CE QUE LE DÉPLOIEMENT DOIT DÉCLARER. La liste est ici, pas dérivée du code :
# c'est le CONTRAT entre le dépôt et le tableau de bord Render. Une variable
# nouvelle qui branche un service extérieur s'ajoute aux deux endroits.
VARIABLES = (
    'STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET', 'STRIPE_PRICE_PRO',
    'STRIPE_PRICE_ENTREPRISE', 'STRIPE_TAX_RATE_ID',
    'BREVO_API_KEY', 'BREVO_WEBHOOK_TOKEN', 'MAIL_FROM', 'MAIL_TO', 'MAIL_CC',
    'CONSEILPREV_NOTIFY_EMAIL', 'SITE_BASE_URL', 'CRON_SECRET',
)


def _variables_declarees():
    doc = yaml.safe_load(io.open(os.path.join(ICI, 'render.yaml'),
                                 encoding='utf-8').read())
    declarees = {}
    for service in doc.get('services') or []:
        for e in service.get('envVars') or []:
            if isinstance(e, dict) and 'key' in e:
                declarees[e['key']] = e
    return declarees


# ── 1. LE DÉPLOIEMENT DÉCLARE CE QUI BRANCHE LE SITE ────────────────────────

@pytest.mark.parametrize('variable', VARIABLES)
def test_le_deploiement_declare_la_variable_sans_en_ecrire_la_valeur(variable):
    """Chaque variable de connexion est déclarée dans render.yaml, en
    `sync: false` : Render la demande à la création, le dépôt n'en porte
    jamais la valeur."""
    declarees = _variables_declarees()
    assert variable in declarees, (
        'render.yaml ne déclare pas %s : un service recréé depuis ce fichier '
        'partirait sans elle, et rien ne le dirait' % variable)
    assert declarees[variable].get('sync') is False, (
        '%s doit être déclarée « sync: false » (valeur posée dans le tableau '
        'de bord), pas %r' % (variable, declarees[variable]))


def test_aucune_valeur_de_connexion_n_est_ecrite_dans_le_depot():
    """Une clé ou une adresse écrite dans render.yaml serait publiée avec le
    dépôt. Les variables de connexion n'ont ni `value` ni `generateValue`."""
    fautes = [v for v, e in _variables_declarees().items()
              if v in VARIABLES and ('value' in e or 'generateValue' in e)]
    assert not fautes, 'valeur écrite dans render.yaml pour : %s' % fautes


# ── 2. LES TÂCHES PLANIFIÉES ABOUTISSENT ────────────────────────────────────

@pytest.fixture
def taches_doublees(monkeypatch):
    """Les deux travaux sont remplacés par un compteur : la règle mesure la
    GARDE de la route, pas les relances ni la purge."""
    appels = []
    monkeypatch.setattr(A, '_essai_relances', lambda: appels.append('essai'))
    monkeypatch.setattr(A, 'rgpd_purge_run',
                        lambda simulation=False: appels.append('purge') or {})
    monkeypatch.setenv('CRON_SECRET', SECRET)
    return appels


@pytest.mark.parametrize('route', CRON)
def test_la_tache_planifiee_aboutit_avec_le_bon_secret(route, taches_doublees):
    """LE DÉFAUT MESURÉ : 500 NameError avec le bon secret."""
    r = A.app.test_client().post(route, headers={'X-Cron-Secret': SECRET})
    assert r.status_code == 200, (
        'avec le bon secret, %s répond %s : %s' % (route, r.status_code,
                                                    r.get_data(as_text=True)[:200]))
    assert r.get_json().get('ok') is True
    assert taches_doublees == ['essai' if 'essai' in route else 'purge'], (
        'le travail attendu n\'a pas été lancé : %r' % taches_doublees)


@pytest.mark.parametrize('route', CRON)
def test_un_mauvais_secret_est_refuse_sans_rien_lancer(route, taches_doublees):
    r = A.app.test_client().post(route, headers={'X-Cron-Secret': SECRET + 'x'})
    assert r.status_code == 403, r.status_code
    assert taches_doublees == [], 'un travail a été lancé malgré le refus'


@pytest.mark.parametrize('route', CRON)
def test_le_secret_dans_l_adresse_est_refuse(route, taches_doublees):
    """Un secret passé en `?secret=` finit dans les journaux d'accès du
    mandataire : seul l'en-tête vaut."""
    r = A.app.test_client().post(route + '?secret=' + SECRET)
    assert r.status_code == 403, (
        'le secret passé dans l\'adresse est accepté (%s)' % r.status_code)
    assert taches_doublees == []


@pytest.mark.parametrize('route', CRON)
def test_la_tache_planifiee_ne_repond_pas_en_GET(route, taches_doublees):
    """Un GET se déclenche depuis une barre d'adresse ou un robot ; une tâche
    planifiée se déclenche en POST."""
    r = A.app.test_client().get(route, headers={'X-Cron-Secret': SECRET})
    # 405 pour Flask ; le site rend 404 sur une methode absente, pour ne pas
    # dessiner la carte de ses routes. L'un ou l'autre : jamais 200.
    assert r.status_code in (404, 405), r.status_code
    assert taches_doublees == []


def test_sans_secret_configure_la_tache_est_desactivee(monkeypatch):
    monkeypatch.delenv('CRON_SECRET', raising=False)
    r = A.app.test_client().post(CRON[0], headers={'X-Cron-Secret': 'x'})
    assert r.status_code == 501, r.status_code


# ── 3. ROBOTS.TXT ET LLMS.TXT SUIVENT L'ADRESSE DU SITE ─────────────────────

@pytest.fixture
def adresse_autre():
    """`seo.BASE` est lue à l'import : on recharge le module avec une autre
    adresse, puis on le remet comme il était — `app.seo` est le MÊME objet
    module, donc la route voit la nouvelle valeur."""
    ancien = os.environ.get('SITE_BASE_URL')
    os.environ['SITE_BASE_URL'] = AUTRE
    importlib.reload(seo)
    try:
        yield
    finally:
        if ancien is None:
            os.environ.pop('SITE_BASE_URL', None)
        else:
            os.environ['SITE_BASE_URL'] = ancien
        importlib.reload(seo)


@pytest.mark.parametrize('route', ('/robots.txt', '/llms.txt'))
def test_le_fichier_suit_l_adresse_du_site(route, adresse_autre):
    """LE DÉFAUT MESURÉ : l'ancien hôte écrit en dur, servi par le nouveau
    service."""
    assert seo.BASE == AUTRE, seo.BASE
    r = A.app.test_client().get(route, headers=NAVIGATEUR)
    assert r.status_code == 200, r.status_code
    corps = r.get_data(as_text=True)
    assert AUTRE in corps, '%s ne porte pas SITE_BASE_URL' % route
    assert 'conseilprev.onrender.com' not in corps, (
        '%s désigne encore l\'ancien service : %s'
        % (route, [l for l in corps.splitlines() if 'onrender' in l][:3]))


def test_llms_txt_se_lit_sans_ressembler_a_un_navigateur():
    """`llms.txt` est écrit POUR des assistants, qui le lisent sans
    Accept-Language ni Accept-Encoding. L'heuristique « vrai navigateur » du
    middleware exemptait robots.txt et le plan du site, pas lui : 404 mesuré
    pour un lecteur qui n'envoie que son User-Agent."""
    r = A.app.test_client().get('/llms.txt', headers={
        'User-Agent': 'Mozilla/5.0 (compatible; LecteurAssistant/1.0)'})
    assert r.status_code == 200, (
        'llms.txt répond %s à un lecteur sans en-têtes de navigateur'
        % r.status_code)
    assert r.get_data(as_text=True).startswith('# ConseilPrev')
