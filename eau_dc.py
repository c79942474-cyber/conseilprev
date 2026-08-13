# -*- coding: utf-8 -*-
"""L’eau de la SOURCE : ce que le WUE de site ne dit pas.

POURQUOI CE MODULE EXISTE

La page publiait, pour les centres cartographiés, l’eau consommée SUR LE
SITE — le volume d’appoint des tours et des systèmes adiabatiques. C’est le
chiffre que tout le monde publie, celui qu’exige le règlement délégué (UE)
2024/1364, et celui que compare la presse.

Il est incomplet, et son incomplétude va toujours dans le même sens.

Produire un kilowattheure consomme de l’eau : les centrales thermiques et
nucléaires en évaporent dans leurs tours aéroréfrigérantes. Un centre de
données qui remplace son refroidissement évaporatif par un refroidissement sec
affiche alors un WUE de site NUL — tout en consommant davantage d’électricité,
donc davantage d’eau en amont. Sur un mix thermique, l’arbitrage s’inverse : le
dossier qui ne regarde que le site conclut à l’envers de ce qu’il faut faire.

CE QUE CE MODULE AJOUTE, ET CE QU’IL N’AJOUTE PAS

Il ajoute le second terme du bilan : l’eau consommée en amont par la production
de l’électricité achetée, pays par pays, sur le parc réellement cartographié.
Il rend visible le rapport entre les deux, qui est la seule grandeur qui permet
d’arbitrer.

Il n’ajoute AUCUNE mesure. Les facteurs eau de la production électrique sont
des ordres de grandeur de la littérature, à ±40 %, et ils varient davantage
selon la technologie de refroidissement des centrales que selon le mix. Ils
portent donc la nature `ordre_grandeur` et non `referentiel`, et le module
refuse de les présenter autrement : sur douze des vingt-trois pays du parc,
aucune valeur nationale n’existe et c’est la moyenne européenne qui sert — ce
qui est écrit à chaque fois plutôt que dissous dans un total.

PROVENANCE

Le référentiel EWIF, la borne physique d’évaporation et le cadre EED
proviennent du moteur d’ingénierie `datacenter.py` de conseilprevcyber, dont
c’est le domaine. Ils sont repris ici sans être retouchés : deux copies d’un
référentiel qui divergent valent moins qu’une seule qui se cite.
"""
from __future__ import annotations

VERSION = "2026-08-a"

# ═══════════════════════════════════════════════════════════════════════════
#  RÉFÉRENTIEL
# ═══════════════════════════════════════════════════════════════════════════

PROVENANCE = {
    "module": "datacenter.py — moteur d’ingénierie centres de données bas carbone",
    "site": "conseilprevcyber",
    "version_amont": "2026-08-a",
    "note": "Référentiel repris sans retouche. Toute correction se fait en amont, "
            "puis se reporte ici : deux copies qui divergent valent moins qu’une "
            "seule qui se cite.",
}

# Borne PHYSIQUE de l’évaporation : l’eau qu’il faut évaporer pour évacuer un
# kilowattheure de chaleur. Elle ne dépend d’aucune technologie — c’est la
# chaleur latente de vaporisation de l’eau. Aucune tour ne fait mieux, et un
# fournisseur qui annonce moins décrit soit un refroidissement partiellement
# sec, soit une erreur.
BORNE_EVAPORATION = {
    "valeur_l_par_kwh_thermique": round(3600.0 / 2442.0, 3),   # ≈ 1,474
    "nature": "physique",
    "formule": "1 kWh = 3 600 kJ ; 3 600 ÷ chaleur latente (2 442 kJ/kg à 25 °C)",
    "source": "Chaleur latente de vaporisation de l’eau, tables thermodynamiques usuelles",
    "note": "La chaleur latente varie de 2 501 kJ/kg à 0 °C à 2 406 kJ/kg à 40 °C ; "
            "l’écart sur la plage d’exploitation reste sous 2 %.",
}

# Facteur eau de la production électrique — EWIF, Energy Water Intensity Factor.
# C’est l’eau CONSOMMÉE (évaporée, non restituée au milieu), et non l’eau
# PRÉLEVÉE : confondre les deux change le résultat d’un facteur dix sur un parc
# nucléaire en circuit ouvert, et c’est l’erreur la plus fréquente des dossiers.
EWIF_PAYS = {
    "FR": {"valeur": 1.30, "mix": "nucléaire majoritaire, hydraulique",
           "note": "Forte évaporation des tours aéroréfrigérantes du parc nucléaire."},
    "DE": {"valeur": 1.10, "mix": "renouvelables, gaz, charbon résiduel"},
    "SE": {"valeur": 0.45, "mix": "hydraulique, nucléaire, éolien"},
    "NO": {"valeur": 0.30, "mix": "hydraulique quasi exclusif"},
    "FI": {"valeur": 0.55, "mix": "nucléaire, biomasse, hydraulique"},
    "IE": {"valeur": 0.55, "mix": "éolien, gaz"},
    "NL": {"valeur": 0.80, "mix": "gaz, éolien offshore"},
    "ES": {"valeur": 1.00, "mix": "solaire, éolien, gaz, nucléaire"},
    "IT": {"valeur": 1.05, "mix": "gaz, hydraulique, solaire"},
    "PL": {"valeur": 1.60, "mix": "charbon majoritaire"},
    "DK": {"valeur": 0.35, "mix": "éolien majoritaire"},
}
EWIF_DEFAUT = {"valeur": 1.00, "mix": "moyenne européenne",
               "note": "Employée à défaut de valeur nationale. Ce n’est pas une "
                       "mesure du pays : c’est l’aveu qu’on n’en a pas."}
EWIF_SOURCE = ("Ordres de grandeur convergents de la littérature sur l’intensité en "
               "eau de la production électrique — eau consommée, hors prélèvement "
               "restitué. À REMPLACER par la valeur du fournisseur ou du "
               "gestionnaire de réseau dès qu’elle est disponible : ces facteurs "
               "varient fortement selon la technologie de refroidissement des "
               "centrales, pas seulement selon le mix.")
EWIF_INCERTITUDE = "±40 %"
EWIF_NATURE = "ordre_grandeur"

# Le cadre européen qui rend ces grandeurs déclarables — et donc opposables.
CADRE_EED = {
    "titre": "Directive efficacité énergétique (UE) 2023/1791, art. 12, et "
             "règlement délégué (UE) 2024/1364",
    "seuil_kw_it": 500,
    "portee": "Centres de données dont la puissance informatique installée atteint "
              "ou dépasse 500 kW.",
    "exige": [
        "consommation d’énergie totale",
        "PUE — efficacité de l’usage de l’énergie",
        "consommation d’eau et WUE",
        "part d’énergie renouvelable (REF)",
        "chaleur fatale réutilisée (ERF)",
        "trafic de données entrant et sortant",
        "quantité de données stockées",
        # Une seule entrée, comme au référentiel amont : la scinder en deux
        # faisait annoncer NEUF grandeurs ici et HUIT sur conseilprevcyber, pour
        # le même texte réglementaire. Deux sites qui comptent différemment les
        # obligations d’un règlement se contredisent devant le même lecteur ;
        # c’est le module d’origine qui fait foi.
        "surface, puissance installée, taux d’utilisation",
    ],
    "note": "Déclaration annuelle. Le WUE exigé est celui du SITE : la déclaration "
            "réglementaire ne couvre donc pas l’eau de la source, et un parc "
            "parfaitement conforme peut voir sa consommation d’eau réelle croître "
            "en passant au refroidissement sec.",
    "nature": "referentiel",
}

# Correspondance entre les modes de refroidissement du référentiel des sites et
# la part de chaleur évacuée par voie évaporative. C’est CE paramètre qui porte
# tout le compromis eau/énergie.
PART_EVAPORATIVE = {
    "eau": {"part": 0.90, "nom": "Tour évaporative / circuit d’eau",
            "note": "Le meilleur compromis énergétique historique, et le plus "
                    "exposé au risque eau."},
    "adiabatique": {"part": 0.25, "nom": "Free cooling indirect à assistance adiabatique",
                    "note": "L’eau n’est consommée que pendant les heures chaudes : "
                            "le WUE annuel masque des pointes estivales, qui sont "
                            "précisément le moment où la ressource est tendue."},
    "free_cooling": {"part": 0.0, "nom": "Free cooling direct sur air",
                     "note": "Aucune eau sur le site — toute l’eau du bilan est en amont."},
    # Présent au référentiel des modes de `datacentres.py` sans être porté par
    # aucun site du parc. Il figure quand même : sans son nom, le tableau des
    # modes affichait la clé brute « air », ce qui se lit comme un défaut.
    "air": {"part": 0.0, "nom": "Détente directe (DX) sur air",
            "note": "Sans eau sur le site, mais le mode le plus consommateur "
                    "d’électricité — donc le plus consommateur d’eau en amont."},
    "recuperation_chaleur": {"part": 0.10, "nom": "Récupération de chaleur fatale",
                             "note": "La chaleur exportée n’est pas à évacuer : "
                                     "elle sort du bilan eau du site."},
    "inconnu": {"part": None, "nom": "Mode non publié",
                "note": "Aucune part évaporative ne peut être posée sans inventer "
                        "une conception : ces sites ne reçoivent pas d’estimation "
                        "de part évaporative."},
}
PART_SOURCE = ("Parts d’évaporation par famille de refroidissement, moteur "
               "d’ingénierie datacenter.py (conseilprevcyber). Valeurs de "
               "cadrage : une étude de site les remplace.")


# ═══════════════════════════════════════════════════════════════════════════
#  D’OÙ VIENT L’EAU — la question que le volume ne pose pas
#
#  UN MÈTRE CUBE N’EST PAS UN MÈTRE CUBE. Le module comptait des volumes sans
#  jamais dire QUELLE eau : c’est pourtant la première chose qu’un service
#  instructeur regarde. L’Arcep a mesuré le point décisif sur le parc français
#  — les prélèvements directs sont « en quasi-totalité potable ». De l’eau
#  traitée pour être bue, évaporée pour refroidir des serveurs, prélevée sur le
#  même réseau que les habitants : c’est cette phrase-là qui fait un arrêté
#  sécheresse, pas le volume.
#
#  CE QUE PORTE LA `tension` — ET CE QU’ELLE N’EST PAS. Ce n’est pas une
#  grandeur physique : un mètre cube reste un mètre cube. C’est un COEFFICIENT
#  D’ARBITRAGE, déclaré ici pour être discuté, qui dit combien ce mètre cube
#  entre en concurrence avec les autres usages du bassin. Il ne se multiplie
#  jamais aux volumes — il les CLASSE. Une pondération qu’on cache dans un
#  total devient un jugement qu’on fait passer pour une mesure.
# ═══════════════════════════════════════════════════════════════════════════

SOURCES_EAU = {
    "potable": {
        "nom": "Réseau d’eau potable",
        "tension": 1.00,
        "sens": "Le cas par défaut, et le plus tendu : eau traitée pour être bue, "
                "prélevée sur le même réseau que les habitants. C’est celui qu’un "
                "arrêté sécheresse restreint en premier.",
        "observe": "Arcep : les prélèvements directs du parc français sont « en "
                   "quasi-totalité » de l’eau potable.",
    },
    "brute_superficielle": {
        "nom": "Eau brute de surface (rivière, canal, plan d’eau)",
        "tension": 0.70,
        "sens": "Hors réseau potable, mais en concurrence directe avec l’irrigation "
                "et le milieu à l’étiage — c’est-à-dire l’été, quand le "
                "refroidissement évaporatif consomme le plus.",
    },
    "brute_souterraine": {
        "nom": "Eau brute de nappe",
        "tension": 0.85,
        "sens": "Le prélèvement ne se voit pas et se reconstitue lentement : une "
                "nappe surexploitée ne se répare pas à l’échelle d’un projet.",
    },
    "reut": {
        "nom": "Eau usée traitée réutilisée (REUT)",
        "tension": 0.25,
        "sens": "Le meilleur arbitrage disponible sur un site continental : le "
                "volume ne se retranche à aucun usage. Suppose une station à "
                "distance raisonnable et une qualité compatible avec les circuits.",
    },
    "mer": {
        "nom": "Eau de mer",
        "tension": 0.05,
        "sens": "Hors compétition d’usage pour la ressource elle-même. L’enjeu se "
                "déplace sur le rejet thermique et la salinité, pas sur le volume.",
    },
    "recyclee_interne": {
        "nom": "Boucle fermée, appoint seul",
        "tension": 0.30,
        "sens": "Seules les purges et l’évaporation résiduelle sont prélevées. "
                "L’appoint reste à déclarer : « boucle fermée » ne veut pas dire "
                "« sans eau ».",
    },
    "inconnu": {
        "nom": "Origine non publiée",
        "tension": None,
        "sens": "Aucune tension ne peut être posée sans inventer une origine. "
                "C’est le cas de la quasi-totalité du parc cartographié : les "
                "exploitants publient un volume, pas une provenance.",
    },
}
SOURCES_SOURCE = (
    "Coefficients d’arbitrage CONSEILPREV, déclarés pour être discutés — ils "
    "classent, ils ne se multiplient à aucun volume. Le fait observé qui les "
    "motive est publié par l’Arcep (enquête « Pour un numérique soutenable », "
    "volet centres de données)."
)


# ═══════════════════════════════════════════════════════════════════════════
#  LES FAMILLES QUE LE PARC NE CODE PAS ENCORE
#
#  POURQUOI UNE TABLE À PART, ET NON TROIS LIGNES DE PLUS. `equivalence_par_mode`
#  lit les PUE et WUE du référentiel des SITES (datacentres.py) : ce sont les
#  modes réellement portés par le parc cartographié. Y ajouter des familles
#  qu’aucun site ne déclare polluerait un référentiel d’observation avec de la
#  prospective. Elles vivent donc ici, avec leurs propres bornes et un drapeau
#  qui dit qu’elles ne décrivent AUCUN site du parc.
#
#  LES TROIS QU’IL FAUT AJOUTER, ET POURQUOI CELLES-LÀ :
#    — le refroidissement direct par liquide arrive avec l’IA parce que la
#      chaleur produite par les puces ne s’évacue plus par l’air ;
#    — l’immersion suit, pour les mêmes charges ;
#    — le CIRCUIT OUVERT sur cours d’eau, lui, n’est pas nouveau : il est en
#      service (Marseille) et le référentiel ne le code pas. C’est le cas
#      décisif, et pour une raison qui met en défaut tout le modèle — voir la
#      note `restitue` ci-dessous.
#
#  LES BORNES SONT DU CADRAGE. Elles ne viennent pas d’une table publiée mais
#  d’ordres de grandeur convergents ; elles portent donc la nature
#  `ordre_grandeur` et une fourchette large, et se remplacent par les données du
#  constructeur dès qu’on en dispose. Écrire 1,08 aurait été plus impressionnant
#  et moins vrai.
# ═══════════════════════════════════════════════════════════════════════════

FAMILLES_HORS_PARC = {
    "dlc": {
        "nom": "Refroidissement direct par liquide (DLC), boucle fermée",
        "pue": (1.10, 1.25), "wue": (0.0, 1.2), "part": None,
        "restitue": False,
        "resume": "Un mélange eau-glycol circule au contact des puces, en boucle "
                  "fermée. C’est la réponse à la densité de chaleur des charges "
                  "d’IA, que l’air ne suffit plus à évacuer.",
        "ce_qui_trompe":
            "LE DLC NE SUPPRIME PAS LE REJET DE CHALEUR, IL LE DÉPLACE. La boucle "
            "est fermée sur la puce ; il reste à évacuer la même chaleur du "
            "bâtiment, et c’est CET étage qui décide de l’eau. Rejet par "
            "aéroréfrigérant sec : WUE de site quasi nul. Rejet par tour "
            "évaporative : on retrouve le WUE d’une tour. D’où la fourchette "
            "large — elle ne dit pas une imprécision de mesure, elle dit que "
            "deux conceptions portant le même nom ne consomment pas la même eau.",
        "points_ouverts": [
            "L’eau glycolée n’est pas de l’eau : sa fin de vie, son traitement et "
            "son éventuel rejet ne relèvent pas du bilan hydrique mais d’un sujet "
            "de déchet liquide, encore peu documenté.",
            "Une température de fluide plus élevée — les annonces récentes vont "
            "jusqu’à 45 °C — élargit la fenêtre de refroidissement sec et réduit "
            "d’autant le recours à l’évaporatif. C’est le levier qui compte, et "
            "il se lit sur la température de retour, pas sur le nom du système.",
            "Le parc existant garde ses technologies : la généralisation se "
            "compte en années, et le bilan d’un parc reste celui de ses machines "
            "installées, pas de son catalogue.",
        ],
        "maturite": "en déploiement sur les charges d’IA",
    },
    "immersion": {
        "nom": "Refroidissement par immersion (fluide diélectrique)",
        "pue": (1.03, 1.20), "wue": (0.0, 0.8), "part": None,
        "restitue": False,
        "resume": "Les serveurs sont immergés dans un fluide diélectrique qui "
                  "absorbe la chaleur, puis la cède à un circuit de reprise.",
        "ce_qui_trompe":
            "Même déplacement que le DLC : l’immersion supprime les ventilateurs "
            "et abaisse le PUE, elle n’évacue pas la chaleur du site. L’eau du "
            "bilan se joue à l’étage de rejet, pas dans le bac.",
        "points_ouverts": [
            "Le fluide diélectrique est un consommable industriel : sa fabrication "
            "et sa fin de vie sortent du bilan hydrique et n’y sont pas comptées.",
            "Parc installé négligeable en Europe : c’est une option de conception "
            "neuve, pas un levier sur l’existant.",
        ],
        "maturite": "démonstrateurs et premières unités",
    },
    "riviere": {
        "nom": "Circuit ouvert sur cours d’eau (river cooling)",
        "pue": (1.10, 1.30), "wue": (0.0, 0.2), "part": 0.0,
        "restitue": True,
        "resume": "L’eau est prélevée dans un cours d’eau ou une nappe froide, "
                  "traverse un échangeur, et retourne au milieu — plus chaude. "
                  "En service en France, notamment à Marseille.",
        "ce_qui_trompe":
            "ICI, LE MODÈLE DE CE MODULE EST EN DÉFAUT, ET IL FAUT LE DIRE. Tout "
            "le module raisonne en eau CONSOMMÉE — évaporée, non restituée. Un "
            "circuit ouvert restitue la quasi-totalité de ce qu’il prélève : sa "
            "consommation est proche de zéro, et un tableau qui s’arrêterait là "
            "le classerait comme la solution la plus sobre. Or son impact est "
            "AILLEURS : il est THERMIQUE et il est de PRÉLÈVEMENT. Une prise à "
            "15,5 °C restituée jusqu’à 24,5 °C en été change le milieu récepteur "
            "— risque d’eutrophisation — et le débit prélevé entre en concurrence "
            "avec les autres usages, y compris l’eau potable. Aucune des deux "
            "choses ne se voit sur un WUE.",
        "points_ouverts": [
            "L’indicateur qui manque n’est pas un volume mais un DELTA DE "
            "TEMPÉRATURE et un DÉBIT, tous deux encadrés par l’autorisation de "
            "rejet, pas par le règlement (UE) 2024/1364.",
            "Un site en circuit ouvert peut se trouver en zone de stress hydrique "
            "élevé sans que son WUE ne le signale jamais.",
        ],
        "maturite": "en service, non codé au référentiel des sites",
    },
}
FAMILLES_HORS_PARC_SOURCE = (
    "Bornes de CADRAGE, nature ordre_grandeur : ordres de grandeur convergents "
    "de la littérature technique et des annonces constructeurs, à remplacer par "
    "les données du fournisseur. Elles ne décrivent AUCUN site du parc "
    "cartographié — aucun ne déclare ces familles."
)


# ═══════════════════════════════════════════════════════════════════════════
#  REPÈRES PUBLIÉS — ce à quoi le calcul doit ressembler
#
#  POURQUOI ILS MANQUAIENT. Le module produit un rapport amont ÷ site et le
#  présente comme la grandeur qui tranche l’arbitrage. Rien ne disait si ce
#  rapport est de l’ordre de deux, de dix ou de cent — et un lecteur n’a aucun
#  moyen de savoir si le modèle est plausible. Or DEUX autorités publiques ont
#  publié les deux termes pour un parc national entier : le rapport observé s’en
#  déduit, et le modèle devient vérifiable.
#
#  LE RAPPORT EST CALCULÉ ICI, PAS RECOPIÉ. Écrit à la main, il aurait cessé de
#  correspondre à ses deux termes à la première correction de l’un d’eux — et
#  un repère faux est pire qu’aucun repère, puisqu’il sert justement à juger le
#  reste.
# ═══════════════════════════════════════════════════════════════════════════

REPERES = [
    {
        "cle": "arcep_fr_2023",
        "perimetre": "Parc français déclarant, année 2023",
        "site_m3": 681000,
        "amont_m3": 6000000,
        "editeur": "Arcep — enquête annuelle sur l’empreinte environnementale du numérique",
        "lecture": "L’eau prélevée directement par les centres est FAIBLE au regard "
                   "de l’eau consommée indirectement pour produire leur électricité. "
                   "Sur un mix nucléaire, l’écart est structurel : c’est le parc de "
                   "production qui évapore.",
    },
    {
        "cle": "lbnl_us_2023",
        "perimetre": "Parc états-unien, année 2023",
        "site_m3": 64000000,
        "amont_m3": 800000000,
        "editeur": "Lawrence Berkeley National Laboratory, rapport 2024",
        "lecture": "Même conclusion sur un parc dix fois plus grand et un mix tout "
                   "autre : l’ordre de grandeur du rapport ne tient pas à un pays.",
    },
]

# Faits de cadrage qui ne sont pas des rapports, et qu’on ne mélange donc pas
# aux repères ci-dessus : ils servent à situer, pas à vérifier.
FAITS = [
    {"quoi": "Part des systèmes installés qui refroidissent par l’air",
     "valeur": "71 %", "editeur": "ADEME, 2025",
     "portee": "Le parc réel est très majoritairement à air : les familles "
               "liquides décrites plus haut ne décrivent pas l’existant."},
    {"quoi": "Fenêtre du free cooling direct",
     "valeur": "jusqu’à ~24-25 °C d’air extérieur",
     "editeur": "ADEME, 2025",
     "portee": "Au-delà, la climatisation prend le relais — et avec elle, selon la "
               "conception, l’eau. Le réchauffement rétrécit cette fenêtre chaque "
               "année : un site conçu sur les normales d’hier bascule plus souvent "
               "que prévu."},
    {"quoi": "Prélèvement d’un très grand centre nord-américain à tours",
     "valeur": "jusqu’à 19 millions de litres par jour",
     "editeur": "presse spécialisée, ordres de grandeur convergents",
     "portee": "Soit l’ordre de grandeur d’une ville de 10 000 à 50 000 habitants. "
               "Rare en France pour des raisons réglementaires."},
    {"quoi": "Eau ultrapure d’une usine de semi-conducteurs",
     "valeur": "~38 millions de litres par jour",
     "editeur": "littérature sur la fabrication des puces",
     "portee": "C’est l’eau du SCOPE 3 — celle de la fabrication du matériel. Elle "
               "n’est comptée NULLE PART dans ce module, faute de transparence des "
               "fabricants, et son absence tire tous les totaux vers le bas."},
    {"quoi": "Électricité des centres français",
     "valeur": "10 TWh en 2026 → 15-20 TWh en 2030 → 23-28 TWh en 2035",
     "editeur": "RTE",
     "portee": "Le terme amont du bilan eau suit cette trajectoire : à EWIF "
               "constant, il double d’ici 2030 et triple d’ici 2035."},
]


def repere(r):
    """Un repère, avec son rapport CALCULÉ à partir de ses deux termes."""
    d = dict(r)
    d["rapport"] = (round(r["amont_m3"] / float(r["site_m3"]), 1)
                    if r.get("site_m3") else None)
    return d


def reperes():
    return [repere(r) for r in REPERES]


#: Au-delà de ce rapport entre ses deux bornes, un intervalle cesse d’être une
#: prédiction : il contient l’observation quoi qu’elle vaille. Le seuil est
#: assumé et rond — deux ordres de grandeur.
AMPLITUDE_NON_INFORMATIVE = 100.0


def confronter(intervalle, observes=None, quoi="le parc cartographié"):
    """Confronter l’intervalle CALCULÉ aux rapports OBSERVÉS, sans se flatter.

    CE QUE CE CONTRÔLE A CORRIGÉ EN NAISSANT. Écrit d’abord sur la borne BASSE
    du rapport, il annonçait ×0,1 contre ×8,8-12,5 observés et concluait à un
    écart de facteur cent. C’était comparer une borne à un point : le modèle ne
    produit pas un rapport, il en produit un INTERVALLE, et seul l’intervalle se
    confronte.

    CE QU’IL DIT DE PLUS QU’UN « OUI, ÇA RENTRE ». Un intervalle de ×0,1 à ×195
    contient les deux observations — et n’apprend rien, puisqu’il contiendrait
    aussi bien n’importe quoi d’autre. La contenance seule ferait donc passer
    pour une validation ce qui est un aveu d’imprécision. L’AMPLITUDE est donc
    calculée et publiée avec le verdict : c’est elle qui dit si la concordance
    vaut quelque chose.
    """
    obs = [x for x in (observes if observes is not None
                       else [repere(r)["rapport"] for r in REPERES])
           if x is not None]
    if not obs or not intervalle or intervalle.get("min") is None:
        return {"comparable": False,
                "motif": "aucun rapport calculable — rien à confronter"}
    bas = intervalle["min"]
    haut = intervalle.get("max")
    indefini = bool(intervalle.get("max_indefini")) or haut is None
    dedans = [o for o in obs if o >= bas and (indefini or o <= haut)]
    amplitude = (round(haut / bas, 1) if (haut and bas and not indefini) else None)
    informatif = bool(amplitude is not None and amplitude <= AMPLITUDE_NON_INFORMATIVE)

    # « 1 rapports observés » : avec un seul repère — le cas de la confrontation
    # française — l’accord se voit à l’œil nu et décrédibilise la phrase entière.
    nobs = "le rapport observé" if len(obs) == 1 else "les %d rapports observés" % len(obs)

    if len(dedans) == len(obs) and not informatif:
        lecture = (
            "L’intervalle calculé sur %s (×%s à %s) contient %s — mais il est "
            "trop large pour que cela signifie quoi que ce soit : l’écart entre "
            "ses deux bornes est d’un facteur %s. Ce n’est pas une validation du "
            "modèle, c’est la mesure de son imprécision. La cause est connue et "
            "elle est en amont : le mode de refroidissement de la plupart des "
            "sites n’est pas publié, et un mode inconnu porte un WUE de 0 à 2,2 — "
            "deux ordres de grandeur à lui seul. C’est pourquoi l’arbitrage se "
            "tranche mode par mode, jamais sur un total."
            % (quoi, bas, "sans borne" if indefini else "×%s" % haut,
               nobs, ("%d" % round(amplitude)) if amplitude else "?"))
    elif len(dedans) == len(obs):
        lecture = (
            "L’intervalle calculé sur %s (×%s à ×%s) contient %s, et il est assez "
            "resserré (facteur %d d’une borne à l’autre) pour que la concordance "
            "ait un sens."
            % (quoi, bas, haut, nobs, round(amplitude)))
    elif dedans:
        lecture = (
            "L’intervalle calculé sur %s ne contient qu’une partie des rapports "
            "observés (%d sur %d). L’écart doit s’expliquer avant usage."
            % (quoi, len(dedans), len(obs)))
    else:
        lecture = (
            "AUCUN rapport observé ne tombe dans l’intervalle calculé sur %s "
            "(×%s à %s). Ce n’est pas nécessairement une erreur — un parc "
            "cartographié n’a ni la composition ni le mix d’un parc national — "
            "mais tant que l’écart n’est pas expliqué, le calcul ne doit pas "
            "servir d’argument."
            % (quoi, bas, "sans borne" if indefini else "×%s" % haut))

    return {
        "comparable": True, "quoi": quoi,
        "modele_min": bas, "modele_max": haut, "modele_max_indefini": indefini,
        "observes": obs, "observes_dedans": dedans,
        "tous_dedans": len(dedans) == len(obs),
        "amplitude": amplitude, "informatif": informatif,
        "seuil_amplitude": AMPLITUDE_NON_INFORMATIVE,
        "lecture": lecture,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  CALCUL
# ═══════════════════════════════════════════════════════════════════════════

def ewif_pays(code):
    """Facteur eau du pays, et s’il est national ou emprunté à la moyenne UE.

    Renvoie toujours le drapeau : un pays qui reçoit la moyenne européenne n’a
    pas une valeur « moins précise », il n’en a AUCUNE. La différence doit
    remonter jusqu’à l’affichage, sans quoi vingt-trois pays paraissent tous
    documentés.
    """
    e = EWIF_PAYS.get((code or "").upper())
    if e:
        return {"valeur": e["valeur"], "mix": e.get("mix", ""), "note": e.get("note", ""),
                "national": True, "nature": EWIF_NATURE}
    return {"valeur": EWIF_DEFAUT["valeur"], "mix": EWIF_DEFAUT["mix"],
            "note": EWIF_DEFAUT["note"], "national": False, "nature": "defaut_ue"}


def eau_amont_site(estimation, code):
    """Eau consommée en amont par l’électricité d’un site, en m³/an.

    m³ = GWh × 1 000 (→ MWh) × EWIF (L/kWh) ÷ 1 000 (L → m³) × 1 000 (MWh → kWh),
    ce qui se simplifie en : m³ = GWh × 1 000 × EWIF.

    La nature est HÉRITÉE de l’estimation d’électricité et ne peut jamais être
    meilleure : multiplier une consommation de nature « classe » par un facteur
    ne produit pas une mesure.
    """
    if not estimation or estimation.get("nature") == "indisponible":
        return {"nature": "indisponible", "m3": None,
                "motif": "consommation non estimable — aucune eau amont dérivable"}
    gwh = estimation.get("electricite")
    if not gwh:
        return {"nature": "indisponible", "m3": None,
                "motif": "consommation non estimable — aucune eau amont dérivable"}
    e = ewif_pays(code)
    m3 = [round(gwh[0] * 1000.0 * e["valeur"]), round(gwh[1] * 1000.0 * e["valeur"])]
    return {"nature": estimation["nature"], "m3": m3,
            "ewif": e["valeur"], "ewif_national": e["national"],
            "formule": "électricité annuelle (GWh) × 1 000 × EWIF (%s L/kWh)" % e["valeur"],
            "incertitude": EWIF_INCERTITUDE, "motif": None}


def _rapport(amont, site):
    """Rapport amont/site sous forme d’INTERVALLE, bornes correctement appariées.

    Le rapport minimal se lit en divisant l’amont le plus bas par le site le
    plus haut, et non deux bornes basses l’une par l’autre — celles-ci
    donneraient un rapport maximal en le faisant passer pour prudent. C’est
    l’erreur qu’a d’abord commise ce module : il annonçait « ×18 » là où le
    WUE bas de plusieurs modes vaut zéro, ce qui rend le rapport non pas grand
    mais INDÉFINI.
    """
    bas = round(amont[0] / site[1], 1) if site[1] else None
    haut = round(amont[1] / site[0], 1) if site[0] else None
    return {"min": bas, "max": haut,
            "max_indefini": site[0] == 0,
            "note": ("Le WUE bas de plusieurs modes vaut zéro : sans eau sur le "
                     "site, le rapport n’a pas de borne haute — toute l’eau du "
                     "bilan est alors en amont.") if site[0] == 0 else ""}


def _recouvre(a, b):
    """Deux fourchettes se chevauchent-elles ? Si oui, aucune ne l’emporte."""
    return a[0] <= b[1] and b[0] <= a[1]


def _ligne_mode(mode, nom, pue, wue, e, extra=None):
    """Une ligne de comparaison, en litres par kWh informatique.

    Ramenées au kilowattheure informatique, les deux eaux se comparent
    directement : le site vaut son WUE, l’amont vaut EWIF × PUE. Le rapport des
    deux ne dépend plus ni de la taille du parc ni du facteur de charge — il ne
    dépend que de la CONCEPTION et du MIX, c’est-à-dire des deux seules choses
    sur lesquelles on décide.
    """
    amont = [round(e["valeur"] * pue[0], 2), round(e["valeur"] * pue[1], 2)]
    # Amont ÷ site : borne basse = amont bas ÷ site haut, et réciproquement.
    bas = round(amont[0] / wue[1], 1) if wue[1] else None
    haut = round(amont[1] / wue[0], 1) if wue[0] else None
    d = {
        "mode": mode, "nom": nom,
        "wue_site": list(wue), "pue": list(pue),
        "amont_l_kwh_it": amont,
        "rapport": {"min": bas, "max": haut, "max_indefini": wue[0] == 0},
        # Le seul verdict qui se tienne sans hypothèse supplémentaire :
        # l’amont l’emporte-t-il même dans l’hypothèse la plus défavorable ?
        "amont_domine_toujours": bool(wue[1] and amont[0] > wue[1]),
        "amont_domine_parfois": bool(wue[0] == 0 or amont[1] > wue[0]),
    }
    d.update(extra or {})
    return d


def equivalence_par_mode(code=None):
    """Les modes RÉELLEMENT portés par le parc cartographié.

    Rend aussi, sous `_sans_bornes`, les familles connues du référentiel des
    parts d’évaporation auxquelles il manque un PUE ou un WUE. Cette liste
    était auparavant produite par une intersection d’ensembles, donc SILENCIEUSE :
    une famille ajoutée sans ses bornes disparaissait du tableau sans qu’aucune
    ligne ne le dise, et le lecteur voyait un référentiel qu’il croyait complet.
    """
    try:
        import datacentres
        pue_t, wue_t = datacentres.PUE, datacentres.WUE
    except Exception:
        return []
    e = ewif_pays(code)
    chiffrables = set(pue_t) & set(wue_t)
    out = [_ligne_mode(m, (PART_EVAPORATIVE.get(m) or {}).get("nom") or m,
                       pue_t[m], wue_t[m], e)
           for m in sorted(chiffrables)]
    manquants = sorted(set(PART_EVAPORATIVE) - chiffrables)
    if manquants:
        out.append({"mode": "_sans_bornes", "modes": manquants,
                    "motif": "familles connues du référentiel des parts "
                             "d’évaporation mais dépourvues de PUE ou de WUE : "
                             "elles ne peuvent pas être comparées, et c’est écrit "
                             "plutôt que passé sous silence"})
    return out


def equivalence_hors_parc(code=None):
    """Les familles que le référentiel des sites ne code pas encore.

    Servies à part, et JAMAIS mélangées aux modes du parc : les unes décrivent
    des sites observés, les autres une conception possible. Les confondre dans
    un même tableau ferait lire de la prospective comme un relevé.
    """
    e = ewif_pays(code)
    out = []
    for cle in sorted(FAMILLES_HORS_PARC):
        f = FAMILLES_HORS_PARC[cle]
        out.append(_ligne_mode(
            cle, f["nom"], f["pue"], f["wue"], e,
            extra={
                "hors_parc": True,
                "nature": "ordre_grandeur",
                "restitue": f["restitue"],
                "resume": f["resume"],
                "ce_qui_trompe": f["ce_qui_trompe"],
                "points_ouverts": list(f["points_ouverts"]),
                "maturite": f["maturite"],
                # LE DRAPEAU QUI ÉVITE LA CONCLUSION INVERSE. Une famille qui
                # restitue son eau au milieu affiche une consommation quasi
                # nulle : sans cet avertissement, le tableau la désignerait
                # comme la plus sobre, alors que son impact est simplement
                # ailleurs — thermique et de prélèvement.
                "hors_modele": bool(f["restitue"]),
                "hors_modele_motif": (
                    "Consommation quasi nulle parce que l’eau est RESTITUÉE, non "
                    "évaporée. Ce tableau compare des eaux consommées : il ne "
                    "voit ni le débit prélevé ni l’échauffement du milieu, qui "
                    "sont ici les deux seuls impacts. Ne pas lire cette ligne "
                    "comme un bon résultat." if f["restitue"] else ""),
            }))
    return out


def assemble(sites=None):
    """Bilan eau du parc : site, amont, et le rapport entre les deux.

    Le rapport est la seule grandeur qui permette d’arbitrer. Publier deux
    volumes côte à côte sans leur rapport laisse le lecteur faire la division
    de tête, et il la fait rarement.
    """
    sites = sites or []
    par_pays, detail = {}, []
    sans_ewif, sans_eau = set(), 0

    for s in sites:
        code = (s.get("pays") or "").upper()
        est = s.get("estimation") or {}
        amont = eau_amont_site(est, code)
        site_m3 = est.get("eau")
        if not code:
            continue
        e = ewif_pays(code)
        if not e["national"]:
            sans_ewif.add(code)
        p = par_pays.setdefault(code, {
            "pays": code, "n_dc": 0, "site_m3": [0, 0], "amont_m3": [0, 0],
            "ewif": e["valeur"], "ewif_national": e["national"],
            "mix": e["mix"], "n_sans_estimation": 0,
        })
        p["n_dc"] += 1
        if site_m3:
            p["site_m3"][0] += site_m3[0]
            p["site_m3"][1] += site_m3[1]
        else:
            sans_eau += 1
            p["n_sans_estimation"] += 1
        if amont["m3"]:
            p["amont_m3"][0] += amont["m3"][0]
            p["amont_m3"][1] += amont["m3"][1]
        mode = s.get("refroidissement") or "inconnu"
        # L’origine de l’eau, quand le référentiel des sites la porte. Il ne la
        # porte pour aucun site aujourd’hui : les exploitants publient un volume,
        # jamais une provenance. Le champ existe pour ne pas avoir à retoucher le
        # calcul le jour où l’un d’eux la déclarera.
        src = (s.get("source_eau") or "inconnu")
        if src not in SOURCES_EAU:
            src = "inconnu"
        detail.append({
            "id": s.get("id"), "pays": code, "operateur": s.get("operateur"),
            "ville": s.get("ville"), "refroidissement": mode,
            "part_evaporative": (PART_EVAPORATIVE.get(mode) or {}).get("part"),
            "source_eau": src,
            "source_eau_nom": SOURCES_EAU[src]["nom"],
            "tension_usage": SOURCES_EAU[src]["tension"],
            "site_m3": site_m3, "amont": amont,
        })

    for p in par_pays.values():
        p["site_m3"] = [round(p["site_m3"][0]), round(p["site_m3"][1])]
        p["amont_m3"] = [round(p["amont_m3"][0]), round(p["amont_m3"][1])]
        p["total_m3"] = [p["site_m3"][0] + p["amont_m3"][0],
                         p["site_m3"][1] + p["amont_m3"][1]]
        p["rapport"] = _rapport(p["amont_m3"], p["site_m3"])
        p["recouvrement"] = _recouvre(p["amont_m3"], p["site_m3"])

    site = [sum(p["site_m3"][0] for p in par_pays.values()),
            sum(p["site_m3"][1] for p in par_pays.values())]
    amont = [sum(p["amont_m3"][0] for p in par_pays.values()),
             sum(p["amont_m3"][1] for p in par_pays.values())]
    recouvre = _recouvre(amont, site)

    return {
        "version": VERSION,
        "par_pays": sorted(par_pays.values(), key=lambda x: -x["total_m3"][0]),
        "detail": detail,
        "totaux": {
            "site_m3": site, "amont_m3": amont,
            "total_m3": [site[0] + amont[0], site[1] + amont[1]],
            "rapport": _rapport(amont, site),
            "recouvrement": recouvre,
            # Ce que le total permet de conclure — et ce qu’il ne permet PAS.
            # Deux fourchettes qui se recouvrent ne désignent aucun vainqueur,
            # et un ratio unique tiré de leurs bornes basses en fabriquerait un.
            "lecture": (
                "Les deux fourchettes SE RECOUVRENT : au bas des hypothèses de "
                "WUE, l’eau amont domine largement ; au haut, c’est l’eau de "
                "site. Le total du parc ne tranche donc pas l’arbitrage — c’est "
                "le rapport EWIF × PUE ÷ WUE, mode de refroidissement par mode, "
                "qui le tranche."
                if recouvre else
                "Les deux fourchettes ne se recouvrent pas : la comparaison est "
                "tranchée sur l’ensemble du parc."),
            "n_dc": len(detail),
        },
        "par_mode": equivalence_par_mode(),
        "hors_parc": equivalence_hors_parc(),
        "reperes": reperes(),
        "faits": [dict(f) for f in FAITS],
        # LE MODÈLE RENCONTRE L’OBSERVATION, à deux échelles.
        #
        # Sur le parc entier d’abord, contre les deux repères — la confrontation
        # y est large, et le contrôle le dit lui-même plutôt que de s’en
        # prévaloir.
        #
        # Sur le SOUS-PARC FRANÇAIS ensuite, et c’est celle qui vaut : le repère
        # Arcep porte sur la France, avec son mix et sa réglementation. Comparer
        # un parc paneuropéen à un parc national mélange des mix dont l’EWIF va
        # du simple au quintuple ; comparer la France à la France ne mélange
        # rien.
        "confrontation": confronter(_rapport(amont, site), quoi="le parc cartographié"),
        "confrontation_fr": (
            confronter(par_pays["FR"]["rapport"],
                       observes=[repere(REPERES[0])["rapport"]],
                       quoi="le sous-parc français")
            if "FR" in par_pays else
            {"comparable": False,
             "motif": "aucun site français au parc — rien à confronter au repère Arcep"}),
        "couverture": {
            "pays_parc": len(par_pays),
            "pays_ewif_national": sum(1 for p in par_pays.values() if p["ewif_national"]),
            "pays_defaut_ue": sorted(sans_ewif),
            "sites_sans_estimation_eau": sans_eau,
            # L’ORIGINE DE L’EAU N’EST PUBLIÉE NULLE PART. On compte les sites qui
            # la déclarent plutôt que de laisser croire qu’elle est inconnue par
            # accident : c’est un trou du référentiel public, pas du nôtre.
            "sites_source_connue": sum(
                1 for d in detail if d.get("source_eau") not in (None, "inconnu")),
        },
        "referentiel": {
            "ewif": {k: dict(v) for k, v in EWIF_PAYS.items()},
            "ewif_defaut": dict(EWIF_DEFAUT),
            "ewif_source": EWIF_SOURCE,
            "ewif_incertitude": EWIF_INCERTITUDE,
            "ewif_nature": EWIF_NATURE,
            "borne_evaporation": dict(BORNE_EVAPORATION),
            "part_evaporative": {k: dict(v) for k, v in PART_EVAPORATIVE.items()},
            "part_source": PART_SOURCE,
            "sources_eau": {k: dict(v) for k, v in SOURCES_EAU.items()},
            "sources_source": SOURCES_SOURCE,
            "familles_hors_parc": {k: dict(v) for k, v in FAMILLES_HORS_PARC.items()},
            "familles_hors_parc_source": FAMILLES_HORS_PARC_SOURCE,
            "cadre_eed": dict(CADRE_EED),
            "provenance": dict(PROVENANCE),
        },
        "avertissement": (
            "Ces volumes sont des ordres de grandeur dérivés de capacités "
            "annoncées, pas des relevés. Le terme amont porte une incertitude de "
            "±40 %, supérieure à celle du terme de site. Ils servent à comparer "
            "des pays et des conceptions entre eux, jamais à chiffrer un site "
            "particulier."),
        "limites": [
            "L’EWIF est un facteur ANNUEL MOYEN. Il ne dit rien de la tension "
            "saisonnière, qui est pourtant le moment où la ressource manque.",
            "Douze des vingt-trois pays du parc n’ont aucune valeur nationale et "
            "reçoivent la moyenne européenne : leur terme amont est un cadrage, "
            "pas une estimation de pays.",
            "L’eau consommée est distinguée de l’eau prélevée, mais les sources "
            "publiques confondent souvent les deux — l’écart peut atteindre un "
            "facteur dix sur un parc nucléaire en circuit ouvert.",
            "Un contrat d’électricité renouvelable ne change pas l’eau réellement "
            "évaporée par le réseau physique qui alimente le site.",
            "L’ORIGINE de l’eau n’est publiée par aucun exploitant du parc : le "
            "référentiel des sources est servi, mais aucun site ne s’y rattache. "
            "Or l’Arcep mesure que les prélèvements directs du parc français sont "
            "en quasi-totalité de l’eau POTABLE — un mètre cube d’eau potable et "
            "un mètre cube d’eau usée réutilisée n’engagent pas le même bassin.",
            "L’eau de FABRICATION du matériel — semi-conducteurs en tête, de "
            "l’ordre de 38 millions de litres d’eau ultrapure par jour et par "
            "usine — n’est comptée nulle part ici. Elle manque faute de "
            "transparence des fabricants, et son absence tire tous les totaux "
            "vers le bas.",
            "Le modèle raisonne en eau CONSOMMÉE. Il ne décrit donc pas les "
            "circuits ouverts sur cours d’eau, dont l’impact est thermique et de "
            "prélèvement : leur ligne porte un avertissement explicite plutôt "
            "qu’un bon résultat.",
        ],
    }


def arbitrage(part_evap_a, part_evap_b, pue_a, pue_b, code, mwh_it=100000.0):
    """Comparer deux conceptions sur le bilan eau COMPLET.

    C’est l’usage qui justifie tout le module : montrer qu’un refroidissement
    sec, dont le WUE de site est nul, peut consommer davantage d’eau qu’une
    tour évaporative dès que le mix est thermique.
    """
    e = ewif_pays(code)
    lkwh = BORNE_EVAPORATION["valeur_l_par_kwh_thermique"]

    def _bilan(part, pue):
        tot_mwh = mwh_it * pue
        # Toute l’énergie du site finit en chaleur : un centre de données ne
        # produit aucun travail mécanique utile.
        evap_m3 = tot_mwh * part * 1000.0 * lkwh / 1000.0
        amont_m3 = tot_mwh * e["valeur"]
        return {"pue": pue, "part_evaporative": part,
                "site_m3": round(evap_m3), "amont_m3": round(amont_m3),
                "total_m3": round(evap_m3 + amont_m3),
                "wue_site_l_kwh_it": round(evap_m3 * 1000.0 / (mwh_it * 1000.0), 3)}

    a, b = _bilan(part_evap_a, pue_a), _bilan(part_evap_b, pue_b)
    return {
        "pays": code, "ewif": e["valeur"], "ewif_national": e["national"],
        "mwh_it": mwh_it, "a": a, "b": b,
        "ecart_total_m3": b["total_m3"] - a["total_m3"],
        "inversion": (a["site_m3"] > b["site_m3"]) and (a["total_m3"] < b["total_m3"]),
        "lecture": ("Le bilan complet inverse la conclusion du bilan de site."
                    if (a["site_m3"] > b["site_m3"]) and (a["total_m3"] < b["total_m3"])
                    else "Le bilan complet confirme la conclusion du bilan de site."),
        "incertitude": EWIF_INCERTITUDE,
    }


def sante():
    """Ce que le module sait, et ce qu’il ne sait pas — chiffré."""
    modes_chiffres = sum(1 for v in PART_EVAPORATIVE.values() if v["part"] is not None)
    return {
        "version": VERSION,
        "pays_ewif": len(EWIF_PAYS),
        "modes_refroidissement": len(PART_EVAPORATIVE),
        "modes_avec_part_evaporative": modes_chiffres,
        "modes_sans_part": [k for k, v in PART_EVAPORATIVE.items() if v["part"] is None],
        "familles_hors_parc": len(FAMILLES_HORS_PARC),
        "familles_qui_restituent": [k for k, v in FAMILLES_HORS_PARC.items()
                                    if v["restitue"]],
        "sources_eau": len(SOURCES_EAU),
        "sources_avec_tension": sum(1 for v in SOURCES_EAU.values()
                                    if v["tension"] is not None),
        "reperes": len(REPERES),
        "reperes_rapports": [r["rapport"] for r in reperes()],
        "faits": len(FAITS),
        "indicateurs_eed": len(CADRE_EED["exige"]),
        "nature_ewif": EWIF_NATURE,
        "incertitude_ewif": EWIF_INCERTITUDE,
        "provenance": PROVENANCE["module"],
    }
