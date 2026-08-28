"""UN VERROU PRIS AU MOMENT DU fork() RESTE PRIS, ET PLUS PERSONNE NE LE REND.

CE QUI S'EST PASSÉ — une panne totale, sans une ligne de journal.

`fork()` copie la mémoire, les mutex compris, DANS L'ÉTAT OÙ ILS SONT. Il ne
copie pas les fils. Un verrou tenu par un fil du parent à l'instant du fork
arrive donc VERROUILLÉ dans l'enfant, sans propriétaire et sans espoir.

`_PAGE_CACHE_LOCK` était exactement dans ce cas. Le préchauffage du cache de
pages tournait en tâche de fond et tenait ce verrou pendant qu'il lisait,
enrichissait et compressait vingt-cinq pages — dont `sentinel.html` et ses
1,75 Mo. Sous `--preload`, il tournait dans le MAÎTRE, celui-là même que
gunicorn duplique. Quand le fork tombait dans cette fenêtre, chaque page HTML
de chaque worker se bloquait sur ce verrou, définitivement.

RELEVÉ AVEC py-spy, sur les deux workers, une requête `/` en cours :

    Thread "ThreadPoolExecutor-0_0"
        _page_cache_entry (app.py:10685)      ← with _PAGE_CACHE_LOCK
        _serve_page_fast  (app.py:10726)
        view              (app.py:10777)

MESURÉ, gunicorn deux workers, `--preload`, PostgreSQL local :

    avant              après
    /health   0,011 s  /health          0,009 s
    /faq      —        /faq             0,021 s
    /         —        /                0,004 s
    /tarif.   —        /tarifications   0,004 s

Le tiret n'est pas une lenteur : c'est l'absence de réponse au bout de
quarante secondes. `/health` répondait, parce qu'il ne touche pas au cache de
pages — de quoi croire le service en bonne santé pendant qu'il ne servait plus
rien.

CE QUI L'A DÉCLENCHÉ. Le défaut est ancien : le préchauffage démarrait dans un
fil depuis longtemps. C'est une COURSE, et elle ne se gagne pas toujours.
Déplacer `_news_warmup` et `_auto_boucle` hors de l'import — la correction de
la veille — a raccourci la fin de l'import, donc rapproché le fork du moment
où le préchauffage tient son verrou. La course, jusque-là perdue de justesse,
a commencé à être gagnée.

CE QUE CES CONTRÔLES GARDENT. Que le préchauffage ne tourne plus dans un fil ;
que les verrous du module soient remis à neuf dans l'enfant quoi qu'il arrive ;
et — c'est le seul qui compte vraiment — qu'un enfant forké pendant qu'un
verrou est tenu SERVE QUAND MÊME ses pages.
"""
import io
import os
import re
import subprocess
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()


# ── LE PRÉCHAUFFAGE NE TOURNE PLUS DANS UN FIL ───────────────────────────

def _corps_prechauffage():
    d = SOURCE.index('def _prechauffer_cache_pages():')
    f = SOURCE.index('\n_prechauffer_cache_pages()', d)
    return SOURCE[d:f]


def test_le_prechauffage_du_cache_ne_demarre_aucun_fil():
    """LA RÈGLE QUI AURAIT ARRÊTÉ LA PANNE. Sans fil, aucun verrou ne peut être
    tenu au moment où gunicorn se duplique."""
    corps = _corps_prechauffage()
    assert 'threading.Thread' not in corps, (
        "le préchauffage du cache de pages repart dans un fil : sous "
        "`--preload` il tiendra `_PAGE_CACHE_LOCK` pendant que gunicorn forke, "
        "et toutes les pages de tous les workers se bloqueront dessus")
    assert '_travail()' in corps, "le préchauffage n'est plus appelé du tout"


def test_le_prechauffage_reste_appele_au_chargement():
    """Synchrone, oui — mais toujours fait. Sans lui, chaque premier visiteur
    de chaque processus repaie la lecture, l'enrichissement et la compression."""
    assert re.search(r'^_prechauffer_cache_pages\(\)', SOURCE, re.M), (
        "le préchauffage n'est plus déclenché au chargement du module")


# ── LES VERROUS SONT REMIS À NEUF DANS L'ENFANT ──────────────────────────

def test_le_module_se_recale_apres_un_fork():
    """La seconde parade, celle qui protège des fils qu'on ajoutera demain
    sans y penser. `logging` s'en sert déjà pour les siens."""
    assert 'os.register_at_fork' in SOURCE, (
        "plus aucun recalage après fork : un fil ajouté plus tard pourra de "
        "nouveau condamner tous les workers")
    d = SOURCE.index('def _verrous_neufs_dans_l_enfant():')
    f = SOURCE.index('\nif hasattr(os', d)
    corps = SOURCE[d:f]
    for verrou in ('_PAGE_CACHE_LOCK', '_FILS_VERROU', '_REGISTRE_POOL_VERROU'):
        assert verrou in corps, (
            "%s n'est pas remis à neuf dans l'enfant : s'il est tenu au moment "
            "du fork, il ne sera jamais rendu" % verrou)


def test_le_recalage_est_bien_branche_sur_l_enfant():
    """`after_in_child` et pas autre chose : recaler dans le parent ne
    servirait à rien, et recaler avant le fork casserait le parent."""
    # L'APPEL, PAS LA PREMIÈRE MENTION. Une première version cherchait
    # `os.register_at_fork` par son nom : elle tombait sur le commentaire qui
    # l'explique, quinze lignes plus haut, et concluait sur du texte.
    m = re.search(r'os\.register_at_fork\(([^)]*)\)', SOURCE)
    assert m, "l'appel à os.register_at_fork() a disparu"
    assert 'after_in_child=' in m.group(1), (
        "le recalage n'est plus branché sur `after_in_child` mais sur « %s » : "
        "recaler dans le parent ne sert à rien, et recaler avant le fork "
        "casserait le parent" % m.group(1))


# ── LA SEULE RÈGLE QUI COMPTE : L'ENFANT SERT QUAND MÊME ─────────────────

_SONDE = r'''
import os, sys, threading, time, logging
os.environ.setdefault("AUTH_MASTER_TOKEN", "recette_locale_idf_0123456789abcdef")
os.environ.setdefault("FLASK_SECRET_KEY", "recette-verrous")
os.environ.pop("DATABASE_URL", None)
sys.path.insert(0, %(ici)r)
logging.disable(logging.CRITICAL)
import app as A

NAV = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/126 Safari/537.36",
       "Accept-Language": "fr-FR,fr;q=0.9", "Accept": "text/html"}

# ON REPRODUIT LE PIRE CAS, DELIBEREMENT : le verrou du cache de pages est
# tenu au moment precis du fork, comme le faisait le fil de prechauffage.
A._PAGE_CACHE_LOCK.acquire()

pid = os.fork()
if pid == 0:
    # L'ENFANT — un worker gunicorn. Il doit servir malgre le verrou herite.
    # On vide le cache pour forcer le passage par le verrou.
    A._PAGE_CACHE.clear()
    t0 = time.monotonic()
    code = 0
    try:
        r = A.app.test_client().get("/faq", headers=NAV)
        code = r.status_code
    except Exception as e:
        code = -1
    print("ENFANT_CODE=%%d ENFANT_DUREE=%%.2f" %% (code, time.monotonic() - t0))
    sys.stdout.flush()
    os._exit(0)

_, statut = os.waitpid(pid, 0)
A._PAGE_CACHE_LOCK.release()
print("PARENT_OK=1")
''' % {'ici': ICI}


def test_un_enfant_forke_sert_ses_pages_meme_si_un_verrou_etait_tenu():
    """LE CONTRÔLE DÉCISIF, et il reproduit la panne exacte : le verrou du
    cache est tenu à l'instant du fork. Sans recalage, l'enfant se bloque pour
    toujours sur `with _PAGE_CACHE_LOCK` et ce contrôle expire."""
    try:
        r = subprocess.run([sys.executable, '-c', _SONDE], capture_output=True,
                           text=True, timeout=120, cwd='/tmp')
    except subprocess.TimeoutExpired:
        pytest.fail(
            "l'enfant forké ne répond plus : il est bloqué sur un verrou "
            "hérité verrouillé, exactement comme la panne du 28 août")
    sortie = (r.stdout or '') + (r.stderr or '')
    m = re.search(r'ENFANT_CODE=(-?\d+) ENFANT_DUREE=([\d.]+)', sortie)
    assert m, "la sonde n'a rien rapporté :\n%s" % sortie[-2000:]
    assert m.group(1) == '200', (
        "l'enfant a répondu %s au lieu de 200 :\n%s" % (m.group(1), sortie[-1500:]))
    assert float(m.group(2)) < 10.0, (
        "l'enfant a mis %s s à servir une page : le verrou hérité le retient"
        % m.group(2))
    assert 'PARENT_OK=1' in sortie, (
        "le parent n'a pas survécu : le recalage a touché à SES verrous, alors "
        "qu'il ne doit s'appliquer qu'à l'enfant")
