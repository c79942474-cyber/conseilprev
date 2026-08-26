"""BRANCHER i-aes.eu EN DOMAINE PROPRE — ce que le code y opposait.

POURQUOI CE FICHIER EXISTE. Aujourd'hui i-aes.eu ne SERT pas le site : il
REDIRIGE vers l'adresse `*.onrender.com`. Un visiteur paie donc deux
établissements de connexion complets — résolution DNS, poignée TCP, poignée
TLS — avant le moindre octet de page : une fois vers le serveur de
redirection, une fois vers Render. Attacher i-aes.eu directement au service
supprime la première, et laisse au passage l'adresse du cabinet dans la barre
du navigateur.

RIEN DANS L'APPLICATION NE S'Y OPPOSE — c'est vérifié ici : aucun contrôle de
l'en-tête `Host`, donc un nom quelconque est servi. Mais deux réglages
attendaient le site au tournant.

PREMIER — LES ORIGINES CORS. Une seule adresse y était écrite en dur :
`conseilprev.onrender.com`. Tant que le site vit dessus, personne ne s'en
aperçoit : les appels de la page à sa propre API sont de MÊME ORIGINE et ne
passent pas par CORS. Servi depuis un autre nom, cette liste désigne une
adresse où plus rien ne répond, et tout appel croisé est refusé.

SECOND — `Strict-Transport-Security`, posé SANS CONDITION. Envoyé en clair il
est ignoré par les navigateurs, donc il ne protégeait rien là où il était
posé ; sur `localhost` en revanche, il verrouille le poste du développeur sur
du HTTPS que rien n'y sert, pour un an. Et sa directive `includeSubDomains`,
inoffensive sur `*.onrender.com` faute de sous-domaines à nous, forcerait le
HTTPS sur TOUS les sous-domaines de i-aes.eu — pendant un an, auprès de chaque
navigateur l'ayant vue une fois.
"""
import importlib
import io
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-domaine')

import app as application  # noqa: E402

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()

_IP = [200]


def _get(chemin='/health', proto=None, hote=None, **entetes):
    _IP[0] += 1
    h = {'X-Forwarded-For': '198.51.100.%d' % (_IP[0] % 250 + 1)}
    if proto:
        h['X-Forwarded-Proto'] = proto
    if hote:
        h['Host'] = hote
    h.update(entetes)
    return application.app.test_client().get(chemin, headers=h)


# ── UN DOMAINE PROPRE EST SERVI TEL QUEL ─────────────────────────────────

def test_aucun_controle_dhote_ne_bloque_un_domaine_propre():
    """LA CONDITION PRÉALABLE. Si l'application validait l'en-tête `Host`,
    attacher i-aes.eu au service rendrait 400 sur tout, et la cause serait
    introuvable côté Render."""
    r = _get('/health', hote='i-aes.eu')
    assert r.status_code == 200, (
        'une requête portant Host: i-aes.eu répond %s' % r.status_code)
    assert (r.get_json() or {}).get('status') == 'ok'


def test_aucun_nom_dhote_nest_code_en_dur_dans_une_liste_dautorisation():
    """Une liste écrite en dur est exactement ce qui casse une bascule de
    domaine, et ne se voit qu'après."""
    assert "origins\": [\"https://conseilprev.onrender.com\"]" not in SOURCE
    assert "SITE_ORIGINES = " in SOURCE


# ── LES ORIGINES CORS SUIVENT LE SITE ────────────────────────────────────

def test_les_origines_viennent_de_lenvironnement():
    assert "os.environ.get('SITE_ORIGINES')" in SOURCE


def test_plusieurs_origines_sont_admises_ensemble():
    """Une bascule progressive exige que l'ancien ET le nouveau nom soient
    admis en même temps, le temps que le domaine change de cible."""
    os.environ['SITE_ORIGINES'] = ('https://i-aes.eu, '
                                   'https://conseilprevia.onrender.com')
    try:
        m = importlib.reload(application)
        assert m.SITE_ORIGINES == ['https://i-aes.eu',
                                   'https://conseilprevia.onrender.com']
    finally:
        os.environ.pop('SITE_ORIGINES', None)
        importlib.reload(application)


def test_la_valeur_par_defaut_ne_change_rien():
    """La correction doit être sûre à déployer AVANT la bascule."""
    os.environ.pop('SITE_ORIGINES', None)
    m = importlib.reload(application)
    assert m.SITE_ORIGINES == ['https://conseilprev.onrender.com']


# ── HSTS : SEULEMENT SUR UNE CONNEXION CHIFFRÉE ──────────────────────────

def test_hsts_est_pose_sur_une_connexion_chiffree():
    r = _get('/health', proto='https')
    assert 'max-age=' in (r.headers.get('Strict-Transport-Security') or '')


def test_hsts_nest_pas_pose_en_clair():
    """Envoyé en clair il est ignoré par les navigateurs — mais sur localhost
    il verrouille le poste du développeur sur du HTTPS pour un an."""
    r = _get('/health', proto='http')
    assert not r.headers.get('Strict-Transport-Security')


def test_hsts_est_reglable_avant_de_brancher_un_domaine_propre():
    """`includeSubDomains` forcerait le HTTPS sur tous les sous-domaines de
    i-aes.eu pendant un an. Revenir en arrière demande de servir `max-age=0`
    puis d'attendre que chaque visiteur repasse : il faut pouvoir décider
    AVANT, pas après."""
    assert "HSTS = os.environ.get('HSTS'" in SOURCE
    os.environ['HSTS'] = 'max-age=600'
    try:
        m = importlib.reload(application)
        assert m.HSTS == 'max-age=600'
    finally:
        os.environ.pop('HSTS', None)
        importlib.reload(application)


def test_le_defaut_hsts_reste_le_bon_choix():
    """Réglable ne veut pas dire affaibli : sans variable, la protection
    complète est servie."""
    os.environ.pop('HSTS', None)
    m = importlib.reload(application)
    assert m.HSTS == 'max-age=31536000; includeSubDomains'


def test_le_protocole_est_lu_derriere_le_terminateur_tls():
    """Render termine le TLS en amont : `request.scheme` vaut « http » côté
    application même quand le visiteur est en HTTPS. Se fier à lui
    supprimerait HSTS en production."""
    i = SOURCE.index("Strict-Transport-Security'] = HSTS")
    avant = SOURCE[max(0, i - 400):i]
    assert "X-Forwarded-Proto" in avant, (
        "HSTS est décidé sans regarder X-Forwarded-Proto : il ne sera jamais "
        "posé en production")
