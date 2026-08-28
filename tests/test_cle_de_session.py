"""LA CLÉ QUI SIGNE LES SESSIONS NE PEUT PAS ÊTRE PUBLIQUE.

CE QUI A DÉCLENCHÉ CE FICHIER. Le tableau des variables d'environnement du
service en ligne, relevé le 28 août, ne contient pas `FLASK_SECRET_KEY`. Entre
`DATABASE_URL` et `FORMATION_TVA_PCT`, où l'ordre alphabétique la placerait,
il n'y a rien. L'application se rabattait donc sur

    sha256(b'conseilprev-sentinel-fallback-2026')

une constante dont la graine est écrite en clair dans `app.py` et que ce dépôt
publie. N'importe qui pouvait la calculer.

CE QUE CELA OUVRE. Le cookie de session de Flask est SIGNÉ, pas chiffré :
connaître la clé suffit à en fabriquer un. Un tiers pouvait se délivrer
`{'client_id': N}` — le compte de son choix — ou `{'is_conseilprev': True}`,
qui accorde l'accès administrateur complet à Sentinel sans mot de passe. Le
même secret sale par ailleurs `_rgpd_hash()` : les empreintes d'adresses IP et
d'identifiants cessent d'être des pseudonymes dès que le sel est connu.

RIEN NE LE SIGNALAIT. L'application démarrait, servait, authentifiait
normalement. C'est la propriété commune de tous les défauts corrigés cette
semaine : aucun ne produit d'erreur.

CE QUE CES CONTRÔLES GARDENT. Que la constante publique ne puisse plus servir
dès qu'une base est déclarée ; que le repli dérivé soit le même dans tous les
processus — sinon les workers se rejetteraient leurs cookies — et qu'il change
avec la base ; que la variable, quand elle existe, l'emporte ; et que chacun
des deux replis se DISE dans le journal.

CE QU'ILS NE PEUVENT PAS FAIRE. Vérifier que la variable est définie sur
Render. Cela se lit dans le tableau de bord, et c'est la vraie correction —
le repli dérivé n'est qu'un pis-aller qui empêche le pire.
"""
import io
import os
import re
import subprocess
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()

# La graine publique, relevée dans le code — c'est elle qu'on interdit en ligne.
GRAINE = re.search(r"hashlib\.sha256\(b'([^']+)'\)\.hexdigest\(\)", SOURCE)
CONSTANTE_PUBLIQUE = None
if GRAINE:
    import hashlib
    CONSTANTE_PUBLIQUE = hashlib.sha256(GRAINE.group(1).encode()).hexdigest()

_LIRE = ("import sys, logging; sys.path.insert(0, %r); logging.disable(logging.CRITICAL);"
         "import app; print('CLE=' + str(app.app.secret_key));"
         "print('SEL=' + app._rgpd_hash('x'))" % ICI)


def _demarrer(**env):
    """Importe l'application dans un processus neuf, avec l'environnement
    demandé. En sous-processus parce que la clé se fixe À L'IMPORT : la relire
    dans la session pytest mesurerait le cache d'import, pas le code."""
    e = dict(os.environ)
    e.pop('DATABASE_URL', None)
    e.pop('FLASK_SECRET_KEY', None)
    e.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
    e.update({k: v for k, v in env.items() if v is not None})
    r = subprocess.run([sys.executable, '-c', _LIRE], capture_output=True,
                       text=True, env=e, cwd='/tmp', timeout=300)
    sortie = (r.stdout or '') + (r.stderr or '')
    m = re.search(r'^CLE=(.*)$', sortie, re.M)
    s = re.search(r'^SEL=(.*)$', sortie, re.M)
    if not m:
        pytest.fail("l'application n'a pas démarré :\n%s" % sortie[-2000:])
    return m.group(1), (s.group(1) if s else None)


BASE_A = 'postgresql://u:motdepasseA@127.0.0.1:1/b'
BASE_B = 'postgresql://u:motdepasseB@127.0.0.1:1/b'


def test_la_graine_publique_est_bien_dans_le_depot():
    """Le contrôle suivant n'a de sens que si cette constante existe encore.
    Si elle disparaissait, il faudrait le savoir plutôt que de croire garder
    quelque chose."""
    assert CONSTANTE_PUBLIQUE, (
        "la constante de repli a disparu du code : ces contrôles ne gardent "
        "plus rien et doivent être relus")


def test_la_constante_publique_ne_sert_plus_des_qu_une_base_est_declaree():
    """LA RÈGLE. Une clé calculable depuis le dépôt ne doit jamais signer les
    sessions d'un service en ligne."""
    cle, _ = _demarrer(DATABASE_URL=BASE_A)
    assert cle != CONSTANTE_PUBLIQUE, (
        "la clé de session est la constante publiée dans le dépôt : "
        "n'importe qui peut fabriquer un cookie d'administrateur")


def test_le_repli_derive_est_le_meme_dans_tous_les_processus():
    """Deux workers qui tirent des clés différentes se rejettent leurs cookies :
    l'utilisateur est déconnecté une requête sur deux, sans explication."""
    a, _ = _demarrer(DATABASE_URL=BASE_A)
    b, _ = _demarrer(DATABASE_URL=BASE_A)
    assert a == b, (
        "deux démarrages sur la même base donnent des clés différentes : les "
        "workers se rejetteront leurs sessions")


def test_le_repli_derive_change_avec_la_base():
    """Sinon il ne dérive de rien : ce serait une seconde constante, publique
    dès que le code l'est."""
    a, _ = _demarrer(DATABASE_URL=BASE_A)
    b, _ = _demarrer(DATABASE_URL=BASE_B)
    assert a != b, (
        "la clé ne dépend pas de la chaîne de connexion : elle est constante, "
        "donc calculable par qui lit le code")


def test_la_variable_declaree_l_emporte():
    cle, _ = _demarrer(DATABASE_URL=BASE_A, FLASK_SECRET_KEY='un-secret-declare-de-recette')
    assert cle == 'un-secret-declare-de-recette', (
        "FLASK_SECRET_KEY ne l'emporte plus : la déclarer n'aurait plus d'effet")


def test_le_sel_des_empreintes_rgpd_suit_la_cle():
    """`_rgpd_hash()` sale ses empreintes avec `app.secret_key`. Si la clé
    redevenait publique, ces pseudonymes cesseraient d'en être."""
    _, sel_a = _demarrer(DATABASE_URL=BASE_A)
    _, sel_b = _demarrer(DATABASE_URL=BASE_B)
    assert sel_a and sel_b, "_rgpd_hash() n'est plus appelable"
    assert sel_a != sel_b, (
        "l'empreinte RGPD ne dépend plus de la clé de session : son sel est "
        "redevenu constant, et une adresse IP se retrouve par force brute")


def _journal(**env):
    e = dict(os.environ)
    e.pop('DATABASE_URL', None)
    e.pop('FLASK_SECRET_KEY', None)
    e.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
    e.update({k: v for k, v in env.items() if v is not None})
    code = "import sys; sys.path.insert(0, %r); import app" % ICI
    r = subprocess.run([sys.executable, '-c', code], capture_output=True,
                       text=True, env=e, cwd='/tmp', timeout=300)
    return (r.stdout or '') + (r.stderr or '')


def test_le_repli_derive_se_dit_dans_le_journal():
    """Un pis-aller silencieux se prend pour une configuration correcte, et
    personne ne définit jamais la variable."""
    j = _journal(DATABASE_URL=BASE_A)
    assert 'FLASK_SECRET_KEY' in j and 'ERROR' in j, (
        "le repli dérivé ne s'annonce plus : rien ne rappellera de déclarer "
        "la variable")


def test_le_repli_public_se_dit_plus_fort_encore():
    j = _journal()
    assert 'FLASK_SECRET_KEY' in j and 'ERROR' in j, (
        "le repli sur la constante publique ne s'annonce plus")
    assert 'PUBLIQUE' in j.upper(), (
        "le journal ne dit pas que la clé employée est publique : c'est "
        "pourtant la seule chose qui compte dans ce cas")


def test_aucun_autre_chemin_ne_pose_la_cle_de_session():
    """Une seconde affectation, ailleurs, écraserait celle-ci sans que rien
    ne le dise — et pourrait très bien remettre la constante."""
    poses = [m.start() for m in re.finditer(r'app\.secret_key\s*=', SOURCE)]
    assert poses, "plus aucune affectation : le contrôle doit être revu"
    d = SOURCE.index('_CLE_DECLAREE = ')
    f = SOURCE.index("app.config['PERMANENT_SESSION_LIFETIME']")
    hors = [i for i in poses if not (d < i < f)]
    assert not hors, (
        "%d affectation(s) de app.secret_key hors du bloc de décision : la "
        "dernière gagne, et rien ne dit laquelle c'est" % len(hors))
