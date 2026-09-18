# -*- coding: utf-8 -*-
"""Un essai ne doit pas hériter du limiteur de débit de celui d'avant.

L'INCIDENT. Deux essais d'authentification ont échoué UNE FOIS, puis sont
repassés. Le message disait « la session de l'intrus survit au changement de
mot de passe » — une phrase qui envoie chercher un défaut de session. Il n'y en
a pas.

CE QUI EST MESURÉ. À chaque passage, `test_un_chemin_a_saisie_libre_reste_protege`
envoie `/api/registre?q=' OR 1=1--` pour vérifier le filtre anti-injection. Le
filtre fait son travail et bloque l'adresse UNE HEURE
(`limiter.block(ip, 3600, 'injection_attempt')`). L'essai est juste ; son effet
de bord survivait à tout le reste de la recette.

CE QUE J'AI CRU À TORT, et qui ne doit pas se transmettre : l'ordre n'est pas
tiré au sort (aucun greffon d'ordre aléatoire n'est installé), et la rotation
d'adresses ne boucle PAS aujourd'hui — 72 appels mesurés sur un cycle de 250.
Elle emploie un modulo, donc elle peut boucler : le piège est à 178 appels de
se refermer, pas plus.

L'OCCURRENCE OBSERVÉE N'A PAS ÉTÉ REPRODUITE. Ce fichier garde la CLASSE de
défaut, éprouvée par une reproduction délibérée qui, sans isolation, fait
tomber 18 essais sur 47.

LE MÉCANISME, ET IL EST PLUS LARGE QUE LE LIMITEUR. `check()` compte par
(adresse, route) — sa docstring dit pourquoi : « pour ne pas pénaliser
globalement une IP active sur plusieurs routes différentes ». Mais au troisième
dépassement elle appelle `block(ip, 30)`, et l'adresse entre dans
`self.blocked` — que le `before_request` consulte pour TOUTE requête, par deux
chemins indépendants : le contrôle « IP bloquée » d'abord, puis la limite
globale de 120 req/min, dont le `check()` commence lui aussi par `is_blocked`.
Trois dépassements sur une route quelconque ferment donc le site entier à cette
adresse : trente secondes, puis cent vingt, puis six cents.

DEUX CONSÉQUENCES POUR CE FICHIER. La sonde vise une route SANS limiteur — si
elle refuse, ce n'est pas son propre compteur qui parle. Et une mutation qui ne
couperait qu'un des deux chemins laisserait la règle verte : vérifié, il faut
les couper tous les deux pour la faire tomber.

Les essais d'authentification distribuent leurs requêtes sur 250 adresses pour
ne pas se limiter eux-mêmes, et ce compteur BOUCLE. Il suffit qu'un autre
fichier ait fait bloquer l'une de ces adresses pour qu'une requête reçoive 429
là où l'essai attend 200. Aucun `conftest.py` n'existait, et aucun essai ne
touchait au limiteur : son état traversait toute la recette.

CE QUE CE FICHIER GARDE. Pas une intention — un CHEMIN. Il salit le limiteur,
constate qu'une route publique refuse, remet à zéro, et constate qu'elle
accepte. Si la remise à zéro disparaît ou devient partielle, la reproduction
retombe ici plutôt qu'au hasard sur un essai d'authentification, dans un
message qui parlerait d'autre chose.

CE QUI N'EST PAS CORRIGÉ, ET C'EST VOULU. Le comportement de l'application ne
change pas : bloquer une adresse qui insiste est une décision d'anti-abus, et
sa docstring décrit les deux moitiés. Ce qui manquait était l'isolation de la
recette.
"""
import os
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import app as A                                                    # noqa: E402
import conftest as CONF                                            # noqa: E402

# UNE ROUTE SANS AUCUN LIMITEUR, ET C'EST TOUT L'INTÉRÊT. Sonder une route
# limitée laisserait un doute : son propre compteur aurait pu répondre à sa
# place. `/robots.txt` n'a pas de décorateur de débit — si elle refuse, c'est
# le blocage global du `before_request` qui parle, et rien d'autre.
SONDE = "/robots.txt"
ADRESSE = "203.0.113.42"           # hors de la plage employée ailleurs
ENTETES = {"X-Forwarded-For": ADRESSE, "User-Agent": "Mozilla/5.0 (recette)"}


def _salir(adresse=ADRESSE, route="une_autre_route"):
    """Ce qu'un autre fichier de recette produit sans le vouloir : assez de
    dépassements sur UNE route pour que l'adresse soit bloquée sur TOUTES."""
    for _ in range(40):
        A.limiter.check(adresse, limit=1, window=300, endpoint=route)


# ═══════════════════════════════════════════════════════════════════════════
#  1. LE CHEMIN, REJOUÉ EN ENTIER
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_POINT_QUI_DECIDE_un_blocage_herite_ferme_une_route_sans_rapport():
    """LA REPRODUCTION, ET LA CURE, DANS LE MÊME ESSAI.

    Salir puis sonder prouve que le mécanisme est réel ; remettre à zéro puis
    sonder à nouveau prouve que la remise à zéro le défait. Les deux moitiés
    sont nécessaires : sans la première, la règle pourrait passer sur une
    application où le blocage n'existe plus et ne garderait plus rien.
    """
    client = A.app.test_client()
    assert client.get(SONDE, headers=ENTETES).status_code == 200, (
        "la sonde ne répond pas 200 sur un limiteur propre : la règle ne peut "
        "rien distinguer")

    _salir()
    assert A.limiter.is_blocked(ADRESSE), (
        "des dépassements répétés ne bloquent plus l'adresse : le mécanisme "
        "reproduit n'existe plus, et cette règle ne garde plus rien")
    assert client.get(SONDE, headers=ENTETES).status_code == 429, (
        "une route SANS RAPPORT avec la route saturée répond encore 200 — "
        "le blocage n'est plus global, revoir ce que cette règle affirme")

    CONF.reinitialiser_limiteur()
    assert client.get(SONDE, headers=ENTETES).status_code == 200, (
        "la remise à zéro ne rend pas la main : un essai continuerait "
        "d'hériter du limiteur de celui d'avant")


# ═══════════════════════════════════════════════════════════════════════════
#  2. LA REMISE À ZÉRO EST COMPLÈTE, ET LE RESTE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_remise_a_zero_vide_TOUT_ce_que_le_limiteur_porte():
    """DÉRIVÉE, JAMAIS ÉNUMÉRÉE. `RateLimiter` porte cinq dictionnaires
    aujourd'hui. Les nommer un par un ferait qu'un sixième, ajouté demain, ne
    serait pas nettoyé — et l'essai suivant en hériterait sans que rien ne le
    dise. La règle lit les attributs de l'instance, quels qu'ils soient."""
    _salir("203.0.113.51")
    A.limiter.check("203.0.113.52", limit=99, window=60, endpoint="chat")
    A.limiter.chat_req["203.0.113.53"].append(0)
    pleins = [nom for nom, v in vars(A.limiter).items() if v]
    assert len(pleins) >= 4, (
        "l'état à nettoyer est trop mince pour que la règle prouve quoi que "
        "ce soit : %s" % pleins)

    nettoyes = CONF.reinitialiser_limiteur()
    # ═══ LE COMPTE PORTE SUR TOUS LES GARDIENS, PAS SUR UN SEUL ════════
    # La remise à zéro dérivait les ATTRIBUTS d'un limiteur mais ÉNUMÉRAIT
    # l'objet. Il y en avait déjà deux — `bf_protector` bloque un courriel
    # cinq minutes après cinq connexions ratées — et rien ne le vidait.
    # L'attendu se DÉRIVE donc lui aussi : l'écrire en dur ici replacerait
    # exactement le défaut qu'on vient de corriger, un cran plus bas.
    attendu = sum(len(vars(g)) for _n, g in CONF.gardiens(A))
    assert nettoyes == attendu, (
        "la remise à zéro a nettoyé %d attributs pour %d portés par les "
        "gardiens : elle n'a pas parcouru tout ce qui peut refuser un "
        "appelant" % (nettoyes, attendu))
    for nom_g, g in CONF.gardiens(A):
        restants = {nom: v for nom, v in vars(g).items() if v}
        assert not restants, (
            "des états survivent à la remise à zéro dans %s : %s"
            % (nom_g, restants))


def test_la_remise_a_zero_refuse_ce_qu_elle_ne_sait_pas_vider():
    """UN ATTRIBUT SAUTÉ EN SILENCE EST LE DÉFAUT QU'ON CORRIGE. Le jour où
    `RateLimiter` porte un compteur entier plutôt qu'un dictionnaire, la remise
    à zéro doit s'arrêter et demander une décision — pas l'ignorer poliment."""
    A.limiter.compteur_de_recette = 7            # ne sait pas se vider
    try:
        with pytest.raises(AssertionError) as leve:
            CONF.reinitialiser_limiteur()
        assert "compteur_de_recette" in str(leve.value)
    finally:
        del A.limiter.compteur_de_recette
    CONF.reinitialiser_limiteur()


def test_la_remise_a_zero_encadre_l_essai_DES_DEUX_COTES():
    """AVANT POUR NE PAS HÉRITER, APRÈS POUR NE PAS LÉGUER.

    POURQUOI CETTE RÈGLE LIT LA FORME PLUTÔT QUE L'EFFET, alors que ce fichier
    préfère partout l'inverse. Tant que la moitié « après » fonctionne, aucun
    essai ne peut OBSERVER l'absence de la moitié « avant » : il trouve un
    limiteur propre dans les deux cas. Une mutation qui supprime la première
    survivait donc à toutes les règles de ce fichier — vérifié.

    Ce que la moitié « avant » couvre, et que l'autre ne couvre pas : la saleté
    produite HORS d'un essai — au moment de la collecte, à l'import d'un module
    qui touche au limiteur, ou par un essai qui s'exempterait de la fixture. On
    ne peut pas la mettre en scène sans fabriquer exprès l'un de ces cas ; on
    exige donc que l'appel soit là, des deux côtés du `yield`."""
    import inspect
    corps = inspect.getsource(CONF.limiteur_propre)
    assert corps.count("yield") == 1, (
        "la fixture a changé de forme : la règle ne sait plus où couper")
    avant, apres = corps.split("yield")
    assert "reinitialiser_limiteur()" in avant, (
        "la fixture ne nettoie plus AVANT l'essai : un état produit hors essai "
        "— à l'import d'un module, à la collecte — serait hérité")
    assert "reinitialiser_limiteur()" in apres, (
        "la fixture ne nettoie plus APRÈS l'essai : un essai qui s'exempterait "
        "de la fixture hériterait du précédent")


def test_la_remise_a_zero_ne_charge_pas_l_application_pour_rien():
    """Les fichiers qui n'éprouvent aucune route n'ont pas d'état à nettoyer.
    Leur faire payer l'import d'`app.py` — plus d'une seconde — pour vider des
    dictionnaires qui n'existent pas serait un coût pris à chaque essai."""
    import inspect
    corps = inspect.getsource(CONF.reinitialiser_limiteur)
    assert "sys.modules.get" in corps, (
        "la remise à zéro importe l'application au lieu de regarder si elle "
        "est déjà chargée")
    assert "import app" not in corps


# ═══════════════════════════════════════════════════════════════════════════
#  3. L'ISOLATION S'APPLIQUE SANS QUE PERSONNE AIT À Y PENSER
# ═══════════════════════════════════════════════════════════════════════════

def test_la_fixture_est_automatique():
    """Une isolation qu'il faut demander est une isolation qu'on oublie. Les
    quarante-sept essais d'authentification n'en savent rien, et c'est la
    condition pour qu'ils cessent de dépendre de l'ordre de passage."""
    # LE NOM DE L'ATTRIBUT A CHANGÉ ENTRE DEUX VERSIONS DE PYTEST — c'était
    # `_pytestfixturefunction`, c'est `_fixture_function_marker` depuis la 8.4.
    # Les essayer tous les deux évite qu'une mise à jour de l'outil fasse
    # tomber une règle qui parle du produit, pas de l'outil.
    marque = (getattr(CONF.limiteur_propre, "_fixture_function_marker", None)
              or getattr(CONF.limiteur_propre, "_pytestfixturefunction", None))
    assert marque is not None, (
        "`limiteur_propre` n'est pas une fixture — ou pytest a encore renommé "
        "sa marque : vérifier avant de conclure")
    assert marque.autouse is True, (
        "la fixture doit être demandée pour s'appliquer : les essais existants "
        "ne la demandent pas")
    assert marque.scope == "function", (
        "une fixture de portée plus large ne nettoierait pas ENTRE les essais, "
        "seulement entre les fichiers ou les sessions")


def test_chaque_essai_part_d_un_limiteur_vide():
    """La preuve par l'essai courant : la fixture a tourné avant celui-ci, et
    l'essai précédent de ce fichier a laissé le limiteur sale à dessein."""
    assert not any(vars(A.limiter).values()), (
        "cet essai hérite d'un limiteur non vide : %s"
        % {n: v for n, v in vars(A.limiter).items() if v})


def test_le_pollueur_existe_toujours_et_bloque_toujours_une_heure():
    """LE FAIT MESURÉ, GARDÉ LÀ OÙ ON LE CHERCHERA.

    `test_un_chemin_a_saisie_libre_reste_protege` envoie
    `/api/registre?q=' OR 1=1--` pour vérifier que le filtre anti-injection
    s'applique aux chemins à saisie libre. Le filtre fait son travail — et
    bloque l'adresse UNE HEURE. L'essai est juste ; c'est son effet de bord qui
    survivait à toute la recette.

    LA RÈGLE NE JUGE PAS CET ESSAI. Elle constate qu'il produit encore un
    blocage : le jour où le filtre cesserait de bloquer, cette explication
    deviendrait fausse, et l'isolation perdrait sa raison écrite. Elle rejoue
    donc le geste, sur une adresse à elle."""
    client = A.app.test_client()
    adresse = "203.0.113.77"
    entetes = {"X-Forwarded-For": adresse, "User-Agent": "Mozilla/5.0 (recette)"}
    client.get("/api/registre?q=' OR 1=1--", headers=entetes)
    assert A.limiter.is_blocked(adresse), (
        "une tentative d'injection ne bloque plus l'adresse : le pollueur "
        "décrit dans ce fichier n'existe plus, vérifier ce que l'isolation "
        "protège encore")
    reste = A.limiter.blocked[adresse] - __import__("time").time()
    assert reste > 3000, (
        "le blocage ne dure plus une heure mais %.0f s — l'ordre de grandeur "
        "qui rend l'incident possible a changé" % reste)


def test_la_rotation_d_adresses_peut_boucler_meme_si_elle_ne_boucle_pas_encore():
    """LA MARGE, MESURÉE PLUTÔT QU'AFFIRMÉE. Les essais d'authentification
    tournent sur 250 adresses pour ne pas se limiter eux-mêmes, et le compteur
    est un MODULO : la rotation peut revenir sur ses pas. Mesuré, elle n'en
    emploie que 72 — 29 % du cycle. Le piège est donc armé sans être déclenché,
    à 178 appels de se refermer.

    LA RÈGLE GARDE LES DEUX MOITIÉS : que le modulo soit toujours là (sinon
    l'explication de ce fichier est à revoir), et que la marge soit encore
    connue. Elle ne fixe AUCUN plafond au nombre d'appels : l'isolation rend le
    bouclage inoffensif, et interdire au fichier de grandir serait garder la
    conséquence au lieu de la cause."""
    import io
    import re
    source = io.open(os.path.join(ICI, "tests",
                                  "test_inscription_et_connexion.py"),
                     encoding="utf-8").read()
    rotation = re.search(r"X-Forwarded-For':\s*'[\d.]*%d'\s*%\s*\(([^)]*)\)",
                         source)
    assert rotation, ("la rotation d'adresses a changé de forme : vérifier que "
                      "ce fichier décrit encore le bon mécanisme")
    assert "%" in rotation.group(1), (
        "la rotation n'emploie plus de modulo : si elle ne peut plus boucler, "
        "cette règle et son explication sont à revoir")
    modulo = re.search(r"%\s*(\d+)", rotation.group(1))
    assert modulo and int(modulo.group(1)) >= 100, (
        "le cycle d'adresses s'est raccourci à %s : la rotation boucle "
        "beaucoup plus tôt qu'à la mesure, et l'isolation devient la seule "
        "chose qui tienne" % (modulo.group(1) if modulo else "?"))


# ═══════════════════════════════════════════════════════════════════════════
#  LE SECOND GARDIEN — CELUI QUE PERSONNE NE NETTOYAIT
# ═══════════════════════════════════════════════════════════════════════════
#
# L'INTERMITTENCE OBSERVÉE, ET CE QU'ELLE ÉTAIT VRAIMENT.
# `test_un_changement_de_mot_de_passe_coupe_les_sessions_ouvertes` a échoué une
# fois sur trois en recette complète, et passait isolément. Le `conftest`
# décrivait un piège voisin — une adresse bloquée une heure et une rotation
# modulo — mais ce n'était pas celui-là.
#
# LA CAUSE, REPRODUITE SANS RIEN SUPPOSER. `/api/sentinel-auth/login` est gardé
# par un SECOND objet, `bf_protector`, clé `login:<courriel>` : cinq connexions
# ratées bloquent ce courriel cinq minutes, puis jusqu'à une heure. La remise à
# zéro de la recette dérivait les ATTRIBUTS d'un limiteur — le raisonnement est
# écrit en tête du conftest — mais ÉNUMÉRAIT l'objet. Elle nettoyait cinq
# attributs de `limiter` et zéro du protecteur. L'essai suivant qui se connecte
# avec ce courriel reçoit 429 là où il attend 200 ; au second passage le
# blocage a expiré, et la recette redevient verte. C'est la définition même
# d'une intermittence qu'on ne trouve pas en relançant.
#
# LES COURRIELS D'ESSAI SONT DÉRIVÉS DU MÊME COMPTEUR que les adresses —
# `recette<N>@exemple-test.fr` — ce qui donne au blocage une chance réelle de
# retomber sur un courriel réutilisé.

def _bloquer_un_courriel(courriel="recette-isolation@exemple-test.fr"):
    """Cinq connexions ratées : c'est le seuil du protecteur."""
    cle = "login:%s" % courriel
    for _ in range(5):
        A.bf_protector.record_attempt(cle, success=False)
    return courriel, cle


def test_LE_DEFAUT_le_protecteur_anti_force_brute_survivait_a_la_remise_a_zero():
    """LA RÈGLE QUI PORTE CETTE SECTION.

    Elle rejoue le chemin : on bloque, on remet à zéro, on regarde. Sans le
    correctif, le protecteur reste bloqué et la règle tombe.
    """
    courriel, cle = _bloquer_un_courriel()
    assert A.bf_protector.is_blocked(cle), \
        "le protecteur ne bloque plus après cinq échecs : la règle ne mesure rien"
    CONF.reinitialiser_limiteur()
    assert not A.bf_protector.is_blocked(cle), (
        "le blocage de « %s » survit à la remise à zéro : il fuira vers "
        "l'essai suivant qui se connecte avec ce courriel" % courriel)


def test_LE_TEMOIN_la_route_de_connexion_ne_rend_plus_429_apres_remise_a_zero():
    """LE VOLET QUI COMPTE VRAIMENT — celui du symptôme, pas de l'état interne.

    Une implémentation qui viderait `blocked` sans vider `attempts` passerait
    la règle précédente : le courriel n'est plus bloqué, mais il lui reste
    quatre échecs au compteur et le cinquième le rebloque aussitôt. On mesure
    donc ce que l'essai suivant REÇOIT.
    """
    courriel, cle = _bloquer_un_courriel()
    CONF.reinitialiser_limiteur()
    # LE COMPTEUR D'ESSAIS EST VIDE, pas seulement le blocage — et on le
    # regarde AVANT la requête, parce que celle-ci en ajoutera un
    # légitimement. Sans ce volet, une remise à zéro qui ne viderait que
    # `blocked` passerait : le courriel n'est plus bloqué, il lui reste
    # quatre échecs, et le cinquième le rebloque aussitôt.
    assert not A.bf_protector.attempts.get(cle), \
        "des tentatives héritées subsistent : le prochain échec rebloque"
    c = A.app.test_client()
    r = c.post("/api/sentinel-auth/login",
               headers={"X-Forwarded-For": "198.51.100.211"},
               json={"email": courriel, "password": "MauvaisMotDePasse!1"})
    assert r.status_code != 429, (
        "la connexion suivante reçoit encore 429 : le protecteur n'est pas "
        "réellement remis à zéro (%s)" % (r.get_json() or {}))
    # ET UN SEUL ÉCHEC A ÉTÉ COMPTÉ — celui qu'on vient de faire. Quatre
    # auraient dit que les anciens ont survécu.
    assert len(A.bf_protector.attempts.get(cle) or []) == 1, \
        "%d tentatives comptées après un seul échec" % len(
            A.bf_protector.attempts.get(cle) or [])


def test_la_derivation_des_gardiens_N_EST_PAS_VIDE_et_en_trouve_PLUS_D_UN():
    """LE GARDE-FOU DES DEUX RÈGLES CI-DESSUS.

    Si la dérivation ne rendait plus rien, la remise à zéro ne nettoierait
    rien — et les deux règles précédentes tomberaient, ce qui est bien. Mais
    si elle n'en rendait qu'UN, celui d'avant, elles pourraient passer pour la
    mauvaise raison le jour où le protecteur cesse de bloquer. On exige donc
    que la dérivation voie les DEUX, et qu'elle les nomme.
    """
    noms = [n for n, _g in CONF.gardiens(A)]
    assert "limiter" in noms, "le limiteur de cadence n'est plus dérivé"
    assert "bf_protector" in noms, \
        "le protecteur anti-force-brute n'est plus dérivé : la fuite revient"
    assert len(noms) >= 2


def test_les_CLASSES_sont_ecartees_de_la_derivation():
    """`RateLimiter` et `BruteForceProtector` exposent `is_blocked` elles
    aussi. Elles ne portent aucun état d'exécution, et vider leurs attributs
    de classe démonterait le module — `is_blocked` lui-même y passerait.

    ═══ CE QUI GARDE VRAIMENT CETTE INVARIANT, ET IL FAUT LE DIRE ════════
    Mesuré en retirant l'exclusion : la remise à zéro tombe alors sur
    `__doc__`, une chaîne sans `.clear()`, et REFUSE bruyamment — comme elle
    doit. Mais elle refuse dans une fixture `autouse`, donc AVANT chaque
    essai : la recette ne rend pas un échec, elle rend 15 ERREURS sur ce
    fichier et 47 sur celui des inscriptions. La suite ne peut plus être
    verte.

    C'est une protection plus forte qu'une règle nommée, et c'est pourquoi
    aucune mutation n'est inscrite au banc pour ce cas : un banc qui compte
    les ÉCHECS ne voit pas les erreurs, et l'y forcer aurait demandé
    d'affaiblir le refus — c'est-à-dire de remplacer une garantie par une
    règle. Cette règle-ci énonce donc l'invariant pour le lecteur ; ce qui
    l'applique est le refus.
    """
    for nom, g in CONF.gardiens(A):
        assert not isinstance(g, type), \
            "« %s » est une classe : la remise à zéro effacerait ses méthodes" % nom


def test_un_gardien_AJOUTE_DEMAIN_est_nettoye_sans_que_personne_y_pense():
    """LE POINT DE TOUTE LA DÉRIVATION.

    Un troisième objet capable de refuser un appelant — un quota par clé
    d'API, un verrou d'export — sera nettoyé du seul fait qu'il expose
    `is_blocked`. C'est ce que l'énumération ne savait pas faire, et c'est
    exactement par là que le défaut est entré.
    """
    class GardienDeRecette(object):
        def __init__(self):
            self.refuses = {"une-cle": 1}

        def is_blocked(self, cle):
            return cle in self.refuses

    A.gardien_de_recette = GardienDeRecette()
    try:
        assert "gardien_de_recette" in [n for n, _ in CONF.gardiens(A)]
        CONF.reinitialiser_limiteur()
        assert not A.gardien_de_recette.refuses, \
            "un gardien neuf n'est pas nettoyé : l'énumération est revenue"
    finally:
        delattr(A, "gardien_de_recette")


def test_un_gardien_dont_un_etat_NE_SAIT_PAS_se_vider_est_refuse_BRUYAMMENT():
    """Le message nomme désormais LE GARDIEN, pas seulement l'attribut.
    « RateLimiter.x ne sait pas se vider » était faux dès qu'il y en avait
    deux — et c'est le genre de message qui envoie chercher au mauvais
    endroit."""
    class GardienEntier(object):
        def __init__(self):
            self.compteur = 7                       # ne sait pas se vider

        def is_blocked(self, cle):
            return False

    A.gardien_entier = GardienEntier()
    try:
        with pytest.raises(AssertionError) as leve:
            CONF.reinitialiser_limiteur()
        assert "gardien_entier.compteur" in str(leve.value), str(leve.value)
    finally:
        delattr(A, "gardien_entier")
