# -*- coding: utf-8 -*-
"""« Formations conformité IA » — les quatre sujets, le calendrier, le tarif.

CE QUE CE MODULE EST, ET CE QU'IL N'EST PAS. Il porte la LOGIQUE d'une offre de
formation sur site : quels sujets, à quelles dates on peut réserver, et combien
coûte chaque séance. Il ne parle ni à la base, ni à Stripe, ni à Flask — la
persistance des réservations et l'encaissement vivent dans app.py, qui appelle
d'ici le référentiel et le tarif. Isolé ainsi, il se mesure hors ligne, au point
près : deux appels aux mêmes arguments rendent le même résultat.

LES QUATRE SUJETS SONT CEUX DU VISUEL, mot pour mot. Un cinquième sujet inventé,
ou un intitulé de travers, tromperait le client sur ce qu'il réserve.

LE CALENDRIER EST DÉTERMINISTE, ET C'EST VOULU. `creneaux(depuis)` prend la date
de référence en ARGUMENT — il ne lit jamais l'horloge. La route lui passe la
date du jour ; un test lui passe une date fixe et obtient toujours le même
calendrier. Une séance de quatre heures par semaine, du premier créneau utile
jusqu'à fin mars 2027 : au-delà, la campagne s'arrête, et le dire vaut mieux que
proposer des dates qu'on ne tiendra pas.

LE TARIF SUIT LA RÈGLE ANNONCÉE : la PREMIÈRE séance d'un client est gratuite
(sur site), les suivantes sont à 800 € HT. Le rang — combien de séances ce
client a déjà réservées — décide, et lui seul. Une séance gratuite n'est pas un
prix à zéro qu'on aurait oublié de remplir : c'est une décision, et la sortie la
nomme.

CE QUE CE MODULE NE FIXE PAS DANS LE MARBRE. Le montant de 800 € HT est le tarif
ANNONCÉ ; il est ici l'unique source, servie à la fois à l'affichage et (le jour
où Stripe est configuré) au montant prélevé, si bien que le prix montré et le
prix facturé ne peuvent pas diverger — la même discipline que le catalogue
existant, où le prix vient d'un seul calcul. Le jour où une référence de prix
Stripe existe pour cette offre, `TARIF_HT_CENTS` cédera la place à ce prix lu.
"""
import datetime
import os

VERSION = "2026-09-a"

# ═══════════════════════════════════════════════════════════════════════════
#  1. LES QUATRE SUJETS — repris du visuel, sans un mot de plus
# ═══════════════════════════════════════════════════════════════════════════
SUJETS = [
    {"cle": "gouvernance-ia", "num": 1, "titre": "Gouvernance IA",
     "resume": "Registre, qualification par niveau de risque, contrôles et "
               "preuves."},
    {"cle": "gouvernance-agentique", "num": 2, "titre": "Gouvernance agentique",
     "resume": "Supervision proportionnée à l'autonomie, seuils d'escalade, "
               "traçabilité."},
    {"cle": "securite-ia", "num": 3, "titre": "Sécurité de l'IA",
     "resume": "Injection de prompt, détournement d'agents, EBIOS RM."},
    {"cle": "ingenierie-projet", "num": 4, "titre": "Ingénierie de projet",
     "resume": "Cybersécurité industrielle et data centers, MOE et AMO."},
]
NB_SUJETS = len(SUJETS)
_CLES_SUJETS = {s["cle"] for s in SUJETS}

# OÙ LA SÉANCE SE TIENT, DIT UNE FOIS. Le formateur se déplace SUR LE SITE DU
# CLIENT, et seulement en Île-de-France : c'est une limite de l'offre, pas un
# détail d'affichage. Un client de Bordeaux qui réserve sans le savoir découvre
# le refus après coup — d'où la mention partout où l'on demande le lieu. La page
# lit cette valeur dans le référentiel ; les textes qui la recopient ailleurs
# sont tenus par une règle.
ZONE = "Île-de-France"

OFFRE = {
    "titre": "Angles morts de la conformité IA",
    "sous_titre": "Gouverner les systèmes d'IA et les agents dans vos centres "
                  "de données",
    "modalite": "Sur site, en %s — dans vos locaux" % ZONE,
    "zone": ZONE,
    "duree_h": 4,
}


def sujet(cle):
    for s in SUJETS:
        if s["cle"] == cle:
            return s
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  2. LE CALENDRIER — une séance de 4 h par semaine, jusqu'à fin mars 2027
# ═══════════════════════════════════════════════════════════════════════════
# UNE SEULE SÉANCE PAR SEMAINE, parce qu'un seul formateur se déplace : le
# créneau de la semaine est pris ou libre, il n'y en a pas deux. Le mardi
# 9 h – 13 h par convention ; le jour exact se cale avec le client, mais le
# calendrier doit proposer une date, pas une semaine floue.
JOUR_SEANCE = 1          # 0 = lundi … 1 = mardi (datetime.date.weekday())
HEURE_DEBUT = "09:00"
HEURE_FIN = "13:00"
DUREE_H = 4
LEAD_JOURS = 7           # on ne propose pas une séance pour après-demain
FIN_CAMPAGNE = datetime.date(2027, 3, 31)

_JOURS_FR = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi",
             "dimanche")
_MOIS_FR = ("", "janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre")


def _lire_date(d):
    """Une date, qu'on la reçoive en objet ou en 'AAAA-MM-JJ'. None sinon."""
    if isinstance(d, datetime.datetime):
        return d.date()
    if isinstance(d, datetime.date):
        return d
    try:
        return datetime.date.fromisoformat(str(d)[:10])
    except (TypeError, ValueError):
        return None


def _libelle(d):
    return "%s %d %s %d" % (_JOURS_FR[d.weekday()], d.day, _MOIS_FR[d.month],
                            d.year)


def creneaux(depuis, jusqu=FIN_CAMPAGNE):
    """Les créneaux réservables, du premier utile à la fin de campagne.

    `depuis` : la date de référence (le jour même, en production). On ajoute un
    délai de prévenance, puis on prend le prochain JOUR_SEANCE, puis une date
    par semaine jusqu'à `jusqu` INCLUS. Rien avant, rien après — proposer une
    date passée ou d'après-campagne serait promettre ce qu'on ne tiendra pas.

    Chaque créneau porte son identifiant (la date ISO, unique), son libellé
    lisible, ses heures et sa durée. La DISPONIBILITÉ n'est pas ici : elle
    dépend des réservations déjà prises, que ce module pur ne connaît pas —
    app.py la calcule et l'ajoute.
    """
    dep = _lire_date(depuis)
    fin = _lire_date(jusqu) or FIN_CAMPAGNE
    if dep is None:
        return []
    premier = dep + datetime.timedelta(days=LEAD_JOURS)
    # avancer jusqu'au prochain JOUR_SEANCE (inclus si premier tombe dessus)
    premier += datetime.timedelta(days=(JOUR_SEANCE - premier.weekday()) % 7)
    out, d = [], premier
    while d <= fin:
        out.append({
            "id": d.isoformat(),
            "date": d.isoformat(),
            "libelle": _libelle(d),
            "jour": _JOURS_FR[d.weekday()],
            "debut": HEURE_DEBUT, "fin": HEURE_FIN, "duree_h": DUREE_H,
            "semaine": d.isocalendar()[1],
        })
        d += datetime.timedelta(days=7)
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  3. LE TARIF — première séance gratuite, les suivantes à 800 € HT
# ═══════════════════════════════════════════════════════════════════════════
TARIF_HT_CENTS = 80000            # 800,00 € HT — tarif annoncé, source unique
GRATUITE_RANG = 0                 # la première réservation d'un client
TVA_PCT = int(os.environ.get("FORMATION_TVA_PCT", "20") or "20")


def _ttc(ht_cents):
    return int(round(ht_cents * (100 + TVA_PCT) / 100.0))


def tarif(rang):
    """Le tarif d'une séance selon le RANG du client (0 = sa première).

    `rang` : combien de séances ce client a DÉJÀ réservées. Sa première (rang 0)
    est gratuite, sur site ; les suivantes sont à 800 € HT. Un rang négatif est
    traité comme 0 — on ne fait pas payer plus que prévu par une entrée
    aberrante ; on ne fait pas non plus disparaître le prix d'une séance due.
    """
    try:
        r = int(rang)
    except (TypeError, ValueError):
        r = 0
    if r <= GRATUITE_RANG:
        return {"rang": max(r, 0), "gratuit": True, "ht_cents": 0,
                "tva_pct": TVA_PCT, "ttc_cents": 0,
                "libelle": "Gratuite — première séance sur site",
                "sur_site": True}
    return {"rang": r, "gratuit": False, "ht_cents": TARIF_HT_CENTS,
            "tva_pct": TVA_PCT, "ttc_cents": _ttc(TARIF_HT_CENTS),
            "libelle": "800 € HT", "sur_site": True}


def regle_tarifaire():
    """La règle, dite en toutes lettres, pour l'afficher sans la recopier."""
    return {
        "gratuite": "La première séance, sur l'un des quatre sujets, est "
                    "gratuite et se tient dans vos locaux.",
        "payantes": "Les séances suivantes sont à 800 € HT chacune (TVA %d %%)."
                    % TVA_PCT,
        "ht_cents": TARIF_HT_CENTS, "tva_pct": TVA_PCT,
        "ttc_cents": _ttc(TARIF_HT_CENTS),
        "nb_sujets": NB_SUJETS,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  4. LE RÉFÉRENTIEL SERVI À LA PAGE
# ═══════════════════════════════════════════════════════════════════════════

def referentiel(depuis):
    """Tout ce dont la page a besoin, sauf la disponibilité (calculée avec la
    base par app.py) : l'offre, les sujets, les créneaux, la règle de tarif."""
    return {
        "version": VERSION,
        "offre": OFFRE,
        "sujets": SUJETS,
        "creneaux": creneaux(depuis),
        "tarif": regle_tarifaire(),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  5. CONTRÔLE AU CHARGEMENT — l'incohérence est encore gratuite ici
# ═══════════════════════════════════════════════════════════════════════════

def _verifier():
    pb = []
    if len(_CLES_SUJETS) != len(SUJETS):
        pb.append("clés de sujets en double")
    if NB_SUJETS != 4:
        pb.append("le visuel porte quatre sujets ; %d déclaré(s)" % NB_SUJETS)
    for s in SUJETS:
        for champ in ("cle", "titre", "resume"):
            if not str(s.get(champ, "")).strip():
                pb.append("sujet incomplet : %r" % s.get("cle"))
    if not (0 < JOUR_SEANCE < 7 or JOUR_SEANCE == 0):
        pb.append("jour de séance hors semaine")
    # La zone est une LIMITE de l'offre : si la modalité cessait de la dire, le
    # client ne l'apprendrait qu'après avoir réservé.
    if ZONE not in OFFRE["modalite"]:
        pb.append("la modalité ne dit plus où la séance se tient (%s)" % ZONE)
    if TARIF_HT_CENTS <= 0:
        pb.append("tarif HT non positif")
    # La gratuité doit être exactement la première, et le tarif exactement au-
    # dessus : c'est la règle annoncée, et une échelle qui la trahirait ici
    # ferait payer une séance gratuite ou offrirait une séance due.
    if not tarif(0)["gratuit"] or tarif(0)["ht_cents"] != 0:
        pb.append("la première séance n'est pas gratuite")
    if tarif(1)["gratuit"] or tarif(1)["ht_cents"] != TARIF_HT_CENTS:
        pb.append("la deuxième séance n'est pas au tarif plein")
    return pb


_pb = _verifier()
if _pb:
    raise RuntimeError("formations_ia incohérent : " + " ; ".join(_pb))
del _pb


def sante():
    return {"module": "formations_ia", "version": VERSION,
            "sujets": NB_SUJETS, "tarif_ht_cents": TARIF_HT_CENTS,
            "tva_pct": TVA_PCT, "fin_campagne": FIN_CAMPAGNE.isoformat(),
            "problemes": _verifier()}
