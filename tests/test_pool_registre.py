"""LE POOL POSTGRES NE SE PARTAGE PAS ENTRE PROCESSUS.

CE QUI S'EST PASSÉ. Le journal de production du 27 août affichait, sur CHAQUE
« GET / », pendant des heures :

    WARNING REGISTRE_IA — getconn pool echoue, connexion directe :
            couldn't get a connection after 10.00 sec

Toutes les réponses étaient 200. Le service n'était pas en panne : il payait
dix secondes par requête avant de se rabattre sur une connexion directe, plus
le temps d'ouvrir celle-ci. Vu d'un navigateur, cela s'appelle « le site ne
répond plus ».

LA CAUSE, ÉTABLIE PAR LA MESURE. Le pool était construit au niveau module.
Sous `--preload`, gunicorn importe le module UNE FOIS dans le maître, puis
forke ses workers — le journal le montre : les lignes d'initialisation portent
des horodatages antérieurs à « Starting gunicorn », et il n'y en a qu'un jeu
pour deux workers. Or `fork()` copie la mémoire mais PAS les fils d'exécution.

Dans psycopg_pool 3.2, cela partage la table en deux :

  · `putconn()` rend la connexion synchronement — un enfant sait donc recycler
    ce dont il a hérité ;
  · `_add_connection()`, qui CRÉE une connexion, n'est atteint que par
    `run_task()` → `self._tasks.put_nowait(task)`, c'est-à-dire par un fil de
    maintenance. Dans l'enfant, cette file n'est jamais dépilée.

Trois mesures, sur PostgreSQL 16 local, délai ramené à 3 s pour la lisibilité :

  1. un enfant forké ne dépasse JAMAIS le nombre de connexions héritées —
     la troisième demande échoue à 3,00 s pile, quand `max_size` vaut 8 ;
  2. une connexion perdue après le fork n'est JAMAIS remplacée : toutes les
     demandes suivantes échouent, à 3,00 s, indéfiniment ;
  3. le même incident, sur un pool créé APRÈS le fork, est réparé sur-le-champ.

La deuxième explique le journal : maître et enfants tiennent les mêmes sockets,
une connexion finit forcément par se casser, et le worker ne s'en relève pas.

CE QUE CES CONTRÔLES GARDENT. Que le pool ne naisse plus à l'import, qu'il soit
retenu par PID, qu'un pool hérité ne soit jamais servi ni fermé — le fermer
enverrait un paquet de terminaison sur des sockets qui appartiennent aussi au
processus qui les a ouverts — et que `registre_get_db()` passe par là.

CE QU'ILS NE PEUVENT PAS FAIRE. Mesurer une durée. Les chiffres ci-dessus ont
été relevés à la main, avec un PostgreSQL local ; ils ne tiennent pas dans une
recette qui doit passer sans base. Les contrôles qui EN ONT BESOIN se déclarent
ignorés en le disant, et un dernier contrôle vérifie que cet aveu n'est pas
devenu un silence.
"""
import io
import os
import re
import subprocess
import sys
import textwrap

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-pool')

import app as application  # noqa: E402

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()

# Une base de recette, si le poste en offre une. Sinon les contrôles qui en
# dépendent se déclarent ignorés — bruyamment.
PG_RECETTE = os.environ.get('RECETTE_PG_URL', '').strip()


def _postgres_joignable(url):
    if not url:
        return False
    try:
        import psycopg
        c = psycopg.connect(url, connect_timeout=3)
        c.close()
        return True
    except Exception:
        return False


PG_DISPO = _postgres_joignable(PG_RECETTE)


# ── LE POOL EST ATTACHÉ AU PROCESSUS QUI L'A OUVERT ──────────────────────
#
# UNE PREMIÈRE VERSION DE CE FICHIER GARDAIT LA MAUVAISE PROPRIÉTÉ. Elle
# exigeait qu'AUCUN pool n'existe après l'import — règle fausse, et vraie
# seulement par accident : la recette importe le module sans `DATABASE_URL`, si
# bien que la règle passait à vide. Avec une base déclarée, l'import ouvre bel
# et bien un pool, parce que les migrations touchent la base à ce moment-là.
#
# Ce n'est pas un défaut : un pool ouvert à l'import est parfaitement sain
# TANT QU'IL RESTE AU PROCESSUS QUI L'A OUVERT. Le défaut, c'est de le SERVIR à
# un autre. C'est cette propriété-là qui est gardée ici.

def test_le_pool_porte_le_pid_de_celui_qui_l_a_ouvert(pools_propres, monkeypatch):
    """La table est indexée par PID, et rien d'autre ne doit décider."""
    monkeypatch.setattr(application, 'REGISTRE_USE_PG', True)
    monkeypatch.setattr(application, 'DATABASE_URL', 'postgresql://x@127.0.0.1:1/x')
    application.registre_pool()
    clefs = set(application._REGISTRE_POOLS) | set(application._REGISTRE_POOL_ECHEC)
    assert clefs == {os.getpid()}, (
        "la table des pools n'est plus indexée par le PID courant : %r" % clefs)


# ── UN POOL HÉRITÉ N'EST NI SERVI NI FERMÉ ───────────────────────────────

class _PoolFactice:
    """Un pool qui note ce qu'on lui fait — sans base, sans socket."""

    def __init__(self):
        self.ferme = False
        self.demandes = 0

    def close(self):
        self.ferme = True

    def getconn(self, *a, **k):
        self.demandes += 1
        raise AssertionError("un pool hérité ne doit jamais être interrogé")


@pytest.fixture
def pools_propres():
    avant = dict(application._REGISTRE_POOLS)
    avant_echec = dict(application._REGISTRE_POOL_ECHEC)
    application._REGISTRE_POOLS.clear()
    application._REGISTRE_POOL_ECHEC.clear()
    yield
    application._REGISTRE_POOLS.clear()
    application._REGISTRE_POOLS.update(avant)
    application._REGISTRE_POOL_ECHEC.clear()
    application._REGISTRE_POOL_ECHEC.update(avant_echec)


def test_un_pool_d_un_autre_processus_n_est_jamais_servi(pools_propres, monkeypatch):
    """C'est le cœur du correctif : le worker ne doit pas recevoir le pool du
    maître, quel que soit ce qu'il trouve en mémoire."""
    monkeypatch.setattr(application, 'REGISTRE_USE_PG', True)
    etranger = _PoolFactice()
    application._REGISTRE_POOLS[os.getpid() + 10_000] = etranger
    # L'ouverture d'un vrai pool échouera (pas de base ici) : ce qui compte est
    # que la fonction ne rende PAS le pool de l'autre processus.
    monkeypatch.setattr(application, 'DATABASE_URL', 'postgresql://x@127.0.0.1:1/x')
    rendu = application.registre_pool()
    assert rendu is not etranger, (
        "registre_pool() a rendu le pool d'un autre processus — c'est "
        "exactement le défaut corrigé")
    assert etranger.demandes == 0


def test_un_pool_d_un_autre_processus_n_est_jamais_ferme(pools_propres, monkeypatch):
    """Ses sockets appartiennent aussi au processus qui les a ouverts. Un
    `close()` y enverrait un paquet de terminaison et casserait SA connexion —
    on abandonne la référence, on ne touche à rien."""
    monkeypatch.setattr(application, 'REGISTRE_USE_PG', True)
    etranger = _PoolFactice()
    application._REGISTRE_POOLS[os.getpid() + 10_000] = etranger
    monkeypatch.setattr(application, 'DATABASE_URL', 'postgresql://x@127.0.0.1:1/x')
    application.registre_pool()
    assert not etranger.ferme, (
        "le pool d'un autre processus a été fermé : cela coupe les connexions "
        "que ce processus utilise encore")


def test_un_echec_d_ouverture_n_est_pas_definitif(pools_propres, monkeypatch):
    """Une base momentanément injoignable au démarrage ne doit pas condamner le
    processus à la connexion directe jusqu'au prochain déploiement."""
    monkeypatch.setattr(application, 'REGISTRE_USE_PG', True)
    monkeypatch.setattr(application, 'DATABASE_URL', 'postgresql://x@127.0.0.1:1/x')
    assert application.registre_pool() is None
    assert os.getpid() in application._REGISTRE_POOL_ECHEC, (
        "l'échec n'est pas mémorisé : le pool sera retenté à chaque requête, "
        "et son attente d'ouverture s'ajoutera au repli")
    # Tant que le délai n'est pas écoulé, on ne retente pas : l'attente
    # d'ouverture s'ajouterait à celle du repli, à chaque requête.
    marque = application._REGISTRE_POOL_ECHEC[os.getpid()]
    assert application.registre_pool() is None
    assert application._REGISTRE_POOL_ECHEC[os.getpid()] == marque, (
        "une nouvelle tentative a eu lieu avant l'expiration du délai : son "
        "coût s'ajoutera à celui du repli, sur chaque requête")

    # Le délai passé, elle doit avoir lieu — et l'horodatage bouger.
    application._REGISTRE_POOL_ECHEC[os.getpid()] = marque - (application.REGISTRE_POOL_RETENTE + 1)
    assert application.registre_pool() is None
    assert application._REGISTRE_POOL_ECHEC[os.getpid()] > marque - application.REGISTRE_POOL_RETENTE, (
        "la ré-tentative n'a pas eu lieu : l'échec est devenu définitif, et le "
        "processus restera en connexion directe jusqu'au prochain déploiement")


# ── LE POINT D'USAGE PASSE PAR LÀ ────────────────────────────────────────

def test_registre_get_db_demande_le_pool_du_processus(monkeypatch):
    """Lire une variable de module donnerait, dans un worker, le pool du
    maître. Le contrôle porte sur l'APPEL, pas sur le nom."""
    appelee = {'n': 0}

    def _faux_pool():
        appelee['n'] += 1
        return None

    monkeypatch.setattr(application, 'REGISTRE_USE_PG', True)
    monkeypatch.setattr(application, 'registre_pool', _faux_pool)
    monkeypatch.setattr(application, 'DATABASE_URL', 'postgresql://x@127.0.0.1:1/x')
    with pytest.raises(Exception):
        application.registre_get_db()
    assert appelee['n'] == 1, (
        "registre_get_db() ne passe plus par registre_pool() : il reprendra le "
        "pool hérité du maître")


def test_le_delai_du_pool_ne_double_pas_celui_du_repli():
    """Attendre longtemps un pool AVANT un repli qui, lui, fonctionne, c'est
    payer deux fois. Le rapport entre les deux réglages est la règle ; le
    chiffre exact ne l'est pas."""
    assert application.REGISTRE_POOL_TIMEOUT <= application.REGISTRE_CONNECT_TIMEOUT, (
        "le délai du pool (%.0f s) dépasse celui d'une connexion directe "
        "(%.0f s) : au-delà, attendre le pool coûte plus cher que de s'en "
        "passer — c'est ce que faisaient les dix secondes d'origine"
        % (application.REGISTRE_POOL_TIMEOUT, application.REGISTRE_CONNECT_TIMEOUT))


def test_le_pool_a_autant_de_place_que_le_service_a_de_fils():
    """Un worker gthread sert `--threads` requêtes à la fois. Un pool plus petit
    que ce nombre fait attendre des fils pour rien — c'est ce que faisait
    `max_size=5` face à huit fils."""
    fils = int(os.environ.get('RECETTE_THREADS', '8'))
    assert application.REGISTRE_POOL_MAX >= fils, (
        "le pool plafonne à %d connexions pour %d fils : %d fils attendront"
        % (application.REGISTRE_POOL_MAX, fils, fils - application.REGISTRE_POOL_MAX))


def test_le_pool_attend_d_etre_rempli_avant_d_etre_rendu():
    """`open=True` DEMANDE le remplissage, il ne l'attend pas : la création des
    connexions est confiée au fil de maintenance. Sans `wait()`, la toute
    première requête du processus court après une file encore vide."""
    d = SOURCE.index('def registre_pool():')
    f = SOURCE.index('\ndef ', d + 10)
    corps = SOURCE[d:f]
    assert 'pool.wait(' in corps, (
        "registre_pool() ne s'assure plus que le pool est rempli avant de le "
        "rendre : la première requête paiera l'ouverture")


# ── CE QUI DEMANDE UNE VRAIE BASE ────────────────────────────────────────

_SCRIPT_FORK = r'''
import os, sys, time
sys.path.insert(0, %(ici)r)
os.environ['DATABASE_URL'] = %(url)r
os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-pool')
import logging; logging.disable(logging.CRITICAL)
import app as A

# Le maître ouvre son pool, comme le ferait un `--preload` suivi d'un usage.
p_maitre = A.registre_pool()
id_maitre = id(p_maitre)

pid = os.fork()
if pid == 0:
    p_enfant = A.registre_pool()
    # 1. l'enfant a SON pool, pas celui du maitre
    distinct = (p_enfant is not None) and (id(p_enfant) != id_maitre)

    # 2. il sait le faire grandir au-dela de ce dont il aurait herite
    gardees, croissance = [], True
    for _ in range(4):
        try:
            gardees.append(p_enfant.getconn(timeout=3))
        except Exception:
            croissance = False
            break
    for c in gardees:
        p_enfant.putconn(c)

    # 3. et il se releve d'une connexion perdue. C'est le point qui decidait
    #    du sort du service : maitre et enfants tenant les memes sockets, une
    #    connexion FINIT par se casser, et sur un pool herite le remplacement
    #    est confie a un fil de maintenance qui n'existe pas.
    c = p_enfant.getconn(timeout=3)
    try:
        c.close()
    except Exception:
        pass
    p_enfant.putconn(c)
    t0 = time.monotonic()
    try:
        c2 = p_enfant.getconn(timeout=3)
        p_enfant.putconn(c2)
        reparation = True
    except Exception:
        reparation = False
    duree = time.monotonic() - t0

    print("DISTINCT=%%s CROISSANCE=%%s N=%%d REPARATION=%%s DUREE=%%.2f"
          %% (distinct, croissance, len(gardees), reparation, duree))
    os._exit(0)
os.waitpid(pid, 0)
''' % {'ici': ICI, 'url': PG_RECETTE}


@pytest.mark.skipif(not PG_DISPO,
                    reason="RECETTE_PG_URL absente ou base injoignable — "
                           "les contrôles de fork sur base réelle sont ignorés")
def test_un_enfant_forke_obtient_son_propre_pool_et_peut_le_faire_grandir():
    r = subprocess.run([sys.executable, '-c', _SCRIPT_FORK],
                       capture_output=True, text=True, timeout=120, cwd=ICI)
    sortie = (r.stdout or '') + (r.stderr or '')
    assert 'DISTINCT=True' in sortie, (
        "l'enfant forké a repris le pool du maître :\n%s" % sortie[-1500:])
    assert 'CROISSANCE=True' in sortie and 'N=4' in sortie, (
        "l'enfant n'a pas pu obtenir quatre connexions : son pool ne grandit "
        "pas, c'est le défaut d'origine :\n%s" % sortie[-1500:])
    assert 'REPARATION=True' in sortie, (
        "l'enfant ne se relève pas d'une connexion perdue : à la première "
        "casse, toutes ses requêtes paieront le délai entier, définitivement "
        "— c'est exactement ce que montrait le journal de production :\n%s"
        % sortie[-1500:])
    m = re.search(r'DUREE=([\d.]+)', sortie)
    assert m and float(m.group(1)) < 1.0, (
        "la reprise après une connexion perdue a coûté %s s : le pool ne "
        "remplace plus ses connexions dans le processus" % (m.group(1) if m else '?'))


def test_l_aveu_d_ignorance_n_est_pas_devenu_un_silence():
    """Un contrôle ignoré que personne ne remarque ne vaut rien. Quand le poste
    DÉCLARE une base de recette, ces contrôles doivent s'exécuter."""
    if not PG_RECETTE:
        pytest.skip("aucune base de recette déclarée : rien à vérifier ici")
    assert PG_DISPO, (
        "RECETTE_PG_URL est déclarée (%s) mais la base ne répond pas : les "
        "contrôles de fork se croient ignorés alors qu'ils sont muets"
        % PG_RECETTE.split('@')[-1])
