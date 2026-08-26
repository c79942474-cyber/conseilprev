"""AUCUNE ATTENTE SANS LIMITE — ni vers la base, ni vers le réseau.

LA FAUTE, ET CE QU'ELLE COÛTAIT. `registre_get_db()` emprunte un repli quand
le pool de connexions ne rend pas de connexion : `psycopg.connect(DATABASE_URL)`,
SANS `connect_timeout`. Les deux autres chemins vers Postgres, eux, sont bornés
— le test de démarrage à 5 s, le pool à 10 s. Celui-là ne l'était pas.

CE QUE ÇA DONNE QUAND LA BASE NE RÉPOND PLUS. Un SYN TCP sans réponse — base
suspendue, injoignable, ou dans une autre région que le service — est retenté
par Linux pendant environ 127 secondes. Gunicorn tue le worker à 90. Et comme
la commande de démarrage ne déclare pas `--workers`, gunicorn n'en lance QU'UN :
ce n'est donc pas une requête qui échoue, c'est le site qui tombe, le temps du
redémarrage. Le journal de production ne montrait rien d'autre qu'un
« CRITICAL WORKER TIMEOUT » sans requête associée.

CE QUE CES CONTRÔLES MESURENT. Pas la ligne corrigée : TOUS les appels
sortants du dépôt, relus à l'arbre syntaxique. Un `grep` compte des lignes et
laisse passer un `timeout=` posé trois lignes plus bas — c'est ce qui m'a fait
d'abord accuser à tort les appels HTTP, qui sont tous bornés. L'arbre, lui,
voit l'appel entier.

CE QUE CES CONTRÔLES NE PEUVENT PAS FAIRE. Prouver que la base était bien la
cause du timeout observé : le journal ne nomme pas la requête en cours. Ils
prouvent qu'aucune attente non bornée ne subsiste — ce qui est vrai
indépendamment de la cause, et se vérifie.
"""
import ast
import glob
import io
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

# Les appels dont une attente sans limite retient un worker entier.
BORNER = {
    ('psycopg', 'connect'): 'connect_timeout',
    ('requests', 'get'): 'timeout',
    ('requests', 'post'): 'timeout',
    ('requests', 'put'): 'timeout',
    ('requests', 'head'): 'timeout',
    ('requests', 'delete'): 'timeout',
    ('requests', 'request'): 'timeout',
}


def _sources():
    """Le code servi, pas les recettes : un script de recette qui pend gêne
    son auteur, pas un visiteur."""
    for f in sorted(glob.glob(os.path.join(ICI, '*.py'))):
        n = os.path.basename(f)
        if n.startswith(('recette_', 'test_')):
            continue
        yield n, io.open(f, encoding='utf-8').read()


def _appels_sans_delai():
    manquants = []
    for nom, src in _sources():
        try:
            arbre = ast.parse(src)
        except SyntaxError:                                    # noqa: PERF203
            continue
        for n in ast.walk(arbre):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            if not (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)):
                continue
            cle = (f.value.id, f.attr)
            attendu = BORNER.get(cle)
            if attendu and not any(k.arg == attendu for k in n.keywords):
                manquants.append('%s:%d  %s.%s() sans %s'
                                 % (nom, n.lineno, cle[0], cle[1], attendu))
    return manquants


def test_aucun_appel_sortant_nattend_sans_limite():
    """LE CONTRÔLE QUI AURAIT VU LE DÉFAUT. Il ne connaît pas la ligne
    fautive : il relit tous les appels du dépôt."""
    manquants = _appels_sans_delai()
    assert not manquants, (
        'attentes non bornées — un worker peut y rester plus longtemps que le '
        'délai de gunicorn :\n   ' + '\n   '.join(manquants))


def test_le_controle_sait_reperer_un_appel_non_borne():
    """DISCRIMINATION. Un contrôle qui déclare « rien à signaler » sans savoir
    reconnaître le défaut ne protège de rien. On lui soumet le code fautif tel
    qu'il était écrit, et il doit le voir."""
    fautif = ast.parse(
        'import psycopg\n'
        'def f():\n'
        '    return psycopg.connect(DATABASE_URL, row_factory=r)\n')
    vus = []
    for n in ast.walk(fautif):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and isinstance(n.func.value, ast.Name)):
            cle = (n.func.value.id, n.func.attr)
            attendu = BORNER.get(cle)
            if attendu and not any(k.arg == attendu for k in n.keywords):
                vus.append(cle)
    assert vus == [('psycopg', 'connect')], vus


def test_le_delai_est_declare_une_seule_fois():
    """Il était écrit en dur dans le test de démarrage et absent du repli :
    deux endroits, deux comportements. Une seule constante, lue par les deux."""
    src = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
    assert 'REGISTRE_CONNECT_TIMEOUT = int(os.environ.get(' in src
    # LU DANS L'ARBRE, PAS DANS LE TEXTE. Une première version cherchait
    # « connect_timeout= » ligne à ligne et accusait un COMMENTAIRE qui
    # décrivait l'ancien état — la règle voyait de la prose et la comptait
    # comme du code. L'arbre syntaxique ne voit que les arguments réels.
    en_dur = []
    for n in ast.walk(ast.parse(src)):
        if not isinstance(n, ast.Call):
            continue
        for k in n.keywords:
            if k.arg != 'connect_timeout':
                continue
            if not (isinstance(k.value, ast.Name)
                    and k.value.id == 'REGISTRE_CONNECT_TIMEOUT'):
                en_dur.append('app.py:%d  connect_timeout=%s'
                              % (n.lineno, ast.dump(k.value)[:40]))
    assert not en_dur, 'délai écrit en dur au lieu de la constante : %s' % en_dur


def test_la_constante_vit_hors_du_bloc_conditionnel():
    """Définie dans `if REGISTRE_USE_PG:`, elle n'existerait pas quand ce bloc
    est sauté — et la ligne qui la lit lèverait un NameError en pleine requête,
    loin de l'endroit où elle aurait dû être posée."""
    src = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
    for ligne in src.split('\n'):
        if ligne.startswith('REGISTRE_CONNECT_TIMEOUT'):
            return
    raise AssertionError(
        'REGISTRE_CONNECT_TIMEOUT n\'est pas définie à l\'indentation zéro : '
        'elle dépend d\'un bloc qui peut ne pas s\'exécuter')


def test_le_repli_ne_bascule_pas_en_silence_sur_sqlite():
    """Un repli qui servirait SQLite quand Postgres ne répond pas montrerait
    une base VIDE sous le même nom — cela se lit comme des données perdues,
    pas comme une panne. L'erreur doit remonter."""
    src = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
    i = src.index('def registre_get_db():')
    corps = src[i:src.index('\ndef ', i + 10)]
    pg, sqlite = corps.split('else:', 1)
    assert 'sqlite3.connect' not in pg, (
        'la branche Postgres retombe sur SQLite : une base vide serait servie '
        'sous le nom de la vraie')
    assert 'sqlite3.connect' in sqlite
