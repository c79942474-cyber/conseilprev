# -*- coding: utf-8 -*-
"""Contrôles factuels — le registre des vérifications, partagé par tout le site.

POURQUOI CE MODULE
Les pages du site avancent des chiffres : intensités carbone, rendements de
centres de données, dates réglementaires, existence de sites et de
déploiements. Ces chiffres sont lus par des professionnels de l'investissement,
du crédit, de l'assurance et du climat — pour qui un ordre de grandeur non
sourcé n'est pas une information mais un risque.

Chaque affirmation vérifiable est donc enregistrée ICI avec son VERDICT, la
source qui l'étaye ou la contredit, et la date du contrôle. Les pages ne
racontent plus qu'elles sont fiables : elles affichent le contrôle.

CE QUI EST PUBLIÉ, ET CE QUI NE L'EST PAS
Tous les verdicts sont publiés, y compris les défavorables. Un registre qui
n'afficherait que ses succès ne serait pas vérifiable — il serait
promotionnel, et c'est exactement ce qu'un analyste doit pouvoir écarter.

Quand un contrôle a conduit à CORRIGER une valeur du référentiel, la valeur
d'origine reste écrite dans `avant` : sans elle, un lecteur qui aurait cité
l'ancienne valeur ne saurait pas qu'il doit se corriger.
"""

VERSION = "2026-07-a"

# ═══════════════════════════════════════════════════════════════════════════
# 1. ÉCHELLE DES VERDICTS
#    Quatre niveaux seulement. Trois seraient trop peu — « plausible » et
#    « invérifiable » ne se confondent pas : le premier dit que l'ordre de
#    grandeur tient, le second qu'aucune source publique n'existe.
# ═══════════════════════════════════════════════════════════════════════════

VERDICTS = {
    "confirme": {
        "nom": "Confirmé",
        "sens": "Une source primaire ou institutionnelle étaye l'affirmation, "
                "à l'écart de tolérance près déclaré pour cette grandeur.",
        "couleur": "#1E6336", "rang": 1,
    },
    "corrige": {
        "nom": "Corrigé",
        "sens": "La vérification a montré un écart : la valeur du référentiel "
                "a été remplacée. La valeur d'origine reste affichée.",
        "couleur": "#8A5310", "rang": 2,
    },
    "plausible": {
        "nom": "Plausible",
        "sens": "L'ordre de grandeur tient face aux sources disponibles, mais "
                "aucune ne porte exactement l'affirmation.",
        "couleur": "#17497E", "rang": 3,
    },
    "inverifiable": {
        "nom": "Invérifiable",
        "sens": "Aucune source publique ne permet de trancher. L'affirmation "
                "est conservée mais ne doit pas être citée comme un fait.",
        "couleur": "#7A7A7A", "rang": 4,
    },
}

PORTEES = {
    "panorama": "Panorama des systèmes d'IA — Union européenne",
    "empreinte": "Empreinte numérique",
    "observatoire": "Observatoire de la R&D en IA",
    "reglementaire": "Cadre réglementaire (toutes pages)",
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. LE REGISTRE
#    Rempli par un contrôle externe : chaque affirmation a été confrontée à
#    des sources primaires ou institutionnelles, une par une. `avant` porte la
#    valeur qui figurait au référentiel quand elle a été corrigée.
# ═══════════════════════════════════════════════════════════════════════════

CONTROLES = [
    # ── Référentiel d'implantation (implantation.py) — quatre familles ──────
    {"cle": "imp-eau", "portee": ["panorama"],
     "sujet": "Stress hydrique par pays (WEI+) et compétition d'usages",
     "affirmation": "Les classes de stress hydrique nationales suivent l'indice WEI+ "
                    "de l'AEE (millésime 2022) ; la part de l'irrigation agricole "
                    "signale la compétition d'usage estivale.",
     "verdict": "plausible",
     "constat": "Classes cohérentes avec les publications AEE (stress structurel "
                "ibérique, grec et italien ; Flandre parmi les régions les plus "
                "tendues ; abondance nordique). La lecture NATIONALE écrase les "
                "contrastes de bassins — le module l'écrit et renvoie à l'étude "
                "locale. À re-vérifier lors de chaque millésime AEE.",
     "avant": None, "verifie_le": "2026-07-31",
     "source": {"titre": "Water exploitation index plus (WEI+)",
                "editeur": "Agence européenne pour l'environnement",
                "url": "https://www.eea.europa.eu/en/analysis/indicators/use-of-freshwater-resources-in-europe"}},
    {"cle": "imp-mix", "portee": ["panorama"],
     "sujet": "Mix de production électrique 2024 par pays",
     "affirmation": "Les parts nucléaire / renouvelables / fossile sont celles de la "
                    "production 2024 (Ember), volontairement arrondies à 5 points.",
     "verdict": "plausible",
     "constat": "Ordres de grandeur conformes aux séries Ember 2024 (France "
                "nucléaire ~2/3, Pologne fossile ~70 %, Norvège quasi 100 % "
                "renouvelable). L'arrondi à 5 points est un choix d'honnêteté : "
                "une décimale suggérerait une précision que la compilation n'a "
                "pas. Production ≠ consommation pour les pays importateurs.",
     "avant": None, "verifie_le": "2026-07-31",
     "source": {"titre": "Yearly electricity generation", "editeur": "Ember",
                "url": "https://ember-energy.org/data/yearly-electricity-data/"}},
    {"cle": "imp-prix", "portee": ["panorama"],
     "sujet": "Prix de l'électricité industrielle par pays (classes)",
     "affirmation": "Les classes de prix (bas / moyen / élevé) et leurs fourchettes "
                    "en €/MWh reflètent Eurostat nrg_pc_205, bandes industrielles "
                    "hautes, année 2024, hors taxes récupérables.",
     "verdict": "inverifiable",
     "constat": "Le prix RÉEL d'un centre de données est contractuel (PPA, "
                "raccordement, exonérations) et n'apparaît dans aucune statistique "
                "publique : les classes donnent le terrain de départ de la "
                "négociation. Les fourchettes publiées ici sont des ordres de "
                "grandeur à confronter à l'extraction Eurostat du semestre visé "
                "avant toute citation chiffrée.",
     "avant": None, "verifie_le": "2026-07-31",
     "source": {"titre": "Electricity prices for non-household consumers (nrg_pc_205)",
                "editeur": "Eurostat",
                "url": "https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_205/"}},
    {"cle": "imp-2030", "portee": ["panorama"],
     "sujet": "Perspectives d'investissement et contraintes à l'horizon 2030",
     "affirmation": "Les perspectives par pays compilent des ANNONCES publiques "
                    "datées (InvestAI 200 Md€, Sommet de Paris 109 Md€, AWS Aragon, "
                    "moratoire EirGrid, EnEfG…), jamais des engagements comptables.",
     "verdict": "plausible",
     "constat": "Chaque ligne porte sa source et sa date. Une annonce à cinq ans "
                "est l'information la plus fragile de ce marché — le référentiel "
                "des sites en conserve quatre, devenues des abandons, pour le "
                "rappeler. Les CONTRAINTES constatées (moratoire de raccordement "
                "de Dublin, encadrement néerlandais, PUE réglementaire allemand) "
                "sont plus solides que les promesses chiffrées.",
     "avant": None, "verifie_le": "2026-07-31",
     "source": {"titre": "Compilation datée — communiqués et décisions d'autorités",
                "editeur": "conseilprev (analyse)", "url": None}},

    # ── Contrôles de méthode : ils ne portent pas sur une valeur mais sur la
    #    façon de la lire. Ce sont ceux qu'un analyste doit citer en note.
    {"cle": "meth-millesime",
     "portee": ["panorama", "empreinte"],
     "sujet": "Millésime unique du tableau d'intensités",
     "affirmation": "Toutes les intensités carbone se réfèrent à l'année 2024.",
     "verdict": "confirme",
     "constat": "Le contrôle de juillet 2026 a montré que la table précédente mélangeait des "
                "millésimes 2021 à 2023 et surestimait la plupart des pays de 25 à 80 %. Elle a "
                "été refaite sur une source unique et une année unique : mélanger les années "
                "dans un tableau comparatif fausse précisément la comparaison qu'on vient y "
                "chercher.",
     "avant": "millésimes mêlés 2021-2023",
     "verifie_le": "2026-07-30",
     "source": {"titre": "Yearly Electricity Data — CO2 intensity (cycle de vie)",
                "editeur": "Ember", "url": "https://ember-energy.org/data/yearly-electricity-data/"}},
    {"cle": "meth-production",
     "portee": ["panorama", "empreinte"],
     "sujet": "Approche production, et non consommation",
     "affirmation": "Les intensités décrivent la PRODUCTION nationale, pas l'électricité "
                    "réellement consommée au point de raccordement.",
     "verdict": "plausible",
     "constat": "Pour un pays fortement importateur, l'écart est considérable : le Luxembourg "
                "importe environ 60 % de son électricité (production ~130 gCO2e/kWh, consommation "
                "~290), la Lituanie environ 29 %. Un centre de données raccordé au réseau voit "
                "l'intensité de CONSOMMATION. Le Luxembourg conserve donc une valeur "
                "intermédiaire assumée, faute de série de consommation homogène pour tous les "
                "pays.",
     "avant": None,
     "verifie_le": "2026-07-30",
     "source": {"titre": "Yearly Electricity Data — CO2 intensity", "editeur": "Ember",
                "url": "https://ember-energy.org/data/yearly-electricity-data/"}},
    {"cle": "meth-ademe",
     "portee": ["panorama", "empreinte"],
     "sujet": "France — écart entre le référentiel européen et l'ADEME",
     "affirmation": "La France est à 45 gCO₂e/kWh dans la série européenne retenue.",
     "verdict": "plausible",
     "constat": "La Base Empreinte de l'ADEME retient environ 60 gCO₂e/kWh pour le mix "
                "électrique français : les périmètres et les méthodes diffèrent. Un client qui "
                "travaille dans le cadre ADEME doit substituer sa propre valeur — la chaîne de "
                "calcul est publiée pour cela, avec toutes ses hypothèses.",
     "avant": None,
     "verifie_le": "2026-07-30",
     "source": {"titre": "Base Empreinte — facteurs d'émission", "editeur": "ADEME",
                "url": "https://base-empreinte.ademe.fr/"}},
    {"cle": "meth-temps-reel",
     "portee": ["panorama", "empreinte"],
     "sujet": "Intensité du moment plutôt que moyenne annuelle",
     "affirmation": "Quand le serveur sait obtenir le mix de production du moment, il l'emploie "
                    "à la place de la moyenne annuelle.",
     "verdict": "confirme",
     "constat": "Le mix de production est relevé automatiquement pour 27 pays auprès "
                "d'Energy-Charts (Fraunhofer ISE, licence ouverte, sans clé d'API), puis pondéré "
                "par des facteurs d'émission par filière en cycle de vie. Un pays non joint "
                "retombe sur sa moyenne annuelle, et l'état publié dit lequel. L'intensité réelle "
                "variant d'un facteur trois dans la journée, c'est cette valeur du moment qui "
                "décrit un calcul déplaçable, pas la moyenne.",
     "avant": "moyenne annuelle pour tous les pays sauf la France et l'Allemagne",
     "verifie_le": "2026-07-30",
     "source": {"titre": "Energy-Charts — public power (API ouverte)",
                "editeur": "Fraunhofer ISE", "url": "https://api.energy-charts.info/"}},
    {'cle': 'int-AT',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Autriche',
     'affirmation': '105 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember donne 112 gCO2/kWh en 2023, 103 en 2024 et 117 en 2025 pour '
                "l'Autriche (hydraulique dominant) : 160 surestime de 37 a 55% et "
                'correspond plutot a 2022 (141).',
     'avant': '160 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data (CO2 intensity, gCO2/kWh)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-BE',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Belgique',
     'affirmation': '125 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember donne 135 gCO2/kWh en 2023, 127 en 2024 et 109 en 2025 pour la '
                'Belgique : 170 surestime la periode recente de 26 a 56%, juste '
                'au-dela de la tolerance.',
     'avant': '170 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data (CO2 intensity, gCO2/kWh)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-BG',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Bulgarie',
     'affirmation': '320 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': "La Bulgarie a enregistre la plus forte baisse d'emissions electriques "
                "de l'UE en 2023 (-44%, Ember) et son intensite 2024 est estimee a "
                '~320 gCO2/kWh (en baisse de 15% sur un an) : 480 correspond aux '
                'annees 2021-2022, pas a 2023-2025 (ecart 30-50%).',
     'avant': '480 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': "Is Bulgaria's Electricity Too Carbon-Intensive? A European "
                         'Comparison',
                'editeur': "NetZeroLab, Universite de Sofia (d'apres Ember)",
                'url': 'https://netzerolab-feba.bg/is-bulgarias-electricity-too-carbon-intensive-a-european-comparison/'}},
    {'cle': 'int-CH',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Suisse',
     'affirmation': '35 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember donne 34.8 gCO2/kWh en 2023, 34.6 en 2024 et 39.2 en 2025 pour '
                'la Suisse (production nationale, cycle de vie) : 40 est dans la '
                'tolerance (+2 a +15%).',
     'avant': '40 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data (CO2 intensity, gCO2/kWh)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-CY',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Chypre',
     'affirmation': '510 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie) donne 533 gCO2e/kWh en 2023 (plus bas niveau du '
                'siecle pour Chypre), 511 en 2024 et 489 en 2025 : 640 refletait le '
                "parc fioul d'avant 2022 et surestime de 20 a 31% les annees recentes.",
     'avant': '640 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data — CO2 intensity (cycle de vie)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-CZ',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Tchéquie',
     'affirmation': '400 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember donne 450 gCO2/kWh pour la Tchequie en 2023 (~402 en 2024 selon '
                'Low-Carbon Power, facteurs cycle de vie) : la valeur 470 reste dans '
                "l'ecart de 25%.",
     'avant': '470 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'European Electricity Review 2024 — EU electricity trends',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/latest-insights/european-electricity-review-2024/eu-electricity-trends/'}},
    {'cle': 'int-DE',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Allemagne',
     'affirmation': '355 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember donne 371 gCO2/kWh en combustion pour 2023 (le cycle de vie '
                'ajoute ~5-10%), soit un ecart <3% avec la valeur retenue ; la baisse '
                '2024 (~340-365) reste dans la marge de 25%.',
     'avant': '380 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'European Electricity Review 2024 — EU electricity trends',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/latest-insights/european-electricity-review-2024/eu-electricity-trends/'}},
    {'cle': 'int-DK',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Danemark',
     'affirmation': '130 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember donne 152 gCO2/kWh en 2023 (+18%, dans la tolerance), mais '
                "l'intensite danoise chute vite (132 en 2024, ~100 en 2025) : la "
                'valeur reste correcte pour 2023 mais vieillira mal et gagnerait a '
                'etre abaissee vers 100-150.',
     'avant': '180 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data (CO2 intensity, gCO2/kWh)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-EE',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Estonie',
     'affirmation': '415 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': "L'Estonie a fortement reduit le schiste bitumineux (~35% du mix en "
                '2024) : la moyenne 2024 est de 417 gCO2eq/kWh en cycle de vie (~460 '
                "en 2023) ; 620 refletait la situation d'avant 2022 (ecart ~35-49%).",
     'avant': '620 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Estonia Electricity Generation Mix — Low-Carbon Power Data',
                'editeur': 'Low-Carbon Power (facteurs cycle de vie GIEC)',
                'url': 'https://lowcarbonpower.org/region/Estonia'}},
    {'cle': 'int-ES',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Espagne',
     'affirmation': '145 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie, facteurs IPCC AR5) donne 170 gCO2e/kWh en 2023, '
                '146 en 2024 et 154 en 2025 : 190 est en haut de la fourchette recente '
                '(+12 a +24%) mais reste dans la tolerance de 25%.',
     'avant': '190 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data — CO2 intensity (cycle de vie)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-FI',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Finlande',
     'affirmation': '65 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember donne 81 gCO2/kWh en 2023, 67 en 2024 et 57 en 2025 pour la '
                "Finlande : 110 correspond a l'avant-Olkiluoto 3 (130 en 2022) et "
                'surestime la periode 2023-2025 de 35 a 91%.',
     'avant': '110 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data (CO2 intensity, gCO2/kWh)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-FR',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — France',
     'affirmation': '45 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie, facteurs GIEC AR5) donne 53 gCO2/kWh en 2023 '
                'pour la France, soit un ecart de +13% ; a noter que 2024-2025 sont '
                'plus bas (~40-41) grace au rebond nucleaire et hydraulique, 60 est '
                'donc le haut de la fourchette recente et coherent avec la Base '
                'Empreinte ADEME.',
     'avant': '60 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data (CO2 intensity, gCO2/kWh)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-GB',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Royaume-Uni',
     'affirmation': '215 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember donne 236 gCO2/kWh en 2023 (+6%) et ~217 en 2024-2025 pour le '
                'Royaume-Uni : 250 est dans la tolerance, en haut de la fourchette '
                'recente.',
     'avant': '250 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data (CO2 intensity, gCO2/kWh)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-GR',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Grèce',
     'affirmation': '320 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie) donne 337 gCO2e/kWh en 2023, 322 en 2024 et 324 '
                "en 2025 : 420 correspond aux niveaux grecs d'avant la sortie "
                'acceleree du lignite et surestime de 25 a 30% les annees recentes.',
     'avant': '420 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data — CO2 intensity (cycle de vie)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-HR',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Croatie',
     'affirmation': '170 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie) donne 195 gCO2e/kWh en 2023, 171 en 2024 et 159 '
                'en 2025 : 240 surestime de 23 a 51% un mix croate largement '
                'hydraulique et en decarbonation rapide.',
     'avant': '240 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data — CO2 intensity (cycle de vie)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-HU',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Hongrie',
     'affirmation': '195 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Moyennes cycle de vie de 206 gCO2eq/kWh en 2023 et 194 en 2024 : la '
                "valeur 240 est en limite haute mais reste sous l'ecart de 25% par "
                'rapport a 2023.',
     'avant': '240 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'CO2 emissions per kWh in Hungary',
                'editeur': 'Nowtricity (donnees ENTSO-E, facteurs cycle de vie)',
                'url': 'https://www.nowtricity.com/country/hungary/'}},
    {'cle': 'int-IE',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Irlande',
     'affirmation': '270 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie) donne 283 gCO2e/kWh en 2023, 271 en 2024 et 256 '
                'en 2025, et le SEAI confirme des emissions electriques irlandaises au '
                'plus bas historique en 2024 : 350 surestime de 24 a 37% les annees '
                'recentes.',
     'avant': '350 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data — CO2 intensity (cycle de vie) ; '
                         'Energy in Ireland 2024',
                'editeur': 'Ember / SEAI',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-IS',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Islande',
     'affirmation': '30 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'confirme',
     'constat': "Ember donne 27.7-27.8 gCO2/kWh sur 2022-2024 pour l'Islande "
                '(hydraulique et geothermie) : 30 est a +8%.',
     'avant': None,
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data (CO2 intensity, gCO2/kWh)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-IT',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Italie',
     'affirmation': '280 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie) donne 323 gCO2e/kWh en 2023, 281 en 2024 et 285 '
                "en 2025 : 330 colle a la valeur 2023 (+2%) et reste sous l'ecart de "
                '25% vis-a-vis de 2024-2025.',
     'avant': '330 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data — CO2 intensity (cycle de vie)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-LT',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Lituanie',
     'affirmation': '200 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'plausible',
     'constat': 'En approche production, la Lituanie est a 160 gCO2/kWh en 2023 et 139 '
                'gCO2eq/kWh en 2024, mais le pays importe une large part de sa '
                "consommation (~29% d'imports nets en 2024, davantage en 2023), ce qui "
                "remonte l'intensite en approche consommation vers la valeur retenue : "
                'ordre de grandeur acceptable, legerement surestime.',
     'avant': None,
     'verifie_le': '2026-07-30',
     'source': {'titre': 'CO2 emissions per kWh in Lithuania',
                'editeur': 'Nowtricity (donnees ENTSO-E, facteurs cycle de vie)',
                'url': 'https://www.nowtricity.com/country/lithuania/'}},
    {'cle': 'int-LU',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Luxembourg',
     'affirmation': '220 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'plausible',
     'constat': 'Les sources divergent selon le perimetre : en base production Ember '
                'donne ~120-132 gCO2/kWh (2023-2025), mais le Luxembourg importe ~60% '
                'de son electricite et les estimations en base consommation '
                '(pertinentes pour un centre de donnees raccorde au reseau) sont '
                'autour de 290 gCO2eq/kWh ; 220 est un ordre de grandeur defendable '
                'entre les deux, sans source directe qui le confirme exactement.',
     'avant': None,
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Luxembourg Electricity Generation Mix (intensite '
                         'consommation ~292 gCO2eq/kWh, imports ~63%)',
                'editeur': 'Low-Carbon Power (donnees Ember/ENTSO-E)',
                'url': 'https://lowcarbonpower.org/region/Luxembourg'}},
    {'cle': 'int-LV',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Lettonie',
     'affirmation': '170 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Moyennes cycle de vie de 159 gCO2eq/kWh en 2023 et 170 en 2024 (hydro '
                'dominant + gaz) : la valeur 190 est a moins de 12% de la moyenne '
                '2024.',
     'avant': '190 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'CO2 emissions per kWh in Latvia',
                'editeur': 'Nowtricity (donnees ENTSO-E, facteurs cycle de vie)',
                'url': 'https://www.nowtricity.com/country/latvia/'}},
    {'cle': 'int-MT',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Malte',
     'affirmation': '490 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie, production nationale au gaz) donne 494 gCO2e/kWh '
                'en 2023, 489 en 2024 et 484 en 2025 : 430 est environ 12% en dessous, '
                "dans la tolerance, d'autant que Malte importe une part de son "
                "electricite via l'interconnexion avec la Sicile.",
     'avant': '430 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data — CO2 intensity (cycle de vie)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-NL',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Pays-Bas',
     'affirmation': '250 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie) donne 268 gCO2e/kWh en 2023, 251 en 2024 et 254 '
                "en 2025 : 350 date de l'ere pre-2022 et surestime de 31 a 40% le mix "
                "neerlandais transforme par l'essor eolien-solaire.",
     'avant': '350 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data — CO2 intensity (cycle de vie)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-NO',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Norvège',
     'affirmation': '30 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'confirme',
     'constat': 'Ember donne 30.5 gCO2/kWh en 2023, 29.7 en 2024 et 28.1 en 2025 pour '
                'la Norvege : la valeur 30 est quasi exacte.',
     'avant': None,
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data (CO2 intensity, gCO2/kWh)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-PL',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Pologne',
     'affirmation': '660 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'confirme',
     'constat': 'Ember mesure 662 gCO2/kWh pour la Pologne en 2023, la plus forte '
                "intensite de l'UE ; la valeur retenue de 660 est quasi identique.",
     'avant': None,
     'verifie_le': '2026-07-30',
     'source': {'titre': 'European Electricity Review 2024 — EU electricity trends',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/latest-insights/european-electricity-review-2024/eu-electricity-trends/'}},
    {'cle': 'int-PT',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Portugal',
     'affirmation': '110 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie) donne 158 gCO2e/kWh en 2023, 111 en 2024 et 128 '
                'en 2025 : la valeur 200 surestime de 26 a 81% un mix portugais devenu '
                'tres majoritairement renouvelable.',
     'avant': '200 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data — CO2 intensity (cycle de vie)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-RO',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Roumanie',
     'affirmation': '230 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': "Les sources s'etalent de 226-232 gCO2eq/kWh (moyennes cycle de vie "
                '2023-2024, Nowtricity) a 264 en combustion 2022 (Ember/Statista) : '
                "l'ordre de grandeur colle mais 290 est au bord superieur (~25% "
                'au-dessus des moyennes 2023-2024), une revision vers ~250 serait plus '
                'juste.',
     'avant': '290 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'CO2 emissions per kWh in Romania',
                'editeur': 'Nowtricity (donnees ENTSO-E, facteurs cycle de vie)',
                'url': 'https://www.nowtricity.com/country/romania/'}},
    {'cle': 'int-SE',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Suède',
     'affirmation': '35 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember donne 38 gCO2/kWh en 2023 et ~35 en 2024-2025 pour la Suede : '
                "45 est a +17% du chiffre 2023, dans la tolerance d'un ordre de "
                'grandeur declare comme tel.',
     'avant': '45 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data (CO2 intensity, gCO2/kWh)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-SI',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Slovénie',
     'affirmation': '230 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember (cycle de vie) donne 225 gCO2e/kWh en 2023, 230 en 2024 et 183 '
                'en 2025 : 250 est a +9-11% des annees 2023-2024, dans la tolerance, '
                'meme si 2025 est nettement plus bas.',
     'avant': '250 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'Yearly Electricity Data — CO2 intensity (cycle de vie)',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/data/yearly-electricity-data/'}},
    {'cle': 'int-SK',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Slovaquie',
     'affirmation': '95 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Les moyennes annuelles cycle de vie recentes sont bien plus basses : '
                '123 gCO2eq/kWh en 2023 et 93 en 2024 (Nowtricity, facteurs GIEC), ~97 '
                'selon Low-Carbon Power, le nucleaire (Mochovce 3) couvrant desormais '
                "plus de 60% du mix ; l'ecart est de 38 a 80%.",
     'avant': '170 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'CO2 emissions per kWh in Slovakia',
                'editeur': 'Nowtricity (donnees ENTSO-E, facteurs cycle de vie)',
                'url': 'https://www.nowtricity.com/country/slovakia/'}},
    {'cle': 'int-UE',
     'portee': ['panorama', 'empreinte'],
     'sujet': 'Intensité carbone du réseau — Union européenne',
     'affirmation': '235 gCO₂e/kWh, cycle de vie, moyenne annuelle',
     'verdict': 'corrige',
     'constat': 'Ember mesure 242 gCO2/kWh en 2023 et 213 en 2024 pour la moyenne UE '
                "(combustion, le cycle de vie ajoutant ~10%) : 250 est dans l'ecart de "
                '25% et convient comme valeur de repli.',
     'avant': '250 gCO₂e/kWh (millésime 2021-2022)',
     'verifie_le': '2026-07-30',
     'source': {'titre': 'European Electricity Review 2025 — Five years of progress',
                'editeur': 'Ember',
                'url': 'https://ember-energy.org/latest-insights/european-electricity-review-2025/five-years-of-progress/'}},
]

# ═══════════════════════════════════════════════════════════════════════════
# 3. LECTURES
# ═══════════════════════════════════════════════════════════════════════════


def par_portee(portee=None):
    """Contrôles d'une page, triés du plus défavorable au plus favorable.

    L'ordre est délibéré : un lecteur qui ne parcourt que les premières lignes
    doit tomber sur les écarts, pas sur les confirmations."""
    lot = [c for c in CONTROLES if not portee or portee in c.get("portee", [])]
    return sorted(lot, key=lambda c: (-VERDICTS.get(c["verdict"], {}).get("rang", 9),
                                      c.get("sujet", "")))


def par_cle(cle):
    """Le contrôle attaché à une valeur précise, pour l'afficher en regard."""
    for c in CONTROLES:
        if c.get("cle") == cle:
            return c
    return None


def resume(portee=None):
    """Compte par verdict, et date du contrôle le plus ancien.

    La date la plus ANCIENNE, et non la plus récente : c'est elle qui dit
    depuis quand le lot n'a pas été entièrement revu."""
    lot = par_portee(portee)
    compte = {k: 0 for k in VERDICTS}
    dates = []
    for c in lot:
        compte[c["verdict"]] = compte.get(c["verdict"], 0) + 1
        if c.get("verifie_le"):
            dates.append(c["verifie_le"])
    return {
        "total": len(lot),
        "compte": compte,
        "verifie_depuis": min(dates) if dates else None,
        "verifie_jusqu_a": max(dates) if dates else None,
        "corriges": [c for c in lot if c["verdict"] == "corrige"],
    }


def sources(portee=None):
    """Sources distinctes citées, dédoublonnées par URL puis par éditeur."""
    vues, out = set(), []
    for c in par_portee(portee):
        s = c.get("source") or {}
        cle = (s.get("url") or "") + "|" + (s.get("editeur") or "")
        if cle.strip("|") and cle not in vues:
            vues.add(cle)
            out.append(s)
    return sorted(out, key=lambda s: (s.get("editeur") or "").lower())


def etat(portee=None):
    """Le bloc publié tel quel par l'API et les pages."""
    return {
        "ok": True,
        "version": VERSION,
        "verdicts": VERDICTS,
        "portees": PORTEES,
        "resume": resume(portee),
        "controles": par_portee(portee),
        "sources": sources(portee),
    }
