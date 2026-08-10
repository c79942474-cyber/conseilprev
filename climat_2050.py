# -*- coding: utf-8 -*-
"""Aléas climatiques d'ici 2030 et 2050 — la couche que les rapports XDI laissent vide.

POURQUOI CE MODULE EXISTE

Le référentiel d'implantation porte déjà trois indicateurs de risque physique,
tous issus de XDI : le classement des centres planifiés (juin 2026), les feux
de forêt (août 2025) et les inondations (septembre 2025). Ils sont excellents
et ils ont deux limites que rien ne comblait :

  1. LES DEUX RAPPORTS D'ALÉAS NE COUVRENT QUE LES VINGT-SEPT ÉTATS MEMBRES.
     Le Royaume-Uni, la Suisse et la Norvège en sont donc absents — non par
     bonne fortune, mais par périmètre. Et la Suède est hors du classement
     des vingt-cinq premiers, donc sans note de risque physique du tout. Trois
     des pays les plus sérieusement candidats à un centre de données européen
     arrivaient au comparateur avec leurs cases d'aléas VIDES.

  2. ILS DONNENT UN ÉTAT, PAS UNE TRAJECTOIRE. Un investisseur décide en 2026
     pour un bâtiment qui vivra quarante ans. « Quel est le risque
     aujourd'hui » et « quel est le risque quand l'actif sera à mi-vie » sont
     deux questions différentes, et la seconde est celle qui engage.

Ce module répond aux deux : six aléas, deux horizons — 2030 et 2050 — pour
vingt-huit pays, y compris ceux que les rapports européens excluent.

CE QUE CE MODULE SERT, ET À QUEL TITRE

Des CLASSES D'EXPOSITION, pas des valeurs modélisées. La différence est
essentielle et elle est écrite partout dans les textes servis. XDI modélise un
site et rend un pourcentage de dommage annuel ; ce module situe un PAYS sur une
échelle à cinq crans, à partir de ce sur quoi les grandes évaluations
s'accordent — GIEC AR6, Agence européenne pour l'environnement, JRC PESETA IV.
Un chiffre décimal par pays et par aléa serait une précision empruntée : les
évaluations s'accordent sur le SENS et sur le NIVEAU RELATIF, pas sur une
valeur nationale au dixième près.

Chaque case porte donc trois choses et non une : la classe à 2030, la classe à
2050, et la CONFIANCE que la littérature autorise. Une classe élevée en
confiance faible ne se lit pas comme une classe élevée en confiance élevée, et
un tableau qui les afficherait pareillement mentirait par omission.

LA SEULE EXCEPTION À « L'ABSENCE N'EST JAMAIS UNE BONNE NOTE »

Partout ailleurs dans ce référentiel, une donnée manquante vaut None et porte
la raison de son absence — jamais une note favorable. Il existe ici UN cas où
l'absence de risque est un fait et non un trou : la submersion côtière d'un
pays sans littoral. La Suisse n'a pas « une donnée manquante » de submersion,
elle n'a pas de mer.

Ce cas est nommé `sans_objet`, il vaut 100, et il est VERROUILLÉ : le contrôle
d'intégrité exécuté au chargement du module refuse `sans_objet` pour tout autre
aléa que la submersion, et pour tout pays absent de la liste des enclavés. Une
exception non gardée deviendrait la porte par laquelle rentrent toutes les
autres.

CE QUE CE MODULE NE FAIT PAS

Il ne chiffre pas un site. La classe nationale ÉCRASE des contrastes énormes :
l'Italie du Pô n'est pas l'Italie des Pouilles, l'Espagne atlantique n'est pas
l'Espagne méditerranéenne. Aucune décision de terrain ne se prend là-dessus —
il faut l'étude d'aléa locale, le plan de prévention des risques applicable et
la cote de référence du site. Ce module dit où regarder, et avec quelle
urgence.
"""
from datetime import datetime, timezone

VERSION = "2026-08-a"

HORIZONS = (2030, 2050)
HORIZON_REFERENCE = 2025

# ═══════════════════════════════════════════════════════════════════════════
# 1. L'ÉCHELLE — cinq crans, et un cas verrouillé
# ═══════════════════════════════════════════════════════════════════════════

NIVEAUX = {
    "sans_objet": {
        "nom": "Sans objet", "note": 100, "rang": 0,
        "sens": "l'aléa ne peut pas se produire ici — pays sans littoral",
    },
    "faible": {
        "nom": "Faible", "note": 85, "rang": 1,
        "sens": "aléa présent mais non déterminant pour le choix du pays",
    },
    "modere": {
        "nom": "Modéré", "note": 60, "rang": 2,
        "sens": "à traiter en conception ; ne disqualifie pas le pays",
    },
    "eleve": {
        "nom": "Élevé", "note": 30, "rang": 3,
        "sens": "conditionne le choix du site DANS le pays, et le coût d'assurance",
    },
    "tres_eleve": {
        "nom": "Très élevé", "note": 10, "rang": 4,
        "sens": "peut disqualifier des régions entières ; exige une étude d'aléa avant toute promesse de vente",
    },
}

CONFIANCES = {
    "elevee": {"nom": "Confiance élevée",
               "sens": "les évaluations concordent sur le sens ET sur le niveau relatif"},
    "moyenne": {"nom": "Confiance moyenne",
                "sens": "concordance sur le sens, dispersion sur l'ampleur"},
    "faible": {"nom": "Confiance faible",
               "sens": "signal discuté, ou déterminé par des facteurs locaux que l'échelle nationale ne voit pas"},
}

# Les pays sans littoral. C'est la SEULE liste qui autorise `sans_objet`, et
# uniquement pour la submersion.
ENCLAVES = ("AT", "CH", "CZ", "HU", "LU", "SK", "LI", "RS", "MK")

# ═══════════════════════════════════════════════════════════════════════════
# 2. LES SIX ALÉAS — ce que chacun endommage, et pourquoi il compte ICI
# ═══════════════════════════════════════════════════════════════════════════

ALEAS = {
    "submersion": {
        "nom": "Submersion côtière",
        "atteint": "le foncier et l'accès ; irréversible à l'échelle de la vie du bâtiment",
        "pourquoi": "L'élévation du niveau de la mer est le seul aléa de cette "
                    "liste qui ne redescend pas. Une cote gagnée est gagnée pour "
                    "des siècles : c'est le seul où une erreur d'implantation ne "
                    "se corrige par aucune ingénierie sur site.",
    },
    "feu": {
        "nom": "Feu de forêt",
        "atteint": "l'alimentation électrique aérienne, les fibres, l'accès, la qualité de l'air aspiré",
        "pourquoi": "Un centre de données brûle rarement ; il s'arrête parce que "
                    "la ligne haute tension et la route ont brûlé, et parce que "
                    "les filtres se saturent de suie. Le dommage est presque "
                    "toujours INDIRECT — c'est pourquoi il est sous-estimé.",
    },
    "secheresse": {
        "nom": "Sécheresse",
        "atteint": "le refroidissement évaporatif, le permis d'eau, l'acceptabilité locale",
        "pourquoi": "La sécheresse ne casse rien : elle retire l'autorisation de "
                    "prélever, en général l'été, c'est-à-dire exactement quand le "
                    "refroidissement en a le plus besoin. Le risque est "
                    "réglementaire et politique avant d'être physique.",
    },
    "pluie": {
        "nom": "Précipitations extrêmes et ruissellement",
        "atteint": "les locaux techniques enterrés, les chemins de câbles, les groupes électrogènes",
        "pourquoi": "C'est l'aléa qui monte PARTOUT, y compris là où le total "
                    "annuel baisse : une atmosphère plus chaude porte plus de "
                    "vapeur, donc des averses plus intenses même en climat qui "
                    "s'assèche. Aucun pays d'Europe n'est classé faible ici, et "
                    "c'est l'information principale de cette colonne.",
    },
    "glissement": {
        "nom": "Glissement de terrain",
        "atteint": "les accès, les réseaux enterrés, la stabilité des plateformes en pente",
        "pourquoi": "Aléa très localisé, donc mal saisi par une classe nationale — "
                    "mais qui progresse pour deux raisons identifiées : des pluies "
                    "plus intenses, et la dégradation du pergélisol en altitude, "
                    "qui déstabilise des versants alpins tenus depuis des "
                    "millénaires.",
    },
    "hydrologie": {
        "nom": "Étiage et régime des cours d'eau",
        "atteint": "le refroidissement en eau de rivière, la logistique fluviale, la production électrique amont",
        "pourquoi": "Distinct de la sécheresse : il ne s'agit pas de la ressource "
                    "moyenne mais du DÉBIT AU PIRE MOMENT. Le Rhin de 2018 et de "
                    "2022 a contraint le refroidissement de centrales et la "
                    "logistique de toute une vallée industrielle sans qu'aucun "
                    "arrêté sécheresse ne soit nécessaire.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. LA MER — les seuls chiffres de ce module, et ils sont mondiaux
#
#    Le GIEC publie une élévation du niveau moyen MONDIAL de la mer, par
#    scénario et par horizon, relativement à la moyenne 1995-2014. Ces valeurs
#    sont servies telles quelles parce qu'elles sont publiées telles quelles.
#
#    LE FAIT QUI DÉCIDE, ET QUI SURPREND. À 2050, l'écart entre le scénario le
#    plus sobre et le plus émetteur est de QUATRE CENTIMÈTRES : la trajectoire
#    d'émissions ne change presque rien avant le milieu du siècle, parce que
#    l'élévation d'ici là est déjà engagée par la chaleur accumulée. À 2100
#    l'écart est de trente-trois centimètres. Autrement dit : pour un bâtiment
#    livré en 2030, le scénario ne se discute pas — il faut encaisser environ
#    vingt centimètres quoi qu'il arrive ; c'est APRÈS que le choix collectif
#    pèse. Un dossier qui présenterait un scénario optimiste comme une
#    protection à 2050 serait faux.
# ═══════════════════════════════════════════════════════════════════════════

MER_SCENARIOS = {
    "SSP1-2.6": "Émissions fortement réduites — réchauffement contenu autour de 1,8 °C",
    "SSP2-4.5": "Trajectoire intermédiaire — autour de 2,7 °C",
    "SSP5-8.5": "Émissions très élevées — employé comme test de résistance, pas comme prévision",
}

# scenario : {horizon : (médiane m, borne basse, borne haute)}
# Relativement à la moyenne 1995-2014.
MER = {
    "SSP1-2.6": {2050: (0.19, 0.16, 0.25), 2100: (0.44, 0.32, 0.62)},
    "SSP2-4.5": {2050: (0.20, 0.17, 0.26), 2100: (0.56, 0.44, 0.76)},
    "SSP5-8.5": {2050: (0.23, 0.20, 0.29), 2100: (0.77, 0.63, 1.01)},
}

# L'AR6 ne publie PAS 2030 : ses horizons de référence sont 2050, 2100 et 2150.
# On sert donc un ordre de grandeur interpolé, et on le dit — plutôt que de
# laisser une case vide sur l'horizon que le comparateur propose.
MER_2030 = {
    "valeur_m": 0.10,
    "nature": "calcule",
    "methode": "interpolation linéaire entre la moyenne 1995-2014 et la médiane 2050, "
               "tous scénarios confondus — ils ne se distinguent pas à cet horizon",
    "reserve": "l'élévation ACCÉLÈRE : une interpolation linéaire sous-estime la "
               "seconde moitié de la période et surestime la première. À prendre "
               "comme un ordre de grandeur, jamais comme une cote de projet.",
}

SOURCE_MER = {
    "titre": "AR6, Groupe de travail I — élévation du niveau moyen mondial de la mer",
    "editeur": "GIEC (IPCC), 2021",
    "url": "https://www.ipcc.ch/report/ar6/wg1/",
    "nature": "referentiel",
    "note": "Valeurs MONDIALES, relatives à la moyenne 1995-2014, plages "
            "« probables » (17-83 %). Le niveau LOCAL peut s'en écarter "
            "fortement dans les deux sens — voir les corrections locales "
            "ci-dessous. Les processus d'instabilité de la calotte antarctique, "
            "de confiance faible, ne sont pas dans ces plages et pourraient les "
            "dépasser à la fin du siècle.",
}

# ── LA CORRECTION QUI RENVERSE LE CLASSEMENT ────────────────────────────────
# Le niveau de la mer est mondial ; le niveau RELATIF, celui qui inonde ou non,
# dépend aussi du mouvement du sol. Deux effets opposés, tous deux mesurés :
MER_LOCAL = {
    "FI": (+7.0, "Rebond post-glaciaire dans le golfe de Botnie : le sol se relève "
                 "plus vite que la mer ne monte. Le niveau relatif de la mer y "
                 "BAISSE encore, et devrait continuer de baisser au nord au-delà "
                 "de 2050."),
    "SE": (+6.0, "Rebond post-glaciaire fort au nord (golfe de Botnie), quasi nul "
                 "en Scanie au sud : la Suède porte les deux régimes à la fois. "
                 "Un site nordique et un site méridional n'ont pas la même "
                 "exposition, et l'échelle nationale ne peut pas le montrer."),
    "NO": (+3.0, "Rebond post-glaciaire sur la plus grande partie du littoral, "
                 "atténuant l'élévation ; côtes escarpées peu propices à la "
                 "submersion étendue."),
    "EE": (+2.5, "Rebond modéré au nord du pays, atténuant l'élévation."),
    "NL": (-1.0, "Subsidence des sols tourbeux et des polders drainés : le sol "
                 "s'enfonce pendant que la mer monte. Les deux mouvements "
                 "s'ajoutent au lieu de se compenser."),
    "IT": (-2.0, "Subsidence marquée du delta du Pô et de la lagune de Venise, "
                 "d'origine naturelle et anthropique — elle a localement dépassé "
                 "l'élévation eustatique au XXᵉ siècle."),
}

SOURCE_MER_LOCAL = {
    "titre": "Mouvements verticaux du sol — rebond post-glaciaire et subsidence",
    "editeur": "Synthèse CONSEILPREV d'après AEE, services géologiques nationaux "
               "et GIEC AR6 chapitre 9",
    "nature": "analyse",
    "note": "Ordres de grandeur en millimètres par an, positifs quand le sol se "
            "relève. Contrastes INTRA-nationaux majeurs, notamment en Suède. À "
            "confirmer par le repère de nivellement le plus proche du site.",
}

# ═══════════════════════════════════════════════════════════════════════════
# 4. L'EXPOSITION PAR PAYS — six tables, une par aléa
#
#    Format : pays -> (classe 2030, classe 2050, confiance, note ou None)
#    La note n'est écrite que là où il y a quelque chose de particulier à
#    dire : une table où chaque ligne porte un commentaire ne se lit plus.
# ═══════════════════════════════════════════════════════════════════════════

# ── SUBMERSION CÔTIÈRE ──────────────────────────────────────────────────────
# Classée sur l'étendue des terres basses, l'exposition aux surcotes de tempête
# et le mouvement vertical du sol. La qualité des DÉFENSES n'entre pas dans la
# classe : elle relève du pays, pas de l'aléa — et une défense se finance,
# vieillit et peut être dépassée, tandis que l'aléa reste.
SUBMERSION = {
    "NL": ("eleve", "tres_eleve", "elevee",
           "Un quart du territoire sous le niveau de la mer, sols en subsidence. "
           "À contrebalancer par le fait que les Pays-Bas portent le standard de "
           "protection le plus élevé d'Europe — mais un standard est un choix "
           "budgétaire, pas une propriété du lieu."),
    "BE": ("eleve", "eleve", "elevee",
           "Littoral court mais entièrement bas ; polders et estuaire de l'Escaut."),
    "DK": ("eleve", "eleve", "elevee",
           "Très long linéaire côtier bas et insulaire rapporté à la surface du pays."),
    "DE": ("modere", "eleve", "elevee",
           "Exposition concentrée sur la côte de la mer du Nord et l'estuaire de "
           "l'Elbe ; l'essentiel du territoire est hors d'atteinte."),
    "GB": ("modere", "eleve", "elevee",
           "Estuaires de la Tamise et du Humber, côte est basse. La protection de "
           "Londres est dimensionnée sur un horizon explicite : c'est une date, "
           "pas une garantie perpétuelle."),
    "IE": ("modere", "eleve", "moyenne",
           "Dublin et Cork sur des sites bas d'estuaire."),
    "FR": ("modere", "eleve", "elevee",
           "Deux façades exposées pour des raisons différentes : surcotes "
           "atlantiques, marais littoraux ; Méditerranée microtidale mais "
           "deltas bas (Camargue)."),
    "IT": ("modere", "eleve", "elevee",
           "Delta du Pô et lagune de Venise : la subsidence y ajoute à "
           "l'élévation. Le reste du littoral est en grande partie escarpé."),
    "PL": ("modere", "eleve", "moyenne",
           "Delta de la Vistule (Żuławy) partiellement sous le niveau de la mer ; "
           "surcotes baltiques plus faibles qu'en mer du Nord."),
    "ES": ("modere", "modere", "moyenne",
           "Littoral majoritairement escarpé ; exposition concentrée sur les "
           "deltas (Èbre) et les plaines côtières du Levant."),
    "PT": ("modere", "modere", "moyenne", "Estuaire du Tage et rias du nord."),
    "GR": ("modere", "modere", "moyenne", None),
    "RO": ("faible", "modere", "moyenne",
           "Delta du Danube très exposé, mais sans enjeu d'implantation industrielle."),
    "BG": ("faible", "modere", "faible", None),
    "HR": ("faible", "modere", "moyenne", "Côte adriatique rocheuse et abrupte."),
    "SI": ("faible", "modere", "faible", "Quarante-six kilomètres de littoral."),
    "LV": ("faible", "modere", "moyenne", None),
    "LT": ("faible", "modere", "moyenne", None),
    "EE": ("faible", "faible", "moyenne",
           "Rebond post-glaciaire au nord, atténuant l'élévation."),
    "SE": ("faible", "faible", "elevee",
           "Le sol se relève plus vite que la mer ne monte au nord ; l'effet "
           "s'annule en Scanie. Avantage réel, mais RÉGIONAL et non national."),
    "FI": ("faible", "faible", "elevee",
           "Le niveau relatif de la mer BAISSE encore dans le golfe de Botnie. "
           "C'est le seul cas d'Europe où l'élévation est plus que compensée."),
    "NO": ("faible", "faible", "elevee",
           "Rebond post-glaciaire et côtes escarpées."),
    # ── Les enclavés : un fait, pas une donnée manquante.
    "AT": ("sans_objet", "sans_objet", "elevee", None),
    "CH": ("sans_objet", "sans_objet", "elevee", None),
    "CZ": ("sans_objet", "sans_objet", "elevee", None),
    "HU": ("sans_objet", "sans_objet", "elevee", None),
    "LU": ("sans_objet", "sans_objet", "elevee", None),
    "SK": ("sans_objet", "sans_objet", "elevee", None),
    "LI": ("sans_objet", "sans_objet", "elevee", None),
}

# ── FEU DE FORÊT ────────────────────────────────────────────────────────────
# Le signal robuste n'est pas seulement « le sud brûle » : c'est l'EXTENSION
# vers le nord et l'ALLONGEMENT de la saison. Deux pays réputés hors de danger
# ne le sont plus — la Suède depuis 2018, le Royaume-Uni depuis 2022.
FEU = {
    "PT": ("tres_eleve", "tres_eleve", "elevee",
           "Surface brûlée par habitant parmi les plus élevées d'Europe, "
           "structurellement, depuis des décennies."),
    "GR": ("tres_eleve", "tres_eleve", "elevee", None),
    "ES": ("tres_eleve", "tres_eleve", "elevee", None),
    "IT": ("eleve", "tres_eleve", "elevee", None),
    "FR": ("eleve", "tres_eleve", "elevee",
           "L'extension hors du pourtour méditerranéen est le fait marquant : "
           "les feux de 2022 en Gironde ont touché un massif que la planification "
           "ne classait pas à risque majeur."),
    "HR": ("eleve", "eleve", "moyenne", None),
    "BG": ("eleve", "eleve", "moyenne", None),
    "RO": ("modere", "eleve", "moyenne", None),
    "SI": ("modere", "eleve", "moyenne", None),
    "SE": ("modere", "eleve", "moyenne",
           "Contre-intuitif et documenté : l'été 2018 a brûlé plus de vingt mille "
           "hectares et mobilisé des moyens européens. Le feu boréal est le "
           "signal en plus forte croissance relative du continent — un pays "
           "nordique n'est pas un pays sans feu."),
    "FI": ("modere", "eleve", "moyenne", "Même dynamique boréale qu'en Suède."),
    "NO": ("modere", "modere", "faible",
           "Feux de bruyère côtiers en fin d'hiver sec, distincts du feu boréal estival."),
    "PL": ("modere", "eleve", "moyenne",
           "Grandes pinèdes continentales sur sols sableux — le type de "
           "peuplement le plus inflammable d'Europe centrale."),
    "DE": ("modere", "eleve", "moyenne",
           "Brandebourg : pinèdes sur sable, sols de munitions non dépolluées "
           "qui interdisent l'attaque terrestre sur certains massifs."),
    "HU": ("modere", "eleve", "moyenne", None),
    "SK": ("modere", "eleve", "faible", None),
    "CZ": ("modere", "eleve", "moyenne", None),
    "AT": ("modere", "modere", "faible", None),
    "CH": ("modere", "modere", "moyenne",
           "Vallées sèches intra-alpines (Valais, Tessin) — foyers réels, étendue limitée."),
    "LI": ("modere", "modere", "faible", None),
    "GB": ("faible", "modere", "moyenne",
           "L'épisode de juillet 2022, au-delà de quarante degrés, a produit la "
           "plus forte sollicitation des services d'incendie depuis la guerre. "
           "Le sujet est récent, il n'est plus théorique."),
    "IE": ("faible", "modere", "faible", "Feux de landes et de tourbières."),
    "NL": ("faible", "modere", "moyenne", "Landes sèches (Veluwe) — surfaces limitées."),
    "BE": ("faible", "modere", "faible", None),
    "DK": ("faible", "modere", "faible", None),
    "LU": ("faible", "modere", "faible", None),
    "EE": ("modere", "modere", "faible", None),
    "LV": ("modere", "modere", "faible", None),
    "LT": ("modere", "modere", "faible", None),
}

# ── SÉCHERESSE ──────────────────────────────────────────────────────────────
# Le gradient nord-sud est le signal le plus robuste de toute la climatologie
# européenne. Il se double d'un fait moins connu : l'Europe CENTRALE a connu
# entre 2018 et 2022 une séquence sèche pluriannuelle sans équivalent moderne.
SECHERESSE = {
    "ES": ("tres_eleve", "tres_eleve", "elevee", None),
    "PT": ("tres_eleve", "tres_eleve", "elevee", None),
    "GR": ("tres_eleve", "tres_eleve", "elevee", None),
    "IT": ("eleve", "tres_eleve", "elevee",
           "Le bassin du Pô, cœur industriel du pays, est aussi son bassin le "
           "plus sollicité — la sécheresse de 2022 y a été la plus sévère "
           "depuis deux siècles de relevés."),
    "BG": ("eleve", "eleve", "moyenne", None),
    "RO": ("eleve", "eleve", "moyenne", None),
    "HU": ("eleve", "eleve", "elevee",
           "Bassin pannonien : assèchement projeté parmi les plus marqués "
           "d'Europe continentale, sur un pays dépendant de fleuves entrants."),
    "HR": ("modere", "eleve", "moyenne", None),
    "FR": ("modere", "eleve", "elevee",
           "Gradient interne fort : arrêtés sécheresse désormais annuels dans le "
           "sud et le centre-ouest, rares en Bretagne et dans le Nord."),
    "GB": ("modere", "eleve", "elevee",
           "Le sud-est de l'Angleterre est déjà classé en stress hydrique sérieux "
           "par l'Environment Agency, sur le bassin de population le plus dense "
           "du pays — c'est-à-dire là où les centres de données se construisent."),
    "DE": ("modere", "eleve", "elevee",
           "Séquence sèche 2018-2020 sans précédent moderne ; conflits d'usage "
           "déjà documentés dans le Brandebourg."),
    "PL": ("modere", "eleve", "elevee",
           "Ressource par habitant parmi les plus faibles d'Europe, indépendamment "
           "du changement climatique."),
    "CZ": ("modere", "eleve", "moyenne", None),
    "SK": ("modere", "eleve", "moyenne", None),
    "AT": ("modere", "modere", "moyenne", None),
    "SI": ("modere", "modere", "moyenne", None),
    "BE": ("modere", "eleve", "moyenne",
           "La Flandre figure parmi les régions européennes les plus tendues en "
           "eau par habitant, avant même toute projection."),
    "NL": ("modere", "eleve", "moyenne",
           "Dépendance au débit du Rhin, et salinisation croissante des prises "
           "d'eau de l'ouest lors des étiages."),
    "LU": ("modere", "modere", "faible", None),
    "DK": ("modere", "modere", "moyenne", None),
    "CH": ("faible", "modere", "moyenne",
           "L'abondance actuelle tient en partie à la fonte glaciaire estivale. "
           "Ce soutien passe par un maximum puis décline : l'avantage suisse en "
           "eau d'été s'érode après le pic, pas avant."),
    "LI": ("faible", "modere", "faible", None),
    "IE": ("faible", "modere", "moyenne", None),
    "EE": ("faible", "modere", "faible", None),
    "LV": ("faible", "modere", "faible", None),
    "LT": ("faible", "modere", "moyenne", None),
    "SE": ("faible", "faible", "moyenne",
           "L'été 2018 a produit des restrictions dans le sud du pays : "
           "« faible » ne veut pas dire « jamais »."),
    "FI": ("faible", "faible", "elevee", None),
    "NO": ("faible", "faible", "elevee", None),
}

# ── PRÉCIPITATIONS EXTRÊMES ────────────────────────────────────────────────
# LA colonne à lire en entier. Une atmosphère plus chaude retient plus de
# vapeur d'eau — d'environ 7 % par degré. Les averses extrêmes s'intensifient
# donc y compris là où le cumul annuel baisse. Aucun pays n'est classé faible.
PLUIE = {
    "DE": ("eleve", "tres_eleve", "elevee",
           "La crue de l'Ahr en juillet 2021 est devenue la référence "
           "européenne : plus de cent quatre-vingts morts sur un bassin que "
           "l'aléa de référence ne décrivait pas."),
    "BE": ("eleve", "tres_eleve", "elevee",
           "Même épisode de juillet 2021, versant Vesdre."),
    "AT": ("eleve", "tres_eleve", "elevee", None),
    "CH": ("eleve", "tres_eleve", "elevee",
           "Relief alpin : le temps de concentration se compte en dizaines de "
           "minutes, ce qui laisse peu de marge d'alerte."),
    "SI": ("eleve", "tres_eleve", "moyenne",
           "Les inondations d'août 2023 ont touché une large part du territoire "
           "en un seul épisode."),
    "LI": ("eleve", "tres_eleve", "faible", None),
    "IT": ("eleve", "tres_eleve", "elevee",
           "Épisodes méditerranéens intenses au nord et au centre ; "
           "Émilie-Romagne 2023."),
    "NL": ("eleve", "eleve", "elevee",
           "Ruissellement urbain sur territoire plat : l'eau ne s'évacue pas "
           "gravitairement, elle est POMPÉE. La panne de pompage est le scénario."),
    "LU": ("eleve", "eleve", "moyenne", None),
    "FR": ("modere", "eleve", "elevee",
           "Épisodes cévenols et méditerranéens en intensification ; "
           "ruissellement urbain croissant partout ailleurs."),
    "ES": ("modere", "eleve", "elevee",
           "Moins d'épisodes, plus violents : les gouttes froides "
           "méditerranéennes concentrent des cumuls annuels en quelques heures."),
    "GB": ("modere", "eleve", "elevee", None),
    "IE": ("modere", "eleve", "moyenne", None),
    "CZ": ("modere", "eleve", "moyenne", None),
    "PL": ("modere", "eleve", "moyenne", None),
    "SK": ("modere", "eleve", "moyenne", None),
    "HU": ("modere", "eleve", "moyenne", None),
    "HR": ("modere", "eleve", "moyenne", None),
    "RO": ("modere", "eleve", "moyenne", None),
    "BG": ("modere", "eleve", "moyenne", None),
    "GR": ("modere", "eleve", "moyenne", None),
    "PT": ("modere", "eleve", "moyenne", None),
    "DK": ("modere", "eleve", "moyenne", None),
    "SE": ("modere", "eleve", "moyenne",
           "Les précipitations hivernales augmentent le plus fortement aux "
           "hautes latitudes — le signal nordique est de hausse, pas de calme."),
    "NO": ("modere", "eleve", "elevee",
           "Parmi les hausses de précipitations extrêmes les plus marquées "
           "d'Europe, sur un relief à réponse rapide."),
    "FI": ("modere", "eleve", "moyenne", None),
    "EE": ("modere", "eleve", "faible", None),
    "LV": ("modere", "eleve", "faible", None),
    "LT": ("modere", "eleve", "faible", None),
}

# ── GLISSEMENT DE TERRAIN ──────────────────────────────────────────────────
# Deux moteurs distincts : la pluie intense partout, et la dégradation du
# pergélisol au-dessus d'environ 2 500 mètres — laquelle déstabilise des
# versants tenus depuis la dernière glaciation. Le second moteur ne concerne
# que l'arc alpin et scandinave, et il est irréversible à échelle humaine.
GLISSEMENT = {
    "CH": ("eleve", "tres_eleve", "elevee",
           "Dégradation du pergélisol de haute altitude : des versants stables "
           "depuis des millénaires entrent en mouvement. Aléa très localisé — la "
           "classe nationale ne dit rien d'un site de plaine."),
    "AT": ("eleve", "tres_eleve", "elevee", "Même mécanisme alpin."),
    "LI": ("eleve", "tres_eleve", "moyenne", None),
    "NO": ("eleve", "tres_eleve", "elevee",
           "Deux aléas superposés : versants raides et pluies en hausse, et "
           "argiles sensibles (quick clay) qui peuvent se liquéfier — le "
           "glissement de Gjerdrum en 2020 s'est produit sur terrain plat."),
    "IT": ("eleve", "eleve", "elevee",
           "Le pays d'Europe où le nombre de glissements recensés est le plus "
           "élevé, Alpes et Apennins confondus."),
    "SI": ("eleve", "eleve", "moyenne", None),
    "SE": ("modere", "eleve", "moyenne",
           "Argiles sensibles des vallées du Göta älv : un aléa de PLAINE, mal "
           "anticipé parce qu'il ne ressemble pas à un glissement de montagne."),
    "FR": ("modere", "eleve", "moyenne", "Alpes, Pyrénées, coteaux argileux du bassin parisien."),
    "ES": ("modere", "eleve", "moyenne", None),
    "PT": ("modere", "modere", "moyenne",
           "Aggravé après incendie : un versant brûlé perd sa capacité de "
           "rétention pour plusieurs saisons."),
    "GR": ("modere", "eleve", "moyenne", None),
    "HR": ("modere", "eleve", "moyenne", None),
    "RO": ("modere", "eleve", "moyenne", "Carpates et coteaux subcarpatiques."),
    "BG": ("modere", "eleve", "moyenne", None),
    "SK": ("modere", "eleve", "moyenne", None),
    "CZ": ("modere", "modere", "faible", None),
    "DE": ("faible", "modere", "moyenne", "Concentré sur les versants alpins et de moyenne montagne."),
    "PL": ("faible", "modere", "faible", "Carpates polonaises."),
    "GB": ("faible", "modere", "moyenne", "Falaises côtières en recul et remblais ferroviaires anciens."),
    "IE": ("faible", "modere", "faible", "Coulées de tourbe sur versants saturés."),
    "HU": ("faible", "modere", "faible", None),
    "FI": ("faible", "modere", "faible", None),
    "LU": ("faible", "faible", "faible", None),
    "BE": ("faible", "faible", "faible", None),
    "NL": ("faible", "faible", "elevee", "Territoire plat — l'aléa n'a pas de support."),
    "DK": ("faible", "faible", "moyenne", None),
    "EE": ("faible", "faible", "faible", None),
    "LV": ("faible", "faible", "faible", None),
    "LT": ("faible", "faible", "faible", None),
}

# ── ÉTIAGE ET RÉGIME DES COURS D'EAU ───────────────────────────────────────
# Ce que le WEI+ ne dit pas : il mesure la PRESSION MOYENNE annuelle. Un
# refroidissement en eau de rivière ne se dimensionne pas sur une moyenne, il
# se dimensionne sur l'étiage quinquennal. La projection est ici plus sévère
# que l'état actuel dans presque toute l'Europe centrale.
HYDROLOGIE = {
    "ES": ("tres_eleve", "tres_eleve", "elevee", None),
    "PT": ("tres_eleve", "tres_eleve", "elevee", None),
    "GR": ("tres_eleve", "tres_eleve", "elevee", None),
    "IT": ("eleve", "tres_eleve", "elevee",
           "Étiages du Pô en aggravation ; l'apport glaciaire alpin qui les "
           "soutenait décline."),
    "BG": ("eleve", "eleve", "moyenne", None),
    "RO": ("eleve", "eleve", "moyenne", "Bas Danube en étiage estival prolongé."),
    "HU": ("eleve", "eleve", "elevee",
           "Dépendance quasi totale à des débits produits hors du territoire — "
           "une vulnérabilité de nature géopolitique autant qu'hydrologique."),
    "FR": ("modere", "eleve", "elevee",
           "Étiages plus précoces et plus longs sur la Loire, la Garonne et le "
           "Rhône — les trois bassins qui refroidissent le parc nucléaire."),
    "DE": ("modere", "eleve", "elevee",
           "Le Rhin de 2018 et de 2022 : navigation interrompue et refroidissement "
           "contraint sans qu'aucun arrêté sécheresse ne soit nécessaire."),
    "NL": ("modere", "eleve", "elevee",
           "Aval du Rhin : le pays subit un débit qu'il ne produit pas, et la "
           "baisse du débit fait remonter le biseau salé."),
    "CH": ("modere", "eleve", "moyenne",
           "Le pic d'eau glaciaire : le débit d'été soutenu par la fonte "
           "atteint un maximum puis décroît durablement. L'avantage hydrologique "
           "suisse est réel aujourd'hui et daté."),
    "AT": ("modere", "eleve", "moyenne", "Même mécanisme glaciaire, moindre ampleur."),
    "LI": ("modere", "eleve", "faible", None),
    "SI": ("modere", "eleve", "moyenne", None),
    "HR": ("modere", "eleve", "moyenne", None),
    "CZ": ("modere", "eleve", "elevee",
           "Pays de partage des eaux : presque aucun débit n'y entre, tout en "
           "sort. Il n'y a pas d'amont sur lequel compter."),
    "SK": ("modere", "eleve", "moyenne", None),
    "PL": ("modere", "eleve", "elevee", None),
    "BE": ("modere", "eleve", "moyenne", "Meuse — régime pluvial, étiages sévères."),
    "LU": ("modere", "eleve", "faible", None),
    "GB": ("modere", "eleve", "moyenne", "Bassins du sud-est, à faible soutien d'étiage."),
    "DK": ("modere", "modere", "moyenne", None),
    "IE": ("faible", "modere", "moyenne", None),
    "EE": ("faible", "modere", "faible", None),
    "LV": ("faible", "modere", "faible", None),
    "LT": ("faible", "modere", "faible", None),
    "SE": ("faible", "faible", "elevee",
           "Régime nival : le débit annuel augmente, le pic se déplace vers "
           "l'hiver. L'étiage estival du sud reste le point à surveiller."),
    "FI": ("faible", "faible", "elevee", None),
    "NO": ("faible", "faible", "elevee",
           "Débits en hausse ; c'est l'hydrologie la plus confortable d'Europe "
           "pour un refroidissement en eau."),
}

TABLES = {
    "submersion": SUBMERSION,
    "feu": FEU,
    "secheresse": SECHERESSE,
    "pluie": PLUIE,
    "glissement": GLISSEMENT,
    "hydrologie": HYDROLOGIE,
}

SOURCE_ALEAS = {
    "titre": "Classes d'exposition aux aléas climatiques, horizons 2030 et 2050",
    "editeur": "Synthèse CONSEILPREV d'après GIEC AR6 (groupes I et II, "
               "chapitre Europe), Agence européenne pour l'environnement "
               "(European Climate Risk Assessment, indicateurs d'aléas) et "
               "JRC PESETA IV",
    "nature": "analyse",
    "note": "CLASSES nationales à cinq crans, pas des valeurs modélisées. Elles "
            "traduisent le sens et le niveau RELATIF sur lesquels les "
            "évaluations concordent ; elles n'ont pas la résolution d'une étude "
            "d'aléa et ne s'y substituent pas. La confiance est portée case par "
            "case. La classe nationale écrase des contrastes régionaux qui, "
            "dans plusieurs pays, dépassent l'écart entre pays.",
}

# ═══════════════════════════════════════════════════════════════════════════
# 5. CONTRÔLE D'INTÉGRITÉ AU CHARGEMENT
#
#    Ce module a une exception à la règle « l'absence n'est jamais une bonne
#    note ». Une exception non gardée finit toujours par s'étendre : celle-ci
#    est donc vérifiée à l'import, et le module refuse de se charger si elle
#    déborde. Mieux vaut un service qui ne démarre pas qu'un comparateur qui
#    décerne un 100 silencieux.
# ═══════════════════════════════════════════════════════════════════════════

def _verifier_tables():
    fautes = []
    pays_par_table = {a: set(t) for a, t in TABLES.items()}
    reference = pays_par_table["submersion"]
    for alea, table in TABLES.items():
        for pays, v in table.items():
            if len(v) != 4:
                fautes.append("%s/%s : %d champs au lieu de 4" % (alea, pays, len(v)))
                continue
            n30, n50, conf, _ = v
            for n in (n30, n50):
                if n not in NIVEAUX:
                    fautes.append("%s/%s : niveau inconnu %r" % (alea, pays, n))
                # LE contrôle central de ce fichier.
                if n == "sans_objet":
                    if alea != "submersion":
                        fautes.append("%s/%s : `sans_objet` interdit hors submersion"
                                      % (alea, pays))
                    if pays not in ENCLAVES:
                        fautes.append("%s/%s : `sans_objet` sur un pays à littoral"
                                      % (alea, pays))
            if conf not in CONFIANCES:
                fautes.append("%s/%s : confiance inconnue %r" % (alea, pays, conf))
        manquants = reference - pays_par_table[alea]
        if manquants:
            fautes.append("%s : pays sans classe — %s" % (alea, sorted(manquants)))
    # Un pays enclavé DOIT porter `sans_objet` en submersion : l'oubli
    # produirait une classe d'exposition côtière pour un pays sans côte.
    for pays in ENCLAVES:
        v = SUBMERSION.get(pays)
        if v and v[0] != "sans_objet":
            fautes.append("submersion/%s : pays enclavé sans `sans_objet`" % pays)
    return fautes


_FAUTES = _verifier_tables()
if _FAUTES:
    raise RuntimeError("climat_2050 — tables incohérentes : " + " ; ".join(_FAUTES))

PAYS = sorted(SUBMERSION)

# ═══════════════════════════════════════════════════════════════════════════
# 6. LECTURE
# ═══════════════════════════════════════════════════════════════════════════

def _niveau(alea, pays, horizon):
    """La classe d'un pays pour un aléa à un horizon, ou None s'il n'est pas
    au référentiel — jamais une classe par défaut."""
    v = TABLES[alea].get(pays)
    if not v:
        return None
    return v[1] if int(horizon) >= 2050 else v[0]


def alea_de(pays, alea, horizon=2030):
    """La fiche d'un aléa pour un pays, ou None si le pays est hors référentiel."""
    v = TABLES[alea].get(pays)
    if not v:
        return None
    n30, n50, conf, note = v
    n = n50 if int(horizon) >= 2050 else n30
    return {
        "alea": alea,
        "nom": ALEAS[alea]["nom"],
        "horizon": int(horizon),
        "niveau": n,
        "niveau_nom": NIVEAUX[n]["nom"],
        "note": NIVEAUX[n]["note"],
        "sens": NIVEAUX[n]["sens"],
        "niveau_2030": n30,
        "niveau_2050": n50,
        # Une classe qui monte entre les deux horizons est l'information que le
        # référentiel XDI ne pouvait pas porter : il n'a qu'une date.
        "aggravation": NIVEAUX[n50]["rang"] - NIVEAUX[n30]["rang"],
        "confiance": conf,
        "confiance_nom": CONFIANCES[conf]["nom"],
        "commentaire": note,
        "atteint": ALEAS[alea]["atteint"],
    }


def aleas_de(pays, horizon=2030):
    """Les six aléas d'un pays, ou None si le pays est hors référentiel."""
    if pays not in TABLES["submersion"]:
        return None
    return {a: alea_de(pays, a, horizon) for a in ALEAS}


def note_climat(pays, horizon=2030):
    """0-100, plus haut = moins exposé — moyenne des six aléas.

    Le `sans_objet` d'un pays enclavé compte pour 100 : ne PAS avoir de mer est
    un avantage réel et permanent face à la submersion, et l'écarter du calcul
    reviendrait à ne pas en tenir compte. C'est la seule note favorable que ce
    module attribue à une case sans valeur mesurée, et elle est verrouillée par
    le contrôle d'intégrité.
    """
    if pays not in TABLES["submersion"]:
        return None
    notes = [NIVEAUX[_niveau(a, pays, horizon)]["note"] for a in ALEAS]
    return round(sum(notes) / len(notes))


def note_alea(pays, alea, horizon=2030):
    """0-100 pour UN aléa — ce qui permet de le pondérer séparément."""
    n = _niveau(alea, pays, horizon)
    return NIVEAUX[n]["note"] if n else None


def mer(horizon=2050, scenario="SSP2-4.5"):
    """L'élévation du niveau moyen mondial de la mer, telle que publiée."""
    h = int(horizon)
    if h <= 2030:
        return {"horizon": 2030, "scenario": "tous",
                "mediane_m": MER_2030["valeur_m"], "plage_m": None,
                "nature": MER_2030["nature"], "methode": MER_2030["methode"],
                "reserve": MER_2030["reserve"]}
    h = 2050 if h <= 2075 else 2100
    med, bas, haut = MER[scenario][h]
    return {"horizon": h, "scenario": scenario,
            "scenario_sens": MER_SCENARIOS[scenario],
            "mediane_m": med, "plage_m": [bas, haut],
            "nature": "referentiel", "source": SOURCE_MER["editeur"]}


def ecart_scenarios(horizon=2050):
    """De combien le CHOIX collectif d'émissions change le résultat.

    C'est le calcul qui désamorce le faux débat : à 2050 il vaut quatre
    centimètres, à 2100 trente-trois. Avant le milieu du siècle, aucun scénario
    ne protège — l'élévation est déjà engagée."""
    h = 2050 if int(horizon) <= 2075 else 2100
    bas = MER["SSP1-2.6"][h][0]
    haut = MER["SSP5-8.5"][h][0]
    return {"horizon": h, "sobre_m": bas, "emetteur_m": haut,
            "ecart_m": round(haut - bas, 2),
            "lecture": ("À cet horizon, la trajectoire d'émissions ne change que "
                        "%d cm : l'élévation est déjà engagée." % round((haut - bas) * 100)
                        if h == 2050 else
                        "À cet horizon, la trajectoire d'émissions change %d cm : "
                        "le choix collectif devient déterminant."
                        % round((haut - bas) * 100))}


def mer_locale(pays):
    """La correction verticale du sol, ou None si aucune n'est documentée ici."""
    v = MER_LOCAL.get(pays)
    if not v:
        return None
    mm, note = v
    return {"mouvement_mm_an": mm,
            "sens": "relèvement du sol" if mm > 0 else "enfoncement du sol",
            "commentaire": note}


def pires(alea, horizon=2050, n=5):
    """Les pays les plus exposés à un aléa — pour désigner, pas pour classer."""
    lignes = [(p, NIVEAUX[_niveau(alea, p, horizon)]["rang"]) for p in PAYS
              if _niveau(alea, p, horizon)]
    lignes.sort(key=lambda x: (-x[1], x[0]))
    return [p for p, _ in lignes[:n]]


def dominants(pays, horizon=2030):
    """LES aléas au niveau le plus haut — au pluriel, et c'est délibéré.

    Rendre « l'aléa dominant » au singulier obligerait à départager des
    ex æquo, et le départage se ferait sur l'ordre du dictionnaire : la France
    afficherait « feu » et l'Allemagne « pluie » pour la seule raison que ces
    clés sont écrites dans cet ordre. Quand quatre aléas sont au même niveau,
    l'information est qu'il y en a quatre.
    """
    fiches = aleas_de(pays, horizon)
    if not fiches:
        return None
    haut = max(NIVEAUX[f["niveau"]]["rang"] for f in fiches.values())
    return sorted(a for a, f in fiches.items()
                  if NIVEAUX[f["niveau"]]["rang"] == haut)


def sature(pays, alea):
    """Un aléa déjà au cran maximal en 2030 ne peut PAS montrer d'aggravation.

    L'échelle a cinq crans : le Portugal est « très élevé » au feu dès 2030,
    donc son écart 2030-2050 vaut zéro. Lire ce zéro comme « rien n'empire »
    serait le contresens exact — c'est l'échelle qui bute, pas l'aléa qui se
    calme. Ce drapeau existe pour que l'affichage puisse le dire.
    """
    v = TABLES[alea].get(pays)
    return bool(v) and v[0] == "tres_eleve"


def aggravations(horizon=2050):
    """Où la classe MONTE entre 2030 et 2050, aléa par aléa. C'est ce que le
    comparateur ne pouvait pas montrer avec une seule date."""
    out = []
    for a in ALEAS:
        for p in PAYS:
            v = TABLES[a].get(p)
            if not v:
                continue
            d = NIVEAUX[v[1]]["rang"] - NIVEAUX[v[0]]["rang"]
            if d > 0:
                out.append({"pays": p, "alea": a, "alea_nom": ALEAS[a]["nom"],
                            "de": v[0], "vers": v[1], "crans": d})
    out.sort(key=lambda x: (-x["crans"], x["pays"], x["alea"]))
    return out


def assemble(horizon=2030):
    """Le référentiel complet, prêt à afficher."""
    h = int(horizon)
    lignes = []
    for p in PAYS:
        fiches = aleas_de(p, h)
        lignes.append({
            "pays": p,
            "note": note_climat(p, h),
            "note_2030": note_climat(p, 2030),
            "note_2050": note_climat(p, 2050),
            "aleas": fiches,
            "mer_locale": mer_locale(p),
            # Les aléas au plus haut niveau — ce qu'il faut regarder EN PREMIER.
            "dominants": dominants(p, h),
            # Les aléas déjà au maximum en 2030 : leur écart nul ne dit pas que
            # rien n'empire, il dit que l'échelle bute.
            "satures": sorted(a for a in ALEAS if sature(p, a)),
            "sans_objet": sorted(a for a in ALEAS
                                 if (TABLES[a].get(p) or (None,))[0] == "sans_objet"),
        })
    lignes.sort(key=lambda x: (-(x["note"] or 0), x["pays"]))
    return {
        "version": VERSION,
        "genere": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "horizon": h,
        "horizons": list(HORIZONS),
        "aleas": ALEAS,
        "niveaux": NIVEAUX,
        "confiances": CONFIANCES,
        "pays": lignes,
        "mer": mer(h),
        "mer_ecart": ecart_scenarios(h),
        "mer_scenarios": {s: {**mer(2050, s), "en_2100": mer(2100, s)}
                          for s in MER},
        "aggravations": aggravations(),
        # Le nombre de cases déjà au maximum en 2030 : la mesure de ce que
        # l'échelle ne peut plus exprimer.
        "satures": sum(1 for a in ALEAS for p in PAYS if sature(p, a)),
        "sources": {"aleas": SOURCE_ALEAS, "mer": SOURCE_MER,
                    "mer_locale": SOURCE_MER_LOCAL},
        "avertissement":
            "Classes NATIONALES d'exposition, issues d'une synthèse d'évaluations "
            "publiées — pas de valeurs modélisées par site. Elles servent à "
            "écarter des pays et à ordonner des questions, jamais à dimensionner "
            "un ouvrage. Toute décision de terrain exige l'étude d'aléa locale et "
            "le plan de prévention des risques applicable.",
    }


def sante():
    """Ce qui est couvert, ce qui ne l'est pas, et ce qui repose sur peu."""
    faibles = [(a, p) for a in ALEAS for p in PAYS
               if TABLES[a].get(p) and TABLES[a][p][2] == "faible"]
    total = len(ALEAS) * len(PAYS)
    return {
        "module": "climat_2050", "version": VERSION,
        "pays": len(PAYS), "aleas": len(ALEAS),
        "cases": total,
        "confiance_faible": len(faibles),
        "part_confiance_faible_pct": round(100.0 * len(faibles) / total),
        "enclaves": len([p for p in PAYS if p in ENCLAVES]),
        "aggravations_2050": len(aggravations()),
        "problemes": _verifier_tables(),
    }
