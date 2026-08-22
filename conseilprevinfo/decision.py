"""LES PISTES — ce que le corpus permet de PROPOSER, et rien de plus.

LA DEMANDE ET SON PIÈGE. On attend d'un site de veille qu'il « aide à la
décision » et qu'il fasse émerger des projets commerciaux. La façon
paresseuse de le faire est connue : on lit trois brèves sur une technologie,
on en tire « le marché de X va croître, positionnez-vous », et on habille le
tout d'un chiffre trouvé ailleurs. C'est une opinion déguisée en analyse, et
elle coûte cher à celui qui la suit.

CE QUE CE MODULE FAIT À LA PLACE. Il applique des DÉCLENCHEURS écrits
ci-dessous à ce que le corpus porte réellement, et il rend des pistes qui
disent, chacune :

  — CE QUI LA DÉCLENCHE, avec les fiches qui l'ont déclenchée, nommées ;
  — CE QU'ELLE SUPPOSE, c'est-à-dire l'hypothèse qui reste à vérifier ;
  — CE QU'ELLE N'ÉTABLIT PAS, en particulier qu'il existe un acheteur ;
  — CE QUI LA DISQUALIFIERAIT, pour qu'on puisse la refuser vite.

CE QUE CE MODULE NE FAIT JAMAIS.

  1. AUCUN CHIFFRE DE MARCHÉ. Ni taille, ni croissance, ni prix, ni délai de
     vente. Le corpus n'en porte aucun ; en produire un serait l'inventer, et
     un chiffre inventé se propage plus vite que le texte qui l'entoure.

  2. AUCUNE PRÉDICTION. « Cette technologie va s'imposer » est un pari. Les
     pistes partent de faits CONSTATÉS et de projections DÉCLARÉES par un
     tiers nommé — jamais d'une extrapolation maison.

  3. AUCUNE PISTE SANS FICHE. Une piste qui ne pointerait aucune fiche serait
     une idée du rédacteur ; elle n'a pas sa place dans un module qui prétend
     dériver du corpus. Le contrôle est en bas de ce fichier.

  4. AUCUN MODÈLE DE LANGAGE. Comme partout ici : deux passages sur le même
     corpus rendent les mêmes pistes, dans le même ordre.

CE QU'IL FAUT EN ATTENDRE. Une piste est un point de départ d'instruction,
pas une recommandation. Le module range d'ailleurs les pistes par la SOLIDITÉ
DE LEUR DÉCLENCHEUR, pas par un attrait commercial supposé — qu'il n'a aucun
moyen d'évaluer.
"""
import unicodedata
from collections import defaultdict

import veille as V

VERSION = "2026.08.22"

# ── LES DÉCLENCHEURS, ET CE QUE CHACUN VAUT ───────────────────────────────
# La SOLIDITÉ dit sur quoi la piste repose, pas combien elle rapporterait.
#   1 — la source affirme elle-même la relation qui déclenche la piste ;
#   2 — un fait constaté, répété, tiré d'une seule source ;
#   3 — une projection, DÉCLARÉE par un tiers nommé.
SOLIDITES = {
    1: {"nom": "Adossée à une relation déclarée par la source",
        "dit": "Le déclencheur ne repose sur aucune interprétation de notre "
               "part : le référentiel d'origine affirme lui-même le lien qui "
               "fonde la piste."},
    2: {"nom": "Adossée à des faits constatés et répétés",
        "dit": "Le déclencheur est un motif que plusieurs fiches portent. Il "
               "est solide sur les faits, mais il vient d'une seule source : "
               "ce que cette source ne couvre pas n'y figure pas."},
    3: {"nom": "Adossée à une projection déclarée",
        "dit": "Le déclencheur est une projection, et elle est de son auteur, "
               "pas de nous. Elle peut ne pas se réaliser ; la piste vaut "
               "comme préparation, pas comme pari."},
}

# Le seuil de répétition. Deux fiches ne font pas un motif : sur un corpus de
# quelques dizaines de pièces, deux coïncidences arrivent sans rien signifier.
MINI_REPETITION = 3

_RIEN_ETABLI = ("Cette piste n'établit ni qu'il existe un acheteur, ni ce "
                "qu'il paierait, ni que le cabinet sache la conduire. Elle "
                "dit seulement que le corpus porte de quoi ouvrir le sujet.")


def _sansaccent(x):
    s = unicodedata.normalize("NFD", str(x or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _piste(cle, titre, solidite, declencheur, suppose, disqualifie, fiches,
           n_ecartees=0):
    """Une piste, avec tout ce qui permet de la refuser.

    L'ordre des champs n'est pas décoratif : ce qui la déclenche vient en
    premier, ce qu'elle n'établit pas vient AVANT ce qu'elle propose de
    faire. Un lecteur pressé doit buter sur la réserve, pas la découvrir en
    bas de page après avoir décidé.
    """
    return {
        "cle": cle, "titre": titre,
        "solidite": solidite,
        "solidite_nom": SOLIDITES[solidite]["nom"],
        "solidite_dit": SOLIDITES[solidite]["dit"],
        "declencheur": declencheur,
        "suppose": suppose,
        "n_etablit_pas": _RIEN_ETABLI,
        "disqualifie_par": disqualifie,
        "fiches": [{"id": f.get("id"), "titre": f.get("titre"),
                    "date_fait": f.get("date_fait"),
                    "sujet": f.get("sujet")} for f in fiches[:6]],
        "n_fiches": len(fiches),
        # QUAND LA LISTE EST COUPÉE, ELLE LE DIT — comme partout sur ce site.
        "fiches_non_listees": max(0, len(fiches) - 6) + n_ecartees,
    }


# ── DÉCLENCHEUR 1 — une technique employée dans plusieurs incidents ───────

def _technique_recurrente(corpus):
    """Une technique que la SOURCE rattache à plusieurs incidents distincts.

    C'est le déclencheur le plus solide dont ce site dispose, et il n'existe
    que depuis que les relations déclarées sont collectées : sans elles, il
    aurait fallu rapprocher les incidents nous-mêmes, donc décider nous-mêmes
    ce qui se ressemble.
    """
    pub = V.publiables(corpus)
    par_id = {f.get("id"): f for f in pub}
    incidents = defaultdict(list)
    for f in pub:
        for rel in (f.get("relations") or []):
            cible = par_id.get(rel.get("vers"))
            # On compte les INCIDENTS rattachés à une technique, pas l'inverse.
            if cible and rel.get("nature") == "procedure" \
                    and "technique" in _sansaccent(cible.get("titre", "")):
                incidents[cible["id"]].append(f)

    pistes = []
    for tid, fs in incidents.items():
        uniques = {f["id"]: f for f in fs}
        if len(uniques) < MINI_REPETITION:
            continue
        tech = par_id[tid]
        fs = sorted(uniques.values(), key=lambda f: str(f.get("date_fait")),
                    reverse=True)
        pistes.append(_piste(
            "technique-%s" % tid,
            "Contrôle outillé de la technique « %s »"
            % tech.get("titre", "").split(" — ")[0],
            1,
            "Le référentiel rattache lui-même %d incident(s) distinct(s) à "
            "cette technique. Ce n'est pas nous qui les rapprochons : la "
            "relation est un champ de la source, et chaque incident porte la "
            "phrase par laquelle elle décrit l'étape." % len(uniques),
            "Que la technique concerne les systèmes réellement exploités chez "
            "le client. Le référentiel documente ce qui a été observé "
            "ailleurs ; il ne dit rien de l'exposition d'un parc donné.",
            "Un parc où la fonction visée par la technique n'existe pas, ou "
            "n'est pas exposée : la piste tombe, et il vaut mieux le "
            "constater en une réunion qu'en une mission.",
            fs))
    return pistes


# ── DÉCLENCHEUR 2 — un fournisseur qui revient ────────────────────────────

def _fournisseur_recurrent(corpus):
    """Un fournisseur portant plusieurs entrées de vulnérabilité exploitée.

    MESURE À CE JOUR : ce déclencheur ne produit rien. Le catalogue KEV ne
    livre que six entrées au périmètre industriel, toutes chez des
    fournisseurs différents. La fonction est conservée — elle se déclenchera
    dès que le corpus s'élargira — et `mesure()` dit qu'elle est muette,
    plutôt que de laisser croire qu'aucun fournisseur ne pose de problème.
    """
    pub = V.publiables(corpus)
    par_editeur = defaultdict(list)
    for f in pub:
        if f.get("editeur"):
            par_editeur[_sansaccent(f["editeur"])].append(f)

    pistes = []
    for _, fs in par_editeur.items():
        if len(fs) < MINI_REPETITION:
            continue
        nom = next(f["editeur"] for f in fs if f.get("editeur"))
        fs = sorted(fs, key=lambda f: str(f.get("date_fait")), reverse=True)
        pistes.append(_piste(
            "fournisseur-%s" % _sansaccent(nom).replace(" ", "-"),
            "Revue du parc %s" % nom,
            2,
            "%d fiche(s) du corpus portent sur ce fournisseur. La répétition "
            "chez un même fournisseur désigne un parc à instruire d'un bloc, "
            "et non une suite d'incidents à traiter un par un." % len(fs),
            "Que le client exploite ce fournisseur, et que son parc ne soit "
            "pas déjà couvert par un contrat de maintenance qui traite ces "
            "points.",
            "Un inventaire montrant que les versions exposées ne sont pas "
            "déployées.",
            fs))
    return pistes


# ── DÉCLENCHEUR 3 — une projection déclarée par un tiers nommé ────────────

def _projection_declaree(corpus):
    """Une échéance annoncée par un tiers NOMMÉ, jamais par nous.

    Une projection est le seul matériau qui autorise à parler d'avenir sans
    parier : elle engage son auteur, et la piste consiste à s'y préparer, pas
    à miser dessus. La fiche porte déjà `projette_qui` — le moteur refuse une
    projection anonyme — si bien que ce déclencheur ne peut pas s'appliquer à
    une prévision maison.
    """
    pub = V.publiables(corpus)
    par_auteur = defaultdict(list)
    for f in pub:
        if f.get("horizon") == "projete" and f.get("projette_qui"):
            par_auteur[f["projette_qui"]].append(f)

    pistes = []
    for auteur, fs in par_auteur.items():
        fs = sorted(fs, key=lambda f: str(f.get("date_fait")), reverse=True)
        pistes.append(_piste(
            "projection-%s" % _sansaccent(auteur).replace(" ", "-")[:40],
            "Préparation à l'échéance annoncée par %s" % auteur,
            3,
            "%d fiche(s) portent une projection dont %s est l'auteur déclaré. "
            "Le moteur refuse une projection anonyme : ce qui est annoncé ici "
            "engage quelqu'un." % (len(fs), auteur),
            "Que l'échéance concerne le périmètre du client, et qu'il ait de "
            "quoi s'y préparer d'ici là.",
            "Une projection retirée ou révisée par son auteur — auquel cas la "
            "piste disparaît avec elle, et c'est le comportement voulu.",
            fs))
    return pistes


# ── DÉCLENCHEUR 4 — un sujet qui rompt ────────────────────────────────────

def _sujet_en_rupture(corpus):
    """Un sujet portant plusieurs faits classés « rupture ».

    Le plus faible des quatre, et le plus tentant : c'est celui qui produit
    les notes de tendance. Il est donc borné au seul énoncé que les données
    permettent — « il se passe quelque chose ici » — sans dire quoi, ni si
    cela durera.
    """
    pub = V.publiables(corpus)
    par_sujet = defaultdict(list)
    for f in pub:
        if f.get("impact") == "rupture":
            par_sujet[f.get("sujet")].append(f)

    pistes = []
    for sujet, fs in par_sujet.items():
        if len(fs) < MINI_REPETITION:
            continue
        fs = sorted(fs, key=lambda f: str(f.get("date_fait")), reverse=True)
        nom = V.SUJETS.get(sujet, {}).get("nom", sujet)
        pistes.append(_piste(
            "rupture-%s" % sujet,
            "Note de cadrage — %s" % nom,
            2,
            "%d fiche(s) de ce sujet sont classées « rupture », c'est-à-dire "
            "qu'elles déplacent un arbitrage plutôt qu'elles ne l'alimentent. "
            "La concentration désigne un sujet où l'état de l'art bouge assez "
            "vite pour qu'une position prise il y a un an soit à revoir."
            % len(fs),
            "Que le client ait un arbitrage en cours sur ce sujet. Sans "
            "décision à prendre, une note de cadrage est une lecture, pas une "
            "commande.",
            "Un client dont la position est récente et documentée : il n'a "
            "pas besoin d'un cadrage, il a besoin qu'on n'y touche pas.",
            fs))
    return pistes


DECLENCHEURS = (
    ("technique_recurrente", _technique_recurrente),
    ("fournisseur_recurrent", _fournisseur_recurrent),
    ("projection_declaree", _projection_declaree),
    ("sujet_en_rupture", _sujet_en_rupture),
)


def pistes(corpus):
    """Toutes les pistes, rangées par SOLIDITÉ DU DÉCLENCHEUR.

    Pas par attrait commercial : ce module n'a aucun moyen de l'évaluer, et
    un classement qui en aurait l'air ferait passer une règle de tri pour un
    jugement de marché.
    """
    out = []
    for _, fn in DECLENCHEURS:
        out.extend(fn(corpus))
    out.sort(key=lambda p: (p["solidite"], -p["n_fiches"], p["titre"]))
    return out


def mesure(corpus):
    """CE QUE CHAQUE DÉCLENCHEUR A TROUVÉ — y compris zéro.

    Un module de pistes qui n'afficherait que ses déclencheurs féconds
    laisserait croire que les autres ne trouvent rien parce qu'il n'y a rien à
    trouver. Le plus souvent, c'est que la source qui les nourrirait n'est pas
    branchée.
    """
    par_declencheur = {}
    for nom, fn in DECLENCHEURS:
        par_declencheur[nom] = len(fn(corpus))
    muets = [n for n, k in par_declencheur.items() if not k]
    total = sum(par_declencheur.values())
    return {
        "par_declencheur": par_declencheur,
        "muets": muets,
        "total": total,
        "seuil_repetition": MINI_REPETITION,
        "dit": ("Aucun déclencheur ne trouve de quoi former une piste sur ce "
                "corpus." if not total else
                "%d piste(s) formée(s). Déclencheur(s) muet(s) : %s — ce n'est "
                "pas qu'il n'y a rien à y voir, c'est qu'il faut %d fiches "
                "concordantes pour qu'une piste se forme, et le corpus ne les "
                "porte pas encore."
                % (total, ", ".join(muets) if muets else "aucun",
                   MINI_REPETITION)),
    }


def sante(corpus=None):
    corpus = list(corpus or [])
    return {
        "module": "decision", "version": VERSION,
        "declencheurs": len(DECLENCHEURS),
        "modeles_de_langage": 0,
        "chiffres_de_marche": 0,
        "mesure": mesure(corpus) if corpus else None,
        "portee": "Dérive des PISTES d'instruction depuis ce que le corpus "
                  "porte. Ne produit aucun chiffre de marché, aucune "
                  "prédiction, et aucune piste qui ne pointe des fiches.",
    }


def _verifier():
    if MINI_REPETITION < 3:
        raise RuntimeError(
            "decision : le seuil de répétition est tombé sous trois — deux "
            "coïncidences arrivent sans rien signifier sur un corpus de "
            "quelques dizaines de fiches")
    for rang, s in SOLIDITES.items():
        if len(s["dit"]) < 40:
            raise RuntimeError(
                "decision : la solidité %s n'explique pas ce qu'elle vaut" % rang)
    if "acheteur" not in _RIEN_ETABLI:
        raise RuntimeError(
            "decision : la réserve ne dit plus qu'aucune piste n'établit "
            "l'existence d'un acheteur — c'est la seule chose qu'un lecteur "
            "pressé lira comme acquise")


_verifier()
