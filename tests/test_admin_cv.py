"""LES ROUTES D'ADMINISTRATION NE VERIFIAIENT PAS LEUR JETON, ELLES LE MESURAIENT.

CE QUI A ETE TROUVE, LE 29 AOUT 2026. Trois routes reservees a l'administrateur
s'autorisaient ainsi :

    token = request.args.get('token','').strip()
    if not token or len(token) < 8:
        abort(401)
    # Token valide si non-vide et ADMIN_PASSWORD configure

Le jeton n'etait compare a rien. `?token=12345678` passait. Ce qui restait
entre un inconnu et les CV deposes par les candidats etait de deviner un nom de
fichier — et `/api/admin/cv-list`, gardee de la meme facon, donnait la liste
complete de ces noms. De l'obscurite, et servie sur demande.

CE QUE CES ROUTES EXPOSENT n'est pas un reglage : ce sont des CV, donc des
donnees personnelles de gens qui les ont deposees pour postuler. Le RGPD ne
connait pas la protection par nom de fichier.

POURQUOI PERSONNE NE L'AVAIT VU. Il y avait un controle, il etait ecrit, il
rendait bien 401 sur une requete vide, et le commentaire au-dessus affirmait
qu'il verifiait le jeton. Un controle qui existe et ne controle rien se lit
comme un controle.

ET LA VERIFICATION QUI, ELLE, ETAIT CORRECTE NE SERVAIT A RIEN.
`/api/auth/admin-login` comparait l'adresse et le mot de passe a temps
constant, avec limitation de debit — puis renvoyait un jeton aleatoire SANS
RIEN POSER EN SESSION. L'administrateur repartait avec une preuve que le
serveur ne reconnaissait nulle part.

CE QUE CES REGLES GARDENT. Qu'aucune route d'administration ne serve quoi que
ce soit sans session administrateur ; que la connexion par mot de passe pose
reellement cette session ; qu'un mot de passe faux ne la pose pas ; et que la
faute elle-meme — autoriser sur la longueur d'une chaine — ne puisse plus etre
reecrite.
"""
import io
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()

sys.path.insert(0, ICI)
os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-admin-cv')
os.environ.setdefault('ADMIN_PASSWORD', 'mot-de-passe-de-recette-uniquement')

import app as application  # noqa: E402

ROUTES_PROTEGEES = [
    ('GET', '/api/admin/cv/dossier.pdf'),
    ('GET', '/api/admin/cv-list'),
    ('POST', '/api/admin/candidate'),
]


def _entetes(html=False):
    """Des en-tetes de navigateur credibles.

    Sans `Accept-Language`, l'application journalise HEADERS_INCOHERENTS et
    ecarte la requete avant la vue. Un premier essai a fait echouer le controle
    de deconnexion sur ce motif : `/logout` n'avait jamais ete atteint, la
    session n'avait donc pas ete videe, et la regle accusait le code."""
    return {'X-Forwarded-For': '203.0.113.7',
            'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'),
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept': 'text/html' if html else 'application/json'}


def _appel(client, methode, chemin, **kw):
    f = client.get if methode == 'GET' else client.post
    return f(chemin, headers=_entetes(), **kw)


# ── LA FAUTE NE PEUT PLUS ETRE REECRITE ──────────────────────────────────

def test_aucune_route_admin_n_autorise_sur_la_longueur_d_une_chaine():
    """LA REGLE QUI GARDE LA CORRECTION. Autoriser parce qu'une chaine est
    assez longue n'est pas une verification : c'est une mesure.

    SUR L'ARBRE, PAS SUR LE TEXTE — et j'ai appris pourquoi en l'ecrivant. Une
    premiere version cherchait le motif dans le source : elle est tombee sur la
    docstring de `admin_session_conseilprev`, qui CITE le code fautif pour
    expliquer ce qu'il faisait. La regle accusait le commentaire qui documente
    la correction. C'est la meme faute que celle qu'on garde ailleurs — une
    regle qu'un commentaire satisfait —, prise dans l'autre sens."""
    import ast
    arbre = ast.parse(SOURCE)
    fautes = []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.FunctionDef) or not n.name.startswith('admin_'):
            continue
        for c in ast.walk(n):
            if not isinstance(c, ast.Compare) or not isinstance(c.ops[0], (ast.Lt, ast.LtE)):
                continue
            gauche = ast.unparse(c.left)
            if re.match(r'^len\(\s*\w*token\w*\s*\)$', gauche, re.I):
                fautes.append('%s (%s)' % (n.name, ast.unparse(c)))
    assert not fautes, (
        "route(s) d'administration autorisant sur la longueur du jeton : %s. "
        "Un jeton se compare, il ne se mesure pas." % ', '.join(fautes))


def test_le_jeton_ne_voyage_plus_dans_l_url_cote_client():
    """Un secret place dans une URL se retrouve dans les journaux du serveur,
    dans ceux des intermediaires, et dans l'en-tete Referer de la page
    suivante. Meme verifie, il n'a rien a faire la."""
    front = io.open(os.path.join(ICI, 'platform.page.js'), encoding='utf-8').read()
    assert 'cp_token' not in front, (
        "le client remet un jeton d'administration dans l'URL des routes CV")
    assert "'/api/admin/cv-list'" in front, (
        "l'appel a la liste des CV n'est plus celui attendu — controle a revoir")


# ── SANS SESSION, RIEN N'EST SERVI ───────────────────────────────────────

@pytest.mark.parametrize('methode,chemin', ROUTES_PROTEGEES)
def test_sans_session_la_route_refuse(methode, chemin):
    c = application.app.test_client()
    r = _appel(c, methode, chemin, **({'json': {'uid': 'x'}} if methode == 'POST' else {}))
    assert r.status_code == 403, (
        "%s %s repond %d sans session administrateur" % (methode, chemin, r.status_code))


@pytest.mark.parametrize('methode,chemin', ROUTES_PROTEGEES)
def test_un_jeton_invente_ne_suffit_plus(methode, chemin):
    """LA REQUETE QUI MARCHAIT. Huit caracteres au hasard, et le serveur
    servait."""
    c = application.app.test_client()
    if methode == 'GET':
        r = c.get(chemin + '?token=12345678', headers=_entetes())
    else:
        r = c.post(chemin, headers=_entetes(), json={'token': '1234567890', 'uid': 'x'})
    assert r.status_code == 403, (
        "%s %s accepte encore un jeton invente (%d)" % (methode, chemin, r.status_code))


# ── AVEC SESSION, LA ROUTE SERT ──────────────────────────────────────────

@pytest.mark.parametrize('methode,chemin', ROUTES_PROTEGEES)
def test_avec_session_administrateur_la_route_repond(methode, chemin):
    """L'AUTRE MOITIE DE LA REGLE. Une correction qui fermerait la porte a
    l'administrateur lui-meme ne serait pas une correction : elle serait
    contournee la semaine suivante."""
    c = application.app.test_client()
    with c.session_transaction() as s:
        s['is_conseilprev'] = True
    r = _appel(c, methode, chemin, **({'json': {'uid': 'x'}} if methode == 'POST' else {}))
    assert r.status_code != 403, (
        "%s %s refuse l'administrateur connecte" % (methode, chemin))


def test_l_administrateur_connecte_voit_la_liste_des_cv():
    c = application.app.test_client()
    with c.session_transaction() as s:
        s['is_conseilprev'] = True
    r = c.get('/api/admin/cv-list', headers=_entetes())
    assert r.status_code == 200, r.status_code
    assert r.get_json().get('ok') is True


def test_un_cv_reel_se_telecharge_avec_la_session_et_pas_sans():
    """Le controle decisif : un fichier qui EXISTE. Les autres routes peuvent
    rendre 404 pour de bonnes raisons ; ici on verifie qu'un CV present est
    bien servi a l'administrateur, et bien refuse a l'anonyme."""
    dossier = application.UPLOAD_FOLDER
    os.makedirs(dossier, exist_ok=True)
    nom = 'recette_controle_acces.pdf'
    chemin_fichier = os.path.join(dossier, nom)
    cree = not os.path.exists(chemin_fichier)
    if cree:
        io.open(chemin_fichier, 'wb').write(b'%PDF-1.4 recette\n')
    try:
        anonyme = application.app.test_client()
        r = anonyme.get('/api/admin/cv/' + nom, headers=_entetes())
        assert r.status_code == 403, (
            "un CV existant est servi sans session administrateur (%d) — c'est "
            "exactement la fuite corrigee" % r.status_code)

        admin = application.app.test_client()
        with admin.session_transaction() as s:
            s['is_conseilprev'] = True
        r = admin.get('/api/admin/cv/' + nom, headers=_entetes())
        assert r.status_code == 200, (
            "l'administrateur connecte ne peut plus telecharger un CV (%d)" % r.status_code)
        assert r.data.startswith(b'%PDF'), "le fichier servi n'est pas celui attendu"
    finally:
        if cree and os.path.exists(chemin_fichier):
            os.remove(chemin_fichier)


# ── LA CONNEXION PAR MOT DE PASSE POSE REELLEMENT LA SESSION ─────────────

def test_la_connexion_administrateur_pose_la_session():
    """Elle verifiait le mot de passe a temps constant, puis ne posait rien.
    La verification etait juste et sans effet."""
    c = application.app.test_client()
    r = c.post('/api/auth/admin-login', headers=_entetes(),
               json={'email': application.ADMIN_EMAIL,
                     'password': os.environ['ADMIN_PASSWORD']})
    assert r.status_code == 200 and r.get_json().get('ok') is True, r.get_data(as_text=True)[:300]
    with c.session_transaction() as s:
        assert s.get('is_conseilprev') is True, (
            "la connexion administrateur reussit sans poser de session : le "
            "mot de passe est verifie pour rien")
    assert c.get('/api/admin/cv-list', headers=_entetes()).status_code == 200, (
        "apres connexion, les routes d'administration refusent encore")


def test_un_mauvais_mot_de_passe_ne_pose_rien():
    """La regle inverse, sans laquelle la precedente serait satisfaite par une
    route qui ouvrirait la session AVANT de comparer."""
    c = application.app.test_client()
    r = c.post('/api/auth/admin-login', headers=_entetes(),
               json={'email': application.ADMIN_EMAIL, 'password': 'pas-le-bon'})
    assert r.status_code == 401, r.status_code
    with c.session_transaction() as s:
        assert not s.get('is_conseilprev'), (
            "un mot de passe faux ouvre tout de meme la session administrateur")


def test_une_autre_adresse_ne_pose_rien():
    c = application.app.test_client()
    r = c.post('/api/auth/admin-login', headers=_entetes(),
               json={'email': 'inconnu@example.org',
                     'password': os.environ['ADMIN_PASSWORD']})
    assert r.status_code == 403, r.status_code
    with c.session_transaction() as s:
        assert not s.get('is_conseilprev')


def test_la_deconnexion_retire_bien_l_acces():
    """`/logout` retire deja `is_conseilprev`. Comme la connexion
    administrateur pose desormais ce drapeau, il faut verifier que la porte de
    sortie ferme la porte d'entree."""
    c = application.app.test_client()
    with c.session_transaction() as s:
        s['is_conseilprev'] = True
    # LA ROUTE EST `/api/sentinel-auth/logout`, EN POST. Un premier essai
    # interrogeait `/logout`, qui n'existe pas : le 404 ne vidait aucune
    # session et la regle accusait le code de ne pas deconnecter. Un controle
    # qui se trompe de porte mesure toujours quelque chose, jamais ce qu'il
    # croit.
    r = c.post('/api/sentinel-auth/logout', headers=_entetes())
    assert r.status_code == 200, (
        "la deconnexion n'a pas ete atteinte (%d) : le controle mesurerait "
        "autre chose" % r.status_code)
    assert c.get('/api/admin/cv-list', headers=_entetes()).status_code == 403, (
        "apres deconnexion, les routes d'administration repondent encore")
