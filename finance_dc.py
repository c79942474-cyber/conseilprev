# -*- coding: utf-8 -*-
"""Enveloppe d'investissement et DPGF d'un centre de données, pays par pays.

CE QUE CE MODULE FAIT, ET CE QU'IL REFUSE DE FAIRE

Un investisseur qui décide GO / NO GO a besoin de trois choses : un ordre de
grandeur d'enveloppe, sa décomposition par poste, et la comparaison entre les
pays qu'il envisage. Ce module produit les trois. Il ne produit PAS un prix.

La distinction n'est pas rhétorique, elle est mesurée. Sur les 97 centres de
données du référentiel :
  — AUCUN ne publie sa capacité informatique ;
  — DEUX seulement publient un montant d'investissement, et ni l'un ni l'autre
    ne publie la capacité correspondante.
Il est donc impossible de calibrer un coût au mégawatt sur nos propres données,
et toute valeur au MW affichée ici serait une invention habillée en référentiel.
Le coût unitaire est par conséquent un PARAMÈTRE, déclaré comme hypothèse,
donné en fourchette large, et destiné à être remplacé par vos devis.

CE QUE LE MODULE APPORTE À LA PLACE, ET QUI A DE LA VALEUR

  1. Une DPGF complète et auditable — quatorze lots, chacun avec sa part du
     total en fourchette, sa nature et ce qu'il recouvre. C'est la structure
     qui manque le plus souvent en phase amont, bien avant le prix.
  2. Une modulation par pays UNIQUEMENT là où un critère sourcé la justifie :
     le mode de refroidissement découle du climat et du stress hydrique
     (référentiel d'implantation), l'électricité de la classe de prix Eurostat,
     le coût carbone de l'intensité Ember. Rien d'autre n'est modulé.
  3. La liste explicite de ce que le référentiel NE PEUT PAS trancher —
     foncier, main-d'œuvre, permis, fiscalité — avec la question à poser. Un
     comparateur qui masquerait ces postes ferait croire à une décision
     complète ; celui-ci les affiche vides, et c'est le point.
  4. Un écart entre pays qui SÉPARE ce qui est justifié de ce qui reste à
     renseigner, poste par poste.
  5. Un échéancier jusqu'en 2030 ancré sur la file de raccordement comptée
     depuis les statuts des 97 sites, et sur les annonces datées du référentiel
     de perspectives.

NATURE DE CHAQUE VALEUR, comme partout ailleurs sur cette page
  referentiel  valeur d'une source publique nommée, avec millésime
  calcule      dérivée de nos propres données
  hypothese    ordre de grandeur de filière, à remplacer par vos devis
  analyse      lecture du cabinet, datée

AVERTISSEMENT
Ce module CADRE une décision ; il ne remplace ni une étude de réseau, ni une
étude de sol, ni une consultation d'entreprises, ni une due diligence. Aucune
valeur produite ici n'est un engagement de prix.
"""
from datetime import datetime, timezone

VERSION = "2026-08-a"

AVERTISSEMENT = (
    "Enveloppe de CADRAGE. Le coût au mégawatt provient d'un relevé publié "
    "(Soben, part of Accenture — Data Centre Trends Report 2026, p. 8), en "
    "dollars, converti au taux déclaré : c'est un ordre de grandeur de marché, "
    "pas votre prix. Aucun des 97 sites du référentiel ne publiant sa capacité, "
    "rien ici ne remplace vos devis."
)

# ═══════════════════════════════════════════════════════════════════════════
# 1. LE COÛT UNITAIRE — DÉSORMAIS SOURCÉ, ET NON PLUS SUPPOSÉ
#
# La première version de ce module donnait une fourchette de filière déclarée
# HYPOTHÈSE, faute de source : aucun des 97 sites du référentiel ne publie sa
# capacité, deux seulement publient un montant, et sans la capacité
# correspondante — impossible d'en dériver un coût au mégawatt.
#
# Le Data Centre Trends Report 2026 de Soben, part of Accenture, publie
# précisément cette valeur, issue de leurs propres relevés de coûts :
#
#   « Research by Soben, part of Accenture, found that while cloud data centres
#     currently cost between $8 million and $10 million per MW, GW+ AI data
#     centres are costing as much as $17 million per MW. Contrary to popular
#     belief, this signals that economies of scale are not driving the savings
#     some would expect. »                              (rapport 2026, page 8)
#
# Deux précautions, et elles comptent autant que le chiffre :
#
#   1. LA MONNAIE. La source est en DOLLARS. Convertir en silence reviendrait à
#      fabriquer une précision que la source ne porte pas. Le montant en dollars
#      est donc conservé tel quel, et la conversion passe par un taux DÉCLARÉ,
#      daté, modifiable — dont la nature est « hypothèse », parce qu'un taux de
#      change du jour n'est pas une donnée de référentiel.
#   2. LA COUVERTURE. La source distingue « cloud » et « GW+ AI ». Elle ne dit
#      rien du site régional : ce gabarit-là reste une hypothèse, et le module
#      l'écrit au lieu de faire passer l'ensemble pour sourcé.
# ═══════════════════════════════════════════════════════════════════════════
EUR_USD = 0.92
SOURCE_TAUX = {
    "titre": "Taux de conversion dollar → euro appliqué aux coûts publiés en dollars",
    "valeur": EUR_USD,
    "nature": "hypothese",
    "note": "Ordre de grandeur, à ajuster à la date de votre décision. Un coût "
            "d'investissement s'engage sur plusieurs années : le taux du jour "
            "n'est pas une donnée de référentiel, et une couverture de change "
            "est un contrat, pas une statistique.",
}

COUT_MW = {
    "campus_ia":   {"nom": "Campus dédié à l'IA", "musd_mw": [12.0, 17.0],
                    "nature": "referentiel",
                    "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 8",
                    "citation": "GW+ AI data centres are costing as much as $17 million per MW",
                    "sens": "densité par baie très élevée, refroidissement liquide fréquent, "
                            "redondance forte. La source donne 17 M$/MW comme HAUT de "
                            "fourchette pour les campus de l'ordre du gigawatt ; la borne "
                            "basse retenue ici marque l'écart avec le cloud, la source ne "
                            "la publiant pas"},
    "hyperscale":  {"nom": "Campus hyperscale (cloud)", "musd_mw": [8.0, 10.0],
                    "nature": "referentiel",
                    "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 8",
                    "citation": "cloud data centres currently cost between $8 million and "
                                "$10 million per MW",
                    "sens": "la fourchette publiée pour le cloud, telle quelle"},
    "colocation":  {"nom": "Colocation / hébergement", "musd_mw": [8.0, 11.0],
                    "nature": "analyse",
                    "source": "lecture du cabinet à partir de la fourchette cloud (Soben 2026, p. 8)",
                    "sens": "même socle technique que le cloud, majoré de la redondance "
                            "contractuelle et du cloisonnement par client. La source ne "
                            "traite pas ce gabarit séparément"},
    "regional":    {"nom": "Site régional ou spécialisé", "musd_mw": [9.0, 16.0],
                    "nature": "hypothese",
                    "source": "hypothèse de cadrage CONSEILPREV — NON couverte par la source",
                    "sens": "pas d'effet d'échelle, coûts fixes rapportés à une puissance "
                            "faible. Aucune source publiée ne chiffre ce gabarit : cette "
                            "fourchette reste une hypothèse et se remplace en priorité"},
}
# La page et le moteur travaillent en euros : la conversion est faite ici, une
# seule fois, et le montant en dollars reste exposé à côté.
for _g in COUT_MW.values():
    _g["meur_mw"] = [round(_g["musd_mw"][0] * EUR_USD, 2),
                     round(_g["musd_mw"][1] * EUR_USD, 2)]

SOURCE_COUT = {
    "titre": "Coût d'investissement au mégawatt IT",
    "editeur": "Soben (part of Accenture) — Data Centre Trends Report 2026, page 8",
    "nature": "referentiel",
    "note": "Relevé de coûts d'un cabinet d'economie de la construction, publié en "
            "DOLLARS et converti au taux déclaré. La source distingue le cloud "
            "(8 à 10 M$/MW) des campus d'IA de l'ordre du gigawatt (jusqu'à "
            "17 M$/MW) et souligne que les économies d'échelle n'y jouent PAS "
            "dans le sens attendu. Elle ne couvre ni la colocation ni le site "
            "régional : ces deux gabarits portent leur propre nature.",
}

# La vitesse se paie, et la source le chiffre : « a US hyperscaler recently
# accepted a 25% uplift in tender price from a GC to deliver to a demanding
# timeline » (Soben 2026, p. 8). C'est un levier à part entière d'une décision
# d'investissement — le seul, dans ce module, qui augmente sciemment la dépense.
PRIME_VITESSE = {
    "aucune":   {"nom": "Calendrier de marché", "coef": 1.00, "mois": 0,
                 "sens": "pas de compression, l'entreprise générale travaille à son rythme"},
    "acceleree": {"nom": "Calendrier accéléré", "coef": 1.12, "mois": -6,
                  "sens": "compression modérée : préfabrication, achats anticipés, "
                          "équipes renforcées"},
    "maximale": {"nom": "Vitesse maximale", "coef": 1.25, "mois": -12,
                 "nature": "referentiel",
                 "source": "Soben 2026, p. 8 — surcoût de 25 % accepté par un hyperscaler "
                           "américain pour tenir un calendrier exigeant",
                 "sens": "la valeur haute observée sur le marché. Elle ne garantit "
                         "pas le délai : elle achète la priorité d'une entreprise "
                         "générale, dans un marché où moins de dix d'entre elles "
                         "dominent l'EMEA"},
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. LA DPGF — quatorze lots
#    `part` : part du total en fourchette (fractions). Les bornes basses ne
#    somment pas à 1 et les hautes non plus : c'est normal, un lot lourd se
#    compense sur les autres. La normalisation est faite au calcul, et elle
#    est affichée.
#    `module` : le lot est-il modulé par le pays, et par quel critère SOURCÉ ?
#    `arenseigner` : le référentiel ne peut pas trancher ce poste.
# ═══════════════════════════════════════════════════════════════════════════
LOTS = [
    {"code": "00", "nom": "Études, maîtrise d'œuvre et autorisations",
     "part": [0.030, 0.055], "module": None, "arenseigner": True,
     "recouvre": "études de sol et hydrogéologiques, maîtrise d'œuvre, bureaux d'études "
                 "structure / fluides / électricité, AMO, dossier de permis, étude d'impact",
     "question": "Quel est le coût de l'instruction dans ce pays, et son délai opposable ?"},
    {"code": "01", "nom": "Foncier, VRD et raccordements de site",
     "part": [0.040, 0.110], "module": None, "arenseigner": True,
     "recouvre": "acquisition ou bail du terrain, terrassement, voiries, réseaux divers, "
                 "clôture périmétrique, bassin de rétention",
     "question": "Quel est le prix du foncier viabilisé sur la zone visée ?"},
    {"code": "02", "nom": "Gros œuvre, clos et couvert",
     "part": [0.090, 0.150], "module": None, "arenseigner": True,
     "recouvre": "fondations, structure, dalles techniques, façades, toiture, "
                 "résistance au feu, protection sismique le cas échéant",
     "question": "Quel est l'indice local du coût de la construction et de la main-d'œuvre ?"},
    {"code": "03", "nom": "Raccordement électrique HTB / HTA et poste source",
     "part": [0.070, 0.140], "module": "raccordement", "arenseigner": True,
     "recouvre": "poste de livraison, liaisons, transformateurs de puissance, "
                 "quote-part de renforcement du réseau amont",
     "question": "Le gestionnaire de réseau a-t-il donné un délai et une quote-part OPPOSABLES ?"},
    {"code": "04", "nom": "Distribution électrique et alimentation sans coupure",
     "part": [0.150, 0.230], "module": None, "arenseigner": False,
     "recouvre": "TGBT, onduleurs et batteries, groupes électrogènes et cuves, "
                 "distribution jusqu'aux baies, régime de neutre, sélectivité",
     "question": None},
    {"code": "05", "nom": "Production et distribution de froid",
     "part": [0.110, 0.200], "module": "refroidissement", "arenseigner": False,
     "recouvre": "groupes froid ou aéroréfrigérants, boucles d'eau glacée, "
                 "free cooling, pompes, redondance N+1 ou 2N",
     "question": None},
    {"code": "06", "nom": "Traitement d'air et confinement en salle",
     "part": [0.035, 0.070], "module": "refroidissement", "arenseigner": False,
     "recouvre": "armoires de climatisation, confinement d'allées, "
                 "portes de baie et obturateurs, régulation de pression",
     "question": None},
    {"code": "07", "nom": "Eau, fluides et traitement",
     "part": [0.015, 0.045], "module": "eau", "arenseigner": False,
     "recouvre": "adduction, stockage tampon, traitement et bâchage, "
                 "rejets et conventions de déversement",
     "question": None},
    {"code": "08", "nom": "Sécurité incendie",
     "part": [0.025, 0.045], "module": None, "arenseigner": False,
     "recouvre": "détection très haute sensibilité, extinction par gaz inerte, "
                 "compartimentage, désenfumage, réserve incendie",
     "question": None},
    {"code": "09", "nom": "Sûreté, contrôle d'accès et vidéoprotection",
     "part": [0.015, 0.035], "module": None, "arenseigner": False,
     "recouvre": "périmétrie, sas et tourniquets, contrôle d'accès, vidéo, "
                 "poste de sûreté, durcissement des locaux techniques",
     "question": None},
    {"code": "10", "nom": "GTB, DCIM et courants faibles",
     "part": [0.020, 0.045], "module": None, "arenseigner": False,
     "recouvre": "supervision technique, métrologie PUE et WUE au point de mesure, "
                 "comptage divisionnaire, réseaux d'exploitation",
     "question": None},
    {"code": "11", "nom": "Aménagement des salles informatiques",
     "part": [0.045, 0.090], "module": None, "arenseigner": False,
     "recouvre": "planchers techniques, baies et allées, chemins de câbles, "
                 "distribution en salle, cuivre et fibre — HORS serveurs",
     "question": None},
    {"code": "12", "nom": "Essais, mise en service et certifications",
     "part": [0.020, 0.040], "module": None, "arenseigner": False,
     "recouvre": "essais intégrés en charge, réception par niveau, "
                 "dossier des ouvrages exécutés, certification de conception le cas échéant",
     "question": None},
    {"code": "13", "nom": "Aléas et provision pour risques",
     "part": [0.050, 0.100], "module": "delai", "arenseigner": False,
     "recouvre": "provision d'aléas travaux, dérive des délais, "
                 "révision de prix, tension d'approvisionnement",
     "question": None},
]
SOURCE_LOTS = {
    "titre": "Décomposition du prix global et forfaitaire — centre de données",
    "editeur": "structure de cadrage CONSEILPREV",
    "nature": "hypothese",
    "note": "La STRUCTURE des lots est celle d'une consultation d'entreprises "
            "usuelle. Les PARTS sont des ordres de grandeur de filière en "
            "fourchette : l'électromécanique — lots 04, 05 et 06 — domine "
            "toujours l'enveloppe d'un centre de données, c'est le fait "
            "structurant. Chaque part est modifiable.",
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. LES SCÉNARIOS
#    Un même pays ne se chiffre pas de la même façon selon qu'on construit,
#    qu'on étend ou qu'on reprend. Les coefficients par lot disent CE QUI
#    DISPARAÎT et ce qui reste.
# ═══════════════════════════════════════════════════════════════════════════
SCENARIOS = {
    "neuve": {
        "nom": "Construction neuve",
        "sens": "terrain nu, poste source à créer, tous les lots au complet",
        "coef": {},                      # référence : tout à 1
        "duree_mois": [36, 60],
        "note": "Le délai est commandé par le raccordement, pas par le chantier.",
    },
    "extension": {
        "nom": "Extension d'un site existant",
        "sens": "foncier acquis, poste source existant à renforcer, gros œuvre partiel",
        "coef": {"00": 0.6, "01": 0.15, "02": 0.55, "03": 0.45, "09": 0.4, "10": 0.6},
        "duree_mois": [18, 36],
        "note": "L'extension bute rarement sur le bâtiment : elle bute sur la marge "
                "disponible du poste source et sur le permis, qui n'est jamais acquis.",
    },
    "reprise": {
        "nom": "Reprise / rachat d'un site existant",
        "sens": "acquisition, puis remise à niveau — le neuf n'est pas la référence",
        "coef": {"00": 0.35, "01": 0.0, "02": 0.10, "03": 0.20, "04": 0.45,
                 "05": 0.55, "06": 0.5, "07": 0.3, "08": 0.4, "09": 0.5,
                 "10": 0.7, "11": 0.45, "12": 0.6, "13": 0.9},
        "duree_mois": [9, 24],
        "note": "Ces coefficients chiffrent la REMISE À NIVEAU, jamais le prix "
                "d'acquisition : celui-ci se négocie et ne se modélise pas.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# 4. MODULATION PAR PAYS — uniquement sur des critères sourcés
# ═══════════════════════════════════════════════════════════════════════════
# Le mode de refroidissement retenu découle du climat et du stress hydrique.
# C'est le SEUL couple qui change réellement la solution technique, donc les
# lots 05, 06 et 07 — et le PUE, donc l'électricité pendant vingt ans.
REFROIDISSEMENT = {
    "free_cooling": {
        "nom": "Free cooling à air, appoint mécanique",
        "coef": {"05": 0.85, "06": 0.95, "07": 0.45},
        "pue": [1.10, 1.25], "eau": "faible",
        "sens": "climat froid et eau non contrainte : la solution la moins chère "
                "à l'investissement comme à l'exploitation",
    },
    "adiabatique": {
        "nom": "Adiabatique / évaporatif",
        "coef": {"05": 1.00, "06": 1.00, "07": 1.30},
        "pue": [1.20, 1.45], "eau": "forte",
        "sens": "climat tempéré et eau disponible : bon PUE, mais consommation "
                "d'eau réelle et compétition d'usage l'été",
    },
    "sec": {
        "nom": "Aéroréfrigérants secs, sans eau",
        "coef": {"05": 1.30, "06": 1.05, "07": 0.25},
        "pue": [1.25, 1.50], "eau": "nulle sur site",
        "sens": "eau contrainte : zéro eau SUR SITE, davantage d'électricité — "
                "donc davantage d'eau À LA SOURCE sur un réseau thermique",
    },
    "liquide": {
        "nom": "Refroidissement liquide direct (densité IA)",
        "coef": {"05": 1.20, "06": 0.70, "07": 0.90},
        "pue": [1.08, 1.20], "eau": "modérée",
        "sens": "au-delà d'environ 40 kW par baie, l'air ne suffit plus : "
                "le liquide devient une contrainte, pas une option",
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# CRITÈRES DE CONCEPTION — repris du référentiel d'ingénierie CONSEILPREV
#
# Source : `datacenter.py` de conseilprevcyber, version 2026-08-a, qui cite
# lui-même ASHRAE TC 9.9, la directive (UE) 2023/1791 et son règlement délégué
# (UE) 2024/1364, le Climate Neutral Data Centre Pact et ISO/IEC 30134.
#
# Ces critères ne changent pas le PRIX AU MÉGAWATT — rien ici ne le permet.
# Ils changent ce qui se passe APRÈS : le PUE, donc l'électricité, donc le coût
# total sur dix ans, c'est-à-dire le seul chiffre qui départage deux pays.
# ═══════════════════════════════════════════════════════════════════════════

# Classe d'air admise à l'entrée des équipements. Élargir la plage est le levier
# le moins cher qui existe — il ne coûte aucun matériel — mais il engage la
# garantie constructeur, ce qui doit être écrit noir sur blanc dans l'offre.
#
# Le référentiel d'ingénierie donne les PLAGES, pas un coefficient de PUE :
# le gain dépend du climat heure par heure et ne se déduit pas d'une capitale.
# La classe POSITIONNE donc le PUE dans la bande de la famille retenue, au lieu
# de le recalculer — et cette position est déclarée `hypothese`, pas `calcule`.
CLASSES_ASHRAE = {
    "A1": {"nom": "A1 — 15 à 32 °C", "plage_c": [15, 32], "position": 1.00,
           "sens": "serveurs d'entreprise et stockage : la classe la plus contrainte, "
                   "donc le moins d'heures de free cooling"},
    "A2": {"nom": "A2 — 10 à 35 °C", "plage_c": [10, 35], "position": 0.75,
           "sens": "serveurs de volume, plage courante — le défaut du marché"},
    "A3": {"nom": "A3 — 5 à 40 °C", "plage_c": [5, 40], "position": 0.45,
           "sens": "autorise beaucoup plus de free cooling ; vérifier la qualification "
                   "du matériel retenu"},
    "A4": {"nom": "A4 — 5 à 45 °C", "plage_c": [5, 45], "position": 0.20,
           "sens": "maximise le free cooling ; impose du matériel qualifié et engage "
                   "la garantie constructeur"},
}
ASHRAE_SOURCE = {
    "titre": "ASHRAE TC 9.9, Thermal Guidelines for Data Processing Environments",
    "nature": "referentiel",
    "note": "Les plages sont normatives. Le POSITIONNEMENT du PUE dans la bande de "
            "la famille est une hypothèse de cadrage : le gain réel dépend du profil "
            "horaire de température du site, qu'aucune moyenne nationale ne remplace.",
}

# Taux de charge moyen. L'électricité se calcule dessus : c'est, avec le PUE, ce
# qui commande l'exploitation. Le référentiel d'ingénierie retient 0,65 par
# défaut ; ce module conserve 0,70 pour ne pas réécrire en silence des résultats
# déjà cités, et l'écart est dit ici plutôt que masqué.
CHARGE = {
    "defaut": 0.70,
    "defaut_ingenierie": 0.65,
    "bornes": [0.30, 1.00],
    "nature": "hypothese",
    "sens": "charge réelle moyenne rapportée à la puissance installée",
    "alerte_sous": 0.55,
    "note_alerte": "Sous 0,55, la pénalité de charge partielle des chaînes électriques "
                   "et frigorifiques devient le premier poste de perte : un site "
                   "surdimensionné coûte cher avant même d'être utile.",
}

# Cibles de marché. Volontaires, non réglementaires — mais un dossier qui s'en
# écarte doit le justifier, et un évaluateur technique le demandera.
CIBLES_MARCHE = {
    "titre": "Climate Neutral Data Centre Pact (engagement sectoriel volontaire)",
    "nature": "referentiel",
    "pue_climat_froid": 1.30,
    "pue_climat_tempere_chaud": 1.40,
    "wue_site_max": 0.40,
    "note": "Engagement volontaire, pas une obligation. Il sert de repère : "
            "l'écart se justifie, il ne s'ignore pas.",
}

# Carbone incorporé, amorti sur la durée de vie. Sans cet amortissement, la
# comparaison avec l'exploitation n'a aucun sens — et sans cette ligne, un
# dossier CSRD est incomplet dès sa première page.
INCORPORE = {
    "batiment": {"nom": "Bâtiment (gros œuvre et second œuvre)",
                 "kgco2e_par_kw_it": 2500, "duree_vie_ans": 25},
    "technique": {"nom": "Lots techniques (froid, onduleurs, batteries, groupes)",
                  "kgco2e_par_kw_it": 1400, "duree_vie_ans": 15},
}
INCORPORE_SOURCE = {
    "nature": "hypothese",
    "note": "Ordres de grandeur issus des analyses de cycle de vie publiées du "
            "secteur, repris du référentiel d'ingénierie CONSEILPREV. À REMPLACER "
            "par les déclarations environnementales (FDES / EPD) des équipements "
            "réellement retenus : l'écart entre un ordre de grandeur et une EPD "
            "peut atteindre un facteur deux. Les serveurs sont EXCLUS — ils "
            "relèvent de l'exploitant, pas du constructeur du bâtiment.",
}

# Tension sur le raccordement : elle ne change pas le prix du poste source, elle
# change le DÉLAI, donc la provision d'aléas et le coût de portage.
TENSION_RACCORDEMENT = {
    "saturee":  {"nom": "File saturée", "coef_03": 1.35, "coef_13": 1.40,
                 "mois_sup": [12, 30],
                 "sens": "moratoire ou file d'attente déclarée par le gestionnaire de réseau"},
    "tendue":   {"nom": "File tendue", "coef_03": 1.15, "coef_13": 1.15,
                 "mois_sup": [6, 18],
                 "sens": "densité de projets élevée au regard du parc en service"},
    "ouverte":  {"nom": "File ouverte", "coef_03": 1.00, "coef_13": 1.00,
                 "mois_sup": [0, 6],
                 "sens": "peu de concurrence constatée sur le raccordement"},
}

# Ce que le référentiel NE PEUT PAS trancher. Affiché, jamais estimé.
A_RENSEIGNER = [
    {"cle": "foncier", "lot": "01", "nom": "Prix du foncier viabilisé",
     "pourquoi": "il dépend de la parcelle, pas du pays ; aucune statistique nationale "
                 "ne prédit le prix d'un terrain de 20 hectares près d'un poste source"},
    {"cle": "travail", "lot": "02", "nom": "Coût local de la main-d'œuvre et de la construction",
     "pourquoi": "les indices de niveau de prix de la construction existent chez Eurostat, "
                 "mais ne sont pas repris dans ce référentiel : les inventer serait pire "
                 "que les laisser vides"},
    {"cle": "quotepart", "lot": "03", "nom": "Quote-part de renforcement du réseau",
     "pourquoi": "elle est fixée par le gestionnaire de réseau au cas par cas et n'est "
                 "connue qu'après étude détaillée"},
    {"cle": "fiscalite", "lot": None, "nom": "Fiscalité, aides et régimes locaux",
     "pourquoi": "crédits d'impôt, exonérations de taxe foncière et tarifs d'accès au "
                 "réseau varient par région et par convention"},
    {"cle": "energie_contrat", "lot": None, "nom": "Prix contractuel de l'électricité",
     "pourquoi": "un PPA ou un contrat d'approvisionnement est un contrat privé ; la "
                 "statistique Eurostat donne des bandes, pas votre prix",
     "question": "Quel prix votre PPA ou votre contrat d'approvisionnement retient-il, "
                 "et sur quelle durée ?"},
    # La redondance est le PREMIER multiplicateur de coût des lots 04 et 05 —
    # doubler une chaîne électrique se voit dans l'enveloppe avant tout le
    # reste. Aucune des sources de ce référentiel ne la chiffre. Elle est donc
    # affichée VIDE, comme les autres : un coefficient plausible mais inventé
    # serait plus dangereux qu'une case blanche, parce qu'il serait cru.
    {"cle": "redondance", "lot": "04", "nom": "Niveau de redondance électrique et frigorifique",
     "pourquoi": "passer de N+1 à 2N double des chaînes entières sur les lots 04 et 05 ; "
                 "aucune source de ce référentiel ne donne le coefficient correspondant, "
                 "et il dépend autant de la topologie retenue que du niveau affiché",
     "question": "Quel niveau de disponibilité le contrat de service impose-t-il, et "
                 "quelle topologie l'atteint — N+1, N+2, 2N, 2(N+1) ?"},
]

# ═══════════════════════════════════════════════════════════════════════════
# 5. EXPLOITATION — les postes annuels
# ═══════════════════════════════════════════════════════════════════════════
OPEX = {
    "maintenance": {"nom": "Maintenance et MCO", "part_capex_an": [0.020, 0.040],
                    "nature": "hypothese",
                    "sens": "contrats de maintenance des lots techniques, pièces, essais périodiques"},
    "personnel":   {"nom": "Exploitation et personnel", "keur_mw_an": [18, 45],
                    "nature": "hypothese",
                    "sens": "astreinte 24/7, sûreté, encadrement — fortement dépendant du pays"},
    "assurance":   {"nom": "Assurances et taxes locales", "part_capex_an": [0.004, 0.010],
                    "nature": "hypothese", "sens": "dommages aux biens, pertes d'exploitation, foncier"},
}
EAU_PRIX_EUR_M3 = [1.5, 4.5]   # hypothèse, fourchette large, industriel européen
CO2_EUR_T = [60, 110]          # hypothèse : ordre de grandeur du quota européen, très volatil


# ═══════════════════════════════════════════════════════════════════════════
# 6. LE MOTEUR
# ═══════════════════════════════════════════════════════════════════════════
def _f(x, n=1):
    """Arrondi lisible. Les fourchettes larges ne méritent pas trois décimales."""
    return round(float(x), n)


def _fourchette(a, b, n=1):
    return [_f(min(a, b), n), _f(max(a, b), n)]


def _fr(x):
    """Séparateur décimal français DANS LES PHRASES composées.

    Les nombres renvoyés en JSON restent des nombres — c'est la page qui les
    met en forme. Mais les formules et la trace sont du TEXTE écrit ici : sans
    cette conversion, « 4.0 % de l'enveloppe » se lit à côté de « 879,3 M€ »,
    et sur une page de décision financière la faute se voit."""
    return str(x).replace('.', ',')


def pue_de(mode, classe_ashrae=None, pue_impose=None):
    """Le PUE retenu, et d'où il vient.

    Trois provenances possibles, dans cet ordre de priorité :
      1. le CAHIER DES CHARGES, s'il en impose un — c'est une contrainte, pas
         une estimation, et elle prime sur toute déduction ;
      2. la CLASSE D'AIR ADMISE, qui positionne le PUE dans la bande de la
         famille : élargir la plage augmente les heures de free cooling ;
      3. la bande de la famille, telle quelle, si rien n'est précisé.

    La position dans la bande est une HYPOTHÈSE de cadrage, jamais un calcul :
    le gain réel d'une classe ASHRAE dépend du profil horaire de température du
    site, qu'aucune moyenne nationale ne remplace."""
    bande = list(REFROIDISSEMENT[mode]["pue"])
    if pue_impose:
        v = _f(max(1.02, min(2.5, float(pue_impose))), 2)
        return [v, v], "saisi", ("PUE imposé par le cahier des charges : %s. La bande de "
                                 "la famille (%s à %s) n'est pas retenue."
                                 % (_fr(v), _fr(bande[0]), _fr(bande[1])))
    A = CLASSES_ASHRAE.get(classe_ashrae or "")
    if not A:
        return bande, "hypothese", ("Bande de la famille retenue, sans classe d'air "
                                    "précisée : %s à %s" % (_fr(bande[0]), _fr(bande[1])))
    # La position 1,00 laisse la bande entière (classe la plus contrainte) ;
    # la position 0,00 la ramène sur sa borne basse (classe la plus permissive).
    haut = _f(bande[0] + (bande[1] - bande[0]) * A["position"], 3)
    return ([bande[0], max(bande[0], haut)], "hypothese",
            "Classe %s (%s à %s °C) : la borne haute du PUE passe de %s à %s — "
            "élargir la plage d'air admise achète des heures de free cooling, sans "
            "matériel, mais engage la garantie constructeur."
            % (classe_ashrae, A["plage_c"][0], A["plage_c"][1],
               _fr(bande[1]), _fr(max(bande[0], haut))))


def refroidissement_retenu(climat_classe, eau_classe, densite_ia=False, impose=None):
    """Le mode de refroidissement DÉCOULE du climat et de l'eau — sauf si le
    lecteur en IMPOSE un. C'est le seul endroit où le pays change la solution
    technique elle-même, et donc les lots 05, 06, 07 ainsi que le PUE,
    c'est-à-dire l'électricité sur vingt ans. Un investisseur qui a déjà une
    esquisse doit pouvoir dire ce qu'il sait au lieu de le laisser déduire."""
    if impose and impose in REFROIDISSEMENT:
        return impose
    if densite_ia:
        return "liquide"
    if eau_classe == "eleve":
        return "sec"
    if climat_classe == "nordique":
        return "free_cooling"
    if climat_classe == "meridional":
        return "sec" if eau_classe != "faible" else "adiabatique"
    return "adiabatique"


def tension_de(parc_mw_ou_sites, pipeline):
    """Tension du raccordement, comptée depuis NOS statuts : rapport entre les
    projets en cours (construction + autorisé + annoncé) et le parc en service.
    Un pays qui prépare autant de sites qu'il en exploite déjà sature sa file."""
    parc = max(1, int(parc_mw_ou_sites or 0))
    pip = int(pipeline or 0)
    ratio = pip / parc
    if ratio >= 0.60:
        return "saturee", _f(ratio, 2)
    if ratio >= 0.25:
        return "tendue", _f(ratio, 2)
    return "ouverte", _f(ratio, 2)


def dpgf(mw, gabarit="hyperscale", scenario="neuve", pays=None,
         climat_classe=None, eau_classe=None, densite_ia=False,
         parc_sites=0, pipeline_sites=0, cout_mw=None, vitesse="aucune",
         refroidissement=None, classe_ashrae=None, pue_impose=None):
    """Enveloppe et DPGF pour une puissance IT donnée, dans un pays donné.

    Retourne l'enveloppe en fourchette, la décomposition par lot, les postes
    non chiffrables, et la trace complète du calcul. Aucune valeur n'est
    donnée sans sa nature."""
    mw = max(0.1, float(mw or 0))
    g = COUT_MW.get(gabarit) or COUT_MW["hyperscale"]
    sc = SCENARIOS.get(scenario) or SCENARIOS["neuve"]
    base = list(cout_mw) if cout_mw else list(g["meur_mw"])
    V = PRIME_VITESSE.get(vitesse) or PRIME_VITESSE["aucune"]
    if V["coef"] != 1.0:
        base = [base[0] * V["coef"], base[1] * V["coef"]]

    mode = refroidissement_retenu(climat_classe, eau_classe, densite_ia, refroidissement)
    R = REFROIDISSEMENT[mode]
    pue, pue_nature, pue_note = pue_de(mode, classe_ashrae, pue_impose)
    ten_cle, ten_ratio = tension_de(parc_sites, pipeline_sites)
    T = TENSION_RACCORDEMENT[ten_cle]

    trace = [
        "Coût unitaire retenu : %s à %s M€/MW (%s) — %s"
        % (_fr(_f(base[0], 2)), _fr(_f(base[1], 2)), g["nom"],
           "valeur saisie" if cout_mw else
           ("%s M$/MW convertis au taux %s · source : %s"
            % ('-'.join(_fr(x) for x in g["musd_mw"]), _fr(EUR_USD), g["source"]))),
        "Scénario : %s" % sc["nom"],
        "Calendrier : %s%s" % (V["nom"],
            ("" if V["coef"] == 1.0 else
             " — surcoût de %s %% appliqué à l'enveloppe, %s mois gagnés au mieux"
             % (_fr(_f((V["coef"] - 1) * 100, 0)), abs(V["mois"])))),
        ("Refroidissement IMPOSÉ : %s — le climat (%s) et l'eau (%s) auraient conduit à %s"
         % (R["nom"], climat_classe or "inconnu", eau_classe or "inconnu",
            REFROIDISSEMENT[refroidissement_retenu(climat_classe, eau_classe, densite_ia)]["nom"])
         ) if refroidissement in REFROIDISSEMENT else
        ("Refroidissement déduit du climat (%s) et de l'eau (%s) : %s"
         % (climat_classe or "inconnu", eau_classe or "inconnu", R["nom"])),
        "PUE retenu : %s à %s (%s) — %s" % (_fr(pue[0]), _fr(pue[1]), pue_nature, pue_note),
        "Raccordement : %s (%s projets pour %s sites en service, ratio %s)"
        % (T["nom"], pipeline_sites, parc_sites, _fr(ten_ratio)),
    ]

    lignes, sbas, shaut = [], 0.0, 0.0
    for L in LOTS:
        c = 1.0
        det = []
        if L["code"] in sc["coef"]:
            c *= sc["coef"][L["code"]]
            det.append("scénario ×%s" % sc["coef"][L["code"]])
        if L["module"] == "refroidissement" and L["code"] in R["coef"]:
            c *= R["coef"][L["code"]]
            det.append("%s ×%s" % (R["nom"], R["coef"][L["code"]]))
        if L["module"] == "eau" and L["code"] in R["coef"]:
            c *= R["coef"][L["code"]]
            det.append("%s ×%s" % (R["nom"], R["coef"][L["code"]]))
        if L["module"] == "raccordement":
            c *= T["coef_03"]
            det.append("%s ×%s" % (T["nom"], T["coef_03"]))
        if L["module"] == "delai":
            c *= T["coef_13"]
            det.append("%s ×%s" % (T["nom"], T["coef_13"]))
        pb, ph = L["part"][0] * c, L["part"][1] * c
        sbas += pb
        shaut += ph
        lignes.append({"code": L["code"], "nom": L["nom"], "recouvre": L["recouvre"],
                       "part_brute": _fourchette(pb, ph, 4), "coef": _f(c, 3),
                       "detail_coef": " · ".join(det) or "aucune modulation",
                       "arenseigner": L["arenseigner"], "question": L["question"]})

    # Normalisation. Deux pièges, tous deux vérifiés par le calcul :
    #
    #  1. les parts modulées ne somment plus à 1 — on le dit et on affiche le
    #     facteur, masquer une normalisation revient à masquer un calcul ;
    #  2. la PART d'un lot ne peut pas être donnée en fourchette normalisée.
    #     Normaliser la borne basse par la somme des basses et la haute par la
    #     somme des hautes rend la « borne haute » d'un lot peu étalé PLUS
    #     PETITE que sa borne basse — mesuré : le lot 00 sortait à [3,9 ; 4,0]
    #     alors que sa part haute vaut 3,92 % et sa part basse 4,04 %. Le
    #     pourcentage est donc UN SEUL nombre, calculé au milieu, et l'incertitude
    #     reste où elle a un sens : sur les montants.
    trace.append("Somme des parts modulées : %s à %s, normalisée pour reconstituer "
                 "l'enveloppe" % (_fr(_f(sbas, 3)), _fr(_f(shaut, 3))))
    trace.append("Les bornes basses ne surviennent pas toutes ensemble : leur somme "
                 "reconstitue la BORNE BASSE de l'enveloppe, pas un cas réel où tous "
                 "les lots seraient au plus bas.")
    ebas, ehaut = mw * base[0], mw * base[1]
    mid_env = (ebas + ehaut) / 2.0
    for lg in lignes:
        pb = lg["part_brute"][0] / sbas if sbas else 0
        ph = lg["part_brute"][1] / shaut if shaut else 0
        lg["meur"] = _fourchette(ebas * pb, ehaut * ph, 1)
        mid_lot = (lg["meur"][0] + lg["meur"][1]) / 2.0
        lg["part"] = _f(mid_lot / mid_env * 100 if mid_env else 0, 1)   # % du milieu

    return {
        "version": VERSION,
        "avertissement": AVERTISSEMENT,
        "entree": {"mw": _f(mw, 1), "gabarit": gabarit, "gabarit_nom": g["nom"],
                   "scenario": scenario, "scenario_nom": sc["nom"], "pays": pays,
                   "densite_ia": bool(densite_ia)},
        "cout_mw": {"valeur": _fourchette(base[0], base[1], 2),
                    "musd_mw": None if cout_mw else g["musd_mw"],
                    "taux_eur_usd": None if cout_mw else EUR_USD,
                    "nature": "saisi" if cout_mw else g["nature"],
                    "source": "valeur saisie" if cout_mw else g["source"],
                    "citation": None if cout_mw else g.get("citation")},
        "vitesse": {"cle": vitesse, "nom": V["nom"], "coef": V["coef"],
                    "mois_gagnes": abs(V["mois"]),
                    "nature": V.get("nature", "analyse"),
                    "source": V.get("source"), "sens": V["sens"]},
        "refroidissement": {"cle": mode, "nom": R["nom"], "pue": pue,
                            "pue_famille": R["pue"], "pue_nature": pue_nature,
                            "pue_note": pue_note,
                            "impose": bool(refroidissement in REFROIDISSEMENT),
                            "classe_ashrae": classe_ashrae or None,
                            "eau": R["eau"], "sens": R["sens"],
                            "nature": "saisi" if refroidissement in REFROIDISSEMENT else "calcule"},
        "raccordement": {"cle": ten_cle, "nom": T["nom"], "ratio": ten_ratio,
                         "mois_sup": T["mois_sup"], "sens": T["sens"], "nature": "calcule"},
        "enveloppe_meur": _fourchette(ebas, ehaut, 1),
        "lots": lignes,
        "arenseigner": A_RENSEIGNER,
        # La prime raccourcit le CHANTIER, jamais l'instruction du raccordement :
        # aucun surcoût accepté par un maître d'ouvrage n'accélère un gestionnaire
        # de réseau. Le gain est donc plafonné par la part compressible.
        "duree_mois": [max(6, sc["duree_mois"][0] + V["mois"]) + T["mois_sup"][0],
                       max(12, sc["duree_mois"][1] + V["mois"]) + T["mois_sup"][1]],
        "trace": trace,
    }


def exploitation(env_meur, mw, pue, prix_mwh, intensite_g_kwh=None,
                 wue_m3_mwh=None, charge=None, prix_contrat=None,
                 intensite_contrat=None, part_sans_carbone=0.0):
    """Postes annuels d'exploitation. L'électricité est calculée, pas supposée :
    elle sort de la puissance, du facteur de charge, du PUE et du prix.

    Trois entrées facultatives remplacent une statistique par VOTRE donnée, et
    la nature du poste change en conséquence :

      `prix_contrat`       — le prix de votre PPA remplace la bande Eurostat.
                             C'était l'un des cinq postes affichés vides ; il
                             cesse de l'être dès qu'il est renseigné.
      `intensite_contrat`  — l'intensité de votre fourniture remplace la
                             moyenne nationale (approche « market-based »,
                             GHG Protocol Scope 2 Guidance).
      `part_sans_carbone`  — la part d'énergie sans carbone contractualisée
                             (REF au sens d'EN 50600-4-3 et ISO 30134-3).

    Une donnée saisie n'est pas une donnée vérifiée : elle est marquée `saisi`,
    ce qui dit au lecteur du dossier que c'est VOUS qui l'engagez."""
    mw = max(0.1, float(mw or 0))
    charge = CHARGE["defaut"] if charge is None else float(charge)
    charge = min(CHARGE["bornes"][1], max(CHARGE["bornes"][0], charge))
    prix_source = "bande de prix industriels du pays"
    if prix_contrat:
        p = _f(max(1.0, min(600.0, float(prix_contrat))), 1)
        prix_mwh = [p, p]
        prix_source = "prix contractuel saisi"
    mwh = [mw * charge * 8760 * pue[0], mw * charge * 8760 * pue[1]]
    elec = [mwh[0] * prix_mwh[0] / 1e6, mwh[1] * prix_mwh[1] / 1e6]   # M€
    cb, ch = env_meur[0], env_meur[1]
    maint = [cb * OPEX["maintenance"]["part_capex_an"][0],
             ch * OPEX["maintenance"]["part_capex_an"][1]]
    perso = [mw * OPEX["personnel"]["keur_mw_an"][0] / 1000.0,
             mw * OPEX["personnel"]["keur_mw_an"][1] / 1000.0]
    assur = [cb * OPEX["assurance"]["part_capex_an"][0],
             ch * OPEX["assurance"]["part_capex_an"][1]]
    postes = [
        {"cle": "electricite", "nom": "Électricité", "meur_an": _fourchette(elec[0], elec[1], 2),
         "nature": "saisi" if prix_contrat else "calcule",
         "formule": "MWh = %s MW × %s × 8 760 h × PUE %s-%s → %s à %s MWh/an, "
                    "puis × prix %s-%s €/MWh (%s)"
                    % (_fr(_f(mw, 1)), _fr(charge), _fr(pue[0]), _fr(pue[1]),
                       _fr(_f(mwh[0] / 1000, 0) * 1000), _fr(_f(mwh[1] / 1000, 0) * 1000),
                       _fr(prix_mwh[0]), _fr(prix_mwh[1]), prix_source)},
        {"cle": "maintenance", "nom": OPEX["maintenance"]["nom"],
         "meur_an": _fourchette(maint[0], maint[1], 2), "nature": "hypothese",
         "formule": "%s à %s %% de l'enveloppe par an"
                    % (_fr(_f(OPEX["maintenance"]["part_capex_an"][0] * 100, 1)),
                       _fr(_f(OPEX["maintenance"]["part_capex_an"][1] * 100, 1)))},
        {"cle": "personnel", "nom": OPEX["personnel"]["nom"],
         "meur_an": _fourchette(perso[0], perso[1], 2), "nature": "hypothese",
         "formule": "%s à %s k€ par MW et par an" % tuple(OPEX["personnel"]["keur_mw_an"])},
        {"cle": "assurance", "nom": OPEX["assurance"]["nom"],
         "meur_an": _fourchette(assur[0], assur[1], 2), "nature": "hypothese",
         "formule": "%s à %s %% de l'enveloppe par an"
                    % (_fr(_f(OPEX["assurance"]["part_capex_an"][0] * 100, 1)),
                       _fr(_f(OPEX["assurance"]["part_capex_an"][1] * 100, 1)))},
    ]
    if wue_m3_mwh:
        eau = [mwh[0] * wue_m3_mwh[0] * EAU_PRIX_EUR_M3[0] / 1e6,
               mwh[1] * wue_m3_mwh[1] * EAU_PRIX_EUR_M3[1] / 1e6]
        postes.append({"cle": "eau", "nom": "Eau de refroidissement",
                       "meur_an": _fourchette(eau[0], eau[1], 2), "nature": "hypothese",
                       "formule": "MWh × WUE %s-%s m³/MWh × %s-%s €/m³"
                                  % (_fr(wue_m3_mwh[0]), _fr(wue_m3_mwh[1]),
                                     _fr(EAU_PRIX_EUR_M3[0]), _fr(EAU_PRIX_EUR_M3[1]))})
    carbone = None
    # L'intensité CONTRACTUELLE prime sur la moyenne nationale : c'est
    # l'approche « market-based » du GHG Protocol, celle qu'un auditeur CSRD
    # attend. La moyenne nationale reste affichée pour que l'écart se voie.
    inten = float(intensite_contrat) if intensite_contrat else intensite_g_kwh
    ref = max(0.0, min(1.0, float(part_sans_carbone or 0.0)))
    if inten:
        eff = inten * (1.0 - ref)
        t = [mwh[0] * eff / 1000.0, mwh[1] * eff / 1000.0]
        carbone = {"t_co2e_an": _fourchette(t[0], t[1], 0),
                   "cout_meur_an": _fourchette(t[0] * CO2_EUR_T[0] / 1e6,
                                               t[1] * CO2_EUR_T[1] / 1e6, 2),
                   "intensite_retenue_g": _f(eff, 1),
                   "intensite_reseau_g": intensite_g_kwh,
                   "part_sans_carbone": ref,
                   "nature": "saisi" if (intensite_contrat or ref) else "calcule",
                   "formule": "MWh × %s gCO₂e/kWh%s%s, valorisé %s à %s €/t — le prix "
                              "du quota est une hypothèse très volatile"
                              % (_fr(_f(inten, 1)),
                                 " (fourniture contractuelle, approche market-based)"
                                 if intensite_contrat
                                 else " (moyenne nationale, Ember 2024, cycle de vie)",
                                 " × (1 − %s de part sans carbone contractualisée)"
                                 % _fr(ref) if ref else "",
                                 CO2_EUR_T[0], CO2_EUR_T[1])}
    tot = [sum(p["meur_an"][0] for p in postes), sum(p["meur_an"][1] for p in postes)]
    alerte = (CHARGE["note_alerte"] if charge < CHARGE["alerte_sous"] else None)
    return {"postes": postes, "total_meur_an": _fourchette(tot[0], tot[1], 2),
            "carbone": carbone, "charge": charge,
            "charge_alerte": alerte, "prix_source": prix_source,
            "prix_mwh": list(prix_mwh)}


def carbone_incorpore(mw, annees=None):
    """Le carbone de la CONSTRUCTION, amorti sur la durée de vie de chaque lot.

    Sans cet amortissement, la comparaison avec l'exploitation n'a aucun sens —
    et sans cette ligne, un dossier CSRD est incomplet dès sa première page.
    Les serveurs sont volontairement EXCLUS : ils relèvent de l'exploitant et de
    son cycle de renouvellement, pas du constructeur du bâtiment."""
    mw = max(0.1, float(mw or 0))
    kw = mw * 1000.0
    postes, total_t, total_t_an = [], 0.0, 0.0
    for cle, I in INCORPORE.items():
        t = kw * I["kgco2e_par_kw_it"] / 1000.0
        t_an = t / I["duree_vie_ans"]
        total_t += t
        total_t_an += t_an
        postes.append({"cle": cle, "nom": I["nom"],
                       "t_co2e": _f(t, 0), "duree_vie_ans": I["duree_vie_ans"],
                       "t_co2e_an": _f(t_an, 0), "nature": "hypothese",
                       "formule": "%s kW IT × %s kgCO₂e/kW ÷ %s ans"
                                  % (_fr(_f(kw, 0)), I["kgco2e_par_kw_it"],
                                     I["duree_vie_ans"])})
    return {"postes": postes, "total_t_co2e": _f(total_t, 0),
            "total_t_co2e_an": _f(total_t_an, 0), "nature": "hypothese",
            "source": INCORPORE_SOURCE["note"],
            "note": "Amorti par lot sur sa propre durée de vie : le bâtiment sur "
                    "25 ans, les lots techniques sur 15. Un carbone incorporé non "
                    "amorti ne se compare à rien."}


def conformite_marche(pue, wue_m3_mwh=None, climat_classe=None):
    """Confrontation aux cibles du Climate Neutral Data Centre Pact.

    Engagement volontaire, pas une obligation : le verdict n'est donc pas
    « conforme / non conforme » mais « dans la cible / à justifier ». Un dossier
    qui s'écarte du repère de marché doit l'expliquer, il ne peut pas l'ignorer."""
    froid = climat_classe in ("nordique", "continental")
    cible_pue = (CIBLES_MARCHE["pue_climat_froid"] if froid
                 else CIBLES_MARCHE["pue_climat_tempere_chaud"])
    haut = pue[1]
    out = [{"cle": "pue", "nom": "PUE annuel",
            "cible": cible_pue, "valeur": _f(haut, 3),
            "cible_nom": "climat froid" if froid else "climat tempéré ou chaud",
            "verdict": "dans la cible" if haut <= cible_pue else "à justifier",
            "sens": "Le PUE retenu est comparé à la borne haute : c'est elle qui "
                    "engage, pas la borne basse."}]
    if wue_m3_mwh:
        out.append({"cle": "wue", "nom": "WUE site (m³/MWh IT)",
                    "cible": CIBLES_MARCHE["wue_site_max"],
                    "valeur": _f(wue_m3_mwh[1], 2),
                    "verdict": ("dans la cible" if wue_m3_mwh[1] <= CIBLES_MARCHE["wue_site_max"]
                                else "à justifier"),
                    "sens": "Le WUE annuel masque les pointes estivales, qui sont "
                            "précisément le moment où la ressource est tendue."})
    return {"reperes": out, "source": CIBLES_MARCHE["titre"],
            "nature": CIBLES_MARCHE["nature"], "note": CIBLES_MARCHE["note"]}


def tco(env_meur, opex_an_meur, annees=10):
    """Coût total de possession, sans actualisation — volontairement.
    Un taux d'actualisation est une décision d'investisseur, pas une donnée de
    référentiel : l'appliquer ici reviendrait à choisir à sa place."""
    return {"annees": annees,
            "capex_meur": list(env_meur),
            "opex_cumule_meur": _fourchette(opex_an_meur[0] * annees,
                                            opex_an_meur[1] * annees, 1),
            "total_meur": _fourchette(env_meur[0] + opex_an_meur[0] * annees,
                                      env_meur[1] + opex_an_meur[1] * annees, 1),
            "nature": "calcule",
            "note": "Sans actualisation ni valeur terminale : le taux est votre "
                    "décision, pas une donnée du référentiel."}


def ecart(a, b, expl_a=None, expl_b=None, tco_a=None, tco_b=None):
    """Gap analysis entre deux pays.

    UN POINT QUI DÉCIDE DE L'UTILITÉ DE CE COMPARATEUR, et qu'il faut dire au
    lecteur avant qu'il ne le découvre : à puissance et gabarit identiques,
    l'ENVELOPPE D'INVESTISSEMENT est la même dans les deux pays. Ce n'est pas
    un défaut du calcul, c'est un refus assumé — le coût unitaire au mégawatt
    n'est modulé par aucun indice national, parce que ce référentiel n'en porte
    aucun et qu'en inventer un serait pire que de s'en passer.

    Ce qui diffère réellement, et que le référentiel PEUT justifier :
      — la COMPOSITION de l'enveloppe (le froid, l'eau, le raccordement) ;
      — l'EXPLOITATION, où le prix de l'électricité et le PUE se multiplient
        pendant vingt ans ;
      — le DÉLAI, donc le coût de portage ;
      — le CARBONE, donc l'exposition CSRD.
    C'est pourquoi la comparaison porte sur le coût total de possession, et non
    sur le seul investissement : sur le seul CAPEX, elle afficherait zéro."""
    ia = {l["code"]: l for l in a["lots"]}
    ib = {l["code"]: l for l in b["lots"]}
    postes = []
    for L in LOTS:
        c = L["code"]
        la, lb = ia.get(c), ib.get(c)
        if not la or not lb:
            continue
        mid_a = (la["meur"][0] + la["meur"][1]) / 2
        mid_b = (lb["meur"][0] + lb["meur"][1]) / 2
        d = mid_b - mid_a
        justifie = la["coef"] != lb["coef"]
        postes.append({
            "code": c, "nom": L["nom"],
            "a_meur": la["meur"], "b_meur": lb["meur"],
            "ecart_meur": _f(d, 1),
            "ecart_pct": _f((d / mid_a * 100) if mid_a else 0, 1),
            "justifie": justifie,
            "raison": (lb["detail_coef"] if justifie else
                       ("poste non modulé — l'écart ne vient que de l'enveloppe globale"
                        if abs(d) > 0.05 else "aucun écart")),
            "arenseigner": L["arenseigner"],
        })
    ea, eb = a["enveloppe_meur"], b["enveloppe_meur"]
    ma, mb = (ea[0] + ea[1]) / 2, (eb[0] + eb[1]) / 2

    def mid(x):
        return (x[0] + x[1]) / 2.0 if x else None

    lignes_ex, ecart_opex = [], None
    if expl_a and expl_b:
        pa = {p["cle"]: p for p in expl_a["postes"]}
        pb2 = {p["cle"]: p for p in expl_b["postes"]}
        for cle in sorted(set(pa) | set(pb2)):
            x, y = pa.get(cle), pb2.get(cle)
            if not x or not y:
                continue
            d = mid(y["meur_an"]) - mid(x["meur_an"])
            lignes_ex.append({"cle": cle, "nom": x["nom"],
                              "a_meur_an": x["meur_an"], "b_meur_an": y["meur_an"],
                              "ecart_meur_an": _f(d, 2),
                              "ecart_pct": _f(d / mid(x["meur_an"]) * 100
                                              if mid(x["meur_an"]) else 0, 1),
                              "nature": x.get("nature")})
        oa, ob = mid(expl_a["total_meur_an"]), mid(expl_b["total_meur_an"])
        ecart_opex = {"a_meur_an": expl_a["total_meur_an"], "b_meur_an": expl_b["total_meur_an"],
                      "ecart_meur_an": _f(ob - oa, 2),
                      "ecart_pct": _f((ob - oa) / oa * 100 if oa else 0, 1)}

    ecart_tco = None
    if tco_a and tco_b:
        ta, tb = mid(tco_a["total_meur"]), mid(tco_b["total_meur"])
        ecart_tco = {"annees": tco_a.get("annees"),
                     "a_meur": tco_a["total_meur"], "b_meur": tco_b["total_meur"],
                     "ecart_meur": _f(tb - ta, 1),
                     "ecart_pct": _f((tb - ta) / ta * 100 if ta else 0, 1),
                     "avantage": (b["entree"]["pays"] if tb < ta else a["entree"]["pays"])}

    ecart_carbone = None
    if expl_a and expl_b and expl_a.get("carbone") and expl_b.get("carbone"):
        ca, cb2 = mid(expl_a["carbone"]["t_co2e_an"]), mid(expl_b["carbone"]["t_co2e_an"])
        ecart_carbone = {"a_t_an": expl_a["carbone"]["t_co2e_an"],
                         "b_t_an": expl_b["carbone"]["t_co2e_an"],
                         "ecart_t_an": _f(cb2 - ca, 0),
                         "ecart_pct": _f((cb2 - ca) / ca * 100 if ca else 0, 1)}

    da, db = a["duree_mois"], b["duree_mois"]
    return {
        "a": {"pays": a["entree"]["pays"], "enveloppe_meur": ea,
              "refroidissement": a["refroidissement"]["nom"],
              "raccordement": a["raccordement"]["nom"], "duree_mois": da},
        "b": {"pays": b["entree"]["pays"], "enveloppe_meur": eb,
              "refroidissement": b["refroidissement"]["nom"],
              "raccordement": b["raccordement"]["nom"], "duree_mois": db},
        "ecart_capex_meur": _f(mb - ma, 1),
        "ecart_capex_pct": _f((mb - ma) / ma * 100 if ma else 0, 1),
        "capex_identique": abs(mb - ma) < 0.05,
        "note_capex": ("À puissance et gabarit identiques, l'enveloppe est la MÊME : "
                       "aucun indice national de coût de construction n'est appliqué, "
                       "faute d'en avoir un dans ce référentiel. Ce qui départage les "
                       "pays se lit plus bas — composition, exploitation, délai, carbone."
                       if abs(mb - ma) < 0.05 else
                       "L'écart d'enveloppe vient des paramètres saisis, pas d'un indice "
                       "national de coût."),
        "postes": postes,
        "justifies": [p for p in postes if p["justifie"]],
        "arenseigner": [p for p in postes if p["arenseigner"]],
        "exploitation": lignes_ex,
        "ecart_opex": ecart_opex,
        "ecart_tco": ecart_tco,
        "ecart_carbone": ecart_carbone,
        "ecart_delai_mois": [db[0] - da[0], db[1] - da[1]],
        "note": "L'écart affiché ne couvre QUE ce que le référentiel peut justifier. "
                "Les postes marqués « à renseigner » — foncier, main-d'œuvre, "
                "quote-part de raccordement, fiscalité — peuvent renverser ce "
                "classement à eux seuls, et aucun d'eux n'est estimé ici.",
    }


def trajectoire(devis, depart_annee=None, perspectives=None):
    """Échéancier jusqu'en 2030, phasé, avec le décaissement par phase.
    Ancré sur la durée du scénario ET sur la tension du raccordement — c'est
    elle qui commande, pas le chantier."""
    an0 = int(depart_annee or 2026)
    d0, d1 = devis["duree_mois"]
    phases = [
        ("etudes", "Études, foncier et dossier d'autorisation", 0.18, [6, 12], ["00", "01"]),
        ("raccordement", "Instruction réseau et engagement du raccordement", 0.14, [6, 24], ["03"]),
        ("gros_oeuvre", "Gros œuvre et clos-couvert", 0.20, [8, 14], ["02"]),
        ("technique", "Lots techniques — énergie, froid, air, fluides", 0.36, [10, 18],
         ["04", "05", "06", "07", "08"]),
        ("finitions", "Sûreté, GTB, aménagement des salles", 0.08, [4, 8], ["09", "10", "11"]),
        ("essais", "Essais intégrés et mise en service", 0.04, [3, 6], ["12"]),
    ]
    env = devis["enveloppe_meur"]
    lots = {l["code"]: l for l in devis["lots"]}
    out, curseur_bas, curseur_haut = [], 0, 0
    for cle, nom, part, dur, codes in phases:
        deb_a = an0 + int(curseur_bas // 12)
        fin_a = an0 + int((curseur_haut + dur[1]) // 12)
        montant = _fourchette(env[0] * part, env[1] * part, 1)
        out.append({
            "cle": cle, "nom": nom,
            "lots": codes,
            "lots_noms": [lots[c]["nom"] for c in codes if c in lots],
            "duree_mois": dur,
            "debut": deb_a, "fin": min(2030, fin_a), "depasse_2030": fin_a > 2030,
            "part": _f(part * 100, 0),
            "meur": montant,
        })
        curseur_bas += dur[0]
        curseur_haut += dur[1]
    fin_bas = an0 + int(curseur_bas // 12)
    fin_haut = an0 + int(curseur_haut // 12)
    jalons = []
    if perspectives:
        for p in perspectives:
            if p.get("pays") in (devis["entree"].get("pays"), "UE"):
                jalons.append({"quoi": p.get("resume"), "source": p.get("source"),
                               "date": p.get("date"), "nature": "referentiel"})
    return {
        "depart": an0,
        "phases": out,
        "mise_en_service": [fin_bas, fin_haut],
        "tient_2030": fin_haut <= 2030,
        "duree_totale_mois": [d0, d1],
        "jalons_pays": jalons,
        "avis": ("Trajectoire compatible avec un horizon 2030." if fin_haut <= 2030 else
                 "La borne haute dépasse 2030 : soit vous engagez le raccordement "
                 "avant les études détaillées, soit vous découpez en tranches et "
                 "n'annoncez que la première."),
        "nature": "analyse",
    }


def referentiel():
    """Tout ce que le module expose, pour la page et pour la vérification."""
    return {
        "version": VERSION,
        "avertissement": AVERTISSEMENT,
        "cout_mw": COUT_MW,
        "source_cout": SOURCE_COUT,
        "taux": SOURCE_TAUX,
        "vitesse": PRIME_VITESSE,
        "lots": LOTS,
        "source_lots": SOURCE_LOTS,
        "scenarios": SCENARIOS,
        "refroidissement": REFROIDISSEMENT,
        "tension": TENSION_RACCORDEMENT,
        "arenseigner": A_RENSEIGNER,
        "ashrae": CLASSES_ASHRAE,
        "source_ashrae": ASHRAE_SOURCE,
        "charge": CHARGE,
        "cibles_marche": CIBLES_MARCHE,
        "incorpore": INCORPORE,
        "source_incorpore": INCORPORE_SOURCE,
        "opex": OPEX,
        "hypotheses_prix": {"eau_eur_m3": EAU_PRIX_EUR_M3, "co2_eur_t": CO2_EUR_T},
    }


def sante():
    n = len(LOTS)
    sbas = sum(l["part"][0] for l in LOTS)
    shaut = sum(l["part"][1] for l in LOTS)
    return {"module": "finance_dc", "version": VERSION, "lots": n,
            "somme_parts_basses": _f(sbas, 3), "somme_parts_hautes": _f(shaut, 3),
            "scenarios": len(SCENARIOS), "modes_refroidissement": len(REFROIDISSEMENT),
            "postes_a_renseigner": len(A_RENSEIGNER),
            "classes_ashrae": len(CLASSES_ASHRAE),
            "postes_incorpore": len(INCORPORE),
            "horodatage": datetime.now(timezone.utc).isoformat(timespec="seconds")}
