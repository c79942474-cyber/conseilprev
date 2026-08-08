# -*- coding: utf-8 -*-
"""Le risque climatique physique entre au comparateur — sans mentir par omission.

CE QU'ON PROTÈGE. Un critère qui note douze pays sur vingt-huit peut se lire
de deux façons : « les seize autres vont bien » ou « on ne sait pas ». XDI ne
publie que les vingt-cinq premiers pays et n'en classe aucun comptant moins de
trois centres planifiés. L'absence n'est donc PAS une bonne nouvelle, et le
premier groupe de contrôles vérifie qu'elle ne se lit jamais comme telle.

Le second protège l'écart entre faible résilience et résilience avancée : c'est
lui qui distingue un surcoût d'ingénierie d'une erreur d'implantation, et c'est
l'information la plus actionnable du rapport.
"""
import io
import os
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

print("\n══ 1. Le rapport est recopié fidèlement ══\n")

ok("douze pays européens classés par XDI", len(I.XDI) == 12, len(I.XDI))
# Le classement mondial est le fil : s'il se brouille, la source ne se
# retrouve plus dans le rapport.
rangs = sorted(v[0] for v in I.XDI.values())
ok("les rangs sont uniques et dans le top 25",
   len(set(rangs)) == 12 and rangs[0] >= 1 and rangs[-1] <= 25, (rangs[0], rangs[-1]))
for pays, rang, bas, avance, alea in (("CH", 3, 33, 0, "crue"),
                                      ("FR", 5, 26, 18, "submersion"),
                                      ("NL", 6, 25, 0, "ruissellement"),
                                      ("DE", 21, 5, 1, "ruissellement"),
                                      ("ES", 25, 3, 1, "submersion")):
    v = I.XDI[pays]
    ok("%s : rang %d, %d %% → %d %% après ingénierie, %s"
       % (pays, rang, bas, avance, alea),
       v[0] == rang and v[2] == bas and v[3] == avance and v[6] == alea, v)
ok("la France est bien 5e mondiale, pas 5e européenne", I.XDI["FR"][0] == 5)
ok("la hausse française est BORNÉE — le rapport écrit « >300 % »",
   I.XDI["FR"][4] == 300 and I.XDI["FR"][5] is True)
ok("l'agrégat européen recopie les 623 analysés et 45 à haut risque",
   I.XDI_EUROPE["analyses"] == 623 and I.XDI_EUROPE["haut_risque"] == 45)
# CONTRÔLE ARITHMÉTIQUE : 45 / 623 doit bien donner les 7 % publiés. Une
# recopie qui ne boucle pas est une recopie fausse.
ok("…et 45 sur 623 fait bien les 7 % publiés",
   round(100.0 * 45 / 623) == I.XDI_EUROPE["part"], round(100.0 * 45 / 623))

print("\n══ 2. L'absence n'est jamais une bonne note ══\n")

absents = [c for c in ("SE", "PL", "BE", "AT", "GR") if c in par_pays]
ok("des pays hors classement existent bien dans le comparateur", len(absents) >= 4,
   absents)
for c in absents:
    x = par_pays[c]
    ok("%s n'a pas de note de risque physique" % c,
       x["notes"]["climat_physique"] is None, x["notes"]["climat_physique"])
ok("…et chacun porte la RAISON de son absence, en toutes lettres",
   all(par_pays[c]["climat_physique_absence"] for c in absents))
ok("…qui dit les deux causes possibles, sans trancher",
   all("moins de trois centres" in par_pays[c]["climat_physique_absence"]
       and "inférieure à 3 %" in par_pays[c]["climat_physique_absence"]
       for c in absents))
ok("un pays classé, lui, n'a pas de mention d'absence",
   par_pays["FR"]["climat_physique_absence"] is None)
# DISCRIMINATION : si l'absence valait 100, la Suède serait première.
ok("aucune note n'a été inventée pour les non-classés",
   sum(1 for x in d["pays"] if x["notes"]["climat_physique"] is not None) == 12,
   sum(1 for x in d["pays"] if x["notes"]["climat_physique"] is not None))

print("\n══ 3. La note ordonne comme le rapport ══\n")

n = {c: I._note_xdi(c) for c in I.XDI}
ok("la Suisse, pire du panel, tombe à 0", n["CH"] == 0, n["CH"])
ok("l'Espagne, la moins exposée des classés, monte à 91", n["ES"] == 91, n["ES"])
ok("la France reste basse : 21", n["FR"] == 21, n["FR"])
# Deux pays a 5 % (Danemark, Allemagne) recoivent la meme note : comparer des
# listes ordonnees les departagerait au hasard. On compare donc la relation,
# pays a pays : un risque plus faible ne doit JAMAIS donner une note plus
# basse. C'est la propriete qui compte, et elle vaut aussi sur les egalites.
paires = [(a, b) for a in I.XDI for b in I.XDI if a < b]
fautes = [(a, b) for a, b in paires
          if (I.XDI[a][2] < I.XDI[b][2] and n[a] <= n[b])
          or (I.XDI[a][2] > I.XDI[b][2] and n[a] >= n[b])
          or (I.XDI[a][2] == I.XDI[b][2] and n[a] != n[b])]
ok("un risque plus faible donne toujours une note plus haute, sans exception",
   not fautes, fautes[:3])
ok("…et deux pays à risque égal reçoivent la même note",
   n["DK"] == n["DE"] and I.XDI["DK"][2] == I.XDI["DE"][2], (n["DK"], n["DE"]))
ok("l'étalon est le pire du panel, pas une constante écrite à la main",
   I.XDI_PIRE == max(v[2] for v in I.XDI.values()) == 33, I.XDI_PIRE)

print("\n══ 4. L'écart d'ingénierie est calculé, et il accuse la France ══\n")

for c in I.XDI:
    q = I.xdi_de(c)
    ok("%s : part irréductible cohérente" % c,
       q["irreductible_pct"] == round(100.0 * q["haut_risque_adapte_pct"]
                                      / q["haut_risque_pct"]),
       "%d %%" % q["irreductible_pct"])
fr, ch = I.xdi_de("FR"), I.xdi_de("CH")
ok("la Suisse : tout est rattrapable par la conception",
   ch["irreductible_pct"] == 0, ch["irreductible_pct"])
ok("la France : plus des deux tiers du risque tient au LIEU",
   fr["irreductible_pct"] == 69, fr["irreductible_pct"])
ok("…et c'est le pire d'Europe",
   fr["irreductible_pct"] == max(I.xdi_de(c)["irreductible_pct"] for c in I.XDI))

print("\n══ 5. Le comparateur porte le critère, et le sert ══\n")

cles = [c["cle"] for c in d["criteres"]]
ok("dix critères désormais", len(cles) == 10, len(cles))
ok("le nouveau s'appelle climat_physique", "climat_physique" in cles)
crit = [c for c in d["criteres"] if c["cle"] == "climat_physique"][0]
ok("il déclare sa nature « referentiel », pas « analyse »",
   crit["nature"] == "referentiel", crit["nature"])
ok("il nomme XDI et son millésime dans sa source",
   "XDI" in crit["source"] and "2026" in crit["source"])
ok("sa formule dit ce qui arrive aux non-classés",
   "hors classement" in crit["formule"])
ok("la source complète est servie à part",
   d["sources"]["climat_physique"]["editeur"].startswith("XDI"))
ok("…et dit que la chaleur extrême est EXCLUE du classement",
   "chaleur extrême est EXCLUE" in d["sources"]["climat_physique"]["note"])
ok("…et que le scénario est un test de résistance, pas une prévision",
   "test de résistance" in d["sources"]["climat_physique"]["note"])
bloc = d["climat_physique"]
ok("le classement complet voyage, trié par rang",
   len(bloc["classement"]) == 12
   and [x["rang_mondial"] for x in bloc["classement"]] == sorted(rangs))
ok("l'agrégat européen voyage", bloc["europe"]["analyses"] == 623)
ok("le risque INDIRECT est dit, avec son facteur dix",
   "dix fois" in bloc["indirect"] and "138" in bloc["indirect"])

print("\n══ 6. Ce que le critère ne devait pas déplacer ══\n")

ok("la santé du module est verte", I.sante()["ok"], I.sante()["problemes"])
ok("elle compte les pays XDI", I.sante()["pays_xdi"] == 12)
ok("le millésime a changé", d["version"] == "2026-08-c", d["version"])
ok("les sept critères d'origine sont intacts",
   [c for c in cles if c not in ("climat_physique", "feux", "inondations")]
   == ["carbone", "mix", "eau", "climat", "prix", "parc", "pipeline"], cles)
ok("les notes d'origine d'un pays n'ont pas bougé",
   par_pays["FR"]["notes"]["carbone"] is not None
   and par_pays["FR"]["notes"]["climat"] == 65)

print("\n══ 7. Discrimination : rien de tout cela n'existait avant ══\n")

import subprocess                                              # noqa: E402


def _avant(marqueur, fichier):
    """Le fichier juste AVANT l'arrivée du marqueur.

    Deux cas, et le second est celui qui manquait. Si un commit a introduit le
    marqueur, on lit son parent. Si AUCUN ne l'a fait, c'est que la
    modification n'est pas encore livrée : la référence est alors HEAD. Rendre
    une chaîne vide, comme le faisait la version précédente, rendait le
    contrôle CREUX — « XDI n'est pas dans le vide » est toujours vrai."""
    hs = subprocess.check_output(
        ["git", "-C", DEPOT, "log", "-S", marqueur, "--format=%H", "--", fichier],
        text=True).split()
    ref = ("%s^" % hs[-1]) if hs else "HEAD"
    return subprocess.check_output(
        ["git", "-C", DEPOT, "show", "%s:%s" % (ref, fichier)], text=True)


av = _avant("XDI_ALEAS", "implantation.py")
ok("avant, le module ignorait XDI", "XDI" not in av)
# Le motif doit viser la LISTE des criteres, pas toute cle nommee « cle » du
# fichier : les perspectives en portent une aussi.
def _n_criteres(txt):
    i = txt.find("CRITERES = [")
    return txt.count('{"cle": "', i, txt.find("\n]", i)) if i >= 0 else -1


ok("…et ne comptait que sept critères", _n_criteres(av) == 7, _n_criteres(av))
ok("…contre dix aujourd'hui",
   _n_criteres(io.open(DEPOT + "/implantation.py", encoding="utf-8").read()) == 10)
pan = _avant("climat_physique", "panorama.html")
ok("avant, la page n'avait pas de poids pour ce critère",
   "climat_physique" not in pan)

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
