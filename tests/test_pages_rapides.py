"""CE QUE COÛTE UN CLIC DANS LE MENU DE SENTINEL.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande simple : « toutes les pages de
Sentinel à moins de 200 ms ». Avant de corriger quoi que ce soit, il a fallu
chronométrer les cinquante-deux panneaux dans un vrai navigateur, cache intact,
sur le serveur de production (gunicorn). Résultat : `go()` lui-même coûte deux
millisecondes, l'affichage entre douze et quarante-six — et QUATRE panneaux
dépassaient 200 ms, pour trois raisons distinctes.

    pan-sia      275 ms   l'iframe se chargeait au clic
    enveloppe    170 ms   idem
    empreinte    571 ms   appel sortant vers RTE pendant la requête
    ia50         202 ms   soixante millisecondes d'attente fixe, puis deux API

PREMIER DÉFAUT : LE REGISTRE ÉTAIT RETÉLÉCHARGÉ PAR CHACUN DES DIX PANNEAUX QUI
L'AFFICHENT. Un parcours du menu déclenchait DOUZE appels à `/api/registre` —
deux panneaux le demandent deux fois dans le même clic. Même liste, même
client, même seconde. En local l'aller-retour vaut trois millisecondes ; depuis
un navigateur français vers Francfort il en vaut quarante.

DEUXIÈME DÉFAUT : LE PRÉCHARGEMENT DES QUATRE MODULES EN IFRAME ATTENDAIT
`load`. Or `load` n'arrive qu'une fois TOUTES les sous-ressources reçues, la
feuille Google Fonts comprise. Le mécanisme de préchargement existait, était
bien écrit — et ne servait à rien dès que la fonte tardait.

TROISIÈME DÉFAUT : UN APPEL SORTANT SUR LE CHEMIN DE LA REQUÊTE. Le panneau
Empreinte interrogeait ODRE (RTE eCO2mix) avec six secondes de patience,
pendant la requête du visiteur, à chaque expiration du cache de quinze minutes.
C'est le défaut déjà corrigé sur `/api/veille`, au même endroit du raisonnement.

QUATRIÈME DÉFAUT, LE PLUS PETIT : `setTimeout(fn, 60)`. L'intention était bonne
— afficher le panneau avant de lancer un travail lourd — mais soixante
millisecondes ne sont ni le moment de la peinture, ni une borne supérieure.

CE QUE CES CONTRÔLES NE PEUVENT PAS FAIRE. Mesurer un temps de page. Il n'y a
pas de navigateur ici, et le chiffre dépendrait de la machine de compilation.
Ils vérifient les MÉCANISMES dont le chronomètre a montré qu'ils manquaient :
que le registre ne parte qu'une fois, que rien n'attende `load`, qu'aucune
fonction du chemin de requête ne sorte sur le réseau. Le chronomètre, lui,
reste dans le presse-papier de la mise au point, pas dans la recette.
"""
import ast
import io
import os
import re
import sys
import threading
import time

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-pages-rapides')

import app as application  # noqa: E402

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
ARBRE = ast.parse(SOURCE)


def _sans_commentaires(src):
    """Le code, et rien que le code — un automate qui suit les chaînes pour ne
    pas prendre un `//` d'URL pour un commentaire."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'`":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            out.append(src[i:j + 1])
            i = j + 1
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("\n" * src.count("\n", i, j))
            i = j
        elif src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        else:
            out.append(c)
            i += 1
    return "".join(out)


JS = _sans_commentaires(
    io.open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read())


def _corps_py(nom):
    """Le code source d'une fonction de app.py, commentaires exclus — on lit
    l'ARBRE et non le texte, pour qu'une explication en prose ne puisse jamais
    valider une règle."""
    for n in ast.walk(ARBRE):
        if isinstance(n, ast.FunctionDef) and n.name == nom:
            return ast.unparse(n)
    raise AssertionError("fonction %s introuvable dans app.py" % nom)


def _corps_js(debut, fin):
    i = JS.index(debut)
    return JS[i:JS.index(fin, i)]


# ── LE REGISTRE, UNE FOIS AU LIEU DE DIX ─────────────────────────────────

def _lectures_du_registre():
    """Les endroits qui LISENT le registre. Une écriture passe par la même
    adresse — c'est `method:` qui les distingue, et confondre les deux ferait
    passer la règle pour un simple comptage d'URL."""
    lectures, i = [], 0
    while True:
        i = JS.find("fetch('/api/registre'", i)
        if i < 0:
            return lectures
        if 'method:' not in JS[i:i + 90]:
            lectures.append(i)
        i += 1


def test_un_seul_endroit_telecharge_le_registre():
    """LE DÉFAUT MESURÉ : douze appels pour une seule liste."""
    n = len(_lectures_du_registre())
    assert n == 1, (
        "%d endroits téléchargent le registre ; un parcours du menu refait "
        "autant d'allers-retours pour la même liste" % n)


def test_ce_seul_endroit_est_le_chargeur_partage():
    """Un appel unique ne suffit pas : encore faut-il qu'il soit DANS le
    chargeur mémorisé, et non dans un panneau qui aurait gagné la course."""
    i = _lectures_du_registre()[0]
    debut = JS.rindex('window.sentRegistre = function()', 0, i)
    assert 'function' not in JS[debut + 40:i].replace('function()', ''), (
        "la lecture du registre n'est pas celle du chargeur partagé")


def test_les_dix_panneaux_passent_par_le_chargeur_partage():
    """Le compte doit se retrouver de l'autre côté : dix lecteurs, un seul
    téléchargement. Sans cette règle, on pourrait satisfaire la précédente en
    supprimant neuf panneaux."""
    assert JS.count('window.sentRegistre()') == 10, (
        "%d panneaux lisent le registre au lieu des dix mesurés"
        % JS.count('window.sentRegistre()'))


def test_le_chargeur_partage_ne_repart_pas_a_chaque_appel():
    """Sans la promesse gardée, dix appelants dans la même image relanceraient
    dix requêtes : c'est précisément ce qu'on vient de retirer."""
    corps = _corps_js('var _regPromesse = null;', 'window.sentRegistreOublier')
    sans_espaces = corps.replace(' ', '')
    assert 'if(!_regPromesse)' in sans_espaces, "la promesse n'est pas mémorisée"


def test_un_echec_ne_fige_pas_le_registre_pour_la_session():
    """Une promesse rejetée qui resterait en cache condamnerait le registre
    jusqu'au rechargement de la page. Le chargeur d'authentification a déjà
    cette précaution ; celui-ci doit l'avoir aussi."""
    corps = _corps_js('window.sentRegistre = function()', 'window.sentRegistreOublier')
    assert '_regPromesse = null' in corps.split('.catch')[-1], (
        "un échec réseau garde la promesse rejetée : plus aucun panneau ne "
        "pourra recharger le registre")


def test_le_statut_reste_lisible_par_les_deux_appelants_qui_en_ont_besoin():
    """Le registre et la FRIA affichent « session expirée » plutôt qu'une liste
    vide. En mutualisant l'appel, on ne doit pas leur retirer le statut."""
    corps = _corps_js('window.sentRegistre = function()', 'window.sentRegistreOublier')
    assert '_statut' in corps
    assert JS.count('d._statut === 401 || d._statut === 403') == 2, (
        "les deux appelants qui distinguaient 401 et 403 ne le font plus")
    for ancre in ('REG_DATA = d.systemes', 'FRIA_REG_CACHE = d.systemes'):
        i = JS.index(ancre)
        assert 'Session expirée' in JS[max(0, i - 900):i], (
            "« %s » ne distingue plus une session expirée d'un registre vide"
            % ancre)


@pytest.mark.parametrize('apres', ['window.sentRegistreOublier();'])
def test_une_ecriture_perime_le_cache_partage(apres):
    """SANS CELA, LE DÉFAUT SERAIT PIRE QUE CELUI CORRIGÉ. Après un ajout ou
    une suppression, les neuf autres panneaux montreraient le registre d'avant
    l'édition — un cache silencieusement faux, jusqu'au prochain rechargement
    complet de la page."""
    assert JS.count(apres) >= 2, (
        "moins de deux points d'écriture périment le cache partagé "
        "(enregistrement et suppression)")
    # Et l'oubli doit précéder le rendu, sinon un panneau relu dans la foulée
    # reprendrait l'ancienne promesse.
    for ancre in ('REG_DATA = REG_DATA.filter', 'if(REG_EDIT_ID){'):
        i = JS.index(ancre)
        assert 'sentRegistreOublier' in JS[max(0, i - 700):i], (
            "l'écriture « %s » ne périme pas le cache avant de rendre" % ancre)


# ── LE PRÉCHARGEMENT NE DÉPEND PLUS D'UNE RESSOURCE TIERCE ───────────────

def _bloc_prechargement():
    """Du chargeur d'iframe jusqu'au bloc suivant. L'ancre de fin est du CODE
    et non un commentaire : les commentaires sont retirés avant lecture, et
    s'ancrer dessus reviendrait à faire dépendre une règle d'une prose."""
    return _corps_js('function charger(id){', 'var SUIVIS = [')


def test_le_prechargement_des_modules_nattend_pas_load():
    """LE DÉFAUT. `load` attend TOUTES les sous-ressources, la feuille Google
    Fonts comprise. Le préchargement des quatre iframes en dépendait ; mesuré
    avec cette feuille en attente : 275 ms pour Panorama, 170 pour Enveloppe,
    payés sous les yeux de l'utilisateur à chaque clic."""
    bloc = _bloc_prechargement()
    assert "addEventListener('load', demarrer)" not in bloc.replace('"', "'"), (
        "le préchargement des modules attend encore `load` : il ne se produira "
        "pas tant qu'une ressource tierce n'est pas arrivée")
    assert 'DOMContentLoaded' in bloc


def test_le_prechargement_reste_au_second_plan():
    """On retire une dépendance, on ne prend pas de priorité : sans
    `requestIdleCallback`, quatre pages en iframe partiraient en concurrence du
    chargement de Sentinel lui-même."""
    bloc = _bloc_prechargement()
    assert 'requestIdleCallback' in bloc, (
        "le préchargement ne passe plus par le temps mort du navigateur : il "
        "concurrence désormais l'affichage de la page")


def test_le_survol_reste_le_chemin_le_plus_court():
    """Si l'utilisateur va plus vite que le temps mort, le survol de l'entrée
    de menu doit encore lancer le chargement."""
    bloc = _bloc_prechargement()
    for ev in ('mouseenter', 'focus', 'touchstart'):
        assert ev in bloc


# ── L'INITIALISATION DIFFÉRÉE VISE LA PEINTURE, PAS UNE HORLOGE ──────────

def test_aucun_panneau_nattend_un_delai_fixe():
    """LE DÉFAUT. Huit panneaux attendaient 60 ms — ni le moment de la
    peinture, ni une borne supérieure. Sur `ia50`, mesuré à 202 ms, ces
    soixante millisecondes suffisaient à faire dépasser la barre.

    LE COMPTEUR ÉTAIT FIGÉ À HUIT, et il a fait tomber cette règle le jour où
    un NEUVIÈME panneau est arrivé — en annonçant un défaut de délai fixe qui
    n'existait pas. Ce qu'il gardait était juste : que l'extraction ait bien
    trouvé quelque chose. Ce qu'il gardait mal était la manière : un nombre
    qu'il faut mettre à jour à chaque panneau finit par être mis à jour sans
    qu'on relise ce qu'il protège.

    LA PROPRIÉTÉ, ELLE, NE COMPTE RIEN : aucune initialisation de panneau ne
    passe par une horloge — ni `setTimeout(…, <nombre>)` — et il en existe au
    moins une qui passe par `_apresPeinture`, faute de quoi l'extraction aurait
    trouvé un corps vide et se serait tue."""
    i = JS.index('function go(id, el, sec, pg)')
    corps = JS[i:JS.index('\nfunction ', i + 10)]
    horloges = re.findall(r"setTimeout\([^;]*?,\s*(\d+)\s*\)", corps)
    # `navRefresh` est le seul délai admis : il rafraîchit la barre latérale,
    # il n'initialise aucun panneau. Il est nommé, donc distinguable.
    horloges_de_panneau = [h for h in re.findall(
        r"setTimeout\(\s*(?!window\.navRefresh)[^;]*?,\s*\d+\s*\)", corps)]
    assert not horloges_de_panneau, (
        "un panneau attend encore un délai fixe avant de s'initialiser : %s"
        % horloges_de_panneau[:3])
    assert '_apresPeinture(' in corps, (
        "aucune initialisation différée ne passe par _apresPeinture : "
        "l'extraction a-t-elle trouvé le bon corps de fonction ?")
    assert horloges, (
        "plus aucun setTimeout dans `go` : la règle ne distingue plus rien")


def test_apres_peinture_sexecute_bien_apres_la_peinture():
    """`requestAnimationFrame` se déclenche AVANT la peinture de l'image
    suivante : un travail lourd placé directement dedans bloquerait l'affichage
    qu'on cherchait justement à laisser passer. C'est le `setTimeout` qu'il
    enveloppe qui s'exécute après."""
    corps = _corps_js('function _apresPeinture(fn)', '\nfunction go(')
    assert 'requestAnimationFrame(function(){ setTimeout(fn, 0); })' in corps, (
        "l'initialisation repart avant la peinture, pas après")
    assert 'setTimeout(fn, 60)' in corps, (
        "aucun repli là où requestAnimationFrame n'existe pas")


# ── AUCUNE PAGE N'ATTEND UN SERVEUR ÉTRANGER ─────────────────────────────

@pytest.mark.parametrize('fonction', ['_emp_intensite_fr', '_emp_intensite_de'])
def test_lintensite_carbone_ne_sort_pas_sur_le_reseau(fonction):
    """LE DÉFAUT MESURÉ : 571 ms sur le panneau Empreinte, dont l'essentiel
    dans un appel à ODRE fait PENDANT la requête du visiteur, avec six secondes
    de patience, à chaque expiration du cache de quinze minutes."""
    corps = _corps_py(fonction)
    assert 'requests.get' not in corps, (
        "%s appelle un serveur étranger sur le chemin de la requête" % fonction)
    assert '_emp_relever_en_fond' in corps


@pytest.mark.parametrize('fonction', ['_emp_collecter_fr', '_emp_collecter_de'])
def test_le_releve_lui_meme_existe_toujours(fonction):
    """Déplacer l'appel ne doit pas revenir à le supprimer : sans relevé, la
    plateforme afficherait éternellement le facteur par défaut."""
    corps = _corps_py(fonction)
    assert 'requests.get' in corps, "%s ne relève plus rien" % fonction


def test_une_intensite_est_servie_immediatement_meme_sans_reseau(monkeypatch):
    """Le contrôle qui compte : avec un serveur distant qui ne répond jamais,
    la fonction doit rendre la main tout de suite."""
    application._EMP_INT_CACHE.update({'ts': 0.0, 'val': None, 'src': ''})
    application._EMP_INT_VERROUS.clear()

    def _interminable(*a, **k):
        time.sleep(30)
    monkeypatch.setattr(application.requests, 'get', _interminable)

    t = time.perf_counter()
    val, src = application._emp_intensite_fr()
    d = (time.perf_counter() - t) * 1000
    assert d < 100, "l'intensité carbone met %.0f ms : la page attend" % d
    assert val == application.EMP_INTENSITE_DEFAUT['FR']
    assert 'defaut' in src.lower() or 'défaut' in src.lower(), (
        "un chiffre de repli servi sans le dire : la source doit porter la "
        "mention, c'est elle qui fait la différence entre approché et faux")


def test_le_releve_de_fond_met_bien_le_cache_a_jour(monkeypatch):
    """Un relevé en tâche de fond qui n'aboutirait jamais reviendrait à figer
    la valeur par défaut pour toujours."""
    application._EMP_INT_CACHE.update({'ts': 0.0, 'val': None, 'src': ''})
    application._EMP_INT_VERROUS.clear()
    monkeypatch.setattr(
        application, '_emp_collecter_fr',
        lambda: application._EMP_INT_CACHE.update(
            {'ts': time.time(), 'val': 42.0, 'src': 'relevé de recette'}))

    application._emp_intensite_fr()
    for _ in range(100):
        if application._EMP_INT_CACHE['val'] == 42.0:
            break
        time.sleep(0.02)
    assert application._EMP_INT_CACHE['val'] == 42.0, (
        "le relevé de fond n'a jamais rafraîchi le cache")
    assert application._emp_intensite_fr()[0] == 42.0


def test_une_rafale_de_visiteurs_ne_lance_quun_seul_releve(monkeypatch):
    """Sans verrou, vingt visiteurs simultanés lanceraient vingt fils vers le
    même serveur — au moment précis où il répond mal."""
    application._EMP_INT_CACHE.update({'ts': 0.0, 'val': None, 'src': ''})
    application._EMP_INT_VERROUS.clear()
    appels = []
    barriere = threading.Event()

    def _lent():
        appels.append(1)
        barriere.wait(2)
    monkeypatch.setattr(application, '_emp_collecter_fr', _lent)

    fils = [threading.Thread(target=application._emp_intensite_fr) for _ in range(20)]
    for f in fils:
        f.start()
    for f in fils:
        f.join(3)
    time.sleep(0.1)
    barriere.set()
    assert len(appels) == 1, (
        "%d relevés lancés en parallèle vers le même serveur" % len(appels))


def test_une_valeur_fraiche_ne_declenche_aucun_releve(monkeypatch):
    """Le contraire du défaut : relever à chaque requête serait aussi coûteux
    pour le serveur distant que l'ancien code l'était pour le visiteur."""
    application._EMP_INT_CACHE.update(
        {'ts': time.time(), 'val': 51.0, 'src': 'frais'})
    application._EMP_INT_VERROUS.clear()
    appels = []
    monkeypatch.setattr(application, '_emp_collecter_fr', lambda: appels.append(1))
    for _ in range(5):
        application._emp_intensite_fr()
    time.sleep(0.1)
    assert appels == [], "une valeur fraîche déclenche quand même un relevé"


def test_le_delai_de_fraicheur_reste_celui_de_la_source():
    """RTE publie au pas de quinze minutes. Relever plus souvent ne rendrait
    pas la valeur plus juste, seulement le serveur distant plus sollicité."""
    assert application._EMP_INT_FRAIS == 900


def test_le_prechauffage_lance_les_deux_releves():
    """Sinon la fenêtre pendant laquelle on sert le facteur par défaut dure
    jusqu'au premier curieux, et non quelques secondes."""
    corps = _corps_py('_news_warmup')
    assert '_emp_prechauffer_intensites()' in corps
    i = corps.index('_emp_prechauffer_intensites()')
    assert 'except' in corps[i:], "le préchauffage des intensités n'est pas protégé"


def test_lendpoint_empreinte_repond_vite_meme_reseau_coupe(monkeypatch):
    """Bout en bout : c'est cette route que le panneau appelle, et c'est elle
    qui mettait 571 ms."""
    application._EMP_INT_CACHE.update({'ts': 0.0, 'val': None, 'src': ''})
    application._EMP_INT_VERROUS.clear()
    monkeypatch.setattr(application.requests, 'get',
                        lambda *a, **k: time.sleep(30))
    c = application.app.test_client()
    t = time.perf_counter()
    r = c.get('/api/empreinte/live',
              headers={'X-Forwarded-For': '198.51.100.61',
                       'User-Agent': 'Mozilla/5.0 (recette)'})
    d = (time.perf_counter() - t) * 1000
    assert r.status_code in (200, 302, 401, 403), r.status_code
    assert d < 200, "/api/empreinte/live met %.0f ms" % d
