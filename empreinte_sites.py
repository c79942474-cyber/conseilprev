# -*- coding: utf-8 -*-
"""Empreinte environnementale des SIA et des centres de données de l'UE.

CE QUE CE MODULE FAIT
Il applique au parc cartographié — 97 centres de données, 72 systèmes d'IA —
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

INTENSITE = {
    # Très peu carboné — nucléaire et hydraulique dominants
    "FR": 60, "SE": 45, "NO": 30, "FI": 110, "CH": 40, "IS": 30,
    # Intermédiaire
    "ES": 190, "PT": 200, "AT": 160, "SI": 250, "DK": 180, "BE": 170,
    "SK": 170, "HR": 240, "LT": 200, "LV": 190, "IT": 330, "GB": 250,
    "IE": 350, "NL": 350, "HU": 240, "RO": 290,
    # Fortement carboné — charbon et lignite encore présents
    "DE": 380, "CZ": 470, "GR": 420, "BG": 480, "PL": 660, "EE": 620,
    "CY": 640, "MT": 430, "LU": 220,
    # Repli
    "UE": 250,
}
INTENSITE_DEFAUT = 250

SOURCE_INTENSITE = ("Ordres de grandeur cycle de vie, d’après la Base Empreinte de "
                    "l’ADEME, l’Agence internationale de l'énergie et les facteurs "
                    "par filière du GIEC. Moyennes annuelles.")

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
    "PARC ≠ TOTAL — 97 centres de données et 72 systèmes d’IA sont cartographiés ; "
    "le parc européen réel en compte plusieurs milliers. Les cumuls par pays ne "
    "sont donc pas des inventaires nationaux.",
    "Les intensités carbone sont des moyennes annuelles. L’intensité réelle varie "
    "d’un facteur trois dans la journée : un calcul déplacé de la nuit au midi "
    "solaire change son empreinte sans changer sa consommation.",
    "L’eau comptée est celle du refroidissement. L’eau consommée en amont pour "
    "produire l’électricité — considérable pour le thermique et le nucléaire — "
    "n’est PAS incluse : la faire figurer sans la distinguer mélangerait deux "
    "responsabilités différentes.",
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
        p["total_t"] = [round(p["dc_t"][0] + p["sia_t"][0]),
                        round(p["dc_t"][1] + p["sia_t"][1])]
        for k in ("dc_t", "sia_t", "eau_m3"):
            p[k] = [round(p[k][0]), round(p[k][1])]

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
        },
        "avertissement": AVERTISSEMENT,
        "limites": LIMITES,
        "maj": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def sante():
    return {"version": VERSION, "pays_references": len(INTENSITE),
            "types_sia": len(SIA_MWH_AN)}
