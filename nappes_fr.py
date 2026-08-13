# -*- coding: utf-8 -*-
"""L'ÉTAT DES NAPPES FRANÇAISES, ET CE QU'IL DIT DU FONCIER DATA CENTER.

POURQUOI CE MODULE EXISTE. Le comparateur d'implantation note l'eau au niveau
NATIONAL, par l'indice WEI+ de l'Agence européenne pour l'environnement. Le
module le dit lui-même depuis le premier jour : « la lecture nationale ÉCRASE
les contrastes ». La France y est classée en stress MODÉRÉ — et cette classe
recouvre à la fois des bassins excédentaires et des bassins en crise. Un
investisseur qui s'arrêterait à la note nationale conclurait que l'eau n'est pas
le sujet en France. La carte des nappes dit l'inverse, région par région.

CE QU'IL AJOUTE, ET CE QU'IL N'AJOUTE PAS. Il ajoute le CONTRASTE DE BASSINS
pour un seul pays, à une seule date. Il n'ajoute aucune mesure : c'est la lecture
d'une carte publiée, avec ses classes telles qu'elles y figurent, et rien n'y est
converti en chiffre. Aucune note n'en sort — le comparateur garde sa note
nationale, et ce module se lit À CÔTÉ. En faire une note reviendrait à mélanger
deux échelles : un indice annuel d'exploitation de la ressource et un état
piézométrique instantané ne mesurent pas la même chose.

LE PIÈGE DE LA DATE, ET IL EST GROS. Un relevé au 1er août est pris au CREUX de
l'année hydrologique : les nappes se rechargent l'hiver et se vident l'été. Des
niveaux bas au 1er août ne sont donc pas, en eux-mêmes, une anomalie. Ce qui
l'est : la TENDANCE — presque tous les points de suivi en baisse — et le fait
que la recharge de l'hiver précédent n'a pas suffi à effacer le déficit. Le
module sert donc les deux, jamais le niveau seul, et refuse de conclure d'un
niveau sans sa tendance.

CE QUI RENDRAIT CE MODULE FAUX. Une seconde date. Un état de nappes se périme en
un mois : la famille « nappes » est déclarée au registre de péremption avec une
cadence trimestrielle, et la page affiche son âge. Un état piézométrique servi
sans sa date est pire qu'aucun état.
"""
from __future__ import annotations

VERSION = "2026-08-a"

# ═══════════════════════════════════════════════════════════════════════════
#  LA SOURCE, ET SES DEUX AVERTISSEMENTS
# ═══════════════════════════════════════════════════════════════════════════

SOURCE = {
    "titre": "Situation des nappes phréatiques au 1er août 2026",
    "editeur": "BRGM — Bureau de recherches géologiques et minières",
    "reprise": "carte publiée par Les Echos d’après les données BRGM",
    "nature": "referentiel",
    "note": "Lecture de la carte publiée : les classes servies ici sont CELLES DE "
            "SA LÉGENDE, sans conversion ni interpolation. Aucune valeur "
            "piézométrique n’en est tirée — la carte n’en porte pas.",
}

SAISONNALITE = {
    "titre": "Un relevé d’août se lit avec sa saison, ou il ment",
    "texte": "Le 1er août est le CREUX de l’année hydrologique : les nappes se "
             "rechargent l’hiver et se vident l’été. Des niveaux bas à cette date "
             "ne sont donc pas une anomalie en soi. Ce qui en est une : la "
             "TENDANCE, presque uniformément à la baisse, et le fait que la "
             "recharge hivernale n’ait pas effacé le déficit antérieur.",
    "consequence": "Ce module refuse de servir un niveau sans sa tendance. Un "
                   "« niveau bas et stable » et un « niveau bas et en baisse » "
                   "n’engagent pas la même décision d’implantation.",
}

# Les sept classes de la légende, plus le gris. L'ordre est celui de la légende,
# du plus haut au plus bas — il porte le rang, qui sert à comparer.
NIVEAUX = {
    "tres_haut":    {"nom": "Niveau très haut", "rang": 7},
    "haut":         {"nom": "Niveau haut", "rang": 6},
    "moderement_haut": {"nom": "Niveau modérément haut", "rang": 5},
    "moyenne":      {"nom": "Niveau autour de la moyenne", "rang": 4},
    "moderement_bas": {"nom": "Niveau modérément bas", "rang": 3},
    "bas":          {"nom": "Niveau bas", "rang": 2},
    "tres_bas":     {"nom": "Niveau très bas", "rang": 1},
    # LE GRIS N'EST PAS UN BON RÉSULTAT, et c'est la même règle que sur la carte
    # d'Europe du comparateur : sur une carte colorée, le gris se lit
    # spontanément comme « rien à signaler ». Ici il veut dire qu'on ne sait pas.
    "sans_suivi":   {"nom": "Sans nappe libre étendue, ou absence de points de suivi",
                     "rang": None,
                     "note": "Ce n’est PAS un bon résultat : c’est une absence de "
                             "donnée. Un projet qui s’y installerait devrait "
                             "produire sa propre étude piézométrique — et il ne "
                             "pourrait s’appuyer sur aucun historique public."},
}

TENDANCES = {
    "hausse": {"nom": "En hausse", "signe": "↑"},
    "stable": {"nom": "Stable", "signe": "="},
    "baisse": {"nom": "En baisse", "signe": "↓"},
}


# ═══════════════════════════════════════════════════════════════════════════
#  LA LECTURE, RÉGION PAR RÉGION
#
#  POURQUOI LES RÉGIONS ADMINISTRATIVES ET NON LES BASSINS. Parce que c'est
#  l'échelle à laquelle le foncier se décide : les zones identifiées par l'État
#  pour l'implantation de centres de données bas carbone sont annoncées par
#  RÉGION. Croiser deux référentiels exige une maille commune, et une lecture par
#  bassin qu'on ne pourrait rapprocher d'aucune décision publique n'instruirait
#  rien. Le prix de ce choix est écrit : une région n'est pas homogène, et la
#  décision de site exige l'étude du bassin versant.
#
#  `foncier_dc` reprend les régions où l'État a identifié du foncier prêt pour
#  des centres de données destinés à l'IA. C'est ce croisement qui fait l'intérêt
#  du module : il met face à face une intention publique et un état de ressource.
# ═══════════════════════════════════════════════════════════════════════════

REGIONS = {
    "grand_est": {
        "nom": "Grand Est", "niveau": "tres_bas", "tendance": "baisse",
        "foncier_dc": True,
        "lecture": "L’un des deux ensembles les plus bas de la carte, avec des "
                   "points de suivi en baisse et un point stable vers le Rhin.",
    },
    "bourgogne_franche_comte": {
        "nom": "Bourgogne-Franche-Comté", "niveau": "tres_bas", "tendance": "baisse",
        "foncier_dc": True,
        "lecture": "Second ensemble en niveau très bas, entre Dijon et le Jura, "
                   "tous points de suivi en baisse.",
    },
    "auvergne_rhone_alpes": {
        "nom": "Auvergne-Rhône-Alpes", "niveau": "tres_bas", "tendance": "baisse",
        "foncier_dc": True,
        "lecture": "Le cœur du Massif Central, autour de Clermont-Ferrand, est en "
                   "niveau très bas. L’est de la région est plus contrasté, avec "
                   "des points stables vers Lyon et la vallée du Rhône.",
    },
    "ile_de_france": {
        "nom": "Île-de-France", "niveau": "moderement_haut", "tendance": "baisse",
        "foncier_dc": True,
        "lecture": "LA SEULE ZONE ÉTENDUE EN NIVEAU MODÉRÉMENT HAUT de la carte — "
                   "les nappes du bassin parisien. C’est aussi la région qui "
                   "concentre le plus de foncier identifié. Les points de suivi y "
                   "sont pourtant en baisse : le niveau est confortable, la "
                   "trajectoire ne l’est pas.",
    },
    "hauts_de_france": {
        "nom": "Hauts-de-France", "niveau": "moderement_bas", "tendance": "baisse",
        "foncier_dc": True,
        "lecture": "Niveaux modérément bas à bas vers l’est de la région, points "
                   "de suivi en baisse.",
    },
    "normandie": {
        "nom": "Normandie", "niveau": "moderement_bas", "tendance": "baisse",
        "foncier_dc": True,
        "lecture": "Ensemble modérément bas, tous points en baisse.",
    },
    "centre_val_de_loire": {
        "nom": "Centre-Val de Loire", "niveau": "moderement_bas", "tendance": "baisse",
        "foncier_dc": True,
        "lecture": "Modérément bas, en continuité du bassin parisien mais sans "
                   "son niveau : la bordure de la nappe de Beauce se lit ici.",
    },
    "nouvelle_aquitaine": {
        "nom": "Nouvelle-Aquitaine", "niveau": "bas", "tendance": "baisse",
        "foncier_dc": True,
        "lecture": "Niveaux bas dominants, quelques points stables vers Bordeaux "
                   "et le sud-ouest.",
    },
    "provence_alpes_cote_azur": {
        "nom": "Provence-Alpes-Côte d’Azur", "niveau": "moderement_bas",
        "tendance": "baisse", "foncier_dc": True,
        "lecture": "Contrasté : niveaux modérément bas, un point stable et LE SEUL "
                   "point en hausse nettement lisible de la carte, sur le littoral. "
                   "Une exception locale, pas une tendance régionale.",
    },
    "bretagne": {
        "nom": "Bretagne", "niveau": "sans_suivi", "tendance": "baisse",
        "foncier_dc": False,
        "lecture": "Largement en gris : peu de nappes libres étendues, socle "
                   "cristallin. L’absence de suivi n’y est pas une bonne nouvelle "
                   "— elle signifie qu’un projet y arriverait sans historique.",
    },
    "pays_de_la_loire": {
        "nom": "Pays de la Loire", "niveau": "moderement_bas", "tendance": "baisse",
        "foncier_dc": False,
        "lecture": "Modérément bas, points de suivi en baisse.",
    },
    "occitanie": {
        "nom": "Occitanie", "niveau": "bas", "tendance": "baisse",
        "foncier_dc": False,
        "lecture": "Niveaux bas, quelques points stables ; le littoral "
                   "méditerranéen est le plus tendu.",
    },
    "corse": {
        "nom": "Corse", "niveau": "sans_suivi", "tendance": "baisse",
        "foncier_dc": False,
        "lecture": "Sans nappe libre étendue au sens de la carte : aucun état "
                   "n’en est lisible.",
    },
}

# Provenance du croisement : ce que l'État a identifié, et où.
SOURCE_FONCIER = {
    "titre": "Zones identifiées pour l’implantation de centres de données bas "
             "carbone destinés à l’IA",
    "editeur": "annonce publique de l’État français, février 2025",
    "nature": "analyse",
    "note": "Reprise au niveau RÉGIONAL, seule maille commune avec la carte des "
            "nappes. Les surfaces et les dates de disponibilité du foncier ne "
            "sont pas reprises ici : elles relèvent du dossier de site, pas de "
            "la ressource en eau.",
}


# ═══════════════════════════════════════════════════════════════════════════
#  CALCUL
# ═══════════════════════════════════════════════════════════════════════════

def region(cle):
    r = REGIONS.get(cle)
    if not r:
        return None
    n = NIVEAUX[r["niveau"]]
    t = TENDANCES[r["tendance"]]
    return dict(r, cle=cle, niveau_nom=n["nom"], niveau_rang=n["rang"],
                niveau_note=n.get("note"), tendance_nom=t["nom"],
                tendance_signe=t["signe"])


def regions():
    """Toutes les régions, des nappes les plus basses aux plus hautes.

    Le gris arrive EN TÊTE et non en queue : une absence de donnée mérite d'être
    vue avant les valeurs, pas reléguée là où on ne lit plus. Trier sur un rang
    absent l'aurait mise au fond par accident.
    """
    out = [region(k) for k in REGIONS]
    return sorted(out, key=lambda r: (r["niveau_rang"] is not None,
                                      r["niveau_rang"] if r["niveau_rang"] else 0,
                                      r["nom"]))


def croiser():
    """LE CROISEMENT QUI JUSTIFIE LE MODULE : le foncier annoncé, et l'eau dessous.

    Une intention publique d'implantation face à un état de ressource. Ni l'une
    ni l'autre ne se lit seule : le foncier ne dit rien de l'eau, et la carte des
    nappes ne dit rien des projets.
    """
    avec = [r for r in regions() if r["foncier_dc"]]
    # « Tendues » : niveau bas ou très bas. Le seuil est écrit ici plutôt que
    # laissé au lecteur — et il est délibérément strict, pour que le signal ne
    # se dilue pas dans le « modérément bas », qui est presque partout.
    tendues = [r for r in avec if r["niveau_rang"] is not None and r["niveau_rang"] <= 2]
    baisse = [r for r in avec if r["tendance"] == "baisse"]
    grises = [r for r in avec if r["niveau_rang"] is None]
    return {
        "n_regions_foncier": len(avec),
        "regions_foncier": [r["cle"] for r in avec],
        "tendues": [r["cle"] for r in tendues],
        "n_tendues": len(tendues),
        "en_baisse": [r["cle"] for r in baisse],
        "n_en_baisse": len(baisse),
        "sans_suivi": [r["cle"] for r in grises],
        "seuil_tendue": "niveau bas ou très bas",
        "lecture": (
            "Sur les %d régions où l’État a identifié du foncier pour des centres "
            "de données, %d portent des nappes en niveau bas ou très bas au "
            "1er août, et %d voient leurs points de suivi EN BAISSE. La tendance "
            "est le fait marquant : elle est quasi générale, y compris là où le "
            "niveau reste confortable."
            % (len(avec), len(tendues), len(baisse))),
    }


def assemble():
    return {
        "version": VERSION,
        "source": dict(SOURCE),
        "source_foncier": dict(SOURCE_FONCIER),
        "saisonnalite": dict(SAISONNALITE),
        "niveaux": {k: dict(v) for k, v in NIVEAUX.items()},
        "tendances": {k: dict(v) for k, v in TENDANCES.items()},
        "regions": regions(),
        "croisement": croiser(),
        "limites": [
            "UNE SEULE DATE. Un état piézométrique n’est pas une trajectoire : "
            "cette carte dit le 1er août 2026, rien d’autre. Elle se périme en "
            "quelques semaines, et son âge est affiché.",
            "UNE MAILLE RÉGIONALE POUR UN PHÉNOMÈNE DE BASSIN. Une région n’est "
            "pas homogène ; le choix de la maille vient de ce que le foncier se "
            "décide par région. Toute décision de site exige l’étude du bassin "
            "versant et du plan sécheresse locaux.",
            "AUCUNE NOTE N’EN SORT. Le comparateur d’implantation garde sa note "
            "nationale WEI+ : un indice annuel d’exploitation de la ressource et "
            "un état piézométrique instantané ne mesurent pas la même chose, et "
            "les additionner produirait un chiffre qui ne veut rien dire.",
            "LE GRIS EST UNE ABSENCE DE DONNÉE, pas un feu vert. Un projet en "
            "zone grise devrait produire sa propre étude piézométrique, sans "
            "pouvoir s’appuyer sur un historique public.",
            "LA FRANCE SEULE. Aucun équivalent n’est servi pour les autres pays "
            "du comparateur : la carte des nappes est un référentiel national. "
            "L’absence de contraste ailleurs est un trou de notre référentiel, "
            "pas une homogénéité de leurs bassins.",
        ],
    }


def sante():
    c = croiser()
    return {
        "version": VERSION,
        "regions": len(REGIONS),
        "regions_foncier_dc": c["n_regions_foncier"],
        "regions_tendues": c["n_tendues"],
        "regions_sans_suivi": len(c["sans_suivi"]),
        "niveaux": len(NIVEAUX),
        "millesime": "2026-08-01",
    }


def _verifier():
    """Ce qui doit être vrai pour que ce module ne mente pas.

    Une classe de niveau inconnue, une tendance inconnue, ou un rang en double
    rendraient le tri arbitraire sans qu’aucun appel n’échoue — le tableau
    s’afficherait, dans le mauvais ordre, et personne ne le verrait.
    """
    rangs = [v["rang"] for v in NIVEAUX.values() if v["rang"] is not None]
    if len(set(rangs)) != len(rangs):
        raise RuntimeError("nappes : deux classes de niveau partagent un rang")
    for cle, r in REGIONS.items():
        if r["niveau"] not in NIVEAUX:
            raise RuntimeError("nappes : niveau inconnu pour %s — %s" % (cle, r["niveau"]))
        if r["tendance"] not in TENDANCES:
            raise RuntimeError("nappes : tendance inconnue pour %s — %s"
                               % (cle, r["tendance"]))
        for champ in ("nom", "lecture"):
            if not str(r.get(champ, "")).strip():
                raise RuntimeError("nappes : %s sans « %s »" % (cle, champ))
    if NIVEAUX["sans_suivi"]["rang"] is not None:
        raise RuntimeError("nappes : le gris ne doit porter AUCUN rang — lui en "
                           "donner un le ferait comparer à des niveaux mesurés")
    if not any(r["foncier_dc"] for r in REGIONS.values()):
        raise RuntimeError("nappes : aucune région ne porte de foncier identifié — "
                           "le croisement qui justifie ce module serait vide")


_verifier()
