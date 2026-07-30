# -*- coding: utf-8 -*-
"""Socle de données ouvertes — Copernicus, NASA, DINUM, Eurostat.

POURQUOI CE MODULE
Les deux cartes de Sentinel reposent sur un panel documenté : c'est un travail
de recensement, et le lecteur doit nous croire sur parole. Les données ouvertes
publiques changent cela. Elles sont interrogeables par n'importe qui, sous
licence explicite, avec une date : ce sont les SEULES couches du site que le
lecteur peut refaire lui-même. C'est ce qui les rend précieuses, et c'est la
raison pour laquelle chaque mesure est publiée ici avec son point d'accès, sa
licence et sa date de relevé.

CE QUE CE MODULE NE FAIT PAS
Il ne déduit pas l'activité en IA depuis l'imagerie satellitaire. Les radiances
nocturnes, les colonnes de NO₂ ou la densité de produits Sentinel décrivent le
SOL, pas les systèmes d'IA. Les mesures servent de contexte documenté et de
matière première aux cas d'usage recensés — jamais de preuve indirecte.

ARCHITECTURE
Aucun import Flask : le module s'utilise en bibliothèque, se teste seul et ne
connaît rien du serveur. Trois sources interrogées EN PARALLÈLE sous budget de
temps, chacune avec son cache et son repli daté. Aucune clé d'API n'est requise
— une source qui exige une inscription n'est pas ouverte pour le lecteur.
"""
import concurrent.futures as _futures
import json
import os
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

VERSION = "2026-07-a"

_UA = ("Mozilla/5.0 (compatible; SentinelConseilprev/1.0; "
       "+https://conseilprev.onrender.com/panorama)")

# ═══════════════════════════════════════════════════════════════════════════
# 1. RÉFÉRENTIEL DES SOURCES
#    Ce qui est CERTAIN : l'organisme, le point d'accès, la licence, la
#    résolution, la cadence. Rien ici n'est calculé ni interprété.
# ═══════════════════════════════════════════════════════════════════════════

SOURCES = {
    "copernicus": {
        "nom": "Copernicus — programme d'observation de la Terre de l'Union",
        "organisme": "Commission européenne · ESA · EUMETSAT · ECMWF",
        "portail": "https://dataspace.copernicus.eu/",
        "point_acces": "https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
        "licence": "Données Sentinel libres, entières et ouvertes — règlement délégué (UE) 1159/2013",
        "cle_api": False,
        "resolution": "10 m (Sentinel-2), 5 m × 20 m (Sentinel-1), 300 m (Sentinel-3), 3,5 km × 7 km (Sentinel-5P)",
        "cadence": "révisite de 2 à 5 jours en Europe selon la constellation",
        "montre": "la production de produits d'observation mis à disposition sur une fenêtre de temps",
        "ne_montre_pas": "ni la qualité des images (couverture nuageuse), ni ce qui en est fait, "
                         "ni la moindre activité en intelligence artificielle",
    },
    "nasa": {
        "nom": "NASA EONET — suivi ouvert des événements naturels",
        "organisme": "NASA · Earth Science Data Systems",
        "portail": "https://eonet.gsfc.nasa.gov/",
        "point_acces": "https://eonet.gsfc.nasa.gov/api/v3/events",
        "licence": "Domaine public — politique de données ouvertes de la NASA",
        "cle_api": False,
        "resolution": "événement géolocalisé, pas de maillage",
        "cadence": "continue, événements ouverts et clos",
        "montre": "les événements naturels notables en cours, catégorisés et géolocalisés",
        "ne_montre_pas": "un registre exhaustif des aléas : EONET retient les événements "
                         "NOTABLES, la sélection est éditoriale",
    },
    "dinum": {
        "nom": "data.gouv.fr — plateforme française des données publiques",
        "organisme": "DINUM · Etalab",
        "portail": "https://www.data.gouv.fr/",
        "point_acces": "https://www.data.gouv.fr/api/1/datasets/",
        "licence": "Licence Ouverte 2.0 (Etalab) ou ODbL selon le jeu — reportée par jeu",
        "cle_api": False,
        "resolution": "jeu de données, granularité propre à chaque producteur",
        "cadence": "publication continue par les administrations",
        "montre": "ce que l'administration française publie effectivement en ouvert sur un thème",
        "ne_montre_pas": "un recensement des données publiques : une recherche par mots-clés "
                         "sur un catalogue rate ce qui est nommé autrement",
    },
    "eurostat": {
        "nom": "Eurostat — statistiques européennes",
        "organisme": "Commission européenne",
        "portail": "https://ec.europa.eu/eurostat/",
        "point_acces": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/",
        "licence": "Réutilisation libre avec mention de la source — décision 2011/833/UE",
        "cle_api": False,
        "resolution": "État membre, parfois région NUTS 2",
        "cadence": "annuelle pour l'enquête sur l'usage des TIC et de l'IA",
        "montre": "la part d'entreprises déclarant utiliser des technologies d'IA",
        "ne_montre_pas": "les systèmes eux-mêmes : c'est une enquête déclarative, "
                         "déjà exploitée par l'Observatoire R&D du site",
    },
}

# Constellations interrogées côté Copernicus. Ordre = ordre d'affichage.
_COLLECTIONS = ["SENTINEL-2", "SENTINEL-1", "SENTINEL-3", "SENTINEL-5P"]

# Requêtes data.gouv.fr. Deux thèmes : l'IA elle-même, et la donnée spatiale
# qui l'alimente. Séparées pour que le lecteur voie les deux volumes.
_REQUETES_DINUM = [
    {"cle": "ia", "q": "intelligence artificielle",
     "libelle": "Jeux de données publics français référencés « intelligence artificielle »"},
    {"cle": "spatial", "q": "satellite Copernicus Sentinel télédétection",
     "libelle": "Jeux de données publics français d'observation de la Terre"},
]

# ═══════════════════════════════════════════════════════════════════════════
# 2. REPLI DATÉ
#    Relevé manuel, horodaté, servi quand une source ne répond pas. Il est
#    TOUJOURS annoncé comme tel : une valeur de repli présentée comme fraîche
#    serait un mensonge, et c'est exactement ce qu'on refuse ici.
# ═══════════════════════════════════════════════════════════════════════════

SEED = {
    "copernicus": {
        "releve": "2026-07",
        "note": "Ordres de grandeur relevés sur le catalogue Copernicus Data Space. "
                "Le nombre exact varie chaque jour avec les acquisitions et les "
                "retraitements ; seul l'ordre de grandeur est stable.",
        "produits_24h": {"SENTINEL-2": 4200, "SENTINEL-1": 1500,
                         "SENTINEL-3": 2100, "SENTINEL-5P": 320},
    },
    "nasa": {
        "releve": "2026-07",
        "note": "Nombre d'événements ouverts au moment du relevé. EONET suit les "
                "événements notables : le total varie fortement selon la saison.",
        "evenements_ouverts": 118,
        "par_categorie": [["Wildfires", 71], ["Severe Storms", 18],
                          ["Volcanoes", 15], ["Sea and Lake Ice", 8], ["Floods", 6]],
    },
    "dinum": {
        "releve": "2026-07",
        "note": "Volumes relevés sur data.gouv.fr. Le catalogue s'enrichit en continu.",
        "totaux": {"ia": 240, "spatial": 610},
        "exemples": [
            {"titre": "Registre des traitements algorithmiques de l'administration",
             "organisation": "administrations publiques", "licence": "Licence Ouverte"},
            {"titre": "Occupation du sol à grande échelle (OCS GE)",
             "organisation": "IGN", "licence": "Licence Ouverte"},
        ],
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. ACCÈS RÉSEAU
#    Toute lecture passe par ici : un seul endroit à durcir, un seul endroit
#    où le budget de temps est garanti.
# ═══════════════════════════════════════════════════════════════════════════

_TIMEOUT = 8.0            # par requête
_BUDGET = 12.0            # pour l'ensemble des sources, en parallèle


def _hors_ligne():
    for v in ("DO_OFFLINE", "PAN_OFFLINE", "OBS_OFFLINE"):
        if (os.environ.get(v) or "") in ("1", "true", "yes"):
            return True
    return False


def _lire_json(url, timeout=_TIMEOUT):
    """GET JSON. Lève en cas d'échec — l'appelant décide du repli."""
    req = urllib.request.Request(url, headers={
        "User-Agent": _UA,
        "Accept": "application/json",
        "Accept-Language": "fr,en;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        brut = r.read(3_000_000)          # borne dure : une réponse anormale ne
    return json.loads(brut.decode("utf-8", "replace"))   # doit pas saturer la mémoire


def _iso(ts):
    if not ts:
        return None
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ═══════════════════════════════════════════════════════════════════════════
# 4. LECTEURS — un par source
#    Chacun renvoie (données, None) ou (None, "raison lisible de l'échec").
#    La raison est CONSERVÉE et publiée : une source muette sans explication
#    est un défaut qu'on ne voit jamais venir.
# ═══════════════════════════════════════════════════════════════════════════

def lire_copernicus():
    """Produits Sentinel publiés depuis 24 h, par constellation.

    OData avec $top=0&$count=true : on ne rapatrie AUCUN produit, seulement le
    compte. Rapatrier les enregistrements pour les compter ferait passer des
    mégaoctets pour un entier."""
    depuis = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    out, echecs = {}, []
    for col in _COLLECTIONS:
        filtre = ("Collection/Name eq '%s' and ContentDate/Start gt %s" % (col, depuis))
        url = (SOURCES["copernicus"]["point_acces"] + "?"
               + urllib.parse.urlencode({"$filter": filtre, "$top": "0", "$count": "true"}))
        try:
            d = _lire_json(url)
            n = d.get("@odata.count")
            if n is None and isinstance(d.get("value"), list):
                n = len(d["value"])
            if not isinstance(n, int):
                raise ValueError("compte absent de la réponse")
            out[col] = n
        except Exception as e:                       # noqa: BLE001
            echecs.append("%s : %s" % (col, type(e).__name__))
    if not out:
        return None, "catalogue Copernicus injoignable (%s)" % ("; ".join(echecs) or "aucune réponse")
    return {"produits_24h": out,
            "partiel": echecs or None,
            "fenetre": "24 heures glissantes"}, None


def lire_nasa():
    """Événements naturels ouverts suivis par EONET, par catégorie."""
    url = SOURCES["nasa"]["point_acces"] + "?" + urllib.parse.urlencode(
        {"status": "open", "limit": "300"})
    try:
        d = _lire_json(url)
    except Exception as e:                           # noqa: BLE001
        return None, "EONET injoignable (%s)" % type(e).__name__
    ev = d.get("events")
    if not isinstance(ev, list):
        return None, "réponse EONET inattendue (champ « events » absent)"
    par_cat = {}
    for e in ev:
        for c in (e.get("categories") or []):
            titre = (c.get("title") or "").strip()
            if titre:
                par_cat[titre] = par_cat.get(titre, 0) + 1
    classe = sorted(par_cat.items(), key=lambda kv: (-kv[1], kv[0]))
    return {"evenements_ouverts": len(ev),
            "par_categorie": [[k, v] for k, v in classe[:6]]}, None


def lire_dinum():
    """Volumes et exemples du catalogue data.gouv.fr, par thème."""
    totaux, exemples, echecs = {}, [], []
    for r in _REQUETES_DINUM:
        url = SOURCES["dinum"]["point_acces"] + "?" + urllib.parse.urlencode(
            {"q": r["q"], "page_size": "5"})
        try:
            d = _lire_json(url)
            total = d.get("total")
            jeux = d.get("data")
            if not isinstance(total, int) or not isinstance(jeux, list):
                raise ValueError("réponse inattendue")
            totaux[r["cle"]] = total
            for j in jeux[:2]:
                lic = j.get("license") or "non précisée"
                org = (j.get("organization") or {}).get("name") or "producteur non précisé"
                exemples.append({"titre": (j.get("title") or "").strip()[:110],
                                 "organisation": str(org)[:70],
                                 "licence": str(lic)[:40],
                                 "theme": r["cle"]})
        except Exception as e:                       # noqa: BLE001
            echecs.append("%s : %s" % (r["cle"], type(e).__name__))
    if not totaux:
        return None, "data.gouv.fr injoignable (%s)" % ("; ".join(echecs) or "aucune réponse")
    return {"totaux": totaux, "exemples": exemples[:4],
            "partiel": echecs or None}, None


_LECTEURS = {"copernicus": lire_copernicus, "nasa": lire_nasa, "dinum": lire_dinum}

# TTL par source, calé sur le rythme RÉEL de chaque producteur : interroger
# plus souvent ne donne pas une donnée plus fraîche, seulement de la charge.
_TTL = {"copernicus": 3 * 3600, "nasa": 3600, "dinum": 6 * 3600}
_RETRY = 600              # après échec, on ne repart pas à l'assaut

_CACHE = {k: {"ts": 0.0, "ts_ok": 0.0, "data": None, "erreur": None} for k in _LECTEURS}
# UN VERROU PAR SOURCE, et non un verrou global : les trois lectures tournent en
# parallèle, un verrou partagé n'en laisserait passer qu'une et les deux autres
# repartiraient sans avoir essayé — muettes, et sans raison à publier.
_LOCKS = {k: threading.Lock() for k in _LECTEURS}


def _obtenir(cle, force=False):
    """Valeur d'une source : cache, puis réseau, puis repli daté."""
    c = _CACHE[cle]
    maintenant = time.time()
    frais = c["data"] is not None and (maintenant - c["ts"]) < _TTL[cle]
    recemment_echoue = c["data"] is None and (maintenant - c["ts"]) < _RETRY
    if not force and (frais or recemment_echoue):
        return c["data"], c["erreur"], c["ts_ok"]
    if _hors_ligne():
        return None, "mode hors-ligne (variable d'environnement)", c["ts_ok"]
    # Verrou NON bloquant : si un autre fil interroge déjà, on sert l'existant
    # plutôt que d'attendre. Une page qui patiente derrière un verrou réseau
    # est une page qui finit par faire tomber le serveur.
    if not _LOCKS[cle].acquire(blocking=False):
        return c["data"], c["erreur"], c["ts_ok"]
    try:
        data, err = _LECTEURS[cle]()
        c["ts"] = time.time()
        if data is not None:
            c["data"], c["erreur"], c["ts_ok"] = data, None, c["ts"]
        else:
            c["data"], c["erreur"] = None, err
        return c["data"], c["erreur"], c["ts_ok"]
    finally:
        _LOCKS[cle].release()


def rearmer():
    """Remet les caches en état de retenter immédiatement."""
    for c in _CACHE.values():
        c.update({"ts": 0.0, "ts_ok": 0.0, "data": None, "erreur": None})


# ═══════════════════════════════════════════════════════════════════════════
# 5. ASSEMBLAGE
# ═══════════════════════════════════════════════════════════════════════════

METHODOLOGIE = {
    "principe": "Trois sources publiques, sans clé d'API, interrogées en direct. "
                "Chaque mesure est publiée avec son point d'accès, sa licence et "
                "l'heure de son relevé : le lecteur peut refaire la requête.",
    "limites": [
        "CONTEXTE, PAS PREUVE — aucune mesure satellitaire ne démontre l'usage "
        "d'une IA. Ces couches décrivent le sol et l'activité d'observation ; "
        "les systèmes d'IA sont recensés séparément, par pièces documentaires.",
        "Les valeurs de repli sont datées et signalées comme telles. Une source "
        "en repli est écrite « relevé » et jamais « en direct ».",
        "Les comptes Copernicus portent sur les produits MIS À DISPOSITION sur "
        "24 heures glissantes, retraitements compris : ce n'est pas un compte "
        "d'images nouvelles, encore moins de surface observée sans nuages.",
        "Une recherche par mots-clés dans un catalogue ouvert (data.gouv.fr) "
        "n'est pas un recensement : elle rate ce qui est nommé autrement.",
    ],
    "reproduire": "Chaque point d'accès figure dans le référentiel des sources "
                  "ci-dessus. Les requêtes sont des GET simples, sans "
                  "authentification, documentées par leurs producteurs.",
}


def assemble(force=False):
    """Vue complète du socle : référentiel, mesures, état de chaque source."""
    mesures, etat = {}, {}
    if _hors_ligne():
        for cle in _LECTEURS:
            mesures[cle] = dict(SEED[cle], mode="repli")
            etat[cle] = {"ok": False, "mode": "repli", "depuis": None,
                         "raison": "mode hors-ligne (variable d'environnement)"}
    else:
        # En parallèle, sous budget : trois sources en série, c'est trois
        # délais d'attente qui s'additionnent et un serveur qui se fige.
        with _futures.ThreadPoolExecutor(max_workers=len(_LECTEURS)) as ex:
            taches = {cle: ex.submit(_obtenir, cle, force) for cle in _LECTEURS}
            _futures.wait(list(taches.values()), timeout=_BUDGET)
            for cle, t in taches.items():
                if t.done() and not t.cancelled():
                    try:
                        data, err, ts_ok = t.result()
                    except Exception as e:           # noqa: BLE001
                        data, err, ts_ok = None, "erreur interne (%s)" % type(e).__name__, 0.0
                else:
                    t.cancel()
                    data, err, ts_ok = None, "délai dépassé (budget %.0f s)" % _BUDGET, 0.0
                if data is not None:
                    mesures[cle] = dict(data, mode="direct")
                    etat[cle] = {"ok": True, "mode": "direct", "depuis": _iso(ts_ok), "raison": None}
                else:
                    mesures[cle] = dict(SEED[cle], mode="repli")
                    etat[cle] = {"ok": False, "mode": "repli", "depuis": _iso(ts_ok),
                                 "raison": err or "source muette"}

    en_direct = sum(1 for e in etat.values() if e["ok"])
    return {
        "version": VERSION,
        "sources": SOURCES,
        "mesures": mesures,
        "etat": etat,
        "resume": {"sources_total": len(SOURCES), "interrogees": len(_LECTEURS),
                   "en_direct": en_direct},
        "methodologie": METHODOLOGIE,
        "maj": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def sante():
    """Bloc compact pour /api/health — sans déclencher d'appel réseau."""
    return {
        "version": VERSION,
        "sources": len(SOURCES),
        "etat": {cle: {"en_cache": _CACHE[cle]["data"] is not None,
                       "dernier_succes": _iso(_CACHE[cle]["ts_ok"]),
                       "erreur": _CACHE[cle]["erreur"]}
                 for cle in _LECTEURS},
    }
