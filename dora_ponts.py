# -*- coding: utf-8 -*-
"""
DORA — CE QU'IL ÉCARTE, ET CE QU'IL RÉUTILISE.

═══ DEUX PONTS, ET ILS NE SONT PAS DE MÊME NATURE ══════════════════════
Le premier est un pont de PRÉSÉANCE : entre DORA et NIS 2, la question
n'est pas « que puis-je réutiliser », c'est « lequel des deux textes
m'est opposable ». L'article 1er, paragraphe 2, de DORA et l'article 4 de
la directive (UE) 2022/2555 se répondent, et leur effet est une mise à
l'écart — pas un recouvrement.

Le second est un pont de PREUVE : entre DORA et ISO/IEC 27001, la
question est l'inverse. La norme n'écarte rien — aucune certification ne
tient lieu de conformité à un règlement — mais un système de management
certifié produit déjà une partie des pièces que le règlement délégué
(UE) 2024/1774 réclame. Savoir lesquelles, et surtout lesquelles NON,
c'est la différence entre un programme de douze mois et un programme de
vingt-quatre.

═══ POURQUOI UN PONT QUI N'EST QUE DE LA PROSE EST UNE PROMESSE ════════
« DORA prime sur NIS 2 » se dit en réunion et ne se vérifie pas. « Les
articles 20, 21 et 23 ainsi que le chapitre VII de la directive ne vous
sont pas opposables, mais l'article 3, paragraphes 3 et 4, le reste » se
vérifie, article par article, et c'est la phrase qu'on écrit dans une
note. Les deux ponts de ce module se calculent donc, et chaque ligne
porte l'article qui la fonde.

═══ LE PIÈGE QUE CE MODULE EXISTE POUR FERMER ══════════════════════════
L'article 1er, paragraphe 2, vise les ENTITÉS FINANCIÈRES. Le prestataire
tiers de services TIC — point u) de l'article 2, paragraphe 1 — n'en est
pas une : l'article 2, paragraphe 2, réserve le terme aux points a) à t).
Un hébergeur, un exploitant de centre de données ou un fournisseur de
services gérés qui sert des banques ne voit donc RIEN d'écarté : NIS 2
lui reste pleinement opposable, et DORA l'atteint en plus, au titre du
chapitre V. C'est l'erreur de lecture la plus coûteuse du marché, et le
module refuse de la commettre.
"""

import dora
import dora_risque

VERSION = "2026-09-a"

RESERVE = (
    "Ce module rapproche deux textes ; il ne prononce pas l'articulation. "
    "Le périmètre exact de la mise à l'écart est fixé par les dispositions "
    "nationales de transposition et par les lignes directrices que la "
    "Commission publie au titre de l'article 4, paragraphe 3, de la "
    "directive (UE) 2022/2555. Seuls les textes publiés font foi."
)


# ═══════════════════════════════════════════════════════════════════════
# 1. LES SOURCES DES DEUX PONTS
# ═══════════════════════════════════════════════════════════════════════

SOURCES = (
    {"cle": "dora", "titre": "Règlement (UE) 2022/2554 (DORA)",
     "celex": "32022R2554",
     "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri="
             "CELEX:32022R2554",
     "licence": "Texte de l'Union, réutilisable avec attribution",
     "apporte": "L'article 1er, paragraphe 2, qui fait de DORA un acte "
                "juridique sectoriel, et le considérant 16, qui le dit "
                "lex specialis."},
    {"cle": "nis2", "titre": "Directive (UE) 2022/2555 (NIS 2)",
     "celex": "32022L2555",
     "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri="
             "CELEX:32022L2555",
     "licence": "Texte de l'Union, réutilisable avec attribution",
     "apporte": "L'article 4, qui dit ce qu'un acte sectoriel écarte, et "
                "l'annexe I, qui dit quels types financiers y figurent."},
    {"cle": "rts_1774", "titre": "Règlement délégué (UE) 2024/1774",
     "celex": "32024R1774",
     "lien": "https://eur-lex.europa.eu/eli/reg_del/2024/1774/oj",
     "licence": "Texte de l'Union, réutilisable avec attribution",
     "apporte": "Les quarante-deux articles contre lesquels la "
                "correspondance ISO est établie."},
    {"cle": "iso27001", "titre": "ISO/IEC 27001:2022",
     "celex": None,
     "lien": "https://www.iso.org/standard/27001",
     "licence": "Norme sous droit d'auteur. Numéros et intitulés de "
                "mesures seulement ; aucune exigence n'est reproduite.",
     "apporte": "Les quatre-vingt-treize mesures de l'annexe A et les "
                "chapitres 4 à 10, cités par numéro."},
)

#: CE QUE LE MODULE NE SAIT PAS, ET LE DIT.
LACUNES = (
    "Le périmètre exact des « dispositions pertinentes » que l'article 4, "
    "paragraphe 1, de NIS 2 écarte n'est pas énuméré par le texte. Les "
    "lignes directrices de la Commission prévues au paragraphe 3 le "
    "précisent ; ce module distingue donc ce que le texte nomme de ce qui "
    "s'en déduit.",
    "La correspondance avec ISO/IEC 27001 est un rapprochement du cabinet, "
    "établi sur l'objet de chaque article du règlement délégué. Elle "
    "n'est publiée par aucun organisme et ne lie personne.",
    "Les États membres peuvent identifier comme essentielles ou "
    "importantes des entités qui ne figurent dans aucune annexe, au titre "
    "de l'article 2, paragraphe 2, points b) à e). Le module ne connaît "
    "pas ces désignations nationales : il les accepte en déclaration.",
)


# ═══════════════════════════════════════════════════════════════════════
# 2. PONT DORA ↔ NIS 2 — LA MÉCANIQUE, EN QUATRE ARTICLES
# ═══════════════════════════════════════════════════════════════════════

MECANIQUE = (
    {"cle": "dora_c16", "texte": "DORA", "article": "Considérant 16",
     "dit": "Le règlement relève le niveau d'harmonisation et pose des "
            "exigences plus strictes que le droit de l'Union en vigueur "
            "sur les services financiers, y compris que celles de la "
            "directive (UE) 2022/2555. Il constitue à son égard une "
            "lex specialis."},
    {"cle": "dora_1_2", "texte": "DORA",
     "article": "Article 1er, paragraphe 2",
     "dit": "Pour les entités financières identifiées comme essentielles "
            "ou importantes selon les dispositions nationales transposant "
            "l'article 3 de la directive (UE) 2022/2555, le règlement est "
            "considéré comme un acte juridique sectoriel de l'Union aux "
            "fins de l'article 4 de cette directive."},
    {"cle": "nis2_4_1", "texte": "NIS 2", "article": "Article 4, "
     "paragraphe 1",
     "dit": "Lorsqu'un acte sectoriel impose des mesures de gestion des "
            "risques ou la notification des incidents importants avec un "
            "effet au moins équivalent, les dispositions pertinentes de la "
            "directive — y compris celles relatives à la supervision et à "
            "l'exécution prévues au chapitre VII — ne s'appliquent pas. "
            "Lorsque l'acte sectoriel ne couvre pas toutes les entités du "
            "secteur, la directive continue de s'appliquer aux autres."},
    {"cle": "nis2_4_2", "texte": "NIS 2", "article": "Article 4, "
     "paragraphe 2",
     "dit": "L'équivalence est acquise si les mesures de gestion des "
            "risques valent au moins celles de l'article 21, paragraphes "
            "1 et 2, ou si l'acte sectoriel ouvre aux CSIRT, aux autorités "
            "compétentes ou aux points de contact uniques un accès "
            "immédiat aux notifications et pose des exigences de "
            "notification au moins équivalentes à l'article 23, "
            "paragraphes 1 à 6."},
    {"cle": "nis2_4_3", "texte": "NIS 2", "article": "Article 4, "
     "paragraphe 3",
     "dit": "La Commission publie des lignes directrices clarifiant "
            "l'application des paragraphes 1 et 2, et les réexamine."},
)


# ═══════════════════════════════════════════════════════════════════════
# 3. CE QUE L'ARTICLE 4 ÉCARTE — ET AVEC QUELLE CERTITUDE
# ═══════════════════════════════════════════════════════════════════════
# « certitude » vaut avertissement : « texte » quand un article nomme la
# disposition écartée, « deduit » quand elle tombe sous la formule
# « dispositions pertinentes », dont le périmètre appartient aux lignes
# directrices de l'article 4, paragraphe 3. Annoncer les deux du même ton
# serait vendre une certitude qu'on n'a pas.

CERTITUDES = {
    "texte": "Un article le nomme.",
    "deduit": "Se déduit de la formule « dispositions pertinentes » de "
              "l'article 4, paragraphe 1 ; les lignes directrices de la "
              "Commission en fixent le périmètre.",
}

ECARTE = (
    {"cle": "nis2_21", "nis2": "Article 21 — Mesures de gestion des risques "
                               "en matière de cybersécurité",
     "certitude": "texte",
     "pourquoi": "L'article 4, paragraphe 2, point a), fixe l'équivalence "
                 "par rapport à l'article 21, paragraphes 1 et 2 : c'est "
                 "la disposition que l'acte sectoriel remplace.",
     "remplace_par": "DORA, chapitre II — articles 5 à 16, précisés par le "
                     "règlement délégué (UE) 2024/1774."},
    {"cle": "nis2_23", "nis2": "Article 23 — Obligations de notification",
     "certitude": "texte",
     "pourquoi": "L'article 4, paragraphe 2, point b), fixe l'équivalence "
                 "par rapport à l'article 23, paragraphes 1 à 6.",
     "remplace_par": "DORA, chapitre III — articles 17 à 23, et les délais "
                     "du règlement délégué (UE) 2025/301."},
    {"cle": "nis2_ch7", "nis2": "Chapitre VII — Supervision et exécution",
     "certitude": "texte",
     "pourquoi": "L'article 4, paragraphe 1, le nomme expressément : « y "
                 "compris celles relatives à la supervision et à "
                 "l'exécution prévues au chapitre VII ».",
     "remplace_par": "DORA, chapitre VI — la surveillance revient à "
                     "l'autorité compétente du secteur financier, ACPR ou "
                     "AMF en France."},
    {"cle": "nis2_20", "nis2": "Article 20 — Gouvernance",
     "certitude": "deduit",
     "pourquoi": "L'article 20 porte l'approbation des mesures de "
                 "l'article 21 par les organes de direction ; il suit le "
                 "sort de l'article qu'il commande. Aucun article ne le "
                 "nomme, cependant.",
     "remplace_par": "DORA, article 5 — l'organe de direction définit, "
                     "approuve et supervise le cadre, et ses membres "
                     "maintiennent à jour leurs connaissances "
                     "(article 5, paragraphe 4)."},
)

# ─── CE QUI RESTE DEBOUT ────────────────────────────────────────────────
# UNE MISE À L'ÉCART N'EST PAS UNE SORTIE DU CHAMP. Le client qui entend
# « DORA prime » comprend « NIS 2 ne me concerne plus » et cesse de
# répondre à son autorité nationale. Les quatre lignes ci-dessous sont
# celles qu'on lit à voix haute en réunion.

RESTE = (
    {"cle": "identification",
     "quoi": "L'identification comme entité essentielle ou importante, et "
             "l'inscription sur la liste que l'État membre établit.",
     "article": "NIS 2, article 3, paragraphe 3",
     "pourquoi": "L'article 1er, paragraphe 2, de DORA SUPPOSE cette "
                 "identification : elle est la condition de la mise à "
                 "l'écart, elle n'en est pas l'objet."},
    {"cle": "enregistrement",
     "quoi": "La communication à l'autorité compétente du nom, de "
             "l'adresse et des coordonnées, du secteur et sous-secteur, et "
             "des États membres où l'entité fournit ses services.",
     "article": "NIS 2, article 3, paragraphe 4",
     "pourquoi": "Ce n'est ni une mesure de gestion du risque ni une "
                 "notification d'incident : l'article 4, paragraphe 1, ne "
                 "l'atteint pas."},
    {"cle": "csirt",
     "quoi": "La transmission des notifications d'incident aux CSIRT ou "
             "aux autorités désignés au titre de NIS 2, lorsque l'État "
             "membre en décide ainsi.",
     "article": "DORA, article 19, paragraphe 1, deuxième alinéa",
     "pourquoi": "DORA prévoit lui-même ce canal, et le considérant 16 "
                 "en donne la raison : le lien avec le cadre horizontal "
                 "doit être maintenu."},
    {"cle": "non_couvertes",
     "quoi": "Les entités d'un secteur que l'acte sectoriel ne couvre pas "
             "restent sous la directive, en entier.",
     "article": "NIS 2, article 4, paragraphe 1, seconde phrase",
     "pourquoi": "DORA ne couvre pas tout ce que les annexes de NIS 2 "
                 "atteignent — à commencer par les prestataires tiers de "
                 "services TIC, qui ne sont pas des entités financières."},
)


# ═══════════════════════════════════════════════════════════════════════
# 4. QUELS TYPES FINANCIERS FIGURENT DANS LES ANNEXES DE NIS 2
# ═══════════════════════════════════════════════════════════════════════
# TROIS SUR VINGT. C'est le fait qui décide de presque tous les dossiers,
# et il n'est nulle part écrit en une phrase : une compagnie d'assurance,
# une société de gestion ou un établissement de paiement ne figure dans
# AUCUNE annexe de la directive. Il n'y a donc rien à écarter pour eux —
# non parce que DORA l'emporte, mais parce que NIS 2 ne les visait pas.

ANNEXE_I_NIS2 = (
    {"entite": "etablissement_credit", "secteur": "banque",
     "secteur_nom": "Secteur bancaire",
     "renvoi": "Établissements de crédit au sens de l'article 4, point 1), "
               "du règlement (UE) n° 575/2013"},
    {"entite": "plateforme_negociation", "secteur": "marches_financiers",
     "secteur_nom": "Infrastructures des marchés financiers",
     "renvoi": "Exploitants de plates-formes de négociation au sens de "
               "l'article 4, point 24), de la directive 2014/65/UE"},
    {"entite": "contrepartie_centrale", "secteur": "marches_financiers",
     "secteur_nom": "Infrastructures des marchés financiers",
     "renvoi": "Contreparties centrales au sens de l'article 2, point 1), "
               "du règlement (UE) n° 648/2012"},
)

ANNEXE_I_PAR_ENTITE = {a["entite"]: a for a in ANNEXE_I_NIS2}


# ═══════════════════════════════════════════════════════════════════════
# 5. LES ISSUES — CINQ, ET UNE SEULE EST « ÉCARTÉ »
# ═══════════════════════════════════════════════════════════════════════

ISSUES = {
    "ecarte": {
        "nom": "Les dispositions pertinentes de NIS 2 sont écartées",
        "quoi": "L'entité est une entité financière dans le champ de DORA "
                "et identifiée comme essentielle ou importante : "
                "l'article 1er, paragraphe 2, joue, et l'article 4 de la "
                "directive produit son effet.",
    },
    "sans_objet": {
        "nom": "Rien à écarter : NIS 2 ne vise pas cette entité",
        "quoi": "L'entité est dans le champ de DORA, mais elle n'est pas "
                "identifiée comme entité essentielle ou importante. "
                "L'article 4 n'a pas d'objet ; DORA s'applique de son "
                "propre chef.",
    },
    "cumul": {
        "nom": "Les deux textes s'appliquent, chacun à son titre",
        "quoi": "L'entité n'est pas une entité financière au sens de "
                "l'article 2, paragraphe 2 : l'article 1er, paragraphe 2, "
                "ne la vise pas. NIS 2 lui reste opposable en entier, et "
                "DORA l'atteint au titre du chapitre V.",
    },
    "hors_dora": {
        "nom": "DORA ne s'applique pas : il n'écarte rien",
        "quoi": "L'entité est exclue par l'article 2, paragraphe 3. Un "
                "règlement qui ne s'applique pas ne peut pas être l'acte "
                "sectoriel qui écarte la directive.",
    },
    "a_completer": {
        "nom": "Déclaration incomplète",
        "quoi": "Le type d'entité ou l'identification au titre de "
                "l'article 3 de la directive n'est pas déclaré. "
                "L'articulation ne se devine pas.",
    },
}


# ─── DEUX SITUATIONS QUI SE LISENT COMME LES AUTRES, ET N'EN SONT PAS ──
# MESURÉ : une compagnie d'assurance déclarée identifiée rendait
# exactement le même verdict qu'un établissement de crédit — « écarté »,
# quatre articles mis de côté — alors que son type ne figure dans AUCUNE
# annexe de la directive. Le verdict n'est pas faux : un État membre peut
# l'avoir désignée au titre de l'article 2, paragraphe 2, points b) à e).
# Mais rendre les deux du même ton laisserait passer une déclaration
# erronée sans que rien ne la signale.

ALERTES = {
    "identifiee_hors_annexe": {
        "quoi": "Ce type d'entité ne figure ni à l'annexe I ni à "
                "l'annexe II de la directive. Une identification comme "
                "entité essentielle ou importante suppose donc une "
                "désignation nationale au titre de l'article 2, "
                "paragraphe 2, points b) à e).",
        "a_verifier": "Confirmer cette désignation auprès de l'autorité "
                      "nationale avant de conclure à la mise à l'écart.",
    },
    "annexe_sans_identification": {
        "quoi": "Ce type d'entité figure à l'annexe I de la directive. "
                "L'absence d'identification suppose que l'entité reste "
                "sous les seuils de taille de l'article 2, paragraphe 1.",
        "a_verifier": "Vérifier le dépassement des seuils de taille : "
                      "au-dessus, l'identification n'est pas une option.",
    },
}


def articulation(qualification=None, identifiee_nis2=None):
    """Lequel des deux textes vous est opposable, et sur quels articles.

    `qualification` est le retour de `dora.qualifier`. `identifiee_nis2`
    est un booléen déclaré : l'entité est-elle identifiée comme
    essentielle ou importante selon les dispositions nationales
    transposant l'article 3 de la directive ?

    LE MODULE NE DEVINE PAS L'IDENTIFICATION. Elle appartient à l'État
    membre ; la supposer serait annoncer une mise à l'écart qui n'existe
    peut-être pas, et c'est précisément l'erreur qui coûte cher.
    """
    q = qualification or {}
    if not isinstance(q, dict) or not q.get("ok"):
        return {"ok": False, "motif": "qualification_illisible",
                "reserve": RESERVE}

    e = q.get("entite") or {}
    cle = e.get("cle")
    if not cle:
        return _issue("a_completer", None, identifiee_nis2,
                      "Aucun type d'entité déclaré à l'article 2, "
                      "paragraphe 1.")

    annexe = ANNEXE_I_PAR_ENTITE.get(cle)

    # ── HORS DU CHAMP DE DORA : il n'y a pas d'acte sectoriel ───────────
    if q.get("dans_le_champ") is False:
        return _issue("hors_dora", e, identifiee_nis2,
                      "Exclusion de l'article 2, paragraphe 3 : le "
                      "règlement ne s'applique pas à cette entité.",
                      annexe)

    # ── LE PRESTATAIRE TIERS N'EST PAS UNE ENTITÉ FINANCIÈRE ────────────
    # LE VERROU DU MODULE. L'article 1er, paragraphe 2, vise les entités
    # financières ; l'article 2, paragraphe 2, réserve ce terme aux points
    # a) à t). Le point u) reste donc sous NIS 2, pleinement.
    if e.get("financiere") is False:
        return _issue("cumul", e, identifiee_nis2,
                      "Prestataire tiers de services TIC : l'article 1er, "
                      "paragraphe 2, vise les entités financières, que "
                      "l'article 2, paragraphe 2, réserve aux points a) "
                      "à t). Rien n'est écarté.",
                      annexe)

    # ── L'IDENTIFICATION NIS 2 EST LA CONDITION, ET ELLE SE DÉCLARE ─────
    if identifiee_nis2 is None:
        return _issue("a_completer", e, None,
                      "L'identification comme entité essentielle ou "
                      "importante, au titre des dispositions nationales "
                      "transposant l'article 3 de la directive, n'est pas "
                      "déclarée.", annexe)

    if not identifiee_nis2:
        return _issue("sans_objet", e, False,
                      "L'entité n'est pas identifiée comme essentielle ou "
                      "importante : l'article 4 de la directive n'a pas "
                      "d'objet à son égard.", annexe)

    return _issue("ecarte", e, True,
                  "Entité financière dans le champ du règlement et "
                  "identifiée au titre de l'article 3 de la directive : "
                  "l'article 1er, paragraphe 2, fait de DORA un acte "
                  "juridique sectoriel aux fins de l'article 4.", annexe)


def _issue(cle, entite, identifiee, motif, annexe=None):
    ecarte = cle == "ecarte"
    alerte = None
    if ecarte and not annexe:
        alerte = "identifiee_hors_annexe"
    elif cle == "sans_objet" and annexe:
        alerte = "annexe_sans_identification"
    return {
        "ok": True,
        "issue": cle,
        "nom": ISSUES[cle]["nom"],
        "quoi": ISSUES[cle]["quoi"],
        "motif": motif,
        "entite": dict(entite) if entite else None,
        "identifiee_nis2": identifiee,
        "dans_annexe_nis2": bool(annexe),
        "annexe_nis2": dict(annexe) if annexe else None,
        "alerte": alerte,
        "alerte_dit": dict(ALERTES[alerte]) if alerte else None,
        # Écarté ou non, ce qui reste debout se dit toujours : c'est la
        # moitié de la phrase que le client retient de travers.
        "ecarte": [dict(x) for x in ECARTE] if ecarte else [],
        "reste": [dict(x) for x in RESTE],
        "mecanique": [dict(m) for m in MECANIQUE],
        "certitudes": dict(CERTITUDES),
        "reserve": RESERVE,
    }


# ═══════════════════════════════════════════════════════════════════════
# 6. PONT DORA ↔ ISO/IEC 27001 — LA PREUVE, PAS LA CONFORMITÉ
# ═══════════════════════════════════════════════════════════════════════
# LA NORME EST SOUS DROIT D'AUTEUR. Seuls les numéros de mesures et de
# chapitres sont cités ; aucune exigence n'est reproduite, et ce que
# chaque article du règlement délégué demande est écrit par le cabinet.

COUVERTURES = {
    "directe": {
        "nom": "Reprise directe",
        "quoi": "Le système de management produit déjà l'artefact que "
                "l'article réclame. Il reste à en vérifier le périmètre.",
        "poids": 1.0,
    },
    "partielle": {
        "nom": "Reprise partielle",
        "quoi": "Une partie de la preuve existe ; l'article demande en "
                "plus quelque chose que la norme ne couvre pas.",
        "poids": 0.5,
    },
    "aucune": {
        "nom": "Propre à DORA",
        "quoi": "Rien dans la norme n'y répond. L'exigence est à "
                "construire intégralement.",
        "poids": 0.0,
    },
}

# (article du RD 2024/1774, couverture, mesures de l'annexe A,
#  chapitres de la norme, ce que la norme ne couvre pas)
CORRESPONDANCE = (
    # ── TITRE II — CADRE COMPLET ───────────────────────────────────────
    (2, "partielle", ("A.5.1", "A.5.2", "A.5.4", "A.5.36", "A.5.37"),
     ("5.2", "5.3"),
     "Le rattachement au cadre de gestion du risque lié aux TIC de "
     "l'article 6 du règlement et son approbation par l'organe de "
     "direction."),
    (3, "partielle", ("A.5.4", "A.5.7"), ("6.1.2", "6.1.3", "8.2", "8.3"),
     "Le niveau de TOLÉRANCE au risque lié aux TIC approuvé au titre de "
     "l'article 6, paragraphe 8, point b), du règlement."),
    (4, "directe", ("A.5.9", "A.5.10", "A.5.37"), (), None),
    (5, "directe", ("A.5.9", "A.5.11", "A.5.12", "A.5.13"), (), None),
    (6, "directe", ("A.8.24",), (), None),
    (7, "partielle", ("A.8.24",), (),
     "Le cycle de vie complet des clés — génération, renouvellement, "
     "archivage, révocation, destruction — que la norme traite en une "
     "seule mesure."),
    (8, "directe", ("A.5.37", "A.8.9", "A.8.19", "A.8.32"), (), None),
    (9, "directe", ("A.8.6",), (), None),
    (10, "directe", ("A.5.7", "A.8.8"), (), None),
    (11, "directe", ("A.5.12", "A.8.3", "A.8.10", "A.8.11", "A.8.12",
                     "A.8.13"), (), None),
    (12, "directe", ("A.8.15", "A.8.16", "A.8.17"), (), None),
    (13, "directe", ("A.8.20", "A.8.21", "A.8.22", "A.8.23"), (), None),
    (14, "directe", ("A.5.14", "A.8.24"), (), None),
    (15, "partielle", ("A.5.8",), (),
     "Le rattachement des projets de TIC à la stratégie de résilience "
     "opérationnelle numérique et le compte rendu à l'organe de "
     "direction."),
    (16, "directe", ("A.8.25", "A.8.26", "A.8.27", "A.8.28", "A.8.29",
                     "A.8.30", "A.8.31", "A.8.33"), (), None),
    (17, "directe", ("A.8.32",), (), None),
    (18, "directe", ("A.7.1", "A.7.2", "A.7.4", "A.7.5", "A.7.8", "A.7.11",
                     "A.7.12", "A.7.13"), (), None),
    (19, "directe", ("A.6.1", "A.6.2", "A.6.3", "A.6.4", "A.6.5", "A.6.6"),
     ("7.2", "7.3"), None),
    (20, "directe", ("A.5.16", "A.5.17", "A.8.5"), (), None),
    (21, "directe", ("A.5.3", "A.5.15", "A.5.18", "A.8.2", "A.8.3",
                     "A.8.18"), (), None),
    (22, "partielle", ("A.5.24", "A.5.26"), (),
     "Le rattachement au processus de gestion des incidents de "
     "l'article 17 du règlement, et la classification de l'article 18 qui "
     "décide de la notification."),
    (23, "partielle", ("A.5.25", "A.8.16"), (),
     "Les critères de déclenchement de la détection, alignés sur les "
     "seuils du règlement délégué (UE) 2024/1772."),
    (24, "partielle", ("A.5.29", "A.5.30"), (),
     "L'analyse d'incidences sur les activités de l'article 11, "
     "paragraphe 5, du règlement, et les objectifs de temps et de point "
     "de reprise qui en découlent."),
    (25, "partielle", ("A.5.29", "A.5.30"), ("9.1",),
     "La périodicité et les scénarios que le règlement impose, que la "
     "norme laisse à l'organisme."),
    (26, "partielle", ("A.5.29", "A.5.30", "A.8.13", "A.8.14"), (),
     "Les conditions d'activation et de désactivation des plans, et leur "
     "articulation avec la notification des incidents majeurs."),
    (27, "aucune", (), (),
     "Le rapport sur le réexamen du cadre, dans un format électronique "
     "interrogeable, destiné à l'autorité compétente. Aucune mesure de "
     "l'annexe A ne le produit."),
    # ── TITRE III — CADRE SIMPLIFIÉ ────────────────────────────────────
    (28, "partielle", ("A.5.2", "A.5.4"), ("5.1", "5.3"),
     "La responsabilité de l'organe de direction telle que l'article 5, "
     "paragraphe 2, du règlement la définit, et la formation de ses "
     "membres qu'impose le paragraphe 4."),
    (29, "directe", ("A.5.1", "A.5.36"), ("5.2",), None),
    (30, "directe", ("A.5.9", "A.5.12"), (), None),
    (31, "partielle", ("A.5.4",), ("6.1.1", "6.1.2", "6.1.3", "8.2", "8.3"),
     "Le niveau de tolérance au risque lié aux TIC et le compte rendu à "
     "l'organe de direction que l'article 16 du règlement commande."),
    (32, "directe", ("A.7.1", "A.7.2", "A.7.4", "A.7.5", "A.7.8", "A.7.11"),
     (), None),
    (33, "directe", ("A.5.15", "A.5.16", "A.5.18", "A.7.2", "A.8.2",
                     "A.8.5"), (), None),
    (34, "directe", ("A.5.9", "A.5.22", "A.8.6", "A.8.8", "A.8.9",
                     "A.8.13"), (), None),
    (35, "directe", ("A.8.7", "A.8.12", "A.8.20", "A.8.22", "A.8.24"),
     (), None),
    (36, "partielle", ("A.8.29",), ("9.2",),
     "Le plan de tests de sécurité des TIC, qui doit confirmer "
     "l'efficacité des mesures des articles 33 à 35, 37 et 38 du "
     "règlement délégué."),
    (37, "directe", ("A.8.25", "A.8.26", "A.8.27", "A.8.30", "A.8.31"),
     (), None),
    (38, "directe", ("A.5.8", "A.8.32"), (), None),
    (39, "partielle", ("A.5.29", "A.5.30"), (),
     "Le scénario de cyberattaque et le basculement vers les capacités "
     "de secours que le règlement délégué impose de prévoir."),
    (40, "partielle", ("A.5.29", "A.5.30"), (),
     "La périodicité annuelle des tests de sauvegarde et de "
     "restauration, que la norme ne fixe pas."),
    (41, "aucune", (), (),
     "Le rapport sur le réexamen du cadre simplifié, dans un format "
     "électronique interrogeable, destiné à l'autorité compétente."),
)

CORRESPONDANCE_PAR_ARTICLE = {c[0]: c for c in CORRESPONDANCE}

# ─── CE QU'AUCUN CERTIFICAT NE COUVRE ───────────────────────────────────
# CHAQUE LIGNE PORTE SON ARTICLE. « La norme ne couvre pas tout » ne se
# discute pas ; « la norme ne couvre pas l'article 28, paragraphe 3 » se
# vérifie, et c'est la différence entre un avertissement et un argument.

NE_REMPLACE_PAS = (
    {"cle": "supervision",
     "quoi": "La surveillance de l'autorité compétente — ACPR ou AMF en "
             "France. Un organisme accrédité certifie un système de "
             "management ; il ne délivre aucune conformité à un règlement.",
     "article": "DORA, chapitre VI"},
    {"cle": "delais",
     "quoi": "Les délais de notification : quatre heures à compter de la "
             "classification et au plus tard vingt-quatre heures à "
             "compter de la connaissance, soixante-douze heures pour le "
             "rapport intermédiaire, un mois pour le rapport final. "
             "Aucune norme ne fixe d'heure.",
     "article": "DORA, article 19 ; règlement délégué (UE) 2025/301, "
                "article 5"},
    {"cle": "classification",
     "quoi": "La classification des incidents contre les seuils chiffrés "
             "qui décident de la notification — clients touchés, durée, "
             "États membres concernés, coûts.",
     "article": "DORA, article 18 ; règlement délégué (UE) 2024/1772"},
    {"cle": "registre",
     "quoi": "Le registre d'informations de tous les accords contractuels "
             "portant sur des services TIC, tenu aux niveaux individuel, "
             "sous-consolidé et consolidé.",
     "article": "DORA, article 28, paragraphe 3"},
    {"cle": "clauses",
     "quoi": "Les neuf clauses contractuelles de l'article 30, "
             "paragraphe 2, et les six clauses supplémentaires du "
             "paragraphe 3 pour les fonctions critiques ou importantes. "
             "La mesure A.5.20 demande des accords ; elle n'en écrit pas "
             "le contenu.",
     "article": "DORA, article 30"},
    {"cle": "tlpt",
     "quoi": "Les tests de pénétration fondés sur la menace, dont "
             "l'obligation est déterminée par les autorités, et non par "
             "l'entité elle-même.",
     "article": "DORA, articles 26 et 27 ; règlement délégué "
                "(UE) 2025/1190, article 2"},
    {"cle": "organe_direction",
     "quoi": "La responsabilité NOMMÉE et personnelle de l'organe de "
             "direction sur le cadre de gestion du risque lié aux TIC. La "
             "mesure A.5.4 demande un engagement ; le règlement désigne "
             "un responsable.",
     "article": "DORA, article 5, paragraphes 2 et 4"},
    {"cle": "perimetre",
     "quoi": "Le domaine d'application. Celui du système de management "
             "est choisi par l'organisme ; celui du règlement ne l'est "
             "pas — il couvre tout ce qui soutient les fonctions "
             "critiques ou importantes. Reprendre le premier pour le "
             "second est l'erreur la plus courante de cette greffe.",
     "article": "DORA, article 6, paragraphe 1"},
)


def apport(regime=None, mesures_en_place=None):
    """Ce qu'un système de management certifié apporte déjà — et à quoi.

    `mesures_en_place` est l'ensemble des numéros de mesures de l'annexe A
    que le client déclare mises en œuvre. Sans lui, le module rend la
    carte théorique — ce qu'apporterait un SMSI dont TOUTES les mesures
    seraient en place — et le dit.

    LE RÉGIME EST OBLIGATOIRE, POUR LA MÊME RAISON QUE DANS L'ANALYSE DE
    RISQUE : les deux titres du règlement délégué ne se recouvrent pas,
    et répondre sur le mauvais titre serait pire que ne pas répondre.
    """
    if regime not in dora_risque.REGIMES:
        return {"ok": False, "motif": "regime_absent",
                "attendu": sorted(dora_risque.REGIMES),
                "pourquoi": "Les titres II et III du règlement délégué ne "
                            "se recouvrent pas : la correspondance n'a de "
                            "sens que dans un régime déclaré.",
                "reserve": RESERVE}

    declare = mesures_en_place is not None
    tenues = set(mesures_en_place or ())
    inconnues = sorted(m for m in tenues if m not in _MESURES_ISO)

    lignes = []
    for num, _titre, _t, _c, _cn in dora_risque.articles(regime):
        n, couv, mes, chaps, manque = CORRESPONDANCE_PAR_ARTICLE[num]
        presentes = tuple(m for m in mes if m in tenues)
        absentes = tuple(m for m in mes if m not in tenues)
        if not declare:
            appui = couv
        elif not mes:
            appui = "aucune"
        elif not presentes:
            appui = "aucune"
        elif absentes:
            appui = "partielle"
        else:
            appui = couv
        lignes.append({
            "article": n,
            "titre": _titre,
            "chapitre": _c,
            "chapitre_nom": _cn,
            "couverture": couv,
            "couverture_nom": COUVERTURES[couv]["nom"],
            "appui": appui,
            "appui_nom": COUVERTURES[appui]["nom"],
            "mesures": list(mes),
            "mesures_tenues": list(presentes),
            "mesures_manquantes": list(absentes),
            "chapitres": list(chaps),
            "ne_couvre_pas": manque,
        })

    total = len(lignes)
    directes = [l for l in lignes if l["appui"] == "directe"]
    partielles = [l for l in lignes if l["appui"] == "partielle"]
    propres = [l for l in lignes if l["couverture"] == "aucune"]
    poids = sum(COUVERTURES[l["appui"]]["poids"] for l in lignes)

    return {
        "ok": True,
        "version": VERSION,
        "regime": regime,
        "regime_nom": dora_risque.REGIMES[regime]["nom"],
        "titre": dora_risque.REGIMES[regime]["titre"],
        "declare": declare,
        "mesures_declarees": sorted(tenues),
        "mesures_inconnues": inconnues,
        "total": total,
        "lignes": lignes,
        "reprise_directe": len(directes),
        "reprise_partielle": len(partielles),
        "propres_a_dora": [{"article": l["article"], "titre": l["titre"],
                            "pourquoi": l["ne_couvre_pas"]}
                           for l in propres],
        "taux_appui": round(100.0 * poids / total, 1) if total else 0.0,
        "mesures_a_pointer": sorted(
            {m for l in lignes for m in l["mesures"]}, key=_ordre_mesure),
        "ne_remplace_pas": [dict(x) for x in NE_REMPLACE_PAS],
        # LE TAUX SE DÉSAMORCE LUI-MÊME. Un chiffre d'appui lu comme un
        # taux de conformité est pire qu'aucun chiffre : il rassure.
        "ce_que_le_taux_ne_dit_pas":
            "Ce pourcentage mesure une REPRISE DE PREUVES, pas une "
            "conformité. Il dit quelle part des articles du règlement "
            "délégué trouve un répondant dans un système de management "
            "certifié — il ne dit pas que ces articles sont tenus, et "
            "encore moins que l'autorité compétente l'admettra.",
        "reserve": RESERVE,
    }


def _ordre_mesure(num):
    bouts = num.replace("A.", "").split(".")
    return tuple(int(b) for b in bouts)


def referentiel(regime=None):
    r = {
        "version": VERSION,
        "reserve": RESERVE,
        "sources": [dict(s) for s in SOURCES],
        "lacunes": list(LACUNES),
        "mecanique": [dict(m) for m in MECANIQUE],
        "certitudes": dict(CERTITUDES),
        "ecarte": [dict(x) for x in ECARTE],
        "reste": [dict(x) for x in RESTE],
        "annexe_i_nis2": [dict(a) for a in ANNEXE_I_NIS2],
        "issues": {k: dict(v) for k, v in ISSUES.items()},
        "alertes": {k: dict(v) for k, v in ALERTES.items()},
        "couvertures": {k: dict(v) for k, v in COUVERTURES.items()},
        "ne_remplace_pas": [dict(x) for x in NE_REMPLACE_PAS],
    }
    if regime in dora_risque.REGIMES:
        r["apport"] = apport(regime)
    return r


# ═══════════════════════════════════════════════════════════════════════
# 7. LE RÉFÉRENTIEL SE CONTREDIT-IL ? CONTRÔLÉ À L'IMPORT
# ═══════════════════════════════════════════════════════════════════════

def _mesures_iso():
    """Les numéros de l'annexe A, pris à la source et jamais recopiés."""
    import iso27001
    return set(iso27001.MESURES)


_MESURES_ISO = _mesures_iso()


def _verifier():
    fautes = []

    # ── La correspondance couvre TOUS les articles évaluables, et EUX
    #    SEULS. Un article oublié ferait mentir le dénominateur ; un
    #    article en trop ferait porter au régime des exigences de l'autre.
    evaluables = {n for n, _t, _ti, _c, _cn in dora_risque.ARTICLES_1774
                  if n not in dora_risque.HORS_EVALUATION}
    couverts = set(CORRESPONDANCE_PAR_ARTICLE)
    if couverts != evaluables:
        fautes.append("correspondance ≠ articles évaluables : manquent %s, "
                      "en trop %s" % (sorted(evaluables - couverts),
                                      sorted(couverts - evaluables)))

    # ── Toute mesure citée EXISTE dans l'annexe A. Un numéro inventé
    #    survivrait à toute relecture : personne ne connaît les 93 par cœur.
    for n, couv, mes, chaps, manque in CORRESPONDANCE:
        for m in mes:
            if m not in _MESURES_ISO:
                fautes.append("article %d : mesure %s absente de "
                              "l'annexe A" % (n, m))
        if couv not in COUVERTURES:
            fautes.append("article %d : couverture inconnue %r" % (n, couv))
        # ── Une couverture partielle ou nulle DIT ce qui manque. Sans
        #    cela, « partielle » est un mot sans contenu.
        if couv in ("partielle", "aucune") and not manque:
            fautes.append("article %d : couverture %s sans motif" % (n, couv))
        if couv == "directe" and manque:
            fautes.append("article %d : couverture directe avec un motif de "
                          "manque" % n)
        if couv == "aucune" and mes:
            fautes.append("article %d : couverture nulle avec des mesures"
                          % n)
        if couv != "aucune" and not mes and not chaps:
            fautes.append("article %d : couverture %s sans aucun appui"
                          % (n, couv))

    # ── Les trois types de l'annexe I existent à l'article 2, §1, et sont
    #    des entités financières.
    for a in ANNEXE_I_NIS2:
        e = dora.ENTITES_PAR_CLE.get(a["entite"])
        if not e:
            fautes.append("annexe I NIS 2 : type %r inconnu de DORA"
                          % a["entite"])
        elif not e[3]:
            fautes.append("annexe I NIS 2 : %r n'est pas une entité "
                          "financière" % a["entite"])

    # ── Aucune certitude inventée.
    for x in ECARTE:
        if x["certitude"] not in CERTITUDES:
            fautes.append("mise à l'écart %r : certitude inconnue %r"
                          % (x["cle"], x["certitude"]))

    # ── Les deux articles de rapport n'ont AUCUN répondant. C'est le
    #    résultat le plus utile du pont, et une correspondance ajoutée par
    #    distraction le ferait disparaître sans bruit.
    for n in (27, 41):
        if CORRESPONDANCE_PAR_ARTICLE[n][1] != "aucune":
            fautes.append("article %d : le rapport à l'autorité ne peut pas "
                          "avoir de répondant dans la norme" % n)

    return fautes


_FAUTES = _verifier()
assert not _FAUTES, "dora_ponts.py se contredit : %s" % _FAUTES
