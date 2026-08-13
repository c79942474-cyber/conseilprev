# -*- coding: utf-8 -*-
"""Empreinte environnementale des SIA et des centres de données de l'UE.

CE QUE CE MODULE FAIT
Il applique au parc cartographié — 249 centres de données, 72 systèmes d'IA —
la même chaîne de calcul que la page /empreinte du site : consommation, PUE,
intensité carbone du pays, impacts incorporés de fabrication. Il en tire une
vue par site, par pays et par cycle de vie.

CE QU'IL NE FAIT PAS, ET POURQUOI
Il ne mesure rien. Aucun exploitant européen ne publie, site par site, sa
consommation électrique ni sa consommation d'eau — c'est le constat qui a
fondé le module datacentres, et il vaut aussi ici. Tout ce qui suit est donc
CALCULÉ, avec la formule sous les yeux du lecteur, et hérite de la nature de
l'estimation d'entrée : « site » quand la capacité est annoncée, « classe »
quand elle ne l'est pas. Une valeur de classe répond à « de quel ordre est un
campus de ce type ? », jamais à « combien émet CE site ? ».

LE CYCLE DE VIE, EN ENTIER
Trois postes, jamais confondus :
  usage         électricité consommée × intensité carbone du pays
  fabrication   serveurs, baies, bâtiment — amortis sur leur durée de vie
  eau           refroidissement, en mètres cubes, hors eau virtuelle du mix
Le poste fabrication est celui qu'on oublie le plus souvent : sur un site
alimenté en électricité peu carbonée, il devient majoritaire, et une carte
qui n'afficherait que l'usage classerait la Suède ou la France bien plus bas
que la réalité de leur empreinte.

SOURCES
ADEME (Base Empreinte, facteurs d'émission cycle de vie), Agence internationale
de l'énergie, Centre commun de recherche de la Commission, GIEC pour les
facteurs par filière. Aucun import Flask, aucun appel réseau : les intensités
temps réel sont INJECTÉES par l'appelant, qui seul sait les obtenir.
"""
import json
from datetime import datetime, timezone

VERSION = "2026-07-a"

# ═══════════════════════════════════════════════════════════════════════════
# 1. INTENSITÉ CARBONE DE L'ÉLECTRICITÉ — gCO2eq/kWh, CYCLE DE VIE
#
#    « Cycle de vie » et non « combustion » : le facteur inclut la
#    construction des moyens de production. C'est ce qui empêche de compter
#    le nucléaire ou l'éolien à zéro, et c'est la convention de la Base
#    Empreinte de l’ADEME comme des travaux du GIEC.
#
#    Ces valeurs sont des ORDRES DE GRANDEUR par pays, moyennés sur l'année.
#    L'intensité réelle varie d'un facteur trois dans la journée : quand
#    l'appelant sait obtenir la valeur du moment (RTE pour la France,
#    ENTSO-E ailleurs), il l'injecte et le module l'utilise à la place.
# ═══════════════════════════════════════════════════════════════════════════

# Millésime 2024, approche CYCLE DE VIE, une seule source de référence pour
# tout le tableau : les moyennes annuelles publiées par Ember (facteurs GIEC
# AR5). Le millésime unique est un choix de méthode, pas un détail — mélanger
# des années dans un tableau comparatif fausse précisément la comparaison qu'on
# vient y chercher.
#
# La table précédente datait de 2021-2022 et surestimait la plupart des pays
# de 25 à 80 % : les réseaux européens se sont décarbonés vite (sortie du
# lignite grec et bulgare, éolien néerlandais, Olkiluoto 3 en Finlande,
# Mochovce 3 en Slovaquie). Le contrôle factuel de juillet 2026 a mesuré ces
# écarts un par un ; ils sont publiés dans factcheck.py, avec la valeur
# d'origine de chaque pays corrigé.
#
# DEUX LIMITES ÉCRITES ICI PARCE QU'ELLES CHANGENT LA LECTURE :
#  — Approche PRODUCTION. Pour les pays qui importent une grande part de leur
#    électricité (Luxembourg ~60 %, Lituanie ~29 %, Malte via la Sicile),
#    l'intensité vue par un site raccordé au réseau est sensiblement plus
#    élevée que celle de la production nationale. LU garde donc une valeur
#    intermédiaire assumée, entre production (~130) et consommation (~290).
#  — La France est à 45 g dans le référentiel Ember, quand la Base Empreinte
#    de l'ADEME retient environ 60 g pour le mix français : périmètres et
#    méthodes diffèrent. Un client travaillant dans le cadre ADEME doit
#    substituer sa propre valeur ; le calcul est publié pour cela.
INTENSITE = {
    # Très peu carboné — nucléaire et hydraulique dominants
    "FR": 45, "SE": 35, "NO": 30, "FI": 65, "CH": 35, "IS": 30,
    # Intermédiaire
    "ES": 145, "PT": 110, "AT": 105, "SI": 230, "DK": 130, "BE": 125,
    "SK": 95, "HR": 170, "LT": 200, "LV": 170, "IT": 280, "GB": 215,
    "IE": 270, "NL": 250, "HU": 195, "RO": 230,
    # Fortement carboné — charbon et lignite encore présents
    "DE": 355, "CZ": 400, "GR": 320, "BG": 320, "PL": 660, "EE": 415,
    "CY": 510, "MT": 490, "LU": 220,
    # Repli
    "UE": 235,
}
INTENSITE_DEFAUT = 235

SOURCE_INTENSITE = ("Moyennes annuelles 2024, approche cycle de vie, d’après les "
                    "séries Ember (facteurs GIEC AR5), recoupées avec l’Agence "
                    "européenne pour l’environnement. Approche production : pour "
                    "un pays fortement importateur, l’intensité vue au point de "
                    "raccordement est plus élevée.")

# ═══════════════════════════════════════════════════════════════════════════
# 2. FABRICATION — LE POSTE QU'ON OUBLIE
#
#    Part des impacts incorporés (serveurs, stockage, réseau, bâtiment)
#    rapportée aux émissions d'usage, une fois amortie sur la durée de vie des
#    équipements. La page /empreinte du site retient 30 % pour les modèles ;
#    on retient la même valeur ici, pour que les deux chiffrages du site
#    reposent sur la même hypothèse et restent comparables.
#
#    Conséquence à dire au lecteur : sur un site suédois alimenté à 45 gCO2/kWh,
#    la fabrication pèse plus lourd que l'usage. Une carte qui n'afficherait
#    que l'usage classerait ce site quasiment à zéro — ce serait faux.
# ═══════════════════════════════════════════════════════════════════════════

FABRICATION_PCT = 30.0

# Sur les sites très peu carbonés, la part relative de la fabrication grimpe
# mécaniquement. On l'exprime en kgCO2e par MWh informatique plutôt qu'en
# pourcentage de l'usage, ce qui la rend indépendante du mix local.
FABRICATION_KG_PAR_MWH = 22.0
SOURCE_FABRICATION = ("Impacts incorporés amortis : ordre de grandeur issu des "
                      "travaux Boavizta et des analyses de cycle de vie "
                      "constructeurs, exprimé par MWh informatique produit.")

# ═══════════════════════════════════════════════════════════════════════════
# 3. SYSTÈMES D'IA — ORDRE DE GRANDEUR PAR TYPE
#
#    Un cas du panel n'a ni capacité ni consommation publiée : il n'a qu'un
#    TYPE et un STADE de déploiement. On en tire un ordre de grandeur annuel,
#    en MWh, toujours en fourchette et toujours marqué « classe ».
#
#    Ces valeurs disent : « un assistant génératif déployé à l'échelle d'un
#    grand groupe consomme de cet ordre ». Elles ne disent rien du système
#    d'une entreprise en particulier, et la carte l'écrit à chaque fois.
# ═══════════════════════════════════════════════════════════════════════════

SIA_MWH_AN = {
    "assistant_llm":          (40, 900),
    "chatbot_client":         (30, 700),
    "agent_autonome":         (25, 500),
    "scoring_ml":             (5, 90),
    "rh_recrutement":         (2, 40),
    "vision_industrielle":    (10, 160),
    "biometrie":              (8, 130),
    "optimisation_predictive": (6, 110),
    "surveillance_salaries":  (4, 70),
    "sante_dm":               (3, 60),
    "observation_terre":      (20, 400),
}
# Le stade module l'ordre de grandeur : un POC ne consomme pas comme un
# déploiement à l'échelle d'un groupe de 140 000 personnes.
SIA_STADE = {
    "poc": (0.05, 0.15), "pilote": (0.15, 0.40), "production": (0.5, 1.0),
    "echelle": (1.0, 1.0), "abandonne": (0.0, 0.0),
}

AVERTISSEMENT = (
    "Aucune de ces valeurs n’est mesurée. Elles sont calculées à partir d’ordres "
    "de grandeur de catégorie, avec la formule affichée, et servent à situer un "
    "parc — jamais à comparer deux sites nommément, ni à établir un bilan "
    "réglementaire. Le bilan réglementaire viendra de la base européenne créée "
    "par la directive (UE) 2023/1791, qui recueillera des valeurs DÉCLARÉES."
)

LIMITES = [
    # Les deux comptes sont des GABARITS remplis a l'assemblage : ecrits en dur,
    # ils mentaient des la premiere extension du referentiel — et un chiffre faux
    # dans la phrase qui avertit du perimetre est le pire endroit pour en avoir un.
    "PARC ≠ TOTAL — {n_dc} centres de données et {n_sia} systèmes d’IA sont cartographiés ; "
    "le parc européen réel en compte plusieurs milliers. Les cumuls par pays ne "
    "sont donc pas des inventaires nationaux.",
    "Les intensités carbone sont des moyennes annuelles. L’intensité réelle varie "
    "d’un facteur trois dans la journée : un calcul déplacé de la nuit au midi "
    "solaire change son empreinte sans changer sa consommation.",
    # CETTE LIMITE DISAIT LE CONTRAIRE, ET ELLE AVAIT CESSÉ D'ÊTRE VRAIE. Elle
    # annonçait que l'eau amont n'est PAS incluse — c'était exact tant que
    # personne ne la calculait. Elle l'est depuis, par eau_dc.py, et elle
    # s'affiche dans la même section, quelques lignes plus bas. Un avertissement
    # qui survit à sa cause envoie chercher ailleurs ce qui est sous les yeux.
    "L’eau de la colonne ci-contre est celle du REFROIDISSEMENT, et elle seule. "
    "L’eau consommée en amont pour produire l’électricité — considérable pour le "
    "thermique et le nucléaire — n’y est pas ajoutée, pour ne pas mélanger deux "
    "responsabilités : elle est calculée et publiée À PART, dans le bilan « l’eau "
    "que le WUE ne compte pas » de cette même section. Sur les parcs nationaux "
    "où les deux termes sont publiés, l’amont pèse de huit à douze fois le site.",
    "L’eau de FABRICATION du matériel n’est comptée nulle part — ni ici, ni dans "
    "le bilan amont. Une usine de semi-conducteurs consomme de l’ordre de "
    "38 millions de litres d’eau ultrapure par jour ; la part imputable à un "
    "serveur ne se reconstitue pas sans données constructeur, et les fabricants "
    "ne les publient pas. Le poste fabrication ci-dessus porte donc le CARBONE "
    "incorporé, jamais l’eau incorporée.",
    "La fabrication est amortie linéairement, sans tenir compte du taux de "
    "renouvellement réel des serveurs, plus rapide sur les charges d’IA.",
    "Un projet annoncé qui ne se réalise pas figure au cumul de son pays tant "
    "qu’il n’est pas retiré du référentiel. Le curseur d’horizon permet de "
    "l’écarter de la lecture.",
]


def intensite_pays(code, live=None):
    """(gCO2e/kWh, libellé de source). `live` prime sur la moyenne annuelle."""
    c = str(code or "").upper()
    if live and c in live:
        try:
            return float(live[c]), "intensité du moment, mesurée par le gestionnaire de réseau"
        except (TypeError, ValueError):
            pass
    if c in INTENSITE:
        return float(INTENSITE[c]), "moyenne annuelle, cycle de vie"
    return float(INTENSITE_DEFAUT), "valeur de repli européenne, cycle de vie"


def empreinte_site(site, estimation, live=None):
    """Empreinte annuelle d'un centre de données, sur tout le cycle de vie.

    `estimation` est le résultat de datacentres.estimer() : on en HÉRITE la
    nature. Un site dont la consommation est de nature « classe » ne peut pas
    produire une empreinte de nature « site » — ce serait blanchir une
    approximation en la faisant passer par une multiplication."""
    if not estimation or estimation.get("nature") == "indisponible":
        return {"nature": "indisponible", "usage_t": None, "fabrication_t": None,
                "total_t": None, "eau_m3": None, "intensite": None,
                "motif": "consommation non estimable — aucune empreinte dérivable"}

    gwh = estimation.get("electricite")
    if not gwh:
        return {"nature": "indisponible", "usage_t": None, "fabrication_t": None,
                "total_t": None, "eau_m3": None, "intensite": None,
                "motif": "consommation non estimable — aucune empreinte dérivable"}

    fe, src_fe = intensite_pays(site.get("pays"), live)
    # GWh × 1000 = MWh ; MWh × gCO2/kWh = kgCO2 ; / 1000 = tonnes
    usage = [round(gwh[0] * 1000 * fe / 1000.0), round(gwh[1] * 1000 * fe / 1000.0)]
    # Fabrication : indexée sur l'énergie INFORMATIQUE, donc hors PUE. On
    # retire le PUE moyen du couple pour ne pas imputer aux serveurs l'énergie
    # dépensée à les refroidir.
    fab = [round(gwh[0] * 1000 / 1.3 * FABRICATION_KG_PAR_MWH / 1000.0),
           round(gwh[1] * 1000 / 1.3 * FABRICATION_KG_PAR_MWH / 1000.0)]
    total = [usage[0] + fab[0], usage[1] + fab[1]]
    # Part de la fabrication dans le total, au point bas : c'est la lecture
    # qui surprend le plus sur les sites nordiques.
    part_fab = round(100.0 * fab[0] / total[0]) if total[0] else None
    return {
        "nature": estimation["nature"],          # jamais meilleure que l'entrée
        "usage_t": usage, "fabrication_t": fab, "total_t": total,
        "part_fabrication_pct": part_fab,
        "eau_m3": estimation.get("eau"),
        "intensite": fe, "source_intensite": src_fe,
        "formule": ("électricité annuelle (GWh) × %g gCO2e/kWh pour l'usage ; "
                    "énergie informatique × %g kgCO2e/MWh pour la fabrication amortie"
                    % (fe, FABRICATION_KG_PAR_MWH)),
        "motif": None,
    }


def empreinte_sia(cas, live=None):
    """Empreinte annuelle d'un système d'IA du panel, par ordre de grandeur.

    Toujours de nature « classe » : un cas n'a ni capacité ni consommation
    publiée, seulement un type et un stade."""
    plage = SIA_MWH_AN.get(cas.get("type"))
    fac = SIA_STADE.get(cas.get("stade"))
    if not plage or not fac or fac[1] == 0:
        return {"nature": "indisponible", "usage_t": None, "total_t": None,
                "mwh": None, "intensite": None,
                "motif": ("système abandonné — aucune consommation courante"
                          if cas.get("stade") == "abandonne"
                          else "type ou stade inconnu du barème")}
    mwh = [round(plage[0] * fac[0], 1), round(plage[1] * fac[1], 1)]
    fe, src_fe = intensite_pays(cas.get("pays"), live)
    usage = [round(mwh[0] * fe / 1000.0, 1), round(mwh[1] * fe / 1000.0, 1)]
    fab = [round(mwh[0] * FABRICATION_KG_PAR_MWH / 1000.0, 1),
           round(mwh[1] * FABRICATION_KG_PAR_MWH / 1000.0, 1)]
    return {
        "nature": "classe",
        "mwh": mwh,
        "usage_t": usage, "fabrication_t": fab,
        "total_t": [round(usage[0] + fab[0], 1), round(usage[1] + fab[1], 1)],
        "intensite": fe, "source_intensite": src_fe,
        "formule": ("ordre de grandeur du type « %s » (%g–%g MWh/an) × facteur de "
                    "stade « %s » × %g gCO2e/kWh"
                    % (cas.get("type_nom") or cas.get("type"), plage[0], plage[1],
                       cas.get("stade"), fe)),
        "motif": None,
    }


def assemble(sites=None, cas=None, live=None):
    """Vue d'ensemble : par site, par cas, et cumuls par pays.

    `sites` et `cas` sont fournis par l'appelant (datacentres / panorama_ia) —
    le module ne les importe pas, il reste utilisable seul et testable seul."""
    sites = sites or []
    cas = cas or []
    par_pays, dc, sia = {}, [], []

    def _cumul(code, cle, val):
        if not val:
            return
        p = par_pays.setdefault(code, {
            "pays": code, "n_dc": 0, "n_sia": 0,
            "dc_t": [0, 0], "sia_t": [0, 0], "eau_m3": [0, 0],
            "intensite": intensite_pays(code, live)[0],
        })
        p[cle][0] += val[0]
        p[cle][1] += val[1]

    for s in sites:
        e = empreinte_site(s, s.get("estimation"), live)
        dc.append({"id": s.get("id"), "operateur": s.get("operateur"), "ville": s.get("ville"),
                   "pays": s.get("pays"), "statut": s.get("statut"),
                   "annee_service": s.get("annee_service"), "gabarit": s.get("gabarit"),
                   "empreinte": e})
        code = s.get("pays")
        if code:
            par_pays.setdefault(code, {"pays": code, "n_dc": 0, "n_sia": 0,
                                       "dc_t": [0, 0], "sia_t": [0, 0], "eau_m3": [0, 0],
                                       "intensite": intensite_pays(code, live)[0]})
            par_pays[code]["n_dc"] += 1
            # COMBIEN ONT PU ÊTRE ESTIMÉS. Un site sans capacité annoncée ni
            # gabarit ne produit aucune empreinte : `_cumul` l'ignore, et la
            # somme de rien vaut zéro. Un pays dont AUCUN site n'est estimable
            # affichait donc « 0 t de CO2e » en face de son nombre de centres —
            # une absence de calcul lue comme un parc propre. On compte donc
            # ceux qui ont produit un chiffre, pour pouvoir dire l'autre cas.
            if e.get("total_t"):
                par_pays[code]["dc_estimes"] = par_pays[code].get("dc_estimes", 0) + 1
            _cumul(code, "dc_t", e.get("total_t"))
            _cumul(code, "eau_m3", e.get("eau_m3"))

    for c in cas:
        e = empreinte_sia(c, live)
        sia.append({"id": c.get("id"), "entreprise": c.get("entreprise"),
                    "pays": c.get("pays"), "type": c.get("type"),
                    "type_nom": c.get("type_nom"), "stade": c.get("stade"),
                    "empreinte": e})
        code = c.get("pays")
        if code:
            par_pays.setdefault(code, {"pays": code, "n_dc": 0, "n_sia": 0,
                                       "dc_t": [0, 0], "sia_t": [0, 0], "eau_m3": [0, 0],
                                       "intensite": intensite_pays(code, live)[0]})
            par_pays[code]["n_sia"] += 1
            _cumul(code, "sia_t", e.get("total_t"))

    for p in par_pays.values():
        # Chaque pays dit si son intensité vient du RELEVÉ DU MOMENT ou de la
        # moyenne annuelle. Sans ce drapeau, une carte rafraîchie en continu et
        # une carte figée se ressemblent — et rien ne signalerait qu'une source
        # est tombée.
        p["intensite_direct"] = bool(live and p["pays"] in (live or {}))
        p["total_t"] = [round(p["dc_t"][0] + p["sia_t"][0]),
                        round(p["dc_t"][1] + p["sia_t"][1])]
        for k in ("dc_t", "sia_t", "eau_m3"):
            p[k] = [round(p[k][0]), round(p[k][1])]
        p.setdefault("dc_estimes", 0)
        p["dc_non_estimes"] = p["n_dc"] - p["dc_estimes"]
        # `estimable` est faux quand le pays porte des centres mais qu'AUCUN
        # n'a pu être chiffré. Le zéro qui suit n'est alors pas une mesure, et
        # l'interface doit écrire « non estimée », jamais « 0 ».
        p["estimable"] = not (p["n_dc"] > 0 and p["dc_estimes"] == 0
                              and p["total_t"][1] == 0)
        p["motif_non_estimable"] = (None if p["estimable"] else
                                    "%s recensé%s dans ce pays ne porte%s ni capacité "
                                    "annoncée ni gabarit : aucune empreinte ne peut en "
                                    "être dérivée. Un zéro affiché serait une absence de "
                                    "calcul, pas une absence d'émissions"
                                    % ("Le seul centre" if p["n_dc"] == 1
                                       else "Les %d centres" % p["n_dc"],
                                       "" if p["n_dc"] == 1 else "s",
                                       "" if p["n_dc"] == 1 else "nt"))

    total = [sum(p["total_t"][0] for p in par_pays.values()),
             sum(p["total_t"][1] for p in par_pays.values())]
    eau = [sum(p["eau_m3"][0] for p in par_pays.values()),
           sum(p["eau_m3"][1] for p in par_pays.values())]

    return {
        "version": VERSION,
        "centres": dc,
        "systemes": sia,
        "par_pays": sorted(par_pays.values(), key=lambda x: -x["total_t"][0]),
        "totaux": {"co2_t": total, "eau_m3": eau,
                   "n_centres": len(dc), "n_systemes": len(sia)},
        "referentiel": {
            "intensite": INTENSITE, "intensite_defaut": INTENSITE_DEFAUT,
            "source_intensite": SOURCE_INTENSITE,
            "fabrication_kg_par_mwh": FABRICATION_KG_PAR_MWH,
            "source_fabrication": SOURCE_FABRICATION,
            "sia_mwh_an": {k: list(v) for k, v in SIA_MWH_AN.items()},
            "sia_stade": {k: list(v) for k, v in SIA_STADE.items()},
            # Les pays dont l'intensité vient du relevé du moment, et la valeur
            # relevée : publiés pour que le lecteur distingue une carte vivante
            # d'une carte figée sans avoir à nous croire.
            "intensite_direct": sorted((live or {}).keys()),
            "intensite_direct_valeurs": {k: round(float(v), 1) for k, v in (live or {}).items()},
        },
        "avertissement": AVERTISSEMENT,
        # Le gabarit est rempli ici, ou les deux longueurs sont connues.
        "limites": [l.format(n_dc=len(sites), n_sia=len(cas)) if "{n_dc}" in l else l
                    for l in LIMITES],
        "maj": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def sante():
    return {"version": VERSION, "pays_references": len(INTENSITE),
            "types_sia": len(SIA_MWH_AN)}
