# -*- coding: utf-8 -*-
"""IL N'Y A PLUS QU'UN ESPACE CLIENT SUR CE SITE, ET C'EST LE SUJET.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande de vérification des inscriptions et
des connexions des espaces clients. Le parcours de /login a été rejoué et tient
(voir `test_inscription_et_connexion.py`). Mais ce site en portait un SECOND,
sur /sourcing, avec ses propres routes `/api/auth/*`, son propre magasin de
comptes et son propre mot de passe — et pas une règle.

CE QUE LA MESURE A MONTRÉ, PARCOURS JOUÉ CONTRE L'APPLICATION.
  · Il n'ouvrait RIEN : le jeton rendu à la connexion n'était relu par aucune
    route, et la plateforme vers laquelle son bouton menait est publique.
  · Les comptes vivaient dans `users_db.json`, à la racine du service : ni
    versionné, ni monté sur un disque. L'hébergeur remplace ce disque à chaque
    déploiement — ils repartaient VIDES, sans que rien ne le dise.
  · Une inscription en attente appartenait au dernier venu : la garde ne
    regardait que les comptes CONFIRMÉS, si bien qu'un inconnu réinscrivant
    l'adresse d'Alice remplaçait son mot de passe, son nom et son jeton. Alice
    cliquait SON lien et lisait « Lien invalide ou expiré ».
  · Le jeton de confirmation revenait dans la réponse (`_dev_link`) dès que
    l'envoi de courrier tombait : confirmer une adresse ne prouvait plus rien.

DEUX ESPACES CLIENTS SUR UN SITE, C'EST UN ESPACE QUI POURRIT SANS TÉMOIN. Le
premier est éprouvé et va bien ; le second ne l'était pas et portait ces quatre
défauts, dont aucun ne se voyait sur une page. Il a donc été retiré plutôt que
réparé : réparer un magasin effacé à chaque mise en ligne aurait été polir ce
qui disparaît. /sourcing renvoie vers /login.

CE QUE CES RÈGLES TIENNENT. Qu'il n'en revienne pas un troisième sans qu'on
s'en aperçoive, que les adresses fermées disent OÙ ALLER plutôt que de se
taire, et que l'accès administrateur — qui n'a jamais dépendu de ce magasin —
reste intact.
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
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-sourcing')

import app as application  # noqa: E402

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
ARBRE = ast.parse(SOURCE)
PAGE = io.open(os.path.join(ICI, 'sourcing.html'), encoding='utf-8').read()
SCRIPT = io.open(os.path.join(ICI, 'sourcing.page.js'), encoding='utf-8').read()

_N = [500]


def _ent():
    _N[0] += 1
    return {'X-Forwarded-For': '203.0.113.%d' % (_N[0] % 240 + 2),
            'User-Agent': 'Mozilla/5.0 (recette)',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept-Encoding': 'identity',
            'Accept': 'application/json'}


# ═══════════════════════════════════════════════════════════════════════════
#  UN SEUL MAGASIN DE COMPTES, ET IL EST DANS LE REGISTRE
# ═══════════════════════════════════════════════════════════════════════════

def test_aucun_second_magasin_de_comptes_ne_subsiste():
    """LA PROPRIÉTÉ, PAS LES NOMS. Un second magasin de comptes ne se signale
    pas : il se remarque le jour où des comptes disparaissent. La règle refuse
    donc qu'une fonction du module lise ou écrive un fichier de comptes hors du
    registre — quel que soit le nom qu'on lui donne."""
    coupables = []
    for n in ast.walk(ARBRE):
        if not isinstance(n, ast.FunctionDef):
            continue
        src = ast.unparse(n)
        if not re.search(r"""open\(|json\.dump|json\.load""", src):
            continue
        if re.search(r"""users?_db|USERS_FILE|comptes?\.json|_load_users|_save_users""",
                     src, re.I):
            coupables.append(n.name)
    assert not coupables, (
        "un magasin de comptes en fichier est revenu : %s" % coupables)
    for mort in ('_load_users', '_save_users', 'USERS_FILE',
                 '_hash_password', '_verify_password'):
        assert not hasattr(application, mort), (
            "%s existe encore : le second espace client peut renaître" % mort)


def test_le_seul_magasin_de_comptes_est_celui_du_registre():
    """LE TÉMOIN POSITIF, sans lequel la règle précédente serait verte sur un
    site qui n'aurait plus AUCUN compte. L'espace client de /login s'appuie sur
    la table `clients` du registre, et il l'interroge."""
    corps = [ast.unparse(n) for n in ast.walk(ARBRE)
             if isinstance(n, ast.FunctionDef) and n.name == 'sentauth_login']
    assert corps and 'FROM clients WHERE email' in corps[0], corps[:1]


# ═══════════════════════════════════════════════════════════════════════════
#  LES ADRESSES FERMÉES DISENT OÙ ALLER
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize('chemin', ['/api/auth/register', '/api/auth/login',
                                    '/api/auth/delete'])
def test_les_anciennes_portes_refusent_en_nommant_lespace_client(chemin):
    """UN 404 MUET EST LE PIRE DES REFUS ICI : un signet, une page gardée en
    cache ou un formulaire rejoué doivent apprendre où est passé l'espace
    client, pas se heurter à rien. 410 dit « c'était là, ce n'est plus là » —
    et le corps dit où."""
    c = application.app.test_client()
    r = c.post(chemin, headers=_ent(),
               json={'email': 'x@example.invalid', 'password': 'Peu1!importe'})
    assert r.status_code == 410, (chemin, r.status_code)
    j = r.get_json() or {}
    assert j.get('espace_client') == '/login', j
    assert '/login' in (j.get('error') or ''), j
    assert j.get('ok') is False


def test_un_lien_de_confirmation_deja_parti_mene_a_lespace_client():
    """Des courriels portant ce lien sont partis. Ils ne peuvent plus rien
    confirmer — le compte visé n'existe plus — mais ils ne doivent pas tomber
    dans le vide."""
    c = application.app.test_client()
    r = c.get('/api/auth/verify?email=a@example.invalid&token=zz', headers=_ent())
    assert r.status_code in (301, 302), r.status_code
    assert '/login' in (r.headers.get('Location') or ''), r.headers


def test_aucune_route_ne_cree_plus_de_compte_hors_du_registre():
    """LA FERMETURE ÉPROUVÉE PAR SON EFFET : quel que soit le corps envoyé,
    aucune de ces adresses ne rend un succès."""
    c = application.app.test_client()
    for chemin in ('/api/auth/register', '/api/auth/login', '/api/auth/delete'):
        for corps in ({}, {'email': 'a@example.invalid'},
                      {'email': 'a@example.invalid', 'password': 'Recette2026!ok',
                       'prenom': 'A', 'nom': 'B', 'consent': True}):
            r = c.post(chemin, headers=_ent(), json=corps)
            assert r.status_code == 410, (chemin, corps, r.status_code)
            assert (r.get_json() or {}).get('ok') is not True


# ═══════════════════════════════════════════════════════════════════════════
#  L'ACCÈS ADMINISTRATEUR N'A JAMAIS DÉPENDU DE CE MAGASIN
# ═══════════════════════════════════════════════════════════════════════════

def test_lacces_administrateur_survit_au_retrait():
    """CE QU'IL NE FAUT PAS EMPORTER AVEC LE RESTE. Cette route partageait le
    fichier, les fonctions de hachage et le module de l'espace client retiré ;
    elle ne partageait pas son magasin. Elle répond toujours, et elle refuse
    toujours."""
    c = application.app.test_client()
    r = c.post('/api/auth/admin-login', headers=_ent(),
               json={'email': 'inconnu@example.invalid', 'password': 'x'})
    assert r.status_code == 403, r.status_code
    assert (r.get_json() or {}).get('ok') is False


def test_lacces_administrateur_ne_lit_aucun_magasin_de_comptes():
    corps = [ast.unparse(n) for n in ast.walk(ARBRE)
             if isinstance(n, ast.FunctionDef) and n.name == 'auth_admin_login']
    assert corps, "la route d'accès administrateur a disparu"
    assert 'ADMIN_PASSWORD' in corps[0] and 'compare_digest' in corps[0]
    assert "session['is_conseilprev'] = True" in corps[0]


# ═══════════════════════════════════════════════════════════════════════════
#  LA PAGE /sourcing DIT LA VÉRITÉ, ET SON SCRIPT NE TOMBE PAS
# ═══════════════════════════════════════════════════════════════════════════

def test_la_page_renvoie_vers_lespace_client_et_ne_demande_plus_de_compte():
    assert 'href="/login"' in PAGE, "la page ne renvoie nulle part"
    for reste in ('id="form-register"', 'id="form-login"', 'id="reg-password"',
                  'id="login-password"', 'id="reg-consent"'):
        assert reste not in PAGE, (
            "la page demande encore un compte qu'elle ne tient pas : %s" % reste)
    # Et elle ne réclame plus de mot de passe du tout, hors accès administrateur.
    champs = re.findall(r'<input[^>]*type="password"[^>]*id="([^"]+)"', PAGE)
    assert all(i.startswith('admin-') for i in champs), champs


def test_le_script_ne_pose_aucun_gestionnaire_sur_un_element_absent():
    """C'EST LA PANNE QUE LE RETRAIT POUVAIT CAUSER, ET ELLE EST TOTALE : un
    `getElementById(...).addEventListener` sur un identifiant retiré de la page
    lève au chargement, et emporte TOUT ce qui suit dans le même fichier — les
    filtres, le compteur, le reste. La page s'affiche, et plus rien ne
    fonctionne. Rien ne le signale."""
    vises = re.findall(r"""getElementById\(\s*['"]([^'"]+)['"]\s*\)\s*\.""", SCRIPT)
    assert vises, "aucun identifiant visé : la règle ne mesure plus rien"
    manquants = sorted({i for i in vises if ('id="%s"' % i) not in PAGE})
    assert not manquants, (
        "le script s'adresse à des éléments absents de la page : %s" % manquants)


def test_le_script_nappelle_plus_les_adresses_fermees():
    appels = re.findall(r"""fetch\(\s*['"](/api/auth/[^'"]+)['"]""", SCRIPT)
    assert appels == ['/api/auth/admin-login'], appels
