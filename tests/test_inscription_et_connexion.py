"""LE PARCOURS D'UN NOUVEAU CLIENT, DE L'INSCRIPTION À L'ACCÈS.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande de vérification des accès et de la
sécurité de connexion à Sentinel après inscription, avec les notifications au
client et à l'administrateur. Le parcours a donc été JOUÉ bout en bout, courriers
capturés, plutôt que relu. La mécanique s'est révélée solide — anti-énumération,
anti-force brute, vérification d'email obligatoire, cloisonnement des plans — et
c'est ce qui rend les quatre défauts trouvés d'autant plus coûteux : ils ne se
voient sur aucune page.

PREMIER DÉFAUT, ET LE PLUS GRAVE : LES TROIS COURRIERS QUI PORTENT UN JETON
DÉSIGNAIENT UN AUTRE SERVICE. Confirmation d'inscription, réinitialisation de
mot de passe, invitation : leurs liens étaient écrits en dur vers
`https://conseilprev.onrender.com`. Un jeton n'existe QUE dans la base du
service qui l'a émis. Le nouveau client confirmait donc son adresse — et son
compte restait inactif. Celui qui avait oublié son mot de passe ne pouvait pas
le changer. Deux parcours morts de bout en bout, sans qu'aucune page cesse de
s'afficher.

DEUXIÈME DÉFAUT : UN INCONNU ÉCRIVAIT DANS LA BOÎTE DE L'ADMINISTRATEUR. Le nom
d'entreprise est choisi librement à l'inscription et était recopié tel quel dans
le HTML de la notification envoyée à CONSEILPREV. S'inscrire sous le nom
`Societe <a href="…">Cliquez ici pour valider le compte</a>` suffisait à faire
arriver un lien de son choix, cliquable, avec l'expéditeur et la mise en page du
site. Vérifié sur pièces avant correction.

TROISIÈME DÉFAUT : CHANGER SON MOT DE PASSE NE FERMAIT AUCUNE SESSION. Le cookie
de Flask est signé, pas stocké : rien ne permettait d'en révoquer un, et il vit
trente jours. Or c'est exactement le geste que les deux courriers d'alerte
demandent au client de faire quand il ne reconnaît pas une connexion. L'intrus
gardait l'accès jusqu'à trente jours — après l'incident, et après l'alerte.

QUATRIÈME DÉFAUT : UNE PANNE DE BASE ANNONÇAIT « CET EMAIL EST DÉJÀ UTILISÉ ».
La connexion à la base était ouverte AVANT le `try`, donc une base injoignable
produisait une erreur 500 avec sa trace, sur la page la plus exposée du site ; et
à l'intérieur, toute défaillance était rapportée comme un doublon — un visiteur
apprenait qu'il possédait déjà un compte, et allait en demander la
réinitialisation.

CE QUE CES CONTRÔLES NE PEUVENT PAS FAIRE. Vérifier qu'un courrier part vraiment :
il n'y a ni Brevo ni SMTP ici. Ils interceptent l'envoi et regardent CE QUI
AURAIT ÉTÉ ENVOYÉ — destinataire, sujet, liens. C'est ce qui a permis de trouver
les deux premiers défauts, et c'est aussi la limite : une clé d'API absente en
production ne se verrait pas ici.
"""
import ast
import io
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-inscription')

import app as application  # noqa: E402
import seo  # noqa: E402

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
ARBRE = ast.parse(SOURCE)

_N = [300]


def _ent():
    _N[0] += 1
    return {'X-Forwarded-For': '198.51.100.%d' % (_N[0] % 250 + 1),
            'User-Agent': 'Mozilla/5.0 (recette)',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept': 'application/json'}


def _corps(nom):
    for n in ast.walk(ARBRE):
        if isinstance(n, ast.FunctionDef) and n.name == nom:
            return ast.unparse(n)
    raise AssertionError('fonction %s introuvable' % nom)


@pytest.fixture
def courriers(monkeypatch):
    """Intercepte les envois et rend la liste de ce qui serait parti."""
    boite = []

    def _capture(to_email, to_name, subject, html, reply_to=None, tags=None):
        boite.append({'a': to_email, 'nom': to_name, 'sujet': subject,
                      'html': html, 'tags': tags or []})
        return True, 'capture'
    monkeypatch.setattr(application, 'send_email_smart', _capture)
    return boite


def _liens(courrier):
    return re.findall(r'href="([^"]+)"', courrier['html'])


@pytest.fixture
def inscrire(courriers):
    """Inscrit un client et rend (email, mot de passe, jeton, courriers)."""
    faits = []

    def _faire(nom='Entreprise Recette', email=None, mdp='Recette2026!ok'):
        email = email or 'recette%d@exemple-test.fr' % (_N[0] + len(faits))
        conn = application.registre_get_db(); cur = conn.cursor()
        cur.execute(application.registre_sql(
            'DELETE FROM clients WHERE email=%s',
            'DELETE FROM clients WHERE email=?'), (email,))
        conn.commit(); conn.close()
        c = application.app.test_client()
        q = c.get('/api/sentinel-auth/register-captcha',
                  headers=_ent()).get_json()['captcha_question']
        a, b = [int(x) for x in re.findall(r'\d+', q)]
        r = c.post('/api/sentinel-auth/register', headers=_ent(), json={
            'nom_entreprise': nom, 'email': email, 'password': mdp,
            'rgpd_consent': True, 'captcha_answer': a + b})
        conn = application.registre_get_db(); cur = conn.cursor()
        cur.execute(application.registre_sql(
            'SELECT verify_email_token FROM clients WHERE email=%s',
            'SELECT verify_email_token FROM clients WHERE email=?'), (email,))
        ligne = cur.fetchone(); conn.close()
        jeton = (dict(ligne) if ligne else {}).get('verify_email_token')
        faits.append(email)
        return {'email': email, 'mdp': mdp, 'jeton': jeton, 'reponse': r}
    yield _faire
    conn = application.registre_get_db(); cur = conn.cursor()
    for e in faits:
        cur.execute(application.registre_sql(
            'DELETE FROM clients WHERE email=%s',
            'DELETE FROM clients WHERE email=?'), (e,))
    conn.commit(); conn.close()


# ── LES TROIS COURRIERS QUI PORTENT UN JETON ─────────────────────────────

JETONS = ['sentauth_send_verification_email', 'sentauth_send_reset_email',
          'sentauth_send_invitation_email']


@pytest.mark.parametrize('fonction', JETONS)
def test_aucun_lien_a_jeton_nest_ecrit_en_dur(fonction):
    """LE DÉFAUT. Un jeton n'existe que dans la base du service qui l'a émis :
    un lien qui en désigne un autre ne mène nulle part, et le compte du nouveau
    client reste inactif pour toujours."""
    corps = _corps(fonction)
    assert 'onrender.com' not in corps, (
        "%s écrit une adresse de service en dur : le jour où le service "
        "déménage, le parcours meurt en silence" % fonction)
    assert 'lien_du_site(' in corps


@pytest.mark.parametrize('fonction', JETONS)
def test_aucun_lien_a_jeton_ne_vient_de_la_requete(fonction):
    """`request.host` vient d'un en-tête envoyé par le client. S'en servir
    laisse n'importe qui se faire adresser un lien de réinitialisation pointant
    vers son propre serveur — l'empoisonnement de réinitialisation."""
    corps = _corps(fonction)
    for interdit in ('request.host', 'request.url_root', 'Host', 'url_for('):
        assert interdit not in corps, (
            "%s construit son lien à partir de la requête (« %s ») : l'adresse "
            "devient dictée par le visiteur" % (fonction, interdit))


def test_le_lien_suit_ladresse_courante(monkeypatch):
    monkeypatch.setattr(seo, 'BASE', 'https://i-aes.eu')
    assert application.lien_du_site('verify-email/JETON') == \
        'https://i-aes.eu/verify-email/JETON'
    assert application.lien_du_site('/verify-email/JETON') == \
        'https://i-aes.eu/verify-email/JETON'


@pytest.mark.parametrize('variables,attendu', [
    ({'SITE_BASE_URL': 'https://i-aes.eu'}, 'https://i-aes.eu'),
    ({'BASE_URL': 'https://ancien.example'}, 'https://ancien.example'),
    # `SITE_BASE_URL` l'emporte : deux variables pour une seule chose finiraient
    # sinon par se contredire sans qu'on sache laquelle fait foi.
    ({'SITE_BASE_URL': 'https://i-aes.eu',
      'BASE_URL': 'https://ancien.example'}, 'https://i-aes.eu'),
    # Une adresse saisie à la main dans un tableau de bord oublie souvent le
    # schéma : sans complétion, toutes les canoniques deviendraient relatives.
    ({'SITE_BASE_URL': 'i-aes.eu'}, 'https://i-aes.eu'),
    ({'SITE_BASE_URL': 'https://i-aes.eu/'}, 'https://i-aes.eu'),
    ({}, None),                       # aucune variable : la valeur par défaut
])
def test_ladresse_est_bien_derivee_des_variables(monkeypatch, variables, attendu):
    """LE CONTRÔLE PRÉCÉDENT NE REGARDE PAS LA DÉRIVATION. Il remplace `BASE`
    directement, donc il passerait même si `BASE` cessait de lire
    l'environnement — une mutation l'a montré. On relit ici le module."""
    import importlib
    for v in ('SITE_BASE_URL', 'BASE_URL'):
        monkeypatch.delenv(v, raising=False)
    for k, v in variables.items():
        monkeypatch.setenv(k, v)
    recharge = importlib.reload(seo)
    try:
        assert recharge.BASE == (attendu or recharge.BASE_PAR_DEFAUT)
    finally:
        for v in ('SITE_BASE_URL', 'BASE_URL'):
            monkeypatch.delenv(v, raising=False)
        importlib.reload(seo)


@pytest.mark.parametrize('fonction,fragment', [
    ('sentauth_send_verification_email', '/verify-email/'),
    ('sentauth_send_reset_email', '/reset-password/'),
    ('sentauth_send_invitation_email', '/invitation/'),
])
def test_le_lien_du_courrier_ignore_len_tete_host(courriers, monkeypatch,
                                                  fonction, fragment):
    """LE CONTRÔLE QUI COMPTE : on FORGE l'en-tête `Host` et on regarde le lien.

    On appelle le constructeur de courrier dans un contexte de requête dont
    l'hôte est celui de l'attaquant, plutôt que de rejouer l'inscription
    entière : le formulaire porte un captcha lié à la session, et changer
    d'origine en cours de route ferait échouer l'inscription avant l'envoi —
    le contrôle passerait alors pour une raison qui n'est pas la sienne."""
    monkeypatch.setattr(seo, 'BASE', 'https://i-aes.eu')
    envoyer = getattr(application, fonction)
    with application.app.test_request_context(
            '/', base_url='http://serveur-de-lattaquant.test'):
        envoyer('client@exemple-test.fr', 'Entreprise', 'JETON-DE-RECETTE')
    liens = [l for m in courriers for l in _liens(m) if fragment in l]
    assert liens, "aucun lien de %s" % fonction
    for l in liens:
        assert l.startswith('https://i-aes.eu/'), l
        assert 'attaquant' not in l


def test_labsence_dadresse_configuree_est_annoncee():
    """Une valeur par défaut qui désigne un service qu'on a quitté ne se voit
    pas : tout démarre, et seul le nouveau client s'en aperçoit."""
    i = SOURCE.index("if not (os.environ.get('SITE_BASE_URL')")
    bloc = SOURCE[i:i + 900]
    assert 'logger.error' in bloc
    assert 'SITE_BASE_URL' in bloc


# ── UN JETON SUR CENT ÉTAIT PRIS POUR UNE ATTAQUE ────────────────────────

def test_la_frequence_du_faux_positif_est_bien_celle_annoncee():
    """LE CHIFFRE QUI JUSTIFIE LA CORRECTION, RECALCULÉ PLUTÔT QUE RECOPIÉ.

    `secrets.token_urlsafe` tire dans un alphabet qui contient le tiret. La
    séquence « -- » y apparaît donc régulièrement — et le filtre anti-injection
    la lit comme un début de commentaire SQL."""
    import secrets
    motif = re.compile(r"('|(%27)|(--)|(%23)|(#))")
    n = 20000
    touches = sum(1 for _ in range(n) if motif.search(secrets.token_urlsafe(32)))
    part = 100.0 * touches / n
    assert 0.4 < part < 2.5, (
        "un jeton sur %.0f contiendrait un motif « injection » — le chiffre "
        "annoncé (environ 1 %%) n'est plus le bon" % (100 / max(part, 0.01)))


@pytest.mark.parametrize('chemin', [
    '/auth/', '/verify-email/', '/reset-password/', '/invitation/'])
def test_un_jeton_contenant_deux_tirets_nest_pas_pris_pour_une_attaque(chemin):
    """LE DÉFAUT. Le client cliquait sur son lien, recevait un 403, et son IP
    était bloquée une heure pour tentative d'injection : il ne pouvait plus ni
    activer son compte, ni redemander un lien, ni revenir sur le site. Côté
    journal, il apparaissait comme un attaquant.

    On n'attend pas 200 — le jeton est faux, donc 404 ou une redirection sont
    des réponses justes. On refuse SEULEMENT le 403 du filtre, et le blocage
    d'IP qui l'accompagne."""
    faux = 'aZ--bY_9' + 'x' * 30
    r = application.app.test_client().get(chemin + faux, headers=_ent())
    assert r.status_code != 403, (
        "%s%s : bloqué comme une injection alors que le jeton vient du serveur"
        % (chemin, faux))


def test_un_chemin_a_saisie_libre_reste_protege():
    """L'exemption ne doit pas s'étendre : elle ne vaut que pour des chemins qui
    ne portent RIEN d'autre qu'un jeton produit par le serveur."""
    r = application.app.test_client().get(
        "/api/registre?q=' OR 1=1--", headers=_ent())
    assert r.status_code == 403, (
        "le filtre anti-injection ne s'applique plus aux chemins à saisie libre")


# ── CE QU'UN INCONNU PEUT ÉCRIRE À L'ADMINISTRATEUR ──────────────────────

def test_un_inscrit_ne_place_aucun_lien_dans_les_courriers(inscrire, courriers):
    """LE DÉFAUT, VÉRIFIÉ SUR PIÈCES AVANT CORRECTION : le lien saisi arrivait
    cliquable dans la boîte de CONSEILPREV, porté par l'expéditeur du site."""
    piege = ('Societe <a href="https://exemple-hameconnage.test/verifier">'
             'Cliquez ici pour valider le compte</a>')
    inscrire(nom=piege, email='piege@exemple-test.fr')
    assert courriers, "aucun courrier"
    for m in courriers:
        for l in _liens(m):
            assert 'exemple-hameconnage.test' not in l, (
                "un lien choisi par l'inscrit est cliquable dans le courrier "
                "à %s" % m['a'])


def test_le_nom_saisi_reste_lisible_mais_inerte(inscrire, courriers):
    """On échappe, on ne supprime pas : l'administrateur doit VOIR sous quel
    nom la personne s'est inscrite, y compris si ce nom est douteux."""
    inscrire(nom='Dupont & Fils <SARL>', email='dupont@exemple-test.fr')
    admin = [m for m in courriers if m['a'] == application.CONSEILPREV_NOTIFY_EMAIL]
    assert admin, "l'administrateur n'a rien reçu"
    assert '&lt;SARL&gt;' in admin[0]['html'] or '&amp;' in admin[0]['html']


def test_ladresse_du_destinataire_nest_jamais_echappee(inscrire, courriers):
    """Échapper une adresse de destinataire la rendrait indélivrable : seul ce
    qui entre dans le CORPS est échappé."""
    d = inscrire(email='client+etiquette@exemple-test.fr')
    dest = [m['a'] for m in courriers]
    assert d['email'] in dest, dest
    for a in dest:
        assert '&' not in a or '&amp;' not in a


# ── LES NOTIFICATIONS ────────────────────────────────────────────────────

def test_linscription_notifie_le_client_et_ladministrateur(inscrire, courriers):
    d = inscrire()
    dest = [m['a'] for m in courriers]
    assert d['email'] in dest, "le nouveau client n'est pas prévenu"
    assert application.CONSEILPREV_NOTIFY_EMAIL in dest, (
        "CONSEILPREV n'est pas prévenu d'une nouvelle inscription")


def test_ladministrateur_par_defaut_est_bien_celui_attendu():
    assert application.CONSEILPREV_NOTIFY_EMAIL == 'christophe.cerf@outlook.com'


def test_la_notification_a_ladministrateur_porte_un_chemin_pour_agir(inscrire, courriers):
    """Elle demandait de se connecter « à Sentinel AI » sans dire où, alors que
    la consigne est d'aller désactiver un compte sans tarder."""
    inscrire()
    admin = [m for m in courriers if m['a'] == application.CONSEILPREV_NOTIFY_EMAIL]
    assert admin
    assert any('/sentinel' in l for l in _liens(admin[0])), _liens(admin[0])


def test_une_connexion_reussie_alerte_le_titulaire(inscrire, courriers):
    import time
    d = inscrire()
    application.app.test_client().get('/verify-email/%s' % d['jeton'], headers=_ent())
    avant = len(courriers)
    application.app.test_client().post(
        '/api/sentinel-auth/login', headers=_ent(),
        json={'email': d['email'], 'password': d['mdp']})
    for _ in range(60):
        if len(courriers) > avant:
            break
        time.sleep(0.05)
    nouveaux = [m for m in courriers[avant:] if m['a'] == d['email']]
    assert nouveaux, "aucune alerte de connexion envoyée au titulaire"


def test_le_courrier_de_confirmation_annonce_la_bonne_duree():
    """Il citait la durée de l'INVITATION alors que le jeton expire selon la
    durée de VÉRIFICATION. Les deux valent 48 h aujourd'hui — la phrase est donc
    juste par coïncidence, et cesserait de l'être au premier réglage."""
    corps = _corps('sentauth_send_verification_email')
    assert 'VERIFY_EMAIL_VALIDITY_HOURS' in corps
    assert 'INVITATION_VALIDITY_HOURS' not in corps


# ── L'ACCÈS, AVANT ET APRÈS CONFIRMATION ─────────────────────────────────

def test_un_compte_non_confirme_nouvre_rien(inscrire):
    d = inscrire()
    c = application.app.test_client()
    r = c.post('/api/sentinel-auth/login', headers=_ent(),
               json={'email': d['email'], 'password': d['mdp']})
    assert r.status_code == 403, r.status_code
    assert c.get('/sentinel', headers=_ent()).status_code == 302
    assert c.get('/api/registre', headers=_ent()).status_code == 401


def test_le_statut_du_compte_nest_revele_quapres_le_mot_de_passe(inscrire):
    """ANTI-ÉNUMÉRATION. « Compte non activé » renseigne sur l'existence d'un
    compte : il ne doit sortir que pour quelqu'un qui connaît déjà le mot de
    passe."""
    d = inscrire()
    r = application.app.test_client().post(
        '/api/sentinel-auth/login', headers=_ent(),
        json={'email': d['email'], 'password': 'MauvaisMotDePasse1!'})
    assert r.status_code == 401
    assert 'activ' not in (r.get_json() or {}).get('error', '').lower()


def test_la_confirmation_ouvre_lacces(inscrire):
    d = inscrire()
    r = application.app.test_client().get('/verify-email/%s' % d['jeton'], headers=_ent())
    assert r.status_code == 302 and 'verified=1' in (r.headers.get('Location') or '')
    c = application.app.test_client()
    r = c.post('/api/sentinel-auth/login', headers=_ent(),
               json={'email': d['email'], 'password': d['mdp']})
    assert r.status_code == 200, r.get_json()
    assert c.get('/sentinel', headers=_ent()).status_code == 200


def test_le_plan_demande_par_linscrit_nest_jamais_enregistre(inscrire):
    """LE CLOISONNEMENT EST POSÉ DEUX FOIS, ET LE CONTRÔLE SUIVANT NE VOYAIT QUE
    LA SECONDE. `sentauth_current_client` reforce « gratuit » à la lecture ; une
    mutation qui faisait entrer le plan du formulaire jusque dans la BASE
    survivait donc, alors que la ligne enregistrée était fausse. On regarde ici
    ce qui est ÉCRIT, pas seulement ce qui est rendu."""
    email = 'plan.demande@exemple-test.fr'
    conn = application.registre_get_db(); cur = conn.cursor()
    cur.execute(application.registre_sql('DELETE FROM clients WHERE email=%s',
                                         'DELETE FROM clients WHERE email=?'), (email,))
    conn.commit(); conn.close()
    c = application.app.test_client()
    q = c.get('/api/sentinel-auth/register-captcha',
              headers=_ent()).get_json()['captcha_question']
    a, b = [int(x) for x in re.findall(r'\d+', q)]
    c.post('/api/sentinel-auth/register', headers=_ent(), json={
        'nom_entreprise': 'Ambitieuse', 'email': email,
        'password': 'Recette2026!ok', 'rgpd_consent': True,
        'captcha_answer': a + b, 'plan': 'entreprise'})
    conn = application.registre_get_db(); cur = conn.cursor()
    cur.execute(application.registre_sql('SELECT plan FROM clients WHERE email=%s',
                                         'SELECT plan FROM clients WHERE email=?'), (email,))
    ligne = cur.fetchone()
    plan = dict(ligne)['plan'] if ligne else None
    cur.execute(application.registre_sql('DELETE FROM clients WHERE email=%s',
                                         'DELETE FROM clients WHERE email=?'), (email,))
    conn.commit(); conn.close()
    assert plan == 'gratuit', (
        "le plan demandé dans le formulaire est enregistré tel quel : « %s »" % plan)


def test_une_inscription_publique_reste_au_plan_gratuit(inscrire):
    """Le cloisonnement des plans : s'inscrire n'ouvre ni le registre, ni la
    gestion des clients, ni le RGPD du site."""
    d = inscrire()
    application.app.test_client().get('/verify-email/%s' % d['jeton'], headers=_ent())
    c = application.app.test_client()
    c.post('/api/sentinel-auth/login', headers=_ent(),
           json={'email': d['email'], 'password': d['mdp']})
    assert c.get('/api/sentinel-auth/me', headers=_ent()).get_json()['plan'] == 'gratuit'
    for route in ('/api/registre', '/api/admin/clients', '/api/rgpd/consentements'):
        assert c.get(route, headers=_ent()).status_code == 403, route


# ── CHANGER SON MOT DE PASSE FERME LES AUTRES SESSIONS ───────────────────

def _reinitialiser(email, nouveau):
    c = application.app.test_client()
    c.post('/api/sentinel-auth/forgot-password', headers=_ent(), json={'email': email})
    conn = application.registre_get_db(); cur = conn.cursor()
    cur.execute(application.registre_sql(
        'SELECT reset_token FROM clients WHERE email=%s',
        'SELECT reset_token FROM clients WHERE email=?'), (email,))
    jeton = dict(cur.fetchone())['reset_token']; conn.close()
    info = c.get('/api/sentinel-auth/reset-password-info/%s' % jeton,
                 headers=_ent()).get_json()
    a, b = [int(x) for x in re.findall(r'\d+', info['captcha_question'])]
    return c.post('/api/sentinel-auth/reset-password', headers=_ent(),
                  json={'token': jeton, 'password': nouveau, 'captcha_answer': a + b})


def test_un_changement_de_mot_de_passe_coupe_les_sessions_ouvertes(inscrire, courriers):
    """LE DÉFAUT. C'est le geste que les deux courriers d'alerte demandent au
    client de faire. Il ne fermait rien : l'intrus gardait l'accès jusqu'à
    trente jours, après l'incident et après l'alerte."""
    d = inscrire()
    application.app.test_client().get('/verify-email/%s' % d['jeton'], headers=_ent())
    intrus = application.app.test_client()
    assert intrus.post('/api/sentinel-auth/login', headers=_ent(),
                       json={'email': d['email'], 'password': d['mdp']}).status_code == 200
    assert intrus.get('/sentinel', headers=_ent()).status_code == 200

    assert _reinitialiser(d['email'], 'Nouveau2026!ok').status_code == 200

    assert intrus.get('/sentinel', headers=_ent()).status_code == 302, (
        "la session de l'intrus survit au changement de mot de passe")
    assert intrus.get('/api/sentinel-auth/me',
                      headers=_ent()).get_json()['authenticated'] is False


def test_le_titulaire_se_reconnecte_avec_le_nouveau_mot_de_passe(inscrire, courriers):
    d = inscrire()
    application.app.test_client().get('/verify-email/%s' % d['jeton'], headers=_ent())
    _reinitialiser(d['email'], 'Nouveau2026!ok')
    c = application.app.test_client()
    assert c.post('/api/sentinel-auth/login', headers=_ent(),
                  json={'email': d['email'], 'password': 'Nouveau2026!ok'}).status_code == 200
    assert c.get('/sentinel', headers=_ent()).status_code == 200


def test_la_mise_en_ligne_ne_deconnecte_personne(inscrire):
    """Un cookie antérieur à cette mise en ligne ne porte aucun numéro. Il doit
    être lu comme la génération des comptes existants — sinon le déploiement
    déconnecte tout le monde, ce qui n'apporte aucune sécurité et se voit."""
    d = inscrire()
    application.app.test_client().get('/verify-email/%s' % d['jeton'], headers=_ent())
    conn = application.registre_get_db(); cur = conn.cursor()
    cur.execute(application.registre_sql(
        'SELECT id, generation_session FROM clients WHERE email=%s',
        'SELECT id, generation_session FROM clients WHERE email=?'), (d['email'],))
    ligne = dict(cur.fetchone()); conn.close()
    assert (ligne['generation_session'] or 0) == 0
    vieux = application.app.test_client()
    with vieux.session_transaction() as s:
        s['client_id'] = ligne['id']          # cookie d'avant : pas de 'sgen'
    assert vieux.get('/sentinel', headers=_ent()).status_code == 200


def test_la_connexion_inscrit_la_generation_dans_la_session():
    corps = _corps('sentauth_login')
    assert "session['sgen']" in corps


# ── CE QUE VOIT UN VISITEUR QUAND LA BASE EST EN PANNE ───────────────────

def test_une_base_injoignable_ne_dit_pas_que_le_compte_existe(monkeypatch):
    """LE DÉFAUT. Le visiteur apprenait qu'il possédait déjà un compte alors
    que la base était tombée — et allait en demander la réinitialisation."""
    c = application.app.test_client()
    q = c.get('/api/sentinel-auth/register-captcha',
              headers=_ent()).get_json()['captcha_question']
    a, b = [int(x) for x in re.findall(r'\d+', q)]

    def _panne():
        raise RuntimeError('base injoignable')
    monkeypatch.setattr(application, 'registre_get_db', _panne)
    r = c.post('/api/sentinel-auth/register', headers=_ent(), json={
        'nom_entreprise': 'Panne', 'email': 'panne@exemple-test.fr',
        'password': 'Recette2026!ok', 'rgpd_consent': True, 'captcha_answer': a + b})
    assert r.status_code == 503, r.status_code
    msg = (r.get_json() or {}).get('error', '')
    assert 'déjà utilisé' not in msg, msg


def test_une_panne_pendant_lecriture_nest_pas_non_plus_un_doublon(monkeypatch):
    """DEUX PANNES DIFFÉRENTES, ET LE CONTRÔLE PRÉCÉDENT N'EN VOYAIT QU'UNE.
    Il coupe la base AVANT l'ouverture de connexion ; la branche qui répondait
    « cet email est déjà utilisé » à toute défaillance se trouve APRÈS, pendant
    l'écriture. Une mutation y survivait donc sans être vue."""
    c = application.app.test_client()
    q = c.get('/api/sentinel-auth/register-captcha',
              headers=_ent()).get_json()['captcha_question']
    a, b = [int(x) for x in re.findall(r'\d+', q)]

    vrai = application.registre_get_db

    class _CurseurCasse:
        def execute(self, *a, **k):
            raise RuntimeError('disque plein')

    class _ConnexionCasse:
        def cursor(self):
            return _CurseurCasse()

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(application, 'registre_get_db', lambda: _ConnexionCasse())
    try:
        r = c.post('/api/sentinel-auth/register', headers=_ent(), json={
            'nom_entreprise': 'Panne', 'email': 'panne2@exemple-test.fr',
            'password': 'Recette2026!ok', 'rgpd_consent': True,
            'captcha_answer': a + b})
    finally:
        monkeypatch.setattr(application, 'registre_get_db', vrai)
    assert r.status_code == 503, r.status_code
    assert 'déjà utilisé' not in (r.get_json() or {}).get('error', '')


def test_un_doublon_reste_annonce_comme_un_doublon(inscrire):
    """L'inverse serait aussi trompeur : quelqu'un qui a réellement un compte
    doit l'apprendre, sinon il réessaiera sans comprendre."""
    d = inscrire()
    c = application.app.test_client()
    q = c.get('/api/sentinel-auth/register-captcha',
              headers=_ent()).get_json()['captcha_question']
    a, b = [int(x) for x in re.findall(r'\d+', q)]
    r = c.post('/api/sentinel-auth/register', headers=_ent(), json={
        'nom_entreprise': 'Doublon', 'email': d['email'],
        'password': 'Recette2026!ok', 'rgpd_consent': True, 'captcha_answer': a + b})
    assert r.status_code == 409, r.status_code


# ── LE COOKIE DE SESSION, ET CE QUE LA PAGE RGPD EN DIT ──────────────────

@pytest.mark.parametrize('reglage,attendu', [
    ('SESSION_COOKIE_SECURE', True),
    ('SESSION_COOKIE_HTTPONLY', True),
    ('SESSION_COOKIE_SAMESITE', 'Lax'),
])
def test_le_cookie_de_session_est_protege(reglage, attendu):
    assert application.app.config.get(reglage) == attendu


def test_le_constat_rgpd_verifie_ce_quil_annonce():
    """LE DÉFAUT. La variable s'appelait `cookie_secure` et lisait
    `SESSION_COOKIE_HTTPONLY` : couper `Secure` — le seul réglage qui empêche le
    cookie de partir en clair — n'aurait rien changé au verdict « conforme »."""
    i = SOURCE.index("_cookie = {")
    bloc = SOURCE[i:i + 500]
    for reglage in ('SESSION_COOKIE_SECURE', 'SESSION_COOKIE_HTTPONLY',
                    'SESSION_COOKIE_SAMESITE'):
        assert reglage in bloc, (
            "le constat article 25 ne vérifie pas %s" % reglage)
