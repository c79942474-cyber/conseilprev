# -*- coding: utf-8 -*-
"""Dossier téléchargeable de l'Observatoire de l'IA — Word et PDF.

POURQUOI CE MODULE EXISTE

L'Observatoire donne à l'écran des cartes, des courbes et des tableaux. Ils
servent à préparer un comité, une note de cadrage, une réponse à appel d'offres
— c'est-à-dire un DOCUMENT. Tant qu'il fallait recopier les chiffres à la main,
chacun perdait en route ce qui fait sa valeur : sa source, sa licence, son
millésime, et surtout sa PRÉCISION — exact, classe, ou lu sur une carte.

CE QUE CE MODULE NE FAIT PAS

Aucun modèle de langage n'intervient. Le texte est composé ici, à partir du
référentiel `observatoire_ia`. Les documents portent donc `ia=False` : pas de
marquage article 50, et ils le disent en toutes lettres.

LES LICENCES VOYAGENT AVEC LES DONNÉES

C'est la contrainte propre à ce dossier, et elle est plus stricte que celle du
Panorama. Les brevets viennent de l'AI Index, publié sous **CC BY-ND 4.0** :
attribution obligatoire, et PAS DE DÉRIVÉE. Un chiffre repris avec son crédit
exact reste une citation ; une figure retravaillée, non. Les talents viennent de
MacroPolo, sous copyright avec citation. Chaque section porte donc sa source,
sa licence et son crédit, et le document rappelle en tête ce que le lecteur a
le droit d'en faire. Un document exporté circule sans nous.

LES FIGURES

Les cartes et les graphiques sont dessinés par le navigateur à partir de ces
mêmes chiffres. Le document les appelle par `![légende](fig:CLE)` ; c'est la
page qui les joint, en PNG. Une figure absente est ÉCRITE comme absente — un
dossier qui promet une carte et n'en porte pas est pire qu'un dossier sans
carte.
"""
from datetime import datetime, timezone

import observatoire_ia

VERSION = "2026-08-a"

FORMATS = ("docx", "pdf")

# Les figures que la page peut joindre, et le chapitre où chacune se pose. La
# clé est le contrat entre le navigateur et ce module : elle ne s'invente pas
# des deux côtés.
FIGURES = (
    ("carte-modeles", "Modèles d'IA remarquables — carte du monde par classe"),
    ("brevets", "Brevets d'IA accordés — vue affichée à l'écran"),
    ("talents", "Chercheurs d'élite en IA — vue affichée à l'écran"),
    # PAS DE FIGURE POUR L'ADOPTION. Ce panneau ne dessine pas de SVG : ses
    # barres sont des blocs HTML mis en forme par la feuille de style. Déclarer
    # la clé quand même aurait produit, à chaque export, un « figure non
    # jointe » que rien ne pouvait satisfaire — un défaut permanent affiché
    # comme un incident. Le chapitre garde son tableau, qui porte les mêmes
    # chiffres.
)

DOSSIERS = {
    "observatoire": {
        "nom": "Observatoire de l'IA — état des lieux mondial et européen",
        "resume": "Les cinq panneaux de l'Observatoire réunis : modèles remarquables "
                  "par pays, brevets accordés, chercheurs d'élite, adoption par les "
                  "entreprises de l'Union, cadre et gouvernance — avec les cartes et "
                  "graphiques affichés, la source et la licence de chaque chiffre.",
    },
}

MARQUE = {
    "ia": False,
    "marque_suffixe": "",
    "bandeau": "Observatoire de l'intelligence artificielle",
    "statut": "Calcul déterministe — aucune rédaction par IA",
}


def _esc(t):
    """Le caractère `|` couperait une cellule de tableau en deux."""
    return str(t if t is not None else "").replace("|", "/")


def _tab(entetes, lignes):
    out = ["| " + " | ".join(_esc(e) for e in entetes) + " |",
           "|" + "|".join(["---"] * len(entetes)) + "|"]
    for l in lignes:
        out.append("| " + " | ".join(_esc(c) for c in l) + " |")
    return "\n".join(out)


def _fr(x):
    """Le séparateur décimal français. Un « 69.7 » au milieu d'une page
    française se lit comme un séparateur de milliers."""
    if x is None:
        return "n. d."
    s = ("%g" % x)
    return s.replace(".", ",")


def _horodatage():
    return datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")


def _bloc_source(d, titre="Source"):
    """La carte d'identité d'un jeu de données, en clair sous son chapitre.

    Quatre lignes, jamais moins : d'où vient le chiffre, sous quelle licence il
    circule, de quand il date, et CE QU'IL VAUT. La quatrième est celle qu'on
    oublie et c'est la plus utile — « classe » et « lecture graphique » ne se
    citent pas comme « exact »."""
    lignes = []
    if d.get("source"):
        lignes.append("- **%s** — %s" % (titre, d["source"]))
    if d.get("licence"):
        lignes.append("- **Licence** — %s" % d["licence"])
    if d.get("date"):
        lignes.append("- **Millésime** — %s" % d["date"])
    if d.get("precision"):
        lignes.append("- **Précision** — %s" % d["precision"])
    if d.get("credit"):
        lignes.append("- **Crédit à reproduire** — %s" % d["credit"])
    return "\n".join(lignes)


# ═══════════════════════════════════════════════════════════════════════════
# 1. MODÈLES REMARQUABLES
# ═══════════════════════════════════════════════════════════════════════════

def md_modeles(d=None):
    m = d or observatoire_ia.SEED["modeles"]
    pays = m.get("pays") or {}
    # Rangés par classe décroissante, puis par nom : un tableau non trié oblige
    # le lecteur à faire lui-même le classement que la carte lui montrait.
    classes = list(m.get("classes") or [])
    rang = {c: i for i, c in enumerate(classes)}
    ordre = sorted(pays.items(),
                   key=lambda kv: (-rang.get(kv[1].get("classe"), -1), kv[0]))
    lignes = [(nom, v.get("classe") or "n. d.", v.get("precision") or "")
              for nom, v in ordre]
    lus = [n for n, v in ordre if "lecture" in (v.get("precision") or "")]
    return "\n\n".join([
        "## 1. Modèles d'IA remarquables — cumul par pays",
        "![Carte des modèles d'IA remarquables par pays, en cinq classes]"
        "(fig:carte-modeles)",
        "Le référentiel publie des **classes**, pas des comptes. Un pays de la "
        "classe « %s » n'est pas comparable à l'unité près avec un autre de la "
        "même classe, et l'écart entre deux classes voisines n'est pas une "
        "différence chiffrée : c'est un changement d'ordre de grandeur."
        % (classes[-1] if classes else "la plus haute"),
        _tab(("Pays", "Classe (nombre de modèles)", "Précision"), lignes),
        ("**Lecture de carte pour %d pays.** Leur classe a été relevée sur la "
         "carte de la source, non publiée sous forme de nombre : %s. Ces lignes "
         "situent, elles ne mesurent pas."
         % (len(lus), ", ".join(lus))) if lus else "",
        _bloc_source(m),
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 2. BREVETS
# ═══════════════════════════════════════════════════════════════════════════

def md_brevets(d=None):
    b = d or observatoire_ia.SEED["brevets"]
    parts = b.get("parts_pct") or {}
    vol = b.get("volume_mondial_milliers") or {}
    annees = sorted(parts.get("Chine", {}), key=int)
    acteurs = ("Chine", "États-Unis", "Europe")

    lignes = []
    for a in annees:
        trois = sum(parts[p][a] for p in acteurs if a in parts.get(p, {}))
        reste = round(100 - trois, 1)
        v = vol.get(a)
        lignes.append([a] + [_fr(parts[p].get(a)) for p in acteurs]
                      + [_fr(reste), _fr(v) if v is not None else "n. d.",
                         _fr(round(parts["Chine"][a] / 100.0 * v, 1)) if v else "n. d."])
    # Le facteur de croissance, calculé et non recopié : c'est le chiffre que la
    # vue en parts fait passer pour un effondrement.
    a0, a1 = annees[0], annees[-1]
    fact = {}
    for p in acteurs:
        d0 = parts[p][a0] / 100.0 * vol[a0]
        d1 = parts[p][a1] / 100.0 * vol[a1]
        fact[p] = round(d1 / d0) if d0 else None
    return "\n\n".join([
        "## 2. Brevets d'IA accordés — part du monde et volume",
        "![Brevets d'IA accordés — vue affichée à l'écran](fig:brevets)",
        "**Deux lectures d'un même relevé, et elles ne disent pas la même "
        "chose.** En PART, l'Europe passe de %s %% à %s %% du total mondial. En "
        "VOLUME, elle est multipliée par %s sur la même période — parce que le "
        "gâteau, lui, a été multiplié par %d. Une part qui baisse peut recouvrir "
        "un nombre qui monte, et c'est exactement ce qui se produit ici : la "
        "Chine a grandi %d fois plus vite que l'Europe, elle n'a pas pris sa "
        "place."
        % (_fr(parts["Europe"][a0]), _fr(parts["Europe"][a1]), fact["Europe"],
           round(vol[a1] / vol[a0]),
           round(fact["Chine"] / float(fact["Europe"]))),
        _tab(("Année", "Chine %", "États-Unis %", "Europe %", "Reste %",
              "Monde (milliers)", "Chine (milliers, déduit)"), lignes),
        "**Facteurs de croissance %s-%s, en volume :** Chine ×%s, États-Unis "
        "×%s, Europe ×%s."
        % (a0, a1, fact["Chine"], fact["États-Unis"], fact["Europe"]),
        "**Ce que ces volumes valent.** Ils sont DÉDUITS : part du monde × "
        "volume mondial de l'année. Les deux séries d'entrée portent leur propre "
        "incertitude — parts en lecture graphique jusqu'en 2022, volume mondial "
        "en lecture graphique. Ce sont des ordres de grandeur, à ne pas citer "
        "comme des comptes officiels.",
        _bloc_source(b),
        "> **Pas de dérivée.** Cette source est publiée sous CC BY-ND 4.0 : les "
        "chiffres se citent avec le crédit exact ci-dessus, et les figures de ce "
        "document sont des vues RECOMPOSÉES depuis les données, non des "
        "reproductions du rapport.",
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 3. CHERCHEURS D'ÉLITE
# ═══════════════════════════════════════════════════════════════════════════

def md_talents(d=None):
    t = d or observatoire_ia.SEED["talents"]
    ori = t.get("origine_pct") or {}
    tra = t.get("lieu_travail_pct") or {}

    def solde(p):
        return (tra[p] - ori[p]) if (p in tra and p in ori) else None

    ordre = sorted(ori, key=lambda p: (solde(p) is None,
                                       -(solde(p) if solde(p) is not None else 0),
                                       -ori[p]))
    lignes = []
    for p in ordre:
        s = solde(p)
        lignes.append([p, _fr(ori[p]),
                       _fr(tra[p]) if p in tra else "non publié",
                       ("+" if s and s > 0 else "−" if s and s < 0 else "")
                       + _fr(abs(s)) if s is not None else "—"])
    muets = [p for p in ordre if solde(p) is None]
    return "\n\n".join([
        "## 3. Chercheurs d'élite en IA — origine et lieu de travail",
        "![Chercheurs d'élite en IA — vue affichée à l'écran](fig:talents)",
        "**Le solde est l'information.** Les États-Unis forment %s %% des "
        "chercheurs d'élite et en emploient %s %% — %+d points, la plus forte "
        "attraction nette. La Chine en forme %s %% et n'en emploie que %s %% — "
        "%+d points."
        % (_fr(ori["États-Unis"]), _fr(tra["États-Unis"]), solde("États-Unis"),
           _fr(ori["Chine"]), _fr(tra["Chine"]), solde("Chine")),
        _tab(("Pays", "Formés %", "Y travaillent %", "Solde (points)"), lignes),
        "**%d pays sur %d n'ont pas de solde.** Le lieu de travail n'est pas "
        "publié pour eux : %s. Une soustraction exige ses deux termes — ils "
        "n'ont donc pas de valeur plutôt qu'une valeur nulle, qui les dirait "
        "« à l'équilibre » sans qu'aucune source l'affirme."
        % (len(muets), len(ordre), ", ".join(muets)),
        "**Définition.** %s" % t.get("definition", ""),
        (("**Note de la source.** %s" % t["note_lieu_travail"])
         if t.get("note_lieu_travail") else ""),
        _bloc_source(t),
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 4. ADOPTION PAR LES ENTREPRISES
# ═══════════════════════════════════════════════════════════════════════════

def md_adoption(d=None):
    a = d or observatoire_ia.SEED["adoption_ue"]
    vals = a.get("valeurs") or {}
    lignes = [(k, _fr(v) + " %") for k, v in
              sorted(vals.items(), key=lambda kv: -(kv[1] or 0))]
    return "\n\n".join([
        "## 4. Adoption de l'IA par les entreprises de l'Union",
        "Part des entreprises déclarant utiliser au moins une technologie d'IA, "
        "enquête TIC entreprises (%s)." % (a.get("annee") or a.get("date") or ""),
        _tab(("Périmètre", "Entreprises utilisant l'IA"), lignes),
        (("**Réserve.** %s" % a["note"]) if a.get("note") else ""),
        _bloc_source(a),
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 5. CADRE ET GOUVERNANCE
# ═══════════════════════════════════════════════════════════════════════════

def md_gouvernance(d=None):
    g = d or observatoire_ia.SEED["gouvernance"]
    blocs = ["## 5. Cadre et gouvernance de l'Union"]
    for e in (g.get("entrees") or []):
        blocs.append("### %s (%s)" % (e.get("titre", ""), e.get("annee", "")))
        if e.get("usage"):
            blocs.append(e["usage"])
        liens = ([e["lien"]] if e.get("lien") else []) + list(e.get("liens_annexes") or [])
        if liens:
            blocs.append("\n".join("- %s" % u for u in liens))
    blocs.append(_bloc_source(g))
    return "\n\n".join(blocs)


# ═══════════════════════════════════════════════════════════════════════════
# ASSEMBLAGE
# ═══════════════════════════════════════════════════════════════════════════

def md_credits(d=None):
    cr = d or observatoire_ia.SEED.get("credits") or []
    return "\n\n".join([
        "## 6. Crédits et conditions de réutilisation",
        "Chaque source ci-dessous impose son propre crédit. Ils sont reproduits "
        "tels quels : les abréger reviendrait à ne plus respecter la licence "
        "sous laquelle la donnée nous a été confiée.",
        "\n".join("- %s" % c for c in cr),
        "Ce document est produit par calcul déterministe à partir du "
        "référentiel `observatoire_ia` version %s. Aucun modèle de langage n'est "
        "intervenu dans sa rédaction." % VERSION,
    ])


def _entete(dossier):
    d = DOSSIERS[dossier]
    s = observatoire_ia.SEED
    refs = "observatoire_ia %s · export_observatoire %s" % (
        s.get("version") or VERSION, VERSION)
    return {"label": d["nom"], "perimetre": d["resume"],
            "date": _horodatage(), "referentiel": refs}


# Ce que le document doit porter, sans exception. Un dossier amputé de ses
# réserves circule mieux qu'un dossier complet — c'est précisément le risque.
EXIGENCES = (
    ("la licence sans dérivée des brevets", "CC BY-ND"),
    ("le crédit Epoch AI", "Epoch AI"),
    ("le crédit MacroPolo", "MacroPolo"),
    ("la mention des pays sans solde", "n'ont pas de solde"),
    ("l'avertissement sur les volumes déduits", "DÉDUITS"),
    ("la distinction classe / mesure", "classes**, pas des comptes"),
)


def _verifier(md):
    manque = [nom for nom, marqueur in EXIGENCES if marqueur not in md]
    if manque:
        raise RuntimeError("dossier incomplet, il manque : %s" % ", ".join(manque))
    return md


# La FORME attendue de chaque section, quand un appelant en fournit une. La
# page, elle, n'en fournit pas : son objet `DATA` est un modèle d'AFFICHAGE —
# les pays y sont une liste de points à projeter, pas un dictionnaire de
# classes — et le lire comme le référentiel produisait un document à moitié
# compris. Une section dont la forme n'est pas reconnue est IGNORÉE, jamais
# devinée : le chapitre se compose alors depuis le référentiel, ce que le
# lecteur ne peut pas distinguer puisque c'est la même source.
FORMES = {
    "modeles": ("pays", dict),
    "brevets": ("parts_pct", dict),
    "talents": ("origine_pct", dict),
    "adoption_ue": ("valeurs", dict),
    "gouvernance": ("entrees", list),
}


def utilisables(donnees):
    """Ne garde que les sections dont la forme est celle du référentiel."""
    d = donnees if isinstance(donnees, dict) else {}
    bon, refuses = {}, []
    for cle, (champ, typ) in FORMES.items():
        v = d.get(cle)
        if v is None:
            continue
        if isinstance(v, dict) and isinstance(v.get(champ), typ) and v.get(champ):
            bon[cle] = v
        else:
            refuses.append(cle)
    return bon, refuses


def composer(dossier="observatoire", donnees=None):
    """Le Markdown du dossier. Un seul point d'entrée : le Word et le PDF
    partent du même texte, ils ne peuvent donc pas diverger.

    `donnees` permet de composer à partir de l'état LIVE servi à la page plutôt
    que du seed — sans quoi le document contredirait l'écran."""
    if dossier not in DOSSIERS:
        raise ValueError("dossier inconnu : %s" % dossier)
    d, _refuses = utilisables(donnees)
    md = "\n\n".join([
        md_modeles(d.get("modeles")),
        md_brevets(d.get("brevets")),
        md_talents(d.get("talents")),
        md_adoption(d.get("adoption_ue")),
        md_gouvernance(d.get("gouvernance")),
        md_credits(d.get("credits")),
    ])
    return _verifier(md)


def produire(dossier, fmt, figures=None, donnees=None):
    """Renvoie (octets, type MIME, nom de fichier)."""
    import livrables_export
    if fmt not in FORMATS:
        raise ValueError("format inconnu : %s" % fmt)
    md = composer(dossier, donnees)
    meta = dict(MARQUE)
    meta.update(_entete(dossier))
    meta["figures"] = figures or {}
    jour = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    nom = "CONSEILPREV-observatoire-ia-%s.%s" % (jour, fmt)
    if fmt == "docx":
        return (livrables_export.build_docx(md, meta),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                nom)
    return livrables_export.build_pdf(md, meta), "application/pdf", nom


def catalogue():
    return {"version": VERSION, "formats": list(FORMATS),
            "figures": [{"cle": k, "legende": v} for k, v in FIGURES],
            "dossiers": [dict(cle=k, **v) for k, v in DOSSIERS.items()]}


def sante():
    try:
        md = composer("observatoire")
        pb = []
    except Exception as e:                                    # noqa: BLE001
        md, pb = "", [str(e)]
    return {"module": "export_observatoire", "version": VERSION,
            "dossiers": len(DOSSIERS), "formats": list(FORMATS),
            "figures": len(FIGURES),
            "signes": len(md), "problemes": pb,
            "horodatage": datetime.now(timezone.utc).isoformat(timespec="seconds")}
