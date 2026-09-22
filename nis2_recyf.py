# -*- coding: utf-8 -*-
"""LE RECYF — CE QUE LA FRANCE VA DEMANDER, ET QUI N'EST PAS ENCORE DU DROIT.

═══ POURQUOI CE MODULE EXISTE À CÔTÉ DE `nis2`, ET JAMAIS À SA PLACE ═════
`nis2` mesure la DIRECTIVE (UE) 2022/2555 : dix mesures à l'article 21 §2,
cinq points de gouvernance à l'article 20. Sa réserve dit déjà l'essentiel —
« une directive n'est pas d'application directe : ce qui oblige une entité,
c'est la loi de transposition ». Elle est exacte, et elle s'arrête là où le
client français a besoin qu'on continue.

CE QUE LA FRANCE PRÉPARE EST D'UNE AUTRE FORME. Le projet de loi relatif à
la résilience des infrastructures critiques et au renforcement de la
cybersécurité remplace, à son article 14, les dix mesures par QUATRE
familles — pilotage, protection, défense, résilience — et renvoie à un
référentiel : le ReCyF. Celui-ci compte VINGT objectifs de sécurité et cent
cinquante-deux moyens acceptables de conformité. Un contrôle de l'ANSSI
portera sur ceux-là, pas sur les dix de la directive.

═══ LA RÉSERVE QUI COMMANDE TOUT CE FICHIER ═════════════════════════════
AUCUN DE CES DEUX TEXTES N'EST EN VIGUEUR.

  · Le PJL est un PROJET DE LOI, présenté en conseil des ministres le
    15 octobre 2024. Il n'est pas voté.
  · Le ReCyF porte « DOCUMENT DE TRAVAIL » et « VERSION DE TRAVAIL » en
    toutes lettres. Version 2.5 du 17 mars 2026.
  · Le décret en Conseil d'État qui doit fixer les objectifs n'existe pas.

CE QUE CELA INTERDIT, ET C'EST LA DÉCISION D'ARCHITECTURE DE CE MODULE :
ce fichier ne produit JAMAIS un taux de conformité. Il produit un taux de
PRÉPARATION, qui ne se fond dans aucun autre. Noter une conformité contre un
document de travail serait un chiffre qui a l'air de mesurer autre chose que
ce qu'il mesure — précisément le défaut que ce dépôt traque partout ailleurs.

Le jour où le décret paraît, la réserve tombe et le taux change de nature.
C'est une décision qui se prend, pas un basculement automatique.

═══ CE QUE LE MODULE MESURE, ET À QUELLE MAILLE ═════════════════════════
IL MESURE PAR OBJECTIF, pas par moyen de conformité. Les moyens ne sont pas
d'application obligatoire : le référentiel le dit lui-même — ce sont des
moyens ACCEPTABLES, et une entité qui atteint l'objectif autrement est en
règle, à charge pour elle de le démontrer (article 15 du PJL). Un taux
calculé sur 152 cases laisserait croire qu'il faut les cocher toutes.

Le NOMBRE de moyens par objectif est porté ici parce qu'il dit le POIDS réel
de chacun — l'objectif 10 en compte dix-sept, l'objectif 1 en compte trois —
et parce qu'il est vérifiable dans le document.

═══ LA GRADATION EE / EI N'EST PAS COSMÉTIQUE ═══════════════════════════
C'est le changement le plus lourd. Dans la directive, être essentielle ou
importante change la SUPERVISION (ex ante ou ex post) et le PLAFOND de
l'amende — pas les mesures : les dix valent pour tout le monde. Le ReCyF
applique un principe de proportionnalité et réserve les objectifs 16 à 20
aux seules entités essentielles. Mesuré : 152 moyens pour une EE, 76 pour
une EI — exactement la moitié.

═══ DROITS ══════════════════════════════════════════════════════════════
Le PJL et le ReCyF sont des documents publics de l'administration française.
Les numéros et intitulés d'objectifs figurent ici dans leur libellé
d'origine : un intitulé reformulé ne se retrouve plus dans le référentiel
quand un auditeur demande où il est écrit. Ce qui est en français courant —
ce que l'objectif demande, en une phrase utilisable en comité — est le
travail du cabinet, pas une recopie. Le texte des 152 moyens n'est pas
reproduit.
"""

# ══════════════════════════════════════════════════════════════════════════
#  LE STATUT, ÉCRIT AVANT TOUT LE RESTE
# ══════════════════════════════════════════════════════════════════════════
#
# IL EST EN TÊTE PARCE QU'IL COMMANDE LA LECTURE DE CHAQUE CHIFFRE QUI SUIT.
# Un écran qui afficherait ces objectifs sans dire qu'ils sortent d'un projet
# de loi et d'un document de travail ferait passer une intention pour une
# obligation.

STATUT = {
    "en_vigueur": False,
    "dit": "Ni le projet de loi ni le ReCyF ne sont en vigueur. Aucune "
           "entité ne peut être sanctionnée aujourd'hui sur le fondement "
           "de ces objectifs.",
    "pourquoi_quand_meme": "Parce que c'est contre eux que le contrôle se "
                           "fera. Une entité qui attend la publication du "
                           "décret pour commencer découvrira alors qu'il "
                           "lui manque vingt objectifs, pas dix mesures.",
    "ce_qui_oblige_aujourdhui": "La directive (UE) 2022/2555, telle que "
                                "transposée — et à ce jour la France n'a "
                                "pas achevé sa transposition.",
    "ce_qui_manque": ("le vote de la loi",
                      "le décret en Conseil d'État qui fixe les objectifs",
                      "la publication du référentiel dans sa version finale"),
}

SOURCES = (
    {"cle": "pjl",
     "titre": "Projet de loi relatif à la résilience des infrastructures "
              "critiques et au renforcement de la cybersécurité "
              "(NOR : PRMD2412608L)",
     "date": "2024-10-15",
     "nature": "projet de loi — non voté",
     "droits": "Document public de l'administration française.",
     "lue": True,
     "apporte": "L'article 14, qui remplace les dix mesures de la directive "
                "par quatre familles et renvoie au référentiel ; l'article "
                "15, qui déplace la charge de la preuve ; l'article 13, qui "
                "écarte la loi devant un acte sectoriel équivalent.",
     "certifiable": False},
    {"cle": "recyf",
     "titre": "ReCyF — Référentiel Cyber France, version 2.5",
     "date": "2026-03-17",
     "nature": "DOCUMENT DE TRAVAIL — la mention figure sur chaque page",
     "droits": "Document public de l'administration française. Les 152 "
               "moyens de conformité ne sont pas reproduits ici.",
     "lue": True,
     "apporte": "Les vingt objectifs de sécurité, leur répartition en "
                "quatre piliers, le nombre de moyens de chacun, la "
                "réservation des objectifs 16 à 20 aux entités "
                "essentielles, et la table de correspondance avec les "
                "dispositions de la directive.",
     "certifiable": False},
    {"cle": "pratique",
     "titre": "ReCyF en pratique — collection de fiches ANSSI, version 1.0",
     "date": "2026-09",
     "nature": "collection en cours de publication",
     "droits": "Document public de l'administration française.",
     "lue": True,
     "apporte": "La seule fiche disponible à ce jour — architectures "
                "sécurisées, objectifs 7 et 8 — et la confirmation que la "
                "collection n'est ni prescriptive ni exhaustive.",
     "certifiable": False},
)


# ══════════════════════════════════════════════════════════════════════════
#  LES QUATRE FAMILLES DE L'ARTICLE 14 DU PROJET DE LOI
# ══════════════════════════════════════════════════════════════════════════
#
# ELLES NE SONT PAS UN RÉSUMÉ DES DIX MESURES : ce sont les obligations que
# la loi française énoncera, et les vingt objectifs s'y rattachent. Les
# citer permet à un client de retrouver, dans le texte de loi, la phrase qui
# fonde ce que Sentinel lui demande.

FAMILLES = (
    ("pilotage", "1°",
     "Mettre en place un pilotage de la sécurité des réseaux et systèmes "
     "d'information adaptée, comprenant notamment la formation à la "
     "cybersécurité des membres des organes de direction et des personnes "
     "exposées aux risques",
     "La formation ne vise pas que le comité de direction : les personnes "
     "EXPOSÉES au risque y sont nommées à égalité."),
    ("protection", "2°",
     "Assurer la protection des réseaux et systèmes d'information, y "
     "compris en cas de recours à la sous-traitance",
     "La sous-traitance est dans l'obligation, pas à côté : un prestataire "
     "qui exploite le système ne déplace pas la responsabilité."),
    ("defense", "3°",
     "Mettre en place des outils et des procédures pour assurer la défense "
     "des réseaux et systèmes d'information et gérer les incidents",
     "Des outils ET des procédures : une console sans personne pour la lire "
     "ne répond pas à cette famille."),
    ("resilience", "4°",
     "Garantir la résilience des activités",
     "L'obligation porte sur les ACTIVITÉS, pas sur les systèmes : "
     "continuer à servir, pas seulement redémarrer une machine."),
)

PILIERS = {
    "gouvernance": "Gouvernance",
    "protection": "Protection",
    "defense": "Défense",
    "resilience": "Résilience",
}


# ══════════════════════════════════════════════════════════════════════════
#  LES VINGT OBJECTIFS DE SÉCURITÉ
# ══════════════════════════════════════════════════════════════════════════
#
# Colonnes : numéro, intitulé d'origine, pilier, moyens attendus d'une EE,
# moyens attendus d'une EI, ce que l'objectif demande (travail du cabinet),
# et les dispositions de la directive auxquelles le référentiel le rattache.
#
# LES NOMBRES SONT COMPTÉS DANS LE DOCUMENT, pas estimés. La garde en bas de
# fichier les ré-additionne à chaque chargement : 152 pour une entité
# essentielle, 76 pour une entité importante.
#
# LA CORRESPONDANCE EST CELLE DU RÉFÉRENTIEL, pas la nôtre. Elle figure dans
# ses annexes, « communiquées uniquement à des fins pédagogiques » — ce qui
# est une réserve que nous portons aussi : elle situe, elle ne prouve pas.

OBJECTIFS = (
    (1, "Recensement des systèmes d'information", "gouvernance", 3, 3,
     "Lister toutes les activités et tous les services, avec un responsable "
     "nommé et les systèmes qui les portent — puis tenir cette liste à jour.",
     ("21.2.i",)),
    (2, "Mise en œuvre d'un cadre de gouvernance de la sécurité numérique",
     "gouvernance", 11, 10,
     "Faire porter la sécurité par le dirigeant exécutif, avec des rôles "
     "écrits, une politique, et de quoi vérifier qu'elle est suivie.",
     ("20", "21.2.a", "21.2.f", "21.2.h", "21.2.i")),
    (3, "Maîtrise de l'écosystème", "gouvernance", 4, 4,
     "Savoir de qui l'on dépend — fournisseurs, prestataires, filiales — et "
     "ce que chacun peut atteindre.",
     ("21.2.d", "21.2.i")),
    (4, "Intégration de la sécurité numérique dans la gestion des "
        "ressources humaines", "gouvernance", 5, 4,
     "Traiter l'arrivée, la mobilité et le départ comme des événements de "
     "sécurité, et former ceux qui sont exposés.",
     ("21.2.g",)),
    (5, "Maîtrise des systèmes d'information", "protection", 10, 8,
     "Connaître ses systèmes : inventaire, versions, correctifs, fin de "
     "support — ce qu'on ne sait pas décrire, on ne sait pas défendre.",
     ("21.2.e", "21.2.i")),
    (6, "Maîtrise des accès physiques aux locaux", "protection", 4, 2,
     "Le pilier physique de l'approche tous risques : qui entre où, et ce "
     "qu'un accès aux locaux permet d'atteindre.",
     ("21.2",)),
    (7, "Sécurisation de l'architecture des systèmes d'information",
     "protection", 13, 6,
     "Cloisonner, filtrer, réduire l'exposition — pour qu'une intrusion "
     "reste où elle est entrée.",
     ("21.2.e", "21.2.h")),
    (8, "Sécurisation des accès distants aux systèmes d'information",
     "protection", 5, 2,
     "Encadrer ce qui entre depuis l'extérieur, là où la sécurité physique "
     "du poste n'est plus garantie.",
     ("21.2.e", "21.2.h", "21.2.j")),
    (9, "Protection des systèmes d'information contre les codes "
        "malveillants", "protection", 7, 5,
     "Empêcher l'exécution de ce qui n'a pas été voulu, et le détecter "
     "quand l'empêchement a échoué.",
     ("21.2.e",)),
    (10, "Gestion des identités et des accès des utilisateurs aux systèmes "
         "d'information", "protection", 17, 16,
     "Qui a le droit de faire quoi, depuis quand, et jusqu'à quand — c'est "
     "l'objectif le plus lourd du référentiel.",
     ("21.2.e", "21.2.i", "21.2.j")),
    (11, "Maîtrise de l'administration des systèmes d'information",
     "protection", 14, 5,
     "Les comptes qui peuvent tout : les nommer, les limiter, les tracer. "
     "Neuf moyens de plus pour une entité essentielle que pour une "
     "importante — le plus grand écart du référentiel.",
     ("21.2.e", "21.2.i")),
    (12, "Identification et réaction aux incidents de sécurité", "defense",
     7, 2,
     "Détecter, qualifier, traiter — et savoir à quel moment l'horloge du "
     "signalement démarre.",
     ("21.2.b",)),
    (13, "Continuité et reprise d'activité", "resilience", 7, 4,
     "Sauvegardes éprouvées et reprise mesurée : ce qui permet de continuer "
     "à servir quand le système principal ne répond plus.",
     ("21.2.c",)),
    (14, "Réaction aux crises d'origine cyber", "resilience", 10, 4,
     "Une cellule de crise qui existe avant la crise, avec des moyens de "
     "communication qui survivent à la panne du système.",
     ("21.2.c", "21.2.j")),
    (15, "Exercices, tests et entrainements", "resilience", 4, 1,
     "Éprouver ce qui est écrit. Un plan jamais joué n'est pas un plan.",
     ("21.2.b", "21.2.c", "21.2.g")),
    (16, "Mise en œuvre d'une approche par les risques", "gouvernance", 4, 0,
     "L'analyse de risque elle-même : gouvernance sous le dirigeant "
     "exécutif, chaque système couvert, risques résiduels acceptés, plan "
     "d'action daté et attribué, réexamen triennal.",
     ("21.2.a",)),
    (17, "Audit de la sécurité des systèmes d'information", "gouvernance",
     5, 0,
     "Se faire regarder par quelqu'un d'autre, à intervalle défini, et "
     "traiter ce qui en sort.",
     ("21.2.f",)),
    (18, "Sécurisation de la configuration des ressources des systèmes "
         "d'information", "protection", 4, 0,
     "Des configurations durcies et vérifiables, au lieu des réglages "
     "d'usine.",
     ("21.2.e",)),
    (19, "Administration des systèmes d'information depuis des ressources "
         "dédiées", "protection", 12, 0,
     "Administrer depuis un poste dédié, sur un réseau dédié — douze moyens, "
     "aucun attendu d'une entité importante.",
     ("21.2.e",)),
    (20, "Supervision de la sécurité des systèmes d'information", "defense",
     6, 0,
     "Collecter, corréler et regarder les journaux : voir l'attaque pendant "
     "qu'elle a lieu.",
     ("21.2.b",)),
)

#: Les objectifs que le principe de proportionnalité réserve aux entités
#: essentielles. Ils ne sont pas « plus difficiles » : ils sont HORS CHAMP
#: pour une entité importante, ce qui n'est pas la même chose qu'un écart.
RESERVES_ESSENTIELLES = (16, 17, 18, 19, 20)

OBJECTIFS_PAR_NUMERO = {o[0]: o for o in OBJECTIFS}

ETATS = {
    "atteint": {"nom": "Atteint",
                "dit": "L'objectif est tenu, et l'entité peut le montrer."},
    "engage": {"nom": "Engagé",
               "dit": "Des travaux sont en cours, l'objectif n'est pas "
                      "encore tenu."},
    "non_engage": {"nom": "Non engagé",
                   "dit": "Rien n'est en place pour cet objectif."},
    "hors_champ": {"nom": "Hors champ",
                   "dit": "Le référentiel ne l'attend pas de cette entité."},
}
ORDRE_ETATS = ("atteint", "engage", "non_engage", "hors_champ")

#: Ce que vaut chaque état dans le taux de préparation. « engagé » vaut la
#: moitié : un chantier ouvert n'est pas rien, et n'est pas fini non plus.
#: « hors champ » ne compte NI au numérateur NI au dénominateur — sans quoi
#: une entité importante afficherait un taux gonflé par cinq objectifs
#: qu'elle n'a jamais eu à tenir.
POIDS = {"atteint": 1.0, "engage": 0.5, "non_engage": 0.0}


# ══════════════════════════════════════════════════════════════════════════
#  LE PÉRIMÈTRE — OBJECTIF 1, ET LE VERROU QU'IL POSE
# ══════════════════════════════════════════════════════════════════════════
#
# C'EST LA RÈGLE LA PLUS FACILE À CONTOURNER, ET LE RÉFÉRENTIEL LA FERME
# EXPLICITEMENT. Les objectifs s'appliquent à TOUS les systèmes de l'entité.
# Une exclusion n'est recevable que si l'entité justifie, PAR UNE ANALYSE DE
# RISQUES, que le système n'est exposé à AUCUN des trois risques nommés — et
# le texte ajoute que la présence de mesures de sécurité ne vaut pas
# justification. « C'est protégé, donc c'est hors périmètre » est refusé.

RISQUES_DU_PERIMETRE = (
    ("interruption",
     "La dégradation ou l'interruption, directe ou indirecte, des activités "
     "ou services de l'entité"),
    ("divulgation",
     "La divulgation à des personnes non autorisées d'informations "
     "sensibles traitées par les activités ou services de l'entité"),
    ("alteration",
     "L'altération des informations nécessaires aux activités ou services "
     "de l'entité"),
)

PERIMETRE_REFUS = {
    "securise": "Une exclusion motivée par les mesures de sécurité en place "
                "est refusée par le référentiel lui-même : « la mise en "
                "œuvre de mesures de sécurité sur ces systèmes "
                "d'information ne permet pas de justifier qu'ils ne sont "
                "exposés à aucun des risques précités ».",
    "sans_justification": "L'exclusion et sa justification doivent figurer "
                          "explicitement dans la liste des systèmes. Une "
                          "exclusion tacite n'existe pas.",
    "sans_analyse": "La justification s'appuie sur une analyse de risques. "
                    "Sans elle, l'exclusion n'est pas recevable.",
}

#: Les mots qui, dans une justification d'exclusion, trahissent le motif que
#: le référentiel refuse. On ne juge pas le fond — on signale la forme.
MOTIFS_REFUSES = ("sécuris", "securis", "protégé", "protege", "chiffré",
                  "chiffre", "pare-feu", "firewall", "antivirus", "cloisonn",
                  "isolé", "isole")


# ══════════════════════════════════════════════════════════════════════════
#  L'ANALYSE DE RISQUE — OBJECTIF 16, EN DÉTAIL
# ══════════════════════════════════════════════════════════════════════════
#
# C'EST LA QUESTION QUI A MOTIVÉ CE MODULE. Dans `nis2`, l'analyse de risque
# est UNE CASE SUR DIX : la mesure a) de l'article 21 §2, avec quatre états.
# L'objectif 16 en fait quatre exigences distinctes, chacune vérifiable —
# et il ne s'adresse qu'aux entités essentielles.

ANALYSE_EXIGENCES = (
    ("gouvernance", "16.1",
     "Une gouvernance par les risques, tenue à jour",
     "Elle place le risque numérique devant le dirigeant exécutif ET les "
     "responsables d'activité, et s'assure que des moyens financiers, "
     "humains ou techniques adéquats sont alloués. L'approche par la "
     "conformité et l'approche par les risques sont complémentaires et "
     "peuvent être mutualisées.",
     "Une analyse de risque produite par la seule équipe sécurité, sans "
     "arbitrage de moyens, ne répond pas à cette exigence."),
    ("couverture", "16.2",
     "Chaque système d'information couvert",
     "L'exigence peut être satisfaite par une analyse par activité ou par "
     "service, à condition qu'elle couvre TOUS les systèmes qui la "
     "portent. Elle s'appuie sur cinq entrées : la PSSI et les "
     "spécificités sectorielles, la maîtrise de l'écosystème, la maîtrise "
     "du système d'information, l'approche par conformité, et les audits. "
     "La méthode EBIOS RM peut être utilisée.",
     "Une analyse qui ne cite aucune de ses cinq entrées est une opinion, "
     "pas une analyse — et c'est ce qu'un contrôle regardera."),
    ("acceptation", "16.3",
     "Validation, risques résiduels acceptés, plan d'action",
     "L'entité valide l'analyse, ACCEPTE explicitement les risques "
     "résiduels, et met en œuvre le plan d'action. Le plan prévoit au "
     "minimum, pour chaque action, une échéance raisonnable et un "
     "responsable.",
     "Un plan d'action sans date ni nom n'est pas un plan : c'est une "
     "liste de souhaits, et le référentiel fixe ce minimum."),
    ("reexamen", "16.4",
     "Réexamen au moins tous les trois ans",
     "Et en tant que de besoin — notamment après un incident de sécurité "
     "ou une évolution majeure du contexte métier, technique ou "
     "organisationnel.",
     "Trois ans est un PLANCHER, pas une cadence : un incident rouvre "
     "l'analyse sans attendre l'échéance."),
)

ANALYSE_ENTREES = (
    ("pssi", "La PSSI et les spécificités sectorielles"),
    ("ecosysteme", "La maîtrise de l'écosystème"),
    ("si", "La maîtrise du système d'information"),
    ("conformite", "L'approche par conformité"),
    ("audits", "Les audits"),
)

#: Le réexamen, en mois. Le référentiel écrit « au minimum tous les trois
#: ans » : trente-six mois est donc la limite haute, pas la cible.
REEXAMEN_MOIS_MAX = 36


# ══════════════════════════════════════════════════════════════════════════
#  LA CHARGE DE LA PREUVE — ARTICLE 15 DU PROJET DE LOI
# ══════════════════════════════════════════════════════════════════════════
#
# ELLE N'EST DANS AUCUN AUTRE MODULE DU DÉPÔT, et c'est pourtant ce qui
# décide de la difficulté d'un contrôle. Mettre en œuvre le référentiel, ce
# n'est pas seulement être en règle : c'est pouvoir S'EN PRÉVALOIR. Faire
# autrement reste permis — à charge de DÉMONTRER que l'objectif est atteint.

PREUVE = {
    "avec_referentiel": {
        "article": "art. 15, alinéa 1",
        "dit": "L'entité qui met en œuvre les exigences du référentiel peut "
               "s'en prévaloir auprès de l'ANSSI lors d'un contrôle pour "
               "démontrer le respect des objectifs.",
        "pour_le_client": "Le référentiel fait office de preuve : c'est le "
                          "chemin le moins coûteux en contrôle.",
    },
    "sans_referentiel": {
        "article": "art. 15, alinéa 2",
        "dit": "Dans le cas contraire, l'entité est tenue de démontrer que "
               "les mesures qu'elle met en œuvre permettent de se "
               "conformer à ces objectifs.",
        "pour_le_client": "Faire autrement est permis, mais la preuve "
                          "change de camp : c'est à l'entité de la "
                          "construire, objectif par objectif.",
    },
}


# ══════════════════════════════════════════════════════════════════════════
#  LES DEUX PONTS QUE LE RÉFÉRENTIEL OUVRE LUI-MÊME
# ══════════════════════════════════════════════════════════════════════════
#
# ILS NE SONT PAS DE NOTRE INVENTION : le référentiel les écrit, et il les
# BORNE. Un pont recopié sans sa borne vaudrait moins que pas de pont.

PONTS = (
    {"cle": "iso27001",
     "quoi": "Un SMSI certifié conforme à l'ISO/CEI 27001:2022",
     "objectifs": (2, 16),
     "borne": "Seulement sur les systèmes d'information COUVERTS PAR LA "
              "CERTIFICATION. Un périmètre de certification restreint ne "
              "couvre qu'une partie de l'objectif — le reste reste à "
              "démontrer.",
     "module": "iso27001",
     "ce_que_le_cabinet_en_fait": "Le périmètre de certification est "
                                  "exactement ce qui plafonne le pont : "
                                  "c'est la première chose à mesurer, "
                                  "avant de compter sur lui."},
    {"cle": "pacs",
     "quoi": "Le recours à une prestation d'accompagnement et de conseil "
             "en sécurité (PACS) qualifiée par l'ANSSI, au titre de "
             "l'article 10 du décret n° 2015-350 du 27 mars 2015 modifié",
     "objectifs": (16,),
     "borne": "Pour la réalisation de l'analyse de risques ET le suivi par "
              "l'entité du plan de traitement qui en est issu. La "
              "prestation seule, sans suivi du plan, ne suffit pas.",
     "module": None,
     "ce_que_le_cabinet_en_fait": "C'est une voie de preuve directe pour "
                                  "l'objectif 16 : la qualification de "
                                  "l'intervenant fait partie de la valeur "
                                  "rendue au client."},
)


def _sans(valeur):
    return valeur is None or valeur == ""


def attendus(statut=None):
    """Ce que le référentiel attend de CETTE entité, et rien de plus.

    LE MODULE REFUSE DE RÉPONDRE SANS STATUT, et ce refus est le premier
    service rendu : la moitié du référentiel dépend de la qualification.
    Rendre un chiffre « moyen » entre EE et EI masquerait exactement ce
    qu'il faut voir."""
    if statut not in ("essentielle", "importante"):
        return {"ok": False,
                "refus": "statut_absent",
                # LES NOMBRES SONT CALCULÉS, PAS ÉCRITS. L'écran les
                # recopiait dans son HTML : deux exemplaires qui auraient
                # divergé au premier changement du référentiel, et c'est la
                # phrase du refus — celle que le client lit — qui aurait
                # menti.
                "dit": ("Le référentiel gradue ses exigences : %d objectifs "
                        "sur %d sont réservés aux entités essentielles, et "
                        "le nombre de moyens attendus change pour les "
                        "autres — %d pour une entité essentielle, %d pour "
                        "une importante. Sans la qualification, tout chiffre "
                        "serait une moyenne entre deux régimes qui ne se "
                        "moyennent pas."
                        % (len(RESERVES_ESSENTIELLES), len(OBJECTIFS),
                           sum(o[3] for o in OBJECTIFS),
                           sum(o[4] for o in OBJECTIFS))),
                "ou_la_trouver": "Le module NIS 2 la calcule à partir du "
                                 "secteur et de la taille."}
    ee = (statut == "essentielle")
    lignes, moyens = [], 0
    for num, titre, pilier, m_ee, m_ei, demande, corr in OBJECTIFS:
        n = m_ee if ee else m_ei
        dans = ee or num not in RESERVES_ESSENTIELLES
        if dans:
            moyens += n
        lignes.append({
            "numero": num, "titre": titre, "pilier": pilier,
            "pilier_nom": PILIERS[pilier],
            "moyens": n, "dans_le_champ": dans,
            "demande": demande,
            "correspondance_nis2": list(corr),
            "reserve_ee": num in RESERVES_ESSENTIELLES,
        })
    dans_champ = [l for l in lignes if l["dans_le_champ"]]
    return {"ok": True, "statut": statut,
            "objectifs": lignes,
            "nombre_objectifs": len(dans_champ),
            "nombre_moyens": moyens,
            "hors_champ": [l["numero"] for l in lignes
                           if not l["dans_le_champ"]],
            "dit": ("Vingt objectifs et %d moyens de conformité."
                    % moyens) if ee else
                   ("Quinze objectifs et %d moyens de conformité : les "
                    "objectifs 16 à 20 sont réservés aux entités "
                    "essentielles." % moyens)}


def preparation(statut=None, etats=None):
    """LE TAUX DE PRÉPARATION — ET IL NE SE FOND DANS AUCUN AUTRE.

    CE QU'IL N'EST PAS, ET C'EST LE POINT : ce n'est pas un taux de
    conformité. Le référentiel qu'il mesure est un document de travail
    attaché à un projet de loi non voté. Un chiffre présenté comme une
    conformité contre un texte qui n'existe pas encore serait faux — et
    faux d'une manière qui ne se voit pas, ce qui est pire.

    CE QU'IL EST : la part du chemin déjà faite vers ce que le contrôle
    demandera. C'est utile, et c'est tout ce que c'est.

    LES OBJECTIFS HORS CHAMP NE COMPTENT NI AU NUMÉRATEUR NI AU
    DÉNOMINATEUR. Sans cela, une entité importante afficherait cinq
    objectifs « acquis » qu'elle n'a jamais eu à tenir."""
    base = attendus(statut)
    if not base["ok"]:
        return dict(base, taux_preparation=None)
    etats = etats or {}
    lignes, num, den = [], 0.0, 0
    for o in base["objectifs"]:
        n = o["numero"]
        if not o["dans_le_champ"]:
            lignes.append(dict(o, etat="hors_champ", compte=False))
            continue
        e = etats.get(n) or etats.get(str(n)) or "non_engage"
        if e not in POIDS:
            e = "non_engage"
        num += POIDS[e]
        den += 1
        lignes.append(dict(o, etat=e, compte=True))
    taux = round(100.0 * num / den, 1) if den else None
    par_pilier = {}
    for l in lignes:
        if not l["compte"]:
            continue
        p = par_pilier.setdefault(l["pilier"], {"nom": PILIERS[l["pilier"]],
                                                "num": 0.0, "den": 0})
        p["num"] += POIDS[l["etat"]]
        p["den"] += 1
    for p in par_pilier.values():
        p["taux"] = round(100.0 * p["num"] / p["den"], 1) if p["den"] else None
    return {
        "ok": True,
        "statut": statut,
        "taux_preparation": taux,
        "sur": den,
        "par_pilier": par_pilier,
        "objectifs": lignes,
        "nombre_moyens": base["nombre_moyens"],
        # ── LA MENTION QUI VOYAGE AVEC LE CHIFFRE ───────────────────────
        # Elle est DANS le résultat, pas à côté : un écran qui n'afficherait
        # que `taux_preparation` afficherait un taux de conformité.
        "nature": "préparation",
        "ne_pas_confondre": "Ce taux n'est PAS un taux de conformité. Il "
                            "mesure l'avancement vers un référentiel qui "
                            "n'est pas en vigueur — document de travail, "
                            "projet de loi non voté, décret non publié.",
        "statut_du_texte": dict(STATUT),
        "ce_qui_oblige_aujourdhui": STATUT["ce_qui_oblige_aujourdhui"],
    }


def perimetre(systemes=None):
    """LE VERROU DE L'OBJECTIF 1 : une exclusion se justifie, ou n'existe pas.

    Chaque système déclaré porte `exclu` et, s'il l'est, `justification` et
    `analyse_de_risques`. On ne juge pas le FOND d'une justification — on
    n'a pas les éléments pour cela. On vérifie qu'elle existe, qu'elle
    s'appuie sur une analyse, et qu'elle n'invoque pas le motif que le
    référentiel refuse en toutes lettres."""
    if systemes is None:
        return {"ok": False, "refus": "aucun_systeme",
                "dit": "L'objectif 1 demande la liste de TOUS les systèmes. "
                       "Sans elle, il n'y a pas de périmètre à vérifier."}
    lignes, refuses = [], 0
    for s in systemes:
        nom = (s or {}).get("nom") or "(système sans nom)"
        if not (s or {}).get("exclu"):
            lignes.append({"nom": nom, "exclu": False, "recevable": True,
                           "dit": "Dans le périmètre."})
            continue
        just = ((s or {}).get("justification") or "").strip()
        analyse = bool((s or {}).get("analyse_de_risques"))
        motifs = []
        if not just:
            motifs.append(PERIMETRE_REFUS["sans_justification"])
        if not analyse:
            motifs.append(PERIMETRE_REFUS["sans_analyse"])
        bas = just.lower()
        if just and any(m in bas for m in MOTIFS_REFUSES):
            motifs.append(PERIMETRE_REFUS["securise"])
        if motifs:
            refuses += 1
        lignes.append({"nom": nom, "exclu": True,
                       "recevable": not motifs,
                       "motifs": motifs,
                       "dit": ("Exclusion recevable en la forme."
                               if not motifs else
                               "Exclusion NON recevable.")})
    return {"ok": True, "systemes": lignes,
            "exclus": sum(1 for l in lignes if l["exclu"]),
            "exclusions_non_recevables": refuses,
            "risques": [{"cle": c, "dit": d} for c, d in RISQUES_DU_PERIMETRE],
            "reserve": "La recevabilité mesurée ici est une recevabilité DE "
                       "FORME. Qu'un système soit réellement hors d'atteinte "
                       "des trois risques est une question de fond, que seule "
                       "l'analyse de risques tranche."}


def analyse_de_risque(declaration=None, statut=None):
    """L'OBJECTIF 16, ET POURQUOI IL NE S'ADRESSE PAS À TOUT LE MONDE.

    Pour une entité IMPORTANTE, cet objectif est hors champ. Ce n'est pas
    un écart, et il ne faut surtout pas l'afficher comme un « 0 % » : le
    référentiel ne le lui demande pas. Le module le dit, plutôt que de
    rendre un chiffre qui serait lu comme un manquement."""
    if statut not in ("essentielle", "importante"):
        return {"ok": False, "refus": "statut_absent",
                "dit": attendus(None)["dit"]}
    if statut == "importante":
        return {"ok": True, "hors_champ": True, "taux": None,
                "dit": "L'objectif 16 est réservé aux entités essentielles "
                       "par le principe de proportionnalité. Le référentiel "
                       "n'attend pas d'approche par les risques formalisée "
                       "d'une entité importante.",
                "ne_veut_pas_dire": "Qu'une analyse de risques serait "
                                    "inutile : l'objectif 1 en exige déjà "
                                    "une pour justifier toute exclusion de "
                                    "périmètre, et la mesure a) de "
                                    "l'article 21 §2 de la directive reste "
                                    "due.",
                "exigences": []}
    d = declaration or {}
    lignes, faits = [], 0
    for cle, ref, titre, dit, piege in ANALYSE_EXIGENCES:
        v = d.get(cle)
        tenu = bool(v)
        manque = []
        if cle == "couverture" and tenu:
            # LES CINQ ENTRÉES SONT NOMMÉES PAR LE RÉFÉRENTIEL : une analyse
            # qui n'en cite aucune ne s'appuie sur rien de vérifiable.
            citees = set(d.get("entrees") or ())
            absentes = [nom for c, nom in ANALYSE_ENTREES if c not in citees]
            if absentes:
                manque.append("entrées non citées : " + " ; ".join(absentes))
        if cle == "acceptation" and tenu:
            if not d.get("risques_residuels_acceptes"):
                manque.append("les risques résiduels ne sont pas "
                              "explicitement acceptés")
            if not d.get("plan_date_et_responsable"):
                manque.append("le plan d'action n'a pas, pour chaque action, "
                              "une échéance et un responsable")
        if cle == "reexamen" and tenu:
            mois = d.get("dernier_reexamen_mois")
            if mois is None:
                manque.append("la date du dernier réexamen n'est pas "
                              "renseignée")
            elif mois > REEXAMEN_MOIS_MAX:
                manque.append("dernier réexamen il y a %d mois — le "
                              "référentiel fixe un plancher de %d"
                              % (mois, REEXAMEN_MOIS_MAX))
        if cle == "gouvernance" and tenu and not d.get("moyens_alloues"):
            manque.append("aucun moyen financier, humain ou technique "
                          "déclaré comme alloué")
        acquis = tenu and not manque
        if acquis:
            faits += 1
        lignes.append({"cle": cle, "reference": ref, "titre": titre,
                       "demande": dit, "piege": piege,
                       "declare": tenu, "acquis": acquis, "manque": manque})
    return {"ok": True, "hors_champ": False,
            "exigences": lignes,
            "acquises": faits, "total": len(ANALYSE_EXIGENCES),
            "taux": round(100.0 * faits / len(ANALYSE_EXIGENCES), 1),
            "nature": "préparation",
            "ne_pas_confondre": "Mesure de complétude de la déclaration, pas "
                                "un jugement sur la qualité de l'analyse.",
            "entrees_attendues": [{"cle": c, "nom": n}
                                  for c, n in ANALYSE_ENTREES]}


def ponts(iso_certifie=None, iso_perimetre_complet=None, pacs=None):
    """CE QUE LE RÉFÉRENTIEL ACCEPTE COMME PREUVE, ET JUSQU'OÙ.

    LA BORNE COMPTE AUTANT QUE LE PONT. Une certification ISO ne vaut que
    sur les systèmes qu'elle couvre : l'annoncer sans son périmètre ferait
    croire à une preuve générale."""
    out = []
    for p in PONTS:
        if p["cle"] == "iso27001":
            if not iso_certifie:
                etat, dit = "absent", "Aucune certification déclarée."
            elif iso_perimetre_complet:
                etat, dit = "complet", ("La certification couvre l'ensemble "
                                        "des systèmes : le pont vaut pour "
                                        "les objectifs 2 et 16.")
            else:
                etat, dit = "partiel", ("La certification ne couvre qu'une "
                                        "partie des systèmes. Hors de ce "
                                        "périmètre, les objectifs 2 et 16 "
                                        "restent à démontrer autrement.")
        else:
            if not pacs:
                etat, dit = "absent", "Aucune prestation qualifiée déclarée."
            else:
                etat, dit = "complet", ("La prestation qualifiée couvre "
                                        "l'objectif 16, à condition que le "
                                        "plan de traitement soit suivi par "
                                        "l'entité.")
        out.append(dict(p, etat=etat, dit=dit))
    return {"ok": True, "ponts": out,
            "preuve": {k: dict(v) for k, v in PREUVE.items()}}


def referentiel():
    """Ce que l'écran a besoin de savoir pour poser les questions."""
    return {
        "statut": dict(STATUT),
        # LE REFUS VOYAGE AVEC LE RÉFÉRENTIEL, et c'est une correction.
        # L'écran l'obtenait par un SECOND appel : une requête de plus, et
        # surtout un instant où le panneau ne dit rien. Si cet appel échoue,
        # le visiteur perd l'explication au moment précis où elle lui est
        # due. Le référentiel est déjà chargé quand le panneau se peint : la
        # phrase y est donc, calculée par le même code.
        "refus_sans_statut": attendus(None),
        "sources": [dict(s) for s in SOURCES],
        "familles": [{"cle": c, "alinea": a, "texte": t, "dit": d}
                     for c, a, t, d in FAMILLES],
        "piliers": [{"cle": c, "nom": n} for c, n in PILIERS.items()],
        "objectifs": [{"numero": n, "titre": t, "pilier": p,
                       "pilier_nom": PILIERS[p], "moyens_ee": me,
                       "moyens_ei": mi, "demande": d,
                       "correspondance_nis2": list(c),
                       "reserve_ee": n in RESERVES_ESSENTIELLES}
                      for n, t, p, me, mi, d, c in OBJECTIFS],
        "etats": [dict(ETATS[c], cle=c) for c in ORDRE_ETATS],
        "analyse": [{"cle": c, "reference": r, "titre": t, "demande": d,
                     "piege": pg}
                    for c, r, t, d, pg in ANALYSE_EXIGENCES],
        "entrees_analyse": [{"cle": c, "nom": n} for c, n in ANALYSE_ENTREES],
        "reexamen_mois_max": REEXAMEN_MOIS_MAX,
        "risques_perimetre": [{"cle": c, "dit": d}
                              for c, d in RISQUES_DU_PERIMETRE],
        "refus_perimetre": dict(PERIMETRE_REFUS),
        "preuve": {k: dict(v) for k, v in PREUVE.items()},
        "ponts": [dict(p) for p in PONTS],
        "totaux": {"objectifs": len(OBJECTIFS),
                   "moyens_ee": sum(o[3] for o in OBJECTIFS),
                   "moyens_ei": sum(o[4] for o in OBJECTIFS),
                   "reserves_ee": list(RESERVES_ESSENTIELLES)},
    }


def _verifier():
    """LA GARDE — elle recompte, elle ne fait pas confiance aux commentaires.

    Les nombres annoncés en tête de fichier — vingt objectifs, 152 moyens
    pour une entité essentielle, 76 pour une importante — sont ré-additionnés
    ici à chaque chargement. Un commentaire se périme en silence ; une
    addition, non."""
    fautes = []
    if len(OBJECTIFS) != 20:
        fautes.append("%d objectifs, on en attend vingt" % len(OBJECTIFS))
    nums = [o[0] for o in OBJECTIFS]
    if nums != list(range(1, 21)):
        fautes.append("les numéros d'objectif ne se suivent pas : %s" % nums)
    ee = sum(o[3] for o in OBJECTIFS)
    ei = sum(o[4] for o in OBJECTIFS)
    if ee != 152:
        fautes.append("%d moyens pour une entité essentielle, on en a "
                      "compté 152 dans le référentiel" % ee)
    if ei != 76:
        fautes.append("%d moyens pour une entité importante, on en a "
                      "compté 76 dans le référentiel" % ei)
    for n in RESERVES_ESSENTIELLES:
        if OBJECTIFS_PAR_NUMERO[n][4] != 0:
            fautes.append("l'objectif %d est réservé aux entités "
                          "essentielles : il ne peut pas attendre de moyens "
                          "d'une entité importante" % n)
    for n, t, p, me, mi, d, c in OBJECTIFS:
        if p not in PILIERS:
            fautes.append("l'objectif %d porte un pilier inconnu : %r" % (n, p))
        if mi > me:
            fautes.append("l'objectif %d attend plus d'une entité importante "
                          "que d'une essentielle" % n)
        if not c:
            fautes.append("l'objectif %d ne se rattache à aucune disposition "
                          "de la directive" % n)
    # LE TAUX NE DOIT JAMAIS S'APPELER AUTREMENT QUE « préparation ».
    p = preparation("essentielle", {})
    if p.get("nature") != "préparation" or "taux_conformite" in p:
        fautes.append("le résultat ne se déclare plus comme une préparation")
    if STATUT["en_vigueur"] is not False:
        fautes.append("le statut déclare le référentiel en vigueur : il ne "
                      "l'est pas, et le taux changerait de nature")
    for s in SOURCES:
        if not s.get("apporte") or "lue" not in s:
            fautes.append("la source %r ne dit pas ce qu'elle apporte ou si "
                          "elle a été lue" % s.get("cle"))
    return tuple(fautes)


_FAUTES = _verifier()
assert not _FAUTES, "nis2_recyf : " + " | ".join(_FAUTES)
