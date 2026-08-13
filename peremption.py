# -*- coding: utf-8 -*-
"""Ce qui a vieilli — et ce qu'une mise à jour automatique ne peut PAS rajeunir.

LE MALENTENDU QUE CE MODULE EXISTE POUR DISSIPER

« Mettre à jour les données toutes les semaines » se traduit spontanément par :
relancer chaque semaine les fonctions qui assemblent le référentiel. Cette
traduction est fausse, et d'une manière qui coûte cher parce qu'elle rassure.

Le référentiel d'implantation repose sur des tables de constantes : le WEI+ de
l'Agence européenne pour l'environnement, millésime 2022 ; les parts de
production Ember 2024 ; les prix Eurostat 2024. Relancer `assemble()` mille
fois n'y change rien — la valeur servie sera identique, avec un horodatage de
génération tout neuf. On obtiendrait une page qui affiche « mis à jour il y a
trois minutes » sur un stress hydrique de quatre ans. C'est un mensonge que
l'automatisation FABRIQUE, et que l'absence d'automatisation ne produisait pas.

CE QUE LA MISE À JOUR HEBDOMADAIRE PEUT ET NE PEUT PAS

Elle PEUT rafraîchir ce qui vient d'une source interrogée en direct : le mix
électrique, l'empreinte qui en découle, le socle de données ouvertes.

Elle NE PEUT PAS rajeunir ce qui vient d'un rapport. Un rapport ne se met pas à
jour, il est REMPLACÉ — par une édition suivante, à une date que son éditeur
choisit, et que personne ici ne contrôle.

Ce module traite donc la seconde moitié du problème, celle qu'aucune boucle ne
résout : il calcule l'ÂGE RÉEL de chaque famille de valeurs, le compare à la
cadence de publication de son éditeur, et dit ce qui aurait dû être remplacé.
La tâche hebdomadaire ne fait pas semblant de rafraîchir ces valeurs : elle
vérifie si une édition plus récente est due, et le signale.

LA DÉRIVE ENTRE LE MILLÉSIME DÉCLARÉ ET LE TEXTE SERVI

Un âge se calcule sur un millésime déclaré ici. Rien n'empêcherait qu'il
diverge du texte que la page affiche au lecteur — on annoncerait alors la
fraîcheur d'une source, en en citant une autre. Chaque famille porte donc une
PREUVE : une chaîne qui doit se retrouver dans le texte réellement servi. Si
elle n'y est plus, la famille est signalée en dérive, et le module refuse de
prétendre connaître son âge.
"""
import re
from datetime import date, datetime, timezone

VERSION = "2026-08-a"

# Trois verdicts, et un quatrième qui n'est pas un âge.
VERDICTS = {
    "frais": {"nom": "À jour", "rang": 0,
              "sens": "dans la fenêtre de publication de l'éditeur"},
    "a_verifier": {"nom": "À vérifier", "rang": 1,
                   "sens": "une édition plus récente est due — aller voir chez l'éditeur"},
    "perime": {"nom": "Périmé", "rang": 2,
               "sens": "deux cycles de publication ou plus sans remplacement ; "
                       "la valeur reste servie, mais son millésime doit être dit "
                       "au lecteur à chaque usage"},
    "derive": {"nom": "En dérive", "rang": 3,
               "sens": "le millésime déclaré ici ne se retrouve plus dans le texte "
                       "servi — on ne sait plus de quelle édition on parle, et un "
                       "âge calculé là-dessus serait faux"},
}

# ── LE REGISTRE ────────────────────────────────────────────────────────────
# `millesime` : (année, mois) de l'édition servie. Le mois vaut 6 quand
#     l'éditeur publie un millésime annuel sans mois — un choix milieu d'année
#     plutôt que janvier, qui ferait vieillir la donnée six mois trop vite.
# `cadence_mois` : la périodicité RÉELLE de l'éditeur, pas un vœu. L'AEE publie
#     le WEI+ annuellement mais avec deux ans de décalage ; c'est la cadence qui
#     compte, le décalage est déjà dans le millésime.
# `preuve` : ce qui doit se retrouver dans le texte servi au lecteur.
# `vivant` : True si une source interrogée en direct alimente cette famille —
#     auquel cas la tâche hebdomadaire la rafraîchit vraiment.
FAMILLES = {
    "eau": {
        "titre": "Stress hydrique WEI+",
        "millesime": (2022, 6), "cadence_mois": 12, "vivant": False,
        "module": "implantation", "source": "SOURCE_EAU", "preuve": "2022",
        "editeur": "Agence européenne pour l'environnement",
        "quoi_faire": "vérifier la parution d'un millésime plus récent de l'indicateur "
                      "d'exploitation de l'eau, et reprendre les classes nationales",
    },
    "mix": {
        "titre": "Mix de production électrique",
        "millesime": (2024, 12), "cadence_mois": 12, "vivant": False,
        "module": "implantation", "source": "SOURCE_MIX", "preuve": "2024",
        "editeur": "Ember",
        "quoi_faire": "reprendre les parts de production de l'année civile close",
    },
    "prix": {
        "titre": "Prix industriels de l'électricité",
        "millesime": (2024, 12), "cadence_mois": 6, "vivant": False,
        "module": "implantation", "source": "SOURCE_PRIX", "preuve": "2024",
        "editeur": "Eurostat (nrg_pc_205)",
        "quoi_faire": "la série est SEMESTRIELLE : reprendre les bandes hautes du "
                      "dernier semestre publié, et revoir la réserve finlandaise "
                      "sur l'accise supprimée en mars 2025",
    },
    "climat_physique": {
        "titre": "Risque physique des centres planifiés",
        "millesime": (2026, 6), "cadence_mois": 12, "vivant": False,
        "module": "implantation", "source": "SOURCE_XDI", "preuve": "juin 2026",
        "editeur": "XDI (Cross Dependency Initiative)",
        "quoi_faire": "attendre l'édition annuelle suivante du classement mondial",
    },
    "feux": {
        "titre": "Risque de feu de forêt 2050",
        "millesime": (2025, 8), "cadence_mois": 12, "vivant": False,
        "module": "implantation", "source": "SOURCE_FEUX", "preuve": "août 2025",
        "editeur": "XDI",
        "quoi_faire": "vérifier si l'édition suivante élargit le champ au-delà des "
                      "dix premiers États membres — c'est la limite qui prive le "
                      "Royaume-Uni, la Suisse et la Suède de note",
    },
    "inondations": {
        "titre": "Risque d'inondation 2050",
        "millesime": (2025, 9), "cadence_mois": 12, "vivant": False,
        "module": "implantation", "source": "SOURCE_INONDATIONS", "preuve": "septembre",
        "editeur": "XDI",
        "quoi_faire": "vérifier si l'édition suivante sort du périmètre des "
                      "vingt-sept États membres",
    },
    "mer": {
        "titre": "Élévation du niveau de la mer",
        "millesime": (2021, 8), "cadence_mois": 84, "vivant": False,
        "module": "climat_2050", "source": "SOURCE_MER", "preuve": "2021",
        "editeur": "GIEC (IPCC)",
        "quoi_faire": "le cycle d'évaluation du GIEC est d'environ sept ans : "
                      "surveiller l'AR7. Un millésime 2021 n'est PAS périmé ici — "
                      "c'est le rythme de la source, et la seule qui fasse autorité",
    },
    "aleas": {
        "titre": "Classes d'exposition aux aléas climatiques",
        "millesime": (2026, 8), "cadence_mois": 12, "vivant": False,
        "module": "climat_2050", "source": "SOURCE_ALEAS", "preuve": "GIEC AR6",
        "editeur": "Synthèse CONSEILPREV",
        "quoi_faire": "relire la synthèse à chaque parution d'un rapport majeur — "
                      "évaluation européenne des risques climatiques, PESETA, AR7",
    },
    "nappes": {
        "titre": "État des nappes phréatiques françaises",
        # LA FAMILLE QUI VIEILLIT LE PLUS VITE DE TOUTES, avec les perspectives.
        # Un état piézométrique est un INSTANTANÉ pris au creux de l'année : il
        # ne décrit ni l'automne ni le printemps suivant. Trois mois est déjà
        # généreux — c'est la cadence de publication des bulletins, pas la durée
        # de validité d'une décision d'implantation.
        "millesime": (2026, 8), "cadence_mois": 3, "vivant": False,
        "module": "nappes_fr", "source": "SOURCE", "preuve": "1er août 2026",
        "editeur": "BRGM",
        "quoi_faire": "reprendre le bulletin de situation hydrologique à chaque "
                      "parution. Un état d'août ne se prolonge PAS en octobre : "
                      "la recharge d'automne le change, et son absence encore "
                      "davantage",
    },
    "perspectives": {
        "titre": "Annonces et jalons réglementaires 2026-2030",
        "millesime": (2026, 8), "cadence_mois": 3, "vivant": False,
        "module": "implantation", "source": "SOURCE_PERSPECTIVES", "preuve": "",
        "editeur": "Compilation du cabinet",
        "quoi_faire": "c'est la famille qui vieillit le plus vite : un moratoire "
                      "levé ou un projet abandonné périme une entrée en quelques "
                      "semaines. Relecture trimestrielle au minimum",
    },
    "intensites": {
        "titre": "Intensité carbone du réseau, en direct",
        "millesime": None, "cadence_mois": 0, "vivant": True,
        "module": "empreinte_sites", "source": None, "preuve": "",
        "editeur": "sources temps réel + Ember en repli",
        "quoi_faire": "rafraîchie par la boucle rapide ; rien à faire à la main",
    },
    "socle_ouvert": {
        "titre": "Socle de données ouvertes",
        "millesime": None, "cadence_mois": 0, "vivant": True,
        "module": "donnees_ouvertes", "source": None, "preuve": "",
        "editeur": "portails publics interrogés",
        "quoi_faire": "rafraîchi par la boucle lente ; rien à faire à la main",
    },
    "parc": {
        "titre": "Référentiel des sites",
        "millesime": (2026, 8), "cadence_mois": 3, "vivant": False,
        "module": "datacentres", "source": None, "preuve": "",
        "editeur": "Relevé du cabinet",
        "quoi_faire": "reprendre les statuts (annoncé → en construction → en service) "
                      "et les horizons d'ouverture ; c'est ce qui fait bouger le "
                      "pipeline et le curseur d'années",
    },
}


def _mois_ecoules(millesime, aujourdhui):
    a, m = millesime
    return (aujourdhui.year - a) * 12 + (aujourdhui.month - m)


def _texte_source(famille):
    """Le texte RÉELLEMENT servi au lecteur pour cette famille, ou None si la
    famille n'en a pas — les familles vivantes n'ont pas de rapport."""
    f = FAMILLES[famille]
    if not f.get("source"):
        return None
    try:
        mod = __import__(f["module"])
        s = getattr(mod, f["source"])
    except Exception:                                            # noqa: BLE001
        return None
    return " ".join(str(v) for v in s.values())


def etat_famille(cle, aujourdhui=None):
    """L'âge d'une famille, son verdict, et ce qu'il y a à faire."""
    f = FAMILLES[cle]
    j = aujourdhui or date.today()
    base = {"cle": cle, "titre": f["titre"], "editeur": f["editeur"],
            "vivant": f["vivant"], "quoi_faire": f["quoi_faire"],
            "module": f["module"]}

    # Les familles vivantes n'ont pas d'âge : elles ont une dernière réussite,
    # que la boucle connaît et que ce module n'a pas à deviner.
    if f["vivant"]:
        return dict(base, verdict="frais", millesime=None, age_mois=None,
                    retard_mois=None,
                    lecture="rafraîchie en direct — l'âge se lit sur la boucle, "
                            "pas sur un millésime")

    # LA DÉRIVE se teste AVANT l'âge : un âge calculé sur un millésime qui ne
    # correspond plus au texte servi serait un chiffre faux, pas une alerte.
    txt = _texte_source(cle)
    if f["preuve"] and txt is not None and f["preuve"] not in txt:
        return dict(base, verdict="derive", millesime=list(f["millesime"]),
                    age_mois=None, retard_mois=None,
                    lecture="le millésime déclaré (%s) ne se retrouve plus dans le "
                            "texte servi : on ne sait plus de quelle édition on parle"
                            % f["preuve"])

    age = _mois_ecoules(f["millesime"], j)
    cad = f["cadence_mois"] or 12
    retard = age - cad
    verdict = "frais" if age < cad else ("a_verifier" if age < 2 * cad else "perime")
    return dict(base, verdict=verdict, millesime=list(f["millesime"]),
                age_mois=age, cadence_mois=cad, retard_mois=max(0, retard),
                lecture=("publiée il y a %d mois ; l'éditeur publie tous les %d mois"
                         % (age, cad))
                        + ("" if verdict == "frais"
                           else " — %d mois de retard sur le cycle" % retard))


def etat(aujourdhui=None):
    """Le registre entier, le plus urgent d'abord."""
    j = aujourdhui or date.today()
    lignes = [etat_famille(c, j) for c in FAMILLES]
    lignes.sort(key=lambda x: (-VERDICTS[x["verdict"]]["rang"],
                               -(x["retard_mois"] or 0), x["cle"]))
    compte = {v: sum(1 for l in lignes if l["verdict"] == v) for v in VERDICTS}
    return {
        "version": VERSION,
        "genere": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "jour": j.isoformat(),
        "verdicts": VERDICTS,
        "familles": lignes,
        "compte": compte,
        "a_traiter": [l["cle"] for l in lignes if l["verdict"] != "frais"],
        # Ce que la boucle rafraîchit VRAIMENT, opposé à ce qu'elle ne peut pas.
        "vivantes": [l["cle"] for l in lignes if l["vivant"]],
        "figees": [l["cle"] for l in lignes if not l["vivant"]],
        "avertissement":
            "Une tâche hebdomadaire rafraîchit les familles VIVANTES — celles qui "
            "viennent d'une source interrogée. Les autres reposent sur des rapports : "
            "un rapport ne se met pas à jour, il est remplacé par son édition "
            "suivante, à une date que son éditeur choisit. Pour celles-là, la tâche "
            "ne rafraîchit rien : elle dit ce qui aurait dû l'être.",
    }


def sante():
    e = etat()
    pb = []
    d = [l["cle"] for l in e["familles"] if l["verdict"] == "derive"]
    if d:
        pb.append("millésime en dérive : %s" % ", ".join(d))
    p = [l["cle"] for l in e["familles"] if l["verdict"] == "perime"]
    if p:
        pb.append("%d famille(s) périmée(s) : %s" % (len(p), ", ".join(p)))
    return {"module": "peremption", "version": VERSION,
            "familles": len(FAMILLES),
            "vivantes": len(e["vivantes"]), "figees": len(e["figees"]),
            "compte": e["compte"], "a_traiter": e["a_traiter"],
            "problemes": pb}
