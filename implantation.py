# -*- coding: utf-8 -*-
"""Choix d'implantation d'un centre de données — référentiel PAR PAYS.

CE QUE CE MODULE AJOUTE, ET POURQUOI ICI
Le référentiel des sites (datacentres.py) dit OÙ est le parc et à quel stade.
L'empreinte (empreinte_sites.py) dit ce que pèse l'électricité de chaque pays.
Aucun des deux ne répond à la question de l'investisseur : « où IMPLANTER ? ».
Ce module porte les quatre critères qui manquaient — l'eau, le mix de
production, le prix de l'électricité, les perspectives à 2030 — et l'analyse
AVANTAGES / INCONVÉNIENTS par pays qui les croise.

LA RÈGLE DE FIABILITÉ, LA MÊME QUE PARTOUT AILLEURS SUR CETTE PAGE
Chaque valeur porte sa NATURE. Trois natures ici :
  referentiel   valeur d'une source publique nommée, avec millésime — à
                re-vérifier à la source primaire avant toute décision ;
  calcule       dérivée de nos propres données (le pipeline 2026-2030 est
                compté depuis les statuts des 97 sites cartographiés) ;
  analyse       lecture rédactionnelle du cabinet, datée — un avis, pas une
                donnée. Les avantages/inconvénients sont de cette nature.
Les prix et les mix sont donnés en CLASSES et en FOURCHETTES LARGES : un
ordre de grandeur honnête vaut mieux qu'une précision empruntée. Chaque
famille de valeurs est inscrite au registre de vérification (factcheck.py).

AVERTISSEMENT — le même que sur la carte : ce référentiel SITUE et COMPARE
des pays ; il ne chiffre pas un site, ne remplace ni une étude de réseau, ni
une étude hydrologique locale, ni une due diligence.
"""
from datetime import datetime, timezone

VERSION = "2026-08-b"

# ═══════════════════════════════════════════════════════════════════════════
# 1. EAU — stress hydrique national et compétition d'usages
#
#    Source : indice d'exploitation de l'eau WEI+ de l'Agence européenne pour
#    l'environnement (AEE), millésime 2022 (dernier publié), lu au niveau
#    NATIONAL. Un WEI+ au-delà de 20 % signale un stress, au-delà de 40 % un
#    stress sévère. La lecture nationale ÉCRASE les contrastes : l'Espagne
#    « stress élevé » a des bassins atlantiques détendus, la France « stress
#    modéré » a des bassins méditerranéens en crise estivale. D'où la note de
#    bassins, et la part de l'IRRIGATION : là où l'agriculture prélève plus de
#    la moitié de l'eau, un refroidissement évaporatif entre en compétition
#    d'usage l'été — précisément quand il consomme le plus.
# ═══════════════════════════════════════════════════════════════════════════

EAU_CLASSES = {
    "faible": {"nom": "Stress faible", "note": 90,
               "sens": "WEI+ national sous ~10 % — la ressource n'est pas le sujet dominant"},
    "modere": {"nom": "Stress modéré", "note": 55,
               "sens": "WEI+ national ~10-20 % ou bassins localement tendus l'été"},
    "eleve": {"nom": "Stress élevé", "note": 20,
              "sens": "WEI+ national au-delà de ~20 % — l'eau conditionne le permis et le mode de refroidissement"},
}

EAU = {
    # pays: (classe, part approx. de l'agriculture dans les prélèvements, note de bassins)
    "SE": ("faible", "~5 %", "ressource abondante ; enjeu limité aux étés secs du sud"),
    "NO": ("faible", "~1 %", "hydrologie excédentaire"),
    "FI": ("faible", "~2 %", "ressource abondante"),
    "DK": ("modere", "~25 %", "eau souterraine sollicitée ; étés secs récurrents"),
    "IE": ("faible", "~2 %", "ressource abondante ; l'enjeu irlandais est le réseau électrique, pas l'eau"),
    "GB": ("modere", "~10 %", "sud-est de l'Angleterre classé « seriously water stressed » par l'Environment Agency"),
    "FR": ("modere", "~45 %", "bassins méditerranéens et sud-ouest en tension estivale ; arrêtés sécheresse fréquents"),
    "BE": ("eleve", "~15 %", "Flandre parmi les régions les plus tendues d'Europe (faible ressource par habitant)"),
    "NL": ("modere", "~30 %", "gestion fine mais dépendance au Rhin et à la Meuse ; salinisation à l'ouest"),
    "DE": ("modere", "~20 %", "bassins de l'est (Brandebourg, autour de Berlin) déjà en conflit d'usage documenté"),
    "PL": ("modere", "~30 %", "ressource par habitant parmi les plus faibles d'Europe ; refroidissement des centrales déjà contraint en canicule"),
    "CZ": ("modere", "~10 %", "sécheresses récurrentes depuis 2015"),
    "AT": ("faible", "~5 %", "ressource alpine abondante"),
    "ES": ("eleve", "~60 %", "irrigation dominante ; bassins du sud et de l'est en stress structurel — l'évaporatif y est un sujet de permis"),
    "PT": ("eleve", "~60 %", "sud en stress structurel ; nord atlantique plus détendu"),
    "IT": ("eleve", "~50 %", "Pô en sécheresse historique 2022 ; contraste nord irrigué / sud aride"),
    "GR": ("eleve", "~80 %", "irrigation très dominante ; stress estival généralisé"),
    "BG": ("modere", "~40 %", "infrastructures vieillissantes, pertes réseau élevées"),
    "RO": ("modere", "~40 %", "tension sur le bas Danube en été"),
    "HU": ("modere", "~30 %", "dépendance quasi totale aux fleuves entrants"),
    "HR": ("faible", "~10 %", "ressource abondante"),
    "SI": ("faible", "~5 %", "ressource alpine"),
    "LU": ("modere", "~5 %", "petite ressource, dépendance amont"),
}

SOURCE_EAU = {
    "titre": "Water exploitation index plus (WEI+) — millésime 2022",
    "editeur": "Agence européenne pour l'environnement (AEE)",
    "url": "https://www.eea.europa.eu/en/analysis/indicators/use-of-freshwater-resources-in-europe",
    "nature": "referentiel",
    "note": "Classes nationales ; la réalité est un contraste de BASSINS — toute "
            "décision de site exige l'étude du bassin versant et du plan "
            "sécheresse locaux. Part de l'irrigation : ordres de grandeur "
            "AEE/FAO AQUASTAT.",
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. MIX DE PRODUCTION ÉLECTRIQUE — d'où vient le kilowattheure
#
#    Source : Ember, année 2024, parts de la PRODUCTION nationale, arrondies
#    à 5 points — la précision décimale serait un mensonge de confort ici.
#    Le mix explique l'intensité carbone (empreinte_sites.py) et dit autre
#    chose qu'elle : un pays nucléaire (FR) et un pays éolien (DK) peuvent
#    afficher des intensités voisines avec des profils de PRIX et de
#    DISPONIBILITÉ opposés — le nucléaire est pilotable, l'éolien expose au
#    profil de vent et au prix de couverture des creux.
# ═══════════════════════════════════════════════════════════════════════════

MIX = {
    # pays: {nucleaire, renouvelables, fossile} en % de la production 2024, arrondi a 5
    "FR": {"nucleaire": 65, "renouvelables": 30, "fossile": 5},
    "SE": {"nucleaire": 30, "renouvelables": 70, "fossile": 0},
    "NO": {"nucleaire": 0, "renouvelables": 100, "fossile": 0},
    "FI": {"nucleaire": 40, "renouvelables": 50, "fossile": 10},
    "DK": {"nucleaire": 0, "renouvelables": 85, "fossile": 15},
    "IE": {"nucleaire": 0, "renouvelables": 40, "fossile": 60},
    "GB": {"nucleaire": 15, "renouvelables": 45, "fossile": 40},
    "NL": {"nucleaire": 5, "renouvelables": 50, "fossile": 45},
    "BE": {"nucleaire": 40, "renouvelables": 30, "fossile": 30},
    "DE": {"nucleaire": 0, "renouvelables": 60, "fossile": 40},
    "PL": {"nucleaire": 0, "renouvelables": 30, "fossile": 70},
    "CZ": {"nucleaire": 40, "renouvelables": 15, "fossile": 45},
    "AT": {"nucleaire": 0, "renouvelables": 85, "fossile": 15},
    "ES": {"nucleaire": 20, "renouvelables": 55, "fossile": 25},
    "PT": {"nucleaire": 0, "renouvelables": 70, "fossile": 30},
    "IT": {"nucleaire": 0, "renouvelables": 40, "fossile": 60},
    "GR": {"nucleaire": 0, "renouvelables": 45, "fossile": 55},
    "BG": {"nucleaire": 40, "renouvelables": 25, "fossile": 35},
    "RO": {"nucleaire": 20, "renouvelables": 45, "fossile": 35},
    "HU": {"nucleaire": 45, "renouvelables": 25, "fossile": 30},
    "HR": {"nucleaire": 0, "renouvelables": 60, "fossile": 40},
    "SI": {"nucleaire": 35, "renouvelables": 35, "fossile": 30},
    "LU": {"nucleaire": 0, "renouvelables": 90, "fossile": 10},
}

SOURCE_MIX = {
    "titre": "Yearly electricity generation — parts de production 2024, arrondies à 5 points",
    "editeur": "Ember",
    "url": "https://ember-energy.org/data/yearly-electricity-data/",
    "nature": "referentiel",
    "note": "Production NATIONALE : un pays importateur consomme un mix différent "
            "de celui qu'il produit (Luxembourg surtout). Le profil pilotable / "
            "intermittent compte autant que la part renouvelable — un centre de "
            "données consomme 8 760 h par an, pas seulement quand il vente.",
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. PRIX DE L'ÉLECTRICITÉ — grands consommateurs industriels
#
#    Source : Eurostat (nrg_pc_205), bandes de consommation industrielles
#    hautes, hors taxes récupérables, année 2024. Donné en CLASSE et en
#    FOURCHETTE LARGE (€/MWh) : le prix pertinent pour un centre de données
#    est un prix NÉGOCIÉ (PPA, tarif de raccordement, exonérations) que la
#    statistique publique ne voit pas. La classe dit le terrain de départ de
#    la négociation, rien de plus.
# ═══════════════════════════════════════════════════════════════════════════

PRIX_CLASSES = {
    "bas": {"nom": "Bas", "note": 85, "sens": "sous ~100 €/MWh en bande industrielle haute"},
    "moyen": {"nom": "Moyen", "note": 55, "sens": "~100-150 €/MWh"},
    "eleve": {"nom": "Élevé", "note": 25, "sens": "au-delà de ~150 €/MWh"},
}

PRIX = {
    # pays: (classe, fourchette €/MWh donnée à titre d'ordre de grandeur)
    "SE": ("bas", (50, 90)), "NO": ("bas", (45, 85)), "FI": ("bas", (60, 100)),
    "DK": ("bas", (70, 110)), "FR": ("moyen", (95, 140)), "ES": ("bas", (75, 115)),
    "PT": ("moyen", (85, 125)), "NL": ("moyen", (110, 150)), "BE": ("moyen", (100, 145)),
    "DE": ("eleve", (150, 210)), "IE": ("eleve", (160, 230)), "GB": ("eleve", (170, 250)),
    "IT": ("eleve", (140, 200)), "PL": ("eleve", (140, 190)), "CZ": ("moyen", (120, 170)),
    "AT": ("moyen", (110, 160)), "GR": ("moyen", (120, 170)), "BG": ("moyen", (90, 140)),
    "RO": ("moyen", (110, 160)), "HU": ("moyen", (110, 160)), "HR": ("moyen", (110, 160)),
    "SI": ("moyen", (110, 160)), "LU": ("moyen", (110, 155)),
}

SOURCE_PRIX = {
    "titre": "Electricity prices for non-household consumers — bandes hautes, 2024",
    "editeur": "Eurostat (nrg_pc_205)",
    "url": "https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_205/",
    "nature": "referentiel",
    "note": "Classes et fourchettes d'ordre de grandeur, hors taxes récupérables. "
            "Le prix réel d'un centre de données est contractuel (PPA, "
            "raccordement, exonérations) : la statistique publique donne le "
            "terrain de départ, jamais le prix payé.",
}

# ═══════════════════════════════════════════════════════════════════════════
# 4. PERSPECTIVES 2026 → 2030 — annonces d'investissement et contraintes
#
#    Nature « analyse » : des ANNONCES datées, avec leur source, jamais des
#    engagements comptables. La règle du référentiel des sites s'applique en
#    plus fort ici : une annonce à cinq ans est l'information la plus fragile
#    qui existe sur ce marché. Les CONTRAINTES (moratoires) sont, elles,
#    des décisions constatées — souvent plus fiables que les promesses.
# ═══════════════════════════════════════════════════════════════════════════

PERSPECTIVES = [
    {"pays": "UE", "sens": "hausse",
     "resume": "Programme InvestAI : 200 Md€ d'investissements IA mobilisés, dont 20 Md€ "
               "pour des gigafactories d'IA (5 annoncées).",
     "source": "Commission européenne", "date": "2025-02"},
    {"pays": "FR", "sens": "hausse",
     "resume": "109 Md€ d'investissements IA annoncés au Sommet pour l'action sur l'IA "
               "(dont campus ~1 GW soutenu par les Émirats, Brookfield ~20 Md€).",
     "source": "Élysée / Sommet IA de Paris", "date": "2025-02"},
    {"pays": "ES", "sens": "hausse",
     "resume": "AWS en Aragon : 15,7 Md€ annoncés en 2024, portés à plus de 30 Md€ en "
               "2025 ; Microsoft en Aragon et à Madrid.",
     "source": "communiqués AWS / Microsoft, gouvernement d'Aragon", "date": "2024-06 → 2025"},
    {"pays": "ES", "sens": "contrainte",
     "resume": "L'Aragon est devenu en partie victime de son succès : le raccordement au "
               "réseau y forme désormais un goulet d'étranglement, et des agriculteurs "
               "imputent aux centres de données les pénuries d'eau — un permis rapide n'y "
               "est plus un raccordement rapide.",
     "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 22",
     "date": "2025"},
    {"pays": "DE", "sens": "hausse",
     "resume": "Microsoft ~3,2 Md€ (2024) ; cloud d'IA industrielle Deutsche "
               "Telekom / NVIDIA (2025) ; Rhénanie et Brandebourg en tête.",
     "source": "communiqués Microsoft / Deutsche Telekom", "date": "2024 → 2025"},
    {"pays": "GB", "sens": "hausse",
     "resume": "Trois premières « AI Growth Zones » désignées — Oxfordshire, Nord-Est "
               "de l'Angleterre, Nord du pays de Galles — avec accès prioritaire au "
               "réseau et instruction accélérée ; parmi les plus gros pipelines d'Europe.",
     "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 30 ; "
               "gouvernement britannique", "date": "2025"},
    {"pays": "IT", "sens": "hausse",
     "resume": "Microsoft ~4,3 Md€ pour l'IA et le cloud (2024) ; les projets planifiés "
               "à Milan porteraient la capacité de 200 MW à 2 GW, soit un facteur dix, "
               "avec récupération de chaleur au programme.",
     "source": "communiqué Microsoft ; Soben (part of Accenture), Data Centre Trends "
               "Report 2026, p. 31", "date": "2024-10 → 2025"},
    {"pays": "SE", "sens": "hausse",
     "resume": "Microsoft ~3,2 Md$ (2024) ; attractivité durable du réseau bas-carbone "
               "et du free cooling.",
     "source": "communiqué Microsoft", "date": "2024-06"},
    {"pays": "SE", "sens": "hausse",
     "resume": "Incitations fiscales (comme la Norvège) et instruction des permis "
               "simplifiée pour les projets hyperscale — le levier porte sur le "
               "calendrier, celui qui commande tout le reste.",
     "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 30",
     "date": "2025"},
    {"pays": "FR", "sens": "hausse",
     "resume": "Marseille s'affirme comme hub de connectivité méditerranéen : câbles "
               "sous-marins vers l'Europe, l'Afrique, le Moyen-Orient et l'Asie, "
               "atterrissage du câble Medusa d'Orange en octobre 2025.",
     "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 31",
     "date": "2025-10"},
    {"pays": "IE", "sens": "hausse",
     "resume": "Une loi autorise désormais les centres de données à produire leur "
               "propre électricité — une voie qui contourne la file de raccordement. "
               "L'obtention des autorisations correspondantes reste difficile.",
     "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 30",
     "date": "2025"},
    {"pays": "NO", "sens": "hausse",
     "resume": "Projet « Stargate Norway » (OpenAI / Nscale / Aker) annoncé en 2025 : "
               "capacité IA de grande échelle sur hydroélectricité.",
     "source": "communiqués OpenAI / Aker", "date": "2025"},
    {"pays": "PL", "sens": "hausse",
     "resume": "Microsoft (~700 M$) et Google : croissance rapide depuis une base "
               "faible ; l'intensité carbone du réseau, très élevée, baisse vite.",
     "source": "communiqués opérateurs", "date": "2024 → 2025"},
    {"pays": "IE", "sens": "contrainte",
     "resume": "Moratoire de fait sur les nouveaux raccordements de centres de données "
               "dans la région de Dublin (EirGrid), reconduit jusqu'à la fin de la "
               "décennie ; croissance reportée hors Dublin.",
     "source": "EirGrid / CRU", "date": "2022 → maintenu"},
    {"pays": "NL", "sens": "contrainte",
     "resume": "Encadrement national des implantations hyperscale depuis 2022 "
               "(après Zeewolde) ; extensions soumises à conditions strictes.",
     "source": "gouvernement néerlandais", "date": "2022 → maintenu"},
    {"pays": "NL", "sens": "contrainte",
     "resume": "Le conseil municipal d'Amsterdam n'examinera de nouveaux projets de "
               "centres de données qu'à partir de 2035 : l'un des cinq hubs "
               "historiques est fermé de fait pour une décennie.",
     "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 30",
     "date": "2035"},
    {"pays": "DE", "sens": "contrainte",
     "resume": "Loi d'efficacité énergétique (EnEfG) : PUE maximal imposé aux "
               "nouveaux sites (1,2 dès 2026) ; réutilisation d'une part de la chaleur "
               "fatale obligatoire pour tout site mis en service à partir du "
               "1er juillet 2026, sauf réseau de chaleur hors d'atteinte.",
     "source": "EnEfG (2023) ; Soben (part of Accenture), Data Centre Trends Report "
               "2026, p. 35", "date": "2023 → 2026-07-01"},
    {"pays": "DE", "sens": "contrainte",
     "resume": "À Francfort, les projets de centres de données dédiés à l'IA sont "
               "gelés jusqu'à la mise en service de nouvelles capacités de réseau, "
               "attendues en 2031 ; la demande se reporte sur les marchés secondaires "
               "allemands et les Nordiques.",
     "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 30",
     "date": "2031"},
    {"pays": "FI", "sens": "contrainte",
     "resume": "Suppression du tarif réduit d'accise sur l'électricité des centres de "
               "données en mars 2025 : de 0,05 à 2,24 centimes par kWh, soit environ "
               "+22 €/MWh. Le pays reste compétitif, mais l'écart avec la Suède et la "
               "Norvège se resserre nettement.",
     "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 30",
     "date": "2025-03"},
    {"pays": "UE", "sens": "contrainte",
     "resume": "Déclaration de performance énergétique obligatoire depuis septembre "
               "2024 (directive 2023/1791) ; un « Data Centre Energy Efficiency "
               "Package » est annoncé pour le premier trimestre 2026, en durcissement "
               "attendu — à anticiper dans tout projet livré après 2027.",
     "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 35",
     "date": "2024-09 → 2026-T1"},
    {"pays": "UE", "sens": "hausse",
     "resume": "File de projets estimée à 351,7 milliards de dollars pour l'Europe au "
               "troisième trimestre 2025 — l'ordre de grandeur de la vague, contre "
               "lequel se mesure la capacité de raccordement de chaque pays.",
     "source": "Soben (part of Accenture), Data Centre Trends Report 2026, p. 29 "
               "(estimation Accenture)", "date": "2025-T3"},
]

SOURCE_PERSPECTIVES = {
    "titre": "Annonces d'investissement et contraintes réglementaires, horizon 2030",
    "editeur": "compilation datée du cabinet (communiqués, autorités)",
    "nature": "analyse",
    "note": "Des ANNONCES, pas des engagements : chaque ligne porte sa source et sa "
            "date, et doit être re-vérifiée avant toute décision. Les contraintes "
            "(moratoires, PUE réglementaire) sont des décisions constatées — "
            "souvent plus solides que les promesses chiffrées.",
}

# ═══════════════════════════════════════════════════════════════════════════
# 5. CLIMAT DE REFROIDISSEMENT — le déterminant physique du PUE
#    Classes latitudinales assumées grossières : le PUE d'un site se conçoit,
#    il ne se déduit pas d'une capitale. La classe dit le POTENTIEL.
# ═══════════════════════════════════════════════════════════════════════════

CLIMAT = {
    "nordique": {"nom": "Nordique — free cooling quasi permanent", "note": 90,
                 "pays": ["SE", "NO", "FI", "DK", "IS", "EE", "LV", "LT"]},
    "tempere": {"nom": "Tempéré océanique — free cooling majoritaire", "note": 65,
                "pays": ["IE", "GB", "NL", "BE", "DE", "FR", "LU", "PL", "CZ", "AT", "HU", "SI", "RO"]},
    "meridional": {"nom": "Méridional — arbitrage eau / PUE", "note": 35,
                   "pays": ["ES", "PT", "IT", "GR", "HR", "BG", "CY", "MT"]},
}

def climat_de(pays):
    for cle, c in CLIMAT.items():
        if pays in c["pays"]:
            return cle
    return "tempere"

# ═══════════════════════════════════════════════════════════════════════════
# 5 bis. RISQUE CLIMATIQUE PHYSIQUE — XDI, juin 2026
#
#    CE QUE CE BLOC AJOUTE, ET POURQUOI IL MANQUAIT. Les cinq critères
#    précédents décrivent le kilowattheure, l'eau et le prix : ce qui fait
#    tourner un centre. Aucun ne dit si le bâtiment sera encore là dans
#    quarante ans. XDI modélise, pour 2 595 centres PLANIFIÉS dans le monde,
#    la probabilité de dommage physique annuel rapporté au coût de
#    remplacement — leur métrique MVAR — sur onze aléas climatiques.
#
#    LA MESURE. Un site est « à haut risque » quand son MVAR atteint 1 % par
#    an : à ce niveau, XDI écrit que l'assurance devient « de plus en plus
#    coûteuse ou dangereusement insuffisante ». Le pourcentage retenu ici est
#    la PART des centres planifiés du pays qui franchissent ce seuil.
#
#    LES DEUX RÉGLAGES, ET CE QUE LEUR ÉCART RÉVÈLE. XDI publie deux
#    résultats : construction à faible résilience, et construction à
#    résilience avancée. L'écart entre les deux dit ce que l'ingénierie peut
#    corriger — et le RESTE dit ce qu'elle ne peut pas. En Suisse, 33 % → 0 % :
#    tout est rattrapable par la conception. En France, 26 % → 18 % : plus des
#    deux tiers du risque tient au LIEU, pas au bâtiment. C'est la différence
#    entre un surcoût d'ingénierie et une erreur d'implantation, et c'est
#    l'information la plus actionnable du rapport.
#
#    CE QUE L'ABSENCE NE SIGNIFIE PAS. XDI ne classe que les pays comptant au
#    moins trois centres planifiés analysés, et ne publie que les vingt-cinq
#    premiers. Un pays absent n'est donc pas « bon » : il est HORS CLASSEMENT,
#    et reçoit une note nulle — pas une bonne note. La Suède, la Pologne, la
#    Belgique et l'Autriche sont dans ce cas.
# ═══════════════════════════════════════════════════════════════════════════

XDI_ALEAS = {
    "submersion": "Submersion côtière",
    "crue": "Crue de rivière",
    "ruissellement": "Ruissellement pluvial",
}

# pays : (rang mondial, centres planifiés analysés, HRP % faible résilience,
#         HRP % résilience avancée, hausse du risque 2026-2100 en %,
#         hausse bornée par « supérieure à », aléa moteur 2026)
XDI = {
    "CH": (3, 3, 33, 0, 147, False, "crue"),
    "FR": (5, 38, 26, 18, 300, True, "submersion"),
    "NL": (6, 12, 25, 0, 83, False, "ruissellement"),
    "FI": (10, 41, 12, 0, 85, False, "ruissellement"),
    "NO": (12, 25, 12, 0, 185, False, "ruissellement"),
    "IT": (17, 45, 9, 0, 142, False, "crue"),
    "PT": (18, 12, 8, 0, 300, True, "crue"),
    "IE": (19, 55, 7, 4, 300, True, "submersion"),
    "DK": (20, 37, 5, 3, 300, True, "submersion"),
    "DE": (21, 79, 5, 1, 135, False, "ruissellement"),
    "GB": (24, 162, 4, 0, 300, True, "crue"),
    "ES": (25, 67, 3, 1, 181, False, "submersion"),
}

# Le pire du panel européen sert d'étalon, comme pour « parc » et « pipeline ».
# Le fixer en dur figerait la note au millésime du rapport.
XDI_PIRE = max(v[2] for v in XDI.values())

XDI_EUROPE = {
    "analyses": 623, "haut_risque": 45, "part": 7, "hausse_2100": 289,
    "phrase": "Sur 623 centres de données planifiés analysés en Europe, 45 "
              "ressortent à haut risque de dommage physique en 2026, soit 7 %. "
              "Le risque moyen de dommage est modélisé en hausse de 289 % "
              "d'ici 2100 sous scénario d'émissions élevées.",
}

# Ce que la seule note ne dit pas, et qui pèse davantage.
XDI_INDIRECT = (
    "Le risque INDIRECT pèse dix fois plus que le dommage direct. Sur un "
    "portefeuille témoin de 138 centres européens, XDI modélise une perte de "
    "productivité multipliée par dix quand on intègre les dépendances — "
    "réseau électrique, transport, eau, chaînes d'approvisionnement — au lieu "
    "du seul dommage au bâtiment ; elle approche 2 % en moyenne et triple d'ici "
    "la fin du siècle. La note ci-dessous ne porte QUE le dommage direct : "
    "elle sous-estime donc l'exposition réelle, et dans des proportions que le "
    "rapport chiffre.")

SOURCE_XDI = {
    "titre": "2026 Global Analysis of Planned Data Centres for Physical "
             "Climate Risk and Resilience — Key Findings",
    "editeur": "XDI (Cross Dependency Initiative), juin 2026",
    "url": "https://xdi.systems/",
    "nature": "referentiel",
    "note": "Classement des vingt-cinq premiers pays, risque de dommage "
            "physique modélisé en 2026, réglages de faible résilience. "
            "Scénario d'émissions élevées RCP 8.5 / SSP5-8.5, employé par "
            "l'éditeur comme test de résistance et non comme prévision. La "
            "chaleur extrême est EXCLUE de ce classement : elle perturbe "
            "l'exploitation sans endommager le bâtiment, et se mesure "
            "autrement. Localisation des sites fournie à XDI par Data Center "
            "Map, distincte de notre propre référentiel.",
}


def xdi_de(pays):
    """La fiche de risque climatique physique d'un pays, ou None s'il est hors
    classement — ce qui n'est pas la même chose qu'un risque faible."""
    v = XDI.get(pays)
    if not v:
        return None
    rang, n, bas, avance, hausse, borne, alea = v
    return {
        "rang_mondial": rang,
        "centres_analyses": n,
        "haut_risque_pct": bas,
        "haut_risque_adapte_pct": avance,
        # La part que l'ingénierie NE rattrape PAS : c'est le risque de LIEU.
        "irreductible_pct": round(100.0 * avance / bas) if bas else 0,
        "hausse_2100_pct": hausse,
        "hausse_bornee": borne,
        "alea": alea,
        "alea_nom": XDI_ALEAS[alea],
    }


def _note_xdi(pays):
    """0-100, plus haut = moins exposé. Un pays hors classement n'a pas de
    note : le comparateur l'écarte du calcul plutôt que de lui en inventer
    une, bonne ou mauvaise."""
    v = XDI.get(pays)
    if not v:
        return None
    return max(0, min(100, round(100 - 100.0 * v[2] / XDI_PIRE)))


# ═══════════════════════════════════════════════════════════════════════════
# 6. AVANTAGES / INCONVÉNIENTS — l'analyse croisée, par pays
#    Nature « analyse » : la lecture du cabinet, datée, à partir des critères
#    ci-dessus et du référentiel des sites. Un avis se discute — c'est le but.
# ═══════════════════════════════════════════════════════════════════════════

AVIS = {
    "FR": {"pour": ["réseau à 45 gCO₂e/kWh porté par un nucléaire pilotable — le kWh décarboné 8 760 h/an",
                    "prix industriel intermédiaire et stable relativement aux voisins",
                    "pipeline politique fort (109 Md€ annoncés, foncier fléché « sites clés en main »)"],
           "contre": ["délais de raccordement et d'instruction hétérogènes selon les régions",
                      "bassins sud en tension hydrique estivale — l'évaporatif s'y discute",
                      "fiscalité locale (IFER, foncier) à modéliser tôt"],
           "comm": "Le meilleur rapport carbone/pilotabilité d'Europe continentale ; la vitesse "
                   "d'exécution dépend du territoire choisi plus que du pays."},
    "SE": {"pour": ["35 gCO₂e/kWh, prix bas, free cooling quasi permanent — le trio le plus favorable du référentiel",
                    "filière constituée (parc existant, chaleur fatale valorisée)",
                    "eau abondante : l'évaporatif n'y est pas un sujet de permis"],
           "contre": ["nord excédentaire mais ÉLOIGNÉ des dorsales — latence vers l'Europe centrale",
                      "goulots de transport internes nord-sud (SE1-SE4) : le prix bas est zonal",
                      "main-d'œuvre spécialisée limitée hors métropoles"],
           "comm": "Optimal pour l'entraînement (latence peu sensible) ; à arbitrer pour "
                   "l'inférence temps réel au plus près des utilisateurs."},
    "NO": {"pour": ["~100 % renouvelable (hydro pilotable), parmi les prix les plus bas d'Europe",
                    "hydrologie excédentaire, climat froid",
                    "projets d'échelle annoncés (Stargate Norway) qui valident la filière"],
           "contre": ["hors UE : cadre réglementaire distinct à intégrer (mais EEE)",
                      "capacité de transport limitée vers le continent",
                      "acceptabilité locale sensible à l'usage de l'hydroélectricité"],
           "comm": "Le kWh le plus propre et le moins cher du panel — pour des charges "
                   "tolérantes à la latence."},
    "FI": {"pour": ["nucléaire + renouvelables ≈ 90 % de la production, prix bas",
                    "free cooling permanent, valorisation de chaleur fatale exemplaire",
                    "foncier et réseau disponibles"],
           "contre": ["latence vers l'Europe de l'Ouest", "frontière orientale : prime de risque géopolitique à modéliser"],
           "comm": "Alternative nordique crédible à la Suède, souvent moins concurrentielle à l'achat."},
    "DK": {"pour": ["~85 % renouvelable, hub d'interconnexions", "parc hyperscale déjà implanté"],
           "contre": ["éolien dominant : profil intermittent, couverture des creux à contractualiser",
                      "eau souterraine sous surveillance — étés secs"],
           "comm": "Excellent profil carbone ; le PPA doit couvrir les creux de vent."},
    "IE": {"pour": ["écosystème hyperscale historique (8 sites cartographiés), fiscalité attractive",
                    "climat idéal pour le free cooling", "eau abondante"],
           "contre": ["MORATOIRE de raccordement de fait sur Dublin (EirGrid) — le premier marché du pays est fermé aux nouveaux",
                      "réseau à 270 gCO₂e/kWh, 60 % fossile (gaz)",
                      "prix électrique parmi les plus élevés d'Europe"],
           "comm": "Le cas d'école du critère « réseau d'abord » : tout y est favorable sauf "
                   "l'électricité — qui bloque. Reprendre un site RACCORDÉ y vaut une prime ; "
                   "en construire un n'y est pas possible à Dublin avant la fin de décennie."},
    "GB": {"pour": ["premier marché européen de colocation (Londres), profondeur locative inégalée",
                    "pipeline politique 2025 (AI Growth Zones) massif"],
           "contre": ["prix électrique le plus élevé du panel", "réseau à 215 gCO₂e/kWh",
                      "sud-est en stress hydrique déclaré", "files de raccordement longues (réforme en cours)"],
           "comm": "La liquidité du marché (location, revente) compense des fondamentaux "
                   "énergie médiocres — un arbitrage financier plus qu'énergétique."},
    "NL": {"pour": ["hub de connectivité européen (AMS-IX), marché de colocation profond",
                    "compétences et chaîne de sous-traitance denses"],
           "contre": ["encadrement national des hyperscale depuis Zeewolde",
                      "réseau saturé par zones (congestion déclarée par les GRD)",
                      "réseau à 250 gCO₂e/kWh"],
           "comm": "Toujours excellent pour la colocation connectée ; devenu défavorable aux "
                   "campus géants — le rachat y domine la construction."},
    "DE": {"pour": ["premier marché continental (Francfort), demande industrielle et cloud souverain",
                    "60 % renouvelable et en progression rapide"],
           "contre": ["prix industriel élevé", "355 gCO₂e/kWh encore — sortie du charbon inachevée",
                      "EnEfG : PUE ≤ 1,2 imposé aux nouveaux sites dès 2026, chaleur fatale à valoriser",
                      "bassins de l'est en conflit d'usage de l'eau documenté"],
           "comm": "Incontournable commercialement, exigeant réglementairement : l'EnEfG "
                   "transforme le PUE en contrainte de permis, pas en option d'ingénierie."},
    "PL": {"pour": ["marché en forte croissance depuis une base faible, coûts fonciers et salariaux bas",
                    "position de hub pour l'Europe centrale"],
           "contre": ["réseau le plus carboné du panel (660 gCO₂e/kWh, 70 % fossile)",
                      "prix électrique élevé et volatil (charbon)",
                      "ressource en eau par habitant parmi les plus faibles d'Europe"],
           "comm": "Un pari sur la décarbonation : l'actif se revalorise si le réseau tient "
                   "ses objectifs — la trajectoire du mix fait partie de la thèse."},
    "ES": {"pour": ["renouvelables abondants et prix bas — parmi les meilleurs PPA solaires d'Europe",
                    "pipeline majeur (AWS Aragon >30 Md€, Microsoft), foncier disponible",
                    "câbles et hub ibérique en construction"],
           "contre": ["stress hydrique structurel au sud et à l'est — l'évaporatif y devient un sujet politique",
                      "intermittence solaire : couverture des nuits à contractualiser",
                      "réseau de transport à renforcer (blackout ibérique d'avril 2025 dans les mémoires)"],
           "comm": "Le grand gagnant du solaire : énergie bon marché et pipeline record — "
                   "à condition de résoudre l'eau par la conception (refroidissement sec) "
                   "et la résilience réseau par le contrat."},
    "PT": {"pour": ["70 % renouvelable, prix compétitifs, câbles transatlantiques (Sines)"],
           "contre": ["sud en stress hydrique", "marché de taille modeste"],
           "comm": "Sines émerge comme alternative ibérique connectée ; mêmes précautions "
                   "d'eau que l'Espagne."},
    "IT": {"pour": ["Milan consolidé comme hub sud-européen, Microsoft 4,3 Md€ annoncés"],
           "contre": ["56 % fossile (gaz), prix élevé", "Pô en tension hydrique", "sismicité à intégrer au choix de site"],
           "comm": "Marché porté par la demande locale plus que par les fondamentaux énergie."},
    "BE": {"pour": ["position centrale, nucléaire prolongé (40 %)", "parc hyperscale existant (Saint-Ghislain)"],
           "contre": ["Flandre en stress hydrique élevé", "prix moyen-élevé"],
           "comm": "Solide en connectivité ; l'eau y est le critère discriminant de site."},
    "CZ": {"pour": ["nucléaire 40 %, position centrale"], "contre": ["45 % fossile, sécheresses récurrentes"],
           "comm": "Marché secondaire en construction."},
    "AT": {"pour": ["85 % renouvelable (hydro alpine), eau abondante"], "contre": ["foncier alpin contraint, marché modeste"],
           "comm": "Niche de qualité plus que destination d'échelle."},
    "GR": {"pour": ["solaire abondant, hub câbles est-méditerranéen émergent"],
           "contre": ["55 % fossile encore, stress hydrique estival généralisé, sismicité"],
           "comm": "Trajectoire favorable, fondamentaux encore en transition."},
    "BG": {"pour": ["nucléaire 40 %, coûts bas"], "contre": ["réseau à 320 gCO₂e/kWh, infrastructures d'eau vieillissantes"],
           "comm": "Marché naissant."},
    "RO": {"pour": ["mix diversifié (hydro, nucléaire), coûts bas"], "contre": ["tension estivale sur le Danube, réseau à moderniser"],
           "comm": "Marché naissant, position balkanique utile."},
    "HU": {"pour": ["nucléaire 45 %"], "contre": ["dépendance hydrique aux fleuves entrants, cadre politique à apprécier"],
           "comm": "Marché secondaire."},
    "HR": {"pour": ["hydro abondante, eau abondante"], "contre": ["marché très petit, sismicité"], "comm": "Niche adriatique."},
    "SI": {"pour": ["nucléaire + hydro, eau alpine"], "contre": ["marché très petit"], "comm": "Niche."},
    "LU": {"pour": ["connectivité et stabilité, hub financier"],
           "contre": ["pays importateur : le mix consommé est celui des voisins, pas les 90 % affichés",
                      "foncier rare et cher"],
           "comm": "L'exemple du biais production/consommation : lire l'intensité avec précaution."},
}

# ═══════════════════════════════════════════════════════════════════════════
# 7. ASSEMBLAGE — notes 0-100 par critère, formule affichée, pipeline calculé
# ═══════════════════════════════════════════════════════════════════════════

CRITERES = [
    {"cle": "carbone", "nom": "Intensité carbone du réseau", "nature": "referentiel",
     "source": "Ember 2024 (cycle de vie) — empreinte_sites.py",
     "formule": "note = 100 × (660 − intensité) ÷ (660 − 30), bornée 0-100"},
    {"cle": "mix", "nom": "Pilotabilité du mix (nucléaire + hydro-dominant)", "nature": "referentiel",
     "source": "Ember 2024, parts arrondies à 5 points",
     "formule": "note = part non fossile, +10 si nucléaire ≥ 30 % (pilotable), bornée 0-100"},
    {"cle": "eau", "nom": "Disponibilité en eau (WEI+, compétition d'usages)", "nature": "referentiel",
     "source": "AEE WEI+ 2022 + parts d'irrigation",
     "formule": "classe faible=90, modéré=55, élevé=20"},
    {"cle": "climat", "nom": "Potentiel free cooling (PUE)", "nature": "analyse",
     "source": "classes latitudinales — PUE par mode (datacentres.py)",
     "formule": "nordique=90, tempéré=65, méridional=35"},
    {"cle": "prix", "nom": "Prix de l'électricité industrielle", "nature": "referentiel",
     "source": "Eurostat nrg_pc_205, 2024, classes",
     "formule": "bas=85, moyen=55, élevé=25"},
    {"cle": "parc", "nom": "Parc en service (filière constituée)", "nature": "calcule",
     "source": "référentiel des 97 sites (datacentres.py)",
     "formule": "note = 100 × sites en service du pays ÷ maximum du panel"},
    {"cle": "climat_physique", "nom": "Risque climatique physique du bâti (XDI)",
     "nature": "referentiel",
     "source": "XDI, juin 2026 — part des centres planifiés à haut risque de dommage, réglages de faible résilience",
     "formule": "note = 100 − 100 × part à haut risque ÷ pire part du panel (33 %, Suisse) ; pays hors classement = pas de note"},
    {"cle": "pipeline", "nom": "File de raccordement 2026-2030 (concurrence)", "nature": "calcule",
     "source": "statuts annoncé + en construction + autorisé des 97 sites",
     "formule": "note = 100 − 100 × pipeline du pays ÷ maximum du panel (moins il y a de file, mieux c'est pour un NOUVEL entrant)"},
]


def _note_carbone(intensite):
    if intensite is None:
        return None
    return max(0, min(100, round(100.0 * (660 - intensite) / (660 - 30))))


def _note_mix(m):
    if not m:
        return None
    note = 100 - m["fossile"]
    if m["nucleaire"] >= 30:
        note += 10
    return max(0, min(100, note))


def assemble(sites, intensites):
    """Le référentiel complet, prêt à afficher : un enregistrement par pays,
    notes par critère, avis, perspectives — et pour chaque famille sa source
    et sa nature. `sites` : liste des sites (datacentres), `intensites` :
    dict pays → gCO2e/kWh (empreinte_sites.INTENSITE)."""
    en_service, pipeline = {}, {}
    for s in sites:
        p = s.get("pays")
        if s.get("statut") == "service":
            en_service[p] = en_service.get(p, 0) + 1
        elif s.get("statut") in ("annonce", "construction", "autorise"):
            pipeline[p] = pipeline.get(p, 0) + 1

    pays_tous = sorted(set(list(EAU) + list(en_service) + list(pipeline)))
    max_service = max(en_service.values() or [1])
    max_pipe = max(pipeline.values() or [1])

    lignes = []
    for p in pays_tous:
        eau = EAU.get(p)
        mix = MIX.get(p)
        prix = PRIX.get(p)
        cl = climat_de(p)
        intensite = intensites.get(p)
        notes = {
            "carbone": _note_carbone(intensite),
            "mix": _note_mix(mix),
            "eau": EAU_CLASSES[eau[0]]["note"] if eau else None,
            "climat": CLIMAT[cl]["note"],
            "prix": PRIX_CLASSES[prix[0]]["note"] if prix else None,
            "parc": round(100.0 * en_service.get(p, 0) / max_service),
            "pipeline": round(100 - 100.0 * pipeline.get(p, 0) / max_pipe),
            "climat_physique": _note_xdi(p),
        }
        avis = AVIS.get(p)
        lignes.append({
            "pays": p,
            "intensite": intensite,
            "mix": mix,
            "eau": ({"classe": eau[0], "classe_nom": EAU_CLASSES[eau[0]]["nom"],
                     "irrigation": eau[1], "bassins": eau[2]} if eau else None),
            "climat": {"classe": cl, "nom": CLIMAT[cl]["nom"]},
            # Hors classement n'est pas « faible risque » : le champ vaut None
            # et porte à côté la raison, sinon l'absence se lirait comme une
            # bonne nouvelle.
            "climat_physique": xdi_de(p),
            "climat_physique_absence": (None if XDI.get(p) else
                                        "hors du classement XDI des vingt-cinq "
                                        "premiers pays : moins de trois centres "
                                        "planifiés analysés, ou part à haut risque "
                                        "inférieure à 3 %"),
            "prix": ({"classe": prix[0], "classe_nom": PRIX_CLASSES[prix[0]]["nom"],
                      "fourchette_eur_mwh": list(prix[1])} if prix else None),
            "en_service": en_service.get(p, 0),
            "pipeline_2030": pipeline.get(p, 0),
            "notes": notes,
            "avis": avis,
            "perspectives": [x for x in PERSPECTIVES if x["pays"] == p],
        })

    return {
        "version": VERSION,
        "genere": datetime.now(timezone.utc).isoformat(),
        "criteres": CRITERES,
        "classes": {"eau": EAU_CLASSES, "prix": PRIX_CLASSES, "climat": {k: v["nom"] for k, v in CLIMAT.items()}},
        "sources": {"eau": SOURCE_EAU, "mix": SOURCE_MIX, "prix": SOURCE_PRIX,
                    "perspectives": SOURCE_PERSPECTIVES, "climat_physique": SOURCE_XDI},
        "climat_physique": {"aleas": XDI_ALEAS, "europe": XDI_EUROPE,
                            "pire_panel": XDI_PIRE, "indirect": XDI_INDIRECT,
                            "classement": sorted(
                                [dict(pays=k, **xdi_de(k)) for k in XDI],
                                key=lambda x: x["rang_mondial"])},
        "perspectives_ue": [x for x in PERSPECTIVES if x["pays"] == "UE"],
        "pays": lignes,
        "avertissement": (
            "Ce référentiel COMPARE des pays en ordres de grandeur sourcés ; il ne "
            "chiffre aucun site. Les notes servent le classement pondéré et n'ont "
            "aucun sens hors de lui. Toute décision exige la vérification des "
            "sources primaires citées et une due diligence locale — réseau, "
            "bassin versant, permis, prix contractuel."),
    }


def sante():
    """Invariants relus à chaque déploiement."""
    pb = []
    for p, m in MIX.items():
        total = m["nucleaire"] + m["renouvelables"] + m["fossile"]
        if not 90 <= total <= 110:
            pb.append("mix %s : total %d hors 90-110" % (p, total))
    for p in EAU:
        if EAU[p][0] not in EAU_CLASSES:
            pb.append("eau %s : classe inconnue" % p)
    for p in PRIX:
        if PRIX[p][0] not in PRIX_CLASSES:
            pb.append("prix %s : classe inconnue" % p)
        a, b = PRIX[p][1]
        if not a < b:
            pb.append("prix %s : fourchette inversée" % p)
    for k, v in XDI.items():
        rang, n, bas, avance, hausse, borne, alea = v
        if alea not in XDI_ALEAS:
            pb.append("xdi %s : alea inconnu %s" % (k, alea))
        if avance > bas:
            pb.append("xdi %s : la resilience avancee aggrave le risque" % k)
        if n < 3:
            pb.append("xdi %s : moins de trois centres analyses, XDI ne classe pas" % k)
        if not 1 <= rang <= 25:
            pb.append("xdi %s : rang hors du top 25" % k)
    if XDI_PIRE <= 0:
        pb.append("xdi : etalon du panel nul, la note serait indefinie")
    for x in PERSPECTIVES:
        if x["sens"] not in ("hausse", "contrainte"):
            pb.append("perspective %s : sens inconnu" % x["pays"])
        if not x.get("source") or not x.get("date"):
            pb.append("perspective %s : source ou date manquante" % x["pays"])
    return {"ok": not pb, "problemes": pb, "version": VERSION,
            "pays_eau": len(EAU), "pays_mix": len(MIX), "pays_prix": len(PRIX),
            "perspectives": len(PERSPECTIVES), "avis": len(AVIS),
            "pays_xdi": len(XDI), "criteres": len(CRITERES)}
