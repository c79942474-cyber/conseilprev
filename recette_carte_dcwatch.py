# -*- coding: utf-8 -*-
"""La carte publiee des centres de donnees francais, rejouee sur la base locale.

CE QUI A DECLENCHE CETTE RECETTE. « Les Echos » a publie en 2026 une carte des
centres de donnees francais, dimensionnee en megawatts et coloriee par origine
de l'operateur, en citant Hubblo-DCWatch et AEF Info. Or CONSEILPREV DEPOSE
cette base DCWatch, sous ODbL, dans le depot. La carte etait donc verifiable, et
elle ne l'avait jamais ete : le referentiel se contentait de recopier « environ
trois cent cinquante » avec sa source.

CE QUE CETTE RECETTE ETABLIT, ET POURQUOI C'EST PLUS QU'UN CONTROLE :

  1. LA REGLE DE LECTURE DE LA CARTE. « Environ trois cent cinquante » ne se
     retrouve pas en comptant les lignes francaises de la base — il y en a
     quatre cent vingt-sept. C'est le compte des lignes EN EXPLOITATION. Sans
     cette regle ecrite quelque part, la prochaine comparaison se fera sur le
     mauvais total, et l'ecart sera lu comme une lacune de la base.

  2. LES ONZE SITES QUE LA CARTE NOMME. Chacun est rejoue depuis la base. Dix
     concordent au dixieme de megawatt pres une fois la regle appliquee. Le
     onzieme, Roubaix, ne concorde pas — et c'est la que la recette gagne son
     interet : la base porte DEUX LIGNES EN DOUBLE, et personne ne le disait.

  3. CE QUE LA CARTE NE MONTRE PAS. Elle cartographie deux gigawatts en
     exploitation. La meme base porte plus du triple en projets, et le rapport
     parlementaire compte quinze gigawatts reserves aupres du RTE. Trois stades,
     trois chiffres, aucune addition possible.

CE QU'ELLE NE FAIT PAS, ET LA LIGNE EST CELLE DE L'ODbL. Elle lit la base par
site — usage INTERNE, article 4.5.c — pour produire un constat, qui est un
travail produit au sens de l'article 4.3 et porte donc la mention de provenance.
Elle n'ajoute aucune valeur DCWatch au referentiel servi : verser ces
estimations dans `datacentres.SITES` en ferait une base derivee, soumise au
partage a l'identique. La ligne passe entre PRODUIRE et REDISTRIBUER.

ET ELLE NE LEVE PAS L'INTERDIT SUR LES MEGAWATTS. Les puissances de la carte
sont ESTIMEES par mesure de batiment sur imagerie satellite : ce sont des
ordres de grandeur de bati, pas des charges informatiques. Le referentiel a
raison de laisser `capacite_mw` nul ; concorder avec la carte ne change rien a
cela, et cette recette ne propose pas de les importer.

  POUR L'EXECUTER :  python3 recette_carte_dcwatch.py
"""
import csv
import io
import os
import re
import sys
import unicodedata

import datacentres as D
import dcwatch
import parc_fr as P

ko = 0


def ok(nom, cond, detail=""):
    global ko
    print("  " + ("OK " if cond else "KO ") + "  " + nom + (" — " + str(detail) if detail else ""))
    if not cond:
        ko += 1


def titre(t):
    print("\n== " + t + " ==\n")


def _plat(s):
    """Sans accents, sans ponctuation : « Val-de-Reuil » et « Val de Reuil »
    designent la meme commune, et la base emploie les deux."""
    s = unicodedata.normalize('NFD', str(s or '')).encode('ascii', 'ignore').decode()
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', s.lower()).split())


# LES ONZE VALEURS QUE LA CARTE PUBLIE, RECOPIEES DEPUIS ELLE ET DE NULLE PART
# AILLEURS. C'est la seule chose qui soit recopiee ici : ce sont les valeurs a
# verifier, et les deriver de la base rendrait la verification circulaire.
CARTE = [
    ("OVHCloud Gravelines",        "ovh",      "gravelines",     4, 30.0),
    ("OVHCloud Roubaix",           "ovh",      "roubaix",        9, 45.0),
    ("OVHCloud Strasbourg",        "ovh",      "strasbourg",     5, 20.0),
    ("Orange BS Normandie",        "orange",   "val de reuil",   2, 48.0),
    ("Orange BS Chartres, Amilly", "orange",   "amilly",         1, 28.5),
    ("DATAGREX Saint-Saturnin",    "datagrex", "saint saturnin", 1, 13.0),
    ("CERN Prevessin-Moens",       "cern",     "prevessin",      1, 12.0),
    ("EQUINIX BX1 Bruges",         "equinix",  "bruges",         1, 20.0),
    ("FULLSAVE TLS00 Toulouse",    "fullsave", "toulouse",       1, 34.4),
    ("Digital Realty Marseille",   "digital",  "marseille",      4, 70.2),
    ("Euclyde DC1 Antibes",        "euclyde",  "antibes",        1,  8.5),
]

# Le dixieme de megawatt : la carte arrondit ses etiquettes (« 28,5 MW »), la
# base porte 28,49. Une tolerance plus large laisserait passer un vrai ecart.
TOLERANCE_MW = 0.35


def _lignes_fr():
    """La base, lue directement — usage interne. Le module `dcwatch` ne rend
    volontairement aucun enregistrement : c'est ce qui lui permet de servir des
    agregats sans ouvrir le referentiel. Une recette qui tourne a la main n'est
    pas un service."""
    if not os.path.exists(dcwatch.FICHIER):
        return None
    with io.open(dcwatch.FICHIER, encoding='utf-8', newline='') as f:
        lignes = [{k: dcwatch._reparer(v) for k, v in l.items()} for l in csv.DictReader(f)]
    return [l for l in lignes if _plat(l.get('country')) == 'france']


titre("0. La base est la, et c'est elle qui parle")

fr = _lignes_fr()
ok("la base DCWatch est deposee", fr is not None,
   dcwatch.FICHIER if fr is None else "%d lignes francaises" % len(fr))
if fr is None:
    # UNE RECETTE QUI NE PEUT PAS MESURER NE DIT PAS « TOUT VA BIEN ». Sans la
    # base, aucune des affirmations ci-dessous n'est verifiable, et les afficher
    # en vert ferait passer une absence pour une concordance.
    print("\nLa base n'est pas la : rien ne peut etre verifie. "
          "Aucun controle n'est presente comme vert.\n")
    sys.exit(1)

print("  " + dcwatch.MENTION)

exploitation = [l for l in fr if _plat(l.get('progress_step')) == 'operating']
projets = [l for l in fr if _plat(l.get('progress_step')) == 'project']


def _mw(lignes):
    return sum(float(l.get('power_total_mw') or 0) for l in lignes)


def _sans_doublon(lignes):
    vus, uniques = set(), []
    for l in lignes:
        cle = (_plat(l.get('name')), _plat(l.get('city_name')))
        if cle not in vus:
            uniques.append(l)
        vus.add(cle)
    return uniques


# ── 1. La regle de lecture ─────────────────────────────────────────────────
titre("1. D'ou vient « environ trois cent cinquante »")

publie = D.COUVERTURE_NATIONALE["FR"]["recense"]
print("  publie par la carte              : environ %d" % publie)
print("  lignes francaises de la base     : %d" % len(fr))
print("  dont en exploitation             : %d" % len(exploitation))
print("  dont en projet                   : %d" % len(projets))
print("  exploitation, doublons retires   : %d" % len(_sans_doublon(exploitation)))

ok("le compte publie ne s'obtient PAS sur toutes les lignes",
   abs(len(fr) - publie) > 25,
   "%d lignes contre %d publies : comparer les deux serait une faute" % (len(fr), publie))
ok("il s'obtient sur les seules lignes EN EXPLOITATION",
   abs(len(exploitation) - publie) <= 10,
   "%d en exploitation contre %d publies" % (len(exploitation), publie))
ok("la regle de lecture est ecrite dans le referentiel",
   "EXPLOITATION" in D.COUVERTURE_NATIONALE["FR"].get("lecture", ""),
   "sans cela, la prochaine comparaison se fera sur le mauvais total")


# ── 2. Les onze sites nommes ───────────────────────────────────────────────
titre("2. Les onze sites que la carte nomme, rejoues sur la base")

uniques = _sans_doublon(exploitation)
concordent = 0
for nom, operateur, ville, n_carte, mw_carte in CARTE:
    sel = [l for l in uniques
           if operateur in _plat(l.get('operator')) + ' ' + _plat(l.get('name'))
           and ville in _plat(l.get('city_name'))]
    mw = _mw(sel)
    accord = abs(mw - mw_carte) <= TOLERANCE_MW and len(sel) == n_carte
    concordent += 1 if accord else 0
    print("  %-4s %-27s carte %2d / %6.1f MW   base %2d / %6.1f MW"
          % ("OK" if accord else "  .", nom, n_carte, mw_carte, len(sel), mw))

ok("dix des onze sites nommes concordent une fois la regle appliquee",
   concordent >= 10, "%d sur %d" % (concordent, len(CARTE)))


# ── 3. Ce que l'ecart restant revele ───────────────────────────────────────
titre("3. Le site qui ne concorde pas, et ce qu'il a fait sortir")

doublons = dcwatch.agregats("France").get("doublons")
brut = [l for l in exploitation
        if 'ovh' in _plat(l.get('operator')) + ' ' + _plat(l.get('name'))
        and 'roubaix' in _plat(l.get('city_name'))]
net = _sans_doublon(brut)
print("  Roubaix : %d lignes dans la base, %d batiments distincts, %d publies par la carte"
      % (len(brut), len(net), 9))

ok("la base porte des lignes en double, et l'agregat les compte",
   doublons and doublons > 0,
   "%s doublon(s) sur le perimetre francais : le parc en exploitation ressort a "
   "%d lignes pour %d sites distincts" % (doublons, len(exploitation), len(uniques)))
ok("le module les rend, au lieu de les taire",
   "doublons" in dcwatch.agregats("France"),
   "un doublon tu se lit comme un site")


# ── 4. Ce que la carte ne montre pas ───────────────────────────────────────
titre("4. Trois stades, trois chiffres, aucune addition possible")

e = P.echelles()
ok("les ordres de grandeur sont derivables", e.get("disponible") is True,
   e.get("pourquoi", ""))
if e.get("disponible"):
    for x in e["echelles"]:
        print("  %-22s %6.2f %-3s %s" % (x["cle"], x["valeur"], x["unite"],
                                         ("%s sites" % x["sites"]) if x["sites"] else ""))
    par_cle = {x["cle"]: x for x in e["echelles"]}
    ok("la carte ne montre que ce qui tourne",
       par_cle["projets"]["valeur"] > par_cle["exploitation"]["valeur"],
       "les projets pesent %.1f fois l'exploitation, et ne sont pas cartographies"
       % (par_cle["projets"]["valeur"] / max(0.01, par_cle["exploitation"]["valeur"])))
    ok("chaque ordre de grandeur porte sa reserve",
       all(len(x.get("reserve") or "") > 50 for x in e["echelles"]),
       "un chiffre sans reserve se lit comme une mesure")
    ok("la mention ODbL accompagne les chiffres produits",
       "ODbL" in (e.get("mention") or ""),
       "l'article 4.3 l'exige sur tout travail produit")


# ── 5. Ce que cette recette n'a PAS fait ───────────────────────────────────
titre("5. La ligne qui n'est pas franchie")

avec_mw = [s for s in D.SITES if s.get("capacite_mw")]
ok("aucune puissance DCWatch n'est entree dans le referentiel servi",
   not avec_mw,
   "y verser ces estimations en ferait une base derivee, soumise au partage a "
   "l'identique — et un ordre de grandeur de batiment y passerait pour une "
   "capacite attestee")
ok("le module public ne rend toujours aucun enregistrement",
   not any(callable(getattr(dcwatch, n, None)) and n in ('sites', 'lignes', 'enregistrements')
           for n in dir(dcwatch)),
   "la lecture par site reste un usage interne (ODbL, art. 4.5.c)")

print("\n" + (str(ko) + " controle(s) en echec" if ko else "tout est vert") + "\n")
sys.exit(1 if ko else 0)
