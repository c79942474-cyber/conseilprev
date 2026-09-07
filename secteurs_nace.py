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
    "reserve": "Les intitulés officiels reproduits ci-dessous sont ceux de la "
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
                  "note": "Les opérateurs et fournisseurs de services relèvent "
                          "de K ; les équipementiers réseau, qui fabriquent, "
                          "de C."},
    "energie":   {"sections": ["D", "E"],
                  "note": "L'électricité et le gaz relèvent de D ; l'eau, "
                          "l'assainissement et les déchets de E."},
    "sante":     {"sections": ["R", "C", "K"],
                  "note": "Les établissements de soins relèvent de R ; les "
                          "fabricants de dispositifs médicaux de C ; les "
                          "éditeurs de logiciels de santé de K."},
    "finance":   {"sections": ["L"],
                  "note": "Banques, assureurs, gestion et paiement relèvent "
                          "tous de L — qui était K avant la révision 2.1."},
    "industrie": {"sections": ["C"],
                  "note": "L'ensemble de l'industrie manufacturière."},
    "transport": {"sections": ["H", "C"],
                  "note": "L'exploitation et la logistique relèvent de H ; les "
                          "constructeurs de véhicules de C."},
    "it":        {"sections": ["K", "J"],
                  "note": "L'édition de logiciels, le cloud et les services "
                          "numériques relèvent de K ; les plateformes de "
                          "contenus de J."},
    "public":    {"sections": ["P"],
                  "note": "Administrations centrales, territoriales et "
                          "organismes publics."},
}

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
    """Quelles sections un profil relevé couvre, et lesquelles non.

    C'EST LE CHIFFRE QUI DÉCIDE DE LA LECTURE DU SÉLECTEUR, comme la couverture
    décide de celle d'un total FinOps. Vingt-deux sections proposées dont neuf
    seulement portent un profil relevé : le taire donnerait vingt-deux entrées
    d'apparence équivalente."""
    couvertes = sorted({c for p in PROFILS_SENTINEL.values()
                        for c in p["sections"]})
    return {
        "total": len(SECTIONS),
        "avec_profil": len(couvertes),
        "sans_profil": len(SECTIONS) - len(couvertes),
        "codes_avec_profil": couvertes,
        "codes_sans_profil": [s["code"] for s in SECTIONS
                              if s["code"] not in couvertes],
    }


def choisir(code):
    """Ce que Sentinel a pour cette section — profil relevé, ou rien de relevé.

    LA SORTIE EST LA MÊME DANS LES DEUX CAS, et c'est voulu : un appelant qui
    ne lirait que `profils` doit tomber sur une liste vide, jamais sur un
    profil de repli choisi à sa place. « Le moins faux » est un choix qui
    appartient au client, pas à ce module.
    """
    s = section(code)
    if not s:
        return {"connu": False, "code": (code or "").strip().upper() or None,
                "section": None, "profils": [],
                "motif": "cette lettre ne désigne aucune section de la NACE "
                         "Rév. 2.1, qui va de A à V"}
    profils = profils_de(s["code"])
    return {
        "connu": True,
        "code": s["code"],
        "section": s,
        "profils": profils,
        "notes": [PROFILS_SENTINEL[p]["note"] for p in profils],
        "motif": None if profils else (
            "aucun profil sectoriel n'est relevé pour cette section. L'audit "
            "reste utilisable : les huit piliers et le questionnaire ne "
            "dépendent pas du secteur. Ce qui manque est le point de départ, "
            "les spécificités réglementaires du secteur et les repères de "
            "budget — et ces trois-là ne s'extrapolent pas."),
        "deplacement_rev2": DEPLACEMENTS_DEPUIS_REV2.get(s["code"]),
    }


def _a_plat(code):
    """Une section, telle que le sélecteur la lit : à plat, motif compris."""
    r = choisir(code)
    return dict(r["section"], profils=r["profils"], notes=r["notes"],
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
