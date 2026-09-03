# -*- coding: utf-8 -*-
"""LE SECOND ESPACE CLIENT — celui de /sourcing, qui n'avait aucune règle.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande de vérification des inscriptions et
des connexions des espaces clients, sur les deux sites. Le parcours de /login a
été joué il y a peu et tient (voir `test_inscription_et_connexion.py`, 31
règles). Ce site en porte un SECOND, sur /sourcing, avec ses propres routes
`/api/auth/*`, son propre magasin, son propre mot de passe — et pas une règle.
Il a donc été joué à son tour, contre l'application qui tourne.

DEUX ESPACES CLIENTS SUR UN SITE, C'EST UN ESPACE QUI POURRIT SANS TÉMOIN.
C'est ce que la mesure montre : celui qui est éprouvé va bien, celui qui ne
l'est pas portait quatre défauts dont aucun ne se voit sur une page.

PREMIER DÉFAUT — UNE INSCRIPTION EN ATTENTE APPARTENAIT AU DERNIER VENU. La
garde ne regardait que les comptes CONFIRMÉS : `if email in users and
users[email].get('verified')`. Une adresse inscrite mais pas encore confirmée
retombait dans le chemin de création et se faisait écraser. Joué : Alice
s'inscrit, ne clique pas tout de suite ; un inconnu réinscrit son adresse ;
prénom « Alice » devient « Mallory », l'empreinte du mot de passe est
remplacée, et le jeton d'Alice est périmé. Alice clique SON lien et lit « Lien
invalide ou expiré » — sans que rien n'ait échoué de son côté.

DEUXIÈME DÉFAUT — LE JETON DE CONFIRMATION REVENAIT DANS LA RÉPONSE. Sous le
nom `_dev_link`, « affiché si SMTP non configuré », et la page en faisait un
lien cliquable. Une commodité de développement qui se retourne en production le
jour où l'envoi tombe : confirmer une adresse ne prouve plus rien si le serveur
rend le jeton à celui qui vient de la saisir. Le déclencheur n'est pas une
attaque — une clé Brevo expirée suffit.

TROISIÈME DÉFAUT — LE MAGASIN NE SURVIT PAS À UNE MISE EN LIGNE, ET SE TAISAIT.
Les comptes vivent dans `users_db.json`, à la racine du service : ni versionné
(il est dans `.gitignore`), ni monté sur un disque (aucun n'est déclaré dans
`render.yaml`). Render remplace ce disque à chaque déploiement. Le registre,
lui, CRIE déjà quand il retombe sur SQLite ; le même défaut, sur le même
service, restait muet ici.

QUATRIÈME DÉFAUT — « ÊTRE CONNECTÉ » N'ÉTAIT PAS UNE AUTORISATION, sans que
personne le dise. `user['session']` n'est relu par aucune route ; `cp_token`,
que la page range dans sessionStorage, n'est renvoyé dans aucune requête. La
route admin le déclarait depuis sa correction ; la route cliente, qui fait
exactement la même chose, ne le disait pas.

CE QUE CES RÈGLES NE FONT PAS. Elles ne tranchent pas la question de fond —
faut-il deux espaces clients sur ce site ? Elles la rendent seulement
impossible à oublier : le magasin éphémère s'annonce, et le jeton qui n'ouvre
rien est éprouvé comme n'ouvrant rien.
"""

import ast
import io
import json
import logging
import os
import re
import subprocess
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-sourcing')

import app as application  # noqa: E402

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
ARBRE = ast.parse(SOURCE)

_N = [500]


def _ent():
    _N[0] += 1
    return {'X-Forwarded-For': '203.0.113.%d' % (_N[0] % 240 + 2),
            'User-Agent': 'Mozilla/5.0 (recette)',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept-Encoding': 'gzip',
            'Accept': 'application/json'}


@pytest.fixture
def magasin(monkeypatch):
    """Un magasin de comptes propre, en mémoire, rendu à la fin.

    En MÉMOIRE et pas sur disque : ces essais créent des comptes, et le fichier
    réel est celui du poste. Aucune règle ne doit laisser un compte derrière
    elle."""
    comptes = {}
    monkeypatch.setattr(application, '_load_users', lambda: comptes)
    monkeypatch.setattr(application, '_save_users',
                        lambda u: comptes.update(u) or True)
    return comptes


@pytest.fixture
def courriers(monkeypatch):
    """Ce qui SERAIT parti : destinataire, et le lien qu'il porte."""
    boite = []

    def _envoi(email, prenom, token):
        lien = application.lien_du_site(
            'api/auth/verify?token=%s&email=%s' % (token, email))
        boite.append({'a': email, 'jeton': token, 'lien': lien})
        return True, lien
    monkeypatch.setattr(application, 'send_validation_email', _envoi)
    return boite


def _inscrire(c, email, mdp='Recette2026!ok', prenom='Alice',
              nom='Martin', entreprise='Alpha'):
    return c.post('/api/auth/register', headers=_ent(), json={
        'email': email, 'password': mdp, 'prenom': prenom, 'nom': nom,
        'entreprise': entreprise, 'consent': True})


def _corps(nom):
    for n in ast.walk(ARBRE):
        if isinstance(n, ast.FunctionDef) and n.name == nom:
            return ast.unparse(n)
    raise AssertionError('fonction %s introuvable' % nom)


# ═══════════════════════════════════════════════════════════════════════════
#  L'INSCRIPTION EN ATTENTE APPARTIENT À CELUI QUI L'A FAITE
# ═══════════════════════════════════════════════════════════════════════════

def test_un_tiers_ne_reprend_pas_une_inscription_en_attente(magasin, courriers):
    """LE PARCOURS D'ALICE, JOUÉ EN ENTIER — c'est la seule façon de voir ce
    défaut, qui ne se manifeste sur aucune page.

    La règle éprouve les QUATRE choses qu'un tiers pouvait emporter : le nom,
    l'empreinte du mot de passe, le jeton d'Alice, et in fine l'accès."""
    c = application.app.test_client()
    m = 'alice@example.invalid'
    assert _inscrire(c, m, 'Alice2026!ok', 'Alice', 'Martin', 'Alpha').status_code == 200
    avant = dict(magasin[m])

    r = _inscrire(c, m, 'Mallory2026!ok', 'Mallory', 'Inconnu', 'Beta')
    assert r.status_code == 200, r.get_json()
    apres = magasin[m]
    assert apres['prenom'] == 'Alice', "le nom d'Alice a été remplacé"
    assert apres['entreprise'] == 'Alpha'
    assert apres['password'] == avant['password'], (
        "le mot de passe d'Alice a été remplacé par celui d'un tiers")
    assert apres['verify_token'] == avant['verify_token'], (
        "le lien de confirmation d'Alice a été périmé par un tiers")

    # Et le parcours d'Alice va jusqu'au bout, celui de Mallory nulle part.
    c.get('/api/auth/verify?email=%s&token=%s' % (m, avant['verify_token']),
          headers=_ent())
    assert magasin[m].get('verified') is True
    assert c.post('/api/auth/login', headers=_ent(),
                  json={'email': m, 'password': 'Alice2026!ok'}).status_code == 200
    assert c.post('/api/auth/login', headers=_ent(),
                  json={'email': m, 'password': 'Mallory2026!ok'}).status_code == 401


def test_la_relance_part_a_ladresse_inscrite_et_porte_le_jeton_dorigine(
        magasin, courriers):
    """POURQUOI CE N'EST PAS UN REFUS SEC. Celui qui réinscrit son adresse est,
    presque toujours, celui qui n'a pas reçu le courrier : on lui renvoie le
    lien. Le tiers, lui, n'obtient rien — le courrier part à L'ADRESSE
    INSCRITE, et porte le jeton d'origine, pas un neuf."""
    c = application.app.test_client()
    m = 'relance@example.invalid'
    _inscrire(c, m)
    jeton = magasin[m]['verify_token']
    courriers.clear()

    # LA SECONDE DEMANDE ÉCRIT L'ADRESSE AUTREMENT — c'est ce qui sépare
    # « l'adresse inscrite » de « ce que la requête raconte ». Les deux
    # coïncidaient dans la première version de cette règle, et une relance
    # qui aurait suivi la saisie brute serait passée inaperçue.
    _inscrire(c, m.upper(), prenom='Tiers')
    assert len(courriers) == 1, courriers
    assert courriers[0]['a'] == m, (
        "le courrier suit la saisie (%r) au lieu de l'adresse inscrite (%r)"
        % (courriers[0]['a'], m))
    assert courriers[0]['jeton'] == jeton, (
        "la relance a frappé un jeton neuf : le lien déjà reçu serait mort")


def test_un_compte_confirme_reste_un_doublon_annonce(magasin, courriers):
    """L'arbitrage de l'autre espace client de ce site, tenu ici aussi : qui a
    réellement un compte doit l'apprendre, sinon il réessaiera sans
    comprendre."""
    c = application.app.test_client()
    m = 'confirme@example.invalid'
    _inscrire(c, m)
    c.get('/api/auth/verify?email=%s&token=%s' % (m, magasin[m]['verify_token']),
          headers=_ent())
    r = _inscrire(c, m, prenom='Tiers')
    assert r.status_code == 409, r.status_code


# ═══════════════════════════════════════════════════════════════════════════
#  LE JETON DE CONFIRMATION NE REVIENT JAMAIS AU DEMANDEUR
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize('part', [True, False])
def test_le_jeton_de_confirmation_ne_revient_pas_dans_la_reponse(
        magasin, monkeypatch, part):
    """LES DEUX BRANCHES, PAS SEULEMENT CELLE QUI MARCHE. Le défaut vivait
    précisément dans la branche d'échec — celle qu'on n'exerce jamais."""
    lien = [None]

    def _envoi(email, prenom, token):
        lien[0] = application.lien_du_site(
            'api/auth/verify?token=%s&email=%s' % (token, email))
        return part, lien[0]
    monkeypatch.setattr(application, 'send_validation_email', _envoi)

    c = application.app.test_client()
    m = 'jeton@example.invalid'
    r = _inscrire(c, m)
    corps = r.get_data(as_text=True)
    jeton = magasin[m]['verify_token']
    assert jeton not in corps, "le jeton de confirmation est rendu au demandeur"
    assert lien[0] not in corps
    assert 'api/auth/verify' not in corps
    assert '_dev_link' not in corps


def test_quand_le_courrier_ne_part_pas_le_refus_dit_quoi_faire(
        magasin, monkeypatch):
    """UN MESSAGE QUI CONSTATE UNE PANNE SANS DIRE QUOI FAIRE LAISSE LE
    VISITEUR SE RÉINSCRIRE EN BOUCLE — et chaque tour lui redit la même chose.
    La réponse doit nommer un geste que le visiteur peut faire."""
    monkeypatch.setattr(application, 'send_validation_email',
                        lambda e, p, t: (False, 'x'))
    c = application.app.test_client()
    r = _inscrire(c, 'panne@example.invalid')
    msg = (r.get_json() or {}).get('message', '')
    assert r.get_json().get('email_sent') is False
    assert '@' in msg, "le message n'indique à qui écrire : %r" % msg
    assert re.search(r'inutile|ne (?:vous )?r[ée]inscri', msg, re.I), (
        "le message ne dit pas d'arrêter de réessayer : %r" % msg)


# ═══════════════════════════════════════════════════════════════════════════
#  CE QUE LA CONNEXION RÉVÈLE, ET CE QU'ELLE OUVRE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_connexion_ne_dit_pas_si_ladresse_est_connue(magasin, courriers):
    """ANTI-ÉNUMÉRATION. Adresse inconnue et adresse connue avec un mauvais mot
    de passe doivent être INDISCERNABLES — même code, même texte."""
    c = application.app.test_client()
    m = 'connue@example.invalid'
    _inscrire(c, m)
    faux = {'password': 'MauvaisMotDePasse1!'}
    a = c.post('/api/auth/login', headers=_ent(), json=dict(email=m, **faux))
    b = c.post('/api/auth/login', headers=_ent(),
               json=dict(email='jamais-vue@example.invalid', **faux))
    assert a.status_code == b.status_code == 401
    assert a.get_json() == b.get_json(), (a.get_json(), b.get_json())


def test_le_jeton_rendu_par_la_connexion_nouvre_pas_lespace_client(
        magasin, courriers):
    """« ÊTRE CONNECTÉ » SUR /sourcing EST UN ÉTAT D'INTERFACE, PAS UNE
    AUTORISATION — et la règle l'éprouve au lieu de le lire. Le jeton rendu ne
    donne pas la session de l'espace client de ce service, qui est un cookie
    signé posé par une tout autre route."""
    c = application.app.test_client()
    m = 'jetonclient@example.invalid'
    _inscrire(c, m)
    c.get('/api/auth/verify?email=%s&token=%s' % (m, magasin[m]['verify_token']),
          headers=_ent())
    r = c.post('/api/auth/login', headers=_ent(),
               json={'email': m, 'password': 'Recette2026!ok'})
    jeton = (r.get_json() or {}).get('token')
    assert jeton, r.get_json()

    e = _ent()
    e['Authorization'] = 'Bearer ' + jeton
    r = c.get('/api/sentinel-auth/me', headers=e)
    assert (r.get_json() or {}).get('authenticated') is not True, (
        "un compte /sourcing ouvre l'espace client de /login")
    assert c.get('/api/registre', headers=e).status_code == 401


def test_aucune_route_ne_lit_le_jeton_range_par_la_connexion():
    """LA PROPRIÉTÉ, PAS LE MOT. `auth_login` écrit `user['session']` ; si un
    jour une route se met à le LIRE pour autoriser quelque chose, ce jeton
    devient une clé — et il est frappé sans être lié à une session serveur.
    Aucune lecture ailleurs que dans l'écriture elle-même."""
    ecrit = _corps('auth_login')
    assert "user['session'] = session_token" in ecrit
    lecteurs = []
    for n in ast.walk(ARBRE):
        if not isinstance(n, ast.FunctionDef) or n.name == 'auth_login':
            continue
        src = ast.unparse(n)
        if re.search(r"""\.get\(\s*['"]session['"]\s*\)|\[\s*['"]session['"]\s*\]""", src):
            lecteurs.append(n.name)
    assert not lecteurs, (
        "ce jeton est relu par %s : il autorise donc quelque chose" % lecteurs)


# ═══════════════════════════════════════════════════════════════════════════
#  UN MAGASIN QUI NE SURVIT PAS À UNE MISE EN LIGNE LE DIT
# ═══════════════════════════════════════════════════════════════════════════

def test_le_magasin_ephemere_sannonce_au_demarrage(monkeypatch, caplog):
    """LA RÈGLE EXÉCUTE L'AVERTISSEMENT au lieu de le relire : un texte présent
    dans le fichier ne prouve pas qu'il sorte."""
    monkeypatch.setattr(os.path, 'isfile', lambda p: False)
    with caplog.at_level(logging.WARNING):
        assert application._avertir_magasin_sourcing_ephemere() is True
    dit = ' '.join(r.getMessage() for r in caplog.records)
    assert 'users_db.json' in dit, dit
    assert '/login' in dit, "l'avertissement ne dit pas où sont les comptes durables"


def test_lavertissement_part_REELLEMENT_au_demarrage(tmp_path):
    """LA RÈGLE PRÉCÉDENTE APPELAIT LA FONCTION ELLE-MÊME — et restait donc
    verte quand l'appel disparaissait du module. Mesuré : la mutation qui
    retire `_avertir_magasin_sourcing_ephemere()` survit à cinq passages.
    Une fonction d'avertissement que personne n'appelle n'avertit personne.

    On importe donc le module DANS UN PROCESSUS NEUF, avec un magasin absent,
    et on regarde ce qui sort."""
    prog = (
        "import logging, sys, os\n"
        "logging.basicConfig(stream=sys.stderr, level=logging.WARNING)\n"
        "sys.path.insert(0, %r)\n"
        "os.environ.setdefault('FLASK_SECRET_KEY', 'recette-demarrage')\n"
        "import app\n"
        "assert not os.path.isfile(app.USERS_FILE)\n" % ICI)
    out = subprocess.run(
        [sys.executable, "-c", prog], capture_output=True, text=True,
        timeout=300, cwd=str(tmp_path),
        # LE MAGASIN EST DÉSIGNÉ AILLEURS, dans un dossier vide : sans cela la
        # règle dirait « conforme » ou « défaillant » selon que ce poste a déjà
        # servi le site en local. Une règle qui dépend de l'état de la machine
        # finit désactivée.
        env=dict(os.environ,
                 SOURCING_USERS_FILE=str(tmp_path / "comptes_absents.json")))
    assert out.returncode == 0, out.stderr[-2000:]
    assert "COMPTES /sourcing" in out.stderr, (
        "le module ne dit RIEN au demarrage sur un magasin qui ne survit pas "
        "a une mise en ligne :\n" + out.stderr[-2000:])


def test_le_magasin_present_ne_declenche_rien(monkeypatch, caplog):
    """LE TÉMOIN NÉGATIF. Sans lui, une fonction qui avertit TOUJOURS passerait
    la règle précédente."""
    monkeypatch.setattr(os.path, 'isfile', lambda p: True)
    with caplog.at_level(logging.WARNING):
        assert application._avertir_magasin_sourcing_ephemere() is False
    assert not [r for r in caplog.records if 'users_db' in r.getMessage()]


def test_le_magasin_de_sourcing_nest_ni_versionne_ni_monte():
    """CE QUI REND L'AVERTISSEMENT VRAI. S'il était un jour versionné ou monté
    sur un disque, l'avertissement deviendrait un mensonge — et c'est une bonne
    nouvelle qu'il faudrait alors retirer."""
    ignore = io.open(os.path.join(ICI, '.gitignore'), encoding='utf-8').read()
    rendu = io.open(os.path.join(ICI, 'render.yaml'), encoding='utf-8').read()
    assert 'users_db.json' in ignore
    assert 'mountPath' not in rendu, (
        "un disque est déclaré : vérifier si les comptes /sourcing y vivent")
