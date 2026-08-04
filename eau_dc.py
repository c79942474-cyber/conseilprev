# -*- coding: utf-8 -*-
"""L’eau de la SOURCE : ce que le WUE de site ne dit pas.

POURQUOI CE MODULE EXISTE

La page publiait, pour les 97 centres cartographiés, l’eau consommée SUR LE
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
        "surface et puissance installée",
        "taux d’utilisation",
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


def equivalence_par_mode(code=None):
    """Là où l’arbitrage se tranche vraiment : mode par mode, en L/kWh_IT.

    Ramenées au kilowattheure informatique, les deux eaux se comparent
    directement : le site vaut son WUE, l’amont vaut EWIF × PUE. Le rapport des
    deux ne dépend plus ni de la taille du parc ni du facteur de charge — il ne
    dépend que de la CONCEPTION et du MIX, c’est-à-dire des deux seules choses
    sur lesquelles on décide.
    """
    try:
        import datacentres
        pue_t, wue_t = datacentres.PUE, datacentres.WUE
    except Exception:
        return []
    e = ewif_pays(code)
    out = []
    for mode in sorted(set(pue_t) & set(wue_t)):
        pue, wue = pue_t[mode], wue_t[mode]
        amont = [round(e["valeur"] * pue[0], 2), round(e["valeur"] * pue[1], 2)]
        # Amont ÷ site : borne basse = amont bas ÷ site haut, et réciproquement.
        bas = round(amont[0] / wue[1], 1) if wue[1] else None
        haut = round(amont[1] / wue[0], 1) if wue[0] else None
        out.append({
            "mode": mode,
            "nom": (PART_EVAPORATIVE.get(mode) or {}).get("nom") or mode,
            "wue_site": list(wue), "pue": list(pue),
            "amont_l_kwh_it": amont,
            "rapport": {"min": bas, "max": haut, "max_indefini": wue[0] == 0},
            # Le seul verdict qui se tienne sans hypothèse supplémentaire :
            # l’amont l’emporte-t-il même dans l’hypothèse la plus défavorable ?
            "amont_domine_toujours": bool(wue[1] and amont[0] > wue[1]),
            "amont_domine_parfois": bool(wue[0] == 0 or amont[1] > wue[0]),
        })
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
        detail.append({
            "id": s.get("id"), "pays": code, "operateur": s.get("operateur"),
            "ville": s.get("ville"), "refroidissement": mode,
            "part_evaporative": (PART_EVAPORATIVE.get(mode) or {}).get("part"),
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
        "couverture": {
            "pays_parc": len(par_pays),
            "pays_ewif_national": sum(1 for p in par_pays.values() if p["ewif_national"]),
            "pays_defaut_ue": sorted(sans_ewif),
            "sites_sans_estimation_eau": sans_eau,
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
        "indicateurs_eed": len(CADRE_EED["exige"]),
        "nature_ewif": EWIF_NATURE,
        "incertitude_ewif": EWIF_INCERTITUDE,
        "provenance": PROVENANCE["module"],
    }
