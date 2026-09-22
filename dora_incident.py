# -*- coding: utf-8 -*-
"""
DORA — CET INCIDENT EST-IL MAJEUR, ET QUAND FAUT-IL LE DÉCLARER ?

═══ LES DEUX QUESTIONS D'UNE ENTITÉ EN CRISE ═════════════════════════════
Elles n'en ont qu'une, en réalité, et elle se pose à trois heures du matin :
« dois-je déclarer, et pour quand ». Ce module y répond par un calcul, pas
par une brochure — parce que les deux textes qui la commandent sont, eux,
parfaitement chiffrés.

  · Règlement délégué (UE) 2024/1772 — les sept critères de classification
    et leurs seuils d'importance significative ;
  · Règlement délégué (UE) 2025/301 — le contenu et les DÉLAIS de la
    notification initiale et des rapports intermédiaire et final.

═══ LE PIÈGE PRINCIPAL : LA RÈGLE EST UNE CONJONCTION ════════════════════
L'article 8, paragraphe 1, du règlement 2024/1772 ne dit pas « un seuil
franchi, donc un incident majeur ». Il dit :

    des services critiques ont été touchés  ET
      ( le seuil de l'article 9, paragraphe 5, point b), est atteint
        OU au moins DEUX des autres seuils le sont )

La criticité des services est une PORTE, pas un septième seuil. Un module
qui additionnerait sept critères et déclencherait au premier franchi
sur-déclarerait massivement — et ferait perdre à l'entité la crédibilité
dont elle a besoin le jour où elle déclare vraiment.

═══ LE SECOND PIÈGE : « QUATRE HEURES » N'EST PAS LE DÉLAI ═══════════════
Le folklore retient « 4 h / 72 h / un mois ». L'article 5, paragraphe 1,
point a), du règlement 2025/301 pose DEUX bornes à la notification
initiale : quatre heures à compter de la CLASSIFICATION comme majeur, et
au plus tard vingt-quatre heures à compter de la CONNAISSANCE. La première
échue commande — sauf lorsque la classification intervient après les
vingt-quatre heures, cas que le paragraphe 2 traite à part.

Et le report de week-end du paragraphe 4 ne vaut PAS pour tout le monde :
le paragraphe 5 l'écarte pour les établissements de crédit, les
contreparties centrales, les plates-formes de négociation et les entités
essentielles ou importantes au sens de NIS 2.

═══ CE QUE CE MODULE NE FAIT PAS ════════════════════════════════════════
Il ne déclare pas à votre place, et il ne dit pas qu'un incident EST
majeur : il dit ce que les seuils donnent sur les éléments déclarés. Un
élément non déclaré n'est pas un seuil non atteint — c'est un élément
manquant, et il ressort comme tel.
"""

import datetime

VERSION = "2026-09-a"

SOURCES = {
    "classification": "Règlement délégué (UE) 2024/1772 — critères de "
                      "classification et seuils d'importance significative",
    "delais": "Règlement délégué (UE) 2025/301 — contenu et délais de la "
              "notification initiale et des rapports intermédiaire et final",
    "socle": "Règlement (UE) 2022/2554, articles 17 à 20",
}

RESERVE = (
    "Ce calcul porte sur les seuls éléments déclarés. Il prépare une "
    "décision de déclaration ; il ne la remplace pas, et il ne vaut pas "
    "avis juridique. En cas de doute, la sur-déclaration se discute avec "
    "l'autorité compétente — l'absence de déclaration, beaucoup moins."
)


# ═══════════════════════════════════════════════════════════════════════
# 1. LA PORTE — ARTICLE 6 DU RÈGLEMENT 2024/1772
# ═══════════════════════════════════════════════════════════════════════

PORTE = {
    "cle": "services_critiques",
    "nom": "Criticité des services touchés",
    "article": "Article 6",
    "quoi": "L'incident a touché des services TIC ou des réseaux et systèmes "
            "d'information qui soutiennent des fonctions critiques ou "
            "importantes, ou des services financiers soumis à agrément.",
    "role": "C'est une CONDITION, pas un seuil. Sans elle, l'article 8, "
            "paragraphe 1, ne peut pas être rempli, quel que soit le nombre "
            "de seuils franchis par ailleurs.",
}


# ═══════════════════════════════════════════════════════════════════════
# 2. LES SIX SEUILS — ARTICLE 9
# ═══════════════════════════════════════════════════════════════════════
# Chaque seuil est atteint dès qu'UNE de ses conditions l'est. Les
# conditions portent leur valeur chiffrée : elles se vérifient, elles ne se
# discutent pas.

SEUILS = (
    {"cle": "clients", "paragraphe": "§1",
     "nom": "Clients, contreparties financières et transactions",
     "critere": "Article premier",
     "conditions": (
         ("part_clients", "Plus de 10 % des clients utilisant le service "
                          "touché", "pourcentage", 10.0),
         ("nombre_clients", "Plus de 100 000 clients touchés utilisant le "
                            "service", "nombre", 100000),
         ("part_contreparties", "Plus de 30 % des contreparties financières "
                                "liées au service", "pourcentage", 30.0),
         ("part_transactions_nombre", "Plus de 10 % du nombre moyen "
                                      "journalier de transactions",
          "pourcentage", 10.0),
         ("part_transactions_volume", "Plus de 10 % de la valeur moyenne "
                                      "journalière des transactions",
          "pourcentage", 10.0),
         ("clients_importants", "Des clients ou contreparties considérés "
                                "comme importants ont été touchés",
          "booleen", None),
     )},
    {"cle": "reputation", "paragraphe": "§2",
     "nom": "Atteinte à la réputation",
     "critere": "Article 2",
     "conditions": (
         ("reputation", "L'une des conditions de l'article 2, points a) à "
                        "d), est remplie", "booleen", None),
     )},
    {"cle": "duree", "paragraphe": "§3",
     "nom": "Durée et interruption de service",
     "critere": "Article 3",
     "conditions": (
         ("duree_heures", "Durée de l'incident supérieure à 24 heures",
          "heures", 24.0),
         ("interruption_heures", "Interruption de service supérieure à "
                                 "2 heures pour des services TIC soutenant "
                                 "des fonctions critiques ou importantes",
          "heures", 2.0),
     )},
    {"cle": "geographie", "paragraphe": "§4",
     "nom": "Répartition géographique",
     "critere": "Article 4",
     "conditions": (
         ("etats_membres", "Incidence dans deux États membres ou plus",
          "nombre", 2),
     )},
    {"cle": "donnees", "paragraphe": "§5",
     "nom": "Pertes de données",
     "critere": "Article 5",
     "conditions": (
         ("atteinte_objectifs", "L'incidence sur la disponibilité, "
                                "l'authenticité, l'intégrité ou la "
                                "confidentialité nuit ou nuira aux objectifs "
                                "opérationnels ou au respect des exigences "
                                "réglementaires", "booleen", None),
         ("acces_malveillant", "Accès réussi, malveillant et non autorisé "
                               "aux réseaux et systèmes d'information, "
                               "susceptible d'entraîner des pertes de "
                               "données", "booleen", None),
     )},
    {"cle": "economique", "paragraphe": "§6",
     "nom": "Conséquences économiques",
     "critere": "Article 7",
     "conditions": (
         ("cout_eur", "Coûts et pertes supportés, ou susceptibles de l'être, "
                      "supérieurs à 100 000 EUR", "euros", 100000.0),
     )},
)

SEUILS_PAR_CLE = {s["cle"]: s for s in SEUILS}

# LE SEUIL QUI SUFFIT À LUI SEUL — article 8, paragraphe 1, point a).
# Il renvoie à l'article 9, paragraphe 5, point b) : l'accès malveillant
# réussi. C'est la seule condition qui n'a pas besoin d'une seconde.
CONDITION_SUFFISANTE = ("donnees", "acces_malveillant")

# Article 8, paragraphe 1, point b).
SEUILS_REQUIS = 2


# ═══════════════════════════════════════════════════════════════════════
# 3. LA RÉCURRENCE — ARTICLE 8, PARAGRAPHE 2
# ═══════════════════════════════════════════════════════════════════════
# ELLE NE VISE PAS TOUT LE MONDE, et c'est écrit. Le troisième alinéa
# écarte les microentreprises et les entités du cadre simplifié de
# l'article 16, paragraphe 1, de DORA. Appliquer la règle à une
# microentreprise lui ferait porter une surveillance mensuelle que le texte
# ne lui demande pas.

RECURRENCE = {
    "article": "Article 8, paragraphe 2",
    "conditions": (
        "Au moins deux occurrences en six mois",
        "Même cause originelle apparente",
        "Collectivement, les critères de l'incident majeur du paragraphe 1",
    ),
    "cadence": "Les entités financières évaluent l'existence d'incidents "
               "récurrents chaque mois.",
    "ne_vise_pas": "Les microentreprises et les entités relevant de "
                   "l'article 16, paragraphe 1, du règlement (UE) 2022/2554.",
}


# ═══════════════════════════════════════════════════════════════════════
# 4. L'ÉVALUATION
# ═══════════════════════════════════════════════════════════════════════

def _nombre(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _condition_atteinte(cond, valeur):
    """Une condition est-elle atteinte ? Et si on ne peut pas le dire, on
    le dit — « non déclaré » n'est pas « non atteint »."""
    _, _, nature, seuil = cond
    if nature == "booleen":
        if valeur is None:
            return None
        return bool(valeur)
    n = _nombre(valeur)
    if n is None:
        return None
    if nature == "nombre" and seuil == 2:          # deux États membres OU PLUS
        return n >= seuil
    return n > seuil


def evaluer(declaration=None):
    """L'incident est-il majeur au sens de l'article 8, paragraphe 1 ?

    LA RÉPONSE PORTE SON CALCUL. « Majeur » sans le chemin qui y mène ne
    se défend pas devant une autorité qui demandera, elle, quels seuils ont
    été retenus et sur quels chiffres.
    """
    d = declaration or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "declaration_illisible"}

    critiques = d.get("services_critiques")
    seuils, manquants = [], []
    for s in SEUILS:
        atteintes, inconnues = [], []
        for cond in s["conditions"]:
            r = _condition_atteinte(cond, d.get(cond[0]))
            if r is None:
                inconnues.append({"cle": cond[0], "quoi": cond[1]})
            elif r:
                atteintes.append({"cle": cond[0], "quoi": cond[1],
                                  "valeur": d.get(cond[0])})
        etat = {
            "cle": s["cle"], "nom": s["nom"], "paragraphe": s["paragraphe"],
            "critere": s["critere"],
            "atteint": bool(atteintes),
            "par": atteintes,
            "non_declare": inconnues,
        }
        seuils.append(etat)
        if not atteintes and inconnues:
            manquants.extend(inconnues)

    atteints = [s for s in seuils if s["atteint"]]
    suffisant = any(a["cle"] == CONDITION_SUFFISANTE[1]
                    for s in seuils if s["cle"] == CONDITION_SUFFISANTE[0]
                    for a in s["par"])

    # ── LA PORTE, ET ELLE COMMANDE ──────────────────────────────────────
    if critiques is None:
        verdict, motif = None, (
            "La criticité des services touchés n'est pas déclarée. C'est la "
            "condition de l'article 8, paragraphe 1 : sans elle, aucun "
            "verdict ne peut être rendu, quel que soit le nombre de seuils "
            "franchis.")
    elif not critiques:
        verdict, motif = False, (
            "Aucun service critique ou important n'a été touché. L'article 8, "
            "paragraphe 1, ne peut donc pas être rempli, même avec %d seuil(s) "
            "franchi(s)." % len(atteints))
    elif suffisant:
        verdict, motif = True, (
            "Des services critiques ont été touchés et le seuil de "
            "l'article 9, paragraphe 5, point b) — accès réussi, malveillant "
            "et non autorisé — est atteint. Ce seuil suffit à lui seul, au "
            "titre de l'article 8, paragraphe 1, point a).")
    elif len(atteints) >= SEUILS_REQUIS:
        verdict, motif = True, (
            "Des services critiques ont été touchés et %d seuils sont "
            "atteints : %s. L'article 8, paragraphe 1, point b), en exige "
            "deux." % (len(atteints), ", ".join(s["nom"] for s in atteints)))
    else:
        verdict, motif = False, (
            "Des services critiques ont été touchés, mais %d seuil est "
            "atteint et l'article 8, paragraphe 1, point b), en exige deux — "
            "à moins que le seuil de l'article 9, paragraphe 5, point b), ne "
            "soit atteint, ce qui n'est pas le cas."
            % len(atteints))

    return {
        "ok": True,
        "majeur": verdict,
        "motif": motif,
        "porte": {"cle": PORTE["cle"], "nom": PORTE["nom"],
                  "article": PORTE["article"], "declaree": critiques},
        "seuils": seuils,
        "atteints": [s["cle"] for s in atteints],
        "nombre_atteints": len(atteints),
        "condition_suffisante": suffisant,
        "requis": SEUILS_REQUIS,
        # UN ÉLÉMENT NON DÉCLARÉ N'EST PAS UN SEUIL NON ATTEINT. S'il en
        # reste, le verdict « non majeur » est provisoire, et le dire est
        # ce qui distingue un calcul d'une opinion.
        "non_declare": manquants,
        "verdict_provisoire": bool(manquants) and verdict is False,
        "recurrence": dict(RECURRENCE),
        "reserve": RESERVE,
        "sources": dict(SOURCES),
    }


# ═══════════════════════════════════════════════════════════════════════
# 5. LES DÉLAIS — ARTICLE 5 DU RÈGLEMENT 2025/301
# ═══════════════════════════════════════════════════════════════════════

RAPPORTS = (
    {"cle": "initial", "nom": "Notification initiale",
     "article": "Article 5, paragraphe 1, point a)",
     "regle": "Le plus tôt possible, et en tout état de cause dans les "
              "quatre heures suivant la classification comme majeur, sans "
              "dépasser vingt-quatre heures depuis la connaissance."},
    {"cle": "intermediaire", "nom": "Rapport intermédiaire",
     "article": "Article 5, paragraphe 1, point b)",
     "regle": "Au plus tard soixante-douze heures après la soumission de la "
              "notification initiale, même si rien n'a changé. Puis une mise "
              "à jour sans retard injustifié, et en tout état de cause "
              "lorsque les activités régulières ont repris."},
    {"cle": "final", "nom": "Rapport final",
     "article": "Article 5, paragraphe 1, point c)",
     "regle": "Au plus tard un mois après la soumission du rapport "
              "intermédiaire ou de sa dernière mise à jour."},
)

# Article 5, paragraphe 5 — les entités pour lesquelles le report de
# week-end NE VAUT PAS, s'agissant de la notification initiale et du
# rapport intermédiaire.
SANS_REPORT = ("etablissement_credit", "contrepartie_centrale",
               "plateforme_negociation")

REPORT = {
    "article": "Article 5, paragraphe 4",
    "quoi": "Lorsque le délai expire un jour de week-end ou un jour férié "
            "dans l'État membre de l'entité déclarante, la soumission peut "
            "intervenir au plus tard à midi le jour ouvrable suivant.",
    "ecarte": "Article 5, paragraphe 5 — le report ne s'applique pas à la "
              "notification initiale ni au rapport intermédiaire des "
              "établissements de crédit, des contreparties centrales, des "
              "plates-formes de négociation, ni des entités essentielles ou "
              "importantes au sens de l'article 3 de la directive "
              "(UE) 2022/2555.",
    "etendue": "Article 5, paragraphe 6 — l'autorité compétente peut écarter "
               "le report pour d'autres entités importantes ou systémiques. "
               "La décision est notifiée et ne vaut que pour les incidents "
               "déclarés après cette notification.",
}


def _horodatage(v):
    if isinstance(v, datetime.datetime):
        return v
    if isinstance(v, str) and v.strip():
        t = v.strip().replace("Z", "+00:00")
        try:
            return datetime.datetime.fromisoformat(t)
        except ValueError:
            return None
    return None


def _mois_plus_tard(quand):
    """Un mois, au sens courant : même quantième le mois suivant, ramené au
    dernier jour quand ce quantième n'existe pas."""
    m, a = quand.month + 1, quand.year
    if m > 12:
        m, a = 1, a + 1
    jour = quand.day
    while jour > 28:
        try:
            return quand.replace(year=a, month=m, day=jour)
        except ValueError:
            jour -= 1
    return quand.replace(year=a, month=m, day=jour)


def _reporte(quand, feries, applicable):
    """Le report de week-end — midi le jour ouvrable suivant."""
    if not applicable:
        return quand, False
    feries = set(feries or ())
    bouge = False
    j = quand
    while j.weekday() >= 5 or j.date().isoformat() in feries:
        j = (j + datetime.timedelta(days=1)).replace(
            hour=12, minute=0, second=0, microsecond=0)
        bouge = True
    return j, bouge


def delais(connaissance, classification=None, entite=None,
           nis2_essentielle_ou_importante=False, feries=None,
           initial_soumis=None, intermediaire_soumis=None):
    """Les trois échéances, calculées — et la raison de chacune.

    LA NOTIFICATION INITIALE A DEUX BORNES, pas une. Quatre heures depuis la
    classification, vingt-quatre heures depuis la connaissance : la première
    échue commande. Sauf si la classification intervient APRÈS ces
    vingt-quatre heures — le paragraphe 2 traite alors le cas à part, et
    c'est là qu'un calcul naïf se trompe, parce qu'un simple minimum
    rendrait une échéance déjà passée.
    """
    su = _horodatage(connaissance)
    if su is None:
        return {"ok": False, "motif": "connaissance_illisible",
                "motif_texte": "Le moment où l'entité a eu connaissance de "
                               "l'incident n'est pas lisible : aucun délai "
                               "ne se calcule sans lui."}
    cl = _horodatage(classification)
    report_possible = not (entite in SANS_REPORT or nis2_essentielle_ou_importante)

    borne_connaissance = su + datetime.timedelta(hours=24)
    if cl is None:
        echeance, regle = borne_connaissance, (
            "L'incident n'est pas encore classé. La borne de vingt-quatre "
            "heures depuis la connaissance court déjà ; celle de quatre "
            "heures partira de la classification.")
        tardive = None
    else:
        borne_classification = cl + datetime.timedelta(hours=4)
        tardive = cl > borne_connaissance
        if tardive:
            # Article 5, paragraphe 2.
            echeance, regle = borne_classification, (
                "La classification est intervenue plus de vingt-quatre heures "
                "après la connaissance : l'article 5, paragraphe 2, fait "
                "courir quatre heures depuis la classification.")
        else:
            echeance = min(borne_classification, borne_connaissance)
            regle = ("Les deux bornes de l'article 5, paragraphe 1, point a), "
                     "courent : quatre heures depuis la classification "
                     "(%s) et vingt-quatre heures depuis la connaissance "
                     "(%s). La première échue commande."
                     % (borne_classification.isoformat(timespec="minutes"),
                        borne_connaissance.isoformat(timespec="minutes")))

    ech_initial, bouge_i = _reporte(echeance, feries, report_possible)

    base_inter = _horodatage(initial_soumis) or ech_initial
    ech_inter, bouge_m = _reporte(
        base_inter + datetime.timedelta(hours=72), feries, report_possible)

    base_final = _horodatage(intermediaire_soumis) or ech_inter
    # LE REPORT S'APPLIQUE AU RAPPORT FINAL SANS EXCEPTION : le paragraphe 5
    # n'écarte que la notification initiale et le rapport intermédiaire.
    ech_final, bouge_f = _reporte(_mois_plus_tard(base_final), feries, True)

    return {
        "ok": True,
        "report_applicable": report_possible,
        "pourquoi_sans_report": None if report_possible else REPORT["ecarte"],
        "classification_tardive": tardive,
        "echeances": [
            {"cle": "initial", "nom": "Notification initiale",
             "quand": ech_initial.isoformat(timespec="minutes"),
             "article": RAPPORTS[0]["article"], "regle": regle,
             "reporte": bouge_i},
            {"cle": "intermediaire", "nom": "Rapport intermédiaire",
             "quand": ech_inter.isoformat(timespec="minutes"),
             "article": RAPPORTS[1]["article"],
             "regle": "Soixante-douze heures après la soumission de la "
                      "notification initiale%s."
                      % ("" if _horodatage(initial_soumis)
                         else ", comptées ici depuis l'échéance de celle-ci, "
                              "faute de date de soumission"),
             "reporte": bouge_m},
            {"cle": "final", "nom": "Rapport final",
             "quand": ech_final.isoformat(timespec="minutes"),
             "article": RAPPORTS[2]["article"],
             "regle": "Un mois après la soumission du rapport intermédiaire "
                      "ou de sa dernière mise à jour.",
             "reporte": bouge_f},
        ],
        "impossibilite": {
            "article": "Article 5, paragraphe 3",
            "quoi": "L'entité qui ne peut pas tenir un délai en informe "
                    "l'autorité compétente au plus tard dans ce même délai, "
                    "et en explique les raisons.",
        },
        "report": dict(REPORT),
        "reserve": RESERVE,
    }


def referentiel():
    return {
        "version": VERSION,
        "sources": dict(SOURCES),
        "reserve": RESERVE,
        "porte": dict(PORTE),
        "seuils": [{"cle": s["cle"], "nom": s["nom"],
                    "paragraphe": s["paragraphe"], "critere": s["critere"],
                    "conditions": [{"cle": c[0], "quoi": c[1],
                                    "nature": c[2], "seuil": c[3]}
                                   for c in s["conditions"]]}
                   for s in SEUILS],
        "condition_suffisante": {"seuil": CONDITION_SUFFISANTE[0],
                                 "condition": CONDITION_SUFFISANTE[1],
                                 "article": "Article 8, paragraphe 1, point a)"},
        "seuils_requis": SEUILS_REQUIS,
        "recurrence": dict(RECURRENCE),
        "rapports": [dict(r) for r in RAPPORTS],
        "report": dict(REPORT),
        "sans_report": list(SANS_REPORT),
    }


def _verifier():
    assert len(SEUILS) == 6, \
        "l'article 9 compte six paragraphes de seuils, §1 à §6"
    assert [s["paragraphe"] for s in SEUILS] == ["§1", "§2", "§3", "§4",
                                                 "§5", "§6"]
    cles = [s["cle"] for s in SEUILS]
    assert len(cles) == len(set(cles))
    for s in SEUILS:
        assert s["conditions"], s["cle"]
        for c in s["conditions"]:
            assert len(c) == 4, c
            assert c[2] in ("booleen", "nombre", "pourcentage", "heures",
                            "euros"), c
            if c[2] == "booleen":
                assert c[3] is None, c
            else:
                assert c[3] is not None, c

    # La condition qui suffit à elle seule existe bien là où on la cite.
    s = SEUILS_PAR_CLE[CONDITION_SUFFISANTE[0]]
    assert any(c[0] == CONDITION_SUFFISANTE[1] for c in s["conditions"]), \
        "l'article 9, paragraphe 5, point b), ne se retrouve pas dans la table"
    assert SEUILS_REQUIS == 2

    assert PORTE["cle"] not in SEUILS_PAR_CLE, \
        "la criticité est une PORTE, pas un septième seuil"
    assert len(RAPPORTS) == 3
    assert SANS_REPORT and all(isinstance(x, str) for x in SANS_REPORT)


_verifier()
