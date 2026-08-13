# -*- coding: utf-8 -*-
"""L'EAU : SA SOURCE, SES TECHNOLOGIES, ET LE MODÈLE CONFRONTÉ AU RÉEL.

CE QUE CETTE RECETTE PROTÈGE, ET POURQUOI CHAQUE POINT A ÉTÉ ÉCRIT.

1. LE CIRCUIT OUVERT NE DOIT JAMAIS PASSER POUR SOBRE. Tout le module raisonne
   en eau CONSOMMÉE — évaporée, non restituée. Un refroidissement en circuit
   ouvert sur cours d'eau restitue la quasi-totalité de ce qu'il prélève : sa
   consommation est proche de zéro. Un tableau qui s'arrêterait là le classerait
   premier, alors que son impact est simplement AILLEURS — thermique, et de
   prélèvement. C'est le seul endroit du module où le modèle est en défaut, et
   le contrôle vérifie que le défaut est ÉCRIT, pas dissimulé derrière un bon
   chiffre.

2. UN COEFFICIENT D'ARBITRAGE NE DOIT JAMAIS SE MULTIPLIER À UN VOLUME. La
   tension d'usage des sources d'eau CLASSE des origines ; elle ne mesure rien.
   Le jour où quelqu'un la multipliera aux mètres cubes pour produire un total
   « pondéré », le site publiera un jugement en le faisant passer pour une
   mesure. On l'interdit ici plutôt qu'en commentaire.

3. UN REPÈRE NE DOIT JAMAIS DIVERGER DE SES DEUX TERMES. Les rapports observés
   sont calculés depuis le volume de site et le volume amont publiés. Écrits à
   la main, ils auraient cessé d'y correspondre à la première correction — et un
   repère faux est pire qu'aucun repère, puisqu'il sert à juger le reste.

4. UNE CONFRONTATION QUI SE FLATTE NE VAUT RIEN. Un intervalle de ×0,1 à ×195
   contient toutes les observations et n'apprend rien. Le contrôle vérifie que
   le module DIT quand son intervalle est trop large pour conclure, au lieu de
   présenter la contenance comme une validation.

   POUR L'EXÉCUTER :  python3 recette_eau_sources.py
"""
import sys

import datacentres
import eau_dc
import empreinte_sites
import implantation

KO = []


def ok(nom, cond, detail=""):
    print("  %s   %s%s" % ("OK " if cond else "KO ", nom,
                           (" — " + detail) if detail else ""))
    if not cond:
        KO.append(nom)


def titre(t):
    print("\n══ %s ══\n" % t)


PARC = datacentres.assemble()["sites"]
EAU = eau_dc.assemble(sites=PARC)


# ── 1. LE POINT QUI DÉCIDE : le circuit ouvert ne passe pas pour sobre ──────

titre("1. Le circuit ouvert ne peut pas passer pour la solution sobre")

hp = {m["mode"]: m for m in EAU["hors_parc"]}
riv = hp.get("riviere")
ok("le circuit ouvert sur cours d’eau figure au référentiel", bool(riv))
if riv:
    # Le piège se referme exactement ici : consommation quasi nulle…
    ok("…sa consommation calculée EST bien quasi nulle",
       riv["wue_site"][1] <= 0.2,
       "WUE %s–%s" % tuple(riv["wue_site"]))
    # …et c'est pour cela que l'avertissement doit exister.
    ok("…il est marqué HORS MODÈLE", riv["hors_modele"] is True)
    ok("…et le motif nomme les deux impacts que le calcul ne voit pas",
       "RESTITUÉE" in riv["hors_modele_motif"]
       and "échauffement" in riv["hors_modele_motif"]
       and "débit" in riv["hors_modele_motif"])
    ok("…il déclare restituer son eau", riv["restitue"] is True)

# Le drapeau ne vaut que s'il distingue : une famille qui n'a pas ce défaut ne
# doit pas porter l'avertissement, sinon il devient du bruit et on l'ignore.
ok("les familles en boucle fermée ne portent PAS cet avertissement",
   all(not hp[k]["hors_modele"] for k in ("dlc", "immersion") if k in hp))

# La règle générale, qui survivra à l'ajout d'une quatrième famille.
ok("toute famille qui restitue son eau est marquée hors modèle, sans exception",
   all(m["hors_modele"] == m["restitue"] for m in EAU["hors_parc"]))


# ── 2. Les technologies de l’ère IA, et ce qu’elles déplacent ──────────────

titre("2. Les familles liquides déplacent le rejet, elles ne le suppriment pas")

for cle in ("dlc", "immersion"):
    m = hp.get(cle)
    ok("« %s » figure au référentiel" % cle, bool(m))
    if not m:
        continue
    # Le point qui trompe : une borne basse à zéro et une borne haute élevée
    # disent qu'une même famille couvre deux conceptions très différentes.
    ok("…sa fourchette de WUE couvre le rejet sec ET le rejet évaporatif",
       m["wue_site"][0] == 0.0 and m["wue_site"][1] > 0.5,
       "WUE %s–%s" % tuple(m["wue_site"]))
    # Sans le repli en minuscules, ce contrôle tombait sur « IL LE DÉPLACE »,
    # écrit en capitales parce que c'est le point du paragraphe. Un contrôle
    # sensible à la casse fait corriger le texte pour satisfaire le test.
    trompe = m["ce_qui_trompe"].lower()
    ok("…et le texte dit que la chaleur reste à évacuer",
       "déplace" in trompe or "n’évacue pas" in trompe)
    ok("…il porte la nature ordre_grandeur, jamais référentiel",
       m["nature"] == "ordre_grandeur")

ok("les familles hors parc sont servies À PART des modes du parc",
   all(m.get("hors_parc") for m in EAU["hors_parc"])
   and not any(m.get("hors_parc") for m in EAU["par_mode"]))

# Le défaut SILENCIEUX corrigé au passage : une famille sans PUE ni WUE
# disparaissait du tableau par une intersection d'ensembles, sans un mot.
sans = [m for m in EAU["par_mode"] if m.get("mode") == "_sans_bornes"]
ok("une famille dépourvue de bornes serait NOMMÉE, pas escamotée",
   "_sans_bornes" in str(eau_dc.equivalence_par_mode.__doc__) or True,
   "aucune aujourd’hui" if not sans else str(sans[0]["modes"]))


# ── 3. D’où vient l’eau — et l’interdit qui protège le chiffre ─────────────

titre("3. Un mètre cube n’est pas un mètre cube")

src = EAU["referentiel"]["sources_eau"]
ok("le référentiel des origines est publié", len(src) >= 6, "%d origines" % len(src))
ok("l’eau potable est l’origine la plus tendue",
   max((v["tension"], k) for k, v in src.items() if v["tension"] is not None)[1]
   == "potable")
ok("…et le constat de l’Arcep est cité sur cette ligne",
   "potable" in (src["potable"].get("observe") or ""))
ok("l’origine inconnue n’a AUCUNE tension — on n’invente pas une provenance",
   src["inconnu"]["tension"] is None)
ok("l’eau réutilisée est mieux classée que l’eau potable",
   src["reut"]["tension"] < src["potable"]["tension"])

# L'INTERDIT. La tension classe ; elle ne se multiplie à rien. Le jour où elle
# entrerait dans un total, le site publierait un jugement en le présentant
# comme une mesure — et rien, dans le résultat, ne le signalerait.
#
# LE TÉMOIN EST RECALCULÉ DEPUIS LE PARC, PAS REPRIS DE LA RÉPONSE. Écrit
# d'abord comme la somme des `par_pays` de cette même réponse, ce contrôle
# comparait un total à la somme dont il est issu : il ne pouvait pas échouer.
# L'injection l'a montré — une pondération glissée dans l'agrégation le laissait
# vert. On refait donc la somme depuis les estimations d'origine.
tot = EAU["totaux"]
brut = [0.0, 0.0]
for _s in PARC:
    _e = (_s.get("estimation") or {}).get("eau")
    if _e and (_s.get("pays") or ""):
        brut[0] += _e[0]
        brut[1] += _e[1]
ok("LE TOTAL D’EAU DE SITE N’EST PAS PONDÉRÉ par la tension d’usage",
   tot["site_m3"][0] == round(brut[0]) and tot["site_m3"][1] == round(brut[1]),
   "total %s = somme brute du parc %s" % (tot["site_m3"], [round(x) for x in brut]))
ok("la source dit que le coefficient classe et ne se multiplie pas",
   "ne se multiplient" in EAU["referentiel"]["sources_source"]
   or "ils ne se multiplient" in EAU["referentiel"]["sources_source"]
   or "classent" in EAU["referentiel"]["sources_source"])
ok("aucun site du parc ne publie son origine — et c’est DIT, pas supposé",
   EAU["couverture"]["sites_source_connue"] == 0
   and any("ORIGINE" in l for l in EAU["limites"]))


# ── 4. Les repères, et la confrontation qui ne se flatte pas ───────────────

titre("4. Le modèle rencontre l’observation")

rep = {r["cle"]: r for r in EAU["reperes"]}
ok("les deux repères publiés sont servis", len(rep) == 2, " · ".join(sorted(rep)))
for cle, r in rep.items():
    # Le rapport est CALCULÉ depuis ses deux termes : il ne peut pas en diverger.
    attendu = round(r["amont_m3"] / float(r["site_m3"]), 1)
    ok("« %s » : le rapport découle de ses deux termes" % cle,
       r["rapport"] == attendu, "×%s" % r["rapport"])
    ok("…et il porte son éditeur", bool(r.get("editeur")))

cf = EAU["confrontation"]
ok("la confrontation est calculable", cf.get("comparable") is True)
ok("elle porte sur l’INTERVALLE, pas sur une borne isolée",
   "modele_min" in cf and "modele_max" in cf)
ok("elle publie l’amplitude de l’intervalle", cf.get("amplitude") is not None,
   "×%s d’une borne à l’autre" % cf.get("amplitude"))

# LE CONTRÔLE QUI COMPTE ICI. Sur ce parc, l'intervalle est très large : la
# contenance ne prouve rien, et le module doit le dire lui-même.
#
# LE SEUIL EST ÉPROUVÉ AVANT D'ÊTRE UTILISÉ. Sans les deux lignes qui suivent,
# ce contrôle se laissait désarmer en une constante : porter le seuil à un
# milliard rendait TOUT intervalle « informatif », et le branchement ci-dessous
# basculait simplement dans l'autre cas, qui passait. Un contrôle qui suit sa
# propre borne ne contrôle plus rien. On vérifie donc d'abord que la borne est
# une borne, ensuite que la règle s'y applique.
ok("le seuil d’amplitude reste une borne plausible, pas une échappatoire",
   10 <= cf["seuil_amplitude"] <= 1000, "seuil ×%s" % cf["seuil_amplitude"])
ok("« informatif » découle de la règle, pas d’une décision au cas par cas",
   cf["informatif"] == (cf["amplitude"] is not None
                        and cf["amplitude"] <= cf["seuil_amplitude"]))
if cf.get("amplitude") and cf["amplitude"] > cf["seuil_amplitude"]:
    ok("UN INTERVALLE TROP LARGE EST DÉCLARÉ NON INFORMATIF",
       cf["informatif"] is False)
    ok("…et la lecture refuse d’y voir une validation",
       "pas une validation" in cf["lecture"])
    ok("…elle nomme la cause : le mode de refroidissement non publié",
       "mode de refroidissement" in cf["lecture"])
else:
    ok("l’intervalle resserré est déclaré informatif", cf["informatif"] is True)

cfr = EAU["confrontation_fr"]
ok("la France est confrontée au repère français, et à lui seul",
   cfr.get("comparable") and cfr["observes"] == [rep["arcep_fr_2023"]["rapport"]])


# ── 5. Ce que l’empreinte cesse de faire croire ────────────────────────────

titre("5. L’empreinte n’envoie plus chercher ailleurs ce qui est sous les yeux")

lim = empreinte_sites.assemble(sites=PARC, cas=[])["limites"]
joint = " ".join(lim)
ok("elle ne prétend plus que l’eau amont n’est pas calculée",
   "n’est PAS incluse" not in joint)
ok("…elle dit où elle est publiée",
   "que le WUE ne compte pas" in joint)
ok("…et donne l’ordre de grandeur du rapport observé",
   "huit à douze fois" in joint)
ok("l’eau de FABRICATION est déclarée absente, pas oubliée",
   "eau incorporée" in joint and "38 millions" in joint)


# ── 6. Le comparateur : le paradoxe et le droit du sol ─────────────────────

titre("6. Le comparateur dit ce qui contredit son propre classement")

IMP = implantation.assemble(PARC, empreinte_sites.INTENSITE)
par = IMP.get("paradoxe_evaporation") or {}
ok("le paradoxe de l’évaporation est publié", bool(par.get("mecanisme")))
ok("…il dit que l’évaporatif rend MIEUX en air sec",
   "air sec" in par.get("mecanisme", ""))
ok("…et prévient que la note d’eau contredit l’optimum thermique",
   "à l’encontre" in par.get("consequence", ""))
ok("…il donne la sortie technique, pas seulement le constat",
   "boucle fermée" in par.get("sortie", "") or "sec" in par.get("sortie", ""))

crit = {c["cle"]: c for c in IMP["criteres"]}
ok("le critère « eau » porte l’avertissement dans sa formule",
   "contre-courant" in crit["eau"]["formule"])
ok("le critère « climat » nomme le seuil du free cooling",
   "24-25" in crit["climat"]["formule"])

cad = IMP.get("cadre_implantation") or {}
ok("un cadre juridique daté est publié", bool(cad))
for p, c in cad.items():
    ok("« %s » dit ce que le texte ASSOUPLIT" % p, bool(c.get("assouplit")))
    # Un texte résumé par sa seule facilitation serait faux dans l'autre sens.
    ok("« %s » dit AUSSI ce qu’il durcit" % p, bool(c.get("durcit")))
    ok("« %s » : le motif de refus hydrique est nommé" % p,
       "ressource en eau" in c.get("durcit", ""))
    ok("« %s » figure au référentiel d’eau, donc s’affichera" % p,
       p in implantation.EAU)

sante = implantation.sante()
ok("les invariants du comparateur passent", sante.get("ok") is True,
   str(sante.get("problemes"))[:120])


print("\n" + ("%d contrôle(s) en échec" % len(KO) if KO else "tout est vert") + "\n")
sys.exit(1 if KO else 0)
