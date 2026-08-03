# -*- coding: utf-8 -*-
"""Prospectives des centres de données — tendances 2026, jalons réglementaires
et réserves sur le référentiel.

POURQUOI CE MODULE EXISTE

Le référentiel d'implantation dit où sont les sites et ce que coûte
l'électricité. Il ne dit pas ce qui est en train de changer. Or une décision
d'investissement se prend sur cinq à dix ans : le gel de Francfort jusqu'en
2031, la fermeture d'Amsterdam jusqu'en 2035 ou la suppression de l'accise
finlandaise en mars 2025 pèsent plus lourd, sur cet horizon, que l'écart de
notation entre deux pays voisins.

D'OÙ VIENNENT CES FAITS

Des quatre rapports versés au dossier, lus intégralement et vérifiés un par un :
chaque entrée porte sa PAGE, son éditeur et, quand une phrase se cite seule, sa
CITATION VERBATIM. Une extraction automatique a produit 175 faits ; une seconde
passe a exigé de retrouver chaque citation LITTÉRALEMENT dans le texte source,
espaces normalisés. Deux citations n'ont pas survécu à ce contrôle — un fragment
recollé par l'extracteur (« electricians and 18% in plumbing », qui n'existe
nulle part) et une phrase coupée à la césure — et ont été reprises sur l'original.
Les entrées sans citation ne sont pas des trous : elles résument une section
entière, le disent à l'écran, et donnent la page pour vérification.

Une source qui REPREND un chiffre n'en est pas l'auteur. Quand c'est le cas, le
champ `source_amont` nomme l'origine réelle — Research and Markets pour le marché
de la périphérie, l'Irish Times pour les raccordements gaziers irlandais — pour
que le lecteur sache qu'entre lui et le chiffre il y a deux publications.

Ce qui suit est ce qui a survécu à cette confrontation ET qui concerne l'Union
européenne.

  Soben (part of Accenture) — Data Centre Trends Report 2026
  Accenture — Powering the Future of US Data Centers
  Accenture — Powering Sustainable AI (canvas V1.0)
  Accenture — ESG Reporting: From Compliance to Competitive Advantage

CE QUE CE MODULE NE FAIT PAS

Il ne recalcule aucune note du référentiel. Quand un fait nouveau PÉRIME une
valeur existante — c'est le cas du prix finlandais — il l'inscrit en RÉSERVE,
datée, à côté de la valeur, au lieu de la corriger en silence. Un référentiel
qui se réécrit sans le dire fait perdre au lecteur la trace de ce qu'il a cité
la semaine précédente.
"""
from datetime import datetime, timezone

VERSION = "2026-08-a"

SOURCES = {
    "soben2026": {
        "titre": "Data Centre Trends Report 2026 — Shifting up a gear",
        "editeur": "Soben (part of Accenture)",
        "date": "2026",
        "nature": "referentiel",
        "portee": "mondiale, avec un chapitre EMEA détaillé",
    },
    "us_dc": {
        "titre": "Powering the Future of US Data Centers",
        "editeur": "Accenture",
        "date": "2025",
        "nature": "referentiel",
        "portee": "États-Unis — transposable avec précaution",
    },
    "sustainable_ai": {
        "titre": "Powering Sustainable AI (canvas V1.0)",
        "editeur": "Accenture",
        "date": "2025",
        "nature": "referentiel",
        "portee": "mondiale",
    },
    "esg": {
        "titre": "ESG Reporting: From Compliance to Competitive Advantage",
        "editeur": "Accenture",
        "date": "2025",
        "nature": "referentiel",
        "portee": "mondiale, cadre européen détaillé",
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# 1. LES DIX TENDANCES 2026
#    `incidence` : ce que la tendance change POUR UN INVESTISSEUR EUROPÉEN.
#    `critere`   : le critère du comparateur d'implantation qu'elle touche,
#                  ou None si elle n'en touche aucun — ce qui est en soi une
#                  information : le référentiel ne capte pas tout.
# ═══════════════════════════════════════════════════════════════════════════
TENDANCES = [
    {"n": 1, "cle": "vitesse", "titre": "La vitesse devient le premier critère",
     "resume": "Les calendriers de livraison se compriment et la vitesse prime sur le coût. "
               "Ce qui se construisait en douze mois pour 400 MW en 2018 est devenu, en 2026, "
               "« un pari énorme ». La conception standardisée, la construction modulaire et "
               "la maquette numérique sont les seuls leviers d'accélération réels.",
     "chiffre": "surcoût de 25 % accepté par un hyperscaler américain pour tenir un calendrier exigeant",
     "citation": "a US hyperscaler recently accepted a 25% uplift in tender price from a GC "
                 "to deliver to a demanding timeline",
     "source": "soben2026", "page": 8, "critere": None,
     "incidence": "La prime de vitesse est un poste d'arbitrage à part entière : elle achète la "
                  "priorité d'une entreprise générale, jamais l'accord du gestionnaire de réseau. "
                  "Le module d'enveloppe la chiffre désormais explicitement."},

    {"n": 2, "cle": "metiers", "titre": "Les métiers du bâtiment se retendent",
     "resume": "Électriciens, plombiers, charpentiers : la demande explose et l'offre recule. "
               "Le déficit se comble par des programmes de formation nationaux et des "
               "initiatives des grands acteurs du cloud, mais pas avant plusieurs années.",
     "chiffre": "Royaume-Uni : effectifs des métiers de l'électricité en baisse de 19,8 % "
                "entre 2018 et 2024, et de 18 % pour la plomberie sur la même période",
     "citation": "the number of electrical workers fell by 19.8% between 2018 and 2024 "
                 "according to Government statistics while the plumbing workforce shrank by "
                 "18% over the same period",
     "source": "soben2026", "page": 9,
     "source_amont": "statistiques du gouvernement britannique",
     "critere": "parc",
     "incidence": "Un pays sans filière constituée n'a pas seulement moins de sites : il a moins "
                  "d'entreprises capables d'en construire. C'est le sens du critère « parc en "
                  "service » du comparateur, et cette tendance en renforce le poids."},

    {"n": 3, "cle": "peripherie", "titre": "Les centres de périphérie cherchent leurs sites",
     "resume": "Une fois les modèles entraînés dans de grands campus éloignés, l'inférence doit "
               "se rapprocher des villes et des bassins industriels. La recherche de sites de "
               "périphérie s'accélère avec le déploiement de la 5G.",
     "chiffre": "marché des centres de périphérie de 15,4 Md$ en 2024 à 39,8 Md$ en 2030",
     "citation": "the market for edge data centres would grow from $15.4 billion in 2024 to "
                 "$39.8 billion in 2030",
     "source": "soben2026", "page": 11,
     "source_amont": "prévision Research and Markets, novembre 2025 — reprise par le rapport, "
                     "pas produite par lui",
     "critere": None,
     "incidence": "Le référentiel recense des campus. Une vague de petits sites d'inférence près "
                  "des villes ne s'y lira pas — et c'est une limite à connaître avant de conclure "
                  "qu'un pays est peu équipé."},

    {"n": 4, "cle": "industrialisation", "titre": "L'industrialisation de la construction",
     "resume": "Préfabrication, modules livrés prêts à raccorder, standardisation des "
               "conceptions : la construction sur site cède du terrain à l'assemblage. "
               "C'est la réponse directe à la pénurie de main-d'œuvre qualifiée.",
     "chiffre": None, "citation": None, "source": "soben2026", "page": 13, "critere": None,
     "incidence": "Une part croissante de l'enveloppe migre du chantier vers l'usine. Les lots "
                  "04 à 06 de la DPGF s'en trouvent moins sensibles au coût local de la "
                  "main-d'œuvre — ce qui atténue, sans l'annuler, l'écart entre pays."},

    {"n": 5, "cle": "gaz", "titre": "Le gaz revient, faute de réseau",
     "resume": "Les contraintes de raccordement relancent le gaz naturel comme source "
               "d'alimentation. Les solutions hybrides — renouvelables plus gaz — offrent "
               "fiabilité et rapidité de mise en service. L'hydrogène et le nucléaire sont "
               "annoncés, mais plus tard.",
     "chiffre": "Irlande : 11 centres de données contractés pour un raccordement au réseau "
                "gazier, 4 en attente de raccordement et 15 en attente de décision ; "
                "Royaume-Uni : 86 demandes de raccordement gazier en douze mois",
     "citation": "11 data centres were contracted to connect to the gas network, with four of "
                 "those waiting for a connection. A further 15 were waiting for a decision on "
                 "whether they could be connected",
     "source": "soben2026", "page": 16,
     "source_amont": "Irish Times, juin 2025 (Irlande) ; Future Energy Networks via Argus "
                     "Media, douze mois à août 2025 (Royaume-Uni)",
     "critere": "carbone",
     "incidence": "Un site alimenté au gaz échappe à la file d'attente du réseau électrique, mais "
                  "son intensité carbone n'est plus celle du mix national. Le comparateur note le "
                  "MIX DU PAYS : un projet sous groupe gaz dédié doit être recalculé à part."},

    {"n": 6, "cle": "refroidissement", "titre": "Le refroidissement change de génération",
     "resume": "Plaques froides, immersion diphasique, microfluidique : les technologies "
               "progressent vite et promettent moins d'énergie ET moins d'eau. Elles "
               "répondent en même temps au coût d'exploitation et à l'acceptabilité.",
     "chiffre": None, "citation": None, "source": "soben2026", "page": 17, "critere": "climat",
     "incidence": "Le critère « potentiel de free cooling » perd de sa force à mesure que le "
                   "refroidissement liquide s'impose pour la densité IA : le climat commande moins "
                   "la solution quand la chaleur est captée à la puce. Le module d'enveloppe le "
                   "traduit déjà par le mode « liquide »."},

    {"n": 7, "cle": "terres_rares", "titre": "Les terres rares se raréfient",
     "resume": "Le renforcement des contrôles chinois à l'exportation expose particulièrement "
               "l'Europe. Extraction, raffinage et recyclage européens se réorganisent, mais "
               "la planification stratégique et l'économie circulaire deviennent des conditions "
               "de résilience, pas des options.",
     "chiffre": None, "citation": None, "source": "soben2026", "page": 19, "critere": None,
     "incidence": "Un risque d'approvisionnement qui ne se lit dans aucun critère du comparateur. "
                  "Il se traite en clause contractuelle et en stock, pas en choix de pays."},

    {"n": 8, "cle": "permis", "titre": "La course aux permis",
     "resume": "Les États simplifient les procédures pour attirer l'investissement ; les "
               "développeurs recourent à l'IA pour accélérer les dossiers. L'adhésion des "
               "riverains et la conception durable — autoproduction, sobriété en eau — "
               "deviennent déterminantes.",
     "chiffre": None, "citation": None, "source": "soben2026", "page": 21, "critere": "pipeline",
     "incidence": "Le délai d'instruction n'est pas dans le référentiel et ne peut pas y être : "
                  "il dépend de la commune. C'est l'un des cinq postes que le module d'enveloppe "
                  "affiche VIDE, avec la question à poser."},

    {"n": 9, "cle": "puces", "titre": "Les puces se diversifient",
     "resume": "Nvidia reste dominant, mais les hyperscalers développent leurs propres "
               "accélérateurs pour réduire leur dépendance. La politique commerciale et les "
               "ruptures d'approvisionnement redessinent le paysage.",
     "chiffre": None, "citation": None, "source": "soben2026", "page": 23, "critere": None,
     "incidence": "Sans effet direct sur le choix d'un pays, mais un effet fort sur la densité "
                  "par baie — donc sur le mode de refroidissement, donc sur les lots 05 à 07."},

    {"n": 10, "cle": "quantique", "titre": "L'année pour se préparer au quantique",
     "resume": "L'informatique quantique passe du concept aux premiers déploiements "
               "commerciaux. Des centres hybrides et des normes se construisent ; les "
               "pionniers prennent une avance qui se rattrape mal.",
     "chiffre": None, "citation": None, "source": "soben2026", "page": 25, "critere": None,
     "incidence": "Horizon au-delà de 2030 pour la plupart des projets européens. À suivre, pas "
                  "à budgéter."},
]

# ═══════════════════════════════════════════════════════════════════════════
# 2. JALONS RÉGLEMENTAIRES EUROPÉENS
#    Datés, opposables, et directement structurants pour un calendrier de projet.
# ═══════════════════════════════════════════════════════════════════════════
JALONS = [
    {"cle": "eed_reporting", "pays": "UE", "date": "2024-09", "statut": "en vigueur",
     "titre": "Reporting de performance énergétique des centres de données",
     "detail": "La directive d'efficacité énergétique (UE) 2023/1791 impose depuis septembre "
               "2024 aux exploitants de déclarer la performance énergétique de leurs centres "
               "de données, et encourage la valorisation de la chaleur fatale dans les réseaux "
               "de chaleur.",
     "citation": "has required operators to report on the energy performance of data centres "
                 "since September 2024",
     "source": "soben2026", "page": 35, "impact": "obligation déclarative"},

    {"cle": "eed_paquet_2026", "pays": "UE", "date": "2026-T1", "statut": "annoncé",
     "titre": "Data Centre Energy Efficiency Package",
     "detail": "L'Union proposera au premier trimestre 2026 un paquet dédié à l'efficacité "
               "énergétique des centres de données, dont les exigences sont attendues en "
               "renforcement des obligations actuelles.",
     "citation": "In the first quarter of 2026, the EU will propose a new Data Centre Energy "
                 "Efficiency Package",
     "source": "soben2026", "page": 35,
     "impact": "durcissement attendu — à anticiper dans tout projet livré après 2027"},

    {"cle": "enefg_chaleur", "pays": "DE", "date": "2026-07-01", "statut": "en vigueur différée",
     "titre": "Allemagne — réutilisation obligatoire de la chaleur fatale",
     "detail": "La loi allemande d'efficacité énergétique (EnEfG), en vigueur depuis novembre "
               "2023, oblige les centres de données de 300 kW et plus à déclarer leur chaleur "
               "fatale depuis le 1er janvier 2025 ; ceux mis en service à compter du "
               "1er juillet 2026 doivent en réutiliser une part. Des exemptions existent "
               "lorsque l'infrastructure ou l'accord d'un réseau de chaleur sont hors "
               "d'atteinte — le rapport note qu'elles sont assez larges pour que beaucoup de "
               "sites n'y soient pas tenus.",
     "citation": "for data centres that go into operation after 1 July 2026, a proportion of "
                 "their waste heat must be reused",
     "source": "soben2026", "page": 35,
     "impact": "conditionne la conception thermique dès l'avant-projet, pas à la réception"},

    {"cle": "csrd_audit", "pays": "UE", "date": "2024", "statut": "en vigueur",
     "titre": "CSRD — audit des informations de durabilité",
     "detail": "Les grandes entreprises soumises à la CSRD voient les informations de "
               "durabilité de l'exercice 2024 entrer dans le champ de l'audit. La quasi-totalité "
               "des réglementations votées ou proposées exigent une assurance externe.",
     "citation": "the EU's CSRD will require large EU and non-EU-based companies to have their "
                 "2024 fiscal year reports audited",
     "source": "esg", "page": 19,
     "impact": "l'empreinte d'un centre de données devient une donnée auditée, pas déclarative"},

    {"cle": "amsterdam_2035", "pays": "NL", "date": "2035", "statut": "annoncé",
     "titre": "Amsterdam — pas de nouveau projet avant 2035",
     "detail": "Le conseil municipal d'Amsterdam a indiqué qu'il n'examinerait de nouveaux "
               "projets de centres de données qu'à partir de 2035.",
     "citation": "will only consider new data centre developments from 2035",
     "source": "soben2026", "page": 30,
     "impact": "ferme de fait l'un des cinq hubs historiques pour une décennie"},

    {"cle": "francfort_2031", "pays": "DE", "date": "2031", "statut": "annoncé",
     "titre": "Francfort — projets d'IA gelés jusqu'à 2031",
     "detail": "À Francfort, les développements de centres de données dédiés à l'IA sont "
               "suspendus jusqu'à la mise en service de nouvelles capacités de réseau, "
               "attendues en 2031.",
     "citation": "AI data centre developments are on hold until new capacity comes online in 2031",
     "source": "soben2026", "page": 30,
     "impact": "déplace la demande vers les marchés secondaires allemands et les Nordiques"},

    {"cle": "finlande_accise", "pays": "FI", "date": "2025-03", "statut": "en vigueur",
     "titre": "Finlande — fin du tarif réduit d'accise sur l'électricité",
     "detail": "En mars 2025, le gouvernement finlandais a supprimé l'avantage fiscal dont "
               "bénéficiaient les centres de données sur l'électricité, faisant passer le taux "
               "de 0,05 centime par kWh au taux standard de 2,24 centimes par kWh.",
     "citation": "abolished tax breaks on electricity for data centres, moving the rate from "
                 "0.05 cents per kWh to the standard 2.24 cents per kWh",
     "source": "soben2026", "page": 30,
     "impact": "environ +22 €/MWh sur la facture — le pays reste compétitif, mais l'écart "
               "avec la Suède et la Norvège se resserre nettement"},

    {"cle": "suede_permis", "pays": "SE", "date": "2025", "statut": "en vigueur",
     "titre": "Suède — incitations fiscales et permis hyperscale simplifiés",
     "detail": "La Suède et la Norvège offrent des incitations fiscales ; la Suède simplifie "
               "en outre l'instruction des permis pour les projets hyperscale.",
     "citation": "Both Sweden and Norway are offering tax incentives, with Sweden also "
                 "streamlining permitting for hyperscale developments",
     "source": "soben2026", "page": 30,
     "impact": "raccourcit la phase d'instruction, celle qui commande le calendrier"},

    {"cle": "irlande_autoprod", "pays": "IE", "date": "2025", "statut": "en vigueur",
     "titre": "Irlande — autoproduction autorisée, permis toujours difficiles",
     "detail": "Le gouvernement irlandais a fait adopter une loi autorisant les centres de "
               "données à produire leur propre électricité ; l'obtention des autorisations "
               "correspondantes reste loin d'être simple.",
     "citation": "the Government passed a law to allow data centres to generate their own power",
     "source": "soben2026", "page": 30,
     "impact": "ouvre une porte contournant la file de raccordement, sans garantie de délai"},

    {"cle": "uk_zones", "pays": "GB", "date": "2025-11", "statut": "en vigueur",
     "titre": "Royaume-Uni — trois AI Growth Zones désignées sur plus de 200 candidatures",
     "detail": "Plus de 200 sites se sont portés candidats ; trois ont été retenus à la "
               "mi-novembre 2025 — Culham dans l'Oxfordshire, Blyth et Cobalt Park dans le "
               "Nord-Est de l'Angleterre, Anglesey et Trawsfynydd au nord du pays de Galles — "
               "avec accès prioritaire au réseau et instruction accélérée.",
     "citation": "Over 200 locations have bid to become an AI Growth Zone with three announced "
                 "by the Government by mid-November 2025",
     "source": "soben2026", "page": 22,
     "impact": "hors Union européenne, mais concurrence directement les marchés continentaux ; "
               "le rapport de 200 à 3 dit aussi le taux de déception à attendre d'un dispositif "
               "de ce type"},

    {"cle": "aragon_saturation", "pays": "ES", "date": "2025", "statut": "constaté",
     "titre": "Aragon — la région victime de son propre succès",
     "detail": "En allégeant l'instruction des permis, l'Aragon a capté des investissements "
               "massifs autour de Saragosse, portés par une électricité verte abondante et la "
               "proximité des lignes à haute tension. Le raccordement au réseau est devenu un "
               "goulet d'étranglement, et des agriculteurs imputent aux centres de données les "
               "pénuries d'eau — AWS y répond par un programme de réduction des fuites.",
     "citation": "the region has to some degree become a victim of its own success. Connections "
                 "to the grid have become a bottleneck",
     "source": "soben2026", "page": 22,
     "impact": "un permis rapide n'est pas un raccordement rapide, et l'acceptabilité locale "
               "se dégrade avec le succès : les deux se vérifient avant de compter sur la "
               "vitesse espagnole"},
]

# ═══════════════════════════════════════════════════════════════════════════
# 3. STRUCTURE DE MARCHÉ — ce qui contraint l'exécution, pas la localisation
# ═══════════════════════════════════════════════════════════════════════════
MARCHE = [
    {"cle": "pipeline_europe", "titre": "Pipeline européen de projets",
     "valeur": "351,7 milliards de dollars", "date": "2025-T3", "nature": "chiffre",
     "citation": "an estimated project pipeline of $351.7 billion for data centres in Europe",
     "source": "soben2026", "page": 29, "source_amont": "estimation Accenture",
     "sens": "L'ordre de grandeur de la vague à venir, contre lequel se mesure la file de "
             "raccordement de chaque pays."},
    {"cle": "entreprises_generales", "titre": "Vivier d'entreprises générales en EMEA",
     "valeur": "moins de dix", "date": "2026", "nature": "chiffre",
     "citation": "Fewer than ten trusted general contractors", "source": "soben2026", "page": 32,
     "sens": "La contrainte d'exécution la plus dure d'Europe. Un nouvel entrant sans "
             "antériorité ne trouvera pas d'entreprise générale, quel que soit son financement."},
    {"cle": "couts_2026", "titre": "Trajectoire des coûts de construction en EMEA",
     "valeur": "hausse supérieure à celle de la construction générale", "date": "2026",
     "nature": "prevision",
     "citation": "costs will continue to rise above those of general construction through 2026",
     "source": "soben2026", "page": 32,
     "sens": "Toute enveloppe établie sur un référentiel de coûts antérieur à 2026 est "
             "sous-estimée."},
    {"cle": "part_ia_electricite", "titre": "Part de l'IA dans la consommation électrique mondiale",
     "valeur": "de 0,2 % en 2024 à 1,9 % en 2030", "date": "2030", "nature": "prevision",
     "citation": "AI's share of global power consumption is set to rise from 0.2% in 2024 to "
                 "1.9% by 2030",
     "source": "sustainable_ai", "page": 11,
     "sens": "Une croissance de 48 % par an, face à 1,5 % pour la demande électrique totale. "
             "C'est cette divergence qui crée la tension sur les réseaux."},
    {"cle": "flapd_sature", "titre": "Les cinq hubs historiques européens sont saturés en réseau",
     "valeur": "Francfort, Londres, Amsterdam, Paris, Dublin", "date": "2026", "nature": "analyse",
     "citation": "the European cities of Frankfurt, London, Amsterdam, Paris and Dublin are "
                 "slowing or stalling data centre developments there",
     "source": "soben2026", "page": 15,
     "sens": "Le référentiel compte des sites EN SERVICE : les cinq hubs y sortent donc en tête, "
             "ce qui est exact et trompeur à la fois. Un parc dense signale une filière mûre, "
             "pas une capacité disponible — sur ces cinq places, c'est même l'inverse."},
    {"cle": "metriques_ia", "titre": "Au-delà du PUE : mesurer par jeton produit",
     "valeur": "jetons par MWh, par tCO₂e, par m³ d'eau", "date": "2025", "nature": "analyse",
     "citation": "tokens per  dollar, per MWh, per tCO₂e and per cubic  meter of water",
     "source": "sustainable_ai", "page": 9,
     "sens": "Le PUE mesure l'efficacité du bâtiment, pas celle du travail utile. Un site au "
             "PUE excellent qui fait tourner des modèles surdimensionnés reste inefficace."},
]

# ═══════════════════════════════════════════════════════════════════════════
# 4. RÉSERVES SUR LE RÉFÉRENTIEL EXISTANT
#    Un fait nouveau qui périme une valeur ne la corrige PAS en silence : il
#    s'inscrit à côté, daté. Le lecteur qui a cité la valeur la semaine dernière
#    doit pouvoir voir ce qui a changé depuis, et décider lui-même.
# ═══════════════════════════════════════════════════════════════════════════
RESERVES = [
    {"pays": "FI", "critere": "prix", "depuis": "2025-03",
     "valeur_referentiel": "classe « bas », 60 à 100 €/MWh (Eurostat nrg_pc_205, 2024)",
     "reserve": "La bande Eurostat retenue est un millésime 2024, ANTÉRIEUR à la suppression du "
                "tarif réduit d'accise de mars 2025. Celle-ci ajoute environ 22 €/MWh : la "
                "borne haute réelle avoisine désormais le seuil de la classe « moyen ». La "
                "classe n'est pas recalculée ici — aucune série publiée postérieure au "
                "changement n'est disponible dans ce référentiel — mais elle doit être "
                "considérée comme optimiste.",
     "jalon": "finlande_accise"},
    {"pays": "NL", "critere": "pipeline", "depuis": "2035",
     "valeur_referentiel": "file de raccordement comptée depuis les statuts des sites",
     "reserve": "Le comptage porte sur les projets déclarés. La décision d'Amsterdam de "
                "n'examiner de nouveaux projets qu'à partir de 2035 ne s'y lit pas : un "
                "pipeline faible peut signifier un marché fermé autant qu'un marché libre.",
     "jalon": "amsterdam_2035"},
    {"pays": "DE", "critere": "pipeline", "depuis": "2031",
     "valeur_referentiel": "file de raccordement comptée depuis les statuts des sites",
     "reserve": "Le gel des projets d'IA à Francfort jusqu'en 2031 concerne le premier hub "
                "allemand. Un pipeline national qui paraît ouvert peut être fermé là où se "
                "trouve la connectivité.",
     "jalon": "francfort_2031"},
    {"pays": "ES", "critere": "pipeline", "depuis": "2025",
     "valeur_referentiel": "file de raccordement comptée depuis les statuts des sites, et "
                           "perspective « hausse » adossée aux annonces AWS et Microsoft",
     "reserve": "L'Aragon a bâti son attractivité sur des permis rapides — le référentiel le "
                "reflète en pipeline. Le raccordement au réseau y est devenu un goulet "
                "d'étranglement, et une contestation locale sur l'eau s'est ouverte : un projet "
                "déclaré n'y est pas un projet raccordable, et la vitesse d'instruction ne dit "
                "rien de la vitesse de mise sous tension.",
     "jalon": "aragon_saturation"},
    {"pays": "IE", "critere": "pipeline", "depuis": "2025",
     "valeur_referentiel": "moratoire de fait sur les nouveaux raccordements",
     "reserve": "La loi autorisant l'autoproduction ouvre une voie que le moratoire ne ferme "
                "pas. Le référentiel ne la distingue pas : un projet irlandais avec production "
                "dédiée ne se lit pas comme un projet raccordé au réseau.",
     "jalon": "irlande_autoprod"},
]


def par_pays(code):
    """Tout ce que ce module sait d'un pays : jalons, réserves, tendances liées."""
    code = (code or "").upper()
    return {
        "pays": code,
        "jalons": [j for j in JALONS if j["pays"] == code],
        "reserves": [r for r in RESERVES if r["pays"] == code],
    }


def assemble():
    return {
        "version": VERSION,
        "genere": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": SOURCES,
        "tendances": TENDANCES,
        "jalons": JALONS,
        "marche": MARCHE,
        "reserves": RESERVES,
        "avertissement":
            "Prospectives issues de rapports d'éditeurs nommés, chaque entrée portant sa "
            "citation et sa page. Une prévision n'est pas une donnée : les entrées de nature "
            "« prevision » engagent leur auteur, pas la réalité. Les RÉSERVES signalent les "
            "valeurs du référentiel qu'un fait postérieur rend optimistes ou incomplètes — "
            "elles ne les corrigent pas d'office.",
    }


def sante():
    """Compte ce qui doit rester vrai. Les deux derniers champs sont les seuls
    qui comptent vraiment : une entrée sans page n'est pas vérifiable, et une
    entrée dont on aurait retiré la citation en la retouchant se verrait ici."""
    tout = TENDANCES + JALONS + MARCHE
    return {"module": "tendances_dc", "version": VERSION,
            "tendances": len(TENDANCES), "jalons": len(JALONS),
            "faits_marche": len(MARCHE), "reserves": len(RESERVES),
            "sources": len(SOURCES),
            "citations_verbatim": len([x for x in tout if x.get("citation")]),
            "entrees_reformulees": len([x for x in tout if not x.get("citation")]),
            "sans_page": [x.get("cle") for x in tout if not x.get("page")],
            # Une réserve dont le jalon a été renommé s'affiche sans son fait
            # déclencheur : elle accuse le référentiel sans dire au nom de quoi.
            "reserves_orphelines": [r["pays"] for r in RESERVES
                                    if r["jalon"] not in {j["cle"] for j in JALONS}],
            "sources_amont": len([x for x in tout if x.get("source_amont")]),
            "pays_couverts": sorted({j["pays"] for j in JALONS}),
            "horodatage": datetime.now(timezone.utc).isoformat(timespec="seconds")}
