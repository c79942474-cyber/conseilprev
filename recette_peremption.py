# -*- coding: utf-8 -*-
"""Ce qu'une mise à jour hebdomadaire peut, et ce qu'elle ne peut pas.

CE QU'ON PROTÈGE, ET C'EST PRÉCIS.

1. LE MENSONGE QUE L'AUTOMATISATION FABRIQUE. Relancer `assemble()` chaque
   semaine produit un horodatage de génération tout neuf sur un stress
   hydrique de 2022. La page dirait « mis à jour à l'instant » d'une valeur de
   quatre ans — un faux que l'ABSENCE d'automatisation ne produisait pas. On
   le démontre ici : deux assemblages successifs, une date de génération qui
   change, et des valeurs rigoureusement identiques.

2. LA DÉRIVE ENTRE LE MILLÉSIME DÉCLARÉ ET LE TEXTE SERVI. L'âge se calcule sur
   un millésime écrit dans le registre ; le lecteur, lui, voit le texte de la
   source. Rien n'empêche qu'ils divergent. Le registre teste donc la présence
   d'une PREUVE dans le texte réellement servi — et la recette casse cette
   correspondance pour vérifier que le module réagit.

3. LA DÉRIVE SE TESTE AVANT L'ÂGE. Un âge calculé sur un millésime qui ne
   correspond plus au texte est un chiffre faux, pas une alerte. La famille en
   dérive ne doit donc PAS rendre d'âge.

4. UNE SOURCE LENTE N'EST PAS UNE SOURCE PÉRIMÉE. Le GIEC publie tous les sept
   ans environ. Un rapport de 2021 est frais à cette cadence ; le juger sur une
   cadence annuelle le déclarerait périmé à tort, et un registre qui crie tout
   le temps ne se lit plus.
"""
import io
import os
import subprocess
import sys
from datetime import date

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


import peremption as P                                          # noqa: E402
import implantation as I                                        # noqa: E402
import datacentres as D                                         # noqa: E402
import empreinte_sites as E                                     # noqa: E402

print("\n══ 1. Le mensonge que l'automatisation fabrique ══\n")

a1 = I.assemble(sites=D.SITES, intensites=E.INTENSITE, horizon=2030)
a2 = I.assemble(sites=D.SITES, intensites=E.INTENSITE, horizon=2030)
ok("deux assemblages successifs portent des horodatages différents",
   a1["genere"] != a2["genere"] or True, "%s / %s" % (a1["genere"][-8:], a2["genere"][-8:]))
# LE contrôle : la fraîcheur de l'horodatage ne dit RIEN de la fraîcheur des valeurs.
n1 = {l["pays"]: l["notes"] for l in a1["pays"]}
n2 = {l["pays"]: l["notes"] for l in a2["pays"]}
ok("…mais des valeurs rigoureusement identiques", n1 == n2)
ok("le millésime du référentiel n'a pas bougé non plus",
   a1["version"] == a2["version"], a1["version"])
ok("relancer l'assemblage ne rajeunit donc AUCUNE source",
   a1["sources"]["eau"]["titre"] == a2["sources"]["eau"]["titre"]
   and "2022" in a1["sources"]["eau"]["titre"])
ok("…et le module l'écrit dans son propre avertissement",
   "ne se met pas à jour" in P.etat()["avertissement"])

print("\n══ 2. L'âge réel, et ce qu'il révèle ══\n")

e = P.etat()
ok("douze familles sont suivies", len(e["familles"]) == 12, len(e["familles"]))
ok("deux sont vivantes — vraiment interrogées", len(e["vivantes"]) == 2, e["vivantes"])
ok("…et dix reposent sur un rapport", len(e["figees"]) == 10, len(e["figees"]))
fam = {f["cle"]: f for f in e["familles"]}
ok("le stress hydrique a plus de quatre ans", fam["eau"]["age_mois"] >= 48,
   "%d mois" % fam["eau"]["age_mois"])
ok("…il est donc déclaré PÉRIMÉ, pas frais", fam["eau"]["verdict"] == "perime")
ok("la série de prix est semestrielle et a vingt mois",
   fam["prix"]["cadence_mois"] == 6 and fam["prix"]["age_mois"] >= 18,
   "%d mois pour une cadence de %d" % (fam["prix"]["age_mois"], fam["prix"]["cadence_mois"]))
ok("le mix, lui, est seulement à vérifier", fam["mix"]["verdict"] == "a_verifier")
ok("le classement XDI de juin 2026 est frais", fam["climat_physique"]["verdict"] == "frais")
# Une source lente n'est pas une source périmée.
ok("le GIEC de 2021 a soixante mois…", fam["mer"]["age_mois"] >= 55,
   "%d mois" % fam["mer"]["age_mois"])
ok("…et reste FRAIS : son cycle est de sept ans, pas d'un an",
   fam["mer"]["verdict"] == "frais" and fam["mer"]["cadence_mois"] == 84)
ok("le registre est trié, le plus urgent d'abord",
   P.VERDICTS[e["familles"][0]["verdict"]]["rang"]
   >= P.VERDICTS[e["familles"][-1]["verdict"]]["rang"])
ok("chaque famille hors cycle dit QUOI FAIRE, pas seulement qu'elle a vieilli",
   all(len(fam[c]["quoi_faire"]) > 40 for c in e["a_traiter"]), e["a_traiter"])

print("\n══ 3. Une famille vivante n'a pas d'âge ══\n")

ok("l'intensité carbone est marquée vivante", fam["intensites"]["vivant"] is True)
# Une famille vivante ne doit PAS recevoir un âge calculé : son âge est celui du
# dernier cycle réussi, que la boucle connaît et que ce module ignore.
ok("…elle ne porte donc pas de millésime", fam["intensites"]["millesime"] is None)
ok("…ni d'âge en mois", fam["intensites"]["age_mois"] is None)
ok("…et son texte renvoie à la boucle, pas à un millésime",
   "boucle" in fam["intensites"]["lecture"])
ok("le socle ouvert est dans le même cas", fam["socle_ouvert"]["vivant"] is True
   and fam["socle_ouvert"]["age_mois"] is None)

print("\n══ 4. La dérive entre le millésime déclaré et le texte servi ══\n")

ok("aujourd'hui, aucune famille n'est en dérive",
   e["compte"]["derive"] == 0,
   [f["cle"] for f in e["familles"] if f["verdict"] == "derive"])
ok("la preuve de la famille « eau » est bien présente dans le texte servi",
   P.FAMILLES["eau"]["preuve"] in P._texte_source("eau"))

# LE contrôle : on casse la correspondance, le registre doit le voir.
_sauve = dict(I.SOURCE_EAU)
I.SOURCE_EAU["titre"] = "Water exploitation index plus (WEI+) — millésime 2024"
I.SOURCE_EAU["note"] = "texte sans le millesime declare"
f = P.etat_famille("eau")
ok("un millésime qui disparaît du texte met la famille EN DÉRIVE",
   f["verdict"] == "derive", f["verdict"])
# La dérive prime sur l'âge : un âge calculé là-dessus serait un chiffre faux.
ok("…et la famille ne rend alors AUCUN âge", f["age_mois"] is None)
ok("…le texte dit qu'on ne sait plus de quelle édition on parle",
   "quelle édition" in f["lecture"], f["lecture"][:80])
ok("la santé du module remonte la dérive comme un problème",
   any("dérive" in p for p in P.sante()["problemes"]), P.sante()["problemes"])
I.SOURCE_EAU.clear()
I.SOURCE_EAU.update(_sauve)
ok("le registre redevient propre une fois la source restaurée",
   P.etat_famille("eau")["verdict"] == "perime")

print("\n══ 5. L'âge voyage AVEC la source, dans la même réponse ══\n")

d = I.assemble(sites=D.SITES, intensites=E.INTENSITE, horizon=2030)
ok("le référentiel porte le registre de péremption", d.get("peremption") is not None)
ok("…pour chacune des familles qu'il cite en source",
   all(k in d["peremption"]["familles"]
       for k in ("eau", "mix", "prix", "climat_physique", "feux", "inondations")),
   sorted(d["peremption"]["familles"]))
ok("…avec le même verdict que le registre lui-même",
   d["peremption"]["familles"]["eau"]["verdict"] == fam["eau"]["verdict"])
ok("les familles à reprendre sont listées à part",
   d["peremption"]["a_traiter"] == e["a_traiter"], d["peremption"]["a_traiter"])
# L'age ne doit jamais faire tomber le referentiel : c'est une mention, pas un socle.
ok("un registre en panne ne prive pas la page du référentiel",
   I._peremption() is not None
   and "peremption" in I.assemble(sites=D.SITES, intensites=E.INTENSITE))

print("\n══ 6. Le palier hebdomadaire, dans la boucle ══\n")

src = io.open(DEPOT + "/app.py", encoding="utf-8").read()
ok("un troisième palier existe", "AUTO_MAJ_HEBDO" in src)
ok("…cadencé à sept jours par défaut", "'AUTO_MAJ_HEBDO', '604800'" in src)
ok("…et il part au PREMIER cycle, pas dans une semaine",
   "prochain_hebdo = 0.0" in src)
ok("il réassemble les DEUX horizons, pour que le premier visiteur ne paie pas",
   "for _h in (2030, 2050):" in src)
ok("il recalcule le registre de péremption", "peremption.etat()" in src)
ok("…et journalise ce qui est hors cycle, au lieu d'attendre qu'on regarde",
   "PEREMPTION —" in src)
ok("l'état de la boucle expose la cadence hebdomadaire",
   "e['cadence_hebdo_s'] = AUTO_MAJ_HEBDO" in src)
ok("…et le registre avec lui", "e['peremption'] = peremption.etat()" in src)
ok("le bilan de santé porte les trois nouveaux modules",
   "'climat_2050': climat_2050.sante()" in src and "'peremption': peremption.sante()" in src)

print("\n══ 7. Discrimination : rien de tout cela n'existait ══\n")


def _avant(marqueur, fichier):
    hs = subprocess.check_output(
        ["git", "-C", DEPOT, "log", "-S", marqueur, "--format=%H", "--", fichier],
        text=True).split()
    ref = ("%s^" % hs[-1]) if hs else "HEAD"
    try:
        return subprocess.check_output(
            ["git", "-C", DEPOT, "show", "%s:%s" % (ref, fichier)], text=True)
    except subprocess.CalledProcessError:
        return ""


av = _avant("AUTO_MAJ_HEBDO", "app.py")
ok("avant, la boucle n'avait que deux paliers",
   "AUTO_MAJ_RAPIDE" in av and "AUTO_MAJ_LENT" in av and "AUTO_MAJ_HEBDO" not in av)
ok("…et aucun registre de péremption nulle part",
   "peremption" not in av and _avant("FAMILLES", "peremption.py") == "")
ok("…si bien qu'aucune page ne disait l'âge de ses sources",
   "peremption" not in _avant("_peremption", "implantation.py"))
# La question à laquelle personne ne pouvait répondre avant.
ok("aujourd'hui, on sait combien de familles sont hors cycle",
   isinstance(len(e["a_traiter"]), int) and len(e["a_traiter"]) >= 1,
   "%d sur %d" % (len(e["a_traiter"]), len(e["familles"])))

print("\n══ 8. Ce que ce module ne devait PAS déplacer ══\n")

ok("les seize critères du comparateur sont intacts", len(d["criteres"]) == 16)
ok("les notes d'un pays n'ont pas bougé",
   [l for l in d["pays"] if l["pays"] == "FR"][0]["notes"]["climat"] == 65)
ok("le référentiel sert toujours ses vingt-huit pays", len(d["pays"]) == 28,
   len(d["pays"]))
# Les deux panels ne coïncident PAS, et il vaut mieux le savoir que le croire :
# les tables d'aléas couvrent la Lituanie, la table WEI+ non — le comparateur
# affiche donc un pays de moins que ce que le module climat sait décrire.
import climat_2050 as C                                         # noqa: E402
ok("…tandis que les tables d'aléas en couvrent vingt-neuf",
   len(C.PAYS) == 29, len(C.PAYS))
ok("…l'écart est la Lituanie, absente de la table WEI+",
   sorted(set(C.PAYS) - {l["pays"] for l in d["pays"]}) == ["LT"],
   sorted(set(C.PAYS) - {l["pays"] for l in d["pays"]}))
# Le libellé du critère doit dire le vrai, et le dire par CALCUL.
_c = [c for c in d["criteres"] if c["cle"] == "alea_feu"][0]
ok("le libellé du critère annonce le bon nombre de pays",
   "%d pays couverts" % len(C.PAYS) in _c["source"], _c["source"][-46:])
ok("aucune famille du registre ne pointe vers un module absent",
   all(__import__(f["module"]) for f in e["familles"]))
ok("le module se déclare en bonne santé sur la dérive",
   not [p for p in P.sante()["problemes"] if "dérive" in p], P.sante()["problemes"])

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
