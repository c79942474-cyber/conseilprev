# -*- coding: utf-8 -*-
"""Couche régionale Île-de-France de la carte des centres de données.

POURQUOI UN MODULE À PART, ET PAS DES LIGNES DE PLUS DANS `datacentres.py`.

Le référentiel européen porte quatre-vingt-dix-sept sites pour tout le
continent, dont cinq en Île-de-France. L'Observatoire de l'Institut Paris
Région en recense cent trente-neuf pour la seule région. Verser les seconds
dans le premier ferait paraître la France vingt fois plus dense que
l'Allemagne — non parce qu'elle l'est, mais parce qu'une agence régionale
française a fait un travail que personne n'a fait pour la Hesse.

C'est très exactement le biais que le référentiel européen s'interdit, et
qu'il documente lui-même :

    « Un dénombrement brut de lignes n'est donc pas un dénombrement de
      centres de données. »
    « L'Irlande et les Pays-Bas sont sur-représentés parce que la
      contestation locale y a produit de la documentation. »

Trois choses casseraient à la fusion : les agrégats de `_agreger()`, le
comparateur de pays, et le tableau Pro/Contra qui en dérive. Ce module ne
touche donc à rien de tout cela — il ne modifie pas `datacentres.SITES`, il
ne s'y ajoute pas, et une recette vérifie qu'aucun agrégat européen ne bouge
d'une unité.

CE QUE LA COUCHE MONTRE, ET QUAND.

Deux jeux de granularité différente ne se mélangent pas : ils s'affichent à
des échelles différentes. C'est le zoom qui les sépare, et non un réglage.

    palier 0-1  un seul marqueur agrégé, qui dit le compte ET sa provenance
    palier 2    les pôles, dérivés des sites réellement chargés
    palier 3    les sites un à un

CE QU'IL MANQUE, ET QUI EST DIT PLUTÔT QUE COMBLÉ.

`SITES_OBS` est vide. L'export de l'Observatoire n'a pas pu être récupéré —
le domaine est refusé par la passerelle réseau de l'environnement de
développement — et sa licence de réutilisation n'a pas été instruite.
Republier n'est pas consulter : cela se tranche avant, pas après.

La couche fonctionne donc aujourd'hui sur les cinq sites franciliens déjà
attestés au référentiel européen, et elle ANNONCE ce qui lui manque. Le jour
où l'export arrive, il se pose dans `SITES_OBS` et rien d'autre ne change.
"""
from datetime import datetime, timezone

import datacentres

VERSION = "2026-08-a"

# ── LE PÉRIMÈTRE, GÉOGRAPHIQUE ET NON DÉCLARATIF ────────────────────────────
# On ne demande pas au référentiel européen s'il pense qu'un site est
# francilien : il ne porte pas de département. On le teste sur ses
# coordonnées, qui sont la seule donnée qu'il garantit. La boîte est large de
# quelques dixièmes de degré au-delà des limites administratives : un
# centroïde de commune tombe parfois à côté de sa frontière, et exclure un
# site pour deux kilomètres serait une fausse rigueur.
BOITE = {"lat_min": 48.10, "lat_max": 49.25, "lon_min": 1.40, "lon_max": 3.60}

REGION = {
    "code": "IDF",
    "nom": "Île-de-France",
    "pays": "FR",
    # Le point d'ancrage du marqueur agrégé. Choisi au centre de gravité du
    # parc francilien — au nord de Paris, où se concentrent Plaine Commune et
    # la Seine-Saint-Denis — et non au centre géométrique de la région, qui
    # tomberait dans une zone sans aucun site.
    "lat": 48.90,
    "lon": 2.36,
}

# ── LA SOURCE ATTENDUE ───────────────────────────────────────────────────────
# Décrite AVANT d'être chargée, avec ce qu'elle annonce publiquement. Les deux
# comptes sont notés séparément parce qu'ils ne désignent pas la même chose et
# que les confondre est l'erreur la plus facile : cent trente-neuf SITES
# portent deux cent treize CENTRES.
OBSERVATOIRE = {
    "nom": "Observatoire des data centers en Île-de-France",
    "editeur": "Institut Paris Région",
    "url": "https://www.institutparisregion.fr/amenagement-et-territoires/"
           "observatoire-des-data-centers-en-ile-de-france/",
    "partenaires": ["DRIEAT", "RTE", "Enedis", "ADEME", "Choose Paris Region"],
    "depuis": 2017,
    # Chiffres ANNONCÉS par l'éditeur, non vérifiés dans le jeu lui-même.
    "annonce_sites": 139,
    "annonce_centres": 213,
    "annonce_detail": {"service": 159, "construction": 21, "programme": 8,
                       "instruction": 19, "etude": 14},
    "charge": False,
    "licence": None,
    "extrait_le": None,
    "pourquoi_absent": (
        "Export non récupéré : le domaine de l'éditeur et sa plateforme de "
        "données ouvertes sont refusés par la passerelle réseau de "
        "l'environnement de développement. La licence de réutilisation n'a pas "
        "davantage pu être instruite — republier un jeu de données n'est pas "
        "le consulter, et cela se tranche avant l'intégration."),
}

# ── LES SITES DE L'OBSERVATOIRE ──────────────────────────────────────────────
# Vide, et volontairement. Chaque entrée devra porter le même vocabulaire de
# champs que le référentiel européen — operateur, ville, lat, lon, statut,
# confiance, source_type, source_libelle — plus `echelle` ("site" ou
# "batiment"), que le référentiel européen ne distingue pas et qu'il ne faut
# pas écraser en les mélangeant.
SITES_OBS = []

CADRE = {
    "objet": ("Densité et implantation des centres de données en "
              "Île-de-France, à une granularité que le référentiel européen "
              "ne porte pas."),
    "ce_que_c_est": (
        "Une couche RÉGIONALE, distincte du référentiel européen et affichée "
        "à d'autres échelles. Elle ne participe à aucun agrégat européen, ne "
        "modifie aucun comptage par pays, et n'entre dans aucune comparaison "
        "entre États."),
    "ce_que_ce_n_est_pas": (
        "Ni une extension du référentiel européen, ni une source de capacité "
        "ou de consommation. Aucun mégawatt, aucun mètre cube n'en dérive."),
    "niveau_de_preuve": (
        "Deux niveaux coexistent sur la carte et sont distingués par la "
        "légende : le référentiel européen atteste site par site, coordonnées "
        "comprises ; la couche régionale reprend un recensement d'agence "
        "d'urbanisme, dont la maille et la méthode sont celles de son "
        "éditeur."),
}

LIMITES = [
    "Deux comptes circulent et ne désignent pas la même chose : cent "
    "trente-neuf SITES portent deux cent treize CENTRES. Un site peut "
    "réunir plusieurs centres d'un même exploitant. Toute phrase qui les "
    "confond fait varier le parc francilien de cinquante pour cent.",

    "La couche ne dit rien de la PUISSANCE. Le référentiel européen a établi "
    "qu'aucune capacité attestée ne survit à la réfutation ; rien n'indique "
    "que le recensement régional soit mieux loti, et aucun mégawatt n'est "
    "dérivé ici.",

    "Le périmètre francilien est testé sur les COORDONNÉES et non sur un "
    "code de département, que le référentiel européen ne porte pas. Un "
    "centroïde de commune posé de travers peut donc classer un site du "
    "mauvais côté d'une limite administrative.",

    "Les pôles sont DÉRIVÉS des sites chargés, par regroupement "
    "géographique, et non déclarés. Ils n'ont donc aucune existence "
    "administrative : ce sont des amas de points, nommés d'après la commune "
    "la plus représentée. Leur composition change dès qu'un site s'ajoute.",

    "Tant que l'export de l'Observatoire n'est pas chargé, la couche affiche "
    "les seuls sites franciliens du référentiel européen — cinq — tout en "
    "annonçant les cent trente-neuf recensés. L'écart est affiché, jamais "
    "comblé par estimation.",

    "Si l'Île-de-France est traitée et pas Francfort, Amsterdam, Dublin ou "
    "Madrid, la carte donne à voir une densité française sans équivalent "
    "ailleurs — qui est un artefact de documentation, pas un fait. Le "
    "marqueur agrégé et la légende sont là pour le dire ; ils ne suppriment "
    "pas le biais, ils le nomment.",
]


def _dans_boite(s):
    """Le site tombe-t-il dans la fenêtre francilienne ?"""
    la, lo = s.get("lat"), s.get("lon")
    if not isinstance(la, (int, float)) or not isinstance(lo, (int, float)):
        return False
    return (BOITE["lat_min"] <= la <= BOITE["lat_max"]
            and BOITE["lon_min"] <= lo <= BOITE["lon_max"])


def herites(sites_europe=None):
    """Les sites franciliens DÉJÀ portés par le référentiel européen.

    Ils restent dessinés par lui — la couche régionale ne les redessine pas,
    sans quoi chaque point apparaîtrait deux fois. Elle les compte, pour dire
    ce qui est déjà là et ce qui manque.
    """
    src = sites_europe if sites_europe is not None else datacentres.SITES
    return [s for s in src if s.get("pays") == "FR" and _dans_boite(s)]


def _cle_amas(s, pas=0.09):
    """La case de la grille où tombe un site. Un dixième de degré ≈ 7 km en
    latitude : assez fin pour séparer Plaine Commune de Marcoussis, assez
    large pour ne pas éclater un campus en trois amas."""
    return (round(s["lat"] / pas), round(s["lon"] / pas))


def poles(sites):
    """Les pôles, DÉRIVÉS des sites fournis — jamais déclarés.

    Nommés d'après la commune la plus représentée de l'amas, ce qui est
    vérifiable, plutôt que d'après une appellation de territoire qui
    supposerait un découpage administratif que ces points n'ont pas.
    """
    amas = {}
    for s in sites:
        if not _dans_boite(s):
            continue
        amas.setdefault(_cle_amas(s), []).append(s)
    out = []
    for cle, membres in amas.items():
        villes = {}
        for m in membres:
            v = (m.get("ville") or "").strip()
            if v:
                villes[v] = villes.get(v, 0) + 1
        nom = max(villes, key=villes.get) if villes else "Île-de-France"
        if len(villes) > 1:
            nom += " et alentours"
        out.append({
            "id": "idf-pole-%d-%d" % cle,
            "nom": nom,
            "n": len(membres),
            "lat": round(sum(m["lat"] for m in membres) / len(membres), 4),
            "lon": round(sum(m["lon"] for m in membres) / len(membres), 4),
            "sites": [m.get("id") for m in membres if m.get("id")],
        })
    return sorted(out, key=lambda p: (-p["n"], p["nom"]))


def assemble(sites_europe=None):
    """La couche régionale, prête à l'affichage.

    `sites_europe` accepte les sites ENRICHIS du référentiel (ceux qui portent
    déjà un `id`), de sorte que les pôles puissent les désigner. Sans
    argument, on retombe sur les sites bruts — utile aux contrôles.
    """
    her = herites(sites_europe)
    tous = her + list(SITES_OBS)
    manque = None
    if not OBSERVATOIRE["charge"]:
        manque = max(0, OBSERVATOIRE["annonce_sites"] - len(tous))
    return {
        "version": VERSION,
        "region": REGION,
        # Ce qui est RÉELLEMENT sur la carte, et ce qui est annoncé ailleurs.
        # Les deux nombres sont servis séparément : les additionner ou les
        # confondre est l'erreur que ce module existe pour empêcher.
        "n_affiches": len(tous),
        "n_herites": len(her),
        "n_observatoire": len(SITES_OBS),
        "n_annonces": OBSERVATOIRE["annonce_sites"],
        "n_manquants": manque,
        # Seuls les sites de l'Observatoire sont à DESSINER par cette couche :
        # les hérités sont déjà tracés par le référentiel européen.
        "sites": list(SITES_OBS),
        "poles": poles(tous),
        "observatoire": OBSERVATOIRE,
        "cadre": CADRE,
        "limites": LIMITES,
        "maj": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def sante():
    her = herites()
    return {"version": VERSION, "region": REGION["code"],
            "n_herites": len(her), "n_observatoire": len(SITES_OBS),
            "observatoire_charge": OBSERVATOIRE["charge"],
            "n_annonces": OBSERVATOIRE["annonce_sites"]}
