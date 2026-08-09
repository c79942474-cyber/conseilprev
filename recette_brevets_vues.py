# -*- coding: utf-8 -*-
"""Deux lectures de plus sur les brevets d'IA — côté données et côté dépôt.

CE QU'ON PROTÈGE.

1. L'IDENTITÉ QUI REND L'EMPILEMENT LÉGITIME. Une colonne empilée n'a le droit
   d'exister que si ses segments reconstituent le total. Ici le segment vaut
   part × volume mondial et les parts somment à 100 par construction — « reste
   du monde » étant déduit. On vérifie l'identité sur les huit millésimes : si
   elle cédait, la vue réconcilierait deux mensonges au lieu de deux vues.

2. LES CHIFFRES ÉCRITS DANS LES TEXTES. Les nouvelles lectures citent ×61 pour
   le volume mondial et ×327 pour la Chine. Un chiffre recopié à la main dans
   une phrase vieillit sans prévenir : chacun est ici RECALCULÉ depuis le
   référentiel, et comparé à ce que la page annonce.

3. LA DISCRIMINATION. Avant, la page ne portait que deux onglets et aucun code
   d'empilement ni de classement. Le contrôle rejoue cette absence sur le
   fichier d'avant, faute de quoi il ne vérifierait rien.
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

BREV = O.SEED["brevets"]
PARTS = BREV["parts_pct"]
VOL = BREV["volume_mondial_milliers"]
ANNEES = sorted(PARTS["Chine"], key=int)

print("\n══ 1. L'identité qui rend l'empilement légitime ══\n")

ok("huit millésimes de parts", len(ANNEES) == 8, ANNEES)
ok("…et un volume mondial pour chacun",
   all(a in VOL for a in ANNEES), [a for a in ANNEES if a not in VOL])

fautes = []
for a in ANNEES:
    trois = sum(PARTS[p][a] for p in ("Chine", "États-Unis", "Europe"))
    reste = 100 - trois
    if reste < 0:
        fautes.append((a, round(trois, 2)))
ok("les trois acteurs nommés ne dépassent jamais 100 %", not fautes, fautes)

# LE contrôle : segments = part × volume, donc la colonne somme au volume.
ecarts = []
for a in ANNEES:
    v = VOL[a]
    trois = sum(PARTS[p][a] for p in ("Chine", "États-Unis", "Europe"))
    segments = [PARTS[p][a] / 100.0 * v for p in ("Chine", "États-Unis", "Europe")]
    segments.append((100 - trois) / 100.0 * v)
    if abs(sum(segments) - v) > 1e-9:
        ecarts.append((a, round(sum(segments), 6), v))
ok("chaque colonne empilée somme EXACTEMENT au volume mondial de son année",
   not ecarts, ecarts)
ok("…y compris la dernière, 122 000 brevets", VOL[ANNEES[-1]] == 122)
# DISCRIMINATION : sans le « reste du monde », l'empilement ne serait plus un
# tout. C'est exactement le calcul qu'on refuse d'écrire.
sans_reste = sum(PARTS[p][ANNEES[-1]] for p in ("Chine", "États-Unis", "Europe")) / 100.0 * 122
ok("…alors qu'en oubliant le reste du monde, la colonne perdrait 16 000 brevets",
   abs(122 - sans_reste - 16.2) < 0.1, "%.1f milliers manquants" % (122 - sans_reste))

print("\n══ 2. Les chiffres des textes sont recalculés, jamais recopiés ══\n")

html = io.open(DEPOT + "/observatoire.html", encoding="utf-8").read()

a0, a1 = ANNEES[0], ANNEES[-1]
fact_monde = round(VOL[a1] / VOL[a0])
ok("le volume mondial est multiplié par 61 entre 2010 et 2023",
   fact_monde == 61, fact_monde)
facteurs = {}
for nom, cle in (("Chine", "chine"), ("États-Unis", "us"), ("Europe", "europe")):
    d = PARTS[nom][a0] / 100.0 * VOL[a0]
    f = PARTS[nom][a1] / 100.0 * VOL[a1]
    facteurs[cle] = round(f / d)
ok("la Chine est multipliée par 327", facteurs["chine"] == 327, facteurs["chine"])
ok("les États-Unis par 22", facteurs["us"] == 22, facteurs["us"])
ok("l'Europe par 21", facteurs["europe"] == 21, facteurs["europe"])
# La page ne doit pas porter ces nombres en dur : elle les calcule.
ok("la page CALCULE le facteur du monde, elle ne l'écrit pas en dur",
   "Math.round(v1 / v0)" in html and "soit " in html)
ok("…et le facteur par acteur passe par une seule fonction",
   html.count("function brevFacteur") == 1 and html.count("brevFacteur(") >= 3,
   html.count("brevFacteur("))

vol_2023 = round(PARTS["Chine"][a1] / 100.0 * VOL[a1], 1)
ok("la Chine pèse 85,0 milliers de brevets en 2023", abs(vol_2023 - 85.0) < 0.05,
   vol_2023)
ok("l'Europe 3,4", abs(round(PARTS["Europe"][a1] / 100.0 * VOL[a1], 1) - 3.4) < 0.05)

print("\n══ 3. Quatre lectures déclarées, et servies ══\n")

for cle in ("part", "volume", "empile", "rang"):
    ok("l'onglet « %s » existe dans la page" % cle,
       ('data-vue="%s"' % cle) in html)
ok("quatre titres, un par lecture",
   len(re.findall(r"^\s+(part|volume|empile|rang):\s+'Brevets", html, re.M)) == 4,
   len(re.findall(r"^\s+(part|volume|empile|rang):\s+'Brevets", html, re.M)))
ok("les deux nouvelles fonctions de rendu existent",
   "function brevEmpile()" in html and "function brevRang()" in html)
ok("…et le rendu leur passe la main avant toute géométrie de courbe",
   re.search(r"function renderBrevets\(\)\{\s*\n\s*if\(BV_VUE === 'empile'\)", html)
   is not None)
# Une vue qui ne dirait pas ce qu'elle cache serait une vue de plus, pas une
# lecture de plus : la discipline du panneau vaut aussi pour les nouvelles.
for mot in ("Ce que montre cette vue", "Ce qu’elle ne montre pas"):
    ok("« %s » est écrit pour les quatre lectures" % mot,
       html.count(mot) >= 4, html.count(mot))

print("\n══ 4. Ce que la géométrie doit garantir ══\n")

ok("la marge gauche s'adapte à la largeur des graduations",
   "BV_VUE === 'part' ? 58 : 96" in html)
ok("…et la marge droite loge DEUX gouttières en vue « part »",
   "var XFIN" in html and "var XAX" in html and "BV_VUE === 'part' ? 176 : 128" in html)
ok("les colonnes sont rentrées d'une demi-largeur, pour ne pas déborder",
   "L + BW / 2 +" in html and "(pw - BW)" in html)
ok("la hauteur du classement suit le nombre de barres",
   "var H = T + lignes.length * BH" in html)
ok("la butée basse des étiquettes tient compte de leur SECONDE ligne",
   "(H - B - 16)" in html)

print("\n══ 5. Discrimination : deux lectures, pas quatre, avant ══\n")


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


av = _avant("function brevEmpile", "observatoire.html")
ok("avant, la page ignorait l'empilement", "brevEmpile" not in av)
ok("…et le classement", "brevRang" not in av)
ok("…et n'offrait que DEUX onglets",
   av.count('role="tab" data-vue=') == 2, av.count('role="tab" data-vue='))
ok("…contre quatre aujourd'hui",
   html.count('role="tab" data-vue=') == 4, html.count('role="tab" data-vue='))
ok("…le titre du panneau se choisissait par un ternaire, pas par une table",
   "BV_TITRES" not in av and "BV_VUE === 'part'\n    ? 'Brevets" in av.replace("\r", ""))
# Les deux défauts de mise en page trouvés au passage n'étaient pas visibles :
# ils demandaient de mesurer les rectangles.
ok("…et sa marge droite tenait les deux gouttières dans la même colonne",
   "XFIN" not in av and "W - R + 8" in av)
ok("…si bien que le « 0 » de l'axe droit et l'étiquette « Europe » se posaient "
   "au même endroit", "W - R + 10" in av and "W - R + 8" in av)

print("\n══ 6. Ce que ces deux lectures ne devaient PAS déplacer ══\n")

ok("les parts publiées de 2023 sont intactes",
   BREV["points_2023"] == {"Chine": 69.7, "États-Unis": 14.2, "Europe": 2.8},
   BREV["points_2023"])
ok("le volume mondial 2021 reste hors des parts — on interroge par année",
   "2021" in VOL and "2021" not in PARTS["Chine"])
ok("la précision des séries est toujours annoncée",
   "lecture graphique" in BREV["precision_parts"])
ok("le crédit de la source est intact", "AI Index" in BREV["source"])
ok("la licence CC BY-ND est rappelée", "CC BY-ND" in BREV["licence"])
ok("la fonction de survol reste unique et partagée",
   html.count("function brevInteraction") == 1)
ok("…et la vue empilée la réutilise plutôt que d'en écrire une seconde",
   "brevInteraction(hote, { W: W, H: H, L: L, R: R, T: T, B: B, pw: pw, ph: ph,\n"
   "                          x: x, y: yv, vue: 'empile'" in html)

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
