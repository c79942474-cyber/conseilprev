"""LES FILS DE FOND APPARTIENNENT AU PROCESSUS QUI SERT LES REQUÊTES.

MÊME CAUSE QUE LE POOL POSTGRES, MÊME JOURNAL. Sous `--preload`, gunicorn
importe le module une fois dans le maître puis forke ses workers, et `fork()`
ne copie pas les fils d'exécution. Relevé sur ce poste, après import puis fork,
avec la version d'avant :

    maître : Thread-1 (_news_warmup), Thread-2 (_auto_boucle),
             pool-1-scheduler, pool-1-worker-0, pool-1-worker-1, pool-1-worker-2
    enfant : aucun

DEUX CONSÉQUENCES, VISIBLES DANS LE JOURNAL DE PRODUCTION.

  1. Le rafraîchissement automatique tournait dans le maître et n'y actualisait
     que SA copie. Les workers servaient des données figées à l'instant du
     fork. Les lignes « EMPS_LIVE 12/27 pays en direct » sont celles d'un
     processus que personne n'interroge.

  2. Le préchauffage de la veille se terminait dix secondes APRÈS le démarrage
     des workers — « [warmup] veille pré-chargée : 48 entrées en 4.3 s » à
     15:10:08, workers démarrés à 15:09:58 — donc entièrement dans le maître.
     Le premier visiteur de chaque worker repayait le chargement complet, qui
     est précisément ce que le préchauffage avait été écrit pour supprimer.

CE QUI DOIT RESTER À L'IMPORT. Le préchauffage du cache de PAGES : il ne
remplit qu'un dictionnaire, et la mémoire, elle, EST copiée par `fork()`. Sous
`--preload`, chaque worker hérite donc d'un cache déjà chaud, gratuitement.
Le déplacer serait perdre cela — et c'est aussi une règle, ci-dessous.

CE QUE CES CONTRÔLES NE PEUVENT PAS FAIRE. Éprouver gunicorn lui-même. Ils
reproduisent ce qui compte — importer, forker, servir une requête — dans un
sous-processus, parce qu'une recette qui importerait le module deux fois de
deux façons dans la même session mesurerait le cache d'import, pas le code.
"""
import io
import os
import re
import subprocess
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()


# ── CE QUE LE SOUS-PROCESSUS VA RAPPORTER ────────────────────────────────

_SONDE = r'''
import os, sys, threading, time, logging
os.environ.setdefault("AUTH_MASTER_TOKEN", "recette_locale_idf_0123456789abcdef")
os.environ.setdefault("FLASK_SECRET_KEY", "recette-fils")
os.environ.pop("DATABASE_URL", None)
sys.path.insert(0, %(ici)r)
logging.disable(logging.CRITICAL)
import app as A

NAV = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/126 Safari/537.36",
       "Accept-Language": "fr-FR,fr;q=0.9", "Accept": "text/html"}

def nos_fils():
    return sorted(t.name for t in threading.enumerate()
                  if t.name in ("auto-maj", "veille-warmup"))

time.sleep(0.6)
print("IMPORT_FILS=%%s" %% ("+".join(nos_fils()) or "-"))
print("IMPORT_PAGES=%%d" %% len(getattr(A, "_PAGE_CACHE", {}) or {}))

pid = os.fork()
if pid == 0:
    c = A.app.test_client()
    c.get("/faq", headers=NAV)
    time.sleep(0.6)
    print("ENFANT_FILS=%%s" %% ("+".join(nos_fils()) or "-"))
    print("ENFANT_PAGES=%%d" %% len(getattr(A, "_PAGE_CACHE", {}) or {}))
    # Une seconde requete ne doit pas redemarrer les memes fils.
    c.get("/faq", headers=NAV)
    time.sleep(0.3)
    tous = [t.name for t in threading.enumerate()]
    print("ENFANT_DOUBLONS=%%d" %% (len([n for n in tous if n == "auto-maj"]) - 1
                                    + len([n for n in tous if n == "veille-warmup"]) - 1))
    os._exit(0)
os.waitpid(pid, 0)
time.sleep(0.3)
print("MAITRE_FILS_APRES=%%s" %% ("+".join(nos_fils()) or "-"))
''' % {'ici': ICI}


@pytest.fixture(scope="module")
def sonde():
    r = subprocess.run([sys.executable, '-c', _SONDE], capture_output=True,
                       text=True, timeout=300, cwd=ICI)
    sortie = (r.stdout or '') + (r.stderr or '')
    releve = dict(re.findall(r'^([A-Z_]+)=(.*)$', sortie, re.M))
    if len(releve) < 5:
        pytest.fail("la sonde n'a rien rapporté d'exploitable :\n%s" % sortie[-2500:])
    return releve


# ── RIEN NE DÉMARRE DANS UN PROCESSUS QUI NE SERT PAS ────────────────────

def test_aucun_fil_de_fond_ne_demarre_au_simple_import(sonde):
    """LA RÈGLE QUI AURAIT ARRÊTÉ LE DÉFAUT. Un fil démarré à l'import est un
    fil que le maître garde pour lui sous `--preload`, et dont aucun worker
    n'hérite."""
    assert sonde['IMPORT_FILS'] == '-', (
        "des fils de fond démarrent au simple import : %s — sous `--preload` "
        "ils tourneront dans le maître, qui ne sert aucune requête"
        % sonde['IMPORT_FILS'])


def test_le_maitre_n_en_demarre_toujours_pas_apres_le_fork(sonde):
    """Le maître vit aussi longtemps que le service. S'il se mettait à
    rafraîchir sa propre copie, ce serait du travail perdu et des appels
    sortants payés pour rien."""
    assert sonde['MAITRE_FILS_APRES'] == '-', (
        "le maître a démarré des fils de fond : %s" % sonde['MAITRE_FILS_APRES'])


# ── CHAQUE WORKER DÉMARRE LES SIENS ──────────────────────────────────────

def test_un_enfant_forke_demarre_ses_propres_fils(sonde):
    presents = set(sonde['ENFANT_FILS'].split('+')) - {''}
    assert presents == {'auto-maj', 'veille-warmup'}, (
        "un worker n'a pas ses fils de fond après sa première requête : %r — "
        "ses données resteront figées à l'instant du fork, et son premier "
        "visiteur repaiera le chargement de la veille" % sorted(presents))


def test_les_fils_ne_sont_demarres_qu_une_fois_par_processus(sonde):
    assert sonde['ENFANT_DOUBLONS'] == '0', (
        "%s fil(s) en double après une seconde requête : la garde par PID ne "
        "tient plus, et chaque requête ajoutera une boucle de "
        "rafraîchissement" % sonde['ENFANT_DOUBLONS'])


# ── CE QUI DOIT RESTER À L'IMPORT ────────────────────────────────────────

def test_le_cache_de_pages_reste_prechauffe_a_l_import(sonde):
    """Il ne remplit qu'un dictionnaire, et la mémoire EST copiée par `fork()`.
    Sous `--preload`, chaque worker hérite d'un cache déjà chaud, gratuitement.
    Le déplacer vers la première requête ferait payer ce que le fork donne."""
    assert int(sonde['IMPORT_PAGES']) >= 20, (
        "le cache de pages n'est plus préchauffé à l'import (%s entrée(s)) : "
        "chaque worker le reconstruira page par page"
        % sonde['IMPORT_PAGES'])


def test_le_cache_de_pages_est_bien_herite_par_l_enfant(sonde):
    """C'est la moitié de la règle précédente, et celle qui la justifie : sans
    héritage, préchauffer à l'import ne servirait à rien."""
    assert int(sonde['ENFANT_PAGES']) >= int(sonde['IMPORT_PAGES']), (
        "l'enfant a moins de pages en cache (%s) que le processus qui a importé "
        "(%s) : l'héritage par fork ne joue plus, et préchauffer à l'import "
        "n'a plus d'objet" % (sonde['ENFANT_PAGES'], sonde['IMPORT_PAGES']))


# ── LE DÉMARRAGE PASSE PAR LA GARDE ──────────────────────────────────────

def test_aucun_demarrage_de_fil_de_fond_hors_de_la_garde():
    """Un `Thread(target=_auto_boucle)` ou `Thread(target=_news_warmup)` posé
    ailleurs ramènerait le défaut sans que la sonde le voie — il suffirait
    qu'il soit conditionnel."""
    d = SOURCE.index('def _demarrer_fils_du_processus():')
    f = SOURCE.index('\n@app.before_request', d)
    for cible in ('_auto_boucle', '_news_warmup'):
        demarrages = [m.start() for m in
                      re.finditer(r'threading\.Thread\([^)]*target=%s' % cible, SOURCE)]
        assert demarrages, "plus aucun fil %s : le contrôle doit être revu" % cible
        hors = [i for i in demarrages if not (d < i < f)]
        assert not hors, (
            "%d démarrage(s) de %s hors de _demarrer_fils_du_processus() — "
            "sous `--preload` ils tourneront dans le maître" % (len(hors), cible))


def test_la_garde_est_branchee_sur_la_premiere_requete():
    """Sans le point d'accroche, la fonction existe et n'est jamais appelée :
    plus aucun rafraîchissement nulle part, ce qui est pire que le défaut."""
    assert '@app.before_request' in SOURCE
    i = SOURCE.index('def _demarrer_fils_du_processus():')
    apres = SOURCE[i:i + 3000]
    assert '@app.before_request' in apres and '_demarrer_fils_du_processus()' in apres, (
        "le démarrage des fils n'est plus branché sur la première requête")
