# -*- coding: utf-8 -*-
"""Les sections de la NACE Rév. 2.1 — le classement d'activités de l'Union.

POURQUOI CE MODULE EXISTE

L'Audit de maturité IA propose HUIT secteurs — télécom, énergie, santé,
finance, industrie, transport, informatique, public. Ce sont des profils
RELEVÉS : chacun porte ses systèmes d'IA typiques, ses réglementations
applicables, ses spécificités et un socle de départ sur les huit piliers. Ils
sont utiles, et ils ne sont pas une nomenclature : une coopérative agricole, un
distributeur, un bailleur social ou une université n'y trouvent pas leur
activité, et doivent choisir « le moins faux ».

La NACE est la nomenclature statistique des activités économiques de l'Union.
C'est celle que porte tout extrait d'immatriculation européen, celle sur
laquelle les administrations classent une entreprise, et celle que la NAF
française décline. Y adosser le choix du secteur permet à un client de désigner
son activité par le classement qu'il connaît déjà — et non par une liste
inventée ici.

CE QUE CE MODULE NE FAIT PAS, ET C'EST L'ESSENTIEL

IL N'INVENTE AUCUN PROFIL. Les treize sections que les huit profils relevés ne
couvrent pas restent SANS socle de piliers, SANS budget de référence et SANS
durée. Fabriquer ces valeurs donnerait vingt-deux secteurs d'apparence
homogène dont huit seraient relevés et treize devinés — et rien, à l'écran, ne
permettrait de distinguer les uns des autres. Une section sans profil le dit,
et l'audit y démarre à « non évalué ».

CE QUE LA SOURCE A CORRIGÉ, ET QUI VAUT D'ÊTRE ÉCRIT

De mémoire, la NACE compte vingt et une sections A à U, la finance en K et
l'informatique en J. C'EST LA RÉVISION 2, ET ELLE N'EST PLUS EN VIGUEUR. La
révision 2.1, applicable depuis le 1er janvier 2025, compte VINGT-DEUX sections
A à V, et redistribue les lettres à partir de G : l'informatique et les
télécommunications forment désormais la section K, la finance passe en L,
l'immobilier en M, l'enseignement en Q, la santé en R. Écrire ce référentiel
sans le relever aurait produit une table fausse à partir de sa septième ligne,
et d'autant plus crédible qu'elle aurait été complète.

LES INTITULÉS SONT CEUX DU RÈGLEMENT, LA TRADUCTION EST DE TRAVAIL

`intitule_officiel` reproduit mot pour mot l'annexe du règlement dans la
version consultée, qui est anglaise. `intitule` est une traduction de travail,
faite ici, et déclarée comme telle : la version française du règlement n'a pas
pu être consultée depuis cet environnement. Un intitulé traduit présenté comme
officiel serait le genre d'erreur qu'on ne repère plus jamais — celle qui a
l'air d'une source.
"""

VERSION = "2026-09-a"

# ── LA SOURCE ──────────────────────────────────────────────────────────────
SOURCE = {
    "acte": "Règlement délégué (UE) 2023/137 de la Commission du 10 octobre "
            "2022 modifiant le règlement (CE) n° 1893/2006 du Parlement "
            "européen et du Conseil établissant la nomenclature statistique "
            "des activités économiques NACE Rév. 2",
    "celex": "32023R0137",
    "journal": "JO L 19 du 20.1.2023, p. 5",
    "url": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32023R0137",
    "revision": "NACE Rév. 2.1",
    "applicable_depuis": "2025-01-01",
    "consulte_le": "2026-09-07",
    "version_consultee": "anglaise",
    "reserve": "Les intitulés officiels reproduits ici sont ceux de la "
               "version ANGLAISE de l'annexe. Les intitulés français sont une "
               "traduction de travail faite ici, non une reprise de la version "
               "française du règlement, qui n'a pas pu être consultée. "
               "`outils/recette_nace.py` dit comment la revérifier.",
}

# ── LES VINGT-DEUX SECTIONS ────────────────────────────────────────────────
# `intitule_officiel` : verbatim de l'annexe du règlement (version anglaise).
# `intitule`          : traduction de travail, faite ici — voir SOURCE['reserve'].
SECTIONS = [
    {"code": "A", "intitule_officiel": "AGRICULTURE, FORESTRY AND FISHING",
     "intitule": "Agriculture, sylviculture et pêche"},
    {"code": "B", "intitule_officiel": "MINING AND QUARRYING",
     "intitule": "Industries extractives"},
    {"code": "C", "intitule_officiel": "MANUFACTURING",
     "intitule": "Industrie manufacturière"},
    {"code": "D", "intitule_officiel":
        "ELECTRICITY, GAS, STEAM AND AIR CONDITIONING SUPPLY",
     "intitule": "Production et distribution d'électricité, de gaz, de vapeur "
                 "et d'air conditionné"},
    {"code": "E", "intitule_officiel":
        "WATER SUPPLY; SEWERAGE, WASTE MANAGEMENT AND REMEDIATION ACTIVITIES",
     "intitule": "Production et distribution d'eau ; assainissement, gestion "
                 "des déchets et dépollution"},
    {"code": "F", "intitule_officiel": "CONSTRUCTION",
     "intitule": "Construction"},
    {"code": "G", "intitule_officiel": "WHOLESALE AND RETAIL TRADE",
     "intitule": "Commerce de gros et de détail"},
    {"code": "H", "intitule_officiel": "TRANSPORTATION AND STORAGE",
     "intitule": "Transports et entreposage"},
    {"code": "I", "intitule_officiel":
        "ACCOMMODATION AND FOOD SERVICE ACTIVITIES",
     "intitule": "Hébergement et restauration"},
    {"code": "J", "intitule_officiel":
        "PUBLISHING, BROADCASTING, AND CONTENT PRODUCTION AND DISTRIBUTION "
        "ACTIVITIES",
     "intitule": "Édition, audiovisuel, production et distribution de contenus"},
    {"code": "K", "intitule_officiel":
        "TELECOMMUNICATION, COMPUTER PROGRAMMING, CONSULTING, COMPUTING "
        "INFRASTRUCTURE AND OTHER INFORMATION SERVICE ACTIVITIES",
     "intitule": "Télécommunications, programmation informatique, conseil, "
                 "infrastructures de calcul et autres services d'information"},
    {"code": "L", "intitule_officiel": "FINANCIAL AND INSURANCE ACTIVITIES",
     "intitule": "Activités financières et d'assurance"},
    {"code": "M", "intitule_officiel": "REAL ESTATE ACTIVITIES",
     "intitule": "Activités immobilières"},
    {"code": "N", "intitule_officiel":
        "PROFESSIONAL, SCIENTIFIC AND TECHNICAL ACTIVITIES",
     "intitule": "Activités spécialisées, scientifiques et techniques"},
    {"code": "O", "intitule_officiel":
        "ADMINISTRATIVE AND SUPPORT SERVICE ACTIVITIES",
     "intitule": "Activités de services administratifs et de soutien"},
    {"code": "P", "intitule_officiel":
        "PUBLIC ADMINISTRATION AND DEFENCE; COMPULSORY SOCIAL SECURITY",
     "intitule": "Administration publique et défense ; sécurité sociale "
                 "obligatoire"},
    {"code": "Q", "intitule_officiel": "EDUCATION",
     "intitule": "Enseignement"},
    {"code": "R", "intitule_officiel":
        "HUMAN HEALTH AND SOCIAL WORK ACTIVITIES",
     "intitule": "Santé humaine et action sociale"},
    {"code": "S", "intitule_officiel": "ARTS, SPORTS AND RECREATION",
     "intitule": "Arts, sports et loisirs"},
    {"code": "T", "intitule_officiel": "OTHER SERVICE ACTIVITIES",
     "intitule": "Autres activités de services"},
    {"code": "U", "intitule_officiel":
        "ACTIVITIES OF HOUSEHOLDS AS EMPLOYERS AND UNDIFFERENTIATED GOODS – "
        "AND SERVICE-PRODUCING ACTIVITIES OF HOUSEHOLDS FOR OWN USE",
     "intitule": "Activités des ménages en tant qu'employeurs ; activités "
                 "indifférenciées des ménages pour usage propre"},
    {"code": "V", "intitule_officiel":
        "ACTIVITIES OF EXTRATERRITORIAL ORGANISATIONS AND BODIES",
     "intitule": "Activités des organisations et organismes extraterritoriaux"},
]

#: Les lettres qui distinguent la révision 2.1 de la révision 2. Elles sont
#: nommées parce que c'est là qu'une table écrite de mémoire se trompe, et que
#: l'erreur ne se voit pas : « K » désigne bien une section dans les deux
#: révisions — pas la même.
DEPLACEMENTS_DEPUIS_REV2 = {
    "J": "En Rév. 2, « Information et communication ». En Rév. 2.1, l'édition, "
         "l'audiovisuel et la production de contenus seuls : l'informatique et "
         "les télécommunications sont passées en K.",
    "K": "En Rév. 2, « Activités financières et d'assurance ». En Rév. 2.1, "
         "les télécommunications, la programmation, le conseil et les "
         "infrastructures de calcul.",
    "L": "En Rév. 2, « Activités immobilières ». En Rév. 2.1, la finance et "
         "l'assurance.",
    "M": "En Rév. 2, les activités spécialisées, scientifiques et techniques. "
         "En Rév. 2.1, l'immobilier.",
    "N": "En Rév. 2, les services administratifs et de soutien. En Rév. 2.1, "
         "les activités spécialisées, scientifiques et techniques.",
    "O": "En Rév. 2, l'administration publique. En Rév. 2.1, les services "
         "administratifs et de soutien.",
    "P": "En Rév. 2, l'enseignement. En Rév. 2.1, l'administration publique.",
    "Q": "En Rév. 2, la santé humaine et l'action sociale. En Rév. 2.1, "
         "l'enseignement.",
    "R": "En Rév. 2, les arts et spectacles. En Rév. 2.1, la santé humaine et "
         "l'action sociale.",
    "S": "En Rév. 2, les autres activités de services. En Rév. 2.1, les arts, "
         "sports et loisirs.",
    "T": "En Rév. 2, les activités des ménages employeurs. En Rév. 2.1, les "
         "autres activités de services.",
    "U": "En Rév. 2, les organismes extraterritoriaux. En Rév. 2.1, les "
         "activités des ménages employeurs.",
    "V": "N'existe pas en Rév. 2 : la section est créée par la Rév. 2.1 pour "
         "les organisations et organismes extraterritoriaux.",
}

# ── LES HUIT PROFILS RELEVÉS DE SENTINEL, ET CE QU'ILS COUVRENT ────────────
# La clé est celle de `MAT_SECTORS` dans sentinel.page.js. Une clé inventée ici
# ferait promettre au sélecteur un profil que l'audit ne connaît pas ; le
# contrôle d'import et une règle du dépôt comparent les deux listes.
PROFILS_SENTINEL = {
    "telecom":   {"sections": ["K", "C"],
                  "socle": "releve",
                  "note": "Les opérateurs et fournisseurs de services relèvent "
                          "de K ; les équipementiers réseau, qui fabriquent, "
                          "de C."},
    "energie":   {"sections": ["D", "E"],
                  "socle": "releve",
                  "note": "L'électricité et le gaz relèvent de D ; l'eau, "
                          "l'assainissement et les déchets de E."},
    "sante":     {"sections": ["R", "C", "K"],
                  "socle": "releve",
                  "note": "Les établissements de soins relèvent de R ; les "
                          "fabricants de dispositifs médicaux de C ; les "
                          "éditeurs de logiciels de santé de K."},
    "finance":   {"sections": ["L"],
                  "socle": "releve",
                  "note": "Banques, assureurs, gestion et paiement relèvent "
                          "tous de L — qui était K avant la révision 2.1."},
    "industrie": {"sections": ["C"],
                  "socle": "releve",
                  "note": "L'ensemble de l'industrie manufacturière."},
    "transport": {"sections": ["H", "C"],
                  "socle": "releve",
                  "note": "L'exploitation et la logistique relèvent de H ; les "
                          "constructeurs de véhicules de C."},
    "it":        {"sections": ["K", "J"],
                  "socle": "releve",
                  "note": "L'édition de logiciels, le cloud et les services "
                          "numériques relèvent de K ; les plateformes de "
                          "contenus de J."},
    "public":    {"sections": ["P"],
                  "socle": "releve",
                  "note": "Administrations centrales, territoriales et "
                          "organismes publics."},

    # ── LES TREIZE PROFILS DE CADRE ────────────────────────────────────────
    #
    # POURQUOI ILS EXISTENT. Treize sections sur vingt-deux n'avaient AUCUN
    # profil. Un client en construction, en commerce ou dans l'enseignement
    # choisissait sa section, lisait « aucun profil relevé » — et l'audit
    # affiché en dessous restait celui du secteur précédent. Il lisait donc un
    # audit qui n'était pas le sien, sans que rien ne le dise.
    #
    # CE QU'ILS PORTENT, ET CE QU'ILS NE PORTENT PAS. Le régime applicable se
    # LIT : l'annexe III de l'IA Act et les annexes I et II de NIS2 nomment des
    # secteurs, et parfois des divisions NACE. Le socle des piliers, le budget
    # et la durée ne se lisent nulle part — ils viennent d'observations et de
    # missions réelles. Ces treize profils sont donc RELEVÉS SUR LE RÉGIME et
    # NON CALIBRÉS SUR LE SOCLE : côté audit ils portent `socle: "cadre"`, et
    # l'écran le dit au lieu d'afficher un chiffre.
    #
    # CE QUE LA LECTURE ÉTABLIT COMME ABSENT est écrit dans les profils au même
    # titre que ce qu'elle établit comme présent. « Aucune annexe NIS2 ne nomme
    # la construction » est un résultat, pas un trou.

    "agro":      {"sections": ["A", "C"],
                  "socle": "cadre",
                  "note": "La production primaire, la sylviculture et la pêche "
                          "relèvent de A ; la transformation alimentaire "
                          "industrielle, que NIS2 vise, de C."},
    "extractif": {"sections": ["B"],
                  "socle": "cadre",
                  "note": "Extraction minière, carrières, pétrole et gaz. NIS2 "
                          "ne nomme pas l'extraction, mais bien le raffinage "
                          "et le stockage (annexe I, point 1)."},
    "construction": {"sections": ["F"],
                  "socle": "cadre",
                  "note": "Le BTP dans son ensemble. Aucune des deux annexes "
                          "NIS2 ne le nomme ; l'IA embarquée dans un engin "
                          "passe par le règlement Machines."},
    "commerce":  {"sections": ["G"],
                  "socle": "cadre",
                  "note": "Gros, détail et places de marché. NIS2 l'atteint "
                          "par deux portes nommées : le gros alimentaire "
                          "(annexe II, 4) et les places de marché (II, 6)."},
    "hotellerie": {"sections": ["I"],
                  "socle": "cadre",
                  "note": "Hôtellerie, restauration et agences de voyage. La "
                          "restauration servant directement reste hors de "
                          "l'annexe II de NIS2, qui vise le gros."},
    "immobilier": {"sections": ["M"],
                  "socle": "cadre",
                  "note": "Transaction, gestion et foncières. Ni NIS2 ni "
                          "l'annexe III ne la nomment — ce sont le RGPD et la "
                          "non-discrimination qui mordent ici."},
    "conseil":   {"sections": ["N"],
                  "socle": "cadre",
                  "note": "Conseil, ingénierie, professions réglementées et "
                          "R&D. NIS2 l'atteint par les « organismes de "
                          "recherche » (annexe II, point 7)."},
    "services_support": {"sections": ["O"],
                  "socle": "cadre",
                  "note": "Intérim, agences d'emploi, centres de contact et "
                          "sécurité privée. L'annexe III, point 4 vise "
                          "directement le recrutement et la sélection."},
    "education": {"sections": ["Q"],
                  "socle": "cadre",
                  "note": "Scolaire, supérieur et formation professionnelle. "
                          "L'annexe III, point 3 couvre les quatre usages, à "
                          "tous les niveaux."},
    "culture":   {"sections": ["S", "J"],
                  "socle": "cadre",
                  "note": "Spectacle, sport et loisirs relèvent de S ; "
                          "l'édition, l'audiovisuel et les plateformes de "
                          "contenus de J."},
    "proximite": {"sections": ["T"],
                  "socle": "cadre",
                  "note": "Associations, organisations professionnelles, "
                          "réparation et services personnels. Aucune annexe "
                          "NIS2 ne les nomme."},
    "services_personne": {"sections": ["U"],
                  "socle": "cadre",
                  "note": "La section vise les MÉNAGES employeurs : l'entité "
                          "auditable n'est pas le particulier mais le "
                          "mandataire ou la plateforme qui opère pour lui."},
    "international": {"sections": ["V"],
                  "socle": "cadre",
                  "note": "Institutions de l'Union, organisations "
                          "intergouvernementales et représentations. Le "
                          "règlement 2018/1725 y tient lieu de RGPD."},
}

#: Les textes LUS pour établir les régimes des profils de cadre. Consignés ici
#: parce qu'une lecture qu'on ne peut pas refaire n'est pas une lecture : la
#: date de version compte autant que la référence — l'annexe III a été modifiée
#: par le règlement (UE) 2026/1744, et une lecture d'avant serait fausse.
SOURCES_REGIMES = [
    {"acte": "Règlement (UE) 2024/1689 (règlement sur l'intelligence "
             "artificielle), annexe III — systèmes d'IA à haut risque",
     "celex": "02024R1689-20260727",
     "version_lue": "consolidée au 27/07/2026, après le règlement (UE) 2026/1744",
     "consulte_le": "2026-09-09",
     "retenu": "Les huit domaines. Les points 3 (éducation et formation "
               "professionnelle) et 4 (emploi, gestion de la main-d'œuvre) "
               "ancrent à eux seuls deux des treize profils."},
    {"acte": "Directive (UE) 2022/2555 (SRI 2), annexe I — secteurs "
             "hautement critiques",
     "celex": "02022L2555-20221227",
     "version_lue": "en vigueur au 27/12/2022",
     "consulte_le": "2026-09-09",
     "retenu": "Énergie, transports, bancaire, marchés financiers, santé, eau "
               "potable, eaux usées, infrastructure numérique, services TIC "
               "interentreprises, administration publique, espace."},
    {"acte": "Directive (UE) 2022/2555 (SRI 2), annexe II — autres secteurs "
             "critiques",
     "celex": "02022L2555-20221227",
     "version_lue": "en vigueur au 27/12/2022",
     "consulte_le": "2026-09-09",
     "retenu": "Postal, déchets, chimie, denrées alimentaires (gros et "
               "transformation INDUSTRIELLE), fabrication (divisions NACE 26 à "
               "30, expressément citées), fournisseurs numériques, organismes "
               "de recherche. C'est la seule des trois annexes qui renvoie à "
               "la NACE par ses divisions."},
]

#: Ce qu'il faudrait pour qu'une section sans profil en reçoive un. Écrit ici
#: plutôt que promis ailleurs : c'est la seule forme qui survit à l'oubli.
A_RENSEIGNER = {
    "socle_des_piliers":
        "Un profil relevé porte un point de départ sur les huit piliers. Il "
        "vient de l'observation d'organisations du secteur, pas d'un calcul. "
        "L'inventer donnerait un audit qui démarre sur une note fabriquée, et "
        "rien à l'écran ne le distinguerait d'une note observée.",
    "budget_et_duree":
        "Les profils relevés portent un budget et une durée de mise en "
        "conformité indicatifs. Ils viennent de missions réelles. Les "
        "extrapoler d'un secteur à l'autre produirait un chiffre d'apparence "
        "précise sans rien derrière.",
    "specificites_reglementaires":
        "Chaque profil nomme les régimes qui s'ajoutent à l'IA Act — MDR pour "
        "la santé, DORA pour la finance, NIS2 et la directive CER pour "
        "l'énergie. Les établir pour une nouvelle section demande de lire les "
        "textes du secteur, pas de raisonner par analogie.",
}

_PAR_CODE = {s["code"]: s for s in SECTIONS}


def _verifier():
    """Le référentiel se contredit-il ? Contrôlé à l'import.

    C'est le seul moment où l'incohérence est encore gratuite : plus tard elle
    sort à l'écran, et à l'écran on la croit."""
    codes = [s["code"] for s in SECTIONS]
    if len(set(codes)) != len(codes):
        raise ValueError("NACE : deux sections portent le même code")
    attendus = [chr(c) for c in range(ord("A"), ord("V") + 1)]
    if codes != attendus:
        raise ValueError(
            "NACE Rév. 2.1 : les sections doivent être A à V, dans l'ordre — "
            "reçu %r. La Rév. 2 s'arrêtait à U ; confondre les deux fausse "
            "toutes les lettres à partir de G." % codes)
    for s in SECTIONS:
        if not s["intitule_officiel"].strip() or not s["intitule"].strip():
            raise ValueError("NACE %s : intitulé vide" % s["code"])
        if s["intitule_officiel"] != s["intitule_officiel"].upper():
            raise ValueError(
                "NACE %s : l'intitulé officiel n'est plus la reprise verbatim "
                "de l'annexe, qui est en capitales — l'a-t-on réécrit ?"
                % s["code"])
    for cle, p in PROFILS_SENTINEL.items():
        if not p["sections"]:
            raise ValueError("profil %s : aucune section déclarée" % cle)
        if p.get("socle") not in ("releve", "cadre"):
            raise ValueError(
                "profil %s : socle « %r » — attendu « releve » (observé sur "
                "des organisations du secteur) ou « cadre » (régime lu dans "
                "les textes, socle non calibré). Un profil sans socle déclaré "
                "serait lu comme relevé par défaut, ce qui est exactement "
                "l'erreur à éviter." % (cle, p.get("socle")))
        for code in p["sections"]:
            if code not in _PAR_CODE:
                raise ValueError(
                    "profil %s : la section « %s » n'existe pas en Rév. 2.1"
                    % (cle, code))


_verifier()


def section(code):
    """La section par son code, ou None. Une lettre inconnue n'est pas devinée."""
    return _PAR_CODE.get((code or "").strip().upper()[:1] or None)


def profils_de(code):
    """Les profils Sentinel relevés qui couvrent cette section — souvent aucun."""
    c = (code or "").strip().upper()
    return sorted(cle for cle, p in PROFILS_SENTINEL.items()
                  if c in p["sections"])


def couverture():
    """Ce que chaque section reçoit — et jusqu'où.

    LA DISTINCTION A CHANGÉ DE NATURE, et le chiffre avec elle. Elle opposait
    « couvert » à « non couvert » : neuf sections avaient un profil, treize
    n'avaient rien. Ce partage n'existe plus — les vingt-deux sont couvertes.
    Il a été remplacé par un partage plus juste et plus exigeant : le RÉGIME se
    lit dans les textes, le SOCLE s'observe sur des organisations.

    POURQUOI CE N'EST PAS UN ASSOUPLISSEMENT. L'ancien état laissait treize
    sections sans profil — et l'audit affiché restait alors celui du secteur
    précédent, sans que rien ne le dise. Un client en construction lisait
    l'audit des télécoms. Nommer le régime de sa section et dire que le socle
    n'est pas calibré est plus honnête que de ne rien nommer du tout.

    C'EST TOUJOURS LE CHIFFRE QUI DÉCIDE DE LA LECTURE DU SÉLECTEUR : taire que
    treize profils sur vingt et un n'ont pas de socle observé donnerait vingt et
    une entrées d'apparence équivalente."""
    couvertes = sorted({c for p in PROFILS_SENTINEL.values()
                        for c in p["sections"]})
    releves = sorted({c for p in PROFILS_SENTINEL.values()
                      if p["socle"] == "releve" for c in p["sections"]})
    return {
        "total": len(SECTIONS),
        "avec_profil": len(couvertes),
        "sans_profil": len(SECTIONS) - len(couvertes),
        "codes_avec_profil": couvertes,
        "codes_sans_profil": [s["code"] for s in SECTIONS
                              if s["code"] not in couvertes],
        # Le partage qui décide désormais de ce que l'écran affiche.
        "profils": len(PROFILS_SENTINEL),
        "profils_releves": sorted(k for k, p in PROFILS_SENTINEL.items()
                                  if p["socle"] == "releve"),
        "profils_cadre": sorted(k for k, p in PROFILS_SENTINEL.items()
                                if p["socle"] == "cadre"),
        "codes_socle_releve": releves,
        "codes_socle_cadre": [s["code"] for s in SECTIONS
                              if s["code"] not in releves],
    }


def choisir(code):
    """Ce que Sentinel a pour cette section — et jusqu'où il l'a.

    LES VINGT-DEUX SECTIONS DÉSIGNENT DÉSORMAIS UN PROFIL. Auparavant treize
    n'en désignaient aucun, et l'écran laissait alors l'audit sur le secteur
    d'avant : un client en construction lisait l'audit des télécoms, avec ses
    systèmes, ses régimes et son budget, sans que rien ne le démente. Ne rien
    proposer n'était pas neutre — c'était laisser en place quelque chose de
    faux.

    CE QUI N'A PAS CHANGÉ : « le moins faux » reste un choix qui appartient au
    client. Quand une section désigne plusieurs profils, ce module les rend
    tous et n'en élit aucun. Ce qui a changé est qu'elle en désigne toujours
    au moins un.

    `socle` VOYAGE AVEC CHAQUE PROFIL. Sans lui, un profil dont seul le régime
    est relevé se lirait exactement comme un profil observé.
    """
    s = section(code)
    if not s:
        return {"connu": False, "code": (code or "").strip().upper() or None,
                "section": None, "profils": [],
                "motif": "cette lettre ne désigne aucune section de la NACE "
                         "Rév. 2.1, qui va de A à V"}
    profils = profils_de(s["code"])
    # ── LA HIÉRARCHIE ÉTAIT DANS LES DONNÉES, MAIS SEULEMENT COMME UN ORDRE ──
    # `sections[0]` est la section PRINCIPALE d'un profil : celle où l'essentiel
    # de son activité se range. Les suivantes sont des tranches — les
    # équipementiers réseau relèvent de C, mais « Télécom » n'est pas le profil
    # de l'industrie manufacturière. Les huit profils respectent cette
    # convention, et les notes la disent en prose ; RIEN ne la garantissait. La
    # rendre explicite est ce qui empêche l'écran de présenter quatre profils
    # en pairs pour la section C, et d'inviter un industriel à cocher Télécom.
    principaux = [k for k in profils if PROFILS_SENTINEL[k]["sections"][0] == s["code"]]
    partiels = [k for k in profils if k not in principaux]
    return {
        "connu": True,
        "code": s["code"],
        "section": s,
        "profils": profils,
        "notes": [PROFILS_SENTINEL[p]["note"] for p in profils],
        # LA NOTE VOYAGE AVEC SON PROFIL. Deux listes parallèles se
        # désynchronisent au premier tri fait d'un seul côté, et l'écran
        # attribue alors la note d'un profil à un autre sans que rien ne le
        # signale.
        "principaux": [{"cle": k, "note": PROFILS_SENTINEL[k]["note"],
                        "socle": PROFILS_SENTINEL[k]["socle"]}
                       for k in principaux],
        "partiels": [{"cle": k, "note": PROFILS_SENTINEL[k]["note"],
                      "socle": PROFILS_SENTINEL[k]["socle"],
                      "principale": PROFILS_SENTINEL[k]["sections"][0]}
                     for k in partiels],
        # LE MOTIF DIT CE QUI MANQUE ENCORE, jamais qu'il n'y a rien. Un profil
        # de cadre porte un régime lu dans les textes ; ce qu'il ne porte pas
        # est le point de départ, le budget et la durée — et ces trois-là ne
        # s'extrapolent pas, c'est écrit dans A_RENSEIGNER.
        "motif": None if any(PROFILS_SENTINEL[k]["socle"] == "releve"
                             for k in profils) else (
            "le régime de cette section est relevé — les textes la nomment, ou "
            "disent qu'ils ne la nomment pas — mais son socle ne l'est pas. "
            "L'audit reste entier : les huit piliers, le questionnaire, les "
            "quatre phases et les livrables ne dépendent pas du secteur. Ce "
            "qui manque est le point de départ, le budget et la durée, qui "
            "viennent d'observations et de missions réelles."),
        "socle": ("releve" if any(PROFILS_SENTINEL[k]["socle"] == "releve"
                                  for k in profils) else "cadre"),
        "deplacement_rev2": DEPLACEMENTS_DEPUIS_REV2.get(s["code"]),
    }


def _a_plat(code):
    """Une section, telle que le sélecteur la lit : à plat, motif compris."""
    r = choisir(code)
    return dict(r["section"], profils=r["profils"], notes=r["notes"],
                principaux=r.get("principaux", []), partiels=r.get("partiels", []),
                socle=r.get("socle"),
                motif=r["motif"], deplacement_rev2=r["deplacement_rev2"])


def etat():
    """Tout ce que le sélecteur doit montrer, source et réserve comprises."""
    return {
        "version": VERSION,
        "source": SOURCE,
        "couverture": couverture(),
        # UNE SEULE DÉFINITION DE CE QUE PORTE UNE SECTION. Un premier jet
        # construisait cette liste à part, avec `profils` et le déplacement
        # mais SANS `motif` — et l'écran peignait, pour les treize sections
        # sans profil, un bloc d'explication vide : exactement l'information
        # qui manquait le plus. Le défaut n'a été vu qu'en exécutant le
        # sélecteur. `choisir()` est donc la seule porte, ici comme ailleurs.
        "sections": [_a_plat(s["code"]) for s in SECTIONS],
        "profils_sentinel": PROFILS_SENTINEL,
        "a_renseigner": A_RENSEIGNER,
    }


def sante():
    c = couverture()
    return {"ok": True, "version": VERSION, "sections": c["total"],
            "avec_profil": c["avec_profil"], "revision": SOURCE["revision"]}
