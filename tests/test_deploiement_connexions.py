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
import logging
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


# ── 2 bis. LA TÂCHE EST LANCÉE PAR UNE COMMANDE, PAS PAR UN NAVIGATEUR ──────
#
# LE DÉFAUT MESURÉ, et pourquoi la recette ne le voyait pas. Un Render Cron
# Job exécute une commande : `curl`, `wget` ou `python-requests`, tous trois
# dans BLOCKED_BOTS. Le middleware répondait donc 404 AVANT la garde du
# secret : la purge RGPD automatique et les relances d'essai n'ont jamais
# tourné, et le 404 faisait croire à une route absente. Le client de test
# Flask, lui, envoie « Werkzeug/… », que rien ne bloque — c'est exactement ce
# que ces règles corrigent : elles envoient l'agent du VRAI appelant.

AGENTS_DE_TACHE = ('curl/8.5.0', 'Wget/1.21', 'python-requests/2.32.3',
                   'Render-Cron/1.0 (curl)')


@pytest.mark.parametrize('route', CRON)
@pytest.mark.parametrize('agent', AGENTS_DE_TACHE)
def test_la_tache_aboutit_quel_que_soit_l_agent_de_la_commande(route, agent, taches_doublees):
    r = A.app.test_client().post(route, headers={'X-Cron-Secret': SECRET,
                                                 'User-Agent': agent})
    assert r.status_code == 200, (
        '%s avec l\'agent %r répond %s' % (route, agent, r.status_code))
    assert taches_doublees == ['essai' if 'essai' in route else 'purge'], taches_doublees


@pytest.mark.parametrize('agent', AGENTS_DE_TACHE)
@pytest.mark.parametrize('chemin', ['/api/registre', '/api/tarifs',
                                    '/api/formation/creneaux'])
def test_l_exemption_ne_vaut_que_pour_les_chemins_de_tache(agent, chemin, caplog):
    """ET EUX SEULS. Exempter tout /api/ du filtre d'agent ouvrirait le site
    aux moissonneurs ; l'exemption s'arrête à /api/cron/ et aux deux points de
    réception signés.

    C'EST LE JOURNAL QU'ON LIT, pas le statut : un chemin exempté peut rendre
    404 pour une tout autre raison (méthode absente, route inconnue), et la
    règle passerait alors sur un code qui n'arrête plus rien."""
    with caplog.at_level(logging.WARNING, logger='conseilprev'):
        r = A.app.test_client().get(chemin, headers={'User-Agent': agent})
    assert 'BOT_BLOCKED' in caplog.text, (
        '%s sert %r sans passer par le filtre d\'agent (%s)' % (chemin, agent, r.status_code))
    assert r.status_code == 404, (chemin, agent, r.status_code)


@pytest.mark.parametrize('route', CRON)
def test_l_exemption_ne_vaut_pas_en_GET(route, taches_doublees, caplog):
    """L'exemption est bornée au POST : un GET depuis une barre d'adresse ou
    un robot ne gagne pas le droit de passer le filtre d'agent.

    LE STATUT NE SUFFIT PAS À LE MESURER — un GET reçoit 404 des deux côtés,
    puisque la route n'accepte que POST. C'est le JOURNAL qui distingue : le
    filtre d'agent écrit « BOT_BLOCKED » avant d'abandonner, l'exemption non.
    Sans cette lecture, la règle passerait sur un code qui exempte tout."""
    with caplog.at_level(logging.WARNING, logger='conseilprev'):
        r = A.app.test_client().get(route, headers={'X-Cron-Secret': SECRET,
                                                    'User-Agent': 'curl/8.5.0'})
    assert r.status_code in (404, 405), r.status_code
    assert taches_doublees == []
    assert 'BOT_BLOCKED' in caplog.text, (
        'un GET a franchi le filtre d\'agent : %s' % caplog.text)


@pytest.mark.parametrize('route', CRON)
def test_l_exemption_vaut_bien_en_POST(route, taches_doublees, caplog):
    """L'autre moitié de la mesure précédente, sur le même journal."""
    with caplog.at_level(logging.WARNING, logger='conseilprev'):
        A.app.test_client().post(route, headers={'X-Cron-Secret': SECRET,
                                                 'User-Agent': 'curl/8.5.0'})
    assert 'BOT_BLOCKED' not in caplog.text, caplog.text


@pytest.mark.parametrize('route', CRON)
def test_le_secret_reste_exige_malgre_l_exemption(route, taches_doublees):
    """CE QUE L'EXEMPTION N'EXEMPTE PAS. On échange un refus fondé sur
    l'apparence contre un refus fondé sur une preuve — pas contre rien."""
    r = A.app.test_client().post(route, headers={'X-Cron-Secret': SECRET + 'x',
                                                 'User-Agent': 'curl/8.5.0'})
    assert r.status_code == 403, r.status_code
    assert taches_doublees == []


# ── 2 ter. L'ADRESSE DU CLIENT VIENT DU MANDATAIRE, PAS DU CLIENT ──────────
#
# LE DÉFAUT MESURÉ. `RateLimiter.get_ip` lisait le PREMIER élément de
# X-Forwarded-For, que le client écrit lui-même. Un anonyme envoyait donc
# « X-Forwarded-For: 3.18.12.63 » (une adresse publique des livraisons
# Stripe) sur un chemin piège : le honeypot bloquait cette adresse une heure,
# et la notification Stripe suivante recevait 429 avant d'atteindre la route.
# Le même en-tête, changé à chaque appel, annulait toutes les bornes par
# adresse.

ADRESSE_STRIPE = '3.18.12.63'
ADRESSE_RENDER = '198.51.100.77'


@pytest.mark.parametrize('xff, attendu', [
    ('%s, %s' % (ADRESSE_STRIPE, ADRESSE_RENDER), ADRESSE_RENDER),
    ('  a, b ,  %s  ' % ADRESSE_RENDER, ADRESSE_RENDER),
    (ADRESSE_RENDER, ADRESSE_RENDER),
    ('', '10.0.0.1'),
], ids=['usurpee-puis-reelle', 'espaces-et-trois-sauts', 'un-seul-saut', 'sans-en-tete'])
def test_l_adresse_lue_est_le_dernier_saut_ajoute(xff, attendu):
    class _Requete(object):
        headers = {'X-Forwarded-For': xff}
        remote_addr = '10.0.0.1'
    assert A.limiter.get_ip(_Requete()) == attendu, xff


def test_un_anonyme_ne_fait_plus_bloquer_l_adresse_d_un_service():
    """Le piège honeypot bloque bien — mais l'adresse du VRAI appelant, pas
    celle qu'il a écrite dans l'en-tête."""
    c = A.app.test_client()
    xff = '%s, %s' % (ADRESSE_STRIPE, ADRESSE_RENDER)
    c.get('/wp-admin', headers={'X-Forwarded-For': xff,
                                'User-Agent': NAVIGATEUR['User-Agent'],
                                'Accept-Language': 'fr-FR'})
    assert not A.limiter.is_blocked(ADRESSE_STRIPE), (
        'l\'adresse usurpée a été bloquée : un anonyme coupe les livraisons')
    assert A.limiter.is_blocked(ADRESSE_RENDER), (
        'le piège ne bloque plus rien du tout')


@pytest.mark.parametrize('chemin, entetes', [
    ('/api/stripe/webhook', {'User-Agent': 'Stripe/1.0'}),
    ('/api/brevo/webhook', {'User-Agent': 'Brevo'}),
])
def test_un_point_de_reception_n_est_jamais_refuse_sur_le_blocage(chemin, entetes):
    """DEUX PORTES FERMAIENT LE SITE À UNE ADRESSE BLOQUÉE : `is_blocked` dans
    le middleware, et la limite globale qui commence par le même test.
    N'en rouvrir qu'une ne rétablissait rien — mesuré : 429 malgré tout."""
    A.limiter.block('192.0.2.50', 3600, 'recette')
    h = dict(entetes); h['X-Forwarded-For'] = '192.0.2.50'
    r = A.app.test_client().post(chemin, data=b'[]', content_type='application/json',
                                 headers=h)
    assert r.status_code != 429, (
        '%s refusé 429 : plus aucune confirmation ni désinscription' % chemin)


@pytest.mark.parametrize('chemin', ['/api/stripe/webhook', '/api/brevo/webhook'])
def test_un_point_de_reception_ne_tombe_pas_sur_le_filtre_d_agent(chemin):
    r = A.app.test_client().post(chemin, data=b'[]', content_type='application/json',
                                 headers={'User-Agent': 'python-requests/2.32.3'})
    assert r.status_code != 404, '%s bloqué sur son agent' % chemin


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
