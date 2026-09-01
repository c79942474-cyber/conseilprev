# -*- coding: utf-8 -*-
"""LE PARC FRANCAIS, EN TROIS ORDRES DE GRANDEUR — un travail produit, pas une base.

POURQUOI CE MODULE EXISTE AILLEURS QUE DANS LES DEUX QU'IL RAPPROCHE.

Le rapprochement demande deux sources : les agregats DCWatch, publies sous ODbL,
et les reperes nationaux du referentiel CONSEILPREV. Il ne pouvait vivre ni dans
l'un ni dans l'autre.

  · Pas dans `datacentres.py` : une regle du depot interdit a ce module
    d'importer DCWatch, et elle a raison. `datacentres.assemble()` est SERVI par
    /api/datacentres ; s'il lisait la base ODbL, le referentiel deviendrait une
    base derivee au sens de l'article 4.4 et son partage a l'identique
    s'imposerait — c'est-a-dire l'ouverture d'un actif proprietaire.

  · Pas dans `dcwatch.py` non plus : ce module s'interdit de rendre autre chose
    que des agregats de la base, et lui faire porter des reperes CONSEILPREV
    brouillerait cette frontiere.

Le rapprochement se fait donc ICI, dans un troisieme lieu qui est explicitement
un TRAVAIL PRODUIT au sens de l'article 4.3 : il porte la mention de provenance,
et ne redistribue aucune base.

CE QU'IL DIT, ET POURQUOI CELA COMPTE.

Un nombre de megawatts ne veut rien dire sans son stade. La carte publiee par
« Les Echos » en 2026, qui cite Hubblo-DCWatch, montre ce qui TOURNE. La base
dont elle derive porte plus du TRIPLE en projets. Le rapport parlementaire sur
les vulnerabilites numeriques compte pres de SEPT FOIS plus en reservations de
raccordement aupres du RTE. Trois stades, trois chiffres — et additionner deux
d'entre eux donne un total qui n'existe a aucune date. C'est l'erreur que
produit spontanement une lecture rapide de la carte, et la seule facon de ne pas
la commettre est de nommer le stade a chaque fois.

CE QU'IL NE FAIT PAS. Il ne lit jamais la base par site : il appelle
`dcwatch.agregats()`, comme n'importe quel autre consommateur. Une lecture par
site depuis un module importable serait une porte ouverte vers l'extraction que
`dcwatch` s'interdit precisement de servir.
"""
import datacentres
import dcwatch

PERIMETRE = "France"


def echelles():
    """Les trois ordres de grandeur, derives a l'appel.

    RIEN N'EST RECOPIE. Les deux premiers viennent de l'agregat DCWatch au
    moment de l'appel ; le troisieme est lu dans `REPERES_FR`, ou il porte deja
    sa source et sa reserve. Si la base bouge, la phrase bouge avec elle : c'est
    ce qui separe une donnee d'une legende.

    Ces chiffres ne viennent d'AUCUN site du referentiel CONSEILPREV, dont
    `capacite_mw` reste nul partout. L'interdit tient, et ce module ne l'entame
    pas : une puissance DCWatch est une estimation de BATIMENT par imagerie
    satellite, pas une charge informatique attestee."""
    if not dcwatch.disponible():
        return {
            "disponible": False,
            "perimetre": PERIMETRE,
            "pourquoi": ("La base DCWatch n'est pas deposee : sans elle, les deux "
                         "premiers ordres de grandeur ne peuvent pas etre derives, et "
                         "les inventer reviendrait a publier une legende."),
        }
    a = dcwatch.agregats(PERIMETRE)
    mw = a.get("puissance_par_etat_mw") or {}
    n = a.get("repartition_etat") or {}
    origine = "%s, version %s" % (dcwatch.SOURCE, dcwatch.VERSION)
    lot = [
        {"cle": "exploitation", "valeur": round((mw.get("operating") or 0) / 1000.0, 2),
         "unite": "GW", "sites": n.get("operating"),
         "libelle": "Puissance estimee des sites EN EXPLOITATION",
         "source": origine, "reserve": dcwatch.RESERVE_METHODE},
        {"cle": "projets", "valeur": round((mw.get("project") or 0) / 1000.0, 2),
         "unite": "GW", "sites": n.get("project"),
         "libelle": "Puissance estimee des sites EN PROJET",
         "source": origine,
         "reserve": ("Un projet n'est pas un batiment. Les annonces ne se realisent "
                     "pas toutes, et celles qui meurent avant publicite ne laissent "
                     "aucune trace : ce total est un plafond d'intentions, pas une "
                     "capacite a venir.")},
    ]
    for r in datacentres.REPERES_FR:
        if r["cle"] == "raccordement_reserve":
            lot.append({"cle": r["cle"], "valeur": r["valeur"], "unite": r["unite"],
                        "sites": None, "libelle": r["libelle"],
                        "source": r["source"], "reserve": r["reserve"]})
    return {
        "disponible": True,
        "perimetre": PERIMETRE,
        "mention": dcwatch.MENTION,
        "doublons_base": a.get("doublons"),
        "echelles": lot,
        "note": ("Trois stades, trois chiffres, et aucune addition possible : ce qui "
                 "tourne, ce qui est annonce, ce qui est reserve au reseau. La carte "
                 "publiee ne montre que le premier."),
    }
