# -*- coding: utf-8 -*-
"""Trois lectures des chercheurs d'élite — côté données et côté dépôt.

CE QU'ON PROTÈGE.

1. LE SOLDE N'EXISTE QUE SI SES DEUX TERMES EXISTENT. Quatre pays sur sept
   n'ont pas de lieu de travail publié. Les compter à zéro les ferait passer
   pour équilibrés — la lecture la plus flatteuse, et la plus fausse. Le
   contrôle rejoue le calcul refusé.

2. UNE FOURCHETTE N'EST PAS UNE VALEUR. « 2–4 % » sert à POSER un repère au
   milieu, jamais à calculer un solde. On vérifie que les deux usages restent
   séparés dans le code.

3. UNE SEULE ÉCRITURE DU SIGNE MOINS. Le texte du panneau écrivait « −14 »
   (U+2212) et le graphique « -14 » (trait d'union) : deux glyphes pour la même
   chose sur le même écran.

4. LA DISCRIMINATION. Avant, le panneau n'avait aucune bascule de vue, et
   `renderTalents` faisait DEUX choses sous un seul nom — la figure et le
   tableau. Ajouter une bascule du même nom aurait écrasé la fonction
   d'origine sans bruit.
"""
import io
import os
import re
import subprocess
import sys

DEPOT = "/home/user/conseilprev"
sys.path.insert(0, DEPOT)
os.chdir(DEPOT)

ko = 0


def ok(nom, cond, detail=""):
    global ko
    print("  %s   %s%s" % ("OK " if cond else "KO ", nom,
                           (" — " + str(detail)) if detail else ""))
    if not cond:
        ko += 1


import observatoire_ia as O                                    # noqa: E402

T = O.SEED["talents"]
ORI = T["origine_pct"]
TRA = T["lieu_travail_pct"]
html = io.open(DEPOT + "/observatoire.html", encoding="utf-8").read()

print("\n══ 1. Le solde n'existe que si ses deux termes existent ══\n")

ok("sept origines publiées", len(ORI) == 7, sorted(ORI))
ok("…et trois lieux de travail seulement", len(TRA) == 3, sorted(TRA))
calculables = [p for p in ORI if p in TRA]
ok("le solde n'est donc calculable que pour trois pays",
   len(calculables) == 3, sorted(calculables))
ok("…États-Unis +29 points", TRA["États-Unis"] - ORI["États-Unis"] == 29)
ok("…Chine −14 points", TRA["Chine"] - ORI["Chine"] == -14)
ok("…et « Autres » +3 points", TRA["Autres"] - ORI["Autres"] == 3)
# DISCRIMINATION : c'est le calcul qu'on refuse d'écrire. À zéro, l'Inde
# passerait pour un pays qui emploie exactement ce qu'il forme.
muets = [p for p in ORI if p not in TRA]
ok("quatre pays n'ont pas de solde", len(muets) == 4, sorted(muets))
ok("…et les poser à zéro les dirait « à l'équilibre », ce qu'aucune source "
   "n'affirme", all(ORI[p] > 0 for p in muets),
   {p: ORI[p] for p in sorted(muets)})
ok("l'Inde en fait partie, avec 7 % de chercheurs formés",
   "Inde" in muets and ORI["Inde"] == 7)

print("\n══ 2. Une fourchette n'est pas une valeur ══\n")

ok("la note dit que quatre pays sont entre 2 et 4 %",
   "entre 2 et 4 %" in T["note_lieu_travail"])
ok("…et que la valeur précise n'est pas publiée",
   "non publiées" in T["note_lieu_travail"])
ok("la page lit la fourchette par une fonction dédiée",
   html.count("function talFourchette") == 1)
ok("…qui rend un intervalle, jamais un nombre",
   "return m ? [+m[1], +m[2]] : null;" in html)
ok("…et la barre hachurée se pose au MILIEU, pas au maximum",
   "var mil = (f[0] + f[1]) / 2;" in html)
ok("le solde, lui, exige un nombre : `typeof p.t !== 'number'` rend null",
   "if(typeof p.o !== 'number' || typeof p.t !== 'number') return null;" in html)
# La fourchette ne doit JAMAIS entrer dans talSolde : ce serait un solde
# fabriqué à partir d'une lecture graphique.
bloc = html[html.find("function talSolde(p){"):]
bloc = bloc[:bloc.find("\n}")]
ok("…et `talSolde` ignore totalement la fourchette",
   "talFourchette" not in bloc and "tn" not in bloc, bloc[-80:])

print("\n══ 3. Un seul signe moins, et une seule fonction pour l'écrire ══\n")

ok("la fonction d'écriture des points existe", "function talPts(" in html)
ok("…et elle emploie le VRAI moins (U+2212)", "'−'" in html)
ok("…appelée par les trois vues et l'axe", html.count("talPts(") >= 5,
   html.count("talPts("))
ok("plus aucune étiquette ne fabrique son signe à la main",
   "(sol > 0 ? '+' : '') + fr(Math.round(sol" not in html)
ok("le texte du panneau écrivait déjà ce moins-là", "−14 points" in html)

print("\n══ 4. Trois lectures déclarées, et servies ══\n")

for cle in ("flux", "barres", "solde"):
    ok("l'onglet « %s » existe" % cle, ('data-tvue="%s"' % cle) in html)
ok("trois titres, un par lecture",
   len(re.findall(r"^\s+(flux|barres|solde):\s+'Chercheurs", html, re.M)) == 3)
ok("les deux nouvelles fonctions de rendu existent",
   "function talBarres()" in html and "function talDiverge()" in html)
ok("…et le dispatch leur passe la main",
   "if(TAL_VUE === 'barres') return talBarres();" in html)
ok("les trois textes de lecture disent ce qu'ils ne montrent pas",
   html.count("Ce qu’elle ne montre pas") >= 3
   or html.count("ne montre pas") >= 3, html.count("ne montre pas"))
ok("la barre horizontale a son propre tracé, arrondi côté valeur",
   "function barPathH(" in html and "function barPathHG(" in html)
ok("…et le miroir gauche existe pour les soldes négatifs",
   "arrondie du côté GAUCHE" in html)
ok("l'échelle divergente est symétrique, ±30",
   "var VMAX = 30;" in html and "[-30, -20, -10, 0, 10, 20, 30]" in html)

print("\n══ 5. Discrimination : ni bascule, ni barres, avant ══\n")


def _avant(marqueur, fichier):
    """Le fichier juste AVANT l'arrivée du marqueur.

    Si un commit l'a introduit, on lit son parent ; sinon la modification n'est
    pas encore livrée et la référence est HEAD. Rendre une chaîne vide rendrait
    le contrôle CREUX."""
    hs = subprocess.check_output(
        ["git", "-C", DEPOT, "log", "-S", marqueur, "--format=%H", "--", fichier],
        text=True).split()
    ref = ("%s^" % hs[-1]) if hs else "HEAD"
    return subprocess.check_output(
        ["git", "-C", DEPOT, "show", "%s:%s" % (ref, fichier)], text=True)


av = _avant("function talBarres", "observatoire.html")
ok("avant, le panneau n'avait aucune bascule de vue", "data-tvue" not in av)
ok("…ni barres jumelées", "talBarres" not in av)
ok("…ni barres divergentes", "talDiverge" not in av)
ok("…et une seule figure, le flux", av.count("function renderFluxTalents") == 1)
# LE piège : `renderTalents` faisait DEUX choses sous un seul nom. Ajouter une
# bascule du meme nom aurait écrasé l'original — et c'est la derniere
# définition qui l'emporte, en silence.
ok("…tandis que `renderTalents` faisait AUSSI le tableau",
   "function renderTalents(){\n  renderFluxTalents();" in av)
ok("le tableau a donc été détaché sous son propre nom",
   "function renderTalTable()" in html
   and "function renderTalents(){\n  renderFluxTalents();" not in html)
ok("…et il n'existe qu'UNE définition de renderTalents",
   html.count("function renderTalents(") == 1, html.count("function renderTalents("))
ok("avant, l'étiquette de solde fabriquait son signe sur place",
   "(sol > 0 ? '+' : '') + fr(Math.round(sol * 10) / 10) + ' pts'" in av)

print("\n══ 6. Ce que ces deux lectures ne devaient PAS déplacer ══\n")

ok("les pourcentages publiés sont intacts",
   ORI["États-Unis"] == 28 and ORI["Chine"] == 26 and TRA["États-Unis"] == 57
   and TRA["Chine"] == 12)
ok("la définition « présentation orale » est toujours là",
   "présentation ORALE" in T["definition"] or "orale" in T["definition"])
ok("le crédit MacroPolo est intact", "MacroPolo" in T["source"])
ok("…et la mention de citation obligatoire", "citation" in T["licence"])
ok("la précision distingue toujours l'exact du lu sur carte",
   "lecture graphique" in T["precision"] and "publiés" in T["precision"])
# Le compte porte sur les APPELS : la ligne de définition contient elle aussi
# « talSurvol(el » et gonflait le total d'un.
ok("le survol est partagé par les trois vues, en une fonction",
   html.count("function talSurvol(") == 1 and html.count("  talSurvol(el") == 3,
   html.count("  talSurvol(el"))
ok("le tri est partagé lui aussi", html.count("function talListe(") == 1)

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
