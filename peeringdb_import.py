# -*- coding: utf-8 -*-
"""Import du registre PeeringDB vers le référentiel des centres de données.

POURQUOI CE MODULE EXISTE
Le référentiel se remplit à la main : une ligne, une source nommée, un couple
lat/lon cohérent avec la commune. C'est ce qui lui donne sa valeur, et c'est
ce qui le maintient à cent dix sites quand l'Europe en compte des milliers.

PeeringDB change l'échelle sans casser la règle. Ce n'est pas un annuaire
tiers : chaque exploitant y inscrit LUI-MÊME ses installations, avec adresse
postale et coordonnées géocodées à partir de cette adresse.

CE QUE L'EXPORT RÉEL A DÉMENTI. Le schéma expose `geocode_status`, qui devait
distinguer une coordonnée normalisée d'une coordonnée saisie. Ce champ est un
PARAMÈTRE DE REQUÊTE : il n'est pas sérialisé dans la fiche, et l'exiger
rejetait deux cent vingt-six lignes sur deux cent vingt-six. Le signal de
repli est la coordonnée elle-même — le registre laisse lat/lon à null quand le
géocodage échoue. Le niveau de preuve est donc MOYEN, il est compté à part, et
chaque site importé le dit dans sa note.

CE QUE CE MODULE NE FAIT PAS
Il ne fusionne rien. Les sites importés portent `provenance='registre'` et
`source_type='registre'` ; les cent dix lignes vérifiées à la main gardent
`provenance='referentiel'`. Confondre les deux ferait passer un enregistrement
déclaratif pour une vérification, ce qui est exactement l'erreur que le
référentiel s'interdit ailleurs — et à six cents lignes contre cent dix, la
vérification serait noyée.

Il ne devine aucune grandeur. PeeringDB ne publie ni puissance, ni PUE, ni
eau, et ne distingue aucun stade d'avancement. Les sites importés arrivent
donc SANS gabarit : le moteur d'estimation répond alors « aucune dérivation
possible » plutôt que de prêter à un bâtiment inconnu l'ordre de grandeur
d'une catégorie qu'on lui aurait attribuée d'office.

CE QU'IL COMPTE, ET POURQUOI IL LE DIT
Chaque écartement est compté par motif. Un import qui annonce « 612 sites
retenus » sans dire qu'il en a écarté 300 laisse croire à une couverture
qu'il n'a pas.

ARCHITECTURE
Aucun import Flask. La lecture réseau est isolée dans `fetch_api`, qui n'est
appelée par rien d'autre : l'import se fait normalement depuis un fichier
JSON déposé, et le module reste testable sans réseau.
"""
import json
import math
import os

VERSION = "2026-08-a"

# ═══════════════════════════════════════════════════════════════════════════
# 1. PÉRIMÈTRE
# ═══════════════════════════════════════════════════════════════════════════

# Les vingt-sept, plus les pays hors Union que le référentiel porte déjà
# (Royaume-Uni, Norvège) et ceux du même espace géographique. Le référentiel
# dit expressément que GB et NO n'appartiennent pas à l'UE ; les accueillir
# reste cohérent tant que la carte le rappelle.
UE27 = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR",
        "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO",
        "SE", "SI", "SK"}
HORS_UE_ACCEPTES = {"GB", "NO", "CH", "IS", "LI"}
EUROPE = UE27 | HORS_UE_ACCEPTES

# La même fenêtre que celle du fond de carte : un point hors cadre ne serait
# pas dessiné, l'accepter reviendrait à gonfler un compte sans rien montrer.
FENETRE = {"lat_min": 34.0, "lat_max": 71.5, "lon_min": -25.0, "lon_max": 32.0}

# Distance en deçà de laquelle un site importé est tenu pour le même bâtiment
# qu'une ligne déjà vérifiée. 1,2 km : au-delà, dans un parc d'activités dense,
# on écraserait des bâtiments réellement distincts ; en deçà, un même campus
# décrit par deux adresses passerait deux fois.
SEUIL_DOUBLON_KM = 1.5

MOTIFS = ("hors_europe", "statut_non_actif", "ferme_declare", "sans_coordonnees",
          "hors_fenetre", "non_geocode", "sans_exploitant", "doublon_referentiel",
          "doublon_interne", "voisinage_a_verifier")

# Une installation FERMÉE reste `status: "ok"` dans le registre : le champ
# décrit l'état de la FICHE, pas celui du bâtiment. Les exploitants écrivent
# la fermeture dans le nom ou dans les notes — « (closed) », « This facility
# has been closed ». Les importer les afficherait « en service », ce qui est
# précisément le contraire de ce qu'ils sont.
_FERME = ("(closed)", "(Closed)", "has been closed", "is now closed",
          "permanently closed", "(ferme)")


# ═══════════════════════════════════════════════════════════════════════════
# 2. LECTURE
# ═══════════════════════════════════════════════════════════════════════════

def charger(source):
    """Une liste d'installations, quelle que soit la forme reçue.

    L'API enveloppe ses résultats dans {"data": [...]} ; un export manuel est
    souvent une liste nue ; une pagination sauvegardée est une liste
    d'enveloppes. Les trois se lisent, parce que le format du fichier déposé
    n'est pas au demandeur de le connaître."""
    if isinstance(source, (list, tuple)):
        brut = list(source)
    elif isinstance(source, dict):
        brut = source.get("data") or []
    else:
        with open(source, encoding="utf-8") as f:
            brut = json.load(f)
        if isinstance(brut, dict):
            brut = brut.get("data") or []
    out = []
    for x in brut:
        if isinstance(x, dict) and "data" in x and isinstance(x["data"], list):
            out.extend(x["data"])          # enveloppe de pagination
        elif isinstance(x, dict):
            out.append(x)
    return out


def fetch_api(pays=None, limite=250, base="https://www.peeringdb.com/api/fac"):
    """Les URL de l'API, page par page. Isolée pour rester sans effet ici.

    Le réseau de compilation n'atteint pas peeringdb.com ; cette fonction
    existe pour le jour où il l'atteindra, et sa construction d'URL est
    vérifiable sans appel. `region_continent=Europe` filtre au plus près,
    `status=ok` écarte les fiches en attente ou supprimées."""
    urls = []
    for i in range(0, 20):
        p = ["status=ok", "limit=%d" % limite, "skip=%d" % (i * limite)]
        p.append("country=%s" % pays if pays else "region_continent=Europe")
        urls.append(base + "?" + "&".join(p))
    return urls


# ═══════════════════════════════════════════════════════════════════════════
# 3. ADMISSION
# ═══════════════════════════════════════════════════════════════════════════

def _coord(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None            # NaN exclu


def ferme(fac):
    """Vrai si la fiche se déclare fermée ailleurs que dans son statut."""
    t = "%s %s" % (fac.get("name") or "", fac.get("notes") or "")
    return any(m.lower() in t.lower() for m in _FERME)


def qualifier(fac, exiger_geocodage=True):
    """None si la fiche est admissible, sinon le motif du refus.

    L'ordre des contrôles suit le coût : le pays d'abord, qui écarte le plus
    de lignes pour le moins de travail."""
    if (fac.get("country") or "").upper() not in EUROPE:
        return "hors_europe"
    if (fac.get("status") or "ok") != "ok":
        return "statut_non_actif"
    if ferme(fac):
        return "ferme_declare"
    lat, lon = _coord(fac.get("latitude")), _coord(fac.get("longitude"))
    if lat is None or lon is None:
        return "sans_coordonnees"
    if not (FENETRE["lat_min"] <= lat <= FENETRE["lat_max"]
            and FENETRE["lon_min"] <= lon <= FENETRE["lon_max"]):
        return "hors_fenetre"
    # LE POINT DE BASCULE, ET SA CORRECTION PAR LES FAITS.
    #
    # `geocode_status` devait distinguer une coordonnée NORMALISÉE par un
    # géocodeur d'une coordonnée saisie à la main — la distinction même qui a
    # fait retirer deux sites du référentiel. Le schéma l'expose... comme
    # PARAMÈTRE DE REQUÊTE. Il n'est pas sérialisé dans la fiche : sur un
    # export réel de 250 installations, aucune ne le porte, et l'exiger
    # rejetait 226 lignes sur 226.
    #
    # Une clé ABSENTE ne vaut donc pas « faux ». Elle vaut « inconnu », et le
    # signal de repli est la coordonnée elle-même : PeeringDB géocode les
    # adresses et laisse lat/lon à null quand il échoue — dans cet export,
    # douze fiches exactement. Le contrôle « sans_coordonnees » ci-dessus fait
    # donc déjà le travail. Ce qui change, c'est le NIVEAU DE PREUVE, et
    # `importer` le compte séparément plutôt que de le taire.
    if exiger_geocodage and fac.get("geocode_status") is False:
        return "non_geocode"
    if not (fac.get("org_name") or "").strip():
        return "sans_exploitant"
    return None


def _souche(nom):
    """Le premier mot significatif d'un nom d'exploitant, en minuscules.

    « NTT (Global Data Centers) », « NTT DATA's Global Data Centers division »
    et « NTT » désignent la même maison ; comparer les chaînes entières les
    séparerait, et le rapprochement de doublons échouerait là où il compte le
    plus — sur les sites que le référentiel porte déjà."""
    t = (nom or "").strip().lower()
    for c in "(),.'":
        t = t.replace(c, " ")
    mots = [m for m in t.split() if m not in ("the", "de", "la", "le")]
    return mots[0] if mots else ""


# Mots trop courants pour identifier un bâtiment : deux fiches qui partagent
# « data », « paris » ou « digital » ne parlent pas forcément du même site.
_BANALS = {"data", "center", "centre", "centers", "centres", "campus", "the",
           "digital", "realty", "interxion", "equinix", "telehouse", "global",
           "switch", "colo", "colocation", "gmbh", "sarl", "inc", "ltd", "bv",
           "paris", "london", "amsterdam", "frankfurt", "vienna", "vienne",
           "madrid", "milan", "berlin", "munich", "dublin", "stockholm",
           "networks", "group", "division", "site", "building", "batiment"}


def _jetons(nom):
    """Les jetons DISTINCTIFS d'un nom de site : « PAR7 », « LD4 », « BER1 »."""
    t = (nom or "").lower()
    out, mot = set(), ""
    for c in t:
        if c.isalnum():
            mot += c
        else:
            if len(mot) >= 3 and mot not in _BANALS:
                out.add(mot)
            mot = ""
    if len(mot) >= 3 and mot not in _BANALS:
        out.add(mot)
    return out


def distance_km(lat1, lon1, lat2, lon2):
    """Haversine. Aux distances qui nous occupent — quelques kilomètres — une
    approximation plane suffirait, mais elle dérive aux latitudes nordiques
    où le référentiel porte de vrais sites (Luleå, Narvik)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


# ═══════════════════════════════════════════════════════════════════════════
# 4. CONVERSION
# ═══════════════════════════════════════════════════════════════════════════

def _adresse(fac):
    bouts = [fac.get("address1"), fac.get("address2"), fac.get("zipcode"),
             fac.get("city")]
    return ", ".join(b.strip() for b in bouts if (b or "").strip())


def _note(fac):
    """Ce que la fiche établit, et ce qu'elle n'établit pas. Écrit à chaque
    ligne parce qu'un lecteur qui clique sur un point n'a pas les limites
    générales sous les yeux."""
    n = ["Enregistrement PeeringDB : l'exploitant a lui-meme inscrit cette "
         "installation, avec son adresse (%s)." % (_adresse(fac) or "non detaillee")]
    compte = []
    for cle, mot in (("net_count", "reseaux"), ("ix_count", "points d'echange"),
                     ("carrier_count", "operateurs de transport")):
        v = fac.get(cle)
        if isinstance(v, int) and v > 0:
            compte.append("%d %s" % (v, mot))
    if compte:
        n.append("Densite d'interconnexion declaree : %s — c'est une mesure du role "
                 "d'echange du site, PAS de sa taille." % ", ".join(compte))
    n.append("Le registre ne distingue aucun stade d'avancement : tout ce qui y "
             "figure est tenu pour en service. Il ne publie ni puissance, ni PUE, "
             "ni consommation d'eau, d'ou l'absence de gabarit — le moteur repond "
             "alors « aucune derivation possible » plutot que de preter a ce "
             "batiment l'ordre de grandeur d'une categorie choisie d'office.")
    if fac.get("geocode_status") is None:
        n.append("Coordonnees : le registre ne publie pas l'indicateur de "
                 "geocodage dans sa reponse ; le point est celui qu'il a calcule "
                 "depuis l'adresse, et les fiches dont le geocodage a echoue "
                 "n'ont aucune coordonnee et n'entrent donc pas. Preuve "
                 "moyenne, non verifiee ligne a ligne.")
    if fac.get("updated"):
        n.append("Fiche mise a jour par l'exploitant le %s." % str(fac["updated"])[:10])
    return " ".join(n)


def convertir(fac):
    """Une fiche PeeringDB dans le schéma du référentiel."""
    nom = (fac.get("name") or "").strip() or (fac.get("name_long") or "").strip()
    return {
        "operateur": (fac.get("org_name") or "").strip(),
        "nom_site": nom or None,
        "ville": (fac.get("city") or "").strip() or None,
        "pays": (fac.get("country") or "").upper(),
        # Quatre décimales : ici elles se justifient, la coordonnée vient d'un
        # géocodage d'adresse et non d'un centroïde de commune.
        "lat": round(_coord(fac.get("latitude")), 4),
        "lon": round(_coord(fac.get("longitude")), 4),
        "statut": "service",
        "annee_service": None,
        "capacite_mw": None,
        "investissement_meur": None,
        "refroidissement": "inconnu",
        "eau_m3_an": None,
        "elec_gwh_an": None,
        "gabarit": None,
        "source_type": "registre",
        "source_libelle": "PeeringDB, fiche installation n° %s inscrite par %s"
                          % (fac.get("id", "?"), (fac.get("org_name") or "?").strip()),
        "confiance": "moyenne",
        "note": _note(fac),
        "provenance": "registre",
    }


# ═══════════════════════════════════════════════════════════════════════════
# 5. IMPORT
# ═══════════════════════════════════════════════════════════════════════════

def importer(source, existants=None, exiger_geocodage=True,
             seuil_km=SEUIL_DOUBLON_KM, voisinage_accepte=()):
    """Les sites retenus, et le compte de tout ce qui ne l'a pas été.

    `voisinage_accepte` : les identifiants PeeringDB dont le signalement a été
    EXAMINÉ et tranché en faveur de l'import. Un site voisin d'un autre du même
    exploitant n'est pas forcément le même bâtiment — PAR1 et PAR7 sont à trois
    kilomètres et sont deux centres réels. La liste rend la décision explicite
    et relisible, au lieu de la cacher dans un seuil.

    `existants` : les lignes déjà présentes au référentiel. Une installation
    importée qui tombe sur l'une d'elles est ÉCARTÉE, jamais fusionnée : la
    ligne vérifiée à la main porte des faits que l'enregistrement n'a pas
    (année, refroidissement, controverse locale) et les remplacer serait une
    perte déguisée en enrichissement."""
    facs = charger(source)
    existants = list(existants or [])
    rapport = {m: 0 for m in MOTIFS}
    rapport["recus"] = len(facs)

    retenus, points = [], []
    ancres = [(s["lat"], s["lon"], _souche(s.get("operateur")),
               _jetons("%s %s" % (s.get("nom_site") or "", s.get("ville") or "")), s)
              for s in existants
              if isinstance(s.get("lat"), (int, float))
              and isinstance(s.get("lon"), (int, float))]
    rapport["sur_preuve_moyenne"] = 0
    rapport["voisinage_a_verifier"] = 0
    rapport["a_verifier"] = []

    for fac in facs:
        motif = qualifier(fac, exiger_geocodage=exiger_geocodage)
        if motif:
            rapport[motif] += 1
            continue
        s = convertir(fac)
        # Doublon avec une ligne déjà vérifiée. Deux critères, parce qu'un seul
        # ne suffit pas : la distance seule laisse passer un même site dont le
        # référentiel porte un point RECONSTITUÉ à deux kilomètres — c'est le
        # cas des treize entrées ajoutées à la main faute de géocodeur. Quand
        # l'exploitant concorde, on élargit donc la fenêtre, et on signale que
        # le registre donne le meilleur point.
        # DEUX RÉGIMES, ET AUCUN N'EST SILENCIEUX.
        #
        # Au-dessous du rayon strict, c'est le même bâtiment : la ligne
        # importée est écartée, la ligne vérifiée reste.
        #
        # Au-dessus, la fusion automatique s'est révélée dangereuse. Élargir
        # sur le seul exploitant confondait PAR1, PAR2 et PAR3 avec PAR7/PAR8 ;
        # ajouter un jeton de nom n'a pas suffi, « Marseille » rapprochant la
        # base sous-marine du campus MRS1-4, distant de cinq kilomètres. On ne
        # fusionne donc plus au jugé : le voisin d'un même exploitant entre 1,5
        # et 5 km est RETENU DEHORS et SIGNALÉ, pour que la décision revienne à
        # qui peut la prendre.
        double, voisin = None, None
        for a, b, souche, jx, ligne in ancres:
            d = distance_km(s["lat"], s["lon"], a, b)
            if d <= seuil_km:
                double = (ligne, d)
                break
            if (souche and souche == _souche(s["operateur"]) and d <= 5.0
                    and (voisin is None or d < voisin[1])):
                voisin = (ligne, d)
        if double:
            rapport["doublon_referentiel"] += 1
            continue
        if voisin and fac.get("id") not in set(voisinage_accepte):
            rapport["a_verifier"].append({
                "importe": s["nom_site"], "ville": s["ville"],
                "voisin_referentiel": voisin[0].get("nom_site") or voisin[0].get("ville"),
                "ecart_km": round(voisin[1], 2),
                "lat": s["lat"], "lon": s["lon"]})
            rapport["voisinage_a_verifier"] += 1
            continue
        if any(distance_km(s["lat"], s["lon"], a, b) <= seuil_km for a, b in points):
            rapport["doublon_interne"] += 1
            continue
        if fac.get("geocode_status") is None:
            rapport["sur_preuve_moyenne"] += 1
        points.append((s["lat"], s["lon"]))
        retenus.append(s)

    rapport["retenus"] = len(retenus)
    rapport["ecartes"] = rapport["recus"] - rapport["retenus"]
    par_pays = {}
    for s in retenus:
        par_pays[s["pays"]] = par_pays.get(s["pays"], 0) + 1
    rapport["par_pays"] = dict(sorted(par_pays.items(), key=lambda x: -x[1]))
    return {"sites": retenus, "rapport": rapport, "version": VERSION}


def resume(rapport):
    """Le rapport en une phrase lisible — celle qu'on colle dans un compte
    rendu. Elle nomme les écartements : un import silencieux sur ses pertes
    se lit comme une couverture complète."""
    pertes = ", ".join("%s %d" % (m.replace("_", " "), rapport[m])
                       for m in MOTIFS if rapport.get(m))
    return ("%d fiches reçues, %d retenues, %d écartées (%s)."
            % (rapport["recus"], rapport["retenus"], rapport["ecartes"],
               pertes or "aucune"))


CLES = ["operateur", "nom_site", "ville", "pays", "lat", "lon", "statut",
        "annee_service", "capacite_mw", "investissement_meur", "refroidissement",
        "eau_m3_an", "elec_gwh_an", "gabarit", "source_type", "source_libelle",
        "confiance", "note", "provenance"]


def lignes_python(sites):
    """Les sites au format exact du fichier `datacentres.py` — un dict par
    ligne, clés dans l'ordre. Le référentiel reste un fichier lisible et
    diffable ; charger l'import depuis un JSON séparé au démarrage ferait
    dépendre la carte d'un fichier que la revue de code ne voit jamais."""
    out = []
    for d in sites:
        out.append(" {%s},"
                   % ", ".join("%r: %r" % (k, d.get(k)) for k in CLES))
    return "\n".join(out)


def sante():
    return {"version": VERSION, "pays_acceptes": len(EUROPE),
            "seuil_doublon_km": SEUIL_DOUBLON_KM,
            "geocodage_exige_par_defaut": True,
            "reseau_requis": False}


if __name__ == "__main__":                                   # pragma: no cover
    import sys
    if len(sys.argv) < 2:
        print("usage : python3 peeringdb_import.py <export.json> [sortie.txt]")
        raise SystemExit(2)
    import datacentres
    r = importer(sys.argv[1], existants=datacentres.SITES)
    print(resume(r["rapport"]))
    print("par pays :", r["rapport"]["par_pays"])
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(lignes_python(r["sites"]) + "\n")
        print("lignes ecrites dans", os.path.basename(sys.argv[2]))
