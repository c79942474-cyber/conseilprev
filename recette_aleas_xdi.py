# -*- coding: utf-8 -*-
"""Feux de forêt et inondations : deux rapports, deux métriques, un piège.

CE QU'ON PROTÈGE, ET C'EST PRÉCIS.

1. LE PIÈGE DE LA LISTE DES PIRES. Le rapport « feux » ne publie que les DIX
   premiers États membres — c'est-à-dire les dix PIRES. Rapporter un rang à la
   taille de cette liste donnerait 100 au dixième : la note dirait « meilleur
   profil d'Europe » d'un pays que la source range dans le pire décile. Le rang
   se rapporte donc aux VINGT-SEPT États membres, et la plage haute reste vide.
   C'est le contrôle central de ce fichier.

2. LE PIÈGE DES DEUX MÉTRIQUES. Les inondations sont classées en RATIO au coût
   de remplacement — comparable d'un pays à l'autre. Les feux sont classés en
   montant ABSOLU — un grand parc bâti y remonte par sa taille. Les lire comme
   deux mesures de même nature est une faute d'analyse, et les textes servis
   doivent l'écrire.

3. LE PIÈGE DE L'ABSENCE. Un pays tiers n'est pas « bien classé » : il n'était
   pas éligible. La Suisse n'apparaît dans aucun des deux rapports alors que le
   rapport centres de données de juin 2026 la classe TROISIÈME MONDIALE pour la
   crue. Si l'absence valait une bonne note, la page se contredirait elle-même.
"""
import io
import os
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


import implantation as I                                       # noqa: E402
import datacentres as D                                        # noqa: E402
import empreinte_sites as E                                    # noqa: E402

d = I.assemble(D.SITES, getattr(E, "INTENSITE", {}))
par_pays = {x["pays"]: x for x in d["pays"]}

print("\n══ 1. Les deux rapports sont recopiés fidèlement ══\n")

ok("dix rangs de feux publiés par horizon", d["feux"]["publies"] == 10,
   d["feux"]["publies"])
ok("…sur onze lignes, parce que le classement BOUGE entre 2025 et 2050",
   d["feux"]["lignes"] == 11 and len(I.FEUX) == 11, len(I.FEUX))
ok("la Croatie sort des dix premiers en 2050",
   I.feux_de("HR")["sort_en_2050"] and I.feux_de("HR")["rang_2025"] == 10)
ok("…et la Pologne y entre", I.feux_de("PL")["entre_en_2050"]
   and I.feux_de("PL")["rang_2050"] == 10)
ok("la France passe DEUXIÈME en 2025 à PREMIÈRE en 2050",
   I.FEUX["FR"][0] == 2 and I.FEUX["FR"][1] == 1, I.FEUX["FR"][:2])
ok("l'Italie fait le trajet inverse", I.FEUX["IT"][:2] == (1, 2), I.FEUX["IT"][:2])
ok("la plus forte hausse 2025-2050 est française, +159 %",
   I.FEUX_HAUSSES["2025_2050"][0] == ("FR", 159), I.FEUX_HAUSSES["2025_2050"][0])
ok("la plus forte hausse 1990-2025 est roumaine, +200 %",
   I.FEUX_HAUSSES["1990_2025"][0] == ("RO", 200), I.FEUX_HAUSSES["1990_2025"][0])

ok("vingt-sept États membres classés pour l'inondation", len(I.INONDATIONS) == 27)
rangs = sorted(v[0] for v in I.INONDATIONS.values())
ok("…et les rangs vont de 1 à 27 sans trou ni doublon",
   rangs == list(range(1, 28)), (rangs[0], rangs[-1], len(set(rangs))))
for pays, rang, h1, h2 in (("IT", 1, 25, 32), ("FR", 2, 19, 23), ("DE", 3, 32, 31),
                           ("MT", 27, 88, 11)):
    v = I.INONDATIONS[pays]
    ok("%s : rang %d, +%d %% depuis 1990, +%d %% d'ici 2050" % (pays, rang, h1, h2),
       v[0] == rang and v[1] == h1 and v[2] == h2, v[:3])
ok("l'Union a déjà pris +30 % de risque depuis 1990",
   I.INONDATIONS_UE["hausse_1990_2025"] == 30)
ok("…et 18 milliards d'euros de dégâts pour la seule année 2024",
   I.INONDATIONS_UE["cout_2024_mdeur"] == 18)
ok("l'Île-de-France, elle, voit +110 % d'ici 2100",
   I.INONDATIONS_UE["idf_2100"] == 110, I.INONDATIONS_UE["idf_2100"])
ok("les feux coûtent déjà 2 Md€ par an à l'Union (Cour des comptes)",
   I.FEUX_UE["cout_annuel_mdeur"] == 2)
ok("les vingt régions les plus exposées tiennent en CINQ pays",
   all(p in I.INONDATIONS_UE["concentration"]
       for p in ("Italie", "Allemagne", "France", "Pologne", "Belgique")))

print("\n══ 2. LE contrôle : une liste des pires ne vaut pas un satisfecit ══\n")

notes_f = {p: I._note_feux(p) for p in I.FEUX}
servies = sorted(n for n in notes_f.values() if n is not None)
ok("les dix pays classés reçoivent tous une note BASSE",
   max(servies) <= 40, "la plus haute vaut %d" % max(servies))
ok("le dixième plafonne à 35, il n'atteint pas la plage haute",
   notes_f["PL"] == 35, notes_f["PL"])
ok("le premier — la France — tombe à 0", notes_f["FR"] == 0, notes_f["FR"])
# DISCRIMINATION ARITHMÉTIQUE : c'est le calcul qu'on a refusé d'écrire. Si le
# dénominateur était la profondeur du classement (10), le dixième vaudrait 100
# et le comparateur sacrerait la Pologne meilleur pays d'Europe sur les feux.
faux = I._note_rang(I.FEUX["PL"][1], 10)
ok("…alors que rapporté aux DIX publiés il aurait valu 100 — le piège évité",
   faux == 100 and notes_f["PL"] != faux, "%d contre %d" % (faux, notes_f["PL"]))
ok("le dénominateur est bien le champ des 27, pas la liste publiée",
   d["feux"]["champ"] == 27 == len(I.UE_27), d["feux"]["champ"])
# Contre-épreuve sur l'autre aléa : là, les 27 SONT classés, donc le dernier
# mérite vraiment 100. La règle n'est pas « brider », c'est « dire vrai ».
ok("pour l'inondation, où les 27 sont classés, le dernier atteint bien 100",
   I._note_inondations("MT") == 100 and I._note_inondations("IT") == 0)

print("\n══ 3. L'absence n'est jamais une bonne note — et elle dit laquelle ══\n")

tiers = [c for c in ("CH", "NO", "GB", "LI") if c in par_pays]
ok("des pays tiers figurent bien au comparateur", len(tiers) >= 3, tiers)
for c in tiers:
    x = par_pays[c]
    ok("%s : aucune note sur les deux aléas" % c,
       x["notes"]["feux"] is None and x["notes"]["inondations"] is None,
       (x["notes"]["feux"], x["notes"]["inondations"]))
    ok("…et les deux raisons disent « hors du champ », pas « faible risque »" ,
       "hors du champ" in x["feux_absence"]
       and "hors du champ" in x["inondations_absence"])
    ok("…en niant explicitement la lecture rassurante",
       "pas un signe de faible exposition" in x["inondations_absence"])
# LA contradiction qu'on interdit : la Suisse est 3e mondiale pour la crue au
# rapport centres de données, et absente du rapport UE. Les deux doivent
# coexister sur la page sans se démentir.
ch = par_pays["CH"]
ok("la Suisse reste 3e mondiale pour la crue au critère centres de données",
   ch["climat_physique"]["rang_mondial"] == 3 and ch["notes"]["climat_physique"] == 0)
ok("…et son absence du rapport UE le RAPPELLE plutôt que de le contredire",
   "troisième mondiale" in ch["inondations_absence"])

membres_hors_dix = [c for c in ("SE", "DE", "NL", "AT", "DK") if c in par_pays]
for c in membres_hors_dix:
    x = par_pays[c]
    ok("%s, membre mais hors des dix feux : pas de note" % c,
       x["notes"]["feux"] is None, x["notes"]["feux"])
    ok("…et la raison n'est PAS celle des pays tiers",
       "hors des DIX" in x["feux_absence"] and "hors du champ" not in x["feux_absence"])
    ok("…tout en ayant, elle, une note d'inondation",
       x["notes"]["inondations"] is not None, x["notes"]["inondations"])
hr = par_pays["HR"]
ok("la Croatie, elle, a un troisième motif : elle SORT du classement",
   hr["notes"]["feux"] is None and "SORT des dix" in hr["feux_absence"])
ok("trois motifs d'absence distincts, jamais un silence",
   len({par_pays["CH"]["feux_absence"], par_pays["SE"]["feux_absence"],
        hr["feux_absence"]}) == 3)
ok("aucune note de feux n'a été inventée hors des dix classés",
   sum(1 for x in d["pays"] if x["notes"]["feux"] is not None) == 10,
   sum(1 for x in d["pays"] if x["notes"]["feux"] is not None))
# DISCRIMINATION : si l'absence valait 100, la Norvège serait sacrée sur deux
# critères qu'aucun rapport n'a mesurés pour elle.
ok("un pays sans note ne peut pas gagner un critère qu'il n'a pas passé",
   par_pays["NO"]["notes"]["feux"] is None
   and par_pays["NO"]["notes"]["inondations"] is None)

print("\n══ 4. La note ordonne comme le rapport, sans jamais inventer d'écart ══\n")

ni = {c: I._note_inondations(c) for c in I.INONDATIONS}
paires = [(a, b) for a in I.INONDATIONS for b in I.INONDATIONS if a < b]
fautes = [(a, b) for a, b in paires
          if (I.INONDATIONS[a][0] < I.INONDATIONS[b][0] and ni[a] >= ni[b])
          or (I.INONDATIONS[a][0] > I.INONDATIONS[b][0] and ni[a] <= ni[b])]
ok("un rang plus exposé donne toujours une note plus basse, sans exception",
   not fautes, fautes[:3])
classes = [c for c in I.FEUX if I.FEUX[c][1]]
fautes_f = [(a, b) for a in classes for b in classes if a < b
            and ((I.FEUX[a][1] < I.FEUX[b][1] and notes_f[a] >= notes_f[b])
                 or (I.FEUX[a][1] > I.FEUX[b][1] and notes_f[a] <= notes_f[b]))]
ok("…et de même pour les feux", not fautes_f, fautes_f[:3])
ok("un rang absent ne produit pas de note, il produit None",
   I._note_rang(None, 27) is None and I._note_rang(0, 27) is None)
ok("un champ dégénéré ne divise pas par zéro", I._note_rang(1, 1) is None)

print("\n══ 5. Les deux métriques ne se lisent pas pareil, et le texte le dit ══\n")

sf, si = d["sources"]["feux"], d["sources"]["inondations"]
ok("la source feux nomme le « Aggregated Damage Risk »", "Damage Risk" in sf["note"])
ok("…et prévient que la grandeur est ABSOLUE, donc sensible à la taille",
   "ABSOLUE" in sf["note"] and "taille" in sf["note"])
ok("…et qu'un pays hors des dix n'a pas de valeur publiée",
   "n'a pas de valeur publiée" in sf["note"])
ok("la source inondations nomme le « Aggregated Damage Ratio »",
   "Damage Ratio" in si["note"])
ok("…et explique POURQUOI l'éditeur a choisi un ratio",
   "taux de change" in si["note"] and "inflation" in si["note"])
ok("…et avoue que la submersion côtière n'est PAS couverte",
   "submersion côtière n'est PAS couverte" in si["note"])
ok("les deux annoncent le scénario RCP 8.5 comme test de résistance",
   "RCP 8.5" in sf["note"] and "RCP 8.5" in si["note"]
   and "test de résistance" in sf["note"])
ok("les deux sont datées de 2025, pas du millésime du rapport de juin 2026",
   "2025" in sf["editeur"] and "2025" in si["editeur"],
   (sf["editeur"], si["editeur"]))

print("\n══ 6. Le comparateur les porte, et les sert ══\n")

cles = [c["cle"] for c in d["criteres"]]
ok("seize critères désormais : dix de socle et six d'aléas",
   len(cles) == 16 and sum(1 for c in d["criteres"] if c["famille"] == "aleas") == 6,
   len(cles))
ok("feux et inondations en font partie",
   "feux" in cles and "inondations" in cles, cles)
cf = [c for c in d["criteres"] if c["cle"] == "feux"][0]
ci = [c for c in d["criteres"] if c["cle"] == "inondations"][0]
ok("tous deux se déclarent « referentiel », pas « analyse »",
   cf["nature"] == ci["nature"] == "referentiel")
ok("la formule des feux explique le plafonnement à 35",
   "35" in cf["formule"] and "VINGT-SEPT" in cf["formule"], cf["formule"][:80])
ok("celle des inondations dit ce que la submersion n'y est pas",
   "submersion" in ci["formule"])
ok("les deux disent le sort des pays hors champ",
   "pas de note" in cf["formule"] and "pas de note" in ci["formule"])
ok("les deux classements complets voyagent, triés",
   [x["rang_2050"] for x in d["inondations"]["classement"]] == list(range(1, 28))
   and [x["pays"] for x in d["feux"]["classement"]][:2] == ["FR", "IT"])
ok("chaque pays classé cite ses régions les plus exposées",
   all(x["regions"] for x in d["inondations"]["classement"])
   and all(x["regions"] for x in d["feux"]["classement"]))
ok("la France cite bien ses trois régions d'inondation",
   par_pays["FR"]["inondations"]["regions"][0].startswith("Provence"),
   par_pays["FR"]["inondations"]["regions"])
ok("les hausses voyagent à part des rangs — seules grandeurs soustrayables",
   set(d["feux"]["hausses"]) == {"1990_2025", "2025_2050"})
# Le compte de sites cité par deux critères était FIGÉ à 97 : la carte disait
# 249 et la formule 97, sur le même écran. Il se substitue désormais.
srcs = " ".join(c["source"] for c in d["criteres"])
ok("aucun critère ne cite plus un parc de 97 sites",
   "97 sites" not in srcs, [c["cle"] for c in d["criteres"] if "97 sites" in c["source"]])
ok("…ils citent le parc RÉEL, et le gabarit reste dans la constante",
   "249 sites" in srcs and "{n_sites}" in I.CRITERES[5]["source"])
# DISCRIMINATION : la substitution suit vraiment la donnée, elle n'est pas une
# seconde valeur écrite en dur.
ok("…et ce compte suit la donnée, il n'est pas recopié",
   "3 sites" in " ".join(c["source"] for c in
                         I.assemble(D.SITES[:3], {})["criteres"]))

print("\n══ 7. Ce que les deux critères ne devaient PAS déplacer ══\n")

ok("la santé du module est verte", I.sante()["ok"], I.sante()["problemes"])
s = I.sante()
ok("elle compte les deux nouveaux jeux",
   s["pays_feux"] == 11 and s["pays_inondations"] == 27,
   (s["pays_feux"], s["pays_inondations"]))
ok("le millésime a changé", d["version"] == "2026-08-d", d["version"])
ok("les huit critères antérieurs sont intacts et dans l'ordre",
   [c for c in cles if not c.startswith("alea_")
    and c not in ("feux", "inondations")]
   == ["carbone", "mix", "eau", "climat", "prix", "parc", "climat_physique",
       "pipeline"], cles)
# Les six aléas s'ajoutent en QUEUE. S'ils s'intercalaient, les poids qu'un
# lecteur a réglés désigneraient d'autres critères au rechargement.
ok("…et les six aléas viennent tous après le socle",
   [i for i, c in enumerate(cles) if c.startswith("alea_")] == list(range(10, 16)),
   cles)
ok("les notes antérieures d'un pays n'ont pas bougé",
   par_pays["FR"]["notes"]["climat"] == 65
   and par_pays["FR"]["notes"]["climat_physique"] == 21,
   par_pays["FR"]["notes"])
ok("le référentiel des sites n'a pas été touché", len(D.SITES) == 249, len(D.SITES))
ok("les sources antérieures sont toujours servies",
   all(k in d["sources"] for k in ("eau", "mix", "prix", "perspectives",
                                   "climat_physique")))

print("\n══ 8. Discrimination : rien de tout cela n'existait avant ══\n")


def _avant(marqueur, fichier):
    """Le fichier juste AVANT l'arrivée du marqueur.

    Si un commit l'a introduit, on lit son parent ; sinon la modification
    n'est pas encore livrée et la référence est HEAD. Rendre une chaîne vide
    rendrait le contrôle CREUX."""
    hs = subprocess.check_output(
        ["git", "-C", DEPOT, "log", "-S", marqueur, "--format=%H", "--", fichier],
        text=True).split()
    ref = ("%s^" % hs[-1]) if hs else "HEAD"
    return subprocess.check_output(
        ["git", "-C", DEPOT, "show", "%s:%s" % (ref, fichier)], text=True)


av = _avant("INONDATIONS_UE", "implantation.py")
ok("avant, le module ignorait les inondations", "INONDATIONS" not in av)
ok("…et les feux de forêt", "FEUX" not in av)
ok("…et ne connaissait pas le périmètre de l'Union", "UE_27" not in av)


def _n_criteres(txt):
    i = txt.find("CRITERES = [")
    return txt.count('{"cle": "', i, txt.find("\n]", i)) if i >= 0 else -1


ok("…et ne comptait que huit critères", _n_criteres(av) == 8, _n_criteres(av))
ok("…contre dix aujourd'hui",
   _n_criteres(io.open(DEPOT + "/implantation.py", encoding="utf-8").read()) == 10)
pan = _avant("imp-c-feux", "panorama.html")
ok("avant, la page n'avait ni poids ni couleur pour ces critères",
   "imp-c-feux" not in pan and "imp-c-inondations" not in pan)
ok("…ni de valeur brute d'aléa dans l'infobulle", "feu de forêt :" not in pan)

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
