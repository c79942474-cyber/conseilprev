# -*- coding: utf-8 -*-
"""Aléas climatiques 2030-2050 — ce qui doit rester vrai.

CE QU'ON PROTÈGE, ET C'EST PRÉCIS.

1. L'EXCEPTION VERROUILLÉE. Ce module accorde UNE note favorable à une case
   sans valeur mesurée : la submersion d'un pays sans littoral. C'est un fait,
   pas un trou. Une exception non gardée s'étend toujours — le contrôle
   d'intégrité refuse donc `sans_objet` ailleurs, et la recette le prouve en
   essayant de le violer dans les deux sens : mauvais aléa, mauvais pays.

2. LE PIÈGE DE L'ÉCHELLE QUI BUTE. Le Portugal est au cran maximal du feu dès
   2030. Son écart 2030-2050 vaut donc zéro. Lire ce zéro comme « rien
   n'empire » est le contresens exact. Chaque case saturée est drapeau, et le
   drapeau est vérifié ici.

3. LE PIÈGE DE L'EX ÆQUO. Rendre « l'aléa dominant » au singulier ferait
   trancher l'ordre du dictionnaire : le Royaume-Uni afficherait « submersion »
   parce que cette clé est écrite en premier, alors que quatre aléas y sont au
   même niveau. On rend la liste, et on vérifie qu'elle en contient bien
   plusieurs là où il y a égalité.

4. LE PIÈGE DU SCÉNARIO RASSURANT. À 2050, l'écart entre la trajectoire la plus
   sobre et la plus émettrice vaut quatre centimètres. Un dossier qui
   présenterait un scénario optimiste comme une protection à cet horizon serait
   faux, et le module doit le dire lui-même.

5. LA DISCRIMINATION. Trois pays sérieusement candidats — Royaume-Uni, Suisse,
   Suède — arrivaient au comparateur avec leurs cases d'aléas VIDES, parce que
   les rapports sources ne couvrent que les vingt-sept États membres. On le
   vérifie sur le référentiel existant, pas sur une mémoire.
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


import climat_2050 as C                                          # noqa: E402
import implantation as I                                         # noqa: E402

print("\n══ 1. La discrimination : ces trois pays n'avaient RIEN ══\n")

# Les trous ne sont pas les mêmes d'un pays à l'autre : on les mesure un par
# un plutôt que d'affirmer un « rien » commode. La Suède, par exemple, EST au
# rapport inondations — c'est le feu et le risque physique qui lui manquent.
def _trous(p):
    return sorted(n for n, v in (("feux", I.feux_de(p)),
                                 ("inondations", I.inondations_de(p)),
                                 ("physique", I._note_xdi(p))) if v is None)


ok("Royaume-Uni : ni feu ni inondation — hors des rapports réservés à l'Union",
   _trous("GB") == ["feux", "inondations"], _trous("GB"))
ok("Suisse : les deux mêmes trous, pour la même raison de périmètre",
   _trous("CH") == ["feux", "inondations"], _trous("CH"))
ok("Suède : elle EST au rapport inondations — ce sont le feu et le risque "
   "physique qui lui manquent",
   _trous("SE") == ["feux", "physique"], _trous("SE"))
ok("…et son rang d'inondation existe bel et bien",
   (I.inondations_de("SE") or {}).get("rang_2050") == 16,
   I.inondations_de("SE"))
ok("au total, vingt-cinq pays du panel sur vingt-neuf ont au moins un aléa vide",
   sum(1 for p in C.PAYS if _trous(p)) == 25,
   "%d pays sur %d" % (sum(1 for p in C.PAYS if _trous(p)), len(C.PAYS)))
ok("…douze en avaient DEUX sur trois, dont le Royaume-Uni, la Suisse et la Suède",
   sum(1 for p in C.PAYS if len(_trous(p)) == 2) == 12
   and all(len(_trous(p)) == 2 for p in ("GB", "CH", "SE")),
   [p for p in C.PAYS if len(_trous(p)) == 2])
ok("…et quatre pays seulement étaient complets — les quatre grands du sud",
   sorted(p for p in C.PAYS if not _trous(p)) == ["ES", "FR", "IT", "PT"],
   sorted(p for p in C.PAYS if not _trous(p)))
ok("le nouveau module, lui, ne laisse aucun pays sans les six aléas",
   all(C.aleas_de(p, 2050) and len(C.aleas_de(p, 2050)) == 6 for p in C.PAYS))
ok("…et leur absence est une question de PÉRIMÈTRE, pas de mérite",
   "hors du champ" in (I._absence_inondations("GB") or "").lower()
   or "vingt-sept" in (I._absence_inondations("GB") or "").lower(),
   I._absence_inondations("GB"))

# Ce que le nouveau module y met.
for p in ("GB", "CH", "SE"):
    f = C.aleas_de(p, 2050)
    ok("%s reçoit maintenant les six aléas" % p,
       f is not None and len(f) == 6 and all(v["niveau"] for v in f.values()))
ok("…et une note d'ensemble aux deux horizons",
   all(C.note_climat(p, 2030) and C.note_climat(p, 2050) for p in ("GB", "CH", "SE")))

print("\n══ 2. L'exception verrouillée ══\n")

ok("la Suisse est sans objet en submersion — elle n'a pas de mer",
   C.TABLES["submersion"]["CH"][0] == "sans_objet")
ok("…et cette case vaut 100, pas None", C.note_alea("CH", "submersion") == 100)
ok("les sept pays enclavés du panel le sont tous",
   all(C.TABLES["submersion"][p][0] == "sans_objet"
       for p in C.ENCLAVES if p in C.TABLES["submersion"]),
   [p for p in C.ENCLAVES if p in C.TABLES["submersion"]])
ok("aucun pays à littoral ne porte `sans_objet`",
   not [p for p, v in C.TABLES["submersion"].items()
        if v[0] == "sans_objet" and p not in C.ENCLAVES])
ok("…et aucun autre aléa ne l'utilise nulle part",
   not [(a, p) for a in C.ALEAS if a != "submersion"
        for p, v in C.TABLES[a].items() if "sans_objet" in (v[0], v[1])])

# LE contrôle : le garde-fou doit RÉAGIR. On le viole dans les deux sens.
_sauve_feu = dict(C.FEU)
C.FEU["FR"] = ("sans_objet", "sans_objet", "elevee", None)
C.TABLES["feu"] = C.FEU
fautes = C._verifier_tables()
ok("un `sans_objet` posé sur un AUTRE aléa est refusé",
   any("interdit hors submersion" in f for f in fautes), fautes[:2])
C.FEU.clear()
C.FEU.update(_sauve_feu)
C.TABLES["feu"] = C.FEU

_sauve_sub = dict(C.SUBMERSION)
C.SUBMERSION["FR"] = ("sans_objet", "sans_objet", "elevee", None)
C.TABLES["submersion"] = C.SUBMERSION
fautes = C._verifier_tables()
ok("…et sur un pays qui A un littoral, aussi",
   any("littoral" in f for f in fautes), fautes[:2])
# On restaure AVANT l'essai suivant : deux entorses simultanées laisseraient
# croire que la seconde est détectée alors qu'on lirait le verdict de la première.
C.SUBMERSION.clear()
C.SUBMERSION.update(_sauve_sub)
C.SUBMERSION["CH"] = ("faible", "faible", "elevee", None)
C.TABLES["submersion"] = C.SUBMERSION
fautes = C._verifier_tables()
ok("un pays enclavé PRIVÉ de son `sans_objet` est signalé lui aussi",
   fautes and all("CH" in f for f in fautes), fautes[:2])
C.SUBMERSION.clear()
C.SUBMERSION.update(_sauve_sub)
C.TABLES["submersion"] = C.SUBMERSION
ok("le référentiel est propre une fois les essais annulés",
   C._verifier_tables() == [], C._verifier_tables()[:2])

print("\n══ 3. L'absence n'est jamais une bonne note ══\n")

ok("un pays hors référentiel n'a pas de note", C.note_climat("US") is None)
ok("…ni de fiche d'aléas", C.aleas_de("US") is None)
ok("…ni de note par aléa", C.note_alea("US", "feu") is None)
ok("…et sa correction locale de niveau marin vaut None, pas zéro",
   C.mer_locale("US") is None)
ok("un pays sans correction locale documentée n'en invente pas",
   C.mer_locale("FR") is None and C.mer_locale("NL") is not None)

print("\n══ 4. L'échelle qui bute, et l'ex æquo ══\n")

ok("le Portugal est au maximum du feu dès 2030", C.sature("PT", "feu"))
agg = [a for a in C.aggravations() if a["pays"] == "PT" and a["alea"] == "feu"]
ok("…il n'affiche donc AUCUNE aggravation sur cet aléa", not agg)
# LE contrôle : ce zéro doit être drapeauté, sinon il se lit à l'envers.
ligne = [x for x in C.assemble(2050)["pays"] if x["pays"] == "PT"][0]
ok("…mais la case est marquée SATURÉE, pour qu'on ne lise pas « ça se calme »",
   "feu" in ligne["satures"], ligne["satures"])
ok("un pays non saturé ne porte pas ce drapeau",
   "feu" not in [x for x in C.assemble(2050)["pays"]
                 if x["pays"] == "SE"][0]["satures"])
ok("le compte des cases saturées est publié",
   C.assemble(2050)["satures"] == 9, C.assemble(2050)["satures"])

dom_gb = C.dominants("GB", 2050)
ok("le Royaume-Uni a plusieurs aléas au même niveau en 2050",
   len(dom_gb) > 1, dom_gb)
ok("…et ils sont rendus TOUS, pas départagés par l'ordre du dictionnaire",
   dom_gb == sorted(dom_gb) and set(dom_gb) <= set(C.ALEAS))
ok("un pays à aléa unique n'en rend qu'un", len(C.dominants("NL", 2050)) == 1,
   C.dominants("NL", 2050))
ok("les dominants sont bien au rang le plus haut du pays",
   max(C.NIVEAUX[C.alea_de("GB", a, 2050)["niveau"]]["rang"] for a in C.ALEAS)
   == C.NIVEAUX[C.alea_de("GB", dom_gb[0], 2050)["niveau"]]["rang"])

print("\n══ 5. La mer : ce que le GIEC publie, et ce qu'il ne publie pas ══\n")

m50 = C.mer(2050, "SSP2-4.5")
ok("2050 est servi tel que publié : médiane et plage probable",
   m50["nature"] == "referentiel" and m50["mediane_m"] == 0.20
   and m50["plage_m"] == [0.17, 0.26], m50["mediane_m"])
ok("les trois scénarios sont portés", set(C.MER) == {"SSP1-2.6", "SSP2-4.5", "SSP5-8.5"})
ok("l'élévation est croissante avec l'horizon, dans chaque scénario",
   all(C.MER[s][2100][0] > C.MER[s][2050][0] for s in C.MER))
ok("…et croissante avec le scénario, à horizon égal",
   C.MER["SSP1-2.6"][2100][0] < C.MER["SSP2-4.5"][2100][0] < C.MER["SSP5-8.5"][2100][0])
# LE fait qui décide.
e50, e100 = C.ecart_scenarios(2050), C.ecart_scenarios(2100)
ok("à 2050, le choix d'émissions ne vaut que quatre centimètres",
   e50["ecart_m"] == 0.04, e50["ecart_m"])
ok("…contre trente-trois à 2100 — c'est APRÈS que le choix pèse",
   e100["ecart_m"] == 0.33, e100["ecart_m"])
ok("…et la lecture servie le dit en toutes lettres",
   "déjà engagée" in e50["lecture"] and "déterminant" in e100["lecture"])
# 2030 n'est pas un horizon publié : il ne doit PAS se faire passer pour tel.
m30 = C.mer(2030)
ok("2030 n'est pas un horizon publié par le GIEC : la valeur est CALCULÉE",
   m30["nature"] == "calcule", m30["nature"])
ok("…sa méthode est écrite", "interpolation" in m30["methode"])
ok("…et sa réserve aussi : l'élévation accélère, l'interpolation ment",
   "ACCÉLÈRE" in m30["reserve"])
ok("aucune plage n'est inventée pour cet horizon", m30["plage_m"] is None)

print("\n══ 6. Le sol bouge aussi — et parfois dans l'autre sens ══\n")

fi = C.mer_locale("FI")
ok("la Finlande voit son sol se relever", fi["mouvement_mm_an"] > 0)
ok("…assez vite pour que le niveau relatif BAISSE encore",
   "BAISSE" in fi["commentaire"])
# La comparaison doit se faire sur la MÊME période que la valeur du GIEC :
# celle-ci part de la moyenne 1995-2014, dont le milieu est 2005 — quarante-cinq
# ans jusqu'à 2050, pas vingt-cinq. Comparer 25 ans de rebond à 45 ans
# d'élévation ferait perdre au sol une course qu'il gagne.
_ANS = 2050 - 2005
ok("le rebond finlandais dépasse l'élévation mondiale sur la même période",
   fi["mouvement_mm_an"] * _ANS / 1000.0 > C.mer(2050)["mediane_m"],
   "%.2f m de relèvement sur %d ans contre %.2f m d'élévation"
   % (fi["mouvement_mm_an"] * _ANS / 1000.0, _ANS, C.mer(2050)["mediane_m"]))
ok("…et le rebond suédois aussi, mais de peu — d'où le contraste interne",
   C.mer_locale("SE")["mouvement_mm_an"] * _ANS / 1000.0 > C.mer(2050)["mediane_m"])
ok("la subsidence néerlandaise, elle, s'AJOUTE à l'élévation",
   C.mer_locale("NL")["mouvement_mm_an"] < 0
   and abs(C.mer_locale("NL")["mouvement_mm_an"]) * _ANS / 1000.0 > 0.04)
ok("les Pays-Bas, eux, s'enfoncent", C.mer_locale("NL")["mouvement_mm_an"] < 0)
ok("…et l'Italie du Pô aussi", C.mer_locale("IT")["mouvement_mm_an"] < 0)
ok("la Suède porte les DEUX régimes, et le texte le dit",
   "Scanie" in C.mer_locale("SE")["commentaire"])
ok("la Finlande et la Suède sont donc classées faibles en submersion aux deux horizons",
   all(C.TABLES["submersion"][p][:2] == ("faible", "faible") for p in ("FI", "SE")))

print("\n══ 7. Ce que la colonne « pluie » dit, et qui vaut pour tous ══\n")

# LA thèse du module : l'averse extrême monte partout, y compris là où le
# cumul annuel baisse. Si un seul pays était classé faible, elle tomberait.
faibles_pluie = [p for p in C.PAYS if C.TABLES["pluie"][p][0] == "faible"
                 or C.TABLES["pluie"][p][1] == "faible"]
ok("aucun pays d'Europe n'est classé faible aux précipitations extrêmes",
   not faibles_pluie, faibles_pluie)
ok("…et le module l'écrit comme son information principale",
   "Aucun pays" in C.ALEAS["pluie"]["pourquoi"])
ok("les pays méditerranéens, qui s'assèchent, y montent quand même",
   all(C.NIVEAUX[C.TABLES["pluie"][p][1]]["rang"] >= 3 for p in ("ES", "GR", "PT")))
ok("les pays nordiques aussi — le nord n'est pas au calme",
   all(C.NIVEAUX[C.TABLES["pluie"][p][1]]["rang"] >= 3 for p in ("SE", "NO", "FI")))
ok("la Suède n'est pas non plus un pays sans feu",
   C.NIVEAUX[C.TABLES["feu"]["SE"][1]]["rang"] >= 3
   and "2018" in (C.TABLES["feu"]["SE"][3] or ""))

print("\n══ 8. La confiance se porte case par case ══\n")

ok("chaque case porte une confiance déclarée",
   all(v[2] in C.CONFIANCES for a in C.ALEAS for v in C.TABLES[a].values()))
s = C.sante()
ok("la part de confiance faible est PUBLIÉE, pas cachée",
   s["part_confiance_faible_pct"] > 0 and "confiance_faible" in s,
   "%d cases sur %d" % (s["confiance_faible"], s["cases"]))
ok("les six aléas couvrent tous les pays du panel",
   not [f for f in s["problemes"] if "sans classe" in f], s["problemes"][:2])
ok("le module se déclare en bonne santé", s["problemes"] == [])
ok("la nature de la synthèse est ANALYSE, pas référentiel",
   C.SOURCE_ALEAS["nature"] == "analyse")
ok("…et le texte dit que ce sont des classes, pas des valeurs modélisées",
   "CLASSES" in C.SOURCE_ALEAS["note"] and "modélisées" in C.SOURCE_ALEAS["note"])
ok("l'avertissement refuse explicitement de dimensionner un ouvrage",
   "jamais à dimensionner" in C.assemble()["avertissement"])

print("\n══ 9. Les deux horizons donnent bien deux résultats ══\n")

a30, a50 = C.assemble(2030), C.assemble(2050)
n30 = {x["pays"]: x["note"] for x in a30["pays"]}
n50 = {x["pays"]: x["note"] for x in a50["pays"]}
ok("aucun pays ne s'améliore entre 2030 et 2050",
   all(n50[p] <= n30[p] for p in n30),
   [p for p in n30 if n50[p] > n30[p]])
ok("…et la plupart se dégradent : l'horizon change le classement",
   sum(1 for p in n30 if n50[p] < n30[p]) >= 25,
   "%d pays sur %d" % (sum(1 for p in n30 if n50[p] < n30[p]), len(n30)))
ok("le classement lui-même n'est pas le même aux deux dates",
   [x["pays"] for x in a30["pays"]] != [x["pays"] for x in a50["pays"]])
ok("cent dix aggravations sont recensées", len(C.aggravations()) == 110,
   len(C.aggravations()))
ok("elles sont triées par ampleur, la plus forte d'abord",
   C.aggravations()[0]["crans"] >= C.aggravations()[-1]["crans"])
ok("un horizon intermédiaire retombe sur la classe 2030, pas sur une moyenne inventée",
   C.note_climat("FR", 2040) == C.note_climat("FR", 2030))

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
