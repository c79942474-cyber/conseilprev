# -*- coding: utf-8 -*-
"""Le limiteur de débit est un état de PROCESSUS. Il traversait toute la recette.

L'INCIDENT. Deux essais d'authentification ont échoué une fois, puis sont
repassés. Le symptôme disait « la session de l'intrus survit au changement de
mot de passe » — une phrase qui envoie chercher un défaut de session. Il n'y en
a pas.

DEUX CHOSES QUE J'AI CRUES ET QUI SONT FAUSSES, corrigées ici plutôt que
laissées dans une explication qui se transmettrait :
  · « l'ordre était tiré au sort » — NON. Aucun greffon d'ordre aléatoire n'est
    installé (pytest 9.1.1, aucun greffon) ; l'ordre est déterministe.
  · « la rotation d'adresses boucle » — pas aujourd'hui. Mesuré : le compteur
    passe de 300 à 372, soit 72 appels sur un cycle de 250. Elle emploie 29 %
    du cycle. C'est un modulo, donc elle PEUT boucler ; elle ne le fait pas
    encore.

CE QUI EST MESURÉ, ET QUI SUFFIT À JUSTIFIER LA CORRECTION. À chaque passage de
la recette, EXACTEMENT UNE adresse est bloquée — `198.51.100.56`, pour UNE
HEURE — par `test_un_chemin_a_saisie_libre_reste_protege`, qui envoie
`/api/registre?q=' OR 1=1--` pour vérifier le filtre anti-injection. Le filtre
fait son travail : `limiter.block(ip, 3600, 'injection_attempt')`. L'essai est
juste, son effet de bord dure une heure, et rien ne le nettoyait.

Les deux faits — une adresse morte pour une heure, une rotation qui peut
revenir dessus — sont à 178 appels l'un de l'autre. Le piège est armé, pas
encore déclenché.

JE N'AI PAS REPRODUIT L'OCCURRENCE OBSERVÉE. Ce qui est corrigé est la CLASSE de
défaut : l'état du limiteur traversait la recette. La reproduction délibérée
(salir, puis lancer le fichier) fait tomber 18 essais sur 47 ; avec la remise à
zéro, aucun. Si le symptôme revient, la cause est ailleurs, et cette
explication-ci ne doit pas servir à le classer sans regarder.

LE MÉCANISME, REPRODUIT PLUTÔT QUE SUPPOSÉ — ET PLUS LARGE QU'IL N'Y PARAÎT.
`RateLimiter.check()` compte par (adresse, route), c'est écrit dans sa
docstring : « pour ne pas pénaliser globalement une IP active sur plusieurs
routes différentes ». Mais au troisième dépassement elle appelle `block(ip, 30)`,
et l'adresse entre dans `self.blocked`.

Or une adresse bloquée n'atteint plus RIEN du site, et par DEUX chemins
indépendants, tous deux dans le `before_request` :

  1. « ── Vérifier si IP bloquée ── » : `is_blocked(ip)` → `abort(429)` ;
  2. « ── Rate limit global : 120 req/min par IP ── » : `check()` commence
     elle-même par `is_blocked(ip)`, donc la limite globale échoue aussi.

Neutraliser l'un des deux ne rétablit rien — mesuré, en tentant de faire tomber
la règle de reproduction avec une seule des deux coupures : elle est restée
verte parce que le second chemin suffisait. C'est pourquoi le symptôme était
total : trente secondes durant, puis cent vingt, puis six cents, cette adresse
recevait 429 sur toutes les routes, limitées ou non.

Les essais d'authentification font tourner leurs requêtes sur 250 adresses
(`198.51.100.1` à `.250`) précisément pour ne pas se limiter eux-mêmes. Le
compteur qui les distribue est global au fichier et repart à 300 : la rotation
BOUCLE. Il suffit qu'un autre fichier — ceux qui éprouvent le cache ou la
compression parcourent des dizaines de pages — ait fait bloquer l'une de ces
adresses pour que la requête suivante reçoive 429 là où l'essai attend 200.

Reproduit en salissant le limiteur avant la session : 18 essais tombent sur 47,
dont les deux observés. La reproduction est dans `test_isolation_limiteur.py`,
et elle ne suppose rien — elle rejoue le chemin.

CE QUI EST CORRIGÉ, ET CE QUI NE L'EST PAS. Le comportement de l'application est
juste : bloquer une adresse qui insiste est une décision d'anti-abus, et sa
docstring décrit les deux moitiés. Ce qui manquait était l'ISOLATION DE LA
RECETTE — aucun `conftest.py` n'existait, et aucun essai ne touchait au limiteur.
Chaque essai part désormais d'un limiteur vide.

POURQUOI LA REMISE À ZÉRO EST DÉRIVÉE ET NON ÉNUMÉRÉE. `RateLimiter` porte cinq
dictionnaires d'état aujourd'hui. Les nommer un par un ici ferait qu'un sixième,
ajouté demain, ne serait pas nettoyé — et l'essai suivant hériterait de lui sans
que rien ne le dise. On vide donc TOUT ce que l'instance porte, et l'on REFUSE
bruyamment ce qu'on ne sait pas vider : un attribut sauté en silence est
exactement le défaut qu'on corrige.
"""
import sys

import pytest


def gardiens(module):
    """TOUT CE QUI, DANS L'APPLICATION, SAIT REFUSER UN APPELANT.

    ═══ CE QUE CETTE FONCTION RÉPARE, ET CE QU'ELLE PROLONGE ═════════════
    La remise à zéro dérivait déjà les ATTRIBUTS d'un limiteur plutôt que de
    les nommer — le raisonnement est en tête de ce fichier : « un sixième,
    ajouté demain, ne serait pas nettoyé ». Elle ÉNUMÉRAIT pourtant l'objet :
    `getattr(module, "limiter")`, et lui seul.

    OR IL Y EN AVAIT DÉJÀ DEUX. `bf_protector` — un `BruteForceProtector`
    clé `login:<courriel>` — bloque cinq minutes après cinq connexions
    ratées, puis jusqu'à une heure. Rien ne le vidait. Reproduit sans rien
    supposer : cinq échecs, la remise à zéro nettoie ses cinq attributs de
    `limiter`, et la connexion suivante sur ce courriel reçoit 429 là où
    l'essai attend 200. C'est l'intermittence observée en recette complète,
    verte au second passage parce que le blocage expire.

    LE MÊME ARGUMENT, D'UN CRAN PLUS HAUT. On ne nomme donc plus l'objet non
    plus : on retient tout ce qui expose `is_blocked` — c'est-à-dire tout ce
    qui peut faire échouer l'essai suivant en refusant un appelant. Un
    troisième gardien ajouté demain sera nettoyé sans que personne y pense.

    LES CLASSES SONT ÉCARTÉES. `RateLimiter` et `BruteForceProtector` exposent
    `is_blocked` elles aussi ; elles ne portent aucun état d'exécution, et
    vider leurs attributs de classe reviendrait à démonter le module.
    """
    for nom, valeur in sorted(vars(module).items()):
        if nom.startswith("_") or isinstance(valeur, type):
            continue
        try:
            refuse = getattr(valeur, "is_blocked", None)
        except Exception:                                      # pragma: no cover
            continue
        if callable(refuse):
            yield nom, valeur


def reinitialiser_limiteur():
    """Vide l'état de TOUS les gardiens. Rend le nombre d'attributs nettoyés.

    N'IMPORTE PAS `app` : si aucun essai ne l'a chargé, il n'y a pas d'état à
    nettoyer, et l'importer ferait payer une seconde de démarrage aux fichiers
    qui n'en ont pas besoin. Un fichier qui touche aux routes l'a forcément
    importé au moment de la collecte, donc bien avant que cette fonction serve.
    """
    module = sys.modules.get("app")
    if module is None:
        return 0
    nettoyes = 0
    for nom_gardien, gardien in gardiens(module):
        for nom, valeur in vars(gardien).items():
            vider = getattr(valeur, "clear", None)
            if vider is None:
                raise AssertionError(
                    "%s.%s ne sait pas se vider : l'isolation de la recette "
                    "est incomplète et cet attribut fuirait d'un essai à "
                    "l'autre. Décidez comment le remettre à zéro."
                    % (nom_gardien, nom))
            vider()
            nettoyes += 1
    return nettoyes


@pytest.fixture(autouse=True)
def limiteur_propre():
    """AVANT **ET APRÈS** CHAQUE ESSAI.

    Avant, pour ne pas hériter ; après, pour ne pas léguer. Nettoyer d'un seul
    côté suffirait tant que tous les essais passent par cette fixture — mais le
    jour où l'un s'en exempte, c'est le nettoyage de sortie qui empêche qu'il
    casse les suivants. Une recette qui casse la suivante est pire qu'une
    recette absente.
    """
    reinitialiser_limiteur()
    yield
    reinitialiser_limiteur()


# ═══════════════════════════════════════════════════════════════════════════
#  LA LIMITE QUI ARRÊTE LA RECETTE AVANT QU'ELLE COMMENCE
# ═══════════════════════════════════════════════════════════════════════════
#
# L'INCIDENT. Sept parcours guidés de plus, et la COLLECTE d'un fichier a levé
#
#     OSError: [Errno 7] Argument list too long: '/opt/node22/bin/node'
#
# Pas une règle rouge : une recette qui ne démarre pas. Le message ne nomme ni
# le fichier fautif, ni le bloc, ni la cause — il nomme l'interpréteur, qui
# n'y est pour rien.
#
# CE QUI SE PASSAIT. Onze fichiers de recette évaluent des morceaux de
# sentinel.page.js en les passant à `node -e`. Linux limite UN SEUL argument à
# MAX_ARG_STRLEN = 32 pages, soit 131 072 octets — indépendamment d'ARG_MAX,
# qui vaut 2 Mio ici et qu'on consulte d'abord parce que c'est celui que
# `getconf` affiche. Le fichier de données ne fait que grandir.
#
# CE QUE FAIT CE GARDE-FOU, ET CE QU'IL NE FAIT PAS. Il ne corrige rien : un
# argument trop long reste trop long. Il REMPLACE un message qui envoie
# chercher au mauvais endroit par un message qui nomme le programme, sa
# taille, la limite, et la correction — écrire dans un fichier temporaire.
# Il s'installe au chargement de conftest, donc AVANT l'import des fichiers de
# recette : c'est la seule façon d'attraper une panne de collecte.

import subprocess as _subprocess

MAX_ARG_STRLEN = 131072
_run_origine = _subprocess.run


def _run_garde(args, *reste, **nommes):
    """`subprocess.run`, avec le diagnostic que l'OS ne donne pas."""
    if isinstance(args, (list, tuple)):
        for i, a in enumerate(args):
            if not isinstance(a, str):
                continue
            taille = len(a.encode("utf-8", "replace"))
            if taille > MAX_ARG_STRLEN:
                raise AssertionError(
                    "argument n°%d de %r : %d octets, au-delà de "
                    "MAX_ARG_STRLEN (%d). Linux refusera l'exécution avec "
                    "« Argument list too long », à la COLLECTE et sans nommer "
                    "la cause. Écrivez le programme dans un fichier "
                    "temporaire et passez son chemin — c'est ce que font "
                    "test_parcours_par_role.py et test_parcours_avancement.py."
                    % (i, args[0], taille, MAX_ARG_STRLEN))
    return _run_origine(args, *reste, **nommes)


_subprocess.run = _run_garde


# ═══════════════════════════════════════════════════════════════════════════
#  STRIPE ET BREVO SANS RÉSEAU : LES VRAIES BIBLIOTHÈQUES, DE FAUX SERVEURS
# ═══════════════════════════════════════════════════════════════════════════
#
# Non automatiques : seul un essai qui les DEMANDE ouvre un faux serveur. Voir
# tests/faux_services.py pour la raison d'être (un faux MODULE rend des dict,
# la bibliothèque 15.x rend des StripeObject sans `.get()`).
#
# LA VRAIE BIBLIOTHÈQUE EST RETENUE ICI, AU CHARGEMENT DE conftest — donc avant
# tout fichier d'essai. test_formation_ia_paiement.py pose un faux module dans
# sys.modules["stripe"] le temps d'un essai ; un `import stripe` fait à ce
# moment-là attraperait le faux. On ne l'importe jamais qu'ici.

import os as _os
import socket as _socket

try:
    import stripe as _STRIPE_REEL
except Exception:                                              # pragma: no cover
    _STRIPE_REEL = None

SECRET_WEBHOOK_RECETTE = "whsec_recette_locale"


@pytest.fixture
def reseau_ferme(monkeypatch):
    """Toute connexion sortante hors des faux serveurs est REFUSÉE : un essai
    qui viserait api.stripe.com ou api.brevo.com tombe au lieu de partir.
    Le mandataire du conteneur écoute lui aussi sur 127.0.0.1 : on n'autorise
    donc pas l'adresse locale entière, seulement les ports des faux serveurs."""
    permis = set()
    vrai = _socket.socket.connect

    def connect(self, adresse):
        if isinstance(adresse, tuple) and not (
                adresse[0] in ("127.0.0.1", "::1") and adresse[1] in permis):
            raise ConnectionRefusedError("recette hors réseau : %r" % (adresse,))
        return vrai(self, adresse)
    monkeypatch.setattr(_socket.socket, "connect", connect)
    return permis


@pytest.fixture
def faux_stripe(monkeypatch, reseau_ferme):
    """La VRAIE bibliothèque `stripe`, `api_base` redirigé vers un faux
    serveur local, clés de recette, et les réglages PARTAGÉS PAR TOUT LE
    PROCESSUS (réessais, client HTTP) sauvés puis restaurés."""
    import app as A
    from faux_services import FauxStripe
    if _STRIPE_REEL is None:                                   # pragma: no cover
        pytest.skip("bibliothèque stripe absente")
    fs = FauxStripe(int(_os.environ.get("FAUX_STRIPE_PORT", "0"))).demarrer()
    reseau_ferme.add(fs.port)
    st = _STRIPE_REEL
    monkeypatch.setitem(sys.modules, "stripe", st)
    monkeypatch.setattr(st, "api_base", fs.url)
    monkeypatch.setattr(st, "api_key", None)
    monkeypatch.setattr(st, "max_network_retries", st.max_network_retries)
    monkeypatch.setattr(st, "default_http_client", None)
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_recette_locale")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET_WEBHOOK_RECETTE)
    monkeypatch.setenv("STRIPE_TAX_RATE_ID", "txr_recette")
    if hasattr(A, "_FORM_TAX_RATE_CACHE"):
        monkeypatch.setitem(A._FORM_TAX_RATE_CACHE, "id", None)
    yield fs
    fs.arreter()


@pytest.fixture
def faux_brevo(monkeypatch, reseau_ferme, tmp_path):
    """Le VRAI transport HTTP de l'envoi Brevo, vers un faux serveur local.
    `BREVO_API_KEY` et `SMTP_*` sont lus à l'IMPORT d'app.py : on remplace les
    attributs du module, pas les variables d'environnement.

    LES DEUX NOMS DE L'ADRESSE BREVO SONT REDIRIGÉS ENSEMBLE. app.py porte
    `BREVO_API_BASE` (la racine : compte, expéditeurs, contacts) et
    `BREVO_API_URL` (l'envoi), la seconde calculée depuis la première À
    L'IMPORT. N'en rediriger qu'une laissait l'autre viser api.brevo.com :
    mesuré à la fusion, le diagnostic des connexions lisait la racine réelle
    et tombait sur le mandataire (quatre règles rouges), pendant que l'envoi
    parlait bien au faux serveur. `raising=False` : sur un code qui n'a pas
    encore la racine, la fixture ne doit pas tomber avant la règle.

    LE COURRIEL DE REPLI VA DANS LE DOSSIER DE L'ESSAI. Un Brevo en panne
    dépose le message sur disque ; sans cette redirection, chaque essai de
    panne en laissait un dans le dépôt."""
    import app as A
    from faux_services import FauxBrevo
    fb = FauxBrevo(int(_os.environ.get("FAUX_BREVO_PORT", "0"))).demarrer()
    reseau_ferme.add(fb.port)
    monkeypatch.setattr(A, "BREVO_API_KEY", "xkeysib-recette-locale")
    monkeypatch.setattr(A, "BREVO_API_BASE", fb.url, raising=False)
    monkeypatch.setattr(A, "BREVO_API_URL", fb.url + "/v3/smtp/email")
    monkeypatch.setattr(A, "REPLI_COURRIELS_DOSSIER", str(tmp_path / "repli"),
                        raising=False)
    monkeypatch.setattr(A, "SMTP_USER", "")
    monkeypatch.setattr(A, "SMTP_PASSWORD", "")
    yield fb
    fb.arreter()
