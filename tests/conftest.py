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


def reinitialiser_limiteur():
    """Vide l'état du limiteur. Rend le nombre d'attributs nettoyés.

    N'IMPORTE PAS `app` : si aucun essai ne l'a chargé, il n'y a pas d'état à
    nettoyer, et l'importer ferait payer une seconde de démarrage aux fichiers
    qui n'en ont pas besoin. Un fichier qui touche aux routes l'a forcément
    importé au moment de la collecte, donc bien avant que cette fonction serve.
    """
    module = sys.modules.get("app")
    if module is None:
        return 0
    limiteur = getattr(module, "limiter", None)
    if limiteur is None:                                       # pragma: no cover
        return 0
    nettoyes = 0
    for nom, valeur in vars(limiteur).items():
        vider = getattr(valeur, "clear", None)
        if vider is None:
            raise AssertionError(
                "RateLimiter.%s ne sait pas se vider : l'isolation de la "
                "recette est incomplète et cet attribut fuirait d'un essai à "
                "l'autre. Décidez comment le remettre à zéro." % nom)
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
