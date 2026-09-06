# -*- coding: utf-8 -*-
"""La veille « gouvernance de l'IA » — LUE chez le site cyber, jamais collectée
une seconde fois.

POURQUOI ON NE COLLECTE PAS ICI, ET C'EST LE CŒUR DE LA DÉCISION. Le site
conseilprevcyber tient déjà un catalogue de trente-six flux, un collecteur qui
lit RSS comme Atom, la distinction entre « cette adresse ne sert pas un flux »
et « ce flux n'a rien publié », des états de santé par source, une rotation qui
évite la famine et un budget de temps par passage. Mesuré le 6 septembre 2026
depuis le shell de son service : QUATRE SOURCES INSTITUTIONNELLES VIVANTES
alimentent la gouvernance de l'IA — CNIL, Commission européenne, NIST, CEPD —
pour une soixantaine d'éléments par passage.

Réécrire tout cela ici pour atteindre exactement les mêmes quatre sources
produirait DEUX DÉFINITIONS DU MÊME MÉTIER. Elles ne divergeraient pas le
premier jour ; elles divergeraient le jour où l'une des deux serait corrigée.
C'est le défaut que ce dépôt corrige partout ailleurs, et il n'y a pas de raison
de l'introduire ici de nos propres mains.

CE QUE CE MODULE FAIT, ET CE QU'IL NE FAIT PAS. Il LIT un flux Atom et n'en
retient que ce qui porte la facette du domaine. Il ne touche ni au réseau, ni à
une base : `app.py` détient les deux. Une fonction qui ouvre une socket ne
s'éprouve qu'en ouvrant une socket — donc jamais dans la suite de règles, donc
jamais vraiment. Ici, tout se mesure sur un texte.

CE QUI RESTE À L'ÉMETTEUR. Les titres et les chapeaux appartiennent aux
éditeurs. On reprend ce qu'ils mettent eux-mêmes dans leurs flux pour être
repris — titre, lien, chapeau — et on porte leur nom. Republier un chapeau sans
son émetteur ni son lien en ferait notre propos, ce qu'il n'est pas.
"""
import xml.etree.ElementTree as ET

VERSION = "2026-09-a"

# La facette du site cyber, écrite ICI UNE SEULE FOIS. Elle doit dire exactement
# ce que `veille_sources.DOMAINES` nomme là-bas : un libellé voisin filtrerait
# sur un domaine qui n'existe pas, ne lèverait rien, et rendrait une liste vide
# — la panne muette que ce flux existe justement pour éviter.
DOMAINE_IA = "ia_gouvernance"

SOURCE_DEFAUT = "https://conseilprevcyber.onrender.com/veille.xml"

# Une semaine. Le même choix que la collecte cyber, pour la même raison : rien
# de ce qu'affiche cette page n'exige d'être plus frais, et solliciter un site
# voisin quatre fois par jour pour republier les mêmes éléments n'a pas d'objet.
INTERVALLE_HEURES = 168

_ATOM = "{http://www.w3.org/2005/Atom}"


def _texte(noeud, balise):
    e = noeud.find(_ATOM + balise)
    return (e.text or "").strip() if e is not None and e.text else ""


def entrees(atom, domaine=DOMAINE_IA):
    """Les entrées du flux qui portent la facette demandée.

    LE FILTRE PORTE SUR LA FACETTE DÉCLARÉE, jamais sur les mots du titre.
    Deviner le domaine d'après le texte ferait entrer « le RGPD des caméras »
    dans la gouvernance de l'IA et sortir un avis qui ne prononce pas le mot :
    le classement est un travail que le site amont a déjà fait, et le refaire
    au jugé le referait mal.

    UN FLUX ILLISIBLE REND UNE LISTE VIDE, jamais une exception. La page qui
    l'affiche a d'autres choses à montrer ; la faire tomber pour un flux
    momentanément absent coûterait plus que l'absence de ce bloc.

    UNE ENTRÉE SANS TITRE EST ÉCARTÉE, PAS DEVINÉE : elle produirait une carte
    vide, cliquable, qui ne dit rien de ce qu'elle ouvre.
    """
    try:
        racine = ET.fromstring(atom)
    except ET.ParseError:
        return []
    sortie = []
    for entree in racine.iter(_ATOM + "entry"):
        facettes = [c.get("term") for c in entree.iter(_ATOM + "category")
                    if c.get("scheme") == "domaine"]
        if domaine not in facettes:
            continue
        titre = _texte(entree, "title")
        if not titre:
            continue
        lien = ""
        for l in entree.iter(_ATOM + "link"):
            if l.get("rel") in (None, "alternate") and l.get("href"):
                lien = l.get("href")
                break
        sortie.append({
            "titre": titre,
            "lien": lien,
            "resume": _texte(entree, "summary"),
            "emetteur": _emetteur(entree),
            "publie": _texte(entree, "updated"),
            "guid": _texte(entree, "id") or lien or titre,
            "themes": sorted({c.get("term") for c in entree.iter(_ATOM + "category")
                              if c.get("scheme") == "theme" and c.get("term")}),
        })
    return sortie


def _emetteur(entree):
    auteur = entree.find(_ATOM + "author")
    return _texte(auteur, "name") if auteur is not None else ""


def est_du(dernier, maintenant, intervalle_heures=INTERVALLE_HEURES):
    """Une semaine s'est-elle écoulée depuis le dernier passage RÉELLEMENT fait ?

    ABSENCE OU HORODATAGE ILLISIBLE = DÛ. Rien à comparer n'est pas une raison
    d'attendre : ce serait laisser un bloc vide une semaine pour se conformer à
    une cadence qu'on ne mesure pas. Et `float("NaN")` ne lève rien tandis que
    toute comparaison avec NaN vaut faux — un horodatage corrompu bloquerait
    donc le rafraîchissement POUR TOUJOURS, sans une ligne de journal. Le défaut
    a été trouvé par une règle sur le site cyber ; on ne le réintroduit pas.
    """
    try:
        precedent = float(dernier or 0)
    except (TypeError, ValueError):
        precedent = 0.0
    if precedent != precedent or precedent in (float("inf"), float("-inf")):
        precedent = 0.0
    return (float(maintenant) - precedent) >= (float(intervalle_heures) * 3600)
