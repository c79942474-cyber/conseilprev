# -*- coding: utf-8 -*-
"""LE POINT DE CONCEPTION, LES DÉFAILLANCES, ET LA CONJONCTION QUE NUL SCORE NE VOIT.

CE QUE LE COMPARATEUR NE DISAIT PAS, ET QUE L'ÉTÉ 2026 A RENDU IMPOSSIBLE À
TAIRE. Seize critères décrivaient le kilowattheure, l'eau, le prix, le climat et
six aléas — et pas un seul ne disait si le refroidissement TIENDRAIT le jour le
plus chaud. Le critère « climat » mesure une OPPORTUNITÉ (des heures de free
cooling gagnées), jamais une RÉSILIENCE (le point où la machine s'arrête). Ce
sont deux questions opposées, et ce sont les défaillances qui ont tranché
laquelle décide.

LES QUATRE CHOSES QUE CE FICHIER PROTÈGE :

  1. LA RÈGLE ÉCRITE EST LA RÈGLE EXÉCUTÉE. Le drapeau de conjonction se lit à
     voix haute devant un client. Si le code s'en écartait, le drapeau
     deviendrait invérifiable — et un drapeau invérifiable finit ignoré, y
     compris quand il a raison. Chaque affirmation de la phrase est éprouvée sur
     des cas témoins.

  2. LA CONJONCTION N'ENTRE DANS AUCUNE NOTE. Un score pondéré ADDITIONNE ; une
     conjonction ne s'additionne pas. La noter compterait de surcroît une
     troisième fois l'eau et le climat, ce que ce module s'interdit ailleurs. Le
     jour où quelqu'un la glissera dans le calcul, le classement se mettra à
     mentir sans que rien ne le signale.

  3. LE RÉSULTAT RESTE CONTRE-INTUITIF, ET C'EST SON INTÉRÊT. Le risque n'est
     pas maximal là où il fait le plus chaud : il l'est là où l'on ne s'y
     attendait pas. Un pays méridional signalé voudrait dire que la règle a
     changé de sens ; le contrôle le refuse.

  4. UNE RÈGLE QUI NE MORD PLUS N'INFORME PLUS. Si plus aucun pays n'était
     signalé, ce ne serait pas une bonne nouvelle — ce serait un contrôle mort.
     Le silence total est le symptôme à attraper.

   POUR L'EXÉCUTER :  python3 recette_conception_canicule.py
"""
import sys

import climat_2050
import datacentres
import empreinte_sites
import implantation as imp

KO = []


def ok(nom, cond, detail=""):
    print("  %s   %s%s" % ("OK " if cond else "KO ", nom,
                           (" — " + detail) if detail else ""))
    if not cond:
        KO.append(nom)


def titre(t):
    print("\n══ %s ══\n" % t)


PARC = datacentres.assemble()["sites"]
A50 = imp.assemble(PARC, empreinte_sites.INTENSITE, horizon=2050)
A30 = imp.assemble(PARC, empreinte_sites.INTENSITE, horizon=2030)


# ── 1. Le point de conception, et ce qu’il faut rattraper ──────────────────

titre("1. Le point de conception est publié, avec son hypothèse fausse")

c = A50.get("conception") or {}
ok("le point de conception figure au référentiel", bool(c))
ok("…il porte la température de projet", c.get("temperature_projet_c") == 37.7,
   str(c.get("temperature_projet_c")) + " °C")
ok("…il dit sur QUOI cette température a été établie",
   "moyennes historiques" in c.get("hypothese", ""))
ok("…et la période de retour supposée, qui est le cœur du défaut",
   "deux cents ans" in c.get("hypothese", ""))
ok("…il énonce la contradiction avec les projections",
   "projections climatiques" in c.get("contradiction", ""))

p = c.get("prescription") or {}
ok("la majoration prescrite est chiffrée", p.get("moyenne_pct") == 11
   and p.get("sites_contraints_pct") == 48,
   "+%s %% en moyenne, +%s %% sur les sites contraints"
   % (p.get("moyenne_pct"), p.get("sites_contraints_pct")))
ok("…la moyenne reste inférieure au cas contraint — sinon l’un des deux est faux",
   p.get("moyenne_pct", 0) < p.get("sites_contraints_pct", 0))
ok("…et elle porte son éditeur", bool(p.get("editeur")))
ok("le facteur aggravant est nommé : la densité des charges d’IA",
   "IA" in c.get("aggravant", ""))
ok("des questions opposables au concepteur sont fournies",
   len(c.get("ce_qu_il_faut_demander") or []) >= 3,
   "%d questions" % len(c.get("ce_qu_il_faut_demander") or []))


# ── 2. Les défaillances, pour leur mécanisme ───────────────────────────────

titre("2. Ce qui est réellement tombé — et par quel mécanisme")

inc = A50.get("incidents") or []
ok("le registre des défaillances est publié", len(inc) >= 4, "%d entrées" % len(inc))
for x in inc:
    ok("« %s » est daté, situé et expliqué" % (x.get("ou") or "?")[:28],
       all(str(x.get(k, "")).strip() for k in ("quand", "ou", "quoi", "mecanisme")))

pantin = [x for x in inc if "Pantin" in (x.get("ou") or "")]
ok("LA DÉFAILLANCE DE PANTIN FIGURE, et c’est la plus instructive", bool(pantin))
if pantin:
    m = pantin[0]["mecanisme"]
    # LE POINT. Ce n'est pas la chaleur qui a arrêté l'installation : c'est
    # l'eau. Un registre qui écrirait « incident dû à la canicule » perdrait
    # exactement ce qui instruit la décision d'implantation.
    ok("…et son mécanisme dit que c’est L’EAU qui a manqué, pas la chaleur",
       "ALIMENTATION EN EAU" in m and "adiabatique" in m)
    ok("…il le dit explicitement pour qu’on ne conclue pas de travers",
       "Ce n’est pas la chaleur" in m)

ok("les défaillances en climat TEMPÉRÉ sont représentées",
   any("Londres" in (x.get("ou") or "") or "Rennes" in (x.get("ou") or "")
       for x in inc))
ok("le second chemin — le réseau électrique — figure aussi",
   any(x.get("enseigne") == "secours" for x in inc))
ok("…et il dit que le secours est carboné",
   any("fioul" in x.get("mecanisme", "") for x in inc))


# ── 3. LA RÈGLE ÉCRITE EST LA RÈGLE EXÉCUTÉE ──────────────────────────────

titre("3. La règle se lit à voix haute, et c’est elle qui s’exécute")

regle = A50.get("regle_conjonction") or ""
ok("la règle est publiée en clair", len(regle) > 120)
ok("…elle annonce les DEUX conditions", "DEUX conditions" in regle)
ok("…elle nomme la première : un refroidissement conçu pour un été doux",
   "été doux" in regle and "tempérée" in regle)
ok("…elle nomme la seconde : l’eau qui se tend", "sécheresse" in regle)
ok("…et elle dit pourquoi le méridional n’est jamais signalé",
   "point de conception" in regle)

# Les trois affirmations, éprouvées une par une sur des cas témoins.
ok("un pays tempéré à eau tendue EST signalé",
   imp.conjonction_de("FR", 2050)["signale"],
   "FR 2050 : " + imp.conjonction_de("FR", 2050)["motif"][:70])
ok("un pays nordique à eau détendue N’EST PAS signalé",
   not imp.conjonction_de("SE", 2050)["signale"])
ok("UN PAYS MÉRIDIONAL N’EST JAMAIS SIGNALÉ, même au pire stress hydrique",
   not imp.conjonction_de("ES", 2050)["signale"],
   "ES : sécheresse très élevée, et pourtant pas signalé — son point de "
   "conception a été posé pour la chaleur")
ok("…et le motif l’explique, au lieu de laisser croire à un oubli",
   "posé pour la chaleur" in imp.conjonction_de("ES", 2050)["motif"])
ok("un pays hors référentiel ne reçoit PAS de verdict",
   imp.conjonction_de("ZZ", 2050)["connu"] is False)

# L'horizon déplace le verdict — sinon la règle ignorerait la date.
ok("l’horizon déplace le signalement",
   len(A50["conjonction_pays"]) > len(A30["conjonction_pays"]),
   "2030 : %s → 2050 : %s" % (A30["conjonction_pays"], A50["conjonction_pays"]))
ok("…et 2030 est INCLUS dans 2050 : la dégradation ne se retourne pas",
   set(A30["conjonction_pays"]) <= set(A50["conjonction_pays"]))


# ── 4. Le résultat est contre-intuitif, et ce n’est pas un défaut ─────────

titre("4. Le risque n’est pas là où il fait le plus chaud")

sig = set(A50["conjonction_pays"])
meridionaux = {p for p in imp.EAU if imp.climat_de(p) == "meridional"}
ok("AUCUN pays méridional n’est signalé", not (sig & meridionaux),
   "méridionaux : " + " ".join(sorted(meridionaux)))
# LA FORMULATION EXACTE COMPTE. Écrit d'abord « tous les méridionaux portent un
# stress élevé », ce contrôle était simplement FAUX : la Croatie est méridionale
# et sa ressource est abondante. Ce qu'on voulait dire, et qui est vrai, est plus
# tranchant : parmi les pays au stress hydrique le plus élevé du référentiel, la
# plupart ne sont PAS signalés — parce qu'ils sont méridionaux, donc conçus pour
# la chaleur. C'est l'inversion que la règle produit, et il fallait l'énoncer sur
# les bons pays plutôt que sur une généralité fausse.
pires_eau = {p for p in imp.EAU if imp.EAU[p][0] == "eleve"}
ok("…alors que la plupart des pays au pire stress hydrique n’y figurent pas",
   len(pires_eau - sig) > len(pires_eau & sig),
   "stress élevé : %s — dont signalés : %s"
   % (" ".join(sorted(pires_eau)), " ".join(sorted(pires_eau & sig)) or "aucun"))
ok("…et ceux-là sont écartés parce qu’ils sont méridionaux, pas par oubli",
   (pires_eau - sig) <= meridionaux,
   " ".join(sorted(pires_eau - sig)))
ok("les pays signalés sont tempérés — Rennes, Pantin et Londres en sont",
   all(imp.climat_de(p) in imp.CLIMATS_ETE_DOUX for p in sig),
   " ".join(sorted(sig)))
ok("…et la France en fait partie", "FR" in sig)

cj = (A50.get("conjonctions") or {}).get("chaleur_eau") or {}
ok("le caractère contre-intuitif est ÉCRIT, pas laissé à déduire",
   "n’est donc PAS maximal" in cj.get("contre_intuitif", ""))
ok("…avec les lieux qui le montrent",
   "Pantin" in cj.get("contre_intuitif", "")
   or "Rennes" in cj.get("contre_intuitif", ""))

# UNE RÈGLE QUI NE MORD PLUS N'INFORME PLUS.
ok("la règle mord sur le référentiel — sinon elle serait morte",
   len(sig) > 0 and len(sig) < len(imp.EAU),
   "%d pays sur %d" % (len(sig), len(imp.EAU)))


# ── 5. LE CONTRÔLE QUI COMPTE : la conjonction n’entre dans aucune note ───

titre("5. Une conjonction ne s’additionne pas — elle ne doit pas être notée")

cles = {c["cle"] for c in A50["criteres"]}
ok("aucun critère noté ne porte la conjonction",
   not any("conj" in k for k in cles), " ".join(sorted(k for k in cles if "conj" in k)))

# Le contrôle décisif : à pondération égale, le score d'un pays signalé doit
# être IDENTIQUE à ce qu'il serait sans le signalement. On le vérifie en
# comparant les notes brutes des deux horizons sur un critère que l'horizon ne
# déplace pas : si le signalement entrait dans le calcul, il les ferait diverger.
fr50 = [l for l in A50["pays"] if l["pays"] == "FR"][0]
fr30 = [l for l in A30["pays"] if l["pays"] == "FR"][0]
ok("la France est signalée à 2050 et pas à 2030",
   fr50["conjonction"]["signale"] and not fr30["conjonction"]["signale"])
socle = [c["cle"] for c in A50["criteres"] if c.get("famille") == "socle"]
diff = [k for k in socle if fr50["notes"].get(k) != fr30["notes"].get(k)]
ok("…ET AUCUNE NOTE DU SOCLE N’EN A BOUGÉ",
   not diff, "notes modifiées : " + (" ".join(diff) if diff else "aucune"))

ok("le signalement porte toujours son motif", all(
    (l["conjonction"].get("motif") or "").strip()
    for l in A50["pays"] if l["conjonction"].get("connu")))
ok("la liste des pays signalés est CALCULÉE, pas recopiée",
   A50["conjonction_pays"] == sorted(
       l["pays"] for l in A50["pays"] if l["conjonction"].get("signale")))


# ── 6. Le critère « climat » ne se lit plus comme une résilience ──────────

titre("6. « Free cooling » dit une opportunité, jamais une résilience")

crit = {c["cle"]: c for c in A50["criteres"]}
f = crit["climat"]["formule"]
ok("le critère climat avertit qu’il mesure une OPPORTUNITÉ",
   "OPPORTUNITÉ" in f and "RÉSILIENCE" in f)
ok("…et rappelle que les défaillances ont eu lieu en climat tempéré",
   "TEMPÉRÉ" in f)
ok("le second couplage — canicule sur le réseau, secours au fioul — est publié",
   "chaleur_reseau" in (A50.get("conjonctions") or {}))
ok("…et il désigne des critères qui existent",
   all(x[k] in cles for x in (A50["conjonctions"] or {}).values()
       for k in ("critere_a", "critere_b")))

sante = imp.sante()
ok("les invariants du comparateur passent", sante.get("ok") is True,
   str(sante.get("problemes"))[:160])


print("\n" + ("%d contrôle(s) en échec" % len(KO) if KO else "tout est vert") + "\n")
sys.exit(1 if KO else 0)
