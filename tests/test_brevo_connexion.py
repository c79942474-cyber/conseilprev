# -*- coding: utf-8 -*-
"""La connexion Brevo : des envois qui arrivent, qui ne coûtent pas le quota,
et qui n'exposent rien.

TOUT EST MESURÉ SANS RÉSEAU. La fixture `faux_brevo` (tests/conftest.py) fait
parler le VRAI `requests` de l'application à un vrai serveur HTTP local qui
note chaque requête — chemin, en-têtes, corps JSON — et `reseau_ferme` refuse
toute autre connexion : une règle qui viserait api.brevo.com tombe au lieu de
partir. Aucun serveur app.py n'est lancé : le client de test Flask suffit.

CE QUE CE FICHIER TIENT, ET LE DÉFAUT MESURÉ QUI L'A FAIT ÉCRIRE (relevé sur
le commit de base, compte Brevo gratuit à 300 envois par jour) :

  · deux routes de diagnostic anonymes envoyaient deux courriels par visite
    et affichaient un fragment de la clé : 160 GET → 240 envois, le quota du
    jour en une minute ;
  · /api/health faisait un appel Brevo et un appel Anthropic par visite
    anonyme et affichait le compte ;
  · /api/notify-selection était un relais ouvert vers n'importe quelle
    adresse, sans échappement : un courriel signé CONSEILPREV portant le lien
    d'un inconnu ;
  · le courriel de repli (jeton de réinitialisation compris) était écrit dans
    uploads_cv/, servi publiquement sous un nom prévisible ;
  · un 429 passager perdait définitivement un courriel ; dix envois ouvraient
    dix connexions TLS ;
  · le webhook acceptait tout POST, et une désinscription reçue ne changeait
    rien ;
  · la garde MAIL_FROM ne voyait pas la valeur par défaut, non vérifiable ;
  · six envois internes visaient une adresse qui n'existe pas (rebond
    garanti, crédit consommé) ;
  · email_log gardait les adresses sans fin ; un anonyme sur /me déclenchait
    les relances.
"""
import io
import logging
import os
import re
import secrets
import socket
import stat
import sys
import threading
from datetime import datetime, timedelta

import pytest
import requests

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)
os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-brevo-connexion')
os.environ.setdefault('ADMIN_PASSWORD', 'mot-de-passe-de-recette-uniquement')

import app as A  # noqa: E402
import formations_ia  # noqa: E402

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
PIEGE = '<a href="https://piege.test/z">Cliquez pour valider</a>'
SMTP_EMAIL = '/v3/smtp/email'


def _entetes(**extra):
    """Des en-têtes de navigateur crédibles : sans Accept-Language, le
    security_middleware écarte la requête avant la vue."""
    h = {'X-Forwarded-For': '203.0.113.9',
         'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'),
         'Accept-Language': 'fr-FR,fr;q=0.9', 'Accept': 'application/json'}
    h.update(extra)
    return h


def _anonyme():
    return A.app.test_client()


def _admin():
    c = A.app.test_client()
    with c.session_transaction() as s:
        s['is_conseilprev'] = True
    return c


def _posts(fb):
    return fb.recues('POST', SMTP_EMAIL, exact=True)


def _destinataires(fb):
    return [x.json['to'][0]['email'] for x in _posts(fb)]


def _sql(requete, params=()):
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute(requete, params)
    lignes = [dict(r) for r in cur.fetchall()] if cur.description else []
    conn.commit(); conn.close()
    return lignes


def _nettoyer():
    """Les traces de recette en base : email_log, suppression, consentements,
    rapports en attente. Chaque table peut manquer sur un code plus ancien."""
    for requete in ("DELETE FROM email_log WHERE destinataire LIKE '%@exemple.test'",
                    # Les sélections comptent pour le plafond global du jour : une
                    # ligne laissée par un essai (ou par une mutation jouée) fausserait
                    # la mesure suivante.
                    "DELETE FROM email_log WHERE sujet LIKE '[CONSEILPREV] Votre s%lection%'",
                    "DELETE FROM email_suppression WHERE email LIKE '%@exemple.test'",
                    "DELETE FROM consent_records WHERE email LIKE '%@exemple.test'",
                    # Les réservations de formation du jour comptent pour les
                    # bornes de /api/formation/inscription : une ligne laissée
                    # fausserait la mesure suivante.
                    "DELETE FROM formation_ia_resa WHERE email LIKE '%@exemple.test'",
                    "DELETE FROM pending_reports WHERE client_id >= 999000"):
        try:
            _sql(requete)
        except Exception:
            pass


@pytest.fixture
def brevo(faux_brevo, monkeypatch, tmp_path):
    """`faux_brevo`, plus : la base d'URL redirigée (contacts, compte), les
    dossiers d'écriture isolés, et l'attente entre deux tentatives ENREGISTRÉE
    au lieu d'être subie (`faux_brevo.pauses`). `raising=False` : sur un code
    qui n'a pas encore ces attributs, la règle doit tomber sur SON assertion,
    pas sur la fixture."""
    _nettoyer()
    pauses = []
    (tmp_path / 'uploads').mkdir()          # existe, comme le vrai uploads_cv/
    monkeypatch.setattr(A, 'BREVO_API_BASE', faux_brevo.url, raising=False)
    monkeypatch.setattr(A, 'REPLI_COURRIELS_DOSSIER', str(tmp_path / 'repli'), raising=False)
    monkeypatch.setattr(A, 'UPLOAD_FOLDER', str(tmp_path / 'uploads'))
    monkeypatch.setattr(A, '_brevo_pause', lambda s: pauses.append(s), raising=False)
    faux_brevo.pauses = pauses
    yield faux_brevo
    _nettoyer()


# ══════════════════════════════════════════════════════════════════════════
#  1. LE CONTRAT HTTP (vert sur le code de base)
# ══════════════════════════════════════════════════════════════════════════

def test_un_envoi_fait_un_seul_POST_selon_le_contrat_brevo(brevo):
    ok, via = A.send_email_smart('client@exemple.test', 'Client Essai', 'Sujet — é',
                                 '<p>Corps</p>', reply_to='rep@exemple.test', tags=['t'])
    assert (ok, via) == (True, 'brevo_api'), (ok, via)
    envois = _posts(brevo)
    assert len(envois) == 1, 'observé %d POST %s' % (len(envois), SMTP_EMAIL)
    r = envois[0]
    assert r.entetes['api-key'] == 'xkeysib-recette-locale', r.entetes
    assert r.entetes['content-type'] == 'application/json', r.entetes
    assert r.entetes['accept'] == 'application/json', r.entetes
    assert r.json == {'sender': {'name': 'CONSEILPREV', 'email': A.MAIL_FROM},
                      'to': [{'email': 'client@exemple.test', 'name': 'Client Essai'}],
                      'subject': 'Sujet — é', 'htmlContent': '<p>Corps</p>',
                      'replyTo': {'email': 'rep@exemple.test'}, 'tags': ['t']}, r.json
    lignes = _sql("SELECT methode, succes FROM email_log WHERE destinataire='client@exemple.test'")
    assert [(l['methode'], l['succes']) for l in lignes] == [('brevo_api', 1)], lignes


def test_brevo_401_donne_saved_locally_sans_reessai_et_une_ligne_email_log(brevo):
    brevo.pannes['POST ' + SMTP_EMAIL] = (401, {'code': 'unauthorized'})
    assert A.send_email_smart('x@exemple.test', 'X', 'S', '<p/>') == (False, 'saved_locally')
    assert len(_posts(brevo)) == 1, 'un 401 a été rejoué %d fois' % len(_posts(brevo))
    lignes = _sql("SELECT methode, succes FROM email_log WHERE destinataire='x@exemple.test' "
                  "ORDER BY id DESC LIMIT 1")
    assert [(l['methode'], l['succes']) for l in lignes] == [('saved_locally', 0)], lignes


@pytest.mark.parametrize('port,classe', [(2525, 'SMTP'), (465, 'SMTP_SSL')])
def test_le_repli_smtp_suit_le_protocole(brevo, monkeypatch, port, classe):
    brevo.pannes['POST ' + SMTP_EMAIL] = (500, {'code': 'internal_error'})
    journal = []

    class _Smtp(object):
        def __init__(self, hote, port_, **kw):
            journal.append(('ouvre', type(self).__name__, hote, port_))
        def __enter__(self): return self
        def __exit__(self, *a): journal.append(('ferme',))
        def ehlo(self): journal.append(('ehlo',))
        def starttls(self, context=None): journal.append(('starttls',))
        def login(self, u, p): journal.append(('login', u))
        def sendmail(self, de, a, msg): journal.append(('sendmail', de, a))

    monkeypatch.setattr(A.smtplib, 'SMTP', type('SMTP', (_Smtp,), {}))
    monkeypatch.setattr(A.smtplib, 'SMTP_SSL', type('SMTP_SSL', (_Smtp,), {}))
    monkeypatch.setattr(A, 'SMTP_USER', 'relais@exemple.test')
    monkeypatch.setattr(A, 'SMTP_PASSWORD', 'cle-smtp')
    monkeypatch.setattr(A, 'SMTP_PORT', port)
    assert A.send_email_smart('d@exemple.test', 'D', 'S', '<p/>') == (True, 'brevo_smtp')
    attendu = [('ouvre', classe, A.SMTP_HOST, port), ('ehlo',)]
    attendu += [('starttls',)] if port != 465 else []
    attendu += [('login', 'relais@exemple.test'),
                ('sendmail', A.MAIL_FROM, ['d@exemple.test']), ('ferme',)]
    assert journal == attendu, journal


def test_le_repli_smtp_ne_journalise_pas_l_adresse_en_clair(brevo, monkeypatch, caplog):
    """Le chemin API masque déjà l'adresse ; le chemin SMTP l'écrivait en
    clair. Les journaux Render sont conservés et lus par des outils : une
    adresse de plus y est une donnée personnelle de plus, pour rien."""
    brevo.pannes['POST ' + SMTP_EMAIL] = (500, {'code': 'internal_error'})

    class _Smtp(object):
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def ehlo(self): pass
        def starttls(self, context=None): pass
        def login(self, u, p): pass
        def sendmail(self, de, a, msg): pass

    monkeypatch.setattr(A.smtplib, 'SMTP', _Smtp)
    monkeypatch.setattr(A, 'SMTP_USER', 'relais@exemple.test')
    monkeypatch.setattr(A, 'SMTP_PASSWORD', 'cle-smtp')
    monkeypatch.setattr(A, 'SMTP_PORT', 2525)
    with caplog.at_level(logging.INFO, logger='conseilprev'):
        assert A.send_email_smart('journal@exemple.test', 'J', 'S', '<p/>') == (True, 'brevo_smtp')
    assert 'BREVO_SMTP_OK' in caplog.text, caplog.text
    assert 'journal@exemple.test' not in caplog.text, 'adresse en clair dans le journal'
    assert 'j***@exemple.test' in caplog.text, caplog.text


# ══════════════════════════════════════════════════════════════════════════
#  2. LES ROUTES DE DIAGNOSTIC (G1 / E3 / M1)
# ══════════════════════════════════════════════════════════════════════════

def test_le_diagnostic_brevo_cv_est_refuse_a_l_anonyme_sans_aucun_envoi(brevo):
    r = _anonyme().get('/api/test-brevo-cv', headers=_entetes())
    assert r.status_code == 403, 'un anonyme obtient %d' % r.status_code
    assert _posts(brevo) == [], '%d courriel(s) partis pour un anonyme' % len(_posts(brevo))


def test_le_diagnostic_brevo_cv_ne_livre_aucun_fragment_de_cle_a_l_administrateur(brevo):
    r = _admin().get('/api/test-brevo-cv', headers=_entetes())
    assert r.status_code == 200, r.status_code
    j = r.get_json() or {}
    corps = r.get_data(as_text=True)
    assert 'brevo_api_key_start' not in j and 'brevo_api_key_len' not in j, sorted(j)
    assert 'xkeysib' not in corps, 'le préfixe de la clé est dans la réponse'
    assert len(_posts(brevo)) == 2, 'le diagnostic admin doit faire ses 2 envois de test'


def test_le_diagnostic_email_est_refuse_a_l_anonyme_sans_livrer_la_configuration(brevo):
    r = _anonyme().get('/api/test-email', headers=_entetes())
    corps = r.get_data(as_text=True)
    assert r.status_code == 403, 'un anonyme obtient %d' % r.status_code
    for donnee in (A.MAIL_TO, A.SMTP_HOST, A.UPLOAD_FOLDER, A.CONSEILPREV_NOTIFY_EMAIL):
        assert donnee not in corps, 'la réponse anonyme contient %r' % donnee


def test_api_health_anonyme_repond_court_sans_appel_sortant_ni_donnee_du_compte(brevo, monkeypatch):
    monkeypatch.setattr(A, 'ANTHROPIC_API_KEY', 'sk-ant-recette-locale')
    tentatives = []
    vrai = socket.socket.connect

    def connect(self, adresse):
        tentatives.append(adresse)
        return vrai(self, adresse)
    monkeypatch.setattr(socket.socket, 'connect', connect)
    r = _anonyme().get('/api/health', headers=_entetes(Accept='text/html'))
    corps = r.get_data(as_text=True)
    assert r.status_code == 200, r.status_code
    assert tentatives == [], 'appels sortants tentés pour un anonyme : %r' % tentatives
    assert len(r.data) < 600, '%d octets pour un anonyme' % len(r.data)
    for donnee in (A.MAIL_TO, A.MAIL_CC, A.SMTP_HOST, 'compte@exemple.test', 'sk-ant', 'plan'):
        assert donnee not in corps, 'la réponse anonyme contient %r' % donnee
    rj = _anonyme().get('/api/health?format=json', headers=_entetes())
    assert rj.status_code == 200 and rj.is_json, (rj.status_code, rj.mimetype)
    assert 'brevo' not in (rj.get_json() or {}), rj.get_json()


def test_api_health_administrateur_interroge_le_compte_brevo_par_la_base_redirigeable(brevo):
    r = _admin().get('/api/health?format=json', headers=_entetes())
    assert r.status_code == 200, r.status_code
    comptes = brevo.recues('GET', '/v3/account', exact=True)
    assert len(comptes) == 1, 'observé %d GET /v3/account' % len(comptes)
    assert comptes[0].entetes['api-key'] == 'xkeysib-recette-locale'
    assert (r.get_json() or {}).get('brevo', {}).get('api_ready') is True, r.get_json().get('brevo')


def test_api_health_ne_livre_rien_a_un_client_connecte_qui_n_est_pas_admin(brevo, monkeypatch):
    """LE TROU QUE LES DEUX RÈGLES VOISINES LAISSAIENT. Elles mesurent
    l'anonyme et l'administrateur ; entre les deux vit le compte Sentinel
    ordinaire, gratuit et ouvert à l'inscription. Avec la garde réduite à
    `if not admin:`, il obtenait MAIL_TO, MAIL_CC, l'hôte SMTP, l'adresse et
    l'offre du compte Brevo — et chaque appel déclenchait un GET /v3/account
    plus un appel au fournisseur du modèle."""
    monkeypatch.setattr(A, 'ANTHROPIC_API_KEY', 'sk-ant-recette-locale')
    monkeypatch.setattr(A, 'sentauth_current_client',
                        lambda: {'id': 999042, 'email': 'client@exemple.test',
                                 'is_conseilprev': False})
    tentatives = []
    vrai = socket.socket.connect

    def connect(self, adresse):
        tentatives.append(adresse)
        return vrai(self, adresse)
    monkeypatch.setattr(socket.socket, 'connect', connect)
    r = _anonyme().get('/api/health?format=json', headers=_entetes())
    assert r.status_code == 200, r.status_code
    assert 'brevo' not in (r.get_json() or {}), r.get_json()
    assert tentatives == [], 'appels sortants pour un client ordinaire : %r' % tentatives
    corps = _anonyme().get('/api/health', headers=_entetes(Accept='text/html')).get_data(as_text=True)
    for donnee in (A.MAIL_TO, A.MAIL_CC, A.SMTP_HOST, A.CONSEILPREV_NOTIFY_EMAIL):
        assert donnee not in corps, 'un client ordinaire lit %r' % donnee
    assert brevo.recues('GET', '/v3/account', exact=True) == []


def test_api_health_reste_atteignable_sans_en_tetes_de_navigateur(brevo):
    """Liste blanche du security_middleware : une sonde n'a pas d'Accept-Language."""
    r = _anonyme().get('/api/health', headers={'User-Agent': 'curl/8.4.0'})
    assert r.status_code == 200, 'la liste blanche ne couvre plus /api/health (%d)' % r.status_code


# ══════════════════════════════════════════════════════════════════════════
#  3. LE RELAIS /api/notify-selection ET L'ÉCHAPPEMENT (G2 / G3)
# ══════════════════════════════════════════════════════════════════════════

def _charge(email='cible@exemple.test'):
    return {'client': {'prenom': 'Paul', 'nom': PIEGE, 'email': email, 'entreprise': 'ACME'},
            'candidates': [{'label': '<img src=https://piege.test/pixel.gif>', 'tjm': 500,
                            'score': 90, 'skills': ['<b>a</b>'],
                            'ident': {'email': 'x@y.test', 'nom': '<script>1</script>'}}]}


def test_la_selection_echappe_les_champs_libres_dans_les_deux_courriels(brevo):
    r = _anonyme().post('/api/notify-selection', json=_charge(), headers=_entetes())
    assert r.status_code == 200, (r.status_code, r.get_json())
    envois = _posts(brevo)
    assert len(envois) == 2, _destinataires(brevo)
    for e in envois:
        html = e.json['htmlContent']
        assert PIEGE not in html, 'lien brut dans le courriel vers %s' % e.json['to'][0]['email']
        assert '<img src=https://piege.test' not in html, 'balise brute dans le courriel'
        assert '<script>' not in html
        assert '&lt;a href=' in html, 'le nom a disparu au lieu d être échappé'


def test_la_selection_est_plafonnee_par_destinataire_et_par_jour(brevo, caplog):
    plafond = getattr(A, 'NOTIFY_SELECTION_PLAFOND_DESTINATAIRE_JOUR', 3)
    for i in range(plafond):
        r = _anonyme().post('/api/notify-selection', json=_charge(), headers=_entetes())
        assert r.status_code == 200, 'envoi n°%d refusé : %s' % (i + 1, r.get_json())
    with caplog.at_level(logging.WARNING, logger='conseilprev'):
        r = _anonyme().post('/api/notify-selection', json=_charge(), headers=_entetes())
    assert r.status_code == 429, 'le %de envoi du jour vers la même adresse passe (%d)' % (
        plafond + 1, r.status_code)
    vers_cible = [d for d in _destinataires(brevo) if d == 'cible@exemple.test']
    assert len(vers_cible) == plafond, 'observé %d envois vers la cible' % len(vers_cible)
    assert 'NOTIFY_SELECTION_REFUSE' in caplog.text, caplog.text
    assert 'cible@exemple.test' not in caplog.text, 'adresse en clair dans le journal'


def test_la_selection_est_plafonnee_globalement_par_jour(brevo, monkeypatch):
    monkeypatch.setattr(A, 'NOTIFY_SELECTION_PLAFOND_GLOBAL_JOUR', 2, raising=False)
    statuts = [_anonyme().post('/api/notify-selection', json=_charge('c%d@exemple.test' % i),
                               headers=_entetes()).status_code for i in range(3)]
    assert statuts == [200, 200, 429], statuts
    assert len(_posts(brevo)) == 4, 'observé %d POST pour 2 sélections' % len(_posts(brevo))


def test_les_plafonds_tiennent_sous_des_appels_simultanes(brevo):
    """LE DÉFAUT MESURÉ. `_notify_selection_autorise` lisait un COUNT, puis la
    route appelait Brevo (jusqu'à 20 s × 3 essais) et la ligne email_log
    n'était écrite qu'APRÈS. Avec 2 workers × 8 fils, toutes les requêtes
    simultanées vers la même adresse lisaient 0 et passaient. Mesure : faux
    Brevo ralenti, 12 fils avec 12 X-Forwarded-For distincts vers la même
    cible → 12 réponses 200, 12 envois, 24 POST, pour un plafond de 3."""
    brevo.lenteurs['POST ' + SMTP_EMAIL] = 0.3
    codes, verrou = [], threading.Lock()

    def tirer(i):
        r = _anonyme().post('/api/notify-selection', json=_charge(),
                            headers=_entetes(**{'X-Forwarded-For': '198.51.100.%d' % (20 + i)}))
        with verrou:
            codes.append(r.status_code)

    fils = [threading.Thread(target=tirer, args=(i,)) for i in range(12)]
    for f in fils:
        f.start()
    for f in fils:
        f.join()
    plafond = A.NOTIFY_SELECTION_PLAFOND_DESTINATAIRE_JOUR
    vers_cible = [d for d in _destinataires(brevo) if d == 'cible@exemple.test']
    assert len(vers_cible) <= plafond, (
        '%d envois vers la cible pour un plafond de %d' % (len(vers_cible), plafond))
    assert codes.count(200) <= plafond, codes
    assert codes.count(429) == 12 - codes.count(200), codes


def test_un_refus_ne_consomme_pas_le_quota_du_jour(brevo):
    """La place réservée est RENDUE quand on refuse : sinon un attaquant
    fermerait le relais pour les vrais clients en se faisant refuser vingt
    fois."""
    reserves = "SELECT COUNT(*) AS n FROM email_log WHERE methode=%r" % (
        A.NOTIFY_SELECTION_METHODE_RESERVE,)
    plafond = A.NOTIFY_SELECTION_PLAFOND_DESTINATAIRE_JOUR
    for _ in range(plafond):
        assert _anonyme().post('/api/notify-selection', json=_charge(),
                               headers=_entetes()).status_code == 200
    for _ in range(4):
        assert _anonyme().post('/api/notify-selection', json=_charge(),
                               headers=_entetes()).status_code == 429
    assert _sql(reserves)[0]['n'] == plafond, (
        'les refus ont consommé des places : %s' % _sql(reserves))


def test_une_base_illisible_refuse_le_relais_sans_aucun_envoi(brevo, monkeypatch):
    """« L'incertitude ne l'ouvre pas », dit la docstring — rien ne le
    mesurait. Avec un `return True, None` à la place du refus, le relais
    public enverrait à n'importe quelle adresse, borné seulement par un
    compteur en mémoire que X-Forwarded-For contourne."""
    def casse():
        raise RuntimeError('base injoignable (simulé)')
    monkeypatch.setattr(A, 'registre_get_db', casse)
    r = _anonyme().post('/api/notify-selection', json=_charge(), headers=_entetes())
    assert r.status_code == 429, (r.status_code, r.get_json())
    assert _posts(brevo) == [], 'envoyé malgré une base illisible : %s' % _destinataires(brevo)


def test_une_adresse_de_destinataire_invalide_est_refusee_sans_envoi(brevo):
    r = _anonyme().post('/api/notify-selection', json=_charge('pas-une-adresse'),
                        headers=_entetes())
    assert r.status_code == 400, r.status_code
    assert _posts(brevo) == [], _destinataires(brevo)


def test_la_selection_en_echec_ne_depose_rien_dans_uploads_cv(brevo, tmp_path):
    """Un nom SANS barre oblique : avec le nom piégé, l'ancien code échouait à
    ouvrir `selection_<date>_<nom>.html` (le nom entrait dans le chemin) et ne
    déposait rien — pour la mauvaise raison."""
    brevo.pannes['POST ' + SMTP_EMAIL] = (500, {'code': 'internal_error'})
    charge = _charge()
    charge['client']['nom'] = 'Simple'
    r = _anonyme().post('/api/notify-selection', json=charge, headers=_entetes())
    assert r.status_code == 200, r.status_code
    uploads = tmp_path / 'uploads'
    deposes = sorted(os.listdir(str(uploads))) if uploads.exists() else []
    assert deposes == [], 'écrit dans uploads_cv/ : %s' % deposes


@pytest.mark.parametrize('gabarit', ['build_html_email', 'build_precontract_html',
                                     'build_conseilprev_notif_html'])
def test_chaque_gabarit_de_courriel_echappe_une_valeur_libre(gabarit):
    if gabarit == 'build_html_email':
        html = A.build_html_email({'prenom': 'X', 'nom': PIEGE, 'message': PIEGE,
                                   'entreprise': PIEGE, 'source_url': PIEGE})
    else:
        html = getattr(A, gabarit)(
            {'prenom': PIEGE, 'nom': PIEGE, 'email': 'e@x.test', 'tel': PIEGE, 'entreprise': PIEGE},
            [{'label': PIEGE, 'titre': PIEGE, 'domaine': PIEGE, 'ville': PIEGE, 'tjm': '500',
              'skills': [PIEGE], 'ident': {'nom': PIEGE, 'email': 'i@x.test', 'source': PIEGE}}])
    assert PIEGE not in html, '%s rend le lien brut' % gabarit
    assert '&lt;a href=' in html, '%s a perdu la valeur au lieu de l échapper' % gabarit


def test_la_demande_de_tarification_echappe_les_valeurs_saisies(brevo):
    r = _anonyme().post('/api/pricing-request', headers=_entetes(),
                        json={'plan': 'pro', 'nom': PIEGE, 'email': 'p@exemple.test',
                              'message': PIEGE, 'secteur': PIEGE})
    assert r.status_code == 200, (r.status_code, r.get_json())
    envois = _posts(brevo)
    assert len(envois) == 1, _destinataires(brevo)
    html = envois[0].json['htmlContent']
    assert PIEGE not in html, 'lien brut dans la notification de tarification'
    assert '&lt;a href=' in html


def test_sanitize_input_ne_pretend_plus_echapper_et_le_dictionnaire_mort_est_parti():
    """Ce qu'elle FAIT est mesuré ; ce qu'elle DIT doit y correspondre."""
    assert A.sanitize_input('<b>x</b>') == '<b>x</b>', 'sanitize_input échappe désormais : ' \
        'les valeurs stockées en base et rendues en JSON sont abîmées'
    assert '_HTML_ESCAPE' not in SOURCE, 'un dictionnaire d échappement défini et jamais employé'
    assert 'chappe les entit' not in (A.sanitize_input.__doc__ or ''), \
        'la docstring promet un échappement que la fonction ne fait pas'


# ══════════════════════════════════════════════════════════════════════════
#  4. LE FICHIER DE REPLI (G4 / F8)
# ══════════════════════════════════════════════════════════════════════════

def test_le_courriel_de_repli_va_dans_un_dossier_dedie_sous_un_nom_imprevisible_en_0600(brevo, tmp_path):
    brevo.pannes['POST ' + SMTP_EMAIL] = (401, {'code': 'unauthorized'})
    ok = A.send_email_smart('victime@exemple.test', 'V', 'Reinitialisation',
                            '<a href="https://site.test/reset-password/JETON-SECRET">x</a>')
    assert ok == (False, 'saved_locally'), ok
    uploads = tmp_path / 'uploads'
    dans_uploads = sorted(os.listdir(str(uploads))) if uploads.exists() else []
    assert dans_uploads == [], 'le courriel de repli est écrit dans uploads_cv/ : %s' % dans_uploads
    repli = tmp_path / 'repli'
    fichiers = sorted(os.listdir(str(repli))) if repli.exists() else []
    assert len(fichiers) == 1, fichiers
    nom = fichiers[0]
    assert re.match(r'^courriel_\d{8}_\d{6}_[0-9a-f]{16}\.html$', nom), 'nom prévisible : %s' % nom
    assert 'victime' not in nom
    mode = stat.S_IMODE(os.stat(str(repli / nom)).st_mode)
    assert mode == 0o600, 'mode du fichier de repli : %o' % mode
    assert stat.S_IMODE(os.stat(str(repli)).st_mode) == 0o700
    assert 'JETON-SECRET' in io.open(str(repli / nom), encoding='utf-8').read()


#: LES ÉCRITURES QUI DÉSIGNENT LE MÊME FICHIER. La garde comparait le chemin
#: BRUT, la route statique le NORMALISE ensuite : les deux ne regardaient donc
#: pas le même fichier. Mesuré avec le client de test puis sous gunicorn avec
#: `curl --path-as-is` : « /uploads_cv/<cv>.pdf » rendait bien 404, mais
#: « /./uploads_cv/<cv>.pdf » et « /%2e/uploads_cv/… » servaient le CV en 200
#: (1 199 octets, %PDF-1.4) — donc des données personnelles de candidats, et
#: des courriels de repli jeton compris. Le filtre anti-injection ne cherche
#: que « ../ » et laisse passer « ./ ».
ECRITURES_DU_MEME_CHEMIN = [
    '/%s/%s',            # la forme canonique
    '/.%%2f%s/%s',       # le point, puis la barre encodée
    '/./%s/%s',
    '/%%2e/%s/%s',
    '/.//%s/%s',
    '/././/%s/%s',
    '/%s/../%s/%s',      # un aller-retour par le parent
    'CASSE',             # le dossier en majuscules (traité à part)
]
#: Des identifiants lisibles : les écritures elles-mêmes portent des « % »
#: que pytest recopie dans le nom de la règle, et une table de mutations
#: nomme cette règle.
NOMS_DES_ECRITURES = ['canonique', 'point-puis-barre-encodee', 'point-barre',
                      'point-encode', 'point-double-barre', 'points-repetes',
                      'aller-retour-par-le-parent', 'casse']


@pytest.mark.parametrize('dossier', ['uploads_cv', 'courriels_repli'])
@pytest.mark.parametrize('ecriture', ECRITURES_DU_MEME_CHEMIN,
                         ids=NOMS_DES_ECRITURES)
def test_un_fichier_des_dossiers_prives_n_est_pas_servi(dossier, ecriture):
    """Un fichier qui EXISTE, dans le vrai dossier, demandé par CHACUNE des
    écritures que `static_folder='.'` sert : 404, sans son contenu."""
    chemin_dossier = os.path.join(ICI, dossier)
    cree_dossier = not os.path.isdir(chemin_dossier)
    os.makedirs(chemin_dossier, exist_ok=True)
    nom = 'recette_prive_%s.html' % secrets.token_hex(4)
    chemin = os.path.join(chemin_dossier, nom)
    io.open(chemin, 'w', encoding='utf-8').write('<p>JETON-SECRET-RECETTE</p>')
    if ecriture == 'CASSE':
        demande = '/%s/%s' % (dossier.upper(), nom)
    elif ecriture.count('%s') == 3:
        demande = ecriture % (dossier, dossier, nom)
    else:
        demande = ecriture % (dossier, nom)
    try:
        r = _anonyme().get(demande, headers=_entetes(Accept='text/html'))
        assert r.status_code == 404, '%s est servi (%d)' % (demande, r.status_code)
        assert b'JETON-SECRET-RECETTE' not in r.data, '%s livre le contenu' % demande
    finally:
        os.remove(chemin)
        if cree_dossier:
            os.rmdir(chemin_dossier)


@pytest.mark.parametrize('dossier', ['uploads_cv', 'courriels_repli'])
def test_le_dossier_prive_lui_meme_n_est_pas_listable(dossier, caplog):
    """Sans barre finale, le chemin désigne le DOSSIER. Werkzeug rend 404 sur
    un dossier de toute façon : c'est le JOURNAL qu'on lit, pour vérifier que
    la garde a bien statué — sinon la règle passerait sur une garde qui ne
    voit plus ce cas, et le jour où la route statique changerait de
    comportement, rien ne le dirait."""
    with caplog.at_level(logging.WARNING, logger='conseilprev'):
        r = _anonyme().get('/' + dossier, headers=_entetes(Accept='text/html'))
    assert r.status_code == 404, '/%s répond %d' % (dossier, r.status_code)
    assert 'DOSSIER_PRIVE' in caplog.text, (
        'la garde ne voit plus /%s : %s' % (dossier, caplog.text))


def test_le_chemin_livre_par_le_mandataire_est_normalise_lui_aussi():
    """Werkzeug réécrit certaines formes AVANT la vue ; un mandataire, non.
    On pose donc le PATH_INFO tel qu'un serveur le livrerait."""
    d = os.path.join(ICI, 'uploads_cv')
    cree = not os.path.isdir(d)
    os.makedirs(d, exist_ok=True)
    nom = 'recette_prive_%s.html' % secrets.token_hex(4)
    io.open(os.path.join(d, nom), 'w', encoding='utf-8').write('<p>JETON-SECRET-RECETTE</p>')
    try:
        for brut in ('//./uploads_cv/' + nom, '/.//uploads_cv/' + nom,
                     '/uploads_cv/./' + nom):
            r = _anonyme().get('/', environ_overrides={'PATH_INFO': brut},
                               headers=_entetes(Accept='text/html'))
            assert r.status_code == 404, '%s est servi (%d)' % (brut, r.status_code)
            assert b'JETON-SECRET-RECETTE' not in r.data
    finally:
        os.remove(os.path.join(d, nom))
        if cree:
            os.rmdir(d)


def test_un_cv_de_demonstration_n_est_plus_servi_en_direct():
    nom = '20260614_181515_Amina_Diallo.pdf'
    assert os.path.exists(os.path.join(ICI, 'uploads_cv', nom)), 'le CV de démonstration manque'
    r = _anonyme().get('/uploads_cv/' + nom, headers=_entetes(Accept='text/html'))
    assert r.status_code == 404, 'un CV est servi à l anonyme (%d)' % r.status_code


def test_l_administrateur_telecharge_toujours_un_cv_par_la_route_protegee():
    nom = 'recette_brevo_%s.pdf' % secrets.token_hex(3)
    chemin = os.path.join(A.UPLOAD_FOLDER, nom)
    os.makedirs(A.UPLOAD_FOLDER, exist_ok=True)
    io.open(chemin, 'wb').write(b'%PDF-1.4 recette\n')
    try:
        assert _anonyme().get('/api/admin/cv/' + nom, headers=_entetes()).status_code == 403
        r = _admin().get('/api/admin/cv/' + nom, headers=_entetes())
        assert r.status_code == 200, 'l administrateur n obtient plus le CV (%d)' % r.status_code
        assert r.data.startswith(b'%PDF')
    finally:
        os.remove(chemin)


def test_le_dossier_de_repli_est_ignore_par_git():
    lignes = [l.strip() for l in io.open(os.path.join(ICI, '.gitignore'), encoding='utf-8')]
    assert 'courriels_repli/' in lignes, lignes


# ══════════════════════════════════════════════════════════════════════════
#  5. RÉESSAI BORNÉ ET RÉUTILISATION DE CONNEXION (M5 / M6)
# ══════════════════════════════════════════════════════════════════════════

def test_un_429_passager_est_reessaye_puis_reussit(brevo):
    vus = []

    def reponse(r):
        vus.append(r)
        return (429, {'code': 'too_many_requests'}) if len(vus) == 1 else (201, {'messageId': '<ok>'})
    brevo.route('POST', SMTP_EMAIL, reponse)
    ok, motif = A.send_via_brevo_api('r@exemple.test', 'R', 'S', '<p/>')
    assert ok is True, 'un 429 passager perd le courriel : %s' % motif
    assert len(_posts(brevo)) == 2, 'observé %d tentatives' % len(_posts(brevo))
    assert brevo.pauses == [0.5], 'attentes observées : %r' % brevo.pauses


def test_un_5xx_persistant_s_arrete_apres_deux_reessais_avec_attentes_courtes(brevo):
    brevo.pannes['POST ' + SMTP_EMAIL] = (503, {'code': 'service_unavailable'})
    assert A.send_via_brevo_api('r@exemple.test', 'R', 'S', '<p/>') == (False, 'http_503')
    assert len(_posts(brevo)) == 3, 'observé %d tentatives' % len(_posts(brevo))
    assert brevo.pauses == [0.5, 1.0], 'attentes observées : %r' % brevo.pauses


@pytest.mark.parametrize('statut', [400, 401, 402])
def test_un_refus_4xx_n_est_jamais_reessaye(brevo, statut):
    brevo.pannes['POST ' + SMTP_EMAIL] = (statut, {'code': 'refus'})
    assert A.send_via_brevo_api('r@exemple.test', 'R', 'S', '<p/>') == (False, 'http_%d' % statut)
    assert len(_posts(brevo)) == 1, 'un %d a été rejoué %d fois' % (statut, len(_posts(brevo)))
    assert brevo.pauses == [], brevo.pauses


def test_un_delai_de_lecture_n_est_jamais_reessaye(brevo, monkeypatch, reseau_ferme):
    """Un serveur qui accepte la connexion et ne répond jamais : la requête EST
    PARTIE. L'ancienne règle attendait ici deux réessais — c'était l'erreur.
    L'API transactionnelle de Brevo n'a pas de clé d'idempotence : chaque
    tentative est un nouvel envoi, et un Brevo lent faisait recevoir trois fois
    la confirmation, puis une quatrième par le repli SMTP."""
    sourd = socket.socket()
    sourd.bind(('127.0.0.1', 0)); sourd.listen(1)
    port = sourd.getsockname()[1]
    reseau_ferme.add(port)
    monkeypatch.setattr(A, 'BREVO_DELAI', 0.2, raising=False)
    monkeypatch.setattr(A, 'BREVO_API_URL', 'http://127.0.0.1:%d%s' % (port, SMTP_EMAIL))
    try:
        ok, motif = A.send_via_brevo_api('r@exemple.test', 'R', 'S', '<p/>')
    finally:
        sourd.close()
    assert (ok, motif) == (False, 'delai_reponse'), (ok, motif)
    assert brevo.pauses == [], 'réessai après un délai de lecture : %r' % brevo.pauses
    lignes = _sql("SELECT methode, raison_echec FROM email_log "
                  "WHERE destinataire='r@exemple.test'")
    assert lignes and lignes[-1]['raison_echec'] == 'delai_reponse', lignes


def test_un_brevo_lent_ne_fait_pas_partir_le_courriel_trois_fois(brevo, monkeypatch):
    """LA MESURE DU DÉFAUT, du côté de Brevo : combien de POST il a REÇUS.
    Le faux serveur lit la requête puis répond au-delà du délai ; l'ancien code
    en envoyait trois, donc trois exemplaires dans la boîte du client."""
    brevo.lenteurs['POST ' + SMTP_EMAIL] = 0.6
    monkeypatch.setattr(A, 'BREVO_DELAI', 0.2, raising=False)
    ok, motif = A.send_email_smart('lent@exemple.test', 'L', 'Votre réservation', '<p/>')
    assert (ok, motif) == (False, 'delai_reponse'), (ok, motif)
    assert len(_posts(brevo)) == 1, '%d envois reçus par Brevo' % len(_posts(brevo))


def test_un_delai_de_lecture_n_enchaine_pas_sur_le_repli(brevo, monkeypatch, tmp_path):
    """L'issue est INCERTAINE, pas négative : un exemplaire certain de plus
    (SMTP, ou le fichier de repli) est pire qu'un envoi douteux."""
    brevo.lenteurs['POST ' + SMTP_EMAIL] = 0.6
    monkeypatch.setattr(A, 'BREVO_DELAI', 0.2, raising=False)
    monkeypatch.setattr(A, 'SMTP_USER', 'recette@exemple.test')
    monkeypatch.setattr(A, 'SMTP_PASSWORD', 'motdepasse-de-recette')
    repli = tmp_path / 'repli2'
    monkeypatch.setattr(A, 'REPLI_COURRIELS_DOSSIER', str(repli), raising=False)
    smtp = []
    monkeypatch.setattr(A.smtplib, 'SMTP', lambda *a, **k: smtp.append(a) or _boum())
    assert A.send_email_smart('lent2@exemple.test', 'L', 'S', '<p/>') == (False, 'delai_reponse')
    assert smtp == [], 'le repli SMTP a été tenté : un quatrième exemplaire'
    assert not repli.exists() or os.listdir(str(repli)) == [], 'courriel déposé en repli'


def _boum():
    raise AssertionError('le repli SMTP ne doit pas être atteint')


def test_une_connexion_refusee_est_reessayee_deux_fois(brevo, monkeypatch, reseau_ferme):
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    reseau_ferme.add(port)
    monkeypatch.setattr(A, 'BREVO_API_URL', 'http://127.0.0.1:%d%s' % (port, SMTP_EMAIL))
    ok, motif = A.send_via_brevo_api('r@exemple.test', 'R', 'S', '<p/>')
    assert ok is False and motif.startswith('reseau'), (ok, motif)
    assert brevo.pauses == [0.5, 1.0], 'attentes observées : %r' % brevo.pauses


def test_dix_envois_reutilisent_une_seule_session_http(brevo, monkeypatch):
    creees = []
    init = requests.Session.__init__

    def espion(self, *a, **k):
        creees.append(self)
        return init(self, *a, **k)
    monkeypatch.setattr(requests.Session, '__init__', espion)
    for i in range(10):
        assert A.send_via_brevo_api('x%d@exemple.test' % i, 'X', 's', '<p/>')[0] is True
    assert len(_posts(brevo)) == 10
    assert len(creees) <= 1, '%d Session créées pour 10 envois' % len(creees)


def test_l_inscription_d_un_contact_consenti_passe_par_la_base_redirigeable(brevo):
    _sql("CREATE TABLE IF NOT EXISTS consent_records (id INTEGER PRIMARY KEY AUTOINCREMENT, "
         "horodatage TEXT, sujet TEXT, email TEXT, email_hash TEXT, methode TEXT, finalites TEXT, "
         "politique_version TEXT, ip_hash TEXT, user_agent TEXT, retrait INTEGER DEFAULT 0, "
         "efface INTEGER DEFAULT 0)")
    _sql("INSERT INTO consent_records (horodatage, email, finalites, retrait, efface) "
         "VALUES (?,?,?,0,0)", (datetime.utcnow().isoformat(), 'abonne@exemple.test',
                                '{"lettre_information": true}'))
    ok, motif = A.add_contact_to_brevo('abonne@exemple.test', 'A', 'B')
    assert (ok, motif) == (True, 'ok'), (ok, motif)
    contacts = brevo.recues('POST', '/v3/contacts', exact=True)
    assert len(contacts) == 1, 'observé %d POST /v3/contacts' % len(contacts)
    assert contacts[0].json['email'] == 'abonne@exemple.test'
    assert contacts[0].entetes['api-key'] == 'xkeysib-recette-locale'


# ══════════════════════════════════════════════════════════════════════════
#  6. LE WEBHOOK ET LA LISTE DE SUPPRESSION (M7 / F5)
# ══════════════════════════════════════════════════════════════════════════

EVENEMENT = [{'event': 'unsubscribe', 'email': 'desinscrit@exemple.test',
              'message-id': '<forge@x>', 'tags': ['essai-j3']}]


def _webhook(client, jeton=None, forme='en-tete', charge=None):
    h = _entetes()
    url = '/api/brevo/webhook'
    if jeton is not None:
        if forme == 'en-tete':
            h['X-Brevo-Token'] = jeton
        elif forme == 'bearer':
            h['Authorization'] = 'Bearer ' + jeton
        else:
            url += '?token=' + jeton
    return client.post(url, json=charge if charge is not None else EVENEMENT, headers=h)


def test_le_webhook_sans_jeton_configure_repond_503_et_le_journalise(monkeypatch, caplog):
    monkeypatch.setattr(A, 'BREVO_WEBHOOK_TOKEN', '', raising=False)
    with caplog.at_level(logging.ERROR, logger='conseilprev'):
        r = _webhook(_anonyme())
    assert r.status_code == 503, 'webhook non configuré et pourtant %d' % r.status_code
    assert 'BREVO_WEBHOOK_SANS_JETON' in caplog.text, caplog.text


@pytest.mark.parametrize('forme', ['en-tete', 'bearer', 'parametre'])
def test_le_webhook_refuse_un_jeton_faux_ou_absent_et_accepte_le_bon(monkeypatch, forme):
    monkeypatch.setattr(A, 'BREVO_WEBHOOK_TOKEN', 'jeton-recette-0123', raising=False)
    assert _webhook(_anonyme()).status_code == 401, 'sans jeton, accepté'
    assert _webhook(_anonyme(), 'jeton-faux', forme).status_code == 401, 'jeton faux accepté'
    r = _webhook(_anonyme(), 'jeton-recette-0123', forme)
    assert r.status_code == 200, (forme, r.status_code, r.get_json())


# « -- » est la forme que `secrets.token_urlsafe` produit tout seul (son
# alphabet porte le tiret) ; l'apostrophe, celle d'un jeton écrit à la main.
# « # » n'est pas ici : aucun client HTTP ne l'envoie dans une adresse, il y
# ouvre un fragment — un jeton qui en contient serait tronqué avant d'arriver,
# ce qui est un autre défaut et pas celui-ci.
@pytest.mark.parametrize('jeton', ['Ab3--xY7zKlmNop', "Ab3'xY7zKlmNop"])
def test_un_jeton_a_caracteres_suspects_passe_en_parametre_sans_bloquer_brevo(monkeypatch, jeton):
    """LE DÉFAUT MESURÉ. La docstring du webhook donne `?token=<jeton>` comme
    forme de repli — la seule que l'écran « Webhooks » de Brevo accepte quand
    il ne propose qu'une adresse — sans contraindre l'alphabet. Or le filtre
    anti-injection s'applique à `request.url`, et un jeton tiré par
    `secrets.token_urlsafe` contient « -- » environ une fois sur cent (le code
    le mesure : 0,98 % sur 200 000 tirages). Avec un tel jeton, CHAQUE
    livraison Brevo recevait 403 et l'adresse de Brevo était bloquée une
    heure : plus un seul événement de suppression enregistré, et même les
    livraisons en en-tête recevant ensuite 429."""
    monkeypatch.setattr(A, 'BREVO_WEBHOOK_TOKEN', jeton, raising=False)
    c = _anonyme()
    r = c.post('/api/brevo/webhook?token=' + jeton, json=[], headers=_entetes())
    assert r.status_code == 200, (jeton, r.status_code, r.get_data(as_text=True)[:120])
    assert not A.limiter.is_blocked('203.0.113.9'), 'adresse de Brevo bloquée'
    # Et la livraison suivante, en en-tête, passe toujours.
    assert _webhook(c, jeton).status_code == 200


def test_le_filtre_anti_injection_reste_arme_ailleurs():
    """L'EXEMPTION S'ARRÊTE AU POINT DE RÉCEPTION. Un chemin à saisie libre
    doit toujours faire tomber le filtre, sinon on a échangé un faux positif
    contre un trou."""
    r = _anonyme().get("/api/registre?q=' OR 1=1--", headers=_entetes())
    assert r.status_code == 403, r.status_code


def test_le_jeton_du_webhook_est_compare_en_temps_constant():
    i = SOURCE.index('def brevo_webhook(')
    corps = SOURCE[i:SOURCE.index('\ndef ', i + 1)]
    assert 'compare_digest' in corps, 'comparaison de jeton par == : mesurable au chronomètre'


# LES FORMES QUE BREVO EMPLOIE RÉELLEMENT. La charge transactionnelle porte
# « unsubscribed » ; la liste des événements d'un webhook dit « unsubscribe ».
# Seule la seconde était mesurée : retirer la première du code laissait les
# désinscriptions réelles sans effet, relances et courriels continuant de
# partir vers une personne qui s'est désinscrite — et la recette restait
# verte. « invalid_email » n'était pas mesuré non plus.
EVENEMENTS_DE_SUPPRESSION = ['unsubscribe', 'unsubscribed', 'hard_bounce',
                             'spam', 'blocked', 'invalid_email']


@pytest.mark.parametrize('evenement', EVENEMENTS_DE_SUPPRESSION)
def test_un_evenement_de_suppression_bloque_les_envois_suivants_sans_POST(brevo, monkeypatch, evenement):
    monkeypatch.setattr(A, 'BREVO_WEBHOOK_TOKEN', 'jeton-recette-0123', raising=False)
    r = _webhook(_anonyme(), 'jeton-recette-0123',
                 charge=[{'event': evenement, 'email': 'signale@exemple.test', 'message-id': '<m>'}])
    assert r.status_code == 200, r.status_code
    assert A.send_email_smart('signale@exemple.test', 'S', 'Votre essai', '<p/>') == (False, 'supprime')
    assert A.send_via_brevo_api('signale@exemple.test', 'S', 'Votre essai', '<p/>') == (False, 'supprime')
    # LA CASSE NE COMPTE PAS, et rien ne le mesurait : Brevo signale l'adresse
    # en minuscules, le site écrit ensuite à celle que le client a SAISIE
    # (« Signale@Exemple.test »). Sans lecture insensible à la casse, l'envoi
    # repart vers une adresse désinscrite.
    assert A.send_email_smart('Signale@Exemple.test', 'S', 'Votre essai', '<p/>') == (False, 'supprime')
    assert _posts(brevo) == [], 'envoyé malgré %s : %s' % (evenement, _destinataires(brevo))
    lignes = _sql("SELECT methode, raison_echec FROM email_log WHERE LOWER(destinataire)='signale@exemple.test'")
    assert lignes and all(l['methode'] == 'refuse' and str(l['raison_echec']).startswith('supprime')
                          for l in lignes), lignes


def test_un_soft_bounce_ne_supprime_pas_l_adresse(brevo, monkeypatch):
    monkeypatch.setattr(A, 'BREVO_WEBHOOK_TOKEN', 'jeton-recette-0123', raising=False)
    _webhook(_anonyme(), 'jeton-recette-0123',
             charge=[{'event': 'soft_bounce', 'email': 'plein@exemple.test'}])
    assert A.send_email_smart('plein@exemple.test', 'P', 'S', '<p/>') == (True, 'brevo_api')


def test_le_webhook_ne_journalise_pas_l_adresse_en_clair(brevo, monkeypatch, caplog):
    monkeypatch.setattr(A, 'BREVO_WEBHOOK_TOKEN', 'jeton-recette-0123', raising=False)
    with caplog.at_level(logging.INFO, logger='conseilprev'):
        assert _webhook(_anonyme(), 'jeton-recette-0123').status_code == 200
    assert 'BREVO_' in caplog.text, caplog.text
    assert 'desinscrit@exemple.test' not in caplog.text, 'adresse en clair dans le journal'
    assert 'd***@exemple.test' in caplog.text, caplog.text


# ══════════════════════════════════════════════════════════════════════════
#  6 bis. LA RÉSERVATION DE FORMATION, QUI EST PUBLIQUE
# ══════════════════════════════════════════════════════════════════════════
#
# /api/formation/inscription est ouverte à l'anonyme, la première séance de
# chaque clé client est OFFERTE et confirmée d'emblée, et chaque envoi fait
# partir deux courriels — l'accusé vers l'adresse fournie, la notification
# vers la boîte réelle de CONSEILPREV. Deux défauts mesurés s'y rejoignent :
# les champs libres arrivaient bruts dans le HTML de la notification, et rien
# ne bornait le nombre de réservations ni de courriels.

def _creneau(n=0):
    import datetime as _dt
    return [x['date'] for x in formations_ia.creneaux(_dt.datetime.utcnow().date())][n]


def _inscrire(creneau, email='inconnu@exemple.test', sujet=0, **extra):
    charge = {'seances': [{'sujet': formations_ia.SUJETS[sujet]['cle'], 'creneau': creneau}],
              'nom': 'Dupont', 'prenom': 'Paul', 'email': email, 'entreprise': 'ACME',
              'telephone': '+33 6 12 34 56 78', 'lieu': '9 av. du Test, 75000 Paris'}
    charge.update(extra)
    return _anonyme().post('/api/formation/inscription', json=charge, headers=_entetes())


def test_la_notification_de_formation_echappe_chaque_champ_libre(brevo, monkeypatch):
    """LE DÉFAUT MESURÉ. `sanitize_input` n'échappe plus rien — c'est voulu, et
    mesuré ailleurs : elle assainit ce qu'on STOCKE. Huit champs de ce
    formulaire public entraient donc bruts dans le HTML d'une notification qui
    part désormais dans la VRAIE boîte de l'administrateur : s'inscrire sous le
    nom `<a href="…">Cliquez pour valider</a>` y faisait arriver un lien
    choisi par un inconnu, sous l'expéditeur du site et avec sa mise en page."""
    monkeypatch.delenv('STRIPE_SECRET_KEY', raising=False)
    r = _inscrire(_creneau(), nom=PIEGE, entreprise=PIEGE, message=PIEGE, lieu=PIEGE,
                  fonction=PIEGE)
    assert r.status_code == 200, r.get_json()
    envois = _posts(brevo)
    assert envois, 'aucun courriel envoyé'
    for e in envois:
        html = e.json['htmlContent']
        assert PIEGE not in html, 'lien brut dans le courriel vers %s' % e.json['to'][0]['email']
    interne = [e for e in envois if e.json['to'][0]['email'] == A.CONSEILPREV_NOTIFY_EMAIL]
    assert interne, _destinataires(brevo)
    assert '&lt;a href=' in interne[0].json['htmlContent'], \
        'la valeur a disparu au lieu d être échappée'


def test_le_nom_affiche_ne_fabrique_pas_une_seconde_adresse(brevo, monkeypatch):
    """`prenom + ' ' + nom` d'un formulaire public entrait tel quel dans le
    champ `to.name`, c'est-à-dire dans l'en-tête « To: » où les chevrons
    DÉLIMITENT l'adresse (RFC 5322)."""
    monkeypatch.delenv('STRIPE_SECRET_KEY', raising=False)
    assert _inscrire(_creneau(), nom=PIEGE).status_code == 200
    noms = [e.json['to'][0].get('name', '') for e in _posts(brevo)]
    assert noms, 'aucun courriel envoyé'
    for n in noms:
        assert '<' not in n and '>' not in n, 'chevrons dans le nom affiché : %r' % n


def test_un_anonyme_ne_peut_pas_prendre_toute_la_campagne(brevo, monkeypatch):
    """LE DÉFAUT MESURÉ. La campagne compte 26 créneaux (2026-10-06 →
    2027-03-30), une date ne se réserve qu'une fois, et la première séance de
    chaque clé client est offerte sans paiement ni vérification de l'adresse.
    26 POST à des courriels inventés suffisaient donc à occuper TOUTE la
    campagne — et à dépenser 52 des 300 envois du jour."""
    monkeypatch.delenv('STRIPE_SECRET_KEY', raising=False)
    codes = [_inscrire(_creneau(i), email='offert%d@exemple.test' % i).status_code
             for i in range(A.FORMATION_IA_OFFERTES_JOUR + 1)]
    assert codes[:-1] == [200] * A.FORMATION_IA_OFFERTES_JOUR, codes
    assert codes[-1] == 429, (
        'la %de séance offerte du jour passe encore (%s)' % (len(codes), codes[-1]))
    poses = _sql("SELECT COUNT(*) AS n FROM formation_ia_resa "
                 "WHERE email LIKE 'offert%@exemple.test'")
    assert poses[0]['n'] == A.FORMATION_IA_OFFERTES_JOUR, poses


def test_une_meme_adresse_ne_reserve_pas_sans_fin(brevo, monkeypatch):
    monkeypatch.delenv('STRIPE_SECRET_KEY', raising=False)
    # Un sujet différent à chaque fois : sinon c'est « déjà inscrit à ce
    # sujet » (409) qui répondrait, et la borne ne serait pas mesurée.
    codes = [_inscrire(_creneau(i), email='repete@exemple.test', sujet=i).status_code
             for i in range(A.FORMATION_IA_PLAFOND_ADRESSE_JOUR + 1)]
    assert codes[:-1] == [200] * A.FORMATION_IA_PLAFOND_ADRESSE_JOUR, codes
    assert codes[-1] == 429, codes


def test_le_plafond_global_du_jour_borne_la_depense_de_courriels(brevo, monkeypatch):
    monkeypatch.delenv('STRIPE_SECRET_KEY', raising=False)
    monkeypatch.setattr(A, 'FORMATION_IA_PLAFOND_GLOBAL_JOUR', 2, raising=False)
    monkeypatch.setattr(A, 'FORMATION_IA_OFFERTES_JOUR', 99, raising=False)
    codes = [_inscrire(_creneau(i), email='glob%d@exemple.test' % i).status_code
             for i in range(3)]
    assert codes == [200, 200, 429], codes
    assert len(_posts(brevo)) == 4, '%d courriels pour 2 réservations' % len(_posts(brevo))


def test_un_refus_de_borne_ne_journalise_pas_l_adresse_en_clair(brevo, monkeypatch, caplog):
    monkeypatch.delenv('STRIPE_SECRET_KEY', raising=False)
    monkeypatch.setattr(A, 'FORMATION_IA_PLAFOND_GLOBAL_JOUR', 1, raising=False)
    _inscrire(_creneau(0), email='premier@exemple.test')
    with caplog.at_level(logging.WARNING, logger='conseilprev'):
        assert _inscrire(_creneau(1), email='refuse@exemple.test').status_code == 429
    assert 'FORMATION_IA_BORNE' in caplog.text, caplog.text
    assert 'refuse@exemple.test' not in caplog.text, 'adresse en clair dans le journal'


# ══════════════════════════════════════════════════════════════════════════
#  6 ter. LE JOURNAL NE SE LAISSE PAS ÉCRIRE PAR UN ANONYME
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize('saut', ['\n', '\r\n', '\r', ' '])
def test_aucune_entree_de_journal_ne_tient_sur_deux_lignes(caplog, saut):
    """LE DÉFAUT MESURÉ, sur /api/stripe/retour : `?session_id=cs_x%0A2026-09-24
    12:00:00,000 INFO STRIPE_OFFRE_ACTIVEE client=7 plan=entreprise` faisait
    apparaître dans le journal Render une FAUSSE activation d'offre, sur sa
    propre ligne, avec l'horodatage et le niveau d'un vrai événement.
    Assainir au point d'écriture demanderait de retrouver les centaines de
    `logger.*` du fichier ; le filtre est le seul endroit par lequel ils
    passent tous."""
    forge = 'cs_x%s2026-09-24 12:00:00,000 INFO STRIPE_OFFRE_ACTIVEE client=7' % saut
    with caplog.at_level(logging.WARNING, logger='conseilprev'):
        A.logger.warning('RECETTE_JOURNAL session=%s', forge)
    ligne = caplog.records[-1].getMessage()
    for f in ('\n', '\r', ' ', ' '):
        assert f not in ligne, 'fin de ligne conservée : %r' % ligne
    assert 'STRIPE_OFFRE_ACTIVEE' in ligne, 'la valeur a été perdue : %r' % ligne


# ══════════════════════════════════════════════════════════════════════════
#  7. L'EXPÉDITEUR ET LES ADRESSES NON ROUTABLES (M8 / M9)
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize('adresse', ['', 'noreply@conseilprev.onrender.com',
                                     'x@internal.system', 'x@gmail.com'])
def test_un_expediteur_non_verifiable_est_signale_au_demarrage(adresse):
    journal = []

    class _Journal(object):
        @staticmethod
        def error(message):
            journal.append(message)
    motif = A.verifier_mail_from(adresse, journal=_Journal)
    assert motif, 'MAIL_FROM=%r accepté sans un mot' % adresse
    assert journal and 'CONFIGURATION INVALIDE' in journal[0], journal


def test_un_expediteur_de_domaine_propre_n_est_pas_signale():
    assert A.verifier_mail_from('contact@i-aes.com') is None


def test_la_garde_est_appelee_au_demarrage_sur_MAIL_FROM_et_le_defaut_est_inchange():
    assert re.search(r'^_MAIL_FROM_MOTIF_REFUS = verifier_mail_from\(MAIL_FROM\)$', SOURCE, re.M), \
        'la garde existe mais rien ne l appelle au démarrage'
    assert "os.environ.get('MAIL_FROM', 'noreply@conseilprev.onrender.com')" in SOURCE, \
        'la valeur par défaut a changé : ce n était pas demandé'


@pytest.mark.parametrize('chemin', ['send_email_smart', 'send_via_brevo_api'])
def test_aucun_envoi_ne_cible_une_adresse_internal_system(brevo, chemin):
    ok, motif = getattr(A, chemin)('conseilprev@internal.system', 'CONSEILPREV', 'Sujet', '<p/>')
    assert (ok, motif) == (False, 'adresse_non_routable'), (ok, motif)
    assert _posts(brevo) == [], 'un crédit consommé pour %s' % _destinataires(brevo)
    lignes = _sql("SELECT methode, raison_echec FROM email_log "
                  "WHERE destinataire='conseilprev@internal.system' ORDER BY id DESC LIMIT 1")
    assert lignes == [{'methode': 'refuse', 'raison_echec': 'adresse_non_routable'}], lignes
    _sql("DELETE FROM email_log WHERE destinataire='conseilprev@internal.system'")


def test_les_notifications_internes_visent_l_adresse_de_notification():
    assert 'send_email_smart(CONSEILPREV_INTERNAL_EMAIL' not in SOURCE, \
        'un envoi vise encore l adresse interne fictive'
    assert ' or CONSEILPREV_INTERNAL_EMAIL' not in SOURCE, \
        'un repli de destinataire vise encore l adresse interne fictive'


def test_le_rapport_de_cartographie_du_compte_conseilprev_est_route_vers_une_boite_reelle():
    A.schedule_cartographie_report(999123, 'conseilprev@internal.system', 'CONSEILPREV')
    lignes = _sql('SELECT client_email FROM pending_reports WHERE client_id=999123')
    _sql('DELETE FROM pending_reports WHERE client_id=999123')
    assert lignes == [{'client_email': A.CONSEILPREV_NOTIFY_EMAIL}], lignes


# ══════════════════════════════════════════════════════════════════════════
#  8. RÉTENTION DU JOURNAL ET TRAVAIL DE FOND (F10 / F11)
# ══════════════════════════════════════════════════════════════════════════

def test_email_log_purge_les_lignes_de_plus_de_90_jours_et_garde_les_recentes(brevo):
    ancien = (datetime.utcnow() - timedelta(days=100)).isoformat()
    recent = (datetime.utcnow() - timedelta(days=80)).isoformat()
    for dest, date in (('ancien@exemple.test', ancien), ('recent@exemple.test', recent)):
        _sql('INSERT INTO email_log (destinataire, sujet, methode, succes, raison_echec, date_envoi) '
             'VALUES (?,?,?,?,?,?)', (dest, 'S', 'brevo_api', 1, None, date))
    A.email_log_record('neuf@exemple.test', 'S', 'brevo_api', True)
    restants = sorted(l['destinataire'] for l in _sql(
        "SELECT destinataire FROM email_log WHERE destinataire IN "
        "('ancien@exemple.test','recent@exemple.test','neuf@exemple.test')"))
    assert restants == ['neuf@exemple.test', 'recent@exemple.test'], restants


def test_un_visiteur_anonyme_sur_me_ne_declenche_aucune_relance(monkeypatch):
    appels = []
    monkeypatch.setattr(A, 'check_pending_reports', lambda: appels.append('rapports'))
    monkeypatch.setattr(A, '_essai_relances', lambda: appels.append('relances'))
    r = _anonyme().get('/api/sentinel-auth/me', headers=_entetes())
    assert r.status_code == 401, r.status_code
    assert appels == [], 'travail de fond déclenché par un anonyme : %r' % appels


def test_un_administrateur_connecte_sur_me_declenche_bien_le_travail_de_fond(monkeypatch):
    appels = []
    monkeypatch.setattr(A, 'check_pending_reports', lambda: appels.append('rapports'))
    monkeypatch.setattr(A, '_essai_relances', lambda: appels.append('relances'))
    r = _admin().get('/api/sentinel-auth/me', headers=_entetes())
    assert r.status_code == 200, r.status_code
    assert appels == ['rapports', 'relances'], appels
