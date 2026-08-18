# -*- coding: utf-8 -*-
"""Toutes les sources de la page, RÉCOLTÉES sur les modules qui les déclarent.

POURQUOI CE MODULE EXISTE.

La page portait, en fin de parcours, une liste de sources écrite à la main :
sept constantes, quatre textes, six jeux de données. Pendant ce temps les
modules en déclaraient vingt et une, et le registre de vérification en citait
seize de plus. Une liste écrite à la main ne se trompe pas le jour où on
l'écrit : elle se trompe le jour où quelqu'un ajoute une source ailleurs, et
personne ne s'en aperçoit — c'est exactement le défaut que ce dépôt traque
partout ailleurs, et il l'avait chez lui.

Ce module ne contient donc AUCUNE source. Il va les chercher là où elles sont
déclarées, avec leur éditeur, leur millésime et leur lien. Ajouter une source
à un moteur suffit à la faire paraître ici ; en retirer une l'en retire. Rien
à tenir à jour.

CE QU'IL MESURE, ET QUI DÉRANGE UN PEU.

Toutes les sources ne portent pas de lien. Certaines sont des synthèses du
cabinet — légitimes, mais elles ne renvoient à aucune publication ; d'autres
citent un éditeur sans son adresse. Le registre COMPTE ces cas au lieu de les
lisser : un lecteur qui vient chercher des sources vérifiables doit savoir,
avant de lire, quelle part de ce qu'on lui montre il peut réellement rouvrir.

CE QU'IL NE FAIT PAS. Il ne va pas chercher les pages en ligne pour vérifier
qu'elles répondent. Un lien mort serait annoncé comme vivant — la limite est
écrite dans la réponse, elle n'est pas cachée.
"""
from datetime import datetime, timezone

VERSION = "2026-08-a"

# Les modules interrogés. La liste est courte et explicite : parcourir
# l'ensemble du dépôt ramasserait des sources d'outils internes qui n'ont
# rien à faire dans un registre destiné au lecteur.
MODULES = (
    ("implantation", "Choix d'implantation"),
    ("climat_2050", "Aléas climatiques"),
    ("empreinte_sites", "Empreinte du parc"),
    ("eau_dc", "Eau et refroidissement"),
    ("finance_dc", "Enveloppe et DPGF"),
    ("equipements_it", "Équipements informatiques"),
    ("kpi_finance", "Indicateurs financiers"),
    ("nappes_fr", "Nappes et foncier"),
    ("tendances_dc", "Tendances et prospective"),
    ("moe_dc", "Maîtrise d'œuvre"),
    ("donnees_ouvertes", "Socle de données ouvertes"),
)

# Les clés sous lesquelles un module peut nommer l'adresse d'une source. Trois
# noms coexistent dans le dépôt ; en retenir un seul aurait fait passer pour
# « sans lien » des sources qui en portent un.
_CLES_LIEN = ("url", "lien", "portail")
_CLES_EDITEUR = ("editeur", "organisme", "auteur")
_CLES_TITRE = ("titre", "nom", "intitule")


def _texte(v):
    return v.strip() if isinstance(v, str) and v.strip() else None


def _premier(d, cles):
    for c in cles:
        t = _texte(d.get(c))
        if t:
            return t
    return None


def _une_source(module, domaine, nom_var, d):
    """Une entrée du registre, ou None si le dictionnaire n'est pas une source.

    LE FILTRE COMPTE. Un module porte des dictionnaires qui commencent par
    SOURCE sans être des sources — des libellés, des seuils. Sans titre NI
    éditeur, on n'a rien à publier, et publier une ligne vide ferait gonfler
    le registre sans rien lui apporter.
    """
    titre = _premier(d, _CLES_TITRE)
    editeur = _premier(d, _CLES_EDITEUR)
    lien = _premier(d, _CLES_LIEN)
    # UNE SOURCE SE CITE : elle a un ÉDITEUR ou une ADRESSE. Le seul titre ne
    # suffit pas, et le laisser passer a produit un faux mesuré — la taxonomie
    # des origines d'eau (« Réseau d'eau potable », « Eau de mer », « Boucle
    # fermée ») vit sous une variable nommée SOURCES_EAU et se retrouvait
    # publiée comme sept sources bibliographiques à compléter. Une nomenclature
    # n'est pas une bibliographie.
    if not editeur and not lien:
        return None
    if not titre and not editeur:
        return None
    # PROPRE AU CABINET : une synthèse maison n'a pas de publication à citer,
    # et ce n'est pas un manquement — c'est une nature. La distinguer d'un
    # lien simplement absent évite de reprocher au registre ce qui est un
    # choix assumé.
    ref = " ".join(filter(None, (titre, editeur, _texte(d.get("nature")))))
    propre = any(m in ref.lower() for m in
                 ("conseilprev", "cabinet", "par nos soins", "construit par"))
    return {
        "module": module,
        "domaine": domaine,
        "variable": nom_var,
        "titre": titre or editeur,
        "editeur": editeur or "—",
        "lien": lien,
        "nature": _texte(d.get("nature")) or ("analyse" if propre else "referentiel"),
        "note": _texte(d.get("note")) or _texte(d.get("reserve")),
        "propre": propre,
    }


def recolter():
    """Toutes les sources déclarées par les modules, dédoublonnées par lien.

    Le dédoublonnage se fait sur le LIEN quand il existe, sur le couple
    titre + éditeur sinon : deux moteurs citant le même jeu de données ne
    doivent pas produire deux lignes, mais deux synthèses distinctes du
    cabinet, oui.
    """
    import importlib
    vues, out = set(), []
    for nom_module, domaine in MODULES:
        try:
            M = importlib.import_module(nom_module)
        except Exception:
            # UN MODULE ABSENT NE FAIT PAS TOMBER LE REGISTRE. Il manquerait
            # ses sources, et c'est tout — un registre qui refuse de se
            # construire n'aide personne.
            continue
        for nom_var in sorted(dir(M)):
            if not nom_var.startswith("SOURCE"):
                continue
            v = getattr(M, nom_var)
            lots = []
            if isinstance(v, dict):
                # Soit la source elle-même, soit un dictionnaire de sources.
                if any(k in v for k in _CLES_TITRE + _CLES_EDITEUR + _CLES_LIEN):
                    lots = [(nom_var, v)]
                else:
                    lots = [(nom_var + "." + str(k), x)
                            for k, x in v.items() if isinstance(x, dict)]
            elif isinstance(v, (list, tuple)):
                lots = [(nom_var + "[%d]" % i, x)
                        for i, x in enumerate(v) if isinstance(x, dict)]
            for var, d in lots:
                s = _une_source(nom_module, domaine, var, d)
                if not s:
                    continue
                cle = s["lien"] or (s["titre"] + "|" + s["editeur"])
                if cle in vues:
                    continue
                vues.add(cle)
                out.append(s)
    return sorted(out, key=lambda s: (s["domaine"], (s["editeur"] or "").lower()))


def verification():
    """Les sources du registre de vérification, avec leurs corroborations.

    Elles ne vivent pas dans un module de calcul : elles appartiennent au
    contrôle factuel, et elles portent des liens que le lecteur peut rouvrir.
    Les omettre aurait donné un registre plus pauvre que le travail fait.
    """
    try:
        import factcheck
    except Exception:
        return []
    vues, out = set(), []
    for c in factcheck.CONTROLES:
        for s in [c.get("source") or {}] + list(c.get("corroborations") or []):
            titre = _premier(s, _CLES_TITRE)
            editeur = _premier(s, _CLES_EDITEUR)
            if not titre and not editeur:
                continue
            lien = _premier(s, _CLES_LIEN)
            cle = lien or (str(titre) + "|" + str(editeur))
            if cle in vues:
                continue
            vues.add(cle)
            out.append({"module": "factcheck", "domaine": "Vérification factuelle",
                        "variable": c.get("cle") or "", "titre": titre or editeur,
                        "editeur": editeur or "—", "lien": lien,
                        "nature": "referentiel", "note": None, "propre": False})
    return sorted(out, key=lambda s: (s["editeur"] or "").lower())


def couverture(lot):
    """Quelle part de ce registre le lecteur peut RÉELLEMENT rouvrir.

    C'est le seul chiffre qui compte pour qui vient chercher des sources
    vérifiables, et c'est celui qu'une liste écrite à la main ne donne
    jamais."""
    n = len(lot)
    avec = sum(1 for s in lot if s["lien"])
    maison = sum(1 for s in lot if s["propre"])
    sans = [s for s in lot if not s["lien"] and not s["propre"]]
    return {
        "total": n,
        "avec_lien": avec,
        "part_avec_lien": round(avec / n, 3) if n else 0.0,
        "syntheses_du_cabinet": maison,
        "sans_lien_a_completer": len(sans),
        "a_completer": [s["titre"] for s in sans],
        "dit": ("%d sources sur %d s'ouvrent d'un clic ; %d sont des synthèses du "
                "cabinet, qui ne renvoient à aucune publication ; %d citent un "
                "éditeur dont l'adresse n'est pas encore enregistrée."
                % (avec, n, maison, len(sans)) if n else "registre vide"),
    }


def etat():
    """Le bloc publié tel quel par l'API et par la page."""
    lot = recolter()
    verif = verification()
    tout = lot + verif
    return {
        "ok": True,
        "version": VERSION,
        "genere": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": lot,
        "verification": verif,
        "couverture": couverture(tout),
        "par_domaine": _par_domaine(tout),
        "limite": "Ce registre récolte ce que les modules DÉCLARENT. Il ne "
                  "vérifie pas que les adresses répondent : un lien devenu mort "
                  "y figurerait encore.",
    }


def _par_domaine(lot):
    d = {}
    for s in lot:
        d.setdefault(s["domaine"], 0)
        d[s["domaine"]] += 1
    return dict(sorted(d.items(), key=lambda x: (-x[1], x[0])))


def sante():
    lot = recolter()
    return {"module": "registre_sources", "version": VERSION,
            "modules_interroges": len(MODULES), "sources": len(lot),
            "verification": len(verification())}
