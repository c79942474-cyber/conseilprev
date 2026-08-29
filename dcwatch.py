# -*- coding: utf-8 -*-
"""DCWATCH — DES AGREGATS, ET RIEN QUE DES AGREGATS.

CE QUE CE MODULE EST, ET CE QU'IL NE SERA PAS. Il lit la base DCWatch, publiee
sous ODbL 1.0, et n'en rend que des chiffres agreges. Il n'expose AUCUNE
fonction qui rende les enregistrements par site, et ce n'est pas une precaution
de style : c'est la condition qui permet d'employer cette base sans ouvrir le
referentiel de CONSEILPREV.

LA LIGNE, ET OU ELLE PASSE EXACTEMENT. L'ODbL impose le partage a l'identique
(art. 4.4) a toute BASE DERIVEE dont on fait un usage public — et servir une
base a des abonnes par une API en releve. Verser les puissances DCWatch dans le
referentiel servi creerait une telle base derivee. L'article 4.5 dit ou s'arrete
cette obligation :

    b. Using this Database [...] to create a Produced Work does not create a
       Derivative Database for purposes of Section 4.4;
    c. Use of a Derivative Database internally within an organisation is not to
       the public and therefore does not fall under the requirements of
       Section 4.4.

Un chiffre agrege est un TRAVAIL PRODUIT au sens de l'article 4.3 : il porte la
mention de provenance, et rien de plus. La ligne passe donc entre PRODUIRE et
REDISTRIBUER LA BASE — pas entre gratuit et payant, ni entre interne et public.

LE SEUIL DE REGROUPEMENT N'EST PAS UNE PRECAUTION DECORATIVE. Une agregation
assez fine redevient la base : une moyenne sur UN site est la valeur de ce site.
Toute ventilation passe donc par `_regrouper`, qui verse dans « autres » toute
categorie comptant moins de SEUIL_AGREGAT sites. Sans ce seuil, publier
« puissance moyenne par commune » republierait la base commune par commune, et
la separation ci-dessus ne vaudrait plus rien.

CE QUE CE MODULE NE PEUT PAS GARANTIR. Que les chiffres soient justes au fond.
DCWatch se declare non exhaustive, et sa puissance est estimee par mesure de
BATIMENT sur imagerie satellite — pas par mesure de charge informatique.
`RESERVE_METHODE` porte cet avertissement, et `agregats()` le rend avec les
chiffres : un ordre de grandeur publie sans sa methode se lit comme une mesure.
"""
import csv
import io
import os

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(ICI, 'dcwatch')
FICHIER = os.path.join(DOSSIER, 'export_summary.csv')

# LA MENTION EXIGEE PAR L'ARTICLE 4.3, mot pour mot dans la forme que la licence
# propose. Elle accompagne CHAQUE chiffre publie : une mention rangee dans une
# page « mentions legales » ne suit pas le chiffre qu'elle doit accompagner.
MENTION = ("Contient des informations de DCWatch, mises à disposition sous "
           "Open Database License (ODbL) 1.0 — "
           "https://opendatacommons.org/licenses/odbl/1-0/")

SOURCE = "DCWatch (Hubblo) — https://gitlab.com/hubblo/datacenter-watch"
VERSION = "2026.04.09"

RESERVE_METHODE = (
    "DCWatch se déclare non exhaustive. Sa puissance est ESTIMÉE par mesure des "
    "dimensions du bâtiment sur imagerie satellite, croisée avec le cadastre et "
    "les rapports extra-financiers : c'est une mesure de bâtiment, pas de charge "
    "informatique. Ces ordres de grandeur ne remplacent pas une puissance "
    "souscrite déclarée.")

# En deçà, une catégorie est versée dans « autres » : voir l'en-tête de module.
SEUIL_AGREGAT = 5

_CACHE = None


def _lire():
    """Les enregistrements, en mémoire, une seule fois. PRIVÉ, et il le reste :
    aucune fonction publique de ce module ne rend cette liste."""
    global _CACHE
    if _CACHE is None:
        if not os.path.exists(FICHIER):
            _CACHE = []
        else:
            with io.open(FICHIER, encoding='utf-8', newline='') as f:
                _CACHE = list(csv.DictReader(f))
    return _CACHE


def disponible():
    """La base est-elle présente ? Une absence se dit, elle ne se devine pas :
    sans ce drapeau, un agrégat vide se lirait comme un parc vide."""
    return bool(_lire())


def _nombre(v):
    try:
        x = float(str(v).strip())
    except (TypeError, ValueError):
        return None
    return x if x > 0 else None


def _regrouper(compte):
    """Verse dans « autres » toute catégorie sous le seuil.

    C'EST CE QUI EMPÊCHE L'AGRÉGAT DE REDEVENIR LA BASE. Une ventilation par
    commune, ou par tout découpage assez fin, finirait par publier des groupes
    d'un seul site — c'est-à-dire la valeur de ce site, et donc la base."""
    gros, reste = {}, 0
    for cle, n in compte.items():
        if n >= SEUIL_AGREGAT:
            gros[cle] = n
        else:
            reste += n
    if reste:
        gros['autres (groupes de moins de %d sites)' % SEUIL_AGREGAT] = reste
    return gros


def agregats(pays=None):
    """Les chiffres publiables : des totaux, des distributions, aucune ligne.

    `pays` restreint au libellé exact du champ `country` (« France »,
    « Switzerland »…). Il ne descend pas plus bas : une restriction plus fine
    ferait du résultat une extraction, pas un agrégat."""
    lignes = _lire()
    if pays:
        lignes = [l for l in lignes if (l.get('country') or '').strip() == pays]

    # LE SEUIL VAUT AUSSI POUR LE PÉRIMÈTRE, ET PAS SEULEMENT POUR SES
    # VENTILATIONS. Éprouvé sur `?pays=Monaco` : trois sites, et un total de
    # puissance sur trois sites n'est plus un agrégat — c'est presque la donnée.
    # Le regroupement des régions ne protégeait rien tant que la sélection
    # elle-même pouvait descendre à trois lignes.
    if 0 < len(lignes) < SEUIL_AGREGAT:
        return {
            'source': SOURCE, 'version': VERSION, 'mention': MENTION,
            'reserve': RESERVE_METHODE,
            'perimetre': pays or 'tous pays de la base',
            'sites': None,
            'trop_petit': True,
            'seuil': SEUIL_AGREGAT,
            'pourquoi': ("Ce périmètre compte moins de %d sites. Un total calculé "
                         "sur si peu de lignes n'est plus un chiffre agrégé : il "
                         "approche la donnée par site, que cette base ne "
                         "redistribue pas." % SEUIL_AGREGAT),
        }

    puissances = [p for p in (_nombre(l.get('power_total_mw')) for l in lignes) if p]
    surfaces = [s for s in (_nombre(l.get('total_floor_area_sqm')) for l in lignes) if s]

    par_pays, par_etat, par_region = {}, {}, {}
    for l in lignes:
        for champ, seau in (('country', par_pays), ('progress_step', par_etat),
                            ('region', par_region)):
            cle = (l.get(champ) or '').strip() or 'non renseigné'
            seau[cle] = seau.get(cle, 0) + 1

    puissances_triees = sorted(puissances)
    mediane = None
    if puissances_triees:
        m = len(puissances_triees) // 2
        mediane = (puissances_triees[m] if len(puissances_triees) % 2
                   else (puissances_triees[m - 1] + puissances_triees[m]) / 2.0)

    return {
        'source': SOURCE,
        'version': VERSION,
        'mention': MENTION,
        'reserve': RESERVE_METHODE,
        'perimetre': pays or 'tous pays de la base',
        'sites': len(lignes),
        # LE DÉNOMINATEUR AVEC LE NUMÉRATEUR. « 3,2 GW » sans « sur 412 sites
        # renseignés parmi 520 » se lit comme un total du parc, et ne l'est pas.
        'sites_avec_puissance': len(puissances),
        'puissance_totale_mw': round(sum(puissances), 1) if puissances else None,
        'puissance_mediane_mw': round(mediane, 2) if mediane is not None else None,
        'puissance_max_mw': round(max(puissances), 1) if puissances else None,
        'sites_avec_surface': len(surfaces),
        'surface_totale_m2': round(sum(surfaces)) if surfaces else None,
        'repartition_pays': _regrouper(par_pays),
        'repartition_etat': _regrouper(par_etat),
        'repartition_region': _regrouper(par_region),
    }


def couverture():
    """Ce que la base couvre, et ce qu'elle ne couvre pas — sans chiffre de
    parc. Sert à décider si un agrégat vaut la peine d'être publié."""
    lignes = _lire()
    if not lignes:
        return {'disponible': False, 'source': SOURCE, 'mention': MENTION}
    renseignes = sum(1 for l in lignes
                     if _nombre(l.get('power_total_mw')) is not None)
    return {
        'disponible': True,
        'source': SOURCE,
        'version': VERSION,
        'mention': MENTION,
        'reserve': RESERVE_METHODE,
        'sites': len(lignes),
        'sites_avec_puissance': renseignes,
        'part_renseignee_pct': round(100.0 * renseignes / len(lignes), 1),
        'pays_couverts': len({(l.get('country') or '').strip()
                              for l in lignes if (l.get('country') or '').strip()}),
    }
