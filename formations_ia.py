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
#  3 bis. LE DEVIS — de 1 à 4 séances d'un coup, et la gratuité CHOISIE
# ═══════════════════════════════════════════════════════════════════════════
# CE QUI CHANGE, ET POURQUOI CE N'EST PAS UN DÉTAIL. `tarif(rang)` fait payer
# selon l'ORDRE de réservation : la première séance réservée est offerte, quelle
# qu'elle soit. Un client qui veut la gouvernance agentique offerte devait donc
# la réserver EN PREMIER, et l'apprendre après coup. La gratuité devient un
# choix explicite, dit au moment de réserver.
#
# LA RÈGLE ANNONCÉE NE BOUGE PAS : une séance offerte par client, pas une par
# commande. Un client qui a déjà consommé la sienne ne la retrouve pas en
# repassant commande — c'est la base qui le sait, et elle le dit au devis par
# `gratuite_disponible`. Rien de ce que le navigateur affirme là-dessus n'est
# cru.
MIN_SEANCES = 1
#: QUATRE, ET CE N'EST PAS UN NOMBRE ROND : c'est le nombre de sujets, et un
#: sujet ne se suit pas deux fois. Le plafond se déduit du catalogue au lieu
#: d'être écrit à côté de lui, où les deux divergeraient.
MAX_SEANCES = NB_SUJETS


def devis(sujets, gratuit=None, gratuite_disponible=True):
    """Ce que coûte un panier de 1 à %d séances, ligne par ligne.

    `sujets` : les clés choisies. `gratuit` : la clé de celle que le client veut
    offerte. `gratuite_disponible` : False si ce client a DÉJÀ consommé la
    sienne — décidé par la base, jamais par le navigateur.

    Rend toujours un dict. En cas de refus, `ok` est faux et `message` dit
    pourquoi en toutes lettres : un devis qui échoue en silence ferait réserver
    à l'aveugle.
    """ % MAX_SEANCES
    cles = [str(x or "").strip() for x in (sujets or []) if str(x or "").strip()]

    def _refus(code, message):
        return {"ok": False, "error": code, "message": message, "lignes": [],
                "nb": 0, "ht_cents": 0, "tva_pct": TVA_PCT, "ttc_cents": 0,
                "gratuite": None}

    if len(cles) < MIN_SEANCES:
        return _refus("aucune_seance",
                      "Choisissez au moins une formation.")
    if len(cles) > MAX_SEANCES:
        return _refus("trop_de_seances",
                      "Quatre formations au maximum : il y a quatre sujets, et "
                      "un sujet ne se suit pas deux fois.")
    if len(set(cles)) != len(cles):
        return _refus("sujet_en_double",
                      "Le même sujet est choisi deux fois.")
    inconnus = [c for c in cles if c not in _CLES_SUJETS]
    if inconnus:
        return _refus("sujet_inconnu",
                      "Sujet de formation inconnu : %s." % ", ".join(inconnus))

    # LA GRATUITE PORTE SUR UNE SÉANCE DU PANIER, jamais sur une autre. Un
    # client qui désignerait un sujet qu'il ne réserve pas obtiendrait sinon une
    # remise sur rien — et la ligne offerte serait introuvable à l'écran.
    choisi = str(gratuit or "").strip() or None
    note = None
    if not gratuite_disponible:
        if choisi:
            note = ("Votre séance offerte a déjà été utilisée : toutes les "
                    "séances de cette commande sont au tarif.")
        choisi = None
    elif choisi and choisi not in cles:
        return _refus("gratuite_hors_panier",
                      "La séance offerte doit être l'une de celles que vous "
                      "réservez.")
    elif not choisi:
        # SANS CHOIX, ON OFFRE LA PREMIÈRE — jamais aucune. Laisser la gratuité
        # tomber faute d'avoir coché ferait payer une séance annoncée offerte.
        choisi = cles[0]
        note = ("Aucune séance n'était désignée : la première de la liste est "
                "offerte.")

    lignes, ht = [], 0
    for cle in cles:
        s = sujet(cle)
        offerte = (cle == choisi)
        pu = 0 if offerte else TARIF_HT_CENTS
        ht += pu
        lignes.append({
            "cle": cle, "titre": s["titre"], "num": s["num"],
            "gratuit": offerte, "ht_cents": pu, "ttc_cents": _ttc(pu),
            "libelle": ("Offerte — séance sur site" if offerte
                        else "%d € HT" % (TARIF_HT_CENTS // 100)),
        })
    return {"ok": True, "error": None, "message": note, "lignes": lignes,
            "nb": len(lignes), "gratuite": choisi,
            "ht_cents": ht, "tva_pct": TVA_PCT, "ttc_cents": _ttc(ht),
            "nb_payantes": sum(1 for l in lignes if not l["gratuit"])}


# ═══════════════════════════════════════════════════════════════════════════
#  3 ter. L'ANNULATION — libre au-delà de sept jours, due en deçà
# ═══════════════════════════════════════════════════════════════════════════
# POURQUOI UN DÉLAI, ET POURQUOI SEPT JOURS. Le formateur se déplace sur le
# site du client et bloque une demi-journée ; le créneau refusé à un autre
# client ne se revend pas la veille. Sept jours est le délai annoncé — il est
# écrit ICI une seule fois, et l'infobulle de la page le lit au lieu de le
# recopier : deux textes qui énoncent le même délai finissent par le dire
# différemment, et c'est celui que le client a lu qui l'engage.
ANNULATION_JOURS = 7


def regle_annulation():
    """Le délai et ce qu'il emporte, dit une fois pour toutes les surfaces."""
    return {
        "jours": ANNULATION_JOURS,
        "titre": "Annulation",
        "payante": "Toute formation payante annulée moins de %d jours avant la "
                   "date prévue est due et sera facturée." % ANNULATION_JOURS,
        "libre": "Au-delà de ce délai, l'annulation est libre et sans frais : "
                 "le lien figure dans votre courriel de confirmation.",
        "offerte": "Une séance offerte n'est jamais facturée, même annulée "
                   "tardivement — prévenez-nous tout de même, le formateur se "
                   "déplace.",
        "infobulle": "Toute formation payante annulée moins de %d jours avant "
                     "la date prévue est due et sera facturée. Au-delà, "
                     "l'annulation est libre et sans frais." % ANNULATION_JOURS,
    }


def annulable(date_creneau, aujourdhui):
    """(possible, motif) — l'annulation est libre à SEPT JOURS OU PLUS.

    « Moins de sept jours avant » est ce qui est facturé : à exactement sept
    jours, l'annulation passe encore. La borne est ici, et nulle part ailleurs.
    """
    d = _lire_date(date_creneau)
    a = _lire_date(aujourdhui)
    if d is None or a is None:
        return False, "Date de séance illisible."
    reste = (d - a).days
    if reste < 0:
        return False, "Cette séance a déjà eu lieu."
    if reste < ANNULATION_JOURS:
        return False, ("Il reste %d jour(s) avant la séance : moins de %d. "
                       "Une séance payante annulée maintenant reste due."
                       % (reste, ANNULATION_JOURS))
    return True, ("Annulation libre : %d jour(s) avant la séance, soit %d ou "
                  "plus." % (reste, ANNULATION_JOURS))


# ═══════════════════════════════════════════════════════════════════════════
#  3 quater. CE QUI EST REMIS, ET CE QUI EST PERSONNALISÉ
# ═══════════════════════════════════════════════════════════════════════════
# CE BLOC DIT L'OFFRE, PAS UNE PROMESSE DE PLUS. Chaque élément porte s'il est
# STANDARD (le même pour tous) ou PERSONNALISÉ (établi sur le contexte du
# client). Annoncer « support personnalisé » sans dire ce qui l'est
# réellement est la promesse la plus facile à démentir le jour de la séance.
SUPPORT = {
    "titre": "Le support de workshop",
    "remise": "Remis à chaque participant, au format PDF, à l'issue de la "
              "séance.",
    "elements": [
        {"quoi": "Le déroulé du workshop et les planches projetées",
         "nature": "standard",
         "detail": "Le socle du sujet, identique d'une séance à l'autre : "
                   "c'est ce qui rend la formation comparable d'un client à "
                   "l'autre."},
        {"quoi": "Les modèles de travail — registre, grille de qualification, "
                 "trame de contrôle",
         "nature": "personnalise",
         "detail": "Pré-remplis avec VOS systèmes et votre vocabulaire, à "
                   "partir de ce que vous transmettez avant la séance. Un "
                   "modèle vide se referme le soir même."},
        {"quoi": "Le relevé des décisions prises pendant la séance",
         "nature": "personnalise",
         "detail": "Ce que vous avez arbitré, qui le porte et pour quand — "
                   "écrit pendant la séance, pas reconstitué après."},
    ],
    "participants": "Sans limite de participants : la séance se tient dans vos "
                    "locaux, vous y conviez qui vous voulez.",
}

#: LES ÉTUDES DE CAS SUIVENT LE TYPE DE CLIENT. Un exploitant de centre de
#: données et un éditeur de logiciel n'ont pas les mêmes angles morts ; leur
#: présenter les mêmes cas fait perdre la moitié de la séance à traduire.
PROFILS = [
    {"cle": "exploitant", "titre": "Exploitant de centre de données",
     "cas": "Supervision d'une salle, contrats d'infogérance, chaîne "
            "d'astreinte et traçabilité des interventions automatisées."},
    {"cle": "porteur", "titre": "Porteur de projet ou maître d'ouvrage",
     "cas": "Cadrage amont, allotissement, pièces de marché et clauses qui "
            "engagent le titulaire sur l'IA embarquée."},
    {"cle": "utilisateur", "titre": "Entreprise utilisatrice (DSI, RSSI, DPO)",
     "cas": "Registre des systèmes, qualification par niveau de risque, "
            "arbitrage entre usage métier et exposition."},
    {"cle": "editeur", "titre": "Éditeur ou intégrateur",
     "cas": "Obligations du fournisseur, documentation technique, "
            "transparence due à l'utilisateur en aval."},
]
_CLES_PROFILS = {p["cle"] for p in PROFILS}


def profil(cle):
    for p in PROFILS:
        if p["cle"] == cle:
            return p
    return None


def etudes_de_cas(profil_cle):
    """Les cas présentés pour ce type de client, et ce qui reste à cadrer.

    UN PROFIL INCONNU NE REND PAS UNE LISTE VIDE : il rend tous les angles, en
    disant que le choix se fera au cadrage. Rendre vide ferait croire qu'aucun
    cas n'est présenté.
    """
    p = profil(profil_cle)
    if p:
        return {"profil": p["cle"], "titre": p["titre"], "cas": p["cas"],
                "choisi": True,
                "note": "Les cas présentés sont ceux de ce profil ; ils se "
                        "précisent avec vous avant la séance."}
    return {"profil": None, "titre": None,
            "cas": " · ".join(x["cas"] for x in PROFILS), "choisi": False,
            "note": "Sans profil indiqué, les cas se choisissent avec vous au "
                    "cadrage, parmi les quatre familles ci-dessus."}


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
        # LES BORNES DU PANIER SONT SERVIES, JAMAIS RECOPIÉES DANS LA PAGE.
        # Un écran qui laisserait cocher cinq sujets se ferait refuser au
        # dernier geste, après la saisie de toutes les coordonnées.
        "bornes": {"min": MIN_SEANCES, "max": MAX_SEANCES},
        "annulation": regle_annulation(),
        "support": SUPPORT,
        "profils": PROFILS,
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
    # LE PLAFOND DU PANIER SUIT LE CATALOGUE. Un plafond plus haut que le
    # nombre de sujets promettrait une cinquième séance qui n'existe pas ;
    # plus bas, il interdirait un sujet qu'on vend.
    if MAX_SEANCES != NB_SUJETS:
        pb.append("le plafond du panier (%d) ne suit pas le catalogue (%d)"
                  % (MAX_SEANCES, NB_SUJETS))
    if MIN_SEANCES < 1:
        pb.append("le plancher du panier est inférieur à une séance")
    # LE DÉLAI D'ANNULATION EST ÉCRIT DANS SON PROPRE TEXTE. Un jour changé
    # d'un côté et pas de l'autre engagerait le client sur le mauvais.
    _ra = regle_annulation()
    if str(ANNULATION_JOURS) not in _ra["payante"]:
        pb.append("la règle d'annulation ne dit pas son propre délai")
    if str(ANNULATION_JOURS) not in _ra["infobulle"]:
        pb.append("l'infobulle d'annulation ne dit pas son propre délai")
    # CHAQUE PROFIL PORTE SES CAS. Un profil sans cas se choisirait à l'écran
    # pour ne rien changer à la séance.
    if len(_CLES_PROFILS) != len(PROFILS):
        pb.append("clés de profils en double")
    for p in PROFILS:
        for champ in ("cle", "titre", "cas"):
            if not str(p.get(champ, "")).strip():
                pb.append("profil incomplet : %r" % p.get("cle"))
    # LE SUPPORT DIT CE QUI EST PERSONNALISÉ, ET IL Y A DE QUOI. Un support
    # entièrement standard annoncé « personnalisable » est la promesse la plus
    # facile à démentir le jour de la séance.
    _nat = {e.get("nature") for e in SUPPORT.get("elements", [])}
    if "personnalise" not in _nat:
        pb.append("le support n'a aucun élément personnalisé")
    if "standard" not in _nat:
        pb.append("le support n'a aucun élément standard — rien n'est comparable")
    for e in SUPPORT.get("elements", []):
        if e.get("nature") not in ("standard", "personnalise"):
            pb.append("élément de support sans nature déclarée : %r" % e.get("quoi"))
    return pb


_pb = _verifier()
if _pb:
    raise RuntimeError("formations_ia incohérent : " + " ; ".join(_pb))
del _pb


def sante():
    return {"module": "formations_ia", "version": VERSION,
            "sujets": NB_SUJETS, "tarif_ht_cents": TARIF_HT_CENTS,
            "tva_pct": TVA_PCT, "fin_campagne": FIN_CAMPAGNE.isoformat(),
            "seances_max": MAX_SEANCES, "annulation_jours": ANNULATION_JOURS,
            "profils": len(PROFILS),
            "problemes": _verifier()}
