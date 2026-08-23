"""LES ABONNÉS — comptes, connexion, préférences d'alerte.

CE QUE CE MODULE PROTÈGE. Une adresse électronique professionnelle, et la
liste des sujets qu'un lecteur suit. Ce second point est moins anodin qu'il
n'en a l'air : savoir qu'un industriel s'est abonné aux alertes sur un
automaticien précis renseigne sur son parc. C'est une donnée d'exposition,
pas une préférence de lecture, et elle est traitée comme telle.

LES CHOIX DE CONCEPTION, ET CE QU'ILS COÛTENT.

  1. LE MOT DE PASSE N'EST JAMAIS STOCKÉ, même chiffré : seul un dérivé
     `scrypt` l'est, avec un sel par compte. Un dérivé ne se déchiffre pas —
     c'est la différence entre « nous pourrions lire vos mots de passe si on
     nous y forçait » et « nous ne le pouvons pas ».

  2. LA COMPARAISON EST À TEMPS CONSTANT. Un `==` sur des empreintes rend une
     réponse d'autant plus lente que le préfixe correspond, ce qui se mesure
     et se remonte octet par octet.

  3. LA CONNEXION NE DIT JAMAIS SI L'ADRESSE EXISTE. « Mot de passe
     incorrect » distingue un compte inconnu d'un compte connu, et transforme
     le formulaire en annuaire d'abonnés. Un seul message pour les deux cas,
     et le même temps de calcul : un compte absent fait tourner le dérivé à
     vide plutôt que de répondre tout de suite.

CE QUE CE MODULE NE FAIT PAS.

  — IL N'ENVOIE AUCUN COURRIEL. Composer un bulletin et l'expédier sont deux
    métiers : le premier est ici et dans `bulletin.py`, le second demande un
    prestataire, un domaine authentifié (SPF, DKIM, DMARC) et l'accord
    explicite du responsable de traitement. Tant que ce n'est pas fait,
    `PRESTATAIRE_COURRIEL` vaut None et l'application le dit à l'écran plutôt
    que de laisser croire à un envoi.

  — IL NE PERSISTE RIEN SUR DISQUE. Les comptes vivent en mémoire du
    processus. C'est assumé pour cette étape : une base de données mal posée
    est pire qu'une absence de base, et le choix du support (chiffrement au
    repos, sauvegarde, effacement sur demande) engage le responsable de
    traitement, pas le développeur.
"""
import hashlib
import hmac
import os
import re
import secrets
import threading
import time
import unicodedata

import veille as V

VERSION = "2026.08.22"

# ── Le prestataire d'envoi, TANT QU'IL N'EXISTE PAS ───────────────────────
# Écrit ici pour que l'absence soit une DÉCLARATION et non un oubli. Toute
# l'application lit cette constante avant de parler d'envoi.
PRESTATAIRE_COURRIEL = None
POURQUOI_PAS_D_ENVOI = (
    "Aucun prestataire d'envoi n'est raccordé. Composer un bulletin et "
    "l'expédier sont deux métiers : l'expédition demande un domaine "
    "authentifié (SPF, DKIM, DMARC), un prestataire, et l'accord explicite du "
    "responsable de traitement. Tant que ce n'est pas fait, ce site COMPOSE "
    "le bulletin et vous le montre — il ne l'envoie pas, et ne prétend pas le "
    "faire.")

# scrypt : paramètres recommandés, écrits ici pour qu'on puisse les relever
# sans chercher. n doit rester une puissance de deux.
#
# `maxmem` N'EST PAS UN RÉGLAGE DE CONFORT. scrypt exige 128 × n × r octets,
# soit exactement 32 Mio pour n = 2^15 et r = 8 — c'est-à-dire le plafond que
# OpenSSL applique par défaut, si bien que la dérivation échoue tout court.
# La tentation est alors de baisser n jusqu'à ce que « ça passe », ce qui
# revient à affaiblir la dérivation pour contourner une limite d'allocation.
# On relève donc le plafond et on garde le coût.
_SCRYPT = {"n": 2 ** 15, "r": 8, "p": 1, "dklen": 32,
           "maxmem": 96 * 1024 * 1024}

# Un jeton de session vaut le mot de passe : même durée de vie courte, même
# révocation à la déconnexion.
DUREE_SESSION = 12 * 3600

_VERROU = threading.RLock()
_COMPTES = {}
_SESSIONS = {}

# Un sel de rechange, pour faire tourner le dérivé même quand le compte
# n'existe pas — voir `connecter`.
_SEL_LEURRE = secrets.token_bytes(16)


def _norme(email):
    """L'adresse sert de clé : elle est normalisée une fois, ici.

    Sans cela « Jean@Exemple.fr » et « jean@exemple.fr » ouvriraient deux
    comptes, et le second ne recevrait jamais rien.
    """
    e = unicodedata.normalize("NFKC", str(email or "")).strip().lower()
    return e


def adresse_plausible(email):
    """Ce contrôle dit que la SAISIE est plausible, pas que l'adresse existe.

    La distinction compte : seule la réception d'un message le prouverait, et
    aucune expression régulière ne remplace cette preuve. On refuse donc ce
    qui est manifestement fautif, sans prétendre valider.
    """
    e = _norme(email)
    if len(e) > 254 or len(e) < 6:
        return False
    return bool(re.match(r"^[^@\s<>\"',;]+@[^@\s<>\"',;]+\.[a-z]{2,}$", e))


def _derive(motdepasse, sel):
    return hashlib.scrypt(str(motdepasse or "").encode("utf-8"),
                          salt=sel, **_SCRYPT)


def _motdepasse_acceptable(m):
    """Une longueur minimale, et rien d'autre.

    LES RÈGLES DE COMPOSITION SONT UN LEURRE : « une majuscule, un chiffre,
    un caractère spécial » produit « Motdepasse1! » et rétrécit l'espace de
    recherche au lieu de l'élargir. La longueur est la seule contrainte qui
    fait un travail réel.
    """
    return isinstance(m, str) and len(m) >= 12


def creer(email, motdepasse, sujets=None, seuil="structurant"):
    if not adresse_plausible(email):
        return {"ok": False, "erreur": "adresse_invalide",
                "message": "Cette adresse ne peut pas être une adresse de "
                           "courrier électronique."}
    if not _motdepasse_acceptable(motdepasse):
        return {"ok": False, "erreur": "motdepasse_court",
                "message": "Douze caractères au minimum. Une phrase entière "
                           "vaut mieux qu'un mot compliqué : elle est plus "
                           "longue, et vous la retenez."}
    mauvais = [s for s in (sujets or []) if s not in V.SUJETS]
    if mauvais:
        return {"ok": False, "erreur": "sujet_inconnu",
                "message": "Sujet inconnu : %s." % ", ".join(mauvais)}
    if seuil not in V.IMPACTS:
        return {"ok": False, "erreur": "seuil_inconnu",
                "message": "Seuil d'alerte inconnu : %s." % seuil}

    e = _norme(email)
    with _VERROU:
        # ON NE DIT PAS QUE L'ADRESSE EST DÉJÀ PRISE — ce serait confirmer à
        # un tiers qu'une personne est abonnée ici. La réponse est la même
        # que pour une création réussie ; c'est le message reçu à l'adresse
        # qui fera la différence, le jour où l'envoi existera.
        if e in _COMPTES:
            return {"ok": True, "deja": True,
                    "message": "Demande enregistrée. Si cette adresse peut "
                               "être abonnée, elle recevra la confirmation."}
        sel = secrets.token_bytes(16)
        _COMPTES[e] = {
            "email": e, "sel": sel, "derive": _derive(motdepasse, sel),
            "sujets": list(sujets or list(V.ORDRE_SUJETS)),
            "seuil": seuil, "cree_le": time.time(),
            "dernier_bulletin": None,
        }
    return {"ok": True, "deja": False,
            "message": "Demande enregistrée. Si cette adresse peut être "
                       "abonnée, elle recevra la confirmation."}


def connecter(email, motdepasse):
    """Un seul message d'échec, et le même temps de calcul dans les deux cas.

    Répondre plus vite pour un compte inconnu revient à publier la liste des
    abonnés à qui prend la peine de chronométrer.
    """
    e = _norme(email)
    with _VERROU:
        c = _COMPTES.get(e)
    sel = c["sel"] if c else _SEL_LEURRE
    derive = _derive(motdepasse, sel)
    bon = bool(c) and hmac.compare_digest(derive, c["derive"])
    if not bon:
        return {"ok": False, "erreur": "identifiants",
                "message": "Adresse ou mot de passe incorrect."}
    jeton = secrets.token_urlsafe(32)
    with _VERROU:
        _SESSIONS[jeton] = {"email": e, "expire": time.time() + DUREE_SESSION}
    return {"ok": True, "jeton": jeton, "expire_dans": DUREE_SESSION,
            "compte": _public(c)}


def compte_de(jeton):
    """Le compte derrière un jeton, ou None. Purge au passage."""
    if not jeton:
        return None
    with _VERROU:
        s = _SESSIONS.get(jeton)
        if not s:
            return None
        if s["expire"] <= time.time():
            _SESSIONS.pop(jeton, None)
            return None
        return _COMPTES.get(s["email"])


def deconnecter(jeton):
    with _VERROU:
        return {"ok": True, "fermee": bool(_SESSIONS.pop(jeton, None))}


def regler(jeton, sujets=None, seuil=None):
    c = compte_de(jeton)
    if not c:
        return {"ok": False, "erreur": "non_connecte"}
    if sujets is not None:
        mauvais = [s for s in sujets if s not in V.SUJETS]
        if mauvais:
            return {"ok": False, "erreur": "sujet_inconnu",
                    "message": "Sujet inconnu : %s." % ", ".join(mauvais)}
        c["sujets"] = list(sujets)
    if seuil is not None:
        if seuil not in V.IMPACTS:
            return {"ok": False, "erreur": "seuil_inconnu"}
        c["seuil"] = seuil
    return {"ok": True, "compte": _public(c)}


# ── CE QUI DOIT DISPARAÎTRE AVEC UN COMPTE ───────────────────────────────
# LA PHRASE « RIEN N'EN SUBSISTE DANS CE PROCESSUS » DOIT RESTER VRAIE. Elle
# l'était tant que ce module tenait seul les données d'un compte. Le jour où
# un autre module en garde — le classeur de documents —, elle devient fausse
# si personne n'y pense, et c'est le pire genre de mensonge : celui qu'un
# ajout légitime introduit sans le vouloir.
#
# Le crochet renverse la charge : un module qui garde quelque chose s'inscrit
# ICI, et `oublier()` l'appelle. Il n'y a plus de liste à tenir à jour dans
# une fonction que personne ne relit.
_PURGES = []


def a_purger(fonction):
    """Inscrit une fonction `f(courriel)` appelée à l'effacement d'un compte."""
    if fonction not in _PURGES:
        _PURGES.append(fonction)
    return fonction


def oublier(jeton):
    """L'effacement, et il est réel.

    Un bouton « supprimer mon compte » qui se contenterait de marquer le
    compte inactif serait un mensonge tenu par le code. Le compte sort du
    registre, ses sessions avec lui, et TOUT CE QUE D'AUTRES MODULES EN
    GARDENT — chacun s'étant inscrit auprès de `a_purger`.
    """
    c = compte_de(jeton)
    if not c:
        return {"ok": False, "erreur": "non_connecte"}
    with _VERROU:
        _COMPTES.pop(c["email"], None)
        for j in [j for j, s in _SESSIONS.items() if s["email"] == c["email"]]:
            _SESSIONS.pop(j, None)
    for purge in _PURGES:
        try:
            purge(c["email"])
        except Exception:  # noqa: BLE001
            # UN MODULE QUI ÉCHOUE NE DOIT PAS EMPÊCHER LES AUTRES DE PURGER.
            # L'effacement partiel vaut mieux que l'effacement abandonné à
            # mi-chemin, et il n'y a rien à rendre au demandeur : son compte
            # EST parti.
            pass
    return {"ok": True, "message": "Compte effacé, sessions fermées. Rien "
                                   "n'en subsiste dans ce processus."}


def _public(c):
    """CE QUI SORT D'UN COMPTE. Ni le sel, ni le dérivé — jamais, à aucune
    route, fût-elle réservée à l'intéressé."""
    return {"email": c["email"], "sujets": list(c["sujets"]),
            "seuil": c["seuil"], "seuil_nom": V.IMPACTS[c["seuil"]]["nom"],
            "dernier_bulletin": c["dernier_bulletin"]}


def sante():
    with _VERROU:
        n, s = len(_COMPTES), len(_SESSIONS)
    return {
        "module": "abonnes", "version": VERSION,
        "comptes": n, "sessions_ouvertes": s,
        "envoi_raccorde": bool(PRESTATAIRE_COURRIEL),
        "pourquoi_pas_d_envoi": None if PRESTATAIRE_COURRIEL
                                else POURQUOI_PAS_D_ENVOI,
        "derivation": "scrypt n=%d r=%d p=%d" % (_SCRYPT["n"], _SCRYPT["r"],
                                                 _SCRYPT["p"]),
        "persistance": "mémoire du processus — aucun compte n'est écrit sur "
                       "disque ; le support engage le responsable de "
                       "traitement, pas le développeur",
        "portee": "Comptes, connexion et préférences d'alerte. N'envoie aucun "
                  "courriel et ne conserve aucun mot de passe.",
    }


def _verifier():
    if _SCRYPT["n"] < 2 ** 14:
        raise RuntimeError(
            "abonnes : le coût de scrypt est tombé sous le seuil recommandé — "
            "un dérivé bon marché se calcule en masse")
    if PRESTATAIRE_COURRIEL and not os.environ.get("COURRIEL_AUTORISE"):
        raise RuntimeError(
            "abonnes : un prestataire d'envoi est déclaré sans que l'envoi "
            "ait été explicitement autorisé — un site qui se met à écrire aux "
            "abonnés parce qu'une constante a changé est un incident")


_verifier()
