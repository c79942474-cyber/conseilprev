# -*- coding: utf-8 -*-
"""Centres de données européens — sites, statuts, énergie, eau, investissement.

CE QUE CE MODULE ÉTABLIT
Un point sur une carte : où se trouve un centre de données, à quel stade il en
est, ce que son exploitant a ANNONCÉ en capacité, en date et en investissement.
Rien de plus. Une annonce n'est pas une mise en service, une capacité à terme
n'est pas une capacité installée, et un investissement annoncé n'est pas un
investissement engagé.

CE QU'IL CALCULE, ET POURQUOI IL LE DIT
La consommation électrique et la consommation d'eau d'un site ne sont presque
jamais publiées. Plutôt que de laisser la case vide — ce qui laisserait croire
qu'il n'y a rien à dire — le module en donne un ORDRE DE GRANDEUR calculé à
partir de la capacité annoncée, avec la formule sous les yeux du lecteur et
toujours sous forme de FOURCHETTE. Un site sans capacité annoncée ne reçoit
aucune estimation : on ne dérive pas d'un vide.

POURQUOI CES DONNÉES N'EXISTENT PAS ENCORE, ET POURQUOI CELA CHANGE
La directive (UE) 2023/1791 sur l'efficacité énergétique, en son article 12,
et le règlement délégué (UE) 2024/1364 obligent les centres de données au-delà
d'un seuil de puissance à déclarer leurs performances — énergie ET eau — dans
une base de données européenne. C'est la source qui rendra un jour ce module
inutile, et c'est tant mieux : elle sera mesurée là où nous estimons.

ARCHITECTURE
Aucun import Flask, aucun appel réseau, aucun modèle de langage dans la chaîne
de calcul : le référentiel est figé par version, les dérivations sont
déterministes et relisibles ligne à ligne.
"""
import json
from datetime import datetime, timezone

VERSION = "2026-07-a"

# ═══════════════════════════════════════════════════════════════════════════
# 1. STATUTS
#    L'ordre est celui de la certitude décroissante : ce qui tourne, ce qui se
#    construit, ce qui est autorisé, ce qui n'est qu'annoncé. La couleur suit.
# ═══════════════════════════════════════════════════════════════════════════

STATUTS = {
    "service": {
        "nom": "En exploitation", "rang": 1, "couleur": "#1C4E80",
        "sens": "le site fonctionne ; sa capacité peut encore monter par tranches",
    },
    "construction": {
        "nom": "En construction", "rang": 2, "couleur": "#C24E37",
        "sens": "chantier engagé ; la date de mise en service reste une cible",
    },
    "autorise": {
        "nom": "Autorisé", "rang": 3, "couleur": "#D89A3C",
        "sens": "permis obtenu, chantier non démarré — le projet peut encore ne pas se faire",
    },
    "annonce": {
        "nom": "Annoncé", "rang": 4, "couleur": "#8A8A8A",
        "sens": "projet rendu public sans autorisation connue : l'information la plus fragile",
    },
    "abandonne": {
        "nom": "Abandonné ou refusé", "rang": 5, "couleur": "#B9B4AC",
        "sens": "projet public puis arrêté — conservé parce qu'un projet mort renseigne "
                "autant qu'un projet vivant sur les contraintes d'un territoire",
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. BARÈME DE DÉRIVATION — DÉTERMINISTE
#
#    Trois grandeurs, trois pièges, expliqués une fois pour toutes :
#
#    MW informatiques   la puissance des serveurs. C'est ce que les exploitants
#                       annoncent. Ce n'est PAS la puissance tirée du réseau.
#    PUE                rapport entre l'énergie totale du site et l'énergie
#                       informatique. Un PUE de 1,3 signifie 30 % d'énergie en
#                       plus pour refroidir, onduler, éclairer.
#    Facteur de charge  un site n'a jamais ses serveurs à 100 % en permanence.
#                       Retenir 100 % gonflerait tous les résultats.
#
#    WUE                litres d'eau consommés par kilowattheure informatique.
#                       Il dépend massivement du mode de refroidissement : un
#                       site en free cooling nordique et un site adiabatique
#                       espagnol ne sont pas comparables.
# ═══════════════════════════════════════════════════════════════════════════

HEURES_AN = 8760

# Fourchettes, jamais de valeur unique : la vérité d'un site inconnu est un
# intervalle, et présenter un point donnerait une précision qu'on n'a pas.
CHARGE = (0.55, 0.80)          # facteur de charge annuel moyen

PUE = {                        # (mini, maxi) par mode de refroidissement
    "free_cooling":          (1.10, 1.25),
    "recuperation_chaleur":  (1.10, 1.30),
    "eau":                   (1.15, 1.35),
    "adiabatique":           (1.20, 1.45),
    "air":                   (1.30, 1.60),
    "inconnu":               (1.15, 1.55),
}

WUE = {                        # litres d'eau par kWh informatique
    "free_cooling":          (0.00, 0.10),
    "recuperation_chaleur":  (0.00, 0.20),
    "air":                   (0.00, 0.20),
    "eau":                   (0.20, 1.20),
    "adiabatique":           (0.80, 2.20),
    "inconnu":               (0.00, 2.20),
}

AVERTISSEMENT = (
    "Ces deux grandeurs sont CALCULÉES à partir de la capacité annoncée, pas "
    "mesurées. Elles donnent un ordre de grandeur et une fourchette ; elles ne "
    "valent pas une déclaration d'exploitant et ne peuvent fonder aucune "
    "comparaison entre deux sites précis."
)

FORMULE_ELEC = ("capacité MW × 8 760 h × facteur de charge (%.2f–%.2f) × PUE (%s) "
                "→ GWh par an")
FORMULE_EAU = ("capacité MW × 8 760 h × facteur de charge (%.2f–%.2f) × WUE (%s L/kWh) "
               "→ m³ par an")


def _fourchette_pue(mode):
    return PUE.get(mode, PUE["inconnu"])


def _fourchette_wue(mode):
    return WUE.get(mode, WUE["inconnu"])


def estimer(site):
    """Ordre de grandeur annuel d'électricité (GWh) et d'eau (m³).

    Renvoie des FOURCHETTES et la formule employée. Un site sans capacité
    annoncée ne reçoit rien : dériver d'une capacité absente reviendrait à
    inventer le chiffre que l'on prétend estimer."""
    mw = site.get("capacite_mw")
    mode = site.get("refroidissement") or "inconnu"
    if not mw:
        return {"nature": "indisponible", "electricite": None, "eau": None,
                "formule_electricite": None, "formule_eau": None,
                "motif": "capacité non annoncée — aucune dérivation possible"}

    pue_min, pue_max = _fourchette_pue(mode)
    wue_min, wue_max = _fourchette_wue(mode)
    # MWh informatiques bruts, avant PUE
    base_min = mw * HEURES_AN * CHARGE[0]
    base_max = mw * HEURES_AN * CHARGE[1]

    elec = (round(base_min * pue_min / 1000.0, 1),      # MWh → GWh
            round(base_max * pue_max / 1000.0, 1))
    # 1 kWh informatique × WUE (L/kWh) → litres ; ÷ 1000 → m³
    eau = (round(base_min * 1000 * wue_min / 1000.0),
           round(base_max * 1000 * wue_max / 1000.0))

    return {
        "nature": "estime",
        "electricite": list(elec),
        "eau": list(eau),
        "formule_electricite": FORMULE_ELEC % (CHARGE[0], CHARGE[1],
                                               "%.2f–%.2f" % (pue_min, pue_max)),
        "formule_eau": FORMULE_EAU % (CHARGE[0], CHARGE[1],
                                      "%.2f–%.2f" % (wue_min, wue_max)),
        "motif": None,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 3. RÉFÉRENTIEL DES SITES
#    Rempli par compilation puis réfutation adversariale : chaque entrée a été
#    proposée par un premier examen, puis contestée par un second dont la
#    consigne était de la mettre en défaut. Les entrées dégradées ont vu leurs
#    chiffres non attestés remis à vide plutôt que conservés « au cas où ».
# ═══════════════════════════════════════════════════════════════════════════

SITES = []          # rempli plus bas, à la version courante
RETIRES = []        # sites écartés en réfutation, avec leur motif
CADRE = {}          # obligations européennes de déclaration
LIMITES = []


def _enrichir():
    out = []
    for i, brut in enumerate(SITES):
        s = dict(brut)
        s["id"] = "dc-%03d" % (i + 1)
        s["statut_nom"] = STATUTS[s["statut"]]["nom"]
        s["statut_couleur"] = STATUTS[s["statut"]]["couleur"]
        s["statut_rang"] = STATUTS[s["statut"]]["rang"]
        s["estimation"] = estimer(s)
        # Ce qui est publié prime toujours sur ce qui est calculé, et le module
        # dit lequel des deux il sert.
        s["elec_nature"] = "publie" if s.get("elec_gwh_an") else s["estimation"]["nature"]
        s["eau_nature"] = "publie" if s.get("eau_m3_an") else s["estimation"]["nature"]
        out.append(s)
    return out


def _agreger(sites):
    par_statut, par_pays = {}, {}
    mw_total = 0.0
    inv_total = 0.0
    n_mw = n_inv = 0
    for s in sites:
        par_statut[s["statut"]] = par_statut.get(s["statut"], 0) + 1
        p = par_pays.setdefault(s["pays"], {"pays": s["pays"], "n": 0, "mw": 0.0, "meur": 0.0})
        p["n"] += 1
        if s.get("capacite_mw"):
            p["mw"] += s["capacite_mw"]; mw_total += s["capacite_mw"]; n_mw += 1
        if s.get("investissement_meur"):
            p["meur"] += s["investissement_meur"]; inv_total += s["investissement_meur"]; n_inv += 1
    for p in par_pays.values():
        p["mw"] = round(p["mw"], 1)
        p["meur"] = round(p["meur"], 1)
    return {
        "par_statut": par_statut,
        "par_pays": sorted(par_pays.values(), key=lambda x: -x["n"]),
        "capacite_mw_cumulee": round(mw_total, 1),
        "investissement_meur_cumule": round(inv_total, 1),
        # Ces totaux ne portent QUE sur les sites dont le chiffre est annoncé :
        # les additionner comme s'ils couvraient tout le panel serait faux.
        "sites_avec_capacite": n_mw,
        "sites_avec_investissement": n_inv,
    }


def assemble():
    sites = _enrichir()
    return {
        "version": VERSION,
        "n_sites": len(sites),
        "sites": sites,
        "statuts": STATUTS,
        "agregats": _agreger(sites),
        "derivation": {
            "charge": list(CHARGE),
            "pue": {k: list(v) for k, v in PUE.items()},
            "wue": {k: list(v) for k, v in WUE.items()},
            "avertissement": AVERTISSEMENT,
        },
        "cadre": CADRE,
        "limites": LIMITES,
        "retires": RETIRES,
        "maj": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def sante():
    return {"version": VERSION, "n_sites": len(SITES),
            "n_retires": len(RETIRES),
            "statuts": sorted(STATUTS)}
