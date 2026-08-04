# -*- coding: utf-8 -*-
"""Précalcul des cartes : ce qui ne dépend que de constantes n'a rien à faire
dans le navigateur.

CE QUI A ÉTÉ MESURÉ

Sur un processeur ralenti ×6 — l'ordre de grandeur d'un téléphone ou d'un
portable de bureau — le premier rendu de la carte du panel coûtait 154 ms, dont
94 ms de pure reconstruction des tracés. Or un tracé de pays ne dépend que de
deux choses : les contours et la projection. L'une et l'autre sont des
constantes du fichier. Le navigateur refaisait donc, à chaque visite de chaque
lecteur, 32 530 projections et une simplification de Douglas-Peucker pour
aboutir très exactement à la même chaîne de caractères.

Ce module fait ce travail UNE fois, ici, et écrit le résultat dans les pages.
Le navigateur n'a plus qu'à lire des chaînes déjà prêtes.

CE QUE ÇA CHANGE POUR LE POIDS DES PAGES

Le gain n'est pas seulement en calcul. Les coordonnées brutes pesaient 445 Ko
dans `panorama.html` et 300 Ko dans `observatoire.html`, qu'il fallait
télécharger puis analyser pour construire trente-deux mille tableaux de deux
nombres. Les tables dérivées, elles, pèsent 120 et 98 Ko. On enlève donc
davantage qu'on n'ajoute.

POURQUOI LA GÉOMÉTRIE SOURCE RESTE DANS LE DÉPÔT

Elle part dans `cartes_source/`. Une page qui ne contiendrait plus que des
tracés déjà projetés serait une impasse : changer la fenêtre de projection, la
tolérance, ou ajouter un pays deviendrait impossible sans retrouver les données
d'origine. Ce qui disparaît de la page reste versionné à côté.

COMMENT ON SAIT QUE LA CARTE N'A PAS BOUGÉ

En comparant, caractère par caractère, ce que produit ce module avec ce que
produit aujourd'hui le navigateur sur les mêmes pages. Tant que les deux
suites de chaînes sont identiques, la carte affichée ne peut pas différer :
ce sont littéralement les mêmes `d="…"`. C'est une preuve d'égalité, pas une
comparaison d'images où l'on négocierait un seuil.

Le contrôle est reproductible :

    python3 cartes_precalc.py --verifier chemins_extraits.json

et il refuse silencieusement de valider quoi que ce soit : toute divergence est
affichée avec le pays, la position du premier caractère qui diffère, et les
deux fragments en regard.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

RACINE = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.path.join(RACINE, "cartes_source")

# Sous le tiers de pixel : deux points séparés de moins que cela tombaient de
# toute façon sur le même pixel à l'écran. La tolérance s'exprime en PIXELS DE
# LA CARTE RENDUE et jamais en degrés — un dixième de degré ne couvre pas la
# même distance à l'écran en Crète et au cap Nord, et une tolérance en degrés
# déformerait le nord de l'Europe en épargnant le sud.
TOLERANCE_PX = 0.34

# Les deux cartes du site. Toute autre page n'a pas de carte à tracer :
# `platform.html` recolore un SVG statique.
#
# La fenêtre de projection n'est PAS recopiée ici : elle est lue dans la page.
# L'avoir recopiée est exactement l'erreur qui a été commise en écrivant ce
# module — le facteur de hauteur vaut 1,25 sur la carte européenne et 1,08 sur
# la mondiale, et la transcription a propagé le premier aux deux. Toute la
# carte du monde s'est décalée verticalement. Deux copies d'une constante
# finissent toujours par diverger ; on n'en garde qu'une, et c'est la page.
CARTES = {
    "panorama": {"fichier": "panorama.html", "source": "contours-ue.json", "etendues": False},
    "observatoire": {"fichier": "observatoire.html", "source": "contours-monde.json", "etendues": True},
}

_RE_PROJ = re.compile(
    r"var\s+PROJ\s*=\s*\{\s*lngMin\s*:\s*(-?[\d.]+)\s*,\s*lngMax\s*:\s*(-?[\d.]+)\s*,"
    r"\s*latMin\s*:\s*(-?[\d.]+)\s*,\s*latMax\s*:\s*(-?[\d.]+)\s*,\s*W\s*:\s*(-?[\d.]+)\s*\}")
_RE_H = re.compile(r"PROJ\.H\s*=\s*Math\.round\(\s*PROJ\.W\s*\*\s*\(PROJ\.latMax\s*-\s*PROJ\.latMin\)\s*/"
                   r"\s*\(PROJ\.lngMax\s*-\s*PROJ\.lngMin\)\s*\*\s*([\d.]+)\s*\)")


def projection(nom: str) -> dict:
    """Fenêtre de projection LUE dans la page, jamais recopiée."""
    s = open(os.path.join(RACINE, CARTES[nom]["fichier"]), encoding="utf-8").read()
    m, h = _RE_PROJ.search(s), _RE_H.search(s)
    if not m or not h:
        raise SystemExit("PROJ introuvable dans %s — la page a changé de forme, "
                         "le module doit être relu avant d'être relancé" % CARTES[nom]["fichier"])
    return {"lngMin": float(m.group(1)), "lngMax": float(m.group(2)),
            "latMin": float(m.group(3)), "latMax": float(m.group(4)),
            "W": float(m.group(5)), "ratio": float(h.group(1))}


# ── Arithmétique : reproduire JavaScript, pas « faire pareil » ────────────────
#
# `Math.round` de JavaScript arrondit la moitié VERS LE HAUT ; `round()` de
# Python arrondit vers le pair le plus proche. Sur seize mille points, la
# différence ne serait pas anecdotique. On réimplémente donc la règle de
# JavaScript, et on la vérifie ensuite contre le navigateur.
def _js_round(x: float) -> int:
    return math.floor(x + 0.5)


def _hauteur(proj: dict) -> float:
    return float(_js_round(proj["W"] * (proj["latMax"] - proj["latMin"])
                           / (proj["lngMax"] - proj["lngMin"]) * proj["ratio"]))


def _num(v: float) -> str:
    """Écriture courte d'un nombre de tracé, à l'identique de la page.

    Pas de « .0 » inutile, pas de zéro avant la virgule. Le nombre est écrit
    depuis l'entier des dixièmes plutôt que depuis le flottant : `str()` de
    Python et `toString()` de JavaScript ne produisent pas la même chaîne pour
    un entier (« 12.0 » contre « 12 »), et cet écart-là se répéterait partout.
    """
    n = _js_round(v * 10)
    if n % 10 == 0:
        return str(n // 10)
    signe = "-" if n < 0 else ""
    a = abs(n)
    ent, dec = a // 10, a % 10
    return signe + ("" if ent == 0 else str(ent)) + "." + str(dec)


def _dp(xs: list, ys: list, tol: float):
    """Douglas-Peucker itératif — le même que celui de la page.

    Itératif et non récursif : une côte norvégienne empilerait des milliers
    d'appels. Distance au SEGMENT et non à la droite : sur un anneau fermé les
    deux extrémités coïncident et la droite dégénère.
    """
    n = len(xs)
    if n < 3:
        return None
    garde = bytearray(n)
    garde[0] = 1
    garde[n - 1] = 1
    pile = [(0, n - 1)]
    t2 = tol * tol
    while pile:
        a, b = pile.pop()
        if b <= a + 1:
            continue
        ax, ay, bx, by = xs[a], ys[a], xs[b], ys[b]
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        pire, dpire = -1, -1.0
        for i in range(a + 1, b):
            px, py = xs[i] - ax, ys[i] - ay
            if l2 == 0:
                d2 = px * px + py * py
            else:
                t = (px * dx + py * dy) / l2
                t = 0.0 if t < 0 else (1.0 if t > 1 else t)
                qx, qy = px - t * dx, py - t * dy
                d2 = qx * qx + qy * qy
            if d2 > dpire:
                dpire, pire = d2, i
        if dpire > t2 and pire > 0:
            garde[pire] = 1
            pile.append((a, pire))
            pile.append((pire, b))
    gx = [xs[k] for k in range(n) if garde[k]]
    gy = [ys[k] for k in range(n) if garde[k]]
    return gx, gy


def chemin(polys, proj: dict, tol: float = TOLERANCE_PX):
    """Tracé SVG d'un pays, et le compte des points avant/après.

    Trois garde-fous, parce qu'une simplification qui fait disparaître un pays
    coûte plus cher que les millisecondes qu'elle gagne :
      · aucun ANNEAU n'est supprimé — un anneau, c'est une île ;
      · un anneau qui descendrait sous quatre points garde ses points d'origine ;
      · le premier et le dernier point sont toujours conservés, sinon le contour
        ne se referme plus.
    """
    if not polys:
        return "", 0, 0
    H = _hauteur(proj)
    W, lo, la = proj["W"], proj["lngMin"], proj["latMin"]
    dlng = proj["lngMax"] - lo
    dlat = proj["latMax"] - la
    d, avant, apres = [], 0, 0
    for poly in polys:
        ring = poly[0]
        n = len(ring)
        avant += n
        dedans = False
        xs, ys = [], []
        # Projection d'abord, simplification ensuite : c'est en pixels que l'on
        # décide de ce qui se voit, pas en degrés.
        for lng, lat in ring:
            if lo < lng < proj["lngMax"] and la < lat < proj["latMax"]:
                dedans = True
            xs.append(max(0.0, min(W, (lng - lo) / dlng * W)))
            latc = max(la, min(proj["latMax"], lat))
            ys.append(max(0.0, min(H, (proj["latMax"] - latc) / dlat * H)))
        if not dedans:
            continue
        simple = _dp(xs, ys, tol)
        gx, gy = simple if simple else (xs, ys)
        if len(gx) < 4:
            gx, gy = xs, ys
        apres += len(gx)
        # Coordonnées RELATIVES, mais les écarts sont calculés sur les valeurs
        # DÉJÀ ARRONDIES : arrondir chaque delta séparément ferait dériver le
        # tracé point après point, et la dérive se verrait au bout d'une côte
        # longue. Ici la somme des écarts redonne exactement la position
        # arrondie.
        seg, px, py = [], 0.0, 0.0
        for m in range(len(gx)):
            rx = _js_round(gx[m] * 10) / 10
            ry = _js_round(gy[m] * 10) / 10
            if m == 0:
                seg.append("M" + _num(rx) + " " + _num(ry))
            else:
                seg.append("l" + _num(rx - px) + " " + _num(ry - py))
            px, py = rx, ry
        d.append("".join(seg) + "Z")
    return "".join(d), avant, apres


def centroide(polys):
    """Centroïde d'AIRE du plus grand polygone, en degrés.

    Formule d'aire et non moyenne des sommets : celle-ci dérive vers les côtes
    les plus découpées et poserait le nom de la Norvège en pleine mer.

    Renvoie None quand aucun anneau n'a d'aire — le Vatican, dont le contour
    du référentiel est dégénéré, est dans ce cas. La page n'écrit alors pas son
    nom, et c'est ce qu'elle faisait déjà : on reproduit, on ne corrige pas au
    passage.
    """
    if not polys:
        return None
    best, besta = None, 0.0
    for poly in polys:
        ring = poly[0]
        a = cx = cy = 0.0
        for i in range(len(ring) - 1):
            x0, y0 = ring[i]
            x1, y1 = ring[i + 1]
            f = x0 * y1 - x1 * y0
            a += f
            cx += (x0 + x1) * f
            cy += (y0 + y1) * f
        a = a / 2
        if abs(a) > abs(besta) and a != 0:
            besta = a
            best = [cx / (6 * a), cy / (6 * a)]
    return best


def etendue(polys, proj: dict):
    """Plus petite dimension du pays à l'écran, en pixels.

    Sert à taire les micro-États : un code posé sur une île de deux pixels ne
    désigne plus rien. Sans écrêtage, contrairement au tracé — c'est la taille
    réelle du pays qui décide, pas la portion visible dans le cadre.
    """
    if not polys:
        return 0.0
    H = _hauteur(proj)
    W, lo, la = proj["W"], proj["lngMin"], proj["latMin"]
    dlng = proj["lngMax"] - lo
    dlat = proj["latMax"] - la
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for poly in polys:
        for lng, lat in poly[0]:
            X = (lng - lo) / dlng * W
            Y = (proj["latMax"] - lat) / dlat * H
            x0, x1 = min(x0, X), max(x1, X)
            y0, y1 = min(y0, Y), max(y1, Y)
    return min(x1 - x0, y1 - y0)


# ── Construction des tables ──────────────────────────────────────────────────
def tables(nom: str) -> dict:
    cfg = CARTES[nom]
    contours = json.load(open(os.path.join(SOURCES, cfg["source"]), encoding="utf-8"))
    proj = projection(nom)
    ch, ce, et = {}, {}, {}
    avant = apres = 0
    for code, polys in contours.items():
        d, a, b = chemin(polys, proj)
        avant += a
        apres += b
        ch[code] = d
        c = centroide(polys)
        if c is not None:
            ce[code] = c
        if cfg["etendues"]:
            et[code] = etendue(polys, proj)
    return {"chemins": ch, "centroides": ce, "etendues": et,
            "points_avant": avant, "points_apres": apres, "pays": len(ch)}


def _arrondi_utile(x: float, n: int = 4) -> float:
    """Un centroïde au dix-millième de degré, c'est onze mètres : bien en deçà
    de ce qu'un libellé de pays exige. Garder quinze décimales n'ajouterait que
    des octets."""
    return round(x, n)


def js_tables(t: dict, etendues: bool) -> str:
    """L'ORDRE DES PAYS EST SIGNIFIANT — ne pas trier.

    La page parcourt `Object.keys(CHEMINS)` pour dessiner, et en SVG le dernier
    tracé passe AU-DESSUS des précédents. L'ordre de la table est donc l'ordre
    de peinture : là où deux pays se recouvrent — une enclave, un micro-État
    posé dans son voisin — c'est lui qui décide lequel reste visible.

    Ces tables ont d'abord été écrites triées par code, ce qui paraissait plus
    propre. La recette l'a rattrapé : l'infobulle d'un pays de la carte
    mondiale ne s'ouvrait plus, parce que ce n'était plus le même pays qui se
    trouvait au-dessus. On conserve donc l'ordre du référentiel d'origine,
    lequel est celui que la page utilisait.
    """
    ch = ",".join('"%s":"%s"' % (k, v) for k, v in t["chemins"].items())
    ce = ",".join('"%s":[%s,%s]' % (k, _arrondi_utile(v[0]), _arrondi_utile(v[1]))
                  for k, v in t["centroides"].items())
    out = "var CHEMINS={%s};\nvar CENTROIDES={%s};\n" % (ch, ce)
    if etendues:
        et = ",".join('"%s":%s' % (k, round(v, 2)) for k, v in t["etendues"].items())
        out += "var ETENDUES_PX={%s};\n" % et
    return out


# ── Vérification contre le navigateur ────────────────────────────────────────
def verifier(chemin_json: str) -> int:
    """Compare, caractère par caractère, avec ce que produit la page aujourd'hui."""
    ecarts = 0
    for nom in CARTES:
        f = chemin_json.replace("NOM", nom)
        if not os.path.exists(f):
            print("  %-12s extraction absente (%s) — ignoré" % (nom, f))
            continue
        ref = json.load(open(f, encoding="utf-8"))
        t = tables(nom)
        print("\n  ══ %s ══" % nom)

        mk_ref, mk_new = set(ref["chemins"]), set(t["chemins"])
        if mk_ref != mk_new:
            print("    KO  liste des pays différente : en trop %s, manquants %s"
                  % (sorted(mk_new - mk_ref), sorted(mk_ref - mk_new)))
            ecarts += 1

        # L'ordre est un contrôle à part entière : en SVG, le dernier tracé
        # passe au-dessus. Deux tables aux mêmes contenus mais aux ordres
        # différents ne dessinent pas la même carte là où des pays se
        # recouvrent, et aucune comparaison de chaînes ne le verrait.
        ordre_ref, ordre_new = list(ref["chemins"]), list(t["chemins"])
        if ordre_ref != ordre_new:
            i = next((i for i in range(min(len(ordre_ref), len(ordre_new)))
                      if ordre_ref[i] != ordre_new[i]), 0)
            print("    KO  ordre de peinture différent au rang %d : page « %s », module « %s »"
                  % (i, ordre_ref[i], ordre_new[i]))
            ecarts += 1
        else:
            print("    OK  ordre de peinture conservé (%s … %s)" % (ordre_ref[0], ordre_ref[-1]))

        diff = []
        for k in sorted(mk_ref & mk_new):
            if ref["chemins"][k] != t["chemins"][k]:
                a, b = ref["chemins"][k], t["chemins"][k]
                i = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
                diff.append((k, i, a[max(0, i - 20):i + 20], b[max(0, i - 20):i + 20]))
        if diff:
            ecarts += 1
            print("    KO  %d tracé(s) diffèrent :" % len(diff))
            for k, i, a, b in diff[:6]:
                print("        %s au caractère %d\n          page   …%s…\n          module …%s…" % (k, i, a, b))
        else:
            print("    OK  %d tracés identiques au caractère près (%s Ko)"
                  % (len(mk_ref), round(sum(len(v) for v in t["chemins"].values()) / 1024)))

        # Les centroïdes sont arrondis au dix-millième de degré pour la page :
        # on compare donc à cette précision-là, celle qui sera réellement
        # embarquée, et non à la précision brute qui ne sera jamais utilisée.
        cd = [k for k in set(ref["centroides"]) | set(t["centroides"])
              if k not in ref["centroides"] or k not in t["centroides"]
              or abs(_arrondi_utile(ref["centroides"][k][0]) - _arrondi_utile(t["centroides"][k][0])) > 1e-9
              or abs(_arrondi_utile(ref["centroides"][k][1]) - _arrondi_utile(t["centroides"][k][1])) > 1e-9]
        if cd:
            ecarts += 1
            print("    KO  %d centroïde(s) diffèrent : %s" % (len(cd), sorted(cd)[:10]))
        else:
            print("    OK  %d centroïdes identiques (dont l'absence de %s)"
                  % (len(t["centroides"]),
                     ", ".join(sorted(set(ref["chemins"]) - set(ref["centroides"]))) or "aucun"))

        if CARTES[nom]["etendues"]:
            ed = [k for k in ref.get("etendues", {})
                  if abs(ref["etendues"][k] - t["etendues"].get(k, -1)) > 0.005]
            if ed:
                ecarts += 1
                print("    KO  %d étendue(s) diffèrent : %s" % (len(ed), sorted(ed)[:10]))
            else:
                print("    OK  %d étendues identiques au centième de pixel"
                      % len(ref.get("etendues", {})))
        print("    points %s → %s (%d %%)"
              % (t["points_avant"], t["points_apres"],
                 round(100 * t["points_apres"] / max(1, t["points_avant"]))))
    return ecarts


# ── Écriture dans les pages ──────────────────────────────────────────────────
#
# Chaque remplacement est ancré sur un motif qui ne peut désigner qu'une seule
# chose, et le module s'ARRÊTE si un motif ne correspond pas exactement une
# fois. Une réécriture qui « fait de son mieux » sur une page qu'elle ne
# reconnaît plus produit un fichier à moitié converti, et c'est le genre de
# dégât qu'on ne voit qu'à l'exécution.

ENTETE = """/* ══════════════════════════════════════════════════════════════════════════
   GÉOGRAPHIE — tracés déjà prêts, calculés hors du navigateur

   Ces tables sont produites par `cartes_precalc.py` à partir de la géométrie
   brute, restée dans `cartes_source/`. Elles NE SONT PAS À MODIFIER À LA MAIN :
   on change la source ou la projection, puis on relance le module.

   Ce que le navigateur faisait avant, et ne fait plus : projeter %(pts)s points
   de coordonnées, les simplifier, et assembler les chaînes — à chaque visite,
   pour un résultat qui ne dépend que de deux constantes du fichier. Mesuré sur
   un processeur ralenti ×6, ce travail coûtait 94 des 154 ms du premier rendu.

   · CHEMINS      tracé SVG par pays, en coordonnées de la carte (viewBox),
                  simplifié à %(tol)s px — sous le tiers de pixel, donc sans
                  effet visible : %(pts)s points ramenés à %(gard)s.
   · CENTROIDES   centroïde d'AIRE en degrés, ancre des libellés. Un pays sans
                  entrée n'a pas d'ancre et n'écrit pas son nom%(va)s.%(etl)s

   L'égalité avec l'ancien calcul a été vérifiée caractère par caractère :
       python3 cartes_precalc.py --verifier <extraction.json>
   ══════════════════════════════════════════════════════════════════════════ */
"""

ACCESSEURS = """
/* Les tracés sont désormais lus, plus calculés. La fonction reste, parce que
   c'est elle que le reste de la page appelle — et parce qu'un pays hors cadre
   doit continuer de renvoyer une chaîne vide plutôt que `undefined`. */
function cheminPays(code){ return CHEMINS[code] || ""; }

/* Exposé pour la mesure : une optimisation dont on ne peut pas vérifier l'effet
   est une optimisation qu'on croit sur parole. Les comptes de points sont
   désormais des faits de fabrication, pas des mesures d'exécution — ils sont
   inscrits par `cartes_precalc.py` et rappelés ici tels quels. */
function cheminStats(){
  return { pays: Object.keys(CHEMINS).length,
           points_origine: %(pts_n)d,
           points_retenus: %(gard_n)d,
           tolerance_px: %(tol)s,
           octets: Object.keys(CHEMINS).reduce(function(s, k){ return s + CHEMINS[k].length; }, 0) };
}
"""

CENTROIDE = """/* Ancre des libellés : centroïde d'AIRE du plus grand polygone, en degrés.
   Formule d'aire et non moyenne des sommets — celle-ci dérive vers les côtes
   les plus découpées et poserait le nom de la Norvège en pleine mer. Le calcul
   est fait à la fabrication ; il ne reste ici que la lecture. */
function centroidePays(code){ return CENTROIDES[code] || null; }
"""

ETENDUE = """/* Plus petite dimension du pays à l'écran, en pixels. Sert à taire les
   micro-États : un code posé sur une île de deux pixels ne désigne plus rien.
   Mesurée sans écrêtage, contrairement au tracé — c'est la taille réelle du
   pays qui décide, pas la portion visible dans le cadre. */
function etendue(code){ var v = ETENDUES_PX[code]; return v === undefined ? 0 : v; }
"""


def _un_seul(s: str, motif, quoi: str, fichier: str):
    """Remplace un motif unique, ou s'arrête en disant lequel et combien."""
    r = motif if hasattr(motif, "finditer") else re.compile(re.escape(motif))
    n = len(r.findall(s))
    if n != 1:
        raise SystemExit("  ✗ %s : « %s » trouvé %d fois (attendu 1) — page non reconnue, "
                         "rien n'a été écrit" % (fichier, quoi, n))
    return r


def ecrire(nom: str) -> None:
    cfg = CARTES[nom]
    p = os.path.join(RACINE, cfg["fichier"])
    s = open(p, encoding="utf-8").read()
    t = tables(nom)
    sans_centre = sorted(set(t["chemins"]) - set(t["centroides"]))
    # Deux écritures du même compte, et elles ne sont pas interchangeables :
    # « 32 530 » se lit dans une phrase, `32530` s'exécute. Les avoir confondues
    # a écrit `points_origine: 32 530` dans le code et cassé toute la page —
    # une espace insécable de typographie française au milieu d'un littéral.
    ctx = {"pts": "{:,}".format(t["points_avant"]).replace(",", "\u202f"),
           "gard": "{:,}".format(t["points_apres"]).replace(",", "\u202f"),
           "pts_n": t["points_avant"], "gard_n": t["points_apres"],
           "tol": TOLERANCE_PX,
           "va": " (c'est le cas de %s, dont le contour du référentiel est "
                 "dégénéré)" % ", ".join(sans_centre) if sans_centre else "",
           "etl": "\n   · ETENDUES_PX  plus petite dimension du pays à l'écran, en pixels."
                  if cfg["etendues"] else ""}

    # 1. Les coordonnées brutes cèdent la place aux tables dérivées.
    r = _un_seul(s, re.compile(r"var CONTOURS = \{.*?\};\n", re.S), "var CONTOURS", cfg["fichier"])
    s = r.sub(lambda _: ENTETE % ctx + js_tables(t, cfg["etendues"]), s, count=1)

    # 2. Le bloc de construction des tracés — du commentaire d'en-tête jusqu'à
    #    la fin de `cheminStats` — devient deux lectures de table.
    r = _un_seul(s, re.compile(
        r"/\* ═+\n   TRACÉS DE PAYS.*?\nfunction cheminStats\(\)\{.*?\n\}\n", re.S),
        "bloc TRACÉS DE PAYS", cfg["fichier"])
    s = r.sub(lambda _: (ACCESSEURS % ctx).lstrip("\n"), s, count=1)

    # 3. Le centroïde d'aire.
    r = _un_seul(s, re.compile(
        r"/\* Centroide du plus grand polygone.*?\nfunction centroidePays\(code\)\{.*?\n\}\n"
        r"|function centroidePays\(code\)\{.*?\n\}\n", re.S), "centroidePays", cfg["fichier"])
    s = r.sub(lambda _: CENTROIDE, s, count=1)

    # 4. L'étendue à l'écran, quand la page en a une.
    if cfg["etendues"]:
        r = _un_seul(s, re.compile(
            r"/\* Plus petite dimension du pays.*?\nfunction etendue\(code\)\{.*?\n  \}\n"
            r"  return ETENDUES\[code\];\n\}\n", re.S), "etendue", cfg["fichier"])
        s = r.sub(lambda _: ETENDUE, s, count=1)
        s = s.replace("var ANCRES = null, ETENDUES = {};", "var ANCRES = null;")

    # 5. Les parcours de la liste des pays lisent la table des tracés.
    n = s.count("CONTOURS")
    s = s.replace("Object.keys(CONTOURS)", "Object.keys(CHEMINS)")
    reste = [l for l in s.split("\n") if "CONTOURS" in l]
    if reste:
        raise SystemExit("  ✗ %s : %d référence(s) à CONTOURS subsistent après réécriture :\n    %s"
                         % (cfg["fichier"], len(reste), "\n    ".join(x.strip()[:110] for x in reste)))

    open(p, "w", encoding="utf-8").write(s)
    print("  %-18s %s pays · %s Ko de tracés · %d renvois vers la table · page %s Ko"
          % (cfg["fichier"], t["pays"],
             round(sum(len(v) for v in t["chemins"].values()) / 1024), n,
             round(len(s) / 1024)))


def extraire_source(chemin_json: str) -> None:
    """Sort la géométrie brute des pages vers `cartes_source/`."""
    os.makedirs(SOURCES, exist_ok=True)
    for nom, cfg in CARTES.items():
        f = chemin_json.replace("NOM", nom)
        d = json.load(open(f, encoding="utf-8"))
        dest = os.path.join(SOURCES, cfg["source"])
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(d["contours"], fh, separators=(",", ":"), ensure_ascii=False)
        print("  %-22s %s pays, %s Ko"
              % (cfg["source"], len(d["contours"]), round(os.path.getsize(dest) / 1024)))


if __name__ == "__main__":
    if "--extraire" in sys.argv:
        extraire_source(sys.argv[sys.argv.index("--extraire") + 1])
    elif "--ecrire" in sys.argv:
        for nom in CARTES:
            ecrire(nom)
    elif "--verifier" in sys.argv:
        n = verifier(sys.argv[sys.argv.index("--verifier") + 1])
        print("\n  %s" % ("✓ le module reproduit exactement la page"
                          if not n else "✗ %d écart(s) — NE PAS EMBARQUER" % n))
        sys.exit(1 if n else 0)
    else:
        for nom in CARTES:
            t = tables(nom)
            print("%-13s %d pays · %d Ko de tracés · points %d → %d"
                  % (nom, t["pays"],
                     round(sum(len(v) for v in t["chemins"].values()) / 1024),
                     t["points_avant"], t["points_apres"]))
